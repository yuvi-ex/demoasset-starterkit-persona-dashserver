-- Market x category P&L, deepest loss first: the finance manager's escalation list.
-- Sorted on PROFIT ascending so the cells destroying margin read first, with the
-- deep-discount share alongside to show whether pricing is the cause.
SELECT s.MARKET                                                           AS MARKET,
       s.CATEGORY                                                         AS CATEGORY,
       COUNT(*)                                                           AS LINES_N,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*COUNT(CASE WHEN s.DISCOUNT > 0.20 THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS CLIFF_LINE_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2 HAVING SUM(s.SALES) > 0 ORDER BY PROFIT LIMIT 200
