-- Monthly catalogue run-rate. Units alongside revenue and realised unit price, so
-- a revenue move separates into "sold more" versus "sold dearer" — the two levers a
-- product manager actually has.
SELECT s.ORDER_MONTH                                                      AS PERIOD,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.QUANTITY),0)                                           AS UNITS,
       ROUND(SUM(s.SALES)/NULLIF(SUM(s.QUANTITY),0),2)                    AS AVG_UNIT_PRICE,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       COUNT(DISTINCT s.PRODUCT_ID)                                       AS PRODUCTS
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1 ORDER BY 1
