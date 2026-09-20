# Project Progress Log

**Team 10, Chhattisgarh**
**Course:** CS F/U 407, Artificial Intelligence

---

## 8 to 12 September 2026, Initial Setup

- Selected Chhattisgarh as the state for the agriculture information system.
- Registered as Team 10 in the shared allocation register.
- Created the GitHub repository `cs-u407`.
- Declared team roles: Source and Data Engineering Lead (Pushti Amish Shah), Model Lead
  (Sourabh Kumar Soni), Evaluation Lead (Priyanshu Khandal).
- Instructor in Charge and TA to be added as repository collaborators.
- Course NDA and IP agreement pending team sign off before data collection begins.

## 15 to 18 September 2026, Problem Framing

- Reviewed the generic production and yield framing and rejected it as not specific to the
  state. Any team could produce it for any state.
- Identified that Chhattisgarh operates Decentralized Procurement at large scale, so an
  administered paddy price and an open mandi price coexist in every district during the
  Kharif Marketing Season.
- Chose Procurement, Prices, Storage and Advisories as the four fact areas on that basis.
- Confirmed the framing forces the full modality spread required by the course: Hindi language
  PDF policy orders, CSV and API price data, HTML listings with no export, text layer advisory
  PDFs and scanned Federation notices.
- Noted that the Federation tender and rate documents supply the non English document the
  Phase 2 gate requires, without having to go looking for one artificially.

## 19 to 21 September 2026, Source Discovery and Verification

- Compiled 21 candidate agriculture information sources for Chhattisgarh across the categories
  named in the brief: monitoring, production, storage, logistics, prices, trade, advisories
  and registries.
- Ran a verification pass, opening each candidate rather than trusting the compiled list.
- Outcome: 14 verified live, 5 marked as needing verification of the specific data page, 2
  retained as documented data gaps where no usable official source could be located.
- Recorded modality, language, update frequency, licence and limitations for every surviving
  source.
- Confirmed the main modalities in use:
  - Structured CSV and API data, via open government data catalogues
  - HTML dashboards and listings with no export function
  - Text layer PDF bulletins, for agromet advisories and statistical publications
  - Scanned and mixed PDF in Hindi, for procurement policy orders and Federation notices
- Designed the knowledge base schema around four fact tables, two dimension tables and a
  provenance pair, and froze it for Phase 1.
- Identified the 2022 district reorganisation as a concrete data engineering problem requiring
  a predecessor district mapping before any join across that boundary.
- Identified unit inconsistency between procurement volumes and price quotations as a second
  normalisation requirement.
- Drafted the proposed extraction agent and tool architecture.
- Prepared the Phase 1 source inventory workbook.
- Uploaded project documentation to GitHub.

## Open items going into the Phase 1 review

- Add Instructor in Charge and TA as repository collaborators.
- Complete team sign off on the course NDA and IP agreement.
- Resolve the 5 sources currently marked as needing verification of the specific data page.
- Confirm retrievable historical depth for agromet advisory bulletins, since collection depth
  determines whether the advisory to price relationship is testable.
- Prepare the Phase 1 presentation.

## Next phase planning

- Begin advisory collection early in Phase 2, because the bulletins are published twice weekly
  and historical retrievability is uncertain.
- Build the district normalisation and predecessor mapping table before any extraction, not
  after.
- Build the held out evaluation set across all four modalities before any fine tuning begins.

## 21 September 2026, Repository Implementation

### Structure
- Implemented the full repository layout in the single course repository rather
  than creating a second one, per the brief's requirement to keep all code and
  documentation together from the beginning.
- Moved scraper selectors and the source registry into `config/` so that a
  portal redesign is a configuration edit rather than a code change.
- Added `db/` holding the schema, data dictionary, migrations and the ten sample
  queries. These are named submission artifacts and were previously homeless.
- Added `data/manifest.csv` and `logs/`, both required by the submission list.

### Evaluation design decision
- Rejected separate `evaluation/baseline/` and `evaluation/lora/` directories.
  Two evaluation code paths drift, and the reported gap between the models would
  then reflect the harness as much as the adapter. Built one harness taking a
  config, where baseline and adapted differ in a single field.
- Added a contamination guard: the harness refuses to run if any eval record also
  appears under `data/processed/`, and `models/train_lora.py` refuses to run if
  its config points inside `data/eval/`.
- Each results file records a fingerprint of the eval set, so a reviewer can
  confirm both runs saw identical data.

### Normalisation
- Implemented district normalisation covering all 33 current districts, with
  alias and Devanagari resolution and an explicit predecessor mapping for the
  districts created in 2022.
- Implemented commodity and unit normalisation. Standard bag deliberately has no
  mass conversion factor, since it is a count rather than a mass and inventing a
  factor would corrupt every tendu aggregate.
- 19 tests passing across normalisation, validation and routing.

### Open item raised
- The district predecessor mapping in `src/normalisation/districts.csv` uses
  project internal codes and must be confirmed against the state gazette
  notifications before any pre 2022 data is loaded.

## 21 September 2026, Inventory Merge

- Merged a second independently compiled source inventory into the Phase 1
  workbook. Combined total is 33 candidate sources: 24 verified, 7 needing
  verification, 2 documented gaps.
- Adopted the distinction between Verified and Sample pulled as separate columns.
  Verified means the page was checked against live evidence. Sample pulled means
  a file has actually been retrieved and hashed into the manifest. Collapsing the
  two would assert more than the team has checked, and Sample pulled is currently
  N on every row.
- Added ICRISAT District Level Database, which supplies district level area,
  yield and production for 20 major crops through an API. Its licence permits
  copying and distribution with acknowledgement through the published DOI.
  Recorded the limitation that its series ends around 2015 to 2017, so it is a
  historical backbone rather than a current source and does not cover the 2022
  reorganisation. Its apportionment method is nonetheless the approach to borrow
  for handling that reorganisation.
- Added NASA POWER and the IMD public API as weather sources, replacing a
  placeholder row. Weather is required as a confound control: it plausibly drives
  both advisory issuance and price movement.
- Added national crop production and paddy sown area datasets, land use
  statistics, and both ICAR advisory editions including the regional languages
  edition.
- Corrected two URLs carried from an earlier draft. A procurement centre
  catalogue pointed at another state's open data node, and a state statistics
  file path contained a transposed spelling and a malformed directory structure.
  The second could not be confirmed and is now marked as needing verification.
- Recorded the licence caution that not every government website falls under the
  Open Government Licence, and separated OGL-India datasets from government sites
  publishing no reuse terms.
