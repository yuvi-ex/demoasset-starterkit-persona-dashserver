-- The routing matrix: what priority was asked for against what service it actually
-- moved on. This is the frame the mismatch claim is made from — read the Critical
-- and High rows sitting on Second or Standard Class.
SELECT s.ORDER_PRIORITY                                                   AS PRIORITY,
       s.SHIP_MODE                                                        AS SHIP_MODE,
       CASE s.ORDER_PRIORITY WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
                             WHEN 'Medium' THEN 3 ELSE 4 END              AS PRI_ORDER,
       COUNT(*)                                                           AS LINES_N,
       ROUND(AVG(s.SHIP_LAG_DAYS),2)                                      AS CYCLE_DAYS,
       ROUND(SUM(s.SHIPPING_COST),0)                                      AS SHIP_COST
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2,3 ORDER BY PRI_ORDER, CYCLE_DAYS
