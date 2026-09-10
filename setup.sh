#!/bin/sh
# One command from a fresh clone to five live dashboards.
#
#   sh setup.sh
#
# Each step is idempotent -- rerun it after a failure rather than unpicking
# anything. The script stops at the FIRST failure with a specific message,
# because the failure that actually happens here is a missing prerequisite and a
# generic "something went wrong" sends people to the wrong place.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"

EXAPUMP="$HOME/.local/bin/exapump"
PROFILE="${EXAPUMP_PROFILE:-starter-kit}"

say() { printf "\n\033[1m==> %s\033[0m\n" "$1"; }
die() { printf "\n\033[31merror: %s\033[0m\n" "$1" >&2; exit 1; }

# --- 0. prerequisites -------------------------------------------------------
say "0/5  checking prerequisites"
[ -x "$EXAPUMP" ] || die "exapump not found at $EXAPUMP.
  Install the Exasol Personal Local Starter Kit first:
  https://github.com/exasol/local-agent-ready-starter"

command -v exakit >/dev/null 2>&1 || die "exakit not found -- install the starter kit first."

# The database has to be UP, not merely installed. A stopped database fails later
# as a connection refused on 8563, which reads like a firewall problem.
exakit status 2>/dev/null | grep -qi "running" || {
  echo "  database not running -- starting it"
  exakit start || die "could not start Exasol. Try: exakit status"
}

VENV=""
for c in "$HOME/.exasol-starter-kit/dash-server-venv/bin/python3" \
         "$HOME/dash-server/.venv/bin/python3"; do
  [ -x "$c" ] && VENV="$c" && break
done
[ -n "$VENV" ] || die "dash-server is not installed. Add it, then rerun:
  EXAKIT_MARKETPLACE_ADDONS=dash-server exakit marketplace"
echo "  exapump      $EXAPUMP"
echo "  dash python  $VENV"
echo "  profile      $PROFILE"

# --- 1. schema --------------------------------------------------------------
say "1/5  creating STARTER_KIT.SUPERSTORE_SRC"
"$EXAPUMP" sql -p "$PROFILE" - < sql/01_schema.sql \
  || die "schema creation failed. Check: exapump sql -p $PROFILE 'SELECT 1'"

# --- 2. data ----------------------------------------------------------------
# CREATE OR REPLACE TABLE in step 1 empties the table, so a rerun reloads rather
# than doubling the row count.
say "2/5  loading 51,290 order lines (12 MB, a few seconds)"
"$EXAPUMP" upload -p "$PROFILE" --table STARTER_KIT.SUPERSTORE_SRC data/superstore.csv \
  || die "data load failed. If it mentions UTF-8 or a stray column, the CSV was
  probably altered by a checkout with CRLF line endings -- see .gitattributes."

# --- 3. view ----------------------------------------------------------------
say "3/5  creating the STARTER_KIT.SUPERSTORE view"
"$EXAPUMP" sql -p "$PROFILE" - < sql/02_view.sql || die "view creation failed."

say "      verifying the load against the published figures"
"$EXAPUMP" sql -p "$PROFILE" - < sql/03_verify.sql

# --- 4. deploy --------------------------------------------------------------
# ship.sh dry-runs all 26 queries against the live database first and refuses to
# deploy if any contract fails, so a broken build never reaches the browser.
say "4/5  dry run, then deploy"
sh ship.sh superstore-boards || die "deploy failed -- read the 'deploy :' line above,
  not the summary: ship.sh prints 'all clean' even when promotion was blocked."

# --- 5. verify --------------------------------------------------------------
# The step that matters. A passing healthcheck does NOT mean the callbacks work;
# this fires the real callback for all five personas and reads the numbers back.
say "5/5  verifying every persona board actually renders"
"$VENV" preflight.py superstore-boards

cat <<'DONE'

  Open the dashboard:  http://127.0.0.1:5100/apps/superstore-boards

  Five tabs under the title: Finance Manager, Sales Manager, Project Manager,
  Data Scientist, Product Manager. They share one filter bar, so a claim made
  on one tab can be checked on another at the identical scope.

DONE
