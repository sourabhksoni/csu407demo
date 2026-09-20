-- TEMPORAL. Mean modal price in the seven days after an advisory was issued,
-- compared against the seven days before it.
SELECT
    a.advisory_id,
    l.district_name,
    a.issue_date,
    a.advisory_type,
    ROUND(AVG(CASE WHEN p.price_date <  a.issue_date THEN p.price_modal END), 2) AS price_before,
    ROUND(AVG(CASE WHEN p.price_date >= a.issue_date THEN p.price_modal END), 2) AS price_after
FROM advisories a
JOIN location l ON l.location_id = a.location_id
JOIN prices   p ON p.location_id = a.location_id
               AND p.price_date BETWEEN date(a.issue_date,'-7 day')
                                    AND date(a.issue_date,'+7 day')
WHERE a.advisory_type = :advisory_type
GROUP BY a.advisory_id, l.district_name, a.issue_date, a.advisory_type
ORDER BY a.issue_date;
