# Data

## Directories

| Path | Version controlled | Contents |
|---|---|---|
| `manifest.csv` | Yes | Provenance row for every collected file. Gate artifact. |
| `raw/` | No | Collected documents as retrieved, never edited |
| `processed/` | No | Derived training and working data, rebuildable from raw |
| `eval/` | Yes | Held out evaluation set. Owned by the Evaluation Lead. |
| `sentinel/` | No | Sentinel-2 derived indicators, optional extension |

`raw/`, `processed/` and `sentinel/` are gitignored. The brief says large
datasets go to the designated storage location with links provided, not to
GitHub. Record the storage link here when collection starts.

Designated storage link: to be added at the start of Phase 2.

## Manifest is a gate, not paperwork

The brief treats a corpus without a manifest, or one containing unlicensed
scraped content, as a red flag requiring remediation. Every file in `raw/` gets
exactly one row in `manifest.csv` before the pipeline touches it.

| Column | Meaning |
|---|---|
| doc_id | Stable identifier, matches `document.document_id` |
| file | Path under `raw/` |
| source_id | An id from `config/sources.yaml` |
| url | Exact retrieval URL |
| collected_on | Retrieval date, ISO 8601 |
| modality | api_csv, html_table, digital_pdf, scanned_pdf_ocr |
| language | en, hi, mixed |
| licence | ogl_india, official_unstated, third_party |
| commodities | In scope commodities the document covers |
| pages | Page count, so page level provenance can be checked |
| sha256 | Content hash, so a re download can be proven identical |
| notes | Retrieval method, OCR needs, known defects |

## Why eval is version controlled and processed is not

`processed/` is derived and rebuildable. `eval/` is hand labelled, small, and
must be reviewable by someone checking that it was not contaminated. Losing it
would mean rebuilding the ground truth by hand.
