-- Ship mode as a real service level. Unlike a bare label, lag here separates
-- cleanly by mode (0.0 -> 2.2 -> 3.2 -> 5.0 days) and unit freight tracks it, so
-- mode choice is a genuine schedule-and-cost lever rather than a description.
SELECT s.SHIP_MODE                                                        AS SHIP_MODE,
       COUNT(*)                                                           AS LINES_N,
       ROUND(AVG(s.SHIP_LAG_DAYS),2)                                      AS CYCLE_DAYS,
       MAX(s.SHIP_LAG_DAYS)                                               AS CYCLE_MAX,
       ROUND(AVG(s.SHIPPING_COST),2)                                      AS AVG_SHIP_COST,
       ROUND(SUM(s.SHIPPING_COST),0)                                      AS SHIP_COST,
       ROUND(100*COUNT(CASE WHEN s.SHIP_LAG_DAYS > CASE s.SHIP_MODE WHEN 'Same Day' THEN 0 WHEN 'First Class' THEN 3
                       WHEN 'Second Class' THEN 5 ELSE 7 END THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS OFF_PLAN_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1 ORDER BY CYCLE_DAYS
