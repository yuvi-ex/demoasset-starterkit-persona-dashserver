-- SALES MANAGER — the book: revenue, who bought, how big the basket, what it cost
-- in discount to close.
--
-- AOV is per ORDER, not per line: a line is a picking instruction, an order is the
-- transaction a rep actually closed. LINES_PER_ORDER is carried so the two cannot
-- be confused.
--
-- REPEAT_CUST_PCT counts customers with more than one distinct order. Note the
-- limit honestly: this table has no acquisition date, so this is repeat-within-scope,
-- not retention.
SELECT ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       COUNT(DISTINCT s.CUSTOMER_ID)                                      AS CUSTOMERS,
       ROUND(SUM(s.SALES)/NULLIF(COUNT(DISTINCT s.ORDER_ID),0),0)         AS AOV,
       ROUND(COUNT(*)*1.0/NULLIF(COUNT(DISTINCT s.ORDER_ID),0),2)         AS LINES_PER_ORDER,
       ROUND(SUM(s.QUANTITY),0)                                           AS UNITS,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT,
       COUNT(*)                                                           AS LINES_N,
       COUNT(DISTINCT s.COUNTRY)                                          AS COUNTRIES,
       MAX(s.ORDER_DATE)                                                  AS ASOF
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
