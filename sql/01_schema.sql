-- Base table for the Global Superstore order book: one row per order LINE.
--
-- Widths are set from the real data with headroom (longest product name is 127
-- chars, longest city 35), not guessed. STATE_NAME rather than STATE because
-- STATE is a RESERVED WORD in Exasol and `AS STATE` is a syntax error.
--
-- Money and rates are DECIMAL, not DOUBLE: this is a margin dashboard and the
-- whole point is that SUM(PROFIT)/SUM(SALES) is reproducible.
CREATE SCHEMA IF NOT EXISTS STARTER_KIT;

CREATE OR REPLACE TABLE STARTER_KIT.SUPERSTORE_SRC (
    ROW_ID          DECIMAL(18,0),
    ORDER_ID        VARCHAR(32),
    ORDER_DATE      DATE,
    SHIP_DATE       DATE,
    SHIP_MODE       VARCHAR(32),
    CUSTOMER_ID     VARCHAR(32),
    CUSTOMER_NAME   VARCHAR(64),
    SEGMENT         VARCHAR(32),
    CITY            VARCHAR(64),
    STATE_NAME      VARCHAR(64),
    COUNTRY         VARCHAR(64),
    MARKET          VARCHAR(16),
    REGION          VARCHAR(32),
    PRODUCT_ID      VARCHAR(32),
    CATEGORY        VARCHAR(32),
    SUBCATEGORY     VARCHAR(32),
    PRODUCT_NAME    VARCHAR(256),
    SALES           DECIMAL(18,4),
    QUANTITY        DECIMAL(18,0),
    DISCOUNT        DECIMAL(9,4),
    PROFIT          DECIMAL(18,4),
    SHIPPING_COST   DECIMAL(18,4),
    ORDER_PRIORITY  VARCHAR(16)
);
