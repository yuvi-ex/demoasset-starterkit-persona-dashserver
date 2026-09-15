# Demo script — five roles, one database

A talk track you can run as-is. Everything below is on the screen in front of
you; nothing needs to be memorised, and every number quoted here is a number the
boards print.

Written to be run by anyone, anywhere — a meetup talk, a customer session, a
classroom, an internal brown-bag. Nothing in it depends on a particular company,
industry or region.

- **Core demo: 10 minutes.** Beats 1–6.
- **Short version: 4 minutes.** Beats 1, 2, 4, 6.
- **Long version: 20 minutes.** Add beats 7–9 and the Q&A bank.

---

## Start here: what you are arguing

A demo that only shows features is forgettable. This one is evidence for a
claim, so know the claim before you open the browser.

**The problem in the room.** Almost everyone you will present to has sat in a
meeting where two teams brought different numbers for the same month, and both
were defensible, because each was cut from a different extract on a different
schedule. The meeting then becomes about whose spreadsheet is right instead of
what to do — and nobody can settle it live, because settling it means
re-deriving both numbers from the same rows.

**The second problem, quieter and worse.** Dashboards rank whatever you give
them. Ask which segment to push and you get a winner at the top, even when the
spread is a third of a percentage point. Somebody acts on it. And a margin
number looks equally authoritative whether or not there is any cost data behind
it.

**What you are showing.** Five roles reading one database through one shared
filter bar — so their numbers cannot diverge — on boards that say out loud when
a dimension is not a lever and when the data cannot answer at all. Running on a
laptop, so trying it costs nothing.

**The one-liner. Say it before you show anything:**

> "Five roles. One database. One filter bar. Watch them agree."

### Know your room

| Audience | Lead with | Lean into | Safe to skip |
|---|---|---|---|
| Business / exec | Beat 2, the money | Beat 4 (scope follows), Beat 5 (refusals) | Beat 8 |
| Data / engineering | Beat 4, then Beat 8 | Beat 8 (residuals), Beat 7 (Ask) | some of Beat 3 |
| Students / general | Beat 1 and Beat 5 | Beat 5 — honesty about limits | Beats 7–9 |
| Mixed meetup | Run 1–6 straight through | Beat 4 is the moment | — |

---

## Before you go on

Ten minutes before, on the machine you will present from:

```sh
cd superstore-demo
~/.exasol-starter-kit/dash-server-venv/bin/python3 preflight.py superstore-boards
```

Wait for `GO`. On `NO-GO`, every failure line tells you the command to run.

Then one minute of setup that saves the demo:

1. Open **http://127.0.0.1:5100/apps/superstore-boards**. Click each of the five
   tabs once and come back to Finance — the first render warms the query path.
   Do it now rather than in front of people.
2. Click **Share** on the tabs you plan to show and keep the downloaded HTML
   files. Each is a self-contained snapshot with the charts and numbers baked in
   and **no database behind it**. If anything dies mid-demo, open one and keep
   talking.
3. Decide whether you are using the **Ask** panel. It is the only feature that
   touches the internet, so on venue wifi it is the first thing to go. If
   preflight flagged it, just do not click it — nothing else depends on it.
4. Browser zoom to ~80% so all five KPI tiles and the tab bar are on one screen.

**Reset between runs:** clear all four filter dropdowns, click back to Finance.
There is no other state.

---

## Beat 1 — What you are looking at (60s)

**Do:** Land on the Finance Manager tab. Point at the tab bar, then the filter
bar, then the tiles.

**Say:**

> This is one order book — 51,290 lines, four years, seven markets — running on
> a database on this laptop. Not a cloud account, not a warehouse bill. The whole
> thing installs from one command.
>
> Five tabs: Finance, Sales, Project, Data Scientist, Product. Five different
> jobs. And **one** filter bar, shared across all of them.
>
> That last part is the entire point, and I will come back to it. Hold on to the
> question: what would it take for these five people to bring the same number to
> a meeting?

---

## Beat 2 — The finding (2 min)

This is the spine. Do not rush it.

**Do:** On Finance, point at the third KPI tile — **"Given away past 20%
discount"**, reading **−$814.7K** on $1.93M of revenue. Then the **Profit** tile:
$1.47M.

**Say:**

> The catalogue earns $1.47 million of profit. Revenue discounted past 20%
> destroys $814.7 thousand of it. Fifty-six percent of everything this business
> makes, given away at the discount desk.

**Do:** Scroll to the **margin by discount band** chart.

**Say:**

> Here is why. No discount: 25.3% margin. One to ten percent: 17.2%. Eleven to
> twenty: 9.9%. Then twenty-one to thirty: **minus 5.5%**. Breakeven is inside
> that band. Past forty percent, margin is minus 74.
>
> That is a cliff, not a slope. And it is not one bad quarter — margin holds
> between 11 and 12 percent across all four years. This is a standing policy
> working exactly as written.

**The closer.** Hold for it:

> The defence of deep discounting is always volume: we give margin away, we get
> units back. In this data, the correlation between quantity and discount is
> **minus 0.02**. Discounting buys no volume here. So the margin it destroys is
> not being recovered anywhere.

---

## Beat 3 — The same fact, five times (3 min)

**Do:** Click through the tabs. Do **not** touch the filters yet. One sentence
each; let the KPI tiles do the talking.

| Tab | Point at | Say |
|---|---|---|
| **Sales Manager** | Territory chart | "Southeast Asia closes at 2.0% margin on 27.2% average discount. North Asia: 19.5% margin on 4.9% discount. Same catalogue. The gap is the discount, and it is monotone." |
| **Project Manager** | "Off plan" 0.2%, then "Priority/mode mismatch" | "Schedule adherence is fine — 0.2% off plan. The problem is routing: **12,275 lines** of Critical and High priority work moved on Second or Standard Class. Not a speed problem, a dispatch-rules problem." |
| **Product Manager** | "Loss-making products" 28.1% | "Twenty-eight percent of the catalogue loses money. The worst 1,303 products carry a 42.1% average discount; the products above +30% margin carry 7.5%. Inverse and clean." |
| **Data Scientist** | R² tile | "Ask whether margin is predictable and you get R² of 0.718 — from **one** feature. Discount. Nothing else is close: sales 0.074, freight 0.068, quantity 0.050." |

**Say, landing back:**

> Four people, four jobs, four dashboards — and they just told you the same
> thing. Nobody coordinated that. It is one dataset, so there is only one answer
> in it.

---

## Beat 4 — The live proof (90s)

The moment that separates this from a slide. If you only get one beat right,
this is it.

**Do:** Stay on the Data Scientist tab. Open the **Market** filter and pick one
— **APAC**, or whichever is closest to your audience. Numbers redraw. Call out
the latency.

**Say:**

> That is 51,290 rows re-aggregated, five queries, and a regression refitted on
> the filtered scope — locally, in well under a second.

**Do:** Now, **without touching the filters**, click back to **Finance**.

**Say:**

> Here is the thing to watch. I have not touched the filter. The scope came with
> me. So the CFO's profit number and the data scientist's R² are now describing
> **exactly the same rows** — and I can say that with certainty, rather than
> hoping two extracts were cut the same way.
>
> That is the meeting I described at the start. This is what it takes to have it.

**Do:** Clear the filter. Watch the totals return.

---

## Beat 5 — The board refuses to answer (2 min)

Usually the moment the room leans in. Do not skip it, even in a short run.

**Do:** Scroll to the **refusals** panel (on every tab).

**Say:**

> Most dashboards rank anything you give them. Ask "which segment should we
> push?" and you get a league table with a winner at the top, and somebody acts
> on it.
>
> This one refuses. Consumer 11.51%, Corporate 11.54%, Home Office 11.99% — a
> **0.48 point** spread across three segments. Ranking that manufactures a winner
> out of rounding error. So the board says it outright: segment is not a margin
> lever here. Discount is.
>
> Same for freight — flat, 10.4 to 11.3% of sales in every market. Same for ship
> lag — 3.68 to 4.01 days across all seven markets. Those are dead ends, and the
> board tells you they are dead ends instead of sending someone to chase one.

**Do:** Scroll to the **limits** panel.

**Say:**

> And this one, on every board. There is no cost of goods in this data. So these
> boards can tell you how much margin a discount destroyed — they cannot tell you
> how much was left, or where the real floor is. There is no delivery date
> either, so cycle time is order-to-dispatch, and on-time performance against a
> customer promise is simply not measurable here.
>
> A dashboard that hides what it cannot see is worse than no dashboard, because
> someone will eventually ask it that question and believe the answer.

---

## Beat 6 — Close (60s)

**Say:**

> To recap what you actually saw: a database on a laptop, no cloud and no
> network; 51,290 rows; five role-specific boards that share one scope;
> sub-second interaction; and findings that are measured rather than
> illustrative — including the ones that say *there is nothing here*.
>
> The whole thing is a git clone and one command, and the data ships in the
> repo. You can be looking at this on your own machine in about ten minutes.

**Do:** Show the terminal, or just the README quickstart block.

If you want a call to action: point at **"Making it your own"** in the README —
one SQL file is the only seam between these five boards and whatever data your
audience actually has.

---

## Beat 7 (optional) — Ask the data (2 min)

**Skip if preflight flagged the Ask panel, or the wifi is bad.** It is the only
part of the demo that leaves the machine.

**Do:** Right-hand panel. Type:

> `profit by sub-category where discount over 30%`

**Say:**

> This writes the SQL, runs it read-only against the same database, and shows
> you both. The SQL being on screen is the point. An answer you cannot audit is
> a rumour with a chart on it.

**Good follow-ups:** `average discount by market`, `top 10 loss-making
products`. Keep it to two questions; it is a garnish, not the demo.

---

## Beat 8 (optional) — The model argues with itself (2 min)

For a technical audience. Data Scientist tab.

**Say:**

> R² of 0.718 off one feature. In most rooms that ends the conversation and
> somebody starts pricing from the line.
>
> Look at the residual table. At exactly 20% discount the fit predicts minus
> 5.9% margin and the data shows **plus 14.7%** — a twenty-point miss. And 4,998
> lines sit on that single rate.
>
> Discounts cluster on round numbers. So the rates carrying the most volume are
> precisely the ones the linear model gets most wrong. The board reports the R²
> **and** tells you not to price from it: use the bands. The residual table is
> not a failure report, it is the feature-engineering queue.

---

## Beat 9 (optional) — Share and take it away (60s)

**Do:** Click **Share**. A file downloads. Open it.

**Say:**

> Self-contained HTML — charts, numbers, the findings, the limits panel. No
> database behind it. That is what you send to someone who will not install
> anything, and it is also my fallback if this laptop gives up mid-demo.

---

## Q&A bank

**"Is this real data?"**
> Global Superstore, a widely circulated retail sample — real shape, not a real
> company. Every number on screen is computed from it; nothing is hard-coded or
> illustrative. The repo ships a verify script that prints the totals your own
> load has to reproduce.

**"How long to stand this up on my machine?"**
> The starter kit, about ten minutes, once. Then clone and `sh setup.sh` — about
> two minutes, and it is idempotent, so a failed run is just rerun.

**"Does it need the cloud?"**
> No. Database, dashboards and all five boards are local. The only outbound call
> in the whole asset is the optional Ask panel.

**"Can I point it at our data?"**
> One view. `sql/02_view.sql` is the only seam — nothing in the app or the 26
> queries touches the base table. Match the column names and all five boards
> follow. Then `dryrun.py` checks every query and every contract against your
> data before anything deploys.

**"Why five dashboards instead of one with a role filter?"**
> Because they are genuinely different questions — the CFO wants a P&L, the PM
> wants an exception list. What they share is scope, not layout. One app, five
> boards, one filter bar is exactly that split.

**"How is this different from [BI tool]?"**
> It is not a BI tool pitch. The demo is about a database fast enough to answer
> five roles interactively on a laptop, and about boards that state their own
> limits. If they push: it is ~3,500 lines of Python and SQL in this repo,
> entirely readable and entirely yours.

**"What's the catch on 28% of products losing money?"**
> Booked profit over booked sales, with no cost of goods in the data. So it is
> "this product line, as sold, did not cover what we recorded against it" — a
> repricing worklist, not a gross-margin statement. The board says so in its own
> limits panel.

**"Couldn't you just fix the discounting?"**
> That is the conversation the board is designed to start, and the honest answer
> is that this data cannot tell you the floor — no cost of goods. What it can
> tell you is that the volume defence does not hold here, which is usually the
> argument in the room.

---

## If something breaks

| Symptom | Do this |
|---|---|
| Page blank or 500 | `preflight.py superstore-boards` — it repairs the stale dash-server credential itself, which is the usual cause |
| Every dropdown empty | Same command. It catches this specifically; a healthcheck will not |
| Tabs show identical numbers | A board did not render. Reload; if it persists, rerun `sh ship.sh superstore-boards` |
| Ask panel hangs or errors | Stop clicking it and carry on. It is the only networked feature and nothing else depends on it |
| Database refused on 8563 | `exakit status`, then `exakit start` |
| Anything else, mid-sentence | Open the Share snapshot you saved before you went on. Keep talking |

**The rule under pressure:** do not debug in front of the room. Open the
snapshot, finish the story, fix it afterwards.
