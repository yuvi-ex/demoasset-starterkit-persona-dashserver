-- The rationalisation worklist: products by profit, deepest loss first.
--
-- Revenue is kept in view beside the loss because the two together decide the
-- action — a deep loss on trivial revenue is a delisting, a deep loss on large
-- revenue is a re-pricing, and they are not the same conversation.
SELECT s.PRODUCT_NAME                                                     AS PRODUCT,
       s.SUBCATEGORY                                                      AS SUBCATEGORY,
       COUNT(*)                                                           AS LINES_N,
       ROUND(SUM(s.QUANTITY),0)                                           AS UNITS,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2 HAVING SUM(s.SALES) > 0 ORDER BY PROFIT LIMIT 200
