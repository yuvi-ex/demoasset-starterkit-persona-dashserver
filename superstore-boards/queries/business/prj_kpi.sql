-- PROJECT MANAGER — delivery execution across the order book: throughput, cycle
-- time, plan adherence and the two things that actually break a schedule here,
-- split shipments and priority/mode mismatch.
--
-- CYCLE_DAYS is order date to ship date. It is NOT delivery: there is no receipt
-- date in this table, so nothing here measures whether the customer got it.
--
-- OFF_PLAN_PCT holds each line against its own mode's observed ceiling, so a
-- Standard Class line is not marked late for being slower than Same Day.
--
-- MISMATCH_PCT is the schedule risk that is inside the team's control: Critical or
-- High priority work moving on Second or Standard Class.
SELECT COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       COUNT(*)                                                           AS LINES_N,
       ROUND(AVG(s.SHIP_LAG_DAYS),2)                                      AS CYCLE_DAYS,
       ROUND(STDDEV_POP(s.SHIP_LAG_DAYS),2)                               AS CYCLE_SD,
       MAX(s.SHIP_LAG_DAYS)                                               AS CYCLE_MAX,
       ROUND(100*COUNT(CASE WHEN s.SHIP_LAG_DAYS > CASE s.SHIP_MODE WHEN 'Same Day' THEN 0 WHEN 'First Class' THEN 3
                       WHEN 'Second Class' THEN 5 ELSE 7 END THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS OFF_PLAN_PCT,
       ROUND(100*COUNT(CASE WHEN s.ORDER_PRIORITY IN ('Critical','High')
                             AND s.SHIP_MODE IN ('Second Class','Standard Class')
                            THEN 1 END)/NULLIF(COUNT(*),0),2)             AS MISMATCH_PCT,
       COUNT(CASE WHEN s.ORDER_PRIORITY IN ('Critical','High')
                   AND s.SHIP_MODE IN ('Second Class','Standard Class')
                  THEN 1 END)                                             AS MISMATCH_LINES,
       ROUND(100*COUNT(CASE WHEN s.ORDER_PRIORITY = 'Critical' THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS CRITICAL_PCT,
       ROUND(COUNT(*)*1.0/NULLIF(COUNT(DISTINCT s.ORDER_ID),0),2)         AS LINES_PER_ORDER,
       ROUND(SUM(s.SHIPPING_COST),0)                                      AS SHIP_COST,
       MAX(s.ORDER_DATE)                                                  AS ASOF
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
