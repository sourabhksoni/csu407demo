-- PROVENANCE. Validation failure rate by source and reason. The brief treats
-- silently discarded rows as a red flag, so failures are counted, not hidden.
SELECT
    q.target_table,
    q.failure_reason,
    s.source_name,
    COUNT(*) AS failed_rows
FROM quarantine q
LEFT JOIN document d ON d.document_id = q.document_id
LEFT JOIN source   s ON s.source_id   = d.source_id
GROUP BY q.target_table, q.failure_reason, s.source_name
ORDER BY failed_rows DESC;
