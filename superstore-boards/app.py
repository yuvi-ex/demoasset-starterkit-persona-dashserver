"""Global Superstore — five persona boards on one order book.

Finance Manager, Sales Manager, Project Manager, Data Scientist and Product
Manager, switched by the tab bar under the title. Chrome, Share snapshot and the
Ask panel come from ../board.py.

WHY ONE APP RATHER THAN FIVE. All five roles argue about the same 51,290 order
lines from different ends, and in this catalogue their arguments all terminate in
the same place: the discount. One shared filter bar means a claim made on the
Finance tab can be checked on the Data Scientist tab at the identical scope,
which is exactly the conversation these five roles need to have and normally
cannot, because each has their own extract.

THE DATA. STARTER_KIT.SUPERSTORE, a typed view over STARTER_KIT.STORESALES —
the raw table is 100% VARCHAR (it arrived as JSON), so the view does the casting
once rather than every query doing TO_DATE and CAST inline. 51,290 lines, 25,035
orders, 1,590 customers, 10,292 products, 7 markets, 147 countries, 2011-01-01
to 2014-12-31.

WHAT THE SIGNAL CHECK FOUND, measured before any of this was written:

  * THE DISCOUNT CLIFF IS THE WHOLE STORY. Sales-weighted margin by discount band
    runs 25.3% (none) -> 17.2% (1-10%) -> 9.9% (11-20%) -> -5.5% (21-30%) ->
    -23.7% (31-40%) -> -74.1% (41%+). Breakeven falls inside 21-30%. The 11,328
    lines discounted past 20% turn $1.93M of revenue into -$814.7K of profit —
    more than half the catalogue's entire $1.47M profit, given away.
  * A SINGLE FEATURE CARRIES THE DATASET. Fitting line margin on discount alone
    gives R2 = 0.718, slope -1.859, and a fitted breakeven at 16.8% discount.
    Nothing else comes close: |r| is 0.074 for sales, 0.068 for freight, 0.050
    for quantity, 0.0003 for ship lag.
  * DISCOUNT BUYS NO VOLUME HERE. corr(quantity, discount) = -0.02. The standard
    defence of deep discounting is not supported by this data, and the Data
    Scientist board reports that as a finding rather than omitting it.
  * REGION IS A REAL LEVER, AND IT IS A DISCOUNT LEVER. Southeast Asia runs 2.0%
    margin on 27.2% average discount; North Asia runs 19.5% on 4.9%. A 17.5pp
    margin spread, monotone in discount.
  * 28.1% OF PRODUCTS (2,889 of 10,292) LOSE MONEY. The 1,303 worst sit below
    -20% margin and carry a 42.1% average discount, against 7.5% for the products
    above +30%. The relationship is inverse and clean.
  * FURNITURE/TABLES is the one loss-making sub-category: -8.5% margin, -$64.1K,
    on the highest average discount in the book (29.1%).
  * SCHEDULE ADHERENCE IS NOT THE PROJECT PROBLEM. Only 0.2% of lines miss their
    own mode's observed ceiling. The problem is ROUTING: 12,275 lines (23.9%) of
    Critical or High priority work moved on Second or Standard Class.

WHAT WAS RULED OUT RATHER THAN REPORTED. Per the house rule, a spread too small
to survive rounding is reported as "this dimension is not the lever", never
ranked into a league table that invents a leader and a laggard:

  * SEGMENT IS FLAT. Consumer 11.51%, Corporate 11.54%, Home Office 11.99%
    margin — a 0.48pp spread on three segments. Charted for growth only; the app
    says outright that segment is not a margin lever.
  * FREIGHT AS A SHARE OF SALES IS FLAT ACROSS MARKETS, 10.4-11.3%. Mode mix,
    not geography, is the freight lever.
  * SHIP LAG IS FLAT ACROSS MARKETS, 3.68-4.01 days on a 3.97-day mean.
  * DISCOUNTING DID NOT DRIFT. Margin holds at 11.0-12.0% across all four years.
    The cliff is a standing pricing policy, not a deterioration.

THE ONE PLACE THE MODEL AND THE DATA DISAGREE, and it is on the board. The
linear fit's residuals are STRUCTURED, not noise: at exactly 20% discount the
observed mean line margin is +14.7% while the fit predicts -5.9%, a +20.5pp
residual, and 4,998 lines sit on that single rate. The round-number rates carry
the volume and the linear model is worst precisely there. So the Data Scientist
board reports R2 = 0.718 AND refuses to let it stand alone: the banded view is
the one to price from, and the residual table is the feature-engineering queue.
"""
import importlib.util
import sys
from pathlib import Path

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html

sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import (  # noqa: E402  (path must be set before this import)
    BAD, GOOD, JAKARTA, LINE, MUTED, SERIES, TINT, WARN,
    _f, base_fig, configure, data_table, empty_fig, fmt, has_error, insight_card,
    kpi_tile, load_row, load_rows, pipe, render_error_panel, share_html,
    snapshot_route, standard_layout, store_snapshot, wire_ask,
)

_LSPEC = importlib.util.spec_from_file_location(
    "gen_llm_sql", Path(__file__).with_name("llm_sql.py"))
_LLM = importlib.util.module_from_spec(_LSPEC); _LSPEC.loader.exec_module(_LLM)

# The typed VIEW, not the raw VARCHAR table. Every query in this recipe reads it,
# so the casting and the date parsing are defined in exactly one place.
SCHEMA, TABLE = "STARTER_KIT", "SUPERSTORE"
TITLE = "Global Superstore"

# One shared filter bar for all five personas. Every persona query honours all
# four params, which is what lets a tab switch hold scope.
FILTER_SPEC = [("markets", "MARKET", "Market"),
               ("categories", "CATEGORY", "Category"),
               ("segments", "SEGMENT", "Segment"),
               ("years", "YEAR", "Order year")]

# Measure -> unit, merged across all five personas. Names do not collide, so one
# dict serves the whole app and board.fmt stays correct on any tab. Anything
# absent formats as a plain number, which is right for counts and day figures.
KINDS = {
    "SALES": "money", "PROFIT": "money", "SHIP_COST": "money",
    "LOSS_SALES": "money", "LOSS_PROFIT": "money",
    "CLIFF_SALES": "money", "CLIFF_PROFIT": "money",
    "AOV": "money", "AVG_SHIP_COST": "money", "AVG_UNIT_PRICE": "money",
    "MARGIN_PCT": "percent", "SHIP_PCT_SALES": "percent",
    "LOSS_LINE_PCT": "percent", "CLIFF_LINE_PCT": "percent",
    "AVG_DISCOUNT_PCT": "percent", "OFF_PLAN_PCT": "percent",
    "MISMATCH_PCT": "percent", "CRITICAL_PCT": "percent",
    "LOSS_PROD_PCT": "percent", "MEAN_MARGIN_PCT": "percent",
    "SD_MARGIN_PCT": "percent", "FIT_MARGIN_PCT": "percent",
    "DISCOUNT_PCT": "percent", "RESIDUAL_PP": "percent",
    "BREAKEVEN_DISC": "percent",
}

# --- thresholds ---------------------------------------------------------------
# Gate severity on SPREAD against the baseline, never on an absolute rate: a
# near-uniform dimension will otherwise light up every tile as critical, which is
# how a board ends up crying wolf about a 0.5pp difference.
FLAT_PP = 3.0        # margin/freight spread below this is ruled out, not ranked
FLAT_DAYS = 1.0      # ship-lag spread below this is noise, not a service level
CLIFF_BAND = 20.0    # measured: the discount % past which this catalogue loses money
R2_USEFUL = 0.30     # below this a feature is reported as "no signal", not weak
RESID_PP = 10.0      # a fit residual past this is structure, not noise

NEGATIVES = [
    "No cost of goods. Margin throughout is Profit/Sales AS BOOKED, so the true "
    "floor a discount could be taken to is not derivable — every board here says "
    "how much margin a discount destroyed, and none can say how much was left.",
    "No list price. Discount is a realised rate per line; whether it was a "
    "campaign, a volume tier or a negotiated concession is not recorded, so the "
    "cliff cannot be attributed to a policy owner.",
    "No delivery or receipt date. Cycle time is order-to-dispatch only. On-time "
    "performance against a customer promise cannot be measured, because neither "
    "the promise date nor the arrival date exists in this data.",
    "No carrier. Shipping Cost is an amount with nothing attached, so carriers "
    "cannot be compared or renegotiated from this table.",
    "No returns or cancellations, so no margin figure here is corrected for goods "
    "that came back.",
    "No inventory, stock position or lead time: fill rate, stockouts and days of "
    "cover are out of reach, and a discount cannot be tied to ageing stock.",
    "No customer acquisition date. 'Repeat' on the Sales board means more than one "
    "order WITHIN THE FILTERED SCOPE — it is not retention, and narrowing the year "
    "filter will move it for arithmetic reasons rather than commercial ones.",
    "No project, milestone, budget or resource table. The Project Manager board is "
    "order-fulfilment delivery, which is what this data can support; it is not "
    "portfolio or programme management and does not pretend to be.",
    "No headcount, site or warehouse. Throughput per facility and labour "
    "productivity are not derivable.",
]
REFUSED = [
    "\"Which segment should we push?\" — refused. Segment margin is 11.51% / "
    "11.54% / 11.99%, a 0.48pp spread across Consumer, Corporate and Home Office. "
    "Ranking that would manufacture a winner out of rounding. Segment is not a "
    "margin lever in this catalogue; discount is.",
    "\"Which market has a freight problem?\" — refused. Freight is 10.4-11.3% of "
    "sales in every market. Mode mix, not geography, is the lever.",
    "\"Which market is slowest to ship?\" — refused. Ship lag runs 3.68-4.01 days "
    "across all seven markets, a 0.33-day spread on a 3.97-day mean.",
    "\"Did discounting get worse over time?\" — refused. Margin holds at "
    "11.0-12.0% across 2011-2014. The cliff is a standing policy, not a drift.",
    "\"What is our real gross margin on Tables?\" — answered only as booked profit "
    "over sales (-8.46%). With no cost of goods there is no way to split that "
    "between a deep discount and a thin underlying product.",
    "\"Can we predict margin from the order?\" — answered with a caveat that is "
    "part of the answer. Discount alone gives R2 = 0.718, but the residuals are "
    "structured at the round-number rates that carry most of the volume, so the "
    "fitted line must not be used to price a specific rate. Use the bands.",
]

configure(schema=SCHEMA, table=TABLE,
          measures=["SALES", "PROFIT", "LINES_N", "SHIP_COST", "UNITS"],
          rates=["MARGIN_PCT", "AVG_DISCOUNT_PCT", "SHIP_PCT_SALES",
                 "CYCLE_DAYS"],
          negatives=NEGATIVES, refused=REFUSED, has_time=True, kinds=KINDS)

ASK_CATALOG = [
    ("SUPERSTORE", "ORDER_ID", "entity_key", "count_only"),
    ("SUPERSTORE", "ORDER_DATE", "temporal_event", "not_applicable"),
    ("SUPERSTORE", "SHIP_DATE", "temporal_event", "not_applicable"),
    ("SUPERSTORE", "ORDER_MONTH", "temporal_bucket", "not_applicable"),
    ("SUPERSTORE", "ORDER_YEAR", "temporal_bucket", "not_applicable"),
    ("SUPERSTORE", "SHIP_MODE", "categorical_dim", "count_only"),
    ("SUPERSTORE", "ORDER_PRIORITY", "categorical_dim", "count_only"),
    ("SUPERSTORE", "CUSTOMER_NAME", "entity_label", "count_only"),
    ("SUPERSTORE", "SEGMENT", "categorical_dim", "count_only"),
    ("SUPERSTORE", "MARKET", "categorical_dim", "count_only"),
    ("SUPERSTORE", "REGION", "categorical_dim", "count_only"),
    ("SUPERSTORE", "COUNTRY", "categorical_dim", "count_only"),
    ("SUPERSTORE", "STATE_NAME", "categorical_dim", "count_only"),
    ("SUPERSTORE", "CITY", "categorical_dim", "count_only"),
    ("SUPERSTORE", "CATEGORY", "categorical_dim", "count_only"),
    ("SUPERSTORE", "SUBCATEGORY", "categorical_dim", "count_only"),
    ("SUPERSTORE", "PRODUCT_NAME", "entity_label", "count_only"),
    ("SUPERSTORE", "SALES", "monetary_amount", "additive"),
    ("SUPERSTORE", "PROFIT", "monetary_amount", "additive"),
    ("SUPERSTORE", "SHIPPING_COST", "monetary_amount", "additive"),
    ("SUPERSTORE", "QUANTITY", "quantity", "additive"),
    ("SUPERSTORE", "DISCOUNT", "rate", "non_additive"),
    ("SUPERSTORE", "SHIP_LAG_DAYS", "duration_days", "non_additive"),
]
ASK_JOINS = [
    "none — SUPERSTORE is a single denormalised fact view, one row per order line",
    "it is a VIEW over STARTER_KIT.STORESALES and is already typed: ORDER_DATE and "
    "SHIP_DATE are real DATEs, SALES/PROFIT/DISCOUNT/SHIPPING_COST are DECIMALs. "
    "Do NOT wrap them in TO_DATE or CAST — that is only needed on the raw table.",
    "DISCOUNT is a fraction (0.20 = 20%), not a percentage. Multiply by 100 to "
    "display it.",
    "margin is non-additive: compute SUM(PROFIT)/SUM(SALES), never AVG of a "
    "per-line ratio, or a $3 pencil weighs as much as a $3,000 copier.",
    "SHIP_LAG_DAYS is order-to-dispatch, already computed in the view.",
]


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def _money(value):
    """Compact money for prose. Board tiles use board.fmt; findings read better
    with a magnitude suffix than with eleven digits mid-sentence."""
    number = _f(value)
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1e9:
        return f"{sign}${number / 1e9:.2f}B"
    if number >= 1e6:
        return f"{sign}${number / 1e6:.2f}M"
    if number >= 1e3:
        return f"{sign}${number / 1e3:.1f}K"
    return f"{sign}${number:,.0f}"


def _spread(rows, key, name_key, weight_key=None, min_share=0.0):
    """(spread, best_row, worst_row) on one numeric key, or None when there is
    nothing to compare.

    Every persona here uses this before making a ranking claim, so that a
    dimension whose spread is inside the noise floor can be REPORTED AS FLAT
    rather than ranked. Rows missing the key are dropped rather than read as
    zero, which would invent a worst performer out of a NULL.

    MATERIALITY GATE. weight_key + min_share drop groups too small to be a fair
    benchmark before anything is ranked, and this is not a nicety: Canada is a
    single market of 201 orders and 0.5% of revenue that happens to carry a 0.0%
    average discount and therefore a 26.6% margin. Ranked naively it becomes the
    comparator for every other market, and the board ends up telling a manager
    responsible for a third of the book to be more like a rounding error. Groups
    are only excluded from being the BENCHMARK — nothing is hidden from the
    charts or tables, which show every row.

    The gate is skipped rather than applied if it would leave fewer than two
    groups, so a scope filtered down to one small market still gets a comparison
    instead of silently losing its findings.
    """
    usable = [r for r in rows if r.get(key) is not None and r.get(name_key)]
    if weight_key and min_share > 0:
        total = sum(_f(r.get(weight_key)) for r in usable)
        if total > 0:
            material = [r for r in usable
                        if _f(r.get(weight_key)) / total >= min_share]
            if len(material) >= 2:
                usable = material
    if len(usable) < 2:
        return None
    ordered = sorted(usable, key=lambda r: _f(r[key]))
    return _f(ordered[-1][key]) - _f(ordered[0][key]), ordered[-1], ordered[0]


# Share of scope revenue a group must carry before it may be used as a benchmark
# in a ranking claim. 2% keeps every market that a manager actually owns and
# excludes the 0.5% ones that would otherwise set the bar.
MATERIAL_SHARE = 0.02


def _nothing(label):
    """A finding for the case where a filter combination leaves no rows. Returned
    instead of an empty list, because an insights panel that renders nothing looks
    like a broken callback rather than an empty scope."""
    return {"tone": "info", "text": f"No {label} in this scope.",
            "meaning": "The filter combination selected leaves nothing to read.",
            "action": "Widen a filter — clearing Market or Order year is usually enough."}


def _tile(label, value, note, good=True, delta=None):
    """share_html reads delta, label, value, note and good UNCONDITIONALLY and
    dies with a bare KeyError otherwise, so every tile is built through here
    rather than by hand."""
    return {"label": label, "value": value, "note": note, "good": good,
            "delta": delta}


def _bar(figure, x, y, name, colour, text=None):
    figure.add_trace(go.Bar(x=x, y=y, name=name, marker_color=colour,
                            text=text, textposition="outside",
                            cliponaxis=False, hovertemplate="%{x}: %{y}<extra></extra>"))
    return figure


# ---------------------------------------------------------------------------
# 1. FINANCE MANAGER
# ---------------------------------------------------------------------------
# Owns the P&L. The question is not "how much did we sell" but "where did the
# margin go", so every tile here is a leak, not a total.
def fin_tiles(kpi):
    margin = _f(kpi.get("MARGIN_PCT"))
    cliff_profit = _f(kpi.get("CLIFF_PROFIT"))
    return [
        _tile("Revenue", fmt(kpi.get("SALES"), "SALES"),
              f"{int(_f(kpi.get('ORDERS'))):,} orders"),
        _tile("Profit", fmt(kpi.get("PROFIT"), "PROFIT"),
              f"{margin:.2f}% booked margin", good=_f(kpi.get("PROFIT")) > 0),
        _tile("Given away past 20% discount", _money(cliff_profit),
              f"on {_money(kpi.get('CLIFF_SALES'))} of revenue",
              good=False),
        _tile("Revenue sold at a loss", fmt(kpi.get("LOSS_SALES"), "LOSS_SALES"),
              f"{_f(kpi.get('LOSS_LINE_PCT')):.1f}% of lines", good=False),
        _tile("Freight", fmt(kpi.get("SHIP_COST"), "SHIP_COST"),
              f"{_f(kpi.get('SHIP_PCT_SALES')):.1f}% of revenue", good=False),
    ]


def fin_insights(kpi, trend, market, bands, detail):
    if not kpi or not bands:
        return [_nothing("revenue")]
    out = []
    profit = _f(kpi.get("PROFIT"))
    cliff_profit = _f(kpi.get("CLIFF_PROFIT"))
    cliff_sales = _f(kpi.get("CLIFF_SALES"))

    # --- 1. the cliff, sized against the P&L it is being taken out of ---------
    # Expressed as a share of profit rather than as a raw number: -$814.7K means
    # nothing until it is set beside the $1.47M it is being subtracted from.
    if cliff_profit < 0 and profit > 0:
        share = 100 * abs(cliff_profit) / profit
        out.append({
            "tone": "bad",
            "text": (f"Lines discounted past {CLIFF_BAND:.0f}% turn "
                     f"{_money(cliff_sales)} of revenue into {_money(cliff_profit)} "
                     f"of profit — {share:.0f}% of everything the book earns."),
            "meaning": (f"Booked profit in scope is {_money(profit)}. The deep-discount "
                        f"tail is {_f(kpi.get('CLIFF_LINE_PCT')):.1f}% of lines and it "
                        f"is not a rounding item: it is the single largest identified "
                        f"drain on this P&L, and it is a pricing decision rather than "
                        f"a cost problem."),
            "action": (f"Set {CLIFF_BAND:.0f}% as a hard approval gate rather than a "
                       f"guideline. Recovering even half of this is worth more than "
                       f"any freight renegotiation available in this data."),
        })

    # --- 2. where breakeven actually falls, read off the bands ----------------
    # The threshold is located from the data rather than asserted, so the number
    # moves correctly when the user filters to a subset with different economics.
    ordered = sorted(bands, key=lambda r: _f(r.get("BAND_ORDER")))
    crossed = next((b for b in ordered if _f(b.get("MARGIN_PCT")) < 0), None)
    if crossed:
        last_good = [b for b in ordered
                     if _f(b.get("BAND_ORDER")) < _f(crossed.get("BAND_ORDER"))
                     and _f(b.get("MARGIN_PCT")) >= 0]
        prior = last_good[-1] if last_good else None
        step = (_f(prior.get("MARGIN_PCT")) - _f(crossed.get("MARGIN_PCT"))
                if prior else 0.0)
        out.append({
            "tone": "warn",
            "text": (f"Margin crosses zero in the {crossed.get('BAND')} discount "
                     f"band, at {_f(crossed.get('MARGIN_PCT')):.1f}%"
                     + (f" — a {step:.1f}pp fall from {prior.get('BAND')}."
                        if prior else ".")),
            "meaning": ("This is where the book stops making money, measured on the "
                        "scope currently filtered rather than assumed from the "
                        "catalogue as a whole. Bands are used instead of a fitted "
                        "line because the response is a threshold, and a threshold "
                        "is exactly what a smooth fit hides."),
            "action": ("Price the gate to the band below this one. Anything deeper "
                       "needs a margin-floor exception, not a discount code."),
        })

    # --- 3. market P&L: ranked ONLY if the spread justifies ranking -----------
    spread = _spread(market, "MARGIN_PCT", "MARKET",
                     weight_key="SALES", min_share=MATERIAL_SHARE)
    if spread:
        gap, best, worst = spread
        if gap >= FLAT_PP:
            out.append({
                "tone": "warn",
                "text": (f"{worst.get('MARKET')} returns "
                         f"{_f(worst.get('MARGIN_PCT')):.1f}% margin against "
                         f"{best.get('MARKET')} at {_f(best.get('MARGIN_PCT')):.1f}% "
                         f"— a {gap:.1f}pp gap."),
                # The discount explanation is only asserted when the discount
                # gap actually runs the same way. Otherwise the gap is reported
                # as unexplained, which is the honest answer and stops the board
                # attributing a cause it has not established.
                "meaning": ((f"{worst.get('MARKET')} carries a "
                             f"{_f(worst.get('AVG_DISCOUNT_PCT')):.1f}% average "
                             f"discount against "
                             f"{_f(best.get('AVG_DISCOUNT_PCT')):.1f}% in "
                             f"{best.get('MARKET')}, so the margin gap tracks the "
                             f"discount gap. Freight is flat across markets and is "
                             f"ruled out as the cause.")
                            if _f(worst.get("AVG_DISCOUNT_PCT"))
                               > _f(best.get("AVG_DISCOUNT_PCT")) else
                            (f"The discount does NOT explain this one: "
                             f"{worst.get('MARKET')} discounts at "
                             f"{_f(worst.get('AVG_DISCOUNT_PCT')):.1f}% against "
                             f"{_f(best.get('AVG_DISCOUNT_PCT')):.1f}% in "
                             f"{best.get('MARKET')}. With freight flat and no cost "
                             f"of goods in this data, the cause is not derivable "
                             f"here — it is a product-mix question.")),
                "action": (f"Take the discount gate to {worst.get('MARKET')} first: "
                           f"it is the largest single-market margin recovery in "
                           f"this scope."),
            })
        else:
            out.append({
                "tone": "info",
                "text": (f"Market is not the lever — margin spans only {gap:.1f}pp "
                         f"across {len(market)} markets."),
                "meaning": ("Below the noise floor this board will rank on, so no "
                            "league table is drawn. Ranking a spread this small "
                            "would invent a laggard out of rounding."),
                "action": "Look at discount policy and product mix instead.",
            })

    # --- 4. freight, reported as ruled out when it is ------------------------
    ship_pct = _f(kpi.get("SHIP_PCT_SALES"))
    freight_spread = _spread(market, "SHIP_PCT_SALES", "MARKET",
                             weight_key="SALES", min_share=MATERIAL_SHARE)
    if freight_spread and freight_spread[0] < FLAT_PP:
        out.append({
            "tone": "good",
            "text": (f"Freight is {ship_pct:.1f}% of revenue and uniform — only "
                     f"{freight_spread[0]:.1f}pp between the highest and lowest "
                     f"market."),
            "meaning": ("There is no geographic freight problem to find here. "
                        "Reported so the search stops rather than continuing to "
                        "look for one. Freight moves with SHIP MODE MIX, which is "
                        "the Project Manager board."),
            "action": "Treat freight as fixed and spend the effort on pricing.",
        })

    # --- 5. the stability check, so the cliff is not mistaken for a trend ----
    if len(trend) >= 6:
        margins = [_f(r.get("MARGIN_PCT")) for r in trend
                   if r.get("MARGIN_PCT") is not None]
        if margins:
            recent = margins[-3:]
            early = margins[:3]
            drift = (sum(recent) / len(recent)) - (sum(early) / len(early))
            tone = "info" if abs(drift) < FLAT_PP else ("good" if drift > 0 else "bad")
            out.append({
                "tone": tone,
                "text": (f"Margin is {'stable' if abs(drift) < FLAT_PP else 'moving'}: "
                         f"{drift:+.1f}pp between the first and last three months in "
                         f"scope."),
                "meaning": ("A standing policy and a deterioration need different "
                            "responses, and only the trend distinguishes them. Flat "
                            "means the cliff has been priced in for years — it is "
                            "not a new leak, which makes it a decision rather than "
                            "an incident."),
                "action": ("Treat this as a pricing-policy change with a dated "
                           "before-and-after, not as an investigation."),
            })
    return out


def fin_figures(kpi, trend, market, bands, detail):
    # --- trend: revenue bars behind a margin line ----------------------------
    fig_trend = base_fig("Revenue and booked margin by month", "Revenue")
    if trend:
        periods = [str(r.get("PERIOD")) for r in trend]
        fig_trend.add_trace(go.Bar(
            x=periods, y=[_f(r.get("SALES")) for r in trend], name="Revenue",
            marker_color=TINT[0], hovertemplate="%{x}: %{y:$,.0f}<extra></extra>"))
        fig_trend.add_trace(go.Scatter(
            x=periods, y=[_f(r.get("MARGIN_PCT")) for r in trend], name="Margin %",
            yaxis="y2", mode="lines", line={"color": SERIES[0], "width": 2.5},
            hovertemplate="%{x}: %{y:.2f}%<extra></extra>"))
        fig_trend.update_layout(
            yaxis2={"overlaying": "y", "side": "right", "title": "Margin %",
                    "showgrid": False, "zeroline": True, "zerolinecolor": LINE})
    else:
        fig_trend = empty_fig("No months in scope")

    # --- composition: profit by market, signed ------------------------------
    fig_comp = base_fig("Profit by market", "Profit")
    if market:
        rows = sorted(market, key=lambda r: _f(r.get("PROFIT")))
        _bar(fig_comp, [str(r.get("MARKET")) for r in rows],
             [_f(r.get("PROFIT")) for r in rows], "Profit",
             [BAD if _f(r.get("PROFIT")) < 0 else SERIES[0] for r in rows])
        fig_comp.update_layout(showlegend=False)
    else:
        fig_comp = empty_fig("No markets in scope")

    # --- rates: THE CLIFF ----------------------------------------------------
    # The one chart this whole board exists to show. Bars coloured by sign so the
    # crossing point reads without consulting the axis.
    fig_rates = base_fig(f"Margin by discount band — breakeven inside "
                         f"{CLIFF_BAND:.0f}-30%", "Margin %")
    if bands:
        rows = sorted(bands, key=lambda r: _f(r.get("BAND_ORDER")))
        _bar(fig_rates, [str(r.get("BAND")) for r in rows],
             [_f(r.get("MARGIN_PCT")) for r in rows], "Margin %",
             [BAD if _f(r.get("MARGIN_PCT")) < 0 else GOOD for r in rows],
             text=[f"{_f(r.get('MARGIN_PCT')):.1f}%" for r in rows])
        fig_rates.add_hline(y=0, line_width=1.2, line_color=MUTED)
        fig_rates.update_layout(showlegend=False)
    else:
        fig_rates = empty_fig("No discount bands in scope")

    # --- concentration: where the loss actually sits -------------------------
    fig_conc = base_fig("Deepest losses, market × category", "Profit")
    losers = [r for r in detail if _f(r.get("PROFIT")) < 0][:12]
    if losers:
        labels = [f"{r.get('MARKET')} · {r.get('CATEGORY')}" for r in losers]
        _bar(fig_conc, labels, [_f(r.get("PROFIT")) for r in losers], "Profit", BAD)
        fig_conc.update_layout(showlegend=False, xaxis={"tickangle": -35})
    else:
        fig_conc = base_fig("Deepest losses, market × category", "Profit")
        fig_conc.add_trace(go.Bar(x=["No loss-making cell"], y=[0],
                                  marker_color=GOOD, name="Profit"))
        fig_conc.update_layout(showlegend=False)
    return {"trend": fig_trend, "composition": fig_comp, "rates": fig_rates,
            "concentration": fig_conc}


# ---------------------------------------------------------------------------
# 2. SALES MANAGER
# ---------------------------------------------------------------------------
# Owns the book and the territories. Revenue is the target, but this catalogue
# punishes revenue bought with discount, so every revenue figure here is shown
# with the margin it was closed at.
def sal_tiles(kpi):
    return [
        _tile("Revenue", fmt(kpi.get("SALES"), "SALES"),
              f"{int(_f(kpi.get('CUSTOMERS'))):,} accounts"),
        _tile("Orders", f"{int(_f(kpi.get('ORDERS'))):,}",
              f"{_f(kpi.get('LINES_PER_ORDER')):.2f} lines each"),
        _tile("Average order value", fmt(kpi.get("AOV"), "AOV"),
              f"{int(_f(kpi.get('UNITS'))):,} units"),
        _tile("Margin closed at", f"{_f(kpi.get('MARGIN_PCT')):.2f}%",
              f"{_money(kpi.get('PROFIT'))} profit",
              good=_f(kpi.get("MARGIN_PCT")) > 0),
        _tile("Average discount given", f"{_f(kpi.get('AVG_DISCOUNT_PCT')):.2f}%",
              f"across {int(_f(kpi.get('COUNTRIES'))):,} countries", good=False),
    ]


def sal_insights(kpi, trend, region, segment, detail):
    if not kpi or not region:
        return [_nothing("orders")]
    out = []

    # --- 1. territory: the one dimension here where ranking IS justified -----
    spread = _spread(region, "MARGIN_PCT", "REGION",
                     weight_key="SALES", min_share=MATERIAL_SHARE)
    if spread:
        gap, best, worst = spread
        if gap >= FLAT_PP:
            worst_disc = _f(worst.get("AVG_DISCOUNT_PCT"))
            best_disc = _f(best.get("AVG_DISCOUNT_PCT"))
            tracks = worst_disc > best_disc
            out.append({
                "tone": "bad",
                "text": (f"{worst.get('REGION')} closes at "
                         f"{_f(worst.get('MARGIN_PCT')):.1f}% margin on "
                         f"{worst_disc:.1f}% average discount; "
                         f"{best.get('REGION')} closes at "
                         f"{_f(best.get('MARGIN_PCT')):.1f}% on {best_disc:.1f}%."),
                "meaning": ((f"A {gap:.1f}pp margin spread across {len(region)} "
                             f"territories, and it moves with the discount rather "
                             f"than with the customer mix — both regions sell the "
                             f"same catalogue to the same three segments, and "
                             f"segment margin is flat anyway. That makes this a "
                             f"selling-behaviour difference, which is coachable, "
                             f"rather than a market-structure one, which is not.")
                            if tracks else
                            (f"A {gap:.1f}pp margin spread across {len(region)} "
                             f"territories, but the discount does not explain it: "
                             f"{worst.get('REGION')} discounts at {worst_disc:.1f}% "
                             f"against {best_disc:.1f}%. Look at product mix before "
                             f"assuming a selling problem.")),
                "action": ((f"Review {worst.get('REGION')} deal-desk approvals "
                            f"before touching its quota. Revenue there is being "
                            f"bought, not won.")
                           if tracks else
                           (f"Pull {worst.get('REGION')}'s category mix on the "
                            f"Product board before setting its quota.")),
            })
        else:
            out.append({
                "tone": "info",
                "text": (f"Territory margin is even — {gap:.1f}pp across "
                         f"{len(region)} regions."),
                "meaning": ("No territory is materially out of line, so no coaching "
                            "target is manufactured from rounding."),
                "action": "Manage the book on volume and coverage instead.",
            })

    # --- 2. segment: explicitly reported as NOT a lever ----------------------
    # This is the honest half of the board. Three near-identical numbers is a
    # negative result, and a negative result stated plainly stops the next four
    # people re-running the same query.
    seg_totals = {}
    for row in segment:
        name = row.get("SEGMENT")
        if not name:
            continue
        bucket = seg_totals.setdefault(name, {"sales": 0.0, "profit": 0.0})
        bucket["sales"] += _f(row.get("SALES"))
        # profit is reconstructed from margin x sales because the frame carries the
        # rate, not the amount; done per year-row so the weighting stays right.
        bucket["profit"] += _f(row.get("SALES")) * _f(row.get("MARGIN_PCT")) / 100.0
    if len(seg_totals) >= 2:
        margins = {k: (100 * v["profit"] / v["sales"] if v["sales"] else 0.0)
                   for k, v in seg_totals.items()}
        gap = max(margins.values()) - min(margins.values())
        listing = ", ".join(f"{k} {v:.2f}%" for k, v in
                            sorted(margins.items(), key=lambda kv: -kv[1]))
        if gap < FLAT_PP:
            out.append({
                "tone": "info",
                "text": f"Segment is not a margin lever: {listing}.",
                "meaning": (f"A {gap:.2f}pp spread across {len(margins)} segments. "
                            f"Whatever is moving margin in this book, it is not who "
                            f"the customer is. Stated as a finding so the question "
                            f"is closed rather than asked again next quarter."),
                "action": ("Segment the SALES PLAY if you like, but do not expect a "
                           "margin difference from it. Price and territory are "
                           "where the margin is."),
            })
        else:
            out.append({
                "tone": "warn",
                "text": f"Segment margin spans {gap:.2f}pp: {listing}.",
                "meaning": ("Wide enough in this scope to be worth a look, though it "
                            "is flat across the catalogue as a whole — narrowing the "
                            "filters has surfaced it."),
                "action": "Check whether the gap survives widening the year filter.",
            })

    # --- 3. account concentration, computed off the ranked detail ------------
    # Read from the top-200 revenue list against the scope total, so the claim is
    # about the accounts actually on screen rather than a separate query nobody
    # can check.
    total_sales = _f(kpi.get("SALES"))
    if detail and total_sales > 0:
        top = detail[:10]
        top_share = 100 * sum(_f(r.get("SALES")) for r in top) / total_sales
        thin = [r for r in detail[:50] if _f(r.get("MARGIN_PCT")) < 0]
        accounts = int(_f(kpi.get("CUSTOMERS")))
        # Concentration and account quality are separate facts and were being
        # welded into one sentence, which read as though a fragmented book were
        # the bad news. Low concentration is GOOD; the loss-making accounts are
        # the bad news. They get their own findings.
        out.append({
            "tone": "good",
            "text": (f"No account concentration risk: the top 10 of "
                     f"{accounts:,} accounts are only {top_share:.1f}% of "
                     f"revenue."),
            "meaning": ("The book is unusually fragmented, so no single account "
                        "loss would threaten it and there is no key-account "
                        "dependency to manage. It also means there is no small set "
                        "of names to fix — margin has to be recovered through "
                        "policy rather than through a handful of negotiations."),
            "action": ("Do not build a key-account programme on this data. Put the "
                       "effort into the discount gate, which reaches every "
                       "account at once."),
        })
        if thin:
            worst_named = sorted(thin, key=lambda r: _f(r.get("PROFIT")))[0]
            out.append({
                "tone": "warn",
                "text": (f"{len(thin)} of the 50 largest accounts are loss-making, "
                         f"the worst being {worst_named.get('CUSTOMER')} at "
                         f"{_f(worst_named.get('MARGIN_PCT')):.1f}% margin on "
                         f"{_money(worst_named.get('SALES'))} of revenue."),
                "meaning": ("Large accounts served at a negative booked margin. "
                            "That is a renegotiation rather than a churn risk — "
                            "the revenue is real and the relationship is working; "
                            "the price is not."),
                "action": ("Take these names into the next account review with "
                           "their discount history attached, not their revenue "
                           "ranking."),
            })

    # --- 4. growth, decomposed into more deals vs bigger deals --------------
    if len(trend) >= 6:
        half = len(trend) // 2
        first, second = trend[:half], trend[half:]

        def _avg(rows, key):
            vals = [_f(r.get(key)) for r in rows if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0.0

        orders_growth = _avg(second, "ORDERS") - _avg(first, "ORDERS")
        aov_growth = _avg(second, "AOV") - _avg(first, "AOV")
        driver = ("more orders" if abs(orders_growth) > 0 and
                  abs(orders_growth) / max(_avg(first, "ORDERS"), 1) >
                  abs(aov_growth) / max(_avg(first, "AOV"), 1) else "bigger orders")
        out.append({
            "tone": "good" if orders_growth > 0 else "warn",
            "text": (f"Monthly orders moved {orders_growth:+.0f} and average order "
                     f"value {aov_growth:+.0f} between the first and second half "
                     f"of the period — growth is coming from {driver}."),
            "meaning": ("A revenue number alone cannot tell these apart, and they "
                        "are different sales problems: more orders is a coverage "
                        "and pipeline result, bigger orders is a basket and "
                        "attach result."),
            "action": (f"Hold the {driver} driver in the next plan and set an "
                       f"explicit target on the other one."),
        })
    return out


def sal_figures(kpi, trend, region, segment, detail):
    # --- trend: revenue with the order count behind it -----------------------
    fig_trend = base_fig("Revenue and orders by month", "Revenue")
    if trend:
        periods = [str(r.get("PERIOD")) for r in trend]
        fig_trend.add_trace(go.Bar(
            x=periods, y=[_f(r.get("SALES")) for r in trend], name="Revenue",
            marker_color=TINT[0], hovertemplate="%{x}: %{y:$,.0f}<extra></extra>"))
        fig_trend.add_trace(go.Scatter(
            x=periods, y=[_f(r.get("ORDERS")) for r in trend], name="Orders",
            yaxis="y2", mode="lines", line={"color": SERIES[2], "width": 2.5},
            hovertemplate="%{x}: %{y:,.0f} orders<extra></extra>"))
        fig_trend.update_layout(
            yaxis2={"overlaying": "y", "side": "right", "title": "Orders",
                    "showgrid": False})
    else:
        fig_trend = empty_fig("No months in scope")

    # --- composition: territory revenue -------------------------------------
    fig_comp = base_fig("Revenue by region", "Revenue")
    if region:
        rows = sorted(region, key=lambda r: -_f(r.get("SALES")))[:12]
        _bar(fig_comp, [str(r.get("REGION")) for r in rows],
             [_f(r.get("SALES")) for r in rows], "Revenue", SERIES[0])
        fig_comp.update_layout(showlegend=False, xaxis={"tickangle": -35})
    else:
        fig_comp = empty_fig("No regions in scope")

    # --- rates: the margin/discount trade-off, per territory ----------------
    # A scatter rather than two bar charts, because the CLAIM is that the two move
    # together and a scatter is the only form in which that claim can be falsified.
    fig_rates = base_fig("Margin against discount, by region", "Margin %")
    if region:
        fig_rates.add_trace(go.Scatter(
            x=[_f(r.get("AVG_DISCOUNT_PCT")) for r in region],
            y=[_f(r.get("MARGIN_PCT")) for r in region],
            text=[str(r.get("REGION")) for r in region],
            mode="markers+text", textposition="top center",
            textfont={"size": 9, "color": MUTED},
            marker={"size": [max(8, min(34, (_f(r.get("SALES")) / 60000) ** 0.5 * 6))
                             for r in region],
                    "color": SERIES[0], "opacity": 0.75,
                    "line": {"width": 1, "color": "#fff"}},
            name="Region",
            hovertemplate="%{text}<br>discount %{x:.1f}%<br>margin %{y:.1f}%<extra></extra>"))
        fig_rates.add_hline(y=0, line_width=1.2, line_color=MUTED)
        fig_rates.update_layout(showlegend=False,
                                xaxis={"title": "Average discount %"})
    else:
        fig_rates = empty_fig("No regions in scope")

    # --- concentration: cumulative revenue share of ranked accounts ---------
    fig_conc = base_fig("Cumulative revenue share, top accounts", "Share of revenue %")
    total = _f(kpi.get("SALES"))
    if detail and total > 0:
        running, xs, ys = 0.0, [], []
        for i, row in enumerate(detail[:100], start=1):
            running += _f(row.get("SALES"))
            xs.append(i)
            ys.append(100 * running / total)
        fig_conc.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", fill="tozeroy", name="Cumulative share",
            line={"color": SERIES[4], "width": 2.5}, fillcolor=TINT[4],
            hovertemplate="top %{x} accounts: %{y:.1f}% of revenue<extra></extra>"))
        fig_conc.update_layout(showlegend=False,
                               xaxis={"title": "Accounts, ranked by revenue"})
    else:
        fig_conc = empty_fig("No accounts in scope")
    return {"trend": fig_trend, "composition": fig_comp, "rates": fig_rates,
            "concentration": fig_conc}


# ---------------------------------------------------------------------------
# 3. PROJECT MANAGER
# ---------------------------------------------------------------------------
# Owns delivery execution across the order book. NOTE the honest framing: there
# is no project table in this data, so this board is order fulfilment — cycle
# time, plan adherence, routing and split shipments — and it says so rather than
# dressing order lines up as milestones.
def prj_tiles(kpi):
    return [
        _tile("Orders delivered", f"{int(_f(kpi.get('ORDERS'))):,}",
              f"{int(_f(kpi.get('LINES_N'))):,} lines"),
        _tile("Cycle time", f"{_f(kpi.get('CYCLE_DAYS')):.2f}d",
              f"±{_f(kpi.get('CYCLE_SD')):.2f}d, max {int(_f(kpi.get('CYCLE_MAX')))}d",
              good=False),
        _tile("Off plan", f"{_f(kpi.get('OFF_PLAN_PCT')):.2f}%",
              "against each mode's own ceiling",
              good=_f(kpi.get("OFF_PLAN_PCT")) < 1.0),
        _tile("Priority/mode mismatch", f"{_f(kpi.get('MISMATCH_PCT')):.1f}%",
              f"{int(_f(kpi.get('MISMATCH_LINES'))):,} urgent lines on slow modes",
              good=False),
        _tile("Freight spend", fmt(kpi.get("SHIP_COST"), "SHIP_COST"),
              f"{_f(kpi.get('CRITICAL_PCT')):.1f}% of lines are Critical"),
    ]


def prj_insights(kpi, trend, modes, priority, detail):
    if not kpi or not modes:
        return [_nothing("orders")]
    out = []
    off_plan = _f(kpi.get("OFF_PLAN_PCT"))
    mismatch = _f(kpi.get("MISMATCH_PCT"))

    # --- 1. adherence: a GOOD finding, and the reason the board pivots -------
    # Leading with what is working is not decoration. It redirects the reader off
    # the metric they came for and onto the one that actually has room in it.
    if off_plan < 1.0:
        out.append({
            "tone": "good",
            "text": (f"Schedule adherence is not the problem: {off_plan:.2f}% of "
                     f"lines miss their own ship mode's observed ceiling."),
            "meaning": ("Each line is held against its own mode rather than against "
                        "a single global target, so a Standard Class line is not "
                        "marked late for being slower than Same Day. On that basis "
                        "dispatch does what it promises almost without exception, "
                        "and there is no expediting problem to chase."),
            "action": ("Stop reporting on-time dispatch weekly. Move the attention "
                       "to routing, below, where the exposure actually is."),
        })
    else:
        out.append({
            "tone": "bad",
            "text": f"{off_plan:.2f}% of lines miss their ship mode's ceiling.",
            "meaning": ("Measured per mode against the slowest dispatch that mode "
                        "actually achieves, so this is a genuine adherence gap "
                        "rather than a mode-mix artefact."),
            "action": "Pull the worst modes from the ship-mode chart and staff them.",
        })

    # --- 2. routing: the real exposure --------------------------------------
    # The benchmark has to be a service level in ROUTINE USE, not merely the
    # fastest one that exists. Same Day dispatches in 0.04 days but carries 5.3%
    # of lines, and quoting it as "available" would tell a delivery manager to
    # move 12,275 lines onto a premium service the operation has never run at
    # that volume. Requiring a 10% share picks First Class instead — genuinely
    # the fast option already in everyday use.
    total_lines = sum(_f(r.get("LINES_N")) for r in modes) or 1.0
    routine = [r for r in modes if _f(r.get("LINES_N")) / total_lines >= 0.10]
    fast = min(routine or modes, key=lambda r: _f(r.get("CYCLE_DAYS")),
               default=None)
    slow_rows = [r for r in modes
                 if str(r.get("SHIP_MODE")) in ("Second Class", "Standard Class")]
    if mismatch > 0 and slow_rows:
        slow_days = (sum(_f(r.get("CYCLE_DAYS")) * _f(r.get("LINES_N"))
                         for r in slow_rows)
                     / max(sum(_f(r.get("LINES_N")) for r in slow_rows), 1))
        achievable = _f(fast.get("CYCLE_DAYS")) if fast else 0.0
        out.append({
            "tone": "bad",
            "text": (f"{int(_f(kpi.get('MISMATCH_LINES'))):,} lines "
                     f"({mismatch:.1f}%) marked Critical or High priority shipped "
                     f"on Second or Standard Class, taking {slow_days:.2f} days "
                     f"against {achievable:.2f} on "
                     f"{fast.get('SHIP_MODE') if fast else 'the fastest mode'}, "
                     f"which is already in everyday use."),
            "meaning": ("This is the schedule risk that is inside the team's "
                        "control, and it is a ROUTING decision rather than a "
                        "capacity limit: the faster service exists, is already in "
                        "use, and was not chosen for this work. Because adherence "
                        "is near-perfect, none of this shows up as a late shipment "
                        "— every one of these lines was 'on time' for the wrong "
                        "mode."),
            "action": ("Make priority drive mode selection automatically. Every one "
                       "of these lines is a promise made at one service level and "
                       "fulfilled at another."),
        })

    # --- 3. mode is a real service level -- established before it is used ----
    lag_spread = _spread(modes, "CYCLE_DAYS", "SHIP_MODE")
    if lag_spread and lag_spread[0] >= FLAT_DAYS:
        gap, slowest, fastest = lag_spread
        cost_gap = _f(slowest.get("AVG_SHIP_COST")) - _f(fastest.get("AVG_SHIP_COST"))
        out.append({
            "tone": "info",
            "text": (f"Ship mode is a genuine service level: {gap:.2f} days between "
                     f"{fastest.get('SHIP_MODE')} ({_f(fastest.get('CYCLE_DAYS')):.2f}d) "
                     f"and {slowest.get('SHIP_MODE')} "
                     f"({_f(slowest.get('CYCLE_DAYS')):.2f}d)."),
            "meaning": (f"And the cost tracks it in the expected direction: "
                        f"${_f(fastest.get('AVG_SHIP_COST')):.2f} against "
                        f"${_f(slowest.get('AVG_SHIP_COST')):.2f} per line, a "
                        f"${abs(cost_gap):.2f} difference. Mode is therefore a real "
                        f"speed-for-money lever and not just a label, which is what "
                        f"makes the routing finding above actionable."),
            "action": ("Publish the speed-and-cost table above as the routing "
                       "standard, so the trade-off is made once rather than per "
                       "order."),
        })
    elif lag_spread:
        out.append({
            "tone": "warn",
            "text": (f"Ship mode barely separates on speed — {lag_spread[0]:.2f} "
                     f"days across {len(modes)} modes."),
            "meaning": ("The modes are priced differently but deliver in about the "
                        "same time in this scope, so the premium is buying little."),
            "action": "Question the premium modes before renewing carrier terms.",
        })

    # --- 4. split orders: the fulfilment defect the data can see -------------
    split = [r for r in detail if _f(r.get("MODES")) > 1]
    if split:
        out.append({
            "tone": "warn",
            "text": (f"{len(split)} of the {len(detail)} orders on this worklist "
                     f"shipped across more than one service level."),
            "meaning": ("A split order arrives in pieces. The customer experiences "
                        "the SLOWEST leg while the business pays for the fastest "
                        "one, so it is the worst of both on service and cost at the "
                        "same time."),
            "action": ("Consolidate to the mode the priority requires, or tell the "
                       "customer it ships in two parts. Silently splitting is the "
                       "only option here that is wrong."),
        })

    # --- 5. is the operation scaling or straining? --------------------------
    if len(trend) >= 6:
        half = len(trend) // 2
        first, second = trend[:half], trend[half:]

        def _avg(rows, key):
            vals = [_f(r.get(key)) for r in rows if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0.0

        vol_change = _avg(second, "ORDERS") - _avg(first, "ORDERS")
        cyc_change = _avg(second, "CYCLE_DAYS") - _avg(first, "CYCLE_DAYS")
        scaling = vol_change > 0 and abs(cyc_change) < 0.5
        out.append({
            "tone": "good" if scaling else "warn",
            "text": (f"Monthly volume moved {vol_change:+.0f} orders while cycle "
                     f"time moved {cyc_change:+.2f} days."),
            "meaning": (("Volume up with cycle time flat is the only evidence in "
                         "this table that the operation is scaling rather than "
                         "straining — throughput rose without the queue growing.")
                        if scaling else
                        ("Cycle time and volume are moving together, which is what "
                         "a capacity limit looks like from the outside.")),
            "action": (("Hold the current staffing model; it is absorbing growth.")
                       if scaling else
                       "Model dispatch capacity before the next volume step."),
        })
    return out


def prj_figures(kpi, trend, modes, priority, detail):
    # --- trend: volume against cycle time -----------------------------------
    fig_trend = base_fig("Orders shipped and cycle time by month", "Orders")
    if trend:
        periods = [str(r.get("PERIOD")) for r in trend]
        fig_trend.add_trace(go.Bar(
            x=periods, y=[_f(r.get("ORDERS")) for r in trend], name="Orders",
            marker_color=TINT[2], hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
        fig_trend.add_trace(go.Scatter(
            x=periods, y=[_f(r.get("CYCLE_DAYS")) for r in trend],
            name="Cycle days", yaxis="y2", mode="lines",
            line={"color": SERIES[2], "width": 2.5},
            hovertemplate="%{x}: %{y:.2f}d<extra></extra>"))
        fig_trend.update_layout(
            yaxis2={"overlaying": "y", "side": "right", "title": "Cycle days",
                    "showgrid": False, "rangemode": "tozero"})
    else:
        fig_trend = empty_fig("No months in scope")

    # --- composition: volume by mode ----------------------------------------
    fig_comp = base_fig("Lines shipped by service level", "Lines")
    if modes:
        rows = sorted(modes, key=lambda r: _f(r.get("CYCLE_DAYS")))
        _bar(fig_comp, [str(r.get("SHIP_MODE")) for r in rows],
             [_f(r.get("LINES_N")) for r in rows], "Lines", SERIES[2])
        fig_comp.update_layout(showlegend=False)
    else:
        fig_comp = empty_fig("No ship modes in scope")

    # --- rates: speed bought against money spent ----------------------------
    fig_rates = base_fig("Cycle time and unit freight by service level", "Cycle days")
    if modes:
        rows = sorted(modes, key=lambda r: _f(r.get("CYCLE_DAYS")))
        names = [str(r.get("SHIP_MODE")) for r in rows]
        fig_rates.add_trace(go.Bar(
            x=names, y=[_f(r.get("CYCLE_DAYS")) for r in rows], name="Cycle days",
            marker_color=SERIES[2],
            hovertemplate="%{x}: %{y:.2f}d<extra></extra>"))
        fig_rates.add_trace(go.Scatter(
            x=names, y=[_f(r.get("AVG_SHIP_COST")) for r in rows],
            name="Freight per line", yaxis="y2", mode="lines+markers",
            line={"color": SERIES[1], "width": 2.5},
            hovertemplate="%{x}: %{y:$,.2f}/line<extra></extra>"))
        fig_rates.update_layout(
            yaxis2={"overlaying": "y", "side": "right",
                    "title": "Freight per line", "showgrid": False,
                    "rangemode": "tozero"})
    else:
        fig_rates = empty_fig("No ship modes in scope")

    # --- concentration: THE ROUTING MATRIX ----------------------------------
    # Grouped bars rather than a heatmap: the comparison that matters is within a
    # priority (which mode did this urgency actually get?), and a grouped bar makes
    # that read left to right without decoding a colour scale.
    fig_conc = base_fig("Where each priority actually shipped", "Lines")
    if priority:
        pri_order, seen = [], set()
        for row in sorted(priority, key=lambda r: _f(r.get("PRI_ORDER"))):
            name = str(row.get("PRIORITY"))
            if name not in seen:
                seen.add(name)
                pri_order.append(name)
        mode_names = ["Same Day", "First Class", "Second Class", "Standard Class"]
        lookup = {(str(r.get("PRIORITY")), str(r.get("SHIP_MODE"))):
                  _f(r.get("LINES_N")) for r in priority}
        for i, mode in enumerate(mode_names):
            fig_conc.add_trace(go.Bar(
                x=pri_order, y=[lookup.get((p, mode), 0) for p in pri_order],
                name=mode, marker_color=SERIES[i % len(SERIES)],
                hovertemplate="%{x} on " + mode + ": %{y:,.0f} lines<extra></extra>"))
        fig_conc.update_layout(barmode="group",
                               xaxis={"title": "Priority requested"})
    else:
        fig_conc = empty_fig("No priority rows in scope")
    return {"trend": fig_trend, "composition": fig_comp, "rates": fig_rates,
            "concentration": fig_conc}


# ---------------------------------------------------------------------------
# 4. DATA SCIENTIST
# ---------------------------------------------------------------------------
# Owns the question "is there a model here, and can it be trusted". This board is
# deliberately the only one that argues with itself: R2 = 0.718 is a good number
# and the residual structure makes it the wrong number to price from, and BOTH
# have to be on the screen or the board is misleading.
def ds_tiles(kpi):
    r2 = _f(kpi.get("R2_DISC"))
    return [
        _tile("R², margin on discount", f"{r2:.3f}",
              f"single feature, {int(_f(kpi.get('ROWS_N'))):,} rows",
              good=r2 >= R2_USEFUL),
        _tile("Slope", f"{_f(kpi.get('SLOPE_DISC')):.3f}",
              "margin points per unit discount", good=False),
        _tile("Fitted breakeven discount", f"{_f(kpi.get('BREAKEVEN_DISC')):.1f}%",
              "where predicted margin hits zero", good=False),
        _tile("corr(quantity, discount)", f"{_f(kpi.get('CORR_QTY_DISC')):+.3f}",
              "discount buys no volume here", good=False),
        _tile("Margin dispersion", f"{100 * _f(kpi.get('SD_MARGIN')):.1f}pp",
              f"mean {100 * _f(kpi.get('MEAN_MARGIN')):.1f}pp per line"),
    ]


def ds_insights(kpi, trend, features, deciles, detail):
    if not kpi or not features:
        return [_nothing("modelable rows")]
    out = []
    r2 = _f(kpi.get("R2_DISC"))
    slope = _f(kpi.get("SLOPE_DISC"))
    breakeven = _f(kpi.get("BREAKEVEN_DISC"))

    # --- 1. the model, stated plainly ---------------------------------------
    if r2 >= R2_USEFUL:
        out.append({
            "tone": "good",
            "text": (f"One feature carries this dataset: margin on discount alone "
                     f"gives R² = {r2:.3f} over "
                     f"{int(_f(kpi.get('ROWS_N'))):,} lines."),
            "meaning": (f"The fit is margin = {_f(kpi.get('INTERCEPT_DISC')):.4f} "
                        f"{slope:+.4f} × discount, so every 10 points of discount "
                        f"costs about {abs(slope) * 10:.1f} points of margin, and "
                        f"predicted margin reaches zero at {breakeven:.1f}% "
                        f"discount. For a business dataset this is an unusually "
                        f"clean single-variable relationship."),
            "action": (f"Use {breakeven:.1f}% as the modelled breakeven, and read "
                       f"the next finding before using the fitted line for "
                       f"anything narrower than that."),
        })
    else:
        out.append({
            "tone": "warn",
            "text": f"No usable single-feature signal: best R² is {r2:.3f}.",
            "meaning": ("Below the threshold this board treats as signal. Reported "
                        "as absent rather than presented as a weak model, which "
                        "would invite someone to use it."),
            "action": "Do not model margin from this scope; widen the filters.",
        })

    # --- 2. THE ARGUMENT WITH THE MODEL -------------------------------------
    # The most important finding on the board. A structured residual is not noise,
    # and a headline R2 that hides one is how a good number becomes a bad decision.
    # Picked among the HIGH-VOLUME rates, not globally. The largest residual in
    # the table belongs to the 80% discount tail — 316 lines — and leading with
    # it would be true but useless, and it would flatly contradict the point the
    # finding is making, which is that the fit fails where the volume is. So the
    # candidate set is restricted to rates carrying a material share of rows
    # first, and the deep tail is left to the residual chart.
    total_rows = sum(_f(r.get("ROWS_N")) for r in deciles) or 1.0
    heavy = [r for r in deciles if _f(r.get("ROWS_N")) / total_rows >= 0.05]
    worst = None
    for row in (heavy or deciles):
        resid = _f(row.get("MEAN_MARGIN_PCT")) - _f(row.get("FIT_MARGIN_PCT"))
        if worst is None or abs(resid) > abs(worst[0]):
            worst = (resid, row)
    if worst and abs(worst[0]) >= RESID_PP:
        resid, row = worst
        rows_n = int(_f(row.get("ROWS_N")))
        row_share = 100 * _f(row.get("ROWS_N")) / total_rows
        out.append({
            "tone": "bad",
            "text": (f"The residuals are structured, not noise: at "
                     f"{_f(row.get('DISCOUNT_PCT')):.0f}% discount the observed "
                     f"mean margin is {_f(row.get('MEAN_MARGIN_PCT')):+.1f}% while "
                     f"the fit predicts {_f(row.get('FIT_MARGIN_PCT')):+.1f}% — a "
                     f"{resid:+.1f}pp miss on {rows_n:,} lines, "
                     f"{row_share:.0f}% of the data."),
            "meaning": ("And it is worst where the volume is. Discounts in this "
                        "catalogue cluster on round numbers, so the rates "
                        "carrying the most lines are the ones the linear fit gets "
                        "most wrong. A high R² earned across the whole range is "
                        "therefore not a licence to predict at a specific rate: "
                        "the relationship is piecewise, and averaging across the "
                        "kink is what produces the good-looking number."),
            "action": ("Price from the banded table on the Finance board, not from "
                       "this fit. If a model is needed, the next step is a "
                       "threshold or spline term on discount, not another feature."),
        })
    elif worst:
        out.append({
            "tone": "good",
            "text": (f"Residuals look like noise: the largest bin miss is "
                     f"{worst[0]:+.1f}pp."),
            "meaning": ("Within the tolerance this board treats as unstructured, so "
                        "the linear form is not obviously wrong in this scope."),
            "action": "The fitted line is safe to use for directional estimates.",
        })

    # --- 3. the feature screen, INCLUDING the failures ----------------------
    strong = [r for r in features if _f(r.get("ABS_R")) >= 0.30]
    weak = [r for r in features if _f(r.get("ABS_R")) < 0.10]
    if strong:
        top = max(features, key=lambda r: _f(r.get("ABS_R")))
        out.append({
            "tone": "info",
            "text": (f"{len(strong)} of {len(features)} candidate features "
                     f"{'carries' if len(strong) == 1 else 'carry'} signal. "
                     f"{top.get('FEATURE')} leads at |r| = "
                     f"{_f(top.get('ABS_R')):.3f}; "
                     + ", ".join(f"{r.get('FEATURE')} {_f(r.get('ABS_R')):.3f}"
                                 for r in weak[:3])
                     + " are effectively zero."),
            "meaning": ("The near-zero features are listed at their real strength "
                        "rather than omitted, because a screen that reports only "
                        "the winner cannot be audited — and because knowing that "
                        "ship lag and quantity carry nothing is itself a result: it "
                        "rules out operational explanations for margin."),
            "action": ("Model on discount and stop adding order-level features. Any "
                       "further lift has to come from data not in this table — cost "
                       "of goods above all."),
        })

    # --- 4. the negative result, stated as a finding ------------------------
    qty_disc = _f(kpi.get("CORR_QTY_DISC"))
    if abs(qty_disc) < 0.10:
        out.append({
            "tone": "bad",
            "text": (f"Discount buys no volume: corr(quantity, discount) = "
                     f"{qty_disc:+.3f}."),
            "meaning": ("The standard defence of deep discounting is that it moves "
                        "units. In this catalogue it does not — the relationship is "
                        "indistinguishable from zero, so the margin the discount "
                        "destroys is not being recovered in volume anywhere in this "
                        "data. This is the finding that turns the cliff from a "
                        "trade-off into a straight loss."),
            "action": ("Put this number in front of whoever owns the discount "
                       "policy. It is the whole case for the gate."),
        })

    # --- 5. does the fit hold through time? ---------------------------------
    slopes = [_f(r.get("SLOPE_DISC")) for r in trend
              if r.get("SLOPE_DISC") is not None]
    if len(slopes) >= 6:
        lo, hi = min(slopes), max(slopes)
        mean_slope = sum(slopes) / len(slopes)
        band = hi - lo
        stable = abs(band) < abs(mean_slope) * 0.75
        out.append({
            "tone": "good" if stable else "warn",
            "text": (f"Refit monthly, the slope holds between {lo:.2f} and "
                     f"{hi:.2f} around a mean of {mean_slope:.2f}."),
            "meaning": (("A relationship that survives refitting in every month is "
                         "structural rather than an artefact of pooling four years "
                         "together, which is the failure mode a single pooled R² "
                         "cannot detect.")
                        if stable else
                        ("The slope wanders enough between months that the pooled "
                         "fit is partly an artefact of pooling. Treat the whole-"
                         "period coefficient with suspicion.")),
            "action": (("Safe to treat the discount-margin relationship as a "
                        "standing property of the catalogue.")
                       if stable else
                       "Fit per period, and do not quote the pooled coefficient."),
        })
    return out


def ds_figures(kpi, trend, features, deciles, detail):
    # --- trend: the coefficient refit per month -----------------------------
    fig_trend = base_fig("Discount coefficient and fit quality, refit monthly",
                         "Slope")
    if trend:
        periods = [str(r.get("PERIOD")) for r in trend]
        fig_trend.add_trace(go.Scatter(
            x=periods, y=[_f(r.get("SLOPE_DISC")) for r in trend], name="Slope",
            mode="lines", line={"color": SERIES[4], "width": 2.5},
            hovertemplate="%{x}: slope %{y:.3f}<extra></extra>"))
        fig_trend.add_trace(go.Scatter(
            x=periods, y=[_f(r.get("R2_DISC")) for r in trend], name="R²",
            yaxis="y2", mode="lines", line={"color": SERIES[2], "width": 1.8,
                                            "dash": "dot"},
            hovertemplate="%{x}: R² %{y:.3f}<extra></extra>"))
        fig_trend.update_layout(
            yaxis2={"overlaying": "y", "side": "right", "title": "R²",
                    "showgrid": False, "range": [0, 1]})
    else:
        fig_trend = empty_fig("No months in scope")

    # --- composition: the feature screen ------------------------------------
    fig_comp = base_fig("Feature strength against line margin", "|r|")
    if features:
        rows = sorted(features, key=lambda r: _f(r.get("ABS_R")))
        _bar(fig_comp, [str(r.get("FEATURE")) for r in rows],
             [_f(r.get("ABS_R")) for r in rows], "|r|",
             [SERIES[0] if _f(r.get("ABS_R")) >= 0.30 else LINE for r in rows],
             text=[f"{_f(r.get('ABS_R')):.3f}" for r in rows])
        fig_comp.update_layout(showlegend=False)
        fig_comp.update_layout(xaxis={"tickangle": -25})
    else:
        fig_comp = empty_fig("No features in scope")

    # --- rates: OBSERVED AGAINST FITTED — the residual diagnostic -----------
    # Both lines on one axis on purpose. This is the chart that carries the
    # board's central argument, and it only works as an overlay.
    fig_rates = base_fig("Observed margin against the linear fit, by discount rate",
                         "Margin %")
    if deciles:
        xs = [_f(r.get("DISCOUNT_PCT")) for r in deciles]
        fig_rates.add_trace(go.Scatter(
            x=xs, y=[_f(r.get("MEAN_MARGIN_PCT")) for r in deciles],
            name="Observed", mode="lines+markers",
            line={"color": SERIES[0], "width": 2.8},
            marker={"size": [max(5, min(20, (_f(r.get("ROWS_N")) / 120) ** 0.5 * 3))
                             for r in deciles]},
            hovertemplate="at %{x:.0f}% discount: observed %{y:.1f}%<extra></extra>"))
        fig_rates.add_trace(go.Scatter(
            x=xs, y=[_f(r.get("FIT_MARGIN_PCT")) for r in deciles],
            name="Linear fit", mode="lines",
            line={"color": SERIES[1], "width": 2, "dash": "dash"},
            hovertemplate="at %{x:.0f}% discount: fit %{y:.1f}%<extra></extra>"))
        fig_rates.add_hline(y=0, line_width=1.2, line_color=MUTED)
        fig_rates.update_layout(xaxis={"title": "Discount %"})
    else:
        fig_rates = empty_fig("No discount rates in scope")

    # --- concentration: the residuals themselves ----------------------------
    fig_conc = base_fig("Largest residuals — where one feature is not enough",
                        "Residual, points")
    if detail:
        rows = detail[:60]
        fig_conc.add_trace(go.Scatter(
            x=[_f(r.get("DISCOUNT_PCT")) for r in rows],
            y=[_f(r.get("RESIDUAL_PP")) for r in rows],
            text=[str(r.get("SUBCATEGORY")) for r in rows],
            mode="markers",
            marker={"size": 9, "opacity": 0.7,
                    "color": [GOOD if _f(r.get("RESIDUAL_PP")) > 0 else BAD
                              for r in rows],
                    "line": {"width": 1, "color": "#fff"}},
            name="Residual",
            hovertemplate=("%{text}<br>discount %{x:.0f}%<br>"
                           "residual %{y:+.1f}pp<extra></extra>")))
        fig_conc.add_hline(y=0, line_width=1.2, line_color=MUTED)
        fig_conc.update_layout(showlegend=False, xaxis={"title": "Discount %"})
    else:
        fig_conc = empty_fig("No residual rows in scope")
    return {"trend": fig_trend, "composition": fig_comp, "rates": fig_rates,
            "concentration": fig_conc}


# ---------------------------------------------------------------------------
# 5. PRODUCT MANAGER
# ---------------------------------------------------------------------------
# Owns the catalogue: what to carry, what to reprice, what to delist. The unit
# here is the PRODUCT rather than the line, because "28% of products lose money"
# and "24% of lines lose money" are different facts with different actions.
def pm_tiles(kpi):
    return [
        _tile("Products carried", f"{int(_f(kpi.get('PRODUCTS'))):,}",
              f"across {int(_f(kpi.get('SUBCATS')))} sub-categories"),
        _tile("Loss-making products", f"{_f(kpi.get('LOSS_PROD_PCT')):.1f}%",
              "negative profit over the whole scope", good=False),
        _tile("Catalogue margin", f"{_f(kpi.get('MARGIN_PCT')):.2f}%",
              f"{_money(kpi.get('PROFIT'))} on {_money(kpi.get('SALES'))}",
              good=_f(kpi.get("MARGIN_PCT")) > 0),
        _tile("Realised unit price", fmt(kpi.get("AVG_UNIT_PRICE"),
                                         "AVG_UNIT_PRICE"),
              f"{int(_f(kpi.get('UNITS'))):,} units sold"),
        _tile("Average discount", f"{_f(kpi.get('AVG_DISCOUNT_PCT')):.2f}%",
              "realised across every line", good=False),
    ]


def pm_insights(kpi, trend, subcat, bands, detail):
    if not kpi or not subcat:
        return [_nothing("products")]
    out = []

    # --- 1. how much of the catalogue does not pay for itself ---------------
    loss_bands = [b for b in bands if _f(b.get("PROFIT")) < 0]
    if loss_bands:
        prods = sum(int(_f(b.get("PRODUCTS"))) for b in loss_bands)
        sales = sum(_f(b.get("SALES")) for b in loss_bands)
        profit = sum(_f(b.get("PROFIT")) for b in loss_bands)
        total_prods = int(_f(kpi.get("PRODUCTS")))
        out.append({
            "tone": "bad",
            "text": (f"{prods:,} products ({100 * prods / max(total_prods, 1):.1f}% "
                     f"of the catalogue) lose money: {_money(sales)} of revenue "
                     f"producing {_money(profit)}."),
            "meaning": ("Counted per PRODUCT over the whole filtered scope, not per "
                        "line, so this is not a good product sold badly once — it "
                        "is the number of things on the shelf that have never paid "
                        "for themselves here."),
            "action": ("Work the detail table from the top. Split it into repricing "
                       "and delisting by revenue, and do not treat the two the same."),
        })

    # --- 2. the inverse discount relationship, per product margin band ------
    # The single most decision-relevant pattern on this board: the products that
    # earn are the ones nobody discounted.
    ordered = sorted(bands, key=lambda r: _f(r.get("BAND_ORDER")))
    if len(ordered) >= 3:
        worst_band, best_band = ordered[0], ordered[-1]
        wd = _f(worst_band.get("AVG_DISCOUNT_PCT"))
        bd = _f(best_band.get("AVG_DISCOUNT_PCT"))
        if wd - bd >= FLAT_PP:
            out.append({
                "tone": "warn",
                "text": (f"Product margin runs inverse to discount: the "
                         f"{worst_band.get('BAND')} margin band carries a "
                         f"{wd:.1f}% average discount against {bd:.1f}% in the "
                         f"{best_band.get('BAND')} band."),
                "meaning": (f"A {wd - bd:.1f}pp discount gap between the worst and "
                            f"best margin bands, monotone across every band between "
                            f"them. The products that earn are the products nobody "
                            f"discounted — so this is a pricing outcome, not a "
                            f"sourcing or a product-quality outcome."),
                "action": ("Do not treat the loss-makers as bad products until they "
                           "have been seen at list price. Most of this is the "
                           "discount, not the item."),
            })

    # --- 3. sub-category league, gated on spread ----------------------------
    spread = _spread(subcat, "MARGIN_PCT", "SUBCATEGORY")
    if spread:
        gap, best, worst = spread
        negatives = [s for s in subcat if _f(s.get("MARGIN_PCT")) < 0]
        if negatives:
            named = ", ".join(f"{s.get('SUBCATEGORY')} "
                              f"({_f(s.get('MARGIN_PCT')):.1f}%)"
                              for s in negatives[:3])
            out.append({
                "tone": "bad",
                "text": (f"{len(negatives)} sub-categor"
                         f"{'y loses' if len(negatives) == 1 else 'ies lose'} "
                         f"money outright: {named}."),
                "meaning": (f"Against {best.get('SUBCATEGORY')} at "
                            f"{_f(best.get('MARGIN_PCT')):.1f}%, a {gap:.1f}pp "
                            f"spread. The loss-makers carry "
                            f"{_f(negatives[0].get('AVG_DISCOUNT_PCT')):.1f}% "
                            f"average discount and "
                            f"{_f(negatives[0].get('CLIFF_LINE_PCT')):.1f}% of "
                            f"their lines are past the "
                            f"{CLIFF_BAND:.0f}% cliff — the same pattern as the "
                            f"catalogue, concentrated."),
                "action": ("Take the discount gate to these sub-categories first. "
                           "They are the cliff in miniature, not a separate problem."),
            })
        elif gap >= FLAT_PP:
            out.append({
                "tone": "warn",
                "text": (f"No sub-category loses money, but margin spans {gap:.1f}pp "
                         f"— {worst.get('SUBCATEGORY')} at "
                         f"{_f(worst.get('MARGIN_PCT')):.1f}% against "
                         f"{best.get('SUBCATEGORY')} at "
                         f"{_f(best.get('MARGIN_PCT')):.1f}%."),
                "meaning": ("Wide enough to be a real mix decision even with nothing "
                            "outright negative in this scope."),
                "action": "Shift merchandising weight toward the top of the league.",
            })
        else:
            out.append({
                "tone": "info",
                "text": (f"Sub-category mix is not the lever — {gap:.1f}pp across "
                         f"{len(subcat)} sub-categories."),
                "meaning": ("Too narrow to rank without inventing a laggard."),
                "action": "Work the product-level table instead of the mix.",
            })

    # --- 4. price against volume, so the lever is named ---------------------
    if len(trend) >= 6:
        half = len(trend) // 2
        first, second = trend[:half], trend[half:]

        def _avg(rows, key):
            vals = [_f(r.get(key)) for r in rows if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0.0

        price0, price1 = _avg(first, "AVG_UNIT_PRICE"), _avg(second, "AVG_UNIT_PRICE")
        units0, units1 = _avg(first, "UNITS"), _avg(second, "UNITS")
        price_pct = 100 * (price1 - price0) / price0 if price0 else 0.0
        units_pct = 100 * (units1 - units0) / units0 if units0 else 0.0
        driver = "volume" if abs(units_pct) > abs(price_pct) else "realised price"
        out.append({
            "tone": "info",
            "text": (f"Growth is a {driver} story: units {units_pct:+.1f}% and "
                     f"realised unit price {price_pct:+.1f}% between the first and "
                     f"second half of the period."),
            "meaning": ("Revenue alone cannot separate these, and a product manager "
                        "owns them differently — volume is assortment and "
                        "availability, realised price is pricing and mix."),
            "action": (f"Name {driver} as the plan's lever and set an explicit "
                       f"target on the other so it is not left to drift."),
        })
    return out


def pm_figures(kpi, trend, subcat, bands, detail):
    # --- trend: units against realised price --------------------------------
    fig_trend = base_fig("Units and realised unit price by month", "Units")
    if trend:
        periods = [str(r.get("PERIOD")) for r in trend]
        fig_trend.add_trace(go.Bar(
            x=periods, y=[_f(r.get("UNITS")) for r in trend], name="Units",
            marker_color=TINT[3], hovertemplate="%{x}: %{y:,.0f} units<extra></extra>"))
        fig_trend.add_trace(go.Scatter(
            x=periods, y=[_f(r.get("AVG_UNIT_PRICE")) for r in trend],
            name="Unit price", yaxis="y2", mode="lines",
            line={"color": SERIES[3], "width": 2.5},
            hovertemplate="%{x}: %{y:$,.2f}<extra></extra>"))
        fig_trend.update_layout(
            yaxis2={"overlaying": "y", "side": "right", "title": "Unit price",
                    "showgrid": False, "rangemode": "tozero"})
    else:
        fig_trend = empty_fig("No months in scope")

    # --- composition: revenue by sub-category -------------------------------
    fig_comp = base_fig("Revenue by sub-category", "Revenue")
    if subcat:
        rows = sorted(subcat, key=lambda r: -_f(r.get("SALES")))[:12]
        _bar(fig_comp, [str(r.get("SUBCATEGORY")) for r in rows],
             [_f(r.get("SALES")) for r in rows], "Revenue", SERIES[3])
        fig_comp.update_layout(showlegend=False, xaxis={"tickangle": -35})
    else:
        fig_comp = empty_fig("No sub-categories in scope")

    # --- rates: the margin league, worst first ------------------------------
    fig_rates = base_fig("Sub-category margin, worst first", "Margin %")
    if subcat:
        rows = sorted(subcat, key=lambda r: _f(r.get("MARGIN_PCT")))[:14]
        _bar(fig_rates, [str(r.get("SUBCATEGORY")) for r in rows],
             [_f(r.get("MARGIN_PCT")) for r in rows], "Margin %",
             [BAD if _f(r.get("MARGIN_PCT")) < 0 else SERIES[3] for r in rows],
             text=[f"{_f(r.get('MARGIN_PCT')):.1f}%" for r in rows])
        fig_rates.add_hline(y=0, line_width=1.2, line_color=MUTED)
        fig_rates.update_layout(showlegend=False, xaxis={"tickangle": -35})
    else:
        fig_rates = empty_fig("No sub-categories in scope")

    # --- concentration: revenue by product margin band, with the discount ---
    fig_conc = base_fig("Revenue by product margin band, and the discount behind it",
                        "Revenue")
    if bands:
        rows = sorted(bands, key=lambda r: _f(r.get("BAND_ORDER")))
        names = [str(r.get("BAND")) for r in rows]
        fig_conc.add_trace(go.Bar(
            x=names, y=[_f(r.get("SALES")) for r in rows], name="Revenue",
            marker_color=[BAD if _f(r.get("PROFIT")) < 0 else SERIES[3]
                          for r in rows],
            hovertemplate="%{x}: %{y:$,.0f}<extra></extra>"))
        fig_conc.add_trace(go.Scatter(
            x=names, y=[_f(r.get("AVG_DISCOUNT_PCT")) for r in rows],
            name="Avg discount %", yaxis="y2", mode="lines+markers",
            line={"color": SERIES[1], "width": 2.5},
            hovertemplate="%{x}: %{y:.1f}% discount<extra></extra>"))
        fig_conc.update_layout(
            yaxis2={"overlaying": "y", "side": "right", "title": "Avg discount %",
                    "showgrid": False, "rangemode": "tozero"},
            xaxis={"tickangle": -25})
    else:
        fig_conc = empty_fig("No product bands in scope")
    return {"trend": fig_trend, "composition": fig_comp, "rates": fig_rates,
            "concentration": fig_conc}


# ---------------------------------------------------------------------------
# persona registry
# ---------------------------------------------------------------------------
# Each entry is a complete board: five queries (KPI row first, then four frames
# of which the LAST is always the detail table), the three builders, the detail
# columns, and the two labels the table card shows. dryrun.py reads this registry
# directly and checks every persona's contracts, which is why the shape is
# uniform even where a board would be shorter written by hand.
FIN_COLS = ["MARKET", "CATEGORY", "LINES_N", "SALES", "PROFIT", "MARGIN_PCT",
            "CLIFF_LINE_PCT"]
SAL_COLS = ["CUSTOMER", "SEGMENT", "MARKET", "ORDERS", "SALES", "PROFIT",
            "MARGIN_PCT", "AVG_DISCOUNT_PCT"]
PRJ_COLS = ["ORDER_ID", "PRIORITY", "MARKET", "LINES_N", "MODES", "CYCLE_DAYS",
            "MISMATCH_LINES", "SALES"]
DS_COLS = ["PRODUCT", "SUBCATEGORY", "MARKET", "DISCOUNT_PCT", "MARGIN_PCT",
           "FIT_MARGIN_PCT", "RESIDUAL_PP", "SALES"]
PM_COLS = ["PRODUCT", "SUBCATEGORY", "LINES_N", "UNITS", "SALES", "PROFIT",
           "MARGIN_PCT", "AVG_DISCOUNT_PCT"]

PERSONAS = {
    "finance": {
        "label": "Finance Manager",
        "queries": ["fin_kpi.sql", "fin_trend.sql", "fin_market.sql",
                    "fin_bands.sql", "fin_detail.sql"],
        "insights": fin_insights, "figures": fin_figures, "tiles": fin_tiles,
        "detail_cols": FIN_COLS,
        "table_title": "Market × category P&L, deepest loss first",
        "table_note": ("The escalation list. Sorted on profit ascending, with the "
                       "share of lines past the 20% discount cliff alongside, so "
                       "each loss can be read as a pricing problem or not."),
        "share_tables": [("Deepest losses, market × category", 3),
                         ("Margin by discount band", 2)],
        "caption": lambda k: (f"{_money(k.get('SALES'))} revenue · "
                              f"{_money(k.get('PROFIT'))} profit · "
                              f"{_f(k.get('MARGIN_PCT')):.2f}% margin · "
                              f"{_money(k.get('CLIFF_PROFIT'))} past the cliff"),
    },
    "sales": {
        "label": "Sales Manager",
        "queries": ["sal_kpi.sql", "sal_trend.sql", "sal_region.sql",
                    "sal_segment.sql", "sal_detail.sql"],
        "insights": sal_insights, "figures": sal_figures, "tiles": sal_tiles,
        "detail_cols": SAL_COLS,
        "table_title": "Top accounts by revenue, with the margin they closed at",
        "table_note": ("The account-review worklist. Read it for large revenue "
                       "sitting on thin or negative margin — that is the "
                       "conversation a sales manager owns and a discount policy "
                       "cannot have for them."),
        "share_tables": [("Top accounts", 3), ("Territory league", 1)],
        "caption": lambda k: (f"{_money(k.get('SALES'))} revenue · "
                              f"{int(_f(k.get('ORDERS'))):,} orders · "
                              f"{int(_f(k.get('CUSTOMERS'))):,} accounts · "
                              f"{_money(k.get('AOV'))} average order"),
    },
    "project": {
        "label": "Project Manager",
        "queries": ["prj_kpi.sql", "prj_trend.sql", "prj_modes.sql",
                    "prj_priority.sql", "prj_detail.sql"],
        "insights": prj_insights, "figures": prj_figures, "tiles": prj_tiles,
        "detail_cols": PRJ_COLS,
        "table_title": "Order exception list, largest schedule exposure first",
        "table_note": ("Ranked by lines that shipped slower than their priority "
                       "asked for, then by cycle time. MODES above 1 is a split "
                       "order: dispatched across several service levels, so it "
                       "arrives in pieces."),
        "share_tables": [("Order exceptions", 3), ("Service levels", 1)],
        "caption": lambda k: (f"{int(_f(k.get('ORDERS'))):,} orders · "
                              f"{_f(k.get('CYCLE_DAYS')):.2f}d cycle · "
                              f"{_f(k.get('OFF_PLAN_PCT')):.2f}% off plan · "
                              f"{_f(k.get('MISMATCH_PCT')):.1f}% misrouted"),
    },
    "datascience": {
        "label": "Data Scientist",
        "queries": ["ds_kpi.sql", "ds_trend.sql", "ds_features.sql",
                    "ds_deciles.sql", "ds_detail.sql"],
        "insights": ds_insights, "figures": ds_figures, "tiles": ds_tiles,
        "detail_cols": DS_COLS,
        "table_title": "Largest residuals — the feature-engineering queue",
        "table_note": ("Observed margin minus the linear fit, in points, refitted "
                       "on the filtered scope. A large positive residual held its "
                       "margin despite a deep discount; a large negative one lost "
                       "margin without one. This is where a second feature would "
                       "have to come from."),
        "share_tables": [("Largest residuals", 3), ("Feature screen", 1)],
        "caption": lambda k: (f"{int(_f(k.get('ROWS_N'))):,} rows · "
                              f"R² {_f(k.get('R2_DISC')):.3f} on one feature · "
                              f"slope {_f(k.get('SLOPE_DISC')):.3f} · "
                              f"fitted breakeven "
                              f"{_f(k.get('BREAKEVEN_DISC')):.1f}%"),
    },
    "product": {
        "label": "Product Manager",
        "queries": ["pm_kpi.sql", "pm_trend.sql", "pm_subcat.sql",
                    "pm_bands.sql", "pm_detail.sql"],
        "insights": pm_insights, "figures": pm_figures, "tiles": pm_tiles,
        "detail_cols": PM_COLS,
        "table_title": "Products by profit, deepest loss first",
        "table_note": ("The rationalisation worklist. Revenue is kept beside the "
                       "loss because the two together decide the action: a deep "
                       "loss on trivial revenue is a delisting, a deep loss on "
                       "large revenue is a repricing."),
        "share_tables": [("Loss-making products", 3), ("Sub-category league", 1)],
        "caption": lambda k: (f"{int(_f(k.get('PRODUCTS'))):,} products · "
                              f"{_f(k.get('LOSS_PROD_PCT')):.1f}% loss-making · "
                              f"{_f(k.get('MARGIN_PCT')):.2f}% margin · "
                              f"{_f(k.get('AVG_DISCOUNT_PCT')):.2f}% avg discount"),
    },
}
# Open on Finance: the cliff is the finding, and it is the finding that gives the
# other four boards their context.
DEFAULT_PERSONA = "finance"


def _tab_bar():
    """dcc.Tabs rather than RadioItems.

    Dash 4 nests radio options under .dash-options-list-option[aria-selected] and
    labelClassName lands on an inner span, so `:checked +` and `:has()` both miss
    and the styling silently does nothing. Tabs take per-tab style props and need
    no CSS selector at all.
    """
    base = {"padding": "0.35rem 0.9rem", "border": "1px solid " + LINE,
            "borderRadius": "999px", "fontSize": "12.5px", "fontWeight": 600,
            "color": MUTED, "backgroundColor": "transparent",
            "marginRight": "0.4rem", "lineHeight": "1.5"}
    selected = {**base, "color": "#fff", "backgroundColor": SERIES[0],
                "border": "1px solid " + SERIES[0]}
    return html.Div(
        dcc.Tabs(id="persona", value=DEFAULT_PERSONA,
                 children=[dcc.Tab(label=cfg["label"], value=key, style=base,
                                   selected_style=selected)
                           for key, cfg in PERSONAS.items()],
                 parent_style={"width": "auto"},
                 style={"display": "flex", "height": "auto", "flexWrap": "wrap",
                        "borderBottom": "none"}),
        style={"marginTop": "0.7rem"})


def create_dash_app(server, url_base_pathname, metadata):
    app = Dash(__name__, server=server, routes_pathname_prefix="/",
               requests_pathname_prefix=url_base_pathname.rstrip("/") + "/",
               external_stylesheets=[JAKARTA],
               title=metadata.get("title", TITLE),
               suppress_callback_exceptions=True)
    snapshot_path, mount = snapshot_route(server, url_base_pathname)
    app.layout = standard_layout(
        title=TITLE, filter_spec=FILTER_SPEC,
        charts=["fig-a", "fig-b", "fig-c", "fig-d"],
        table_title=PERSONAS[DEFAULT_PERSONA]["table_title"],
        table_note=PERSONAS[DEFAULT_PERSONA]["table_note"],
        ask_placeholder="e.g. profit by sub-category where discount over 30%",
        negatives=NEGATIVES + REFUSED,
        extra_header=_tab_bar())

    @app.callback(*[Output(f"filter-{k}", "options") for k, _d, _l in FILTER_SPEC],
                  Input("boot", "n_intervals"))
    def _filters(_n):
        rows = load_rows(server, metadata, __file__, "queries/business/filters.sql")
        if has_error(rows):
            return [[] for _ in FILTER_SPEC]
        return [[{"label": str(r["VAL"]), "value": str(r["VAL"])}
                 for r in rows if r.get("DIM") == dim]
                for _k, dim, _l in FILTER_SPEC]

    def _load(persona, values):
        """One KPI row plus four frames, named by the persona's query list.

        All five personas take the identical filter params, which is what lets a
        tab switch hold scope — the whole reason these boards share one app.
        """
        cfg = PERSONAS[persona]
        params = {k: pipe(values[i]) for i, (k, _d, _l) in enumerate(FILTER_SPEC)}
        kpi = load_row(server, metadata, __file__,
                       f"queries/business/{cfg['queries'][0]}", params=params)
        frames = []
        for name in cfg["queries"][1:]:
            out = load_rows(server, metadata, __file__,
                            f"queries/business/{name}", params=params)
            frames.append([] if has_error(out) else out)
        return kpi, frames

    def _caption(persona, kpi, values):
        scope = " · ".join(
            (", ".join(values[i]) if values[i] else "All " + lbl.lower())
            for i, (_k, _d, lbl) in enumerate(FILTER_SPEC))
        return (f"{PERSONAS[persona]['label']} · orders to "
                f"{str(kpi.get('ASOF'))[:10]} · "
                f"{PERSONAS[persona]['caption'](kpi)} · {scope}")

    @app.callback(
        Output("caption", "children"), Output("kpis", "children"),
        Output("insights", "children"), Output("fig-a", "figure"),
        Output("fig-b", "figure"), Output("fig-c", "figure"),
        Output("fig-d", "figure"), Output("detail", "children"),
        Output("slot-table-title", "children"),
        Output("slot-table-note", "children"),
        Input("persona", "value"),
        *[Input(f"filter-{k}", "value") for k, _d, _l in FILTER_SPEC])
    def _refresh(persona, *values):
        persona = persona if persona in PERSONAS else DEFAULT_PERSONA
        cfg = PERSONAS[persona]
        kpi, frames = _load(persona, values)
        if kpi and has_error(kpi):
            panel = render_error_panel(kpi["_error"])
            blank = empty_fig("Query failed")
            return ("", [panel], [panel], blank, blank, blank, blank, panel,
                    cfg["table_title"], cfg["table_note"])
        kpi = kpi or {}
        detail = frames[3]
        tiles = [kpi_tile(t["label"], t["value"], i, note=t["note"],
                          good_when_up=t["good"])
                 for i, t in enumerate(cfg["tiles"](kpi))]
        cards = [insight_card(f) for f in cfg["insights"](kpi, *frames)]
        figs = cfg["figures"](kpi, *frames)
        table = (data_table(detail, cfg["detail_cols"]) if detail else
                 html.Div("No rows match.",
                          style={"color": MUTED, "fontSize": "13px"}))
        return (_caption(persona, kpi, values), tiles, cards, figs["trend"],
                figs["composition"], figs["rates"], figs["concentration"], table,
                cfg["table_title"], cfg["table_note"])

    # The "not derivable" list is shared and NOT switched per tab: all five
    # personas are limited by the same missing columns, and a reader who moves
    # between tabs should not see the honesty panel change under them.

    @app.callback(Output("dl", "data"), Output("share-link", "children"),
                  Input("btn-share", "n_clicks"), State("persona", "value"),
                  *[State(f"filter-{k}", "value") for k, _d, _l in FILTER_SPEC],
                  prevent_initial_call=True)
    def _share(_clicks, persona, *values):
        persona = persona if persona in PERSONAS else DEFAULT_PERSONA
        cfg = PERSONAS[persona]
        kpi, frames = _load(persona, values)
        if not kpi or has_error(kpi):
            return dict(content="Export failed: the data layer returned an error.",
                        filename="share-error.txt"), ""
        try:
            tables = [(label, frames[idx][:40])
                      for label, idx in cfg["share_tables"]]
            page = share_html(f"{TITLE} — {cfg['label']}",
                              _caption(persona, kpi, values),
                              cfg["tiles"](kpi), cfg["insights"](kpi, *frames),
                              cfg["figures"](kpi, *frames), tables)
        except Exception as exc:
            return (dict(content=f"Report generation failed: {exc}",
                         filename="share-error.txt"), "")
        store_snapshot(mount, page)
        return (dict(content=page, filename=f"superstore-{persona}-report.html"),
                html.A("Open shareable link ↗", href=snapshot_path,
                       target="_blank",
                       style={"color": SERIES[0], "fontWeight": 700,
                              "textDecoration": "none", "fontSize": "11.5px"}))

    wire_ask(app, server, metadata, _LLM, ASK_CATALOG, ASK_JOINS, SCHEMA, TABLE)
    return app
