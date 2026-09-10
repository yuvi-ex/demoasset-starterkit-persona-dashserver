-- FINANCE MANAGER — the P&L as booked, and the size of the leak.
--
-- MARGIN_PCT is Profit/Sales as recorded. There is no cost-of-goods column, so
-- this is the only margin the data can support; it is not a gross margin.
--
-- LOSS_SALES is revenue booked on lines that finished negative. It is deliberately
-- separate from LOSS_PROFIT: the first is the revenue that has to be re-priced or
-- walked away from, the second is what it costs today. They are different decisions.
--
-- CLIFF_* isolates lines discounted past 20%, the band where this catalogue's
-- margin crosses zero. That threshold is measured, not assumed — see fin_bands.sql.
SELECT ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(SUM(s.SHIPPING_COST),0)                                      AS SHIP_COST,
       ROUND(100*SUM(s.SHIPPING_COST)/NULLIF(SUM(s.SALES),0),2)           AS SHIP_PCT_SALES,
       ROUND(SUM(CASE WHEN s.PROFIT < 0 THEN s.SALES  END),0)             AS LOSS_SALES,
       ROUND(SUM(CASE WHEN s.PROFIT < 0 THEN s.PROFIT END),0)             AS LOSS_PROFIT,
       ROUND(100*COUNT(CASE WHEN s.PROFIT < 0 THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS LOSS_LINE_PCT,
       ROUND(SUM(CASE WHEN s.DISCOUNT > 0.20 THEN s.SALES  END),0)        AS CLIFF_SALES,
       ROUND(SUM(CASE WHEN s.DISCOUNT > 0.20 THEN s.PROFIT END),0)        AS CLIFF_PROFIT,
       ROUND(100*COUNT(CASE WHEN s.DISCOUNT > 0.20 THEN 1 END)
               /NULLIF(COUNT(*),0),2)                                     AS CLIFF_LINE_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT,
       COUNT(*)                                                           AS LINES_N,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       MAX(s.ORDER_DATE)                                                  AS ASOF
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
