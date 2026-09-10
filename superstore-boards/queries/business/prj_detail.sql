-- Order-level exception list: the orders a delivery manager would actually chase.
-- Ranked by lines shipped on a mode slower than the priority asked for, then by
-- cycle time — biggest schedule exposure first.
--
-- MODES > 1 marks a SPLIT ORDER: one order dispatched across several service
-- levels, which arrives in pieces and is the fulfilment defect this table can see.
SELECT s.ORDER_ID                                                         AS ORDER_ID,
       MAX(s.ORDER_PRIORITY)                                              AS PRIORITY,
       MAX(s.MARKET)                                                      AS MARKET,
       COUNT(*)                                                           AS LINES_N,
       COUNT(DISTINCT s.SHIP_MODE)                                        AS MODES,
       MAX(s.SHIP_LAG_DAYS)                                               AS CYCLE_DAYS,
       COUNT(CASE WHEN s.ORDER_PRIORITY IN ('Critical','High')
                   AND s.SHIP_MODE IN ('Second Class','Standard Class')
                  THEN 1 END)                                             AS MISMATCH_LINES,
       ROUND(SUM(s.SALES),0)                                              AS SALES
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1 ORDER BY MISMATCH_LINES DESC, CYCLE_DAYS DESC, SALES DESC LIMIT 200
