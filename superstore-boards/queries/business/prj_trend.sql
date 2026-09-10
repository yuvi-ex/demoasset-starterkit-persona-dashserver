-- Monthly delivery run-rate: volume against cycle time. Read together, because
-- cycle time holding flat while volume climbs is the only evidence in this table
-- that the operation is scaling rather than straining.
SELECT s.ORDER_MONTH                                                      AS PERIOD,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       COUNT(*)                                                           AS LINES_N,
       ROUND(AVG(s.SHIP_LAG_DAYS),2)                                      AS CYCLE_DAYS,
       ROUND(100*COUNT(CASE WHEN s.ORDER_PRIORITY IN ('Critical','High')
                             AND s.SHIP_MODE IN ('Second Class','Standard Class')
                            THEN 1 END)/NULLIF(COUNT(*),0),2)             AS MISMATCH_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1 ORDER BY 1
