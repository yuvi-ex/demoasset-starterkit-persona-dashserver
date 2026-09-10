-- Monthly book. Orders alongside revenue so a revenue move can be read as either
-- more deals or bigger deals, which are different sales problems.
SELECT s.ORDER_MONTH                                                      AS PERIOD,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       ROUND(SUM(s.SALES)/NULLIF(COUNT(DISTINCT s.ORDER_ID),0),0)         AS AOV,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1 ORDER BY 1
