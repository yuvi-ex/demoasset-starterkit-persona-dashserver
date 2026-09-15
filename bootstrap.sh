#!/bin/sh
# One command from nothing to five live dashboards.
#
#   curl -fsSL https://raw.githubusercontent.com/yuvi-ex/demoasset-starterkit-dashserver/main/bootstrap.sh | sh
#
# Written to be run BY AN AGENT, not by a person at a prompt:
#
#   * Nothing prompts and nothing waits for a keypress, so it cannot hang an
#     agent console.
#   * It is SAFE UNDER `curl | sh`, which takes two specific things:
#       - every line lives inside main(), so the shell must read the whole
#         script before it executes any of it;
#       - every child script runs with stdin closed (`< /dev/null`).
#     Without both, a child that reads stdin consumes the REST OF THIS SCRIPT,
#     which then silently stops early and exits 0.
#   * Every failure exits non-zero with one specific line saying what to run.
#     No "something went wrong".
#   * It is idempotent. Re-running after a failure is always safe and is the
#     intended repair: it re-uses an existing clone and setup.sh reloads rather
#     than doubling anything.
#
# Knobs (all optional, all env vars -- there are no interactive questions):
#   DEMO_DIR=~/superstore-demo     where to clone
#   BRANCH=main                    which branch
#   --install-kit                  also install the starter kit + dash-server
#                                  if they are missing, instead of stopping
set -eu

REPO="https://github.com/yuvi-ex/demoasset-starterkit-dashserver.git"
DEMO_DIR="${DEMO_DIR:-$HOME/superstore-demo}"
BRANCH="${BRANCH:-main}"
INSTALL_KIT=0
for a in "$@"; do
  if [ "$a" = "--install-kit" ]; then INSTALL_KIT=1; fi
done

# The kit installs into ~/.local/bin, which a non-login shell often lacks.
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) PATH="$HOME/.local/bin:$PATH"; export PATH ;;
esac

say()  { printf "\n\033[1m==> %s\033[0m\n" "$1"; }
die()  { printf "\n\033[31merror: %s\033[0m\n" "$1" >&2; exit 1; }

main() {
  KIT_INSTALL='curl -fsSL https://raw.githubusercontent.com/exasol/local-agent-ready-starter/main/install.sh | sh'
  DASH_INSTALL='EXAKIT_MARKETPLACE_ADDONS=dash-server exakit marketplace'

  # --- 1. the kit -------------------------------------------------------------
  say "1/4  checking the Exasol starter kit"
  if ! command -v exakit >/dev/null 2>&1; then
    [ "$INSTALL_KIT" = 1 ] || die "the Exasol starter kit is not installed.
    Install it, then re-run this script:
        $KIT_INSTALL
    Or re-run with --install-kit to have this script do it."
    say "      installing the starter kit (a few minutes)"
    sh -c "$KIT_INSTALL" < /dev/null || die "starter kit install failed -- run it by hand: $KIT_INSTALL"
    # The installer puts exakit in ~/.local/bin, which this shell may not have.
  fi
  command -v exakit >/dev/null 2>&1 || die "exakit installed but not on PATH.
    Add it and re-run:  export PATH=\"\$HOME/.local/bin:\$PATH\""

  # The database must be UP, not merely installed. A stopped database surfaces
  # later as connection-refused on 8563, which reads like a firewall problem.
  exakit status 2>/dev/null | grep -qi running || {
    say "      starting the database"
    exakit start < /dev/null || die "could not start Exasol. Try: exakit status"
  }

  # --- 2. dash-server ---------------------------------------------------------
  say "2/4  checking the dash-server add-on"
  VENV=""
  for c in "$HOME/.exasol-starter-kit/dash-server-venv/bin/python3" \
           "$HOME/dash-server/.venv/bin/python3"; do
    [ -x "$c" ] && VENV="$c" && break
  done
  if [ -z "$VENV" ]; then
    [ "$INSTALL_KIT" = 1 ] || die "the dash-server add-on is not installed.
    Install it, then re-run this script:
        $DASH_INSTALL
    Or re-run with --install-kit to have this script do it."
    say "      installing dash-server"
    sh -c "$DASH_INSTALL" < /dev/null || die "dash-server install failed -- run it by hand: $DASH_INSTALL"
  fi

  # --- 3. the demo ------------------------------------------------------------
  say "3/4  fetching the demo into $DEMO_DIR"
  command -v git >/dev/null 2>&1 || die "git is not installed."
  if [ -d "$DEMO_DIR/.git" ]; then
    echo "  already cloned -- updating"
    git -C "$DEMO_DIR" fetch --quiet origin "$BRANCH" \
      && git -C "$DEMO_DIR" checkout --quiet "$BRANCH" \
      && git -C "$DEMO_DIR" reset --hard --quiet "origin/$BRANCH" \
      || die "could not update $DEMO_DIR. Delete it and re-run."
  elif [ -e "$DEMO_DIR" ]; then
    die "$DEMO_DIR exists but is not a git clone. Move it aside, or set DEMO_DIR."
  else
    git clone --quiet --branch "$BRANCH" "$REPO" "$DEMO_DIR" \
      || die "clone failed. Check the network, or clone by hand: git clone $REPO"
  fi

  # --- 4. build it ------------------------------------------------------------
  # setup.sh loads the data, builds the view, dry-runs all 26 queries, deploys
  # only if every contract holds, then fires the real callbacks and reports.
  say "4/4  loading the data and deploying the dashboards"
  cd "$DEMO_DIR"
  sh setup.sh < /dev/null
}

# Called last, so `curl | sh` has buffered the entire script before anything runs.
main "$@"
