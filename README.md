# Global Superstore — a five-persona demo on a local Exasol database

A runnable demo asset. One command turns a fresh clone into **five live
dashboards** — Finance Manager, Sales Manager, Project Manager, Data Scientist,
Product Manager — served on your own laptop from a local
[Exasol](https://github.com/exasol/local-agent-ready-starter) database, over one
51,290-line order book.

```sh
git clone https://github.com/yuvi-ex/vitdemoasset.git
cd vitdemoasset
sh setup.sh
```

Then open **http://127.0.0.1:5100/apps/superstore-boards**

Presenting it? The talk track — beat by beat, what to click, what to say, the
questions you will get and the answers — is in **[DEMO.md](DEMO.md)**.

## What this demo is actually showing

Not "here are five dashboards". Five roles, one database, **one shared filter
bar** — so a claim made on the Finance tab can be checked on the Data Scientist
tab at the identical scope, live, in front of the audience.

That is the point of the whole asset. These five roles normally cannot have that
conversation, because each one has their own extract, refreshed on their own
schedule, and by the time they are in the same room the numbers no longer
reconcile. Here they are five questions asked of the same rows at the same
moment, and the audience watches them agree.

Three things the demo is built to let you say out loud:

1. **One finding runs through all five boards.** A discount cliff at 20%. Every
   persona meets it from their own end — the CFO as $814.7K of given-away
   profit, the PM as a loss-making catalogue, the data scientist as R² = 0.718
   off a single feature. It is the same fact, five times.
2. **The boards refuse questions.** Where a dimension is flat, the board says
   *"this is not the lever"* instead of ranking it and inventing a leader. There
   is a panel of refusals on every tab. Demo that panel — it is usually the
   moment the room leans in.
3. **It runs on a laptop, offline.** No cloud account, no warehouse bill, no
   VPN. Sub-second filters on 51,290 rows against a local Exasol instance. Only
   the optional Ask panel touches the network.

## What each board opens on

The findings below are **measured from this data**, not illustrative. They are
what the boards will show on your machine, and `sql/03_verify.sql` prints the
totals your load must reproduce.

| Board | Owns | Opens on |
|---|---|---|
| **Finance Manager** | the P&L | $1.93M of revenue discounted past 20% produces **−$814.7K** of profit — 56% of everything the book earns |
| **Sales Manager** | the book and territories | SE Asia closes at 2.0% margin on 27.2% discount; North Asia at 19.5% on 4.9% |
| **Project Manager** | delivery execution | adherence is fine (0.2% off plan) — but **12,275 urgent lines shipped on slow modes** |
| **Data Scientist** | is there a model | R² = 0.718 from one feature, and why you must not price from it |
| **Product Manager** | the catalogue | **28.1% of products lose money**; margin runs inverse to discount |

### The discount cliff is the spine of the demo

Sales-weighted margin by discount band:

| Discount | None | 1–10% | 11–20% | 21–30% | 31–40% | 41%+ |
|---|---|---|---|---|---|---|
| Margin | 25.3% | 17.2% | 9.9% | **−5.5%** | −23.7% | −74.1% |

Breakeven falls inside 21–30%. Fitting line margin on discount alone gives
**R² = 0.718**, slope −1.859, fitted breakeven **16.8%**.

And the number that turns this from a trade-off into a straight loss:
**`corr(quantity, discount) = −0.02`**. Discounting buys no volume here, so the
margin it destroys is not being recovered anywhere in this data.

### What was ruled out rather than reported

A spread too small to survive rounding is reported as "this dimension is not the
lever", never ranked into a league table:

- **Segment is flat** — Consumer 11.51%, Corporate 11.54%, Home Office 11.99%.
  A 0.48pp spread. The boards say outright that segment is not a margin lever.
- **Freight is flat across markets** (10.4–11.3% of sales). Mode mix, not
  geography, is the lever.
- **Ship lag is flat across markets** (3.68–4.01 days on a 3.97-day mean).
- **Discounting did not drift** — margin holds at 11.0–12.0% across 2011–2014.
  The cliff is a standing policy, not a deterioration.

### The one place the model and the data disagree

On the board, deliberately. The linear fit's residuals are *structured*: at
exactly 20% discount the observed mean margin is +14.7% while the fit predicts
−5.9% — a +20.5pp miss, on 4,998 lines. Discounts cluster on round numbers, so
the rates carrying the most volume are the ones the fit gets most wrong. The
Data Scientist board reports R² = 0.718 **and** refuses to let it stand alone:
price from the bands, not the line.

### What this data cannot support

Every board carries this list in a panel, because a dashboard that hides its
limits is worse than no dashboard:

- **No cost of goods.** Margin is Profit/Sales *as booked*. These boards can say
  how much margin a discount destroyed; none can say how much was left.
- **No delivery date.** Cycle time is order-to-*dispatch*. On-time performance
  against a customer promise is not measurable here.
- **No list price, carrier, returns, or inventory.**
- **No project table.** The Project Manager board is order fulfilment, which is
  what this data supports. It is not portfolio management and does not pretend
  to be.

## Running it on your laptop

### Prerequisites

The [Exasol Personal Local Starter Kit](https://github.com/exasol/local-agent-ready-starter)
with the `dash-server` add-on. Nothing else — the data ships in this repo.

```sh
# the kit (installs Exasol locally, plus exapump and the MCP bridge)
curl -fsSL https://raw.githubusercontent.com/exasol/local-agent-ready-starter/main/install.sh | sh

# the dashboard host
EXAKIT_MARKETPLACE_ADDONS=dash-server exakit marketplace
```

macOS runs Exasol Personal natively; Linux, WSL and Windows get Exasol Nano in a
container. Either is fine. Budget ~10 minutes for the kit install the first
time, and about 2 minutes for `setup.sh` after that.

`setup.sh` checks for both prerequisites and tells you which one is missing
rather than failing obscurely. The **Ask panel** additionally wants an
`ANTHROPIC_API_KEY` (env var, or
`~/.exasol-starter-kit/credentials/anthropic_api_key`); everything else works
without it, and without any network at all.

### What `setup.sh` does

Creates the table, loads the data, builds the view, verifies the totals,
dry-runs all 26 queries against live data, deploys only if every contract holds,
then fires the real callback for all five boards and prints **GO / NO-GO**.

It is idempotent. If a step fails, fix the named cause and rerun the whole
thing — do not unpick anything.

### Before you present

```sh
~/.exasol-starter-kit/dash-server-venv/bin/python3 preflight.py superstore-boards
```

Run it ten minutes before you go on. It walks the exact chain the audience will
exercise — database up → data present → dash-server up → credential valid → app
healthy → callbacks return real numbers → filters bite → latency — and every
failure line says what to run. It also *repairs* the one thing known to rot on
its own: dash-server's own copy of the Exasol password, which a kit reinstall
silently invalidates.

## Layout

```
setup.sh                     one command, prerequisites to verified deploy
DEMO.md                      the talk track for presenting this
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
deploy_dashboard.py          pushes the app through the dash-server MCP plane
```

Nothing in `app.py` or the 26 query files touches `SUPERSTORE_SRC` directly.
`STARTER_KIT.SUPERSTORE` is the only seam, so **you can repoint these five
boards at your own data by rewriting one view** — which is itself a good thing
to say on stage.

## Making it your own

Three levels of customisation, cheapest first:

1. **Change the scope, not the code.** Filter to one market or one year before
   you present, so the numbers match your audience. Every finding recomputes.
2. **Repoint the view.** Rewrite `sql/02_view.sql` to select from your table
   with the same column names. The 26 queries and all five boards follow.
3. **Change a board.** Each persona in the `PERSONAS` registry in `app.py` is
   five SQL files plus three builders (tiles, insights, figures). Add or swap
   one, then run `dryrun.py` — it checks every contract before anything deploys.

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

Three did, and it is worth knowing what they were — they are the reason to
trust the rest:

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
