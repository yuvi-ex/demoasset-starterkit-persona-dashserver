-- Market P&L. Margin is the column that actually separates these rows; freight as
-- a share of sales is carried alongside precisely so it can be RULED OUT — it sits
-- in a ~1pp band across every market, so it is never the explanation.
SELECT s.MARKET                                                           AS MARKET,
       COUNT(*)                                                           AS LINES_N,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*SUM(s.SHIPPING_COST)/NULLIF(SUM(s.SALES),0),2)           AS SHIP_PCT_SALES,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1 ORDER BY SALES DESC
