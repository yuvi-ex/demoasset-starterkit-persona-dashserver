-- Sub-category league on MARGIN, ascending — the mix decision.
--
-- Ordered worst-first on purpose. Revenue-ranked, this catalogue looks healthy;
-- margin-ranked, Furniture/Tables is the one sub-category that loses money outright,
-- and it does so carrying the highest average discount in the book.
SELECT s.SUBCATEGORY                                                      AS SUBCATEGORY,
       s.CATEGORY                                                         AS CATEGORY,
       COUNT(*)                                                           AS LINES_N,
       COUNT(DISTINCT s.PRODUCT_ID)                                       AS PRODUCTS,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT,
       ROUND(100*COUNT(CASE WHEN s.DISCOUNT > 0.20 THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS CLIFF_LINE_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2 ORDER BY MARGIN_PCT
