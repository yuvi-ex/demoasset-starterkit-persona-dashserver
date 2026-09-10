-- THE DISCOUNT CLIFF, in the finance manager's units: profit, not rate.
--
-- Banded rather than plotted per line because the story is a THRESHOLD, not a
-- gradient. BAND_ORDER keeps the x-axis in economic order instead of alphabetical.
SELECT CASE WHEN s.DISCOUNT =  0    THEN 'None'
            WHEN s.DISCOUNT <= 0.10 THEN '1-10%'
            WHEN s.DISCOUNT <= 0.20 THEN '11-20%'
            WHEN s.DISCOUNT <= 0.30 THEN '21-30%'
            WHEN s.DISCOUNT <= 0.40 THEN '31-40%'
            ELSE '41%+' END                                               AS BAND,
       CASE WHEN s.DISCOUNT =  0    THEN 1
            WHEN s.DISCOUNT <= 0.10 THEN 2
            WHEN s.DISCOUNT <= 0.20 THEN 3
            WHEN s.DISCOUNT <= 0.30 THEN 4
            WHEN s.DISCOUNT <= 0.40 THEN 5
            ELSE 6 END                                                    AS BAND_ORDER,
       COUNT(*)                                                           AS LINES_N,
       ROUND(SUM(s.SALES),0)                                              AS SALES,
       ROUND(SUM(s.PROFIT),0)                                             AS PROFIT,
       ROUND(100*SUM(s.PROFIT)/NULLIF(SUM(s.SALES),0),2)                  AS MARGIN_PCT
  FROM STARTER_KIT.SUPERSTORE s
 WHERE ({markets!s}    = '*' OR INSTR({markets!s},    '|' || s.MARKET     || '|') > 0)
   AND ({categories!s} = '*' OR INSTR({categories!s}, '|' || s.CATEGORY   || '|') > 0)
   AND ({segments!s}   = '*' OR INSTR({segments!s},   '|' || s.SEGMENT    || '|') > 0)
   AND ({years!s}      = '*' OR INSTR({years!s},      '|' || s.ORDER_YEAR || '|') > 0)
 GROUP BY 1,2 ORDER BY BAND_ORDER
