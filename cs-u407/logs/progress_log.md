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
