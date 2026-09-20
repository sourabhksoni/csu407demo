-- SPATIAL. Storage capacity available per tonne of the commodity procured.
-- Guards the denominator, since a district may appear with zero procurement.
SELECT
    l.district_name,
    ROUND(SUM(DISTINCT s.capacity_mt), 2)  AS total_capacity_mt,
    ROUND(SUM(DISTINCT pr.quantity_mt), 2) AS procured_mt,
    CASE WHEN SUM(DISTINCT pr.quantity_mt) > 0
         THEN ROUND(SUM(DISTINCT s.capacity_mt) / SUM(DISTINCT pr.quantity_mt), 4)
         ELSE NULL END                     AS capacity_per_tonne
FROM location l
LEFT JOIN storage     s  ON s.location_id  = l.location_id
LEFT JOIN procurement pr ON pr.location_id = l.location_id
                        AND pr.kms_year    = :kms_year
GROUP BY l.district_name
ORDER BY capacity_per_tonne;
