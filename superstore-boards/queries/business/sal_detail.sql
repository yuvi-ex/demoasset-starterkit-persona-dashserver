-- Top accounts by revenue, with the margin they were bought at. This is the
-- account-review worklist: read it for high revenue sitting on thin or negative
-- margin, which is the conversation a sales manager owns and a discount policy
-- cannot have for them.
SELECT s.CUSTOMER_NAME                                                    AS CUSTOMER,
       s.SEGMENT                                                          AS SEGMENT,
       s.MARKET                                                           AS MARKET,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2,3 HAVING SUM(s.SALES) > 0 ORDER BY SALES DESC LIMIT 200
