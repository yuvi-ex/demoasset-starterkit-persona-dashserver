WITH base AS (
  SELECT s.DISCOUNT                       AS D,
         s.PROFIT/NULLIF(s.SALES,0)       AS MG,
         s.SALES                          AS SALES,
         s.PRODUCT_NAME                   AS PRODUCT,
         s.SUBCATEGORY                    AS SUBCATEGORY,
         s.MARKET                         AS MARKET
    FROM STARTER_KIT.SUPERSTORE s
   WHERE s.SALES > 0
   AND ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
),
fit AS (SELECT REGR_SLOPE(MG, D) AS SLOPE, REGR_INTERCEPT(MG, D) AS INTERCEPT FROM base)
-- Residual worklist: the lines the single-feature model gets most wrong.
--
-- RESIDUAL_PP is observed margin minus fitted margin, in points. A large POSITIVE
-- residual is a line that held its margin despite a deep discount; a large NEGATIVE
-- one lost margin without being discounted. Either way this is where a second
-- feature would have to come from, so the table is the feature-engineering queue
-- and not a list of mistakes.
--
-- The fit is refitted on the FILTERED scope (see the `fit` CTE above), so the
-- residuals shown always belong to the model of the data on screen rather than to
-- a whole-table model the user is not looking at.
SELECT b.PRODUCT                                          AS PRODUCT,
       b.SUBCATEGORY                                      AS SUBCATEGORY,
       b.MARKET                                           AS MARKET,
       ROUND(100*b.D,2)                                   AS DISCOUNT_PCT,
       ROUND(100*b.MG,2)                                  AS MARGIN_PCT,
       ROUND(100*(f.INTERCEPT + f.SLOPE*b.D),2)           AS FIT_MARGIN_PCT,
       ROUND(100*(b.MG - (f.INTERCEPT + f.SLOPE*b.D)),2)  AS RESIDUAL_PP,
       ROUND(b.SALES,0)                                   AS SALES
  FROM base b CROSS JOIN fit f
 ORDER BY ABS(b.MG - (f.INTERCEPT + f.SLOPE*b.D)) DESC
 LIMIT 200
