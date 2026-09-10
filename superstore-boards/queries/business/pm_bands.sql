-- How the catalogue's REVENUE is distributed across product margin bands.
--
-- Products are bucketed by their own realised margin, then the revenue and product
-- count in each bucket are reported. This answers the question a sub-category
-- average cannot: how much of the book is being sold at a loss, and by how many
-- distinct SKUs. BAND_ORDER keeps the axis in economic order.
SELECT CASE WHEN p.MARGIN <  -0.20 THEN 'Below -20%'
            WHEN p.MARGIN <   0    THEN '-20% to 0'
            WHEN p.MARGIN <=  0.10 THEN '0 to 10%'
            WHEN p.MARGIN <=  0.20 THEN '10 to 20%'
            WHEN p.MARGIN <=  0.30 THEN '20 to 30%'
            ELSE 'Above 30%' END                                          AS BAND,
       CASE WHEN p.MARGIN <  -0.20 THEN 1
            WHEN p.MARGIN <   0    THEN 2
            WHEN p.MARGIN <=  0.10 THEN 3
            WHEN p.MARGIN <=  0.20 THEN 4
            WHEN p.MARGIN <=  0.30 THEN 5
            ELSE 6 END                                                    AS BAND_ORDER,
       COUNT(*)                                                           AS PRODUCTS,
       ROUND(SUM(p.SALES),0)                                              AS SALES,
       ROUND(SUM(p.PROFIT),0)                                             AS PROFIT,
       ROUND(100*AVG(p.AVG_DISC),2)                                       AS AVG_DISCOUNT_PCT
  FROM (SELECT s.PRODUCT_ID,
               SUM(s.SALES)                                   AS SALES,
               SUM(s.PROFIT)                                  AS PROFIT,
               SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0)           AS MARGIN,
               AVG(s.DISCOUNT)                                AS AVG_DISC
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
         GROUP BY s.PRODUCT_ID HAVING SUM(s.SALES) > 0) p
 GROUP BY 1,2 ORDER BY BAND_ORDER
