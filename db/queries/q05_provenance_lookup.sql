-- PROVENANCE. Which source, document and page did this number come from?
-- This is the query the Phase 3 gate asks for by name.
SELECT
    p.price_id,
    l.district_name,
    c.commodity_name,
    p.price_date,
    p.price_modal,
    s.source_name,
    d.document_name,
    d.document_url,
    d.page_number,
    d.language,
    d.collected_on,
    d.extraction_confidence
FROM prices p
JOIN location  l ON l.location_id  = p.location_id
JOIN commodity c ON c.commodity_id = p.commodity_id
JOIN source    s ON s.source_id    = p.source_id
LEFT JOIN document d ON d.document_id = p.document_id
WHERE p.price_id = :price_id;
