-- Stability check. A model fitted on the pooled data is only usable if the
-- relationship holds through time, so the slope and R2 are REFIT PER MONTH here.
-- A slope that wanders month to month would mean the pooled fit is an artefact.
SELECT s.ORDER_MONTH                                                      AS PERIOD,
       COUNT(*)                                                           AS ROWS_N,
       ROUND(REGR_SLOPE((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),4)                     AS SLOPE_DISC,
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),4)                        AS R2_DISC,
       ROUND(100*AVG((s.PROFIT/NULLIF(s.SALES,0))),2)                                    AS MEAN_MARGIN_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
   AND s.SALES > 0
 GROUP BY 1 HAVING COUNT(*) > 30 ORDER BY 1
