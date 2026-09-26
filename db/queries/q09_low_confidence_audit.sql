-- PROVENANCE. Rows that arrived through the OCR path, so analysis can be
-- re run excluding them and the difference reported.
SELECT
    d.extraction_confidence,
    s.modality,
    s.source_name,
    COUNT(*) AS row_count
FROM prices p
JOIN source   s ON s.source_id   = p.source_id
JOIN document d ON d.document_id = p.document_id
GROUP BY d.extraction_confidence, s.modality, s.source_name
ORDER BY d.extraction_confidence, row_count DESC;
