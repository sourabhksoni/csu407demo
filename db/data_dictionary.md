# Data dictionary

Field level documentation for `db/schema.sql`. Required submission artifact.

## Conventions

- Every fact table carries `source_id` and, for document sourced rows, `document_id`.
- Monetary values are rupees per quintal unless the column name says otherwise.
- Masses are metric tonnes in `quantity_mt` and `capacity_mt`.
- Dates are ISO 8601.
- `NULL` means the source did not state the value. It never means zero.

## source

| Field | Type | Notes |
|---|---|---|
| source_id | INTEGER PK | |
| source_key | TEXT | Matches an `id` in `config/sources.yaml` |
| source_name | TEXT | As written in the Phase 1 workbook, Sheet 2 |
| organisation | TEXT | Publishing body |
| base_url | TEXT | Portal root |
| modality | TEXT | api_csv, html_table, digital_pdf, scanned_pdf_ocr |
| licence | TEXT | ogl_india, official_unstated, third_party |
| update_frequency | TEXT | Free text, for example "daily", "twice weekly" |

## document

| Field | Type | Notes |
|---|---|---|
| document_id | INTEGER PK | |
| source_id | INTEGER FK | |
| document_name | TEXT | Filename or title as published |
| document_url | TEXT | Exact retrieval URL |
| page_number | INTEGER | Required to answer the Phase 3 provenance query |
| language | TEXT | en, hi, mixed |
| collected_on | DATE | Our retrieval date |
| extraction_confidence | TEXT | high, medium, low. Always low for the OCR path. |

## location

| Field | Type | Notes |
|---|---|---|
| location_id | INTEGER PK | |
| state | TEXT | Always Chhattisgarh |
| district_code | TEXT | Project internal code, see `src/normalisation/districts.csv` |
| district_name | TEXT | Canonical English name |
| district_name_hi | TEXT | Devanagari name |
| block | TEXT | Nullable, present for some advisories and centres |
| place_name | TEXT | Mandi, purchase centre, godown or society name |
| place_type | TEXT | mandi, sub_mandi, purchase_centre, godown, society |
| predecessor_district_code | TEXT | Set for districts created in 2022. Pending gazette verification. |

## commodity and commodity_alias

| Field | Type | Notes |
|---|---|---|
| commodity_id | INTEGER PK | |
| commodity_name | TEXT | Canonical English name |
| commodity_name_hi | TEXT | Devanagari name |
| commodity_group | TEXT | cereal, pulse, oilseed, vegetable, minor_forest_produce |
| reporting_unit | TEXT | Unit the source reports in |
| unit_to_quintal_factor | REAL | NULL where no mass conversion exists, for example standard_bag |
| alias | TEXT | One observed spelling or trade name per row in commodity_alias |

## procurement

| Field | Type | Notes |
|---|---|---|
| procurement_id | INTEGER PK | |
| location_id, commodity_id | INTEGER FK | |
| kms_year | TEXT | Kharif Marketing Season, for example 2025-26 |
| season_start_date, season_end_date | DATE | Mapped from the policy order, enables the join to daily prices |
| quantity_mt | REAL | Aggregate quantity procured |
| declared_rate_per_quintal | REAL | Administered rate |
| centre_count | INTEGER | Purchase centres where published |
| farmer_count | INTEGER | Aggregate only. No identities exist anywhere in this schema. |

## prices

| Field | Type | Notes |
|---|---|---|
| price_id | INTEGER PK | |
| location_id, commodity_id | INTEGER FK | |
| price_date | DATE | Join key |
| arrivals_tonnes | REAL | |
| price_min, price_modal, price_max | REAL | Per quintal. CHECK constraints enforce min <= modal <= max. |

## storage

| Field | Type | Notes |
|---|---|---|
| storage_id | INTEGER PK | |
| location_id | INTEGER FK | |
| facility_name | TEXT | |
| agency_type | TEXT | state_warehousing, central_warehousing, fci, private_registered |
| capacity_mt | REAL | |
| snapshot_date | DATE | Our collection date. These portals overwrite rather than archive, so no publication date exists. |

## advisories

| Field | Type | Notes |
|---|---|---|
| advisory_id | INTEGER PK | |
| location_id | INTEGER FK | |
| commodity_id | INTEGER FK | Nullable. Some advisories are not crop specific. |
| issue_date | DATE | Join key |
| advisory_type | TEXT | weather, pest, irrigation, sowing, harvest, departmental |
| language | TEXT | |
| summary_text | TEXT | |

Pest and disease information lives here under `advisory_type = 'pest'` rather
than in a separate table. It arrives in the same documents, carries the same
district and date keys, and a separate table would duplicate every column.

## remote_sensing (optional)

Built only if the Sentinel-2 indicator work proceeds. Indicators are aggregated
to district and date before being written, so what is stored is tabular and
joins on the same key as every other fact table. No raster is interpreted at
query time and no image is stored in the database.

## quarantine

| Field | Type | Notes |
|---|---|---|
| quarantine_id | INTEGER PK | |
| target_table | TEXT | Where the row would have gone |
| payload_json | TEXT | The rejected row as extracted |
| failure_reason | TEXT | From `src/validation/validators.py` |
| document_id | INTEGER FK | Nullable |
| created_at | TIMESTAMP | |

Rows failing validation are recorded rather than dropped, so the failure rate is
auditable and reportable at the gates.
