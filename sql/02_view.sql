-- THE VIEW EVERY QUERY IN THIS DASHBOARD READS. Nothing in app.py or the 26 SQL
-- files touches SUPERSTORE_SRC directly, so this is the single seam between the
-- board and however the data happened to arrive.
--
-- It exists to define the three DERIVED columns exactly once. They were being
-- recomputed inline in every query, which is 26 chances to write a different
-- date format:
--
--   ORDER_MONTH / ORDER_YEAR  the trend and filter buckets
--   SHIP_LAG_DAYS             order-to-DISPATCH, which is NOT delivery -- there
--                             is no receipt date anywhere in this dataset, so no
--                             board here can measure on-time delivery
--
-- DISCOUNT stays a FRACTION (0.20 = 20%). Every query multiplies by 100 at the
-- point of display rather than storing a percentage, so the regression on the
-- Data Scientist board reads a real 0-1 rate.
CREATE OR REPLACE VIEW STARTER_KIT.SUPERSTORE AS
SELECT ROW_ID, ORDER_ID, ORDER_DATE, SHIP_DATE, SHIP_MODE,
       CUSTOMER_ID, CUSTOMER_NAME, SEGMENT, CITY, STATE_NAME, COUNTRY,
       MARKET, REGION, PRODUCT_ID, CATEGORY, SUBCATEGORY, PRODUCT_NAME,
       SALES, QUANTITY, DISCOUNT, PROFIT, SHIPPING_COST, ORDER_PRIORITY,
       TO_CHAR(ORDER_DATE, 'YYYY')            AS ORDER_YEAR,
       TO_CHAR(ORDER_DATE, 'YYYY-MM')         AS ORDER_MONTH,
       DAYS_BETWEEN(SHIP_DATE, ORDER_DATE)    AS SHIP_LAG_DAYS
  FROM STARTER_KIT.SUPERSTORE_SRC
 WHERE ORDER_DATE IS NOT NULL;
