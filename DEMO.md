# Demo script — Global Superstore, five personas on a local Exasol

A talk track you can run as-is. Everything below is on the screen in front of
you; nothing needs to be memorised, and every number quoted here is a number the
boards print.

- **Core demo: 10 minutes.** Beats 1–6.
- **Short version: 4 minutes.** Beats 1, 2, 4, 6.
- **Long version: 20 minutes.** Add beats 7–9 and the Q&A bank.

Audience: anyone who has ever been in a meeting where two teams brought
different numbers for the same month.

---

## Before you go on

Ten minutes before, on the machine you will present from:

```sh
cd vitdemoasset
~/.exasol-starter-kit/dash-server-venv/bin/python3 preflight.py superstore-boards
```

Wait for `GO`. On `NO-GO`, every failure line tells you the command to run.

Then, one minute of setup that saves the demo:

1. Open **http://127.0.0.1:5100/apps/superstore-boards**. Let all five tabs load
   once — click each, come back to Finance. The first render of each board warms
   the query path; do it now rather than in front of people.
2. Click **Share** on the Finance tab and keep the downloaded HTML file. It is a
   self-contained snapshot with the charts and numbers baked in and **no
   database behind it**. If anything dies mid-demo, open that file and keep
   talking. Do this for any tab you plan to show.
3. Decide whether you are using the **Ask** panel. It is the only feature that
   touches the internet, so on venue wifi it is the first thing to go. If
   preflight flagged it, just do not click it — nothing else depends on it.
4. Browser zoom to ~80% so all five KPI tiles and the tab bar are on one screen.

**Reset between runs:** clear all four filter dropdowns and click back to the
Finance tab. There is no other state.

---

## The one-line framing

> "Five roles. One database. One filter bar. Watch them agree."

Say it before you show anything. Everything after this is evidence for that
sentence.

---

## Beat 1 — What you are looking at (60s)

**Do:** Land on the Finance Manager tab. Point at the tab bar, then the filter
bar, then the tiles.

**Say:**

> This is one order book — 51,290 lines, four years, seven markets — running on
> an Exasol database on this laptop. Not a cloud account, not a warehouse bill.
> The whole thing installs from one command.
>
> Five tabs: Finance, Sales, Project, Data Scientist, Product. Five different
> jobs. And **one** filter bar, shared across all of them.
>
> That last part is the entire point. Normally each of these five people has
> their own extract, refreshed on their own schedule, and by the time they are in
> the same room the numbers no longer reconcile — so the meeting is about whose
> spreadsheet is right instead of what to do. Here they are five questions asked
> of the same rows at the same instant.

---

## Beat 2 — The finding (2 min)

This is the spine. Do not rush it.

**Do:** On Finance, point at the third KPI tile: **"Given away past 20%
discount"**, reading **−$814.7K** on $1.93M of revenue. Then point at the
**Profit** tile: $1.47M.

**Say:**

> The catalogue earns $1.47 million of profit. Revenue discounted past 20%
> destroys $814.7 thousand of it. Fifty-six percent of everything this business
> makes, given away at the discount desk.

**Do:** Scroll to the **margin by discount band** chart.

**Say:**

> Here is why. No discount: 25.3% margin. One to ten percent: 17.2%. Eleven to
> twenty: 9.9%. And then twenty-one to thirty: **minus 5.5%**. Breakeven is
> inside that band. Past forty percent, margin is minus 74.
>
> That is a cliff, not a slope. And it is not a story about one bad quarter —
> margin holds between 11 and 12 percent across all four years. This is a
> standing policy working exactly as written.

**The closer.** Hold for it:

> The defence of deep discounting is always volume — we give margin away, we get
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
| **Project Manager** | "Off plan" 0.2% then "Priority/mode mismatch" | "Schedule adherence is fine — 0.2% off plan. The problem is routing: **12,275 lines** of Critical and High priority work moved on Second or Standard Class. That is not a speed problem, it is a dispatch-rules problem." |
| **Product Manager** | "Loss-making products" 28.1% | "Twenty-eight percent of the catalogue loses money. The worst 1,303 products carry a 42.1% average discount; the products above +30% margin carry 7.5%. Inverse and clean." |
| **Data Scientist** | R² tile | "Ask a model whether margin is predictable and you get R² of 0.718 — from **one** feature. Discount. Nothing else is close: sales 0.074, freight 0.068, quantity 0.050." |

**Say, landing back:**

> Four people, four jobs, four dashboards — and they just told you the same
> thing. Nobody coordinated that. It is one dataset, so there is only one answer
> in it.

---

## Beat 4 — The live proof (90s)

The moment that separates this from a slide.

**Do:** Stay on the Data Scientist tab. Open the **Market** filter and select
**APAC** (or any market your audience cares about). Numbers redraw — call out
the latency.

**Say:**

> That is 51,290 rows re-aggregated, five queries, a regression refitted on the
> filtered scope — locally, in well under a second.

**Do:** Now, **without touching the filters**, click back to **Finance**.

**Say:**

> Here is the thing to watch. I have not touched the filter. The scope came with
> me. So the CFO's profit number and the data scientist's R² are now describing
> **exactly the same rows** — and I can say that with certainty rather than
> hoping two extracts were cut the same way.
>
> This is the conversation those five people cannot normally have.

**Do:** Clear the filter. Watch the totals return.

---

## Beat 5 — The board refuses to answer (2 min)

Usually the moment the room leans in. Do not skip it, even in a short run.

**Do:** Scroll to the **refusals** panel (present on every tab).

**Say:**

> Most dashboards will rank anything you give them. Ask "which segment should we
> push?" and you get a league table with a winner at the top, and somebody acts
> on it.
>
> This one refuses. Consumer 11.51%, Corporate 11.54%, Home Office 11.99% — a
> **0.48 point** spread across three segments. Ranking that manufactures a winner
> out of rounding error. So the board says it outright: segment is not a margin
> lever in this catalogue. Discount is.
>
> Same for freight — flat, 10.4 to 11.3% of sales in every market. Same for ship
> lag — 3.68 to 4.01 days across all seven markets. Those are dead ends, and the
> board tells you they are dead ends instead of sending someone off to chase one.

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

> To recap what you have actually seen: a local database on a laptop, no cloud
> and no network; 51,290 rows; five role-specific boards that share one scope;
> sub-second interaction; and findings that are measured rather than
> illustrative — including the ones that say *there is nothing here*.
>
> The whole thing is a git clone and one command, and the data ships in the repo.
> You can be looking at this on your own machine in about ten minutes.

**Do:** Show the terminal, scrolled to the three lines of `setup.sh` output, or
just show the README block.

If you want a call to action: point at the **repoint the view** paragraph in the
README — one SQL file is the only seam between these five boards and whatever
data the audience actually has.

---

## Beat 7 (optional) — Ask the data (2 min)

**Skip this if preflight flagged the Ask panel, or if the wifi is bad.** It is
the only part of the demo that leaves the machine.

**Do:** Right-hand panel. Type:

> `profit by sub-category where discount over 30%`

**Say:**

> This writes the SQL, runs it read-only against the same database, and shows
> you both. The SQL is on screen — that matters. An answer you cannot audit is a
> rumour with a chart on it.

**Good follow-ups that land:** `average discount by market`,
`top 10 loss-making products`. Keep it to two questions; it is a garnish, not
the demo.

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
> database behind it. That is what you email to someone who will not install
> anything, and it is also my fallback if this laptop gives up mid-demo.

---

## Q&A bank

**"Is this real data?"**
> It is Global Superstore, a widely circulated retail sample — real shape, not a
> real company. Every number on screen is computed from it; nothing is hard-coded
> or illustrative. The repo ships a verify script that prints the totals your own
> load has to reproduce.

**"How long does this take to stand up on my machine?"**
> Starter kit install, about ten minutes once. Then clone and `sh setup.sh` —
> about two minutes, and it is idempotent, so a failed run is just rerun.

**"Does it need the cloud?"**
> No. Database, dashboards and all five boards are local. The only outbound call
> in the whole asset is the optional Ask panel.

**"Can I point it at our data?"**
> One view. `sql/02_view.sql` is the only seam — nothing in the app or the 26
> queries touches the base table. Match the column names and all five boards
> follow. Then `dryrun.py` checks every query and every contract against your
> data before anything deploys.

**"Why five dashboards instead of one with a role filter?"**
> Because they are genuinely different questions — the CFO wants the P&L, the PM
> wants an exception list. What they share is scope, not layout. One app, five
> boards, one filter bar is exactly that split.

**"How is this different from [BI tool]?"**
> Not a BI tool pitch. The demo is about a database fast enough to answer five
> roles interactively on a laptop, and about boards that state their own limits.
> If they push: the boards are ~3,500 lines of Python and SQL in this repo,
> entirely readable and entirely yours.

**"What's the catch on 28% of products losing money?"**
> Booked profit over booked sales, with no cost of goods in the data. So it is
> "this product line, as sold, did not cover what we recorded against it" — a
> repricing worklist, not a gross-margin statement. The board says so in its own
> limits panel.

**"Could you not just fix the discounting?"**
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
| Tabs show identical numbers | A board did not render. Reload the page; if it persists, rerun `sh ship.sh superstore-boards` |
| Ask panel hangs or errors | Stop clicking it and carry on. It is the only networked feature and nothing else depends on it |
| Database refused on 8563 | `exakit status`, then `exakit start` |
| Anything else, mid-sentence | Open the Share snapshot you saved before you went on. Keep talking |

**The rule under pressure:** do not debug in front of the room. Open the
snapshot, finish the story, fix it afterwards.
