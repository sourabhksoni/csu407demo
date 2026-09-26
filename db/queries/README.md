# Ten sample queries

Required submission artifact. The Phase 3 gate runs ten queries live, including at
least two spatial, two temporal and one provenance query.

| # | File | Type | Question |
|---|---|---|---|
| 1 | q01_modal_price_vs_declared_rate.sql | temporal | Market modal price against the declared procurement rate, by week |
| 2 | q02_price_divergence_by_district.sql | spatial | Which districts diverged most from the administered rate |
| 3 | q03_storage_per_tonne_procured.sql | spatial | Storage capacity per tonne procured, by district |
| 4 | q04_price_after_advisory.sql | temporal | Price movement in the week following an advisory |
| 5 | q05_provenance_lookup.sql | provenance | Which source, document and page a figure came from |
| 6 | q06_procurement_by_season.sql | temporal | Procurement volume and declared rate by season |
| 7 | q07_cross_district_same_day.sql | spatial | Price of one commodity across districts on a single day |
| 8 | q08_tendu_rate_by_season.sql | temporal | Tendu leaf declared rate by collection season |
| 9 | q09_low_confidence_audit.sql | provenance | Rows sourced from the OCR path, for re running analysis without them |
| 10 | q10_quarantine_rate.sql | provenance | Validation failure rate by source and reason |

Queries 2, 3 and 7 are spatial. Queries 1, 4, 6 and 8 are temporal. Queries 5, 9
and 10 are provenance. That satisfies the gate distribution with margin.

Expected results are recorded in expected_results.md once the database is populated
in Phase 2. Until then each file states what shape of result it should return.
