# Exasol Local Starter Kit — a worked end-to-end demo

A real analytics stack on your laptop, start to finish: **install a local Exasol
database, connect your AI assistant to it over MCP, load a dataset, add the
dash-server add-on, and finish on five role-specific dashboards** built on top
of it.

Everything ships in this repo — the data, the SQL, the boards, and a presenter's
talk track. One command runs the whole chain.

---

## What the Starter Kit is

The [Exasol Personal Local Starter Kit](https://github.com/exasol/local-agent-ready-starter)
puts a full Exasol database on your own machine, with the pieces around it
already wired up:

| | What it gives you |
|---|---|
| **A local database** | Exasol Personal — a full Exasol database running on your own machine. `exakit start`, `exakit status`. No cloud account, no VPN, no data request. |
| **Your AI, connected** | `exakit mcp-setup` registers the database with Claude, Claude Code, Cursor, Codex and others over MCP — as a dedicated **read-only** user, so plain-English questions become SQL you can read before it runs. |
| **Data loading** | `exapump` for CSV and Parquet, `exakit data-load` for the guided path, and a JSON Tables add-on that shreds nested documents into relational tables. |
| **Add-ons** | A marketplace: **dash-server** (agent-built dashboards), VS Code, dbt, a scheduler. |

The kit is the product. **This repo is a demo of it** — a complete, honest
worked example you can run, read and re-present.

## What this demo runs, end to end

| Stage | Kit component | What you see |
|---|---|---|
| 1. Database | Exasol Personal | A real columnar database, running locally |
| 2. Load | `exapump upload` | 51,290 order lines into a typed table, in seconds |
| 3. Model | plain SQL | One view is the single seam between the data and everything above it |
| 4. Verify | `exapump sql` | The load reproduces published totals, or the run stops |
| 5. Deploy | **dash-server's MCP control plane** | `deploy_dashboard.py` is an MCP client — it validates the profile, lists apps and pushes the dashboard as tool calls |
| 6. Serve | dash-server | Five persona dashboards on `:5100`, reading as the kit's read-only user |
| 7. Ask | the kit's MCP server | Your AI assistant queries the same database in plain English, and shows the SQL |

Stages 1–6 are what `setup.sh` automates. Stage 7 is the kit feature you
demonstrate live from your own AI client — nothing in this repo has to script it.

---

## The problem this speaks to

Worth stating, because the demo is evidence for an argument.

**Trying anything is slow.** Testing an idea against real data usually means a
cloud account, a credit card, a VPN and a wait — so most questions never get
asked. A database on your laptop changes what it costs to be curious.

**Every team brings a different number to the same meeting.** Finance has a
margin figure, Sales has a margin figure, both are defensible, because each was
cut from a different extract on a different schedule. The meeting becomes about
whose spreadsheet is right instead of what to do.

**Dashboards answer questions they should refuse.** Give a BI tool a dimension
and it ranks it — even when the spread between first and last is rounding.
Somebody then acts on that ranking. And a margin number looks equally
authoritative whether or not there is any cost data behind it.

The five boards at the end of this demo are built as the answer to the last two:
one filter bar shared across all five roles so their numbers cannot diverge, and
boards that say out loud when a dimension is *not* a lever and when the data
cannot answer at all.

## Run it

```sh
git clone https://github.com/yuvi-ex/demoasset-starterkit-dashserver.git superstore-demo
cd superstore-demo
sh setup.sh
```

Then open **http://127.0.0.1:5100/apps/superstore-boards**

`setup.sh` checks prerequisites, creates the table, loads the data, builds the
view, verifies the totals, dry-runs all 26 queries against live data, deploys
only if every contract holds, then fires the real callback for all five boards
and prints **GO / NO-GO**. It is idempotent — rerun it rather than unpicking
anything.

**Presenting it?** The talk track — the whole arc, beat by beat, what to type,
what to click, what to say, and the questions you will get — is in
**[DEMO.md](DEMO.md)**.

### Prerequisites

The starter kit with the `dash-server` add-on. Nothing else — the data is in the
repo.

```sh
# the kit: local Exasol, exapump, and the MCP bridge
curl -fsSL https://raw.githubusercontent.com/exasol/local-agent-ready-starter/main/install.sh | sh

# connect your AI assistant to the database (stage 7)
exakit mcp-setup

# the dashboard host add-on (stages 5-6)
EXAKIT_MARKETPLACE_ADDONS=dash-server exakit marketplace
```

Budget ~10 minutes for the kit once, then ~2 minutes for `setup.sh`. The **Ask**
panel inside the dashboards additionally wants an `ANTHROPIC_API_KEY` (env var,
or `~/.exasol-starter-kit/credentials/anthropic_api_key`); everything else works
offline.

### Before you present

```sh
~/.exasol-starter-kit/dash-server-venv/bin/python3 preflight.py superstore-boards
```

Walks the exact chain the audience will exercise — database up → data present →
dash-server up → credential valid → app healthy → callbacks return real numbers
→ filters bite → latency — and every failure line names the command that fixes
it. It also *repairs* the one thing known to rot on its own: dash-server's own
copy of the read-only password, which a kit reinstall silently invalidates.

---

## The payoff: five roles, one database

Five dashboards, each genuinely different — the CFO wants a P&L, the project
manager wants an exception list. What they share is **scope**: one filter bar
across all five tabs. Filter on the Data Scientist tab, switch to Finance, and
the scope comes with you, so both boards are describing exactly the same rows.

The findings below are **measured from this data**, not illustrative.
`sql/03_verify.sql` prints the totals your own load must reproduce.

| Board | Owns | Opens on |
|---|---|---|
| **Finance Manager** | the P&L | $1.93M of revenue discounted past 20% produces **−$814.7K** of profit — 56% of everything the book earns |
| **Sales Manager** | the book and territories | SE Asia closes at 2.0% margin on 27.2% discount; North Asia at 19.5% on 4.9% |
| **Project Manager** | delivery execution | adherence is fine (0.2% off plan) — but **12,275 urgent lines shipped on slow modes** |
| **Data Scientist** | is there a model | R² = 0.718 from one feature, and why you must not price from it |
| **Product Manager** | the catalogue | **28.1% of products lose money**; margin runs inverse to discount |

---

## Making it your own

Three levels, cheapest first. The first two need no code.

1. **Change the scope.** Filter to one market or year before you present, so the
   numbers are closer to your audience's world. Every finding recomputes live.
2. **Repoint the view.** `sql/02_view.sql` is the *only* seam — nothing in
   `app.py` or the 26 query files touches the base table. Point it at your own
   table with matching column names and all five boards follow. Load your data
   with `exapump upload` (CSV/Parquet) or the JSON Tables add-on for documents.
3. **Change a board.** Each persona in the `PERSONAS` registry in `app.py` is
   five SQL files plus three builders (tiles, insights, figures). Add or swap
   one, then run `dryrun.py` — it checks every contract before anything deploys.

## Layout

```
setup.sh                     one command: prerequisites to verified deploy
DEMO.md                      the talk track for presenting the whole arc
data/superstore.csv          51,290 order lines, 2011-2014, 7 markets
sql/01_schema.sql            typed base table STARTER_KIT.SUPERSTORE_SRC
sql/02_view.sql              the SUPERSTORE view every query reads
sql/03_verify.sql            the figures your load must reproduce
superstore-boards/
  app.py                     five persona boards, one registry
  queries/business/*.sql     26 queries, five per board
  queries/sql_smoke.json     dry-run params (key order is POSITIONAL)
  llm_sql.py                 the Ask panel's SQL generator
board.py  harness.py         shared chrome: tiles, insights, charts, export
dryrun.py                    runs all 26 queries + contract checks, no deploy
ship.sh                      dry run, then deploy only if everything holds
preflight.py                 fires the real callbacks; GO / NO-GO
deploy_dashboard.py          the MCP client that pushes the app to dash-server
fix_dash_profile.py          re-syncs dash-server's copy of the read-only secret
```

## Working on it

```sh
# run every query and check every contract against live data, without deploying
~/.exasol-starter-kit/dash-server-venv/bin/python3 dryrun.py superstore-boards

# dry run, then deploy only if all contracts hold
sh ship.sh superstore-boards

# fire the real callback for all five boards and read the numbers back
~/.exasol-starter-kit/dash-server-venv/bin/python3 preflight.py superstore-boards
```

`dryrun.py` catches the failures a healthcheck passes over — an unknown insight
tone (bare HTTP 500), figure keys the export ignores (charts silently vanish),
`<> ''` in a filter query (every dropdown empty, every probe green). It also
prints the finding text, because a finding can satisfy every contract and still
say something false.

Three did, and they are the reason to trust the rest:

1. **A tiny group became the benchmark.** Canada is 201 orders and 0.5% of
   revenue at a 0% average discount, hence a 26.6% margin. Ranked naively it
   became the comparator for every market, so two boards told managers owning a
   third of the book to be more like a rounding error. Benchmarks now require a
   2%-of-revenue share — charts still show every row.
2. **The fastest option is not the available option.** The routing finding
   compared 12,275 misrouted lines against Same Day at 0.04 days — a service
   carrying 5.3% of volume. Requiring a 10% share picks First Class (2.18d),
   which is advice someone can act on.
3. **A self-contradicting residual.** Picking the largest residual globally
   landed on the 80%-discount tail (316 lines) under copy reading "worst exactly
   where the volume is". Restricting to bins holding ≥5% of rows surfaces the
   real finding: +20.5pp at 20% discount, on 4,998 lines.

If two persona lines in `preflight.py` ever print *identical* KPIs, that board
was never rendered — an unknown persona key falls back to the default instead of
erroring.

## Data

Global Superstore, a widely circulated retail sample: 51,290 order lines, 25,035
orders, 1,590 customers, 10,292 products, 7 markets, 147 countries, 2011-01-01
to 2014-12-31. Exported here as a typed CSV with ISO dates, so it loads with one
`exapump upload` and no preprocessing.

Sample data for demonstration purposes. `LICENSE` covers the code in this repo.
