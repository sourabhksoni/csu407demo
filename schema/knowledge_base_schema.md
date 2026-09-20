# Knowledge Base Schema

**Project:** Procurement, Price, Storage and Advisory Intelligence System for Chhattisgarh
**Team:** Team 10
**Status:** Frozen for Phase 1. Changes after this point are recorded in the progress log with
a reason, in line with the brief's warning against schema churn.

---

## Purpose

The knowledge base connects the administered procurement price with open market prices,
storage capacity and agricultural advisories, across districts and time, for Chhattisgarh.

Design is four fact tables over two dimension tables plus a provenance pair. Every fact row
carries a foreign key to the document it was extracted from.

---

## Dimension tables

### Location

| Field | Type | Notes |
|---|---|---|
| location_id | PK | |
| state | text | Always Chhattisgarh in this project |
| district_code | text | Canonical district code |
| district_name | text | Canonical English name |
| district_name_hi | text | Devanagari name as published by state sources |
| block | text | Nullable; present for advisories and some centres |
| place_name | text | Mandi, purchase centre, godown or society name |
| place_type | enum | mandi, sub_mandi, purchase_centre, godown, society |
| predecessor_district_code | text | For districts created in the 2022 reorganisation |

The last two fields carry the reasoning for this table existing separately. Chhattisgarh
created several new districts in 2022, so a dataset from before that date reports a district
set that no longer matches the current one. Without an explicit predecessor mapping, any join
across that boundary silently loses rows or double counts them.

### Commodity

| Field | Type | Notes |
|---|---|---|
| commodity_id | PK | |
| commodity_name | text | Canonical English name |
| commodity_name_hi | text | Devanagari name as published |
| commodity_group | enum | cereal, pulse, oilseed, vegetable, minor_forest_produce |
| reporting_unit | text | Unit the source reports in |
| unit_to_quintal_factor | numeric | Conversion factor to the canonical unit |

Needed because procurement volumes are published in metric tonnes while prices are published
per quintal, and minor forest produce is published per standard bag. Storing the conversion
factor rather than converting at extraction time keeps the original figure auditable against
the source document.

---

## Fact tables

### Procurement

| Field | Type | Notes |
|---|---|---|
| procurement_id | PK | |
| location_id | FK | |
| commodity_id | FK | |
| kms_year | text | Kharif Marketing Season, for example 2025-26 |
| season_start_date | date | Mapped from policy document |
| season_end_date | date | Mapped from policy document |
| quantity_mt | numeric | Aggregate quantity procured |
| declared_rate_per_quintal | numeric | Administered rate for that season |
| centre_count | integer | Number of purchase centres, where published |
| farmer_count | integer | Aggregate count only, never identities |
| source_id | FK | |

Primary source examples: Food, Civil Supplies and Consumer Protection Department procurement
policy orders; open government data procurement centre catalogue; Minor Forest Produce
Federation rate notifications.

Minor forest produce, including tendu leaf, is recorded here rather than in its own table. The
Federation buys it at a declared rate per standard unit through society level lots, which is
the same shape as paddy procurement. Keeping it here avoids a fifth fact table for the same
structure.

### Prices

| Field | Type | Notes |
|---|---|---|
| price_id | PK | |
| location_id | FK | |
| commodity_id | FK | |
| price_date | date | |
| arrivals_tonnes | numeric | |
| price_min | numeric | Per quintal |
| price_max | numeric | Per quintal |
| price_modal | numeric | Per quintal |
| source_id | FK | |

Primary source examples: open government daily mandi price dataset; Agmarknet dashboard;
e-NAM.

### Storage

| Field | Type | Notes |
|---|---|---|
| storage_id | PK | |
| location_id | FK | |
| facility_name | text | |
| agency_type | enum | state_warehousing, central_warehousing, fci, private_registered |
| capacity_mt | numeric | |
| snapshot_date | date | Date we collected it, not a publication date |
| source_id | FK | |

Primary source examples: Chhattisgarh State Warehousing Corporation listing; warehousing
regulator registry; central depot listings.

snapshot_date rather than a publication date because these portals overwrite rather than
archive, so the only honest timestamp available is our own collection date.

### Advisories

| Field | Type | Notes |
|---|---|---|
| advisory_id | PK | |
| location_id | FK | |
| commodity_id | FK | Nullable; some advisories are not crop specific |
| issue_date | date | |
| advisory_type | enum | weather, pest, irrigation, sowing, harvest, departmental |
| language | text | |
| summary_text | text | |
| source_id | FK | |

Primary source examples: agromet district advisories published twice weekly; state agricultural
university extension material; Directorate of Agriculture notices.

---

## Provenance tables

### Source

| Field | Type |
|---|---|
| source_id | PK |
| source_name | text |
| organisation | text |
| base_url | text |
| modality | enum |
| licence | enum |
| update_frequency | text |

### Document

| Field | Type |
|---|---|
| document_id | PK |
| source_id | FK |
| document_name | text |
| document_url | text |
| page_number | integer |
| language | text |
| collected_on | date |
| extraction_confidence | enum |

extraction_confidence is set by the pipeline, low for anything that came through the OCR path.
It is stored rather than discarded so that Phase 3 analysis can be re run excluding low
confidence rows and the difference reported.

---

## Join model

```
                      Procurement
                           |
   District + KMS year mapped to date range
                           |
                           v
Prices  <--- District + Date --->  Advisories
   |                                    |
   +------ District + Date -------------+
                    |
                    v
                 Storage
```

Primary join key across all fact tables is District plus Date. Procurement joins on District
plus Kharif Marketing Season year, with the season mapped to a date range so it can be aligned
against the daily price series.

## Initial query types

- What was the modal market price of paddy in a district on a date, against the declared
  procurement rate for that season?
- Which districts hold the most storage capacity per tonne procured?
- How did the price of a commodity vary across districts on the same day?
- Did market prices move in the week after an agromet advisory was issued?
- Which source, document and page did a particular figure come from?

## Known limitations of this schema

- Storage capacity covers registered and public sector facilities only, not total state
  capacity including on farm storage.
- Storage has no historical archive, so its time series begins at our first collection date.
- Procurement is recorded at season granularity, not daily, because that is how it is
  published. Comparison against daily prices is therefore made at season range level.
- farmer_count is an aggregate only. No farmer identity, land record or Aadhaar linked field
  exists anywhere in this schema, by design.
- District reorganisation in 2022 means pre 2022 rows resolve through a predecessor mapping
  and carry an inherent attribution assumption where a district was split.
