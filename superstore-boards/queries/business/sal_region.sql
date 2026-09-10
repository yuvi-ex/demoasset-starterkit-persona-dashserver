-- Territory league. Revenue ranks the rows; margin and discount sit beside it so a
-- big territory bought with discount is visible rather than celebrated.
SELECT s.REGION                                                           AS REGION,
       s.MARKET                                                           AS MARKET,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       COUNT(DISTINCT s.CUSTOMER_ID)                                      AS CUSTOMERS,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2 ORDER BY SALES DESC
