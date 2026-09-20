-- TEMPORAL. Weekly market modal price against the administered procurement rate.
-- Expected shape: one row per district per week, with both prices and the gap.
SELECT
    l.district_name,
    strftime('%Y-%W', p.price_date)          AS week,
    ROUND(AVG(p.price_modal), 2)             AS avg_modal_price,
    pr.declared_rate_per_quintal             AS declared_rate,
    ROUND(AVG(p.price_modal) - pr.declared_rate_per_quintal, 2) AS gap_per_quintal
FROM prices p
JOIN location  l  ON l.location_id  = p.location_id
JOIN commodity c  ON c.commodity_id = p.commodity_id
JOIN procurement pr
       ON pr.commodity_id = p.commodity_id
      AND pr.location_id  = p.location_id
      AND p.price_date BETWEEN pr.season_start_date AND pr.season_end_date
WHERE c.commodity_name = :commodity
GROUP BY l.district_name, week, pr.declared_rate_per_quintal
ORDER BY l.district_name, week;
