# Demo script — the Starter Kit, end to end

A talk track you can run as-is: a database on a laptop, an AI connected to it,
data loaded, dashboards deployed, and five roles finally agreeing on a number.

Everything below is on the screen in front of you. Nothing needs to be
memorised, and every figure quoted here is one the tools print.

Written to be run by anyone, anywhere — a meetup, a customer session, a
classroom, an internal brown-bag. Nothing depends on a particular company,
industry or region.

| Run | Time | Beats |
|---|---|---|
| **Full arc** | 20 min | 1–10 |
| **Core** | 12 min | 1, 3, 4, 6, 8, 9, 10 |
| **Dashboards only** | 8 min | 5–10 |
| **Kit only** | 8 min | 1–4, 10 |

---

## Start here: what you are arguing

A demo that only shows features is forgettable. This one is evidence for a
claim, so know the claim before you open anything.

**Trying anything is slow.** Testing an idea against real data normally means a
cloud account, a credit card, a VPN and a wait — so most questions never get
asked at all. The kit's argument is that a real database on your own machine
changes what it costs to be curious.

**And when the data does arrive, teams still disagree.** Finance has a margin
figure, Sales has a margin figure, both defensible, each cut from a different
extract on a different schedule. The meeting becomes about whose spreadsheet is
right instead of what to do.

**Meanwhile dashboards answer questions they should refuse.** Give a BI tool a
dimension and it ranks it, even when the spread is rounding. Somebody acts on
that ranking.

**The arc you are about to run:** install → connect → load → ask → deploy →
five roles, one scope, on boards that admit what they cannot see.

### Know your room

| Audience | Lead with | Lean into | Safe to skip |
|---|---|---|---|
| Business / exec | Beat 6, the money | Beats 8 and 9 | Beats 2, 4 |
| Data / platform | Beats 1–4, the stack | Beat 3 (MCP), Beat 4 (deploy) | some of Beat 7 |
| Developers | Beat 3, then Beat 4 | Beat 12 (residuals) | Beat 7 |
| Students / general | Beats 1 and 9 | Beat 9 — honesty about limits | Beats 11–13 |
| Mixed meetup | Run 1–10 straight | Beat 8 is the moment | — |

---

## Before you go on

Ten minutes before, on the machine you will present from:

```sh
cd superstore-demo
~/.exasol-starter-kit/dash-server-venv/bin/python3 preflight.py superstore-boards
```

Wait for `GO`. On `NO-GO`, every failure line names the command that fixes it.

Then one minute of setup that saves the demo:

1. Open **http://127.0.0.1:5100/apps/superstore-boards**, click each of the five
   tabs once, come back to Finance. The first render warms the query path — do
   it now, not in front of people.
2. Click **Share** on the tabs you plan to show and keep the downloaded HTML
   files. Each is self-contained, with **no database behind it**. If anything
   dies mid-demo, open one and keep talking.
3. If you are running Beat 3, check your AI client is connected: `exakit
   mcp-doctor`. It is the one beat that depends on another application.
4. Decide about the dashboards' **Ask** panel — the only feature that touches the
   internet, so on venue wifi it is first to go. If preflight flagged it, do not
   click it; nothing else depends on it.
5. Browser zoom ~80% so all five KPI tiles and the tab bar are on one screen.

**Reset between runs:** clear the four filter dropdowns, return to Finance. There
is no other state.

---

# Act 1 — The kit

## Beat 1 — There is a database on this laptop (90s)

**Do:** Terminal, full screen.

```sh
exakit status
exakit info
```

**Say:**

> That is a full Exasol database — columnar, the same engine that runs in
> production — and it is running on this machine. No cloud account, no credit
> card, no VPN, no ticket to a data team.
>
> It went on with one install command, and it starts and stops like any other
> local service. The reason that matters is not cost. It is that the gap between
> "I wonder if" and "here is the answer" collapses. Most analytics questions
> never get asked because asking them is a project.

If someone asks about platform: macOS runs it natively, Linux and Windows get a
container. Same commands either way.

## Beat 2 — Data in, typed, in seconds (90s)

*Skip for a business audience — go to Beat 3.*

**Do:**

```sh
exapump upload -p starter-kit --table STARTER_KIT.SUPERSTORE_SRC data/superstore.csv
```

**Say:**

> 51,290 order lines going into a typed table. Not a staging area, not a
> notebook — a real table with real types.
>
> `exapump` takes CSV and Parquet. If your data is nested documents, the kit has
> a JSON Tables add-on that shreds them into relational tables instead, so you
> are not hand-writing flatteners.

**Do:** Show `sql/02_view.sql` on screen briefly.

**Say:**

> And then one view. Everything above this — 26 queries, five dashboards — reads
> this view and nothing else. That is the seam. Swap what is underneath it and
> the whole stack follows, which is how you would point this at your own data.

## Beat 3 — Now ask it in English (3 min)

The beat that lands hardest with technical audiences.

**Do:** Switch to your AI client (Claude Code, Claude Desktop, Cursor — whatever
`exakit mcp-setup` registered). Ask, in plain English:

> *What tables are in the STARTER_KIT schema, and what does SUPERSTORE contain?*

then

> *What is the average margin by discount band in SUPERSTORE?*

**Say, while it works:**

> The kit registered the database with my assistant over MCP. So it can see the
> schema, write the SQL, and run it — against the database on this laptop, not
> against a copy of it.
>
> Two things to notice. **The SQL is on screen.** I can read it before I believe
> the answer — an answer you cannot audit is a rumour with a chart on it.
>
> And it connects as a **dedicated read-only user** the kit created. This is not
> an assistant with admin rights on my database. It can ask. It cannot change
> anything.

**Do:** Point at the discount-band numbers it returns.

**Say:**

> Hold that shape in mind. In about five minutes you will see it again, from five
> completely different directions.

*If your assistant is not connected, say so and skip — `exakit mcp-doctor`
diagnoses it afterwards. Do not debug live.*

---

# Act 2 — dash-server

## Beat 4 — The add-on, and how the app gets there (2 min)

**Say:**

> Everything so far is the base kit. Dashboards are an add-on — one marketplace
> command — and this is the part people usually assume is a product you buy.

**Do:** Show `deploy_dashboard.py` on screen, around the `call(...)` lines.

**Say:**

> This is the deploy script, and it is worth ten seconds of your attention: it is
> an **MCP client**. It validates the database profile, lists what apps exist and
> pushes the dashboard — all as tool calls, over the same kind of interface my
> assistant used a minute ago.
>
> Which means the deployment path is one an agent can drive. I am running it from
> a shell because that is reproducible on stage; it did not have to be.

**Do:** Run it, or show the tail of `setup.sh` output.

```sh
sh ship.sh superstore-boards
```

**Say:**

> And it refuses to deploy if anything is broken. It dry-runs all 26 queries
> against the live database first, checks every contract, and only promotes if
> they hold. A broken board never reaches the browser.

---

# Act 3 — The payoff

## Beat 5 — What you are looking at (60s)

**Do:** Browser, Finance Manager tab. Point at the tab bar, the filter bar, the
tiles.

**Say:**

> Five tabs: Finance, Sales, Project, Data Scientist, Product. Five different
> jobs, five different boards — reading the database you watched me load.
>
> And **one** filter bar, shared across all of them. That last part is the whole
> point, and I will come back to it. Hold this question: what would it take for
> these five people to bring the same number to a meeting?

## Beat 6 — The finding (2 min)

The spine. Do not rush it.

**Do:** Point at the third KPI tile — **"Given away past 20% discount"**,
reading **−$814.7K** on $1.93M of revenue. Then the **Profit** tile: $1.47M.

**Say:**

> The catalogue earns $1.47 million of profit. Revenue discounted past 20%
> destroys $814.7 thousand of it. Fifty-six percent of everything this business
> makes, given away at the discount desk.

**Do:** Scroll to the **margin by discount band** chart.

**Say:**

> Here is why — and you saw these numbers in the terminal five minutes ago. No
> discount: 25.3% margin. One to ten: 17.2%. Eleven to twenty: 9.9%. Then
> twenty-one to thirty: **minus 5.5%**. Breakeven is inside that band. Past
> forty, margin is minus 74.
>
> That is a cliff, not a slope. And margin holds between 11 and 12 percent across
> all four years, so this is not one bad quarter — it is a standing policy
> working exactly as written.

**The closer.** Hold for it:

> The defence of deep discounting is always volume: we give margin away, we get
> units back. In this data the correlation between quantity and discount is
> **minus 0.02**. Discounting buys no volume here. So the margin it destroys is
> not being recovered anywhere.

## Beat 7 — The same fact, five times (3 min)

**Do:** Click the tabs. Do **not** touch the filters yet. One sentence each.

| Tab | Point at | Say |
|---|---|---|
| **Sales Manager** | Territory chart | "Southeast Asia closes at 2.0% margin on 27.2% average discount. North Asia: 19.5% on 4.9%. Same catalogue. The gap is discount, and it is monotone." |
| **Project Manager** | "Off plan" 0.2%, then "Priority/mode mismatch" | "Schedule adherence is fine — 0.2% off plan. The problem is routing: **12,275 lines** of Critical and High priority work moved on Second or Standard Class. Not a speed problem, a dispatch-rules problem." |
| **Product Manager** | "Loss-making products" 28.1% | "Twenty-eight percent of the catalogue loses money. The worst 1,303 products carry a 42.1% average discount; those above +30% margin carry 7.5%. Inverse and clean." |
| **Data Scientist** | R² tile | "Ask whether margin is predictable: R² of 0.718 — from **one** feature. Discount. Nothing else is close: sales 0.074, freight 0.068, quantity 0.050." |

**Say:**

> Four people, four jobs, four dashboards — and they just told you the same
> thing. Nobody coordinated that. It is one database, so there is one answer in
> it.

## Beat 8 — The live proof (90s)

The moment that separates this from a slide. If you get one beat right, this one.

**Do:** On the Data Scientist tab, open the **Market** filter and pick one —
**APAC**, or whichever is closest to your audience. Numbers redraw. Call out the
latency.

**Say:**

> 51,290 rows re-aggregated, five queries, a regression refitted on the filtered
> scope — locally, in well under a second.

**Do:** Now, **without touching the filters**, click back to **Finance**.

**Say:**

> Watch this. I have not touched the filter. The scope came with me. So the CFO's
> profit number and the data scientist's R² are now describing **exactly the same
> rows** — and I can say that with certainty rather than hoping two extracts were
> cut the same way.
>
> That is the meeting I described at the start. This is what it takes to have it.

**Do:** Clear the filter.

## Beat 9 — The board refuses to answer (2 min)

Usually where the room leans in. Do not skip it, even in a short run.

**Do:** Scroll to the **refusals** panel (on every tab).

**Say:**

> Most dashboards rank anything you give them. Ask "which segment should we
> push?" and you get a league table with a winner at the top, and somebody acts
> on it.
>
> This one refuses. Consumer 11.51%, Corporate 11.54%, Home Office 11.99% — a
> **0.48 point** spread. Ranking that manufactures a winner out of rounding
> error. So the board says it outright: segment is not a margin lever here.
> Discount is.
>
> Same for freight — flat, 10.4 to 11.3% of sales in every market. Same for ship
> lag — 3.68 to 4.01 days across all seven markets. Dead ends, named as dead
> ends, instead of sending someone to chase one.

**Do:** Scroll to the **limits** panel.

**Say:**

> And this one, on every board. There is no cost of goods in this data. So these
> boards can tell you how much margin a discount destroyed — not how much was
> left, or where the real floor is. No delivery date either, so cycle time is
> order-to-dispatch and on-time performance simply is not measurable here.
>
> A dashboard that hides what it cannot see is worse than no dashboard, because
> someone will eventually ask it that question and believe the answer.

## Beat 10 — Close (60s)

**Say:**

> What you actually watched: a database installed on a laptop, an assistant
> connected to it with read-only rights, 51,290 rows loaded, a dashboard deployed
> over a machine interface, and five role-specific boards that share one scope
> and admit what they cannot see. No cloud, no network, sub-second.
>
> The kit is one install command. This demo is a git clone and one more. You can
> be looking at it on your own machine in about ten minutes — and at your own
> data by rewriting a single SQL view.

**Do:** Show the README quickstart block, or the terminal.

---

## Optional beats

### Beat 11 — Ask the data, inside the dashboard (2 min)

*Skip if preflight flagged it or the wifi is bad.*

**Do:** Right-hand panel. Type: `profit by sub-category where discount over 30%`

**Say:**

> Same idea as the assistant earlier, now inside the board for someone who will
> never open a terminal. It writes the SQL, runs it read-only, and shows you
> both.

Good follow-ups: `average discount by market`, `top 10 loss-making products`.
Two questions maximum — it is a garnish.

### Beat 12 — The model argues with itself (2 min)

For a technical room. Data Scientist tab.

**Say:**

> R² of 0.718 off one feature. In most rooms that ends the conversation and
> somebody starts pricing from the line.
>
> Look at the residual table. At exactly 20% discount the fit predicts minus 5.9%
> and the data shows **plus 14.7%** — a twenty-point miss, on 4,998 lines.
>
> Discounts cluster on round numbers, so the rates carrying the most volume are
> precisely where the linear model is worst. The board reports the R² **and**
> tells you not to price from it: use the bands. The residual table is not a
> failure report, it is the feature-engineering queue.

### Beat 13 — Share and take it away (60s)

**Do:** Click **Share**. Open the downloaded file.

**Say:**

> Self-contained HTML — charts, numbers, findings, limits panel. No database
> behind it. That is what you send to someone who will not install anything, and
> it is my fallback if this laptop gives up mid-demo.

---

## Q&A bank

**"Is this a toy database?"**
> No. It is Exasol's engine running locally — the same columnar engine, sized for
> one machine. That is why 51,290 rows re-aggregate in under a second, and why
> the SQL you write here is the SQL you would write against a cluster.

**"Is this real data?"**
> Global Superstore, a widely circulated retail sample — real shape, not a real
> company. Every number on screen is computed from it; nothing is hard-coded. The
> repo ships a verify script printing the totals your own load must reproduce.

**"Is the AI running my database?"**
> It is connected as a read-only user the kit creates for exactly this. It can
> read the schema and run SELECTs. It cannot write, drop or grant. And every
> statement it writes is on screen before it runs.

**"Does any of this need the cloud?"**
> The database, the loading, the dashboards and all five boards are local. Two
> optional things call out: your AI assistant, and the dashboards' Ask panel.
> Both can be skipped.

**"How long to stand this up?"**
> The kit, about ten minutes, once. Then clone and `sh setup.sh` — about two
> minutes, idempotent, so a failed run is just rerun.

**"Can I point it at our data?"**
> Load it with `exapump` (CSV/Parquet) or the JSON Tables add-on (documents),
> then rewrite one view — `sql/02_view.sql` is the only seam. Match the column
> names and all five boards follow. `dryrun.py` then checks every query against
> your data before anything deploys.

**"Why five dashboards instead of one with a role filter?"**
> They are genuinely different questions — the CFO wants a P&L, the PM wants an
> exception list. What they share is scope, not layout.

**"How is this different from [BI tool]?"**
> Not a BI pitch. It is a database fast enough to answer five roles interactively
> on a laptop, a deployment path an agent can drive, and boards that state their
> own limits. If they push: ~3,500 lines of Python and SQL in the repo, entirely
> readable and entirely yours.

**"What's the catch on 28% of products losing money?"**
> Booked profit over booked sales, no cost of goods in the data. So it is "this
> product, as sold, did not cover what we recorded against it" — a repricing
> worklist, not a gross-margin statement. The board says so itself.

---

## If something breaks

| Symptom | Do this |
|---|---|
| Database not responding | `exakit status`, then `exakit start` |
| AI client sees no database | `exakit mcp-doctor`. Skip Beat 3 rather than debugging live |
| Page blank or 500 | `preflight.py superstore-boards` — it repairs the stale dash-server credential, the usual cause |
| Every dropdown empty | Same command. It catches this specifically; a healthcheck will not |
| Tabs show identical numbers | A board did not render. Reload; if it persists, `sh ship.sh superstore-boards` |
| Ask panel hangs | Stop clicking it and carry on. Nothing else depends on it |
| Anything else, mid-sentence | Open the Share snapshot you saved beforehand. Keep talking |

**The rule under pressure:** do not debug in front of the room. Open the
snapshot, finish the story, fix it afterwards.
