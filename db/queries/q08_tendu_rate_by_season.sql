-- TEMPORAL. Tendu leaf declared collection rate by season, the second
-- administered price regime alongside paddy.
SELECT
    pr.kms_year                        AS collection_season,
    l.district_name,
    pr.declared_rate_per_quintal       AS declared_rate,
    c.reporting_unit,
    pr.quantity_mt
FROM procurement pr
JOIN commodity c ON c.commodity_id = pr.commodity_id
JOIN location  l ON l.location_id  = pr.location_id
WHERE c.commodity_group = 'minor_forest_produce'
ORDER BY pr.kms_year, l.district_name;
