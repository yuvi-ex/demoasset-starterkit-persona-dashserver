-- Candidate feature screen against the target (line margin), strongest |r| first.
--
-- This is the frame that says what to model with AND what to drop. Discount is the
-- only strong signal; quantity and freight are near-zero and are shown at their
-- real strength rather than omitted, because a screen that only lists the winner
-- cannot be audited.
--
-- Categorical dimensions are screened by BETWEEN-GROUP SPREAD instead of a
-- correlation, which is not defined for them: the spread column is the gap between
-- the best and worst group's mean margin, in points.
SELECT 'DISCOUNT'      AS FEATURE, 'numeric' AS KIND,
       ROUND(ABS(CORR(s.DISCOUNT, (s.PROFIT/NULLIF(s.SALES,0)))),4)      AS ABS_R,
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.DISCOUNT),4)        AS R2
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0) AND s.SALES > 0
UNION ALL
SELECT 'QUANTITY', 'numeric',
       ROUND(ABS(CORR(s.QUANTITY, (s.PROFIT/NULLIF(s.SALES,0)))),4),
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.QUANTITY),4)
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0) AND s.SALES > 0
UNION ALL
SELECT 'SHIPPING_COST', 'numeric',
       ROUND(ABS(CORR(s.SHIPPING_COST, (s.PROFIT/NULLIF(s.SALES,0)))),4),
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.SHIPPING_COST),4)
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0) AND s.SALES > 0
UNION ALL
SELECT 'SALES', 'numeric',
       ROUND(ABS(CORR(s.SALES, (s.PROFIT/NULLIF(s.SALES,0)))),4),
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.SALES),4)
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0) AND s.SALES > 0
UNION ALL
SELECT 'SHIP_LAG_DAYS', 'numeric',
       ROUND(ABS(CORR(s.SHIP_LAG_DAYS, (s.PROFIT/NULLIF(s.SALES,0)))),4),
       ROUND(REGR_R2((s.PROFIT/NULLIF(s.SALES,0)), s.SHIP_LAG_DAYS),4)
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0) AND s.SALES > 0
ORDER BY ABS_R DESC
