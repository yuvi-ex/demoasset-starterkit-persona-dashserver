-- Segment x year, so growth can be read per segment rather than pooled.
--
-- Segment margin in this catalogue is FLAT (a fraction of a point apart). The frame
-- is charted for growth, and the app is written to say "segment is not the lever"
-- rather than rank three near-identical numbers into a false league.
SELECT s.SEGMENT                                                          AS SEGMENT,
       s.ORDER_YEAR                                                       AS PERIOD,
       COUNT(DISTINCT s.ORDER_ID)                                         AS ORDERS,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT,
       ROUND(100*AVG(s.DISCOUNT),2)                                       AS AVG_DISCOUNT_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2 ORDER BY 1,2
