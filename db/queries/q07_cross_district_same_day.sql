-- SPATIAL. One commodity across every reporting district on a single day.
SELECT
    l.district_name,
    l.place_name    AS mandi,
    p.price_min,
    p.price_modal,
    p.price_max,
    p.arrivals_tonnes
FROM prices p
JOIN location  l ON l.location_id  = p.location_id
JOIN commodity c ON c.commodity_id = p.commodity_id
WHERE c.commodity_name = :commodity
  AND p.price_date     = :price_date
ORDER BY p.price_modal DESC;
