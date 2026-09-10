-- PRODUCT MANAGER — the catalogue: how wide it is, how much of it earns, and how
-- much of it is carried at a loss.
--
-- LOSS_PROD_PCT counts PRODUCTS whose lifetime profit in scope is negative, which
-- is the rationalisation question. It is deliberately not the loss-making LINE
-- share: a good product sold badly once is not a bad product.
--
-- TAIL_PROD_PCT is the share of products contributing the bottom 1% of revenue —
-- the long tail that costs catalogue and merchandising effort to carry.
SELECT COUNT(DISTINCT s.PRODUCT_ID)                                       AS PRODUCTS,
       COUNT(DISTINCT s.SUBCATEGORY)                                      AS SUBCATS,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(SUM(s.QUANTITY),0)                                           AS UNITS,
       ROUND(SUM(s.SALES)/NULLIF(SUM(s.QUANTITY),0),2)                    AS AVG_UNIT_PRICE,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT,
       COUNT(*)                                                           AS LINES_N,
       (SELECT ROUND(100*COUNT(CASE WHEN P < 0 THEN 1 END)
                     /NULLIF(COUNT(*),0),2)
          FROM (SELECT SUM(s2.PROFIT) AS P
                  FROM STARTER_KIT.SUPERSTORE s2
                 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s2.MARKET     || '|') > 0)
                   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s2.CATEGORY   || '|') > 0)
                   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s2.SEGMENT    || '|') > 0)
                   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s2.ORDER_YEAR || '|') > 0)
                 GROUP BY s2.PRODUCT_ID))                                 AS LOSS_PROD_PCT,
       MAX(s.ORDER_DATE)                                                  AS ASOF
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
