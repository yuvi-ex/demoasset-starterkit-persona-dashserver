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
-- THE RESPONSE CURVE, and the reason it is grouped on the discount VALUE rather
-- than on deciles: 56.6% of all lines carry a zero discount and there are only 27
-- distinct rates in the whole catalogue, so NTILE(10) would put five identical
-- all-zero buckets on the x-axis and hide the entire curve.
--
-- Grouping on the observed rate gives one point per rate that actually occurs.
-- MEAN_MARGIN_PCT is observed; FIT_MARGIN_PCT is the pooled linear prediction at
-- the same rate. Drawn together the two lines ARE the residual diagnostic: where
-- they diverge, one feature is not enough.
--
-- HAVING COUNT(*) >= 30 drops the long tail of odd rates with too few lines to
-- carry a stable mean, rather than plotting noise as if it were signal.
SELECT ROUND(100*b.D,2)                                   AS DISCOUNT_PCT,
       COUNT(*)                                           AS ROWS_N,
       ROUND(100*AVG(b.MG),2)                             AS MEAN_MARGIN_PCT,
       ROUND(100*STDDEV_POP(b.MG),2)                      AS SD_MARGIN_PCT,
       ROUND(100*(MAX(f.INTERCEPT) + MAX(f.SLOPE)*b.D),2)  AS FIT_MARGIN_PCT,
       ROUND(SUM(b.SALES),0)                              AS SALES
  FROM base b CROSS JOIN fit f
 GROUP BY b.D
HAVING COUNT(*) >= 30
 ORDER BY b.D
