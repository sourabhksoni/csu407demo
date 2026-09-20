# Statement of Purpose and Problem Framework

**Project:** Procurement, Price, Storage and Advisory Intelligence System for Chhattisgarh
**Course:** CS F/U 407, Artificial Intelligence
**Team:** Team 10
**Phase:** Phase 1, Source Discovery and Knowledge Base Design
**Date:** 21 September 2026

---

## 1. The problem we are addressing

Chhattisgarh is one of a small number of states that runs Decentralized Procurement. The state
buys paddy from farmers at a declared support price through purchase centres operated by
Primary Agricultural Cooperative Societies, and it does this at very large scale across every
district. At the same time the state Mandi Board regulates an open wholesale market in which
the same commodity trades at whatever the market pays on a given day.

So in any Chhattisgarh district, on any date in the Kharif Marketing Season, two prices exist
for the same grain. One is administered and fixed. The other moves. Between them sit two
things that decide whether a farmer can wait: how much storage capacity is available nearby,
and what the weather advisory issued that week said.

None of these four things are published together. Procurement policy and season totals live in
Hindi language PDF orders on the Food Department site. Daily market prices live in a national
dashboard with no export button. Storage capacity lives in a warehousing corporation listing
with no history. Advisories live in a twice weekly district bulletin system. Because they are
never joined, a basic question stays unanswerable: in which districts and in which weeks did
the open market price rise far enough above or fall far enough below the administered price to
matter, and did storage availability or advisory timing line up with that movement?

This project builds the knowledge base that makes that question answerable for Chhattisgarh,
with every stored figure traceable to its source document and page.

## 2. Objective

To design and build an agriculture information system for Chhattisgarh that extracts
procurement, price, storage and advisory information from heterogeneous official sources using
an agentic AI pipeline, stores it in a single queryable database with full provenance, and
supports spatial, temporal and provenance queries over it.

## 3. Why this framing

Four reasons drove the choice of procurement, prices, storage and advisories over the more
common production and yield framing.

**It is specific to Chhattisgarh.** Most states can be described with production and yield
tables. The administered price against market price structure is a property of being a DCP
state at this scale. A project framed this way could not be copied onto another state without
changing.

**The modalities are forced, not manufactured.** Procurement policy arrives as Hindi language
PDF government orders. Prices arrive as API and CSV. Storage arrives as an HTML listing with
no export. Advisories arrive as text layer PDF bulletins, and Federation tender notices arrive
as scanned PDF in Hindi. That is the full modality spread the course expects, and it satisfies
the Phase 2 requirement for at least one non English document without us going looking for one.

**There is an honest join key.** All four publish at district level and all four carry a date
or a season year. District plus date is a real common key here, not a forced one.

**The analysis is worth doing.** The relationship between an administered price floor, market
price movement, storage capacity and advisory timing is a real one in the field. The
spatio temporal relationships reported in Phase 3 will mean something rather than being a
correlation exercise.

## 4. Scope of the knowledge base

| Entity | Type | What it holds |
|---|---|---|
| Location | Dimension | State, district, block, market or purchase centre identity, plus name normalisation |
| Commodity | Dimension | Canonical commodity name, group, and the unit each source reports in |
| Procurement | Fact | Season wise quantity procured, declared rate, centre count and participating farmer count by district |
| Prices | Fact | Daily mandi arrivals with minimum, maximum and modal price by commodity, market and district |
| Storage | Fact | Warehousing and godown capacity by facility, agency and snapshot date |
| Advisories | Fact | District level agromet and departmental advisories with issue date and crop |
| Source and Document | Provenance | Source name, URL, document name, page number, modality, language, licence and collection date |

Fact tables join on District plus Date. Procurement joins on District plus Kharif Marketing
Season year, with the season mapped to its date range so it can be compared against daily
price series.

Tendu leaf and other minor forest produce are recorded in the Procurement fact table rather
than a separate subsystem. The Federation buys them at a declared rate per standard unit
through society level lots, which is structurally the same shape as paddy procurement. This is
a deliberate decision to avoid a seventh table, in line with the brief's warning against
schema churn.

## 5. In scope for Phase 1

- Discovering and manually verifying official agriculture data sources for Chhattisgarh
- Recording modality, update frequency, language, licence and limitations for each source
- Documenting what each source can and cannot provide
- Designing the initial schema and writing down the reasoning behind each entity
- Proposing the extraction agent and the tools it will call

## 6. Explicitly out of scope

- Any record level or beneficiary level farmer data. Chhattisgarh's procurement system is
  biometric and Aadhaar linked at farmer level, and that data is excluded entirely. Only
  aggregate district and centre level figures are used.
- Raster and satellite image interpretation. Spatial data is used only where it exists in
  vector or tabular form.
- Inter state comparison, revisited only if Phase 3 time permits.
- Model fine tuning, which belongs to Phase 2 after the baseline and evaluation set exist.

## 7. Questions the system should eventually answer

1. What was the modal market price of paddy in a given district on a given date, and how did
   it sit against the declared procurement rate for that season?
2. Which districts hold the most storage capacity per tonne of paddy procured?
3. How does the market price of a commodity vary across districts on the same day?
4. Do market prices move in the week following an agromet advisory?
5. Which source, document and page did a particular figure come from?

Questions 2 and 3 are spatial, 1 and 4 are temporal, and 5 is a provenance query, which lines
up with what the Phase 3 gate asks for.

## 8. Known constraints going in

- The Food Department publishes procurement policy as Hindi language PDF orders rather than as
  structured data, so season totals must be extracted rather than downloaded.
- The open government dataset for Chhattisgarh paddy procurement centres is of older vintage
  than the current season, so the centre list will need to be reconciled against current
  policy documents rather than trusted as current.
- Warehousing capacity is published as a current listing without history, so the storage time
  series can only begin from our first collection date.
- District boundaries in Chhattisgarh changed materially in 2022 when several new districts
  were created, so older datasets report a different district set and a reconciliation table
  is required before any join.
- District name transliteration varies across sources, including between Hindi and English
  spellings of the same district, and needs a normalisation table.
- Agromet advisories are published twice a week and are not archived indefinitely by all
  routes, so historical depth may be limited and collection should start early.

These are recorded as limitations rather than hidden, and unverifiable sources are kept in the
inventory as documented data gaps.
