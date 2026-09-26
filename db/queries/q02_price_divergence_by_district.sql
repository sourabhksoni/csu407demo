-- SPATIAL. Districts ranked by how far the open market price sat from the
-- administered rate across the whole season.
SELECT
    l.district_name,
    COUNT(*)                                                  AS observation_days,
    ROUND(AVG(p.price_modal - pr.declared_rate_per_quintal),2) AS mean_gap,
    ROUND(MAX(p.price_modal - pr.declared_rate_per_quintal),2) AS max_gap
FROM prices p
JOIN location l ON l.location_id = p.location_id
JOIN procurement pr
       ON pr.commodity_id = p.commodity_id
      AND pr.location_id  = p.location_id
      AND p.price_date BETWEEN pr.season_start_date AND pr.season_end_date
WHERE pr.kms_year = :kms_year
GROUP BY l.district_name
ORDER BY mean_gap DESC;
