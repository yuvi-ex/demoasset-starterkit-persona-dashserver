-- DATA SCIENTIST — is there a model here, and how much of the variance does it get?
--
-- The honest headline is that ONE feature carries this dataset. Fitting line margin
-- against discount alone gives R2 = 0.718 with slope ~= -1.86: every 10 points of
-- discount costs ~18.6 points of margin, linearly, with no saturation.
--
-- BREAKEVEN_DISC is the fitted root, -intercept/slope, i.e. the discount at which
-- predicted margin hits zero. It is a MODEL output, and it is reported next to the
-- observed band table so the two can be checked against each other rather than
-- either being trusted alone.
--
-- CORR_QTY_DISC is carried to be reported as a NEGATIVE result: discount and
-- quantity are uncorrelated here, so the usual "discount buys volume" defence is
-- not supported by this data.
SELECT COUNT(*)                                                           AS ROWS_N,
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),4)                        AS R2_DISC,
       ROUND(REGR_SLOPE((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),4)                     AS SLOPE_DISC,
       ROUND(REGR_INTERCEPT((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),4)                 AS INTERCEPT_DISC,
       ROUND(-100*REGR_INTERCEPT((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT)
              /NULLIF(REGR_SLOPE((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),0),2)         AS BREAKEVEN_DISC,
       ROUND(CORR(s.DISCOUNT, (s.PROFIT/NULLIF(s.SALES,0))),4)                           AS CORR_DISC_MARGIN,
       ROUND(CORR(s.QUANTITY, s.DISCOUNT),4)                              AS CORR_QTY_DISC,
       ROUND(CORR(s.SHIPPING_COST, s.SALES),4)                            AS CORR_SHIP_SALES,
       ROUND(STDDEV_POP((s.PROFIT/NULLIF(s.SALES,0))),4)                                 AS SD_MARGIN,
       ROUND(AVG((s.PROFIT/NULLIF(s.SALES,0))),4)                                        AS MEAN_MARGIN,
       COUNT(DISTINCT s.PRODUCT_ID)                                       AS PRODUCTS,
       COUNT(DISTINCT s.CUSTOMER_ID)                                      AS CUSTOMERS,
       MAX(s.ORDER_DATE)                                                  AS ASOF
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
   AND s.SALES > 0
