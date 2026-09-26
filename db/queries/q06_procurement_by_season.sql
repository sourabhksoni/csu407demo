-- TEMPORAL. Procurement volume, declared rate and centre count by season.
SELECT
    pr.kms_year,
    c.commodity_name,
    ROUND(SUM(pr.quantity_mt), 2)          AS total_procured_mt,
    MAX(pr.declared_rate_per_quintal)      AS declared_rate,
    SUM(pr.centre_count)                   AS centres,
    COUNT(DISTINCT pr.location_id)         AS districts_reporting
FROM procurement pr
JOIN commodity c ON c.commodity_id = pr.commodity_id
GROUP BY pr.kms_year, c.commodity_name
ORDER BY pr.kms_year, c.commodity_name;
