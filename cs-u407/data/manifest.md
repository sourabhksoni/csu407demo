# Data Manifest, Team 10, Chhattisgarh

Every collected document or dataset in `data/raw/` gets exactly one row here before the
pipeline uses it. The brief treats a corpus without a manifest, or one containing unlicensed
scraped content, as a red flag requiring remediation, so this file is a gate rather than
paperwork.

**Status:** template. Populated during Phase 2 collection.

## Required fields

| Field | Meaning |
|---|---|
| doc_id | Stable local identifier. Matches Document.document_id in the schema |
| file | Path under data/raw/ |
| source | Issuing organisation. Matches a row in the Phase 1 source inventory |
| url | Exact retrieval URL |
| collected_on | Date of retrieval, ISO 8601 |
| modality | One of: api-csv, html-table, digital-pdf, scanned-pdf-ocr |
| language | en, hi, or mixed |
| licence | OGL-India, Official-terms-unstated, or Third-party with terms URL |
| commodities | In scope commodities the document covers |
| notes | Retrieval method, OCR needs, known defects |

## Manifest

| doc_id | file | source | url | collected_on | modality | language | licence | commodities | notes |
|---|---|---|---|---|---|---|---|---|---|
| (none yet, Phase 2) | | | | | | | | | |
