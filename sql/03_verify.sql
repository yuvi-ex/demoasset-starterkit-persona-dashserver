-- Run after loading. These are the numbers the dashboard was built and verified
-- against on 2026-09-10; if your clone prints something else, the load is wrong
-- and the boards will quietly show different findings.
--
--   ROWS 51290 | ORDERS 25035 | CUSTOMERS 1590 | PRODUCTS 10292
--   SALES 12642502 | PROFIT 1467457 | MARGIN_PCT 11.61
--   FIRST 2011-01-01 | LAST 2014-12-31
SELECT COUNT(*)                                              AS ROWS_N,
       COUNT(DISTINCT ORDER_ID)                              AS ORDERS,
       COUNT(DISTINCT CUSTOMER_ID)                           AS CUSTOMERS,
       COUNT(DISTINCT PRODUCT_ID)                            AS PRODUCTS,
       ROUND(SUM(SALES),0)                                   AS SALES,
       ROUND(SUM(PROFIT),0)                                  AS PROFIT,
       ROUND(100*SUM(PROFIT)/SUM(SALES),2)                   AS MARGIN_PCT,
       MIN(ORDER_DATE)                                       AS FIRST_ORDER,
       MAX(ORDER_DATE)                                       AS LAST_ORDER
  FROM STARTER_KIT.SUPERSTORE;
