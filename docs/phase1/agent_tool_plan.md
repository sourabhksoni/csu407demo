# Proposed Agent and Tool Architecture

**Project:** Procurement, Price, Storage and Advisory Intelligence System for Chhattisgarh
**Team:** Team 10
**Phase:** Phase 1 proposed design, to be implemented in Phase 2

---

## 1. Design idea

Rather than writing one script per source, we plan a single controller agent that inspects an
incoming document, decides what kind of thing it is, and calls the right tool for it. That
keeps the system open to sources we have not seen, which matters because the Phase 2 gate
tests live extraction on unseen documents supplied by the instructor, at least one of which
will not be in English.

The agent is responsible for routing and for deciding when an extraction has failed. The tools
do the actual reading. The schema mapper is kept separate from the extractors so that a change
to the schema does not mean rewriting every extractor.

### Governing principle

Use deterministic tools wherever deterministic processing is sufficient, and use the language
model only where semantic interpretation is required.

An already structured numerical table does not need a language model to read it, and sending
it through one adds cost, latency and a hallucination risk in exchange for nothing. The
language model earns its place where the information is embedded in prose, where the layout is
irregular, where terminology has to be resolved across languages, or where a figure has to be
associated with the entity it describes rather than simply read off a grid.

This principle decides the routing table in section 3: API and CSV sources are handled with no
model in the loop at all, HTML tables are parsed deterministically and only escalated when
parsing fails, and the model is reserved for the PDF and OCR paths.

### Extraction contract

The extraction agent must not invent missing information. Where a schema field is not present
in the source document, the extractor returns null for that field and the row carries a
completeness flag. A null is a correct answer. A plausible guess is a silent data error that
propagates into every downstream query and cannot be detected later without re reading the
original document.

This is enforced at two points: the prompt states it explicitly, and the validator rejects any
row whose non null fields cannot be located in the source text span the extractor cited.

## 2. Pipeline

```
Source document
      |
      v
[ Ingestion ]        record URL, collection date, language, licence in the manifest
      |
      v
[ Router Agent ]     classify modality: API / CSV / HTML / text PDF / scanned PDF / voice-audio
      |
      v
[ Extraction Tool ]  selected by modality
      |
      v
[ Normaliser ]       district, commodity and unit resolved to canonical values
      |
      v
[ Schema Mapper ]    map raw fields to Procurement / Prices / Storage / Advisories
      |
      v
[ Validator ]        pass, or route to quarantine with a reason
      |
      v
[ Database ]         row written with its provenance record attached
      |
      v
[ Query Agent ]      natural language question to SQL to answered result with citation
```

## 3. Tools by modality

### 3.1 Structured API and CSV

Representative source: data.gov.in daily mandi price resource; Chhattisgarh procurement centre
catalogue.

Tools: HTTP client plus a tabular loader.
Work done: paginated pull, filter to Chhattisgarh, type coercion on dates and prices,
deduplication on district, market, commodity and date. This is the cleanest path and needs no
language model in the loop. It is also where the un tuned baseline gets most of its easy wins,
which is exactly why the adapter comparison must not be measured only here.

### 3.2 HTML dashboard with no export

Representative source: Agmarknet price dashboard; Chhattisgarh State Warehousing Corporation
godown listing; e-NAM.

Tools: headless browser driver plus an HTML table parser.
Work done: drive the state and district selectors, read the rendered table, stamp every row
with the snapshot date because these portals overwrite rather than archive. Selectors are kept
in a configuration file rather than in code so that a portal redesign is a config change.
Scraping respects robots.txt and is rate limited, and an official bulk download is preferred
wherever one exists.

### 3.3 PDF with a text layer

Representative source: IMD agromet advisory bulletins; Directorate of Economics and Statistics
statistical publications.

Tools: PDF text and layout extractor, then a language model based field extractor.
Work done: pull text per page, locate the district block, and return a structured advisory or
statistics record. Page number is carried through so the provenance query can point back to it.

### 3.4 Scanned or mixed PDF, including Hindi

Representative source: Food Department Kharif Marketing Season procurement policy orders;
Minor Forest Produce Federation tendu leaf tender notices and rate schedules.

Tools: OCR with Devanagari support, then table structure recovery, then the same field
extractor.
Work done: rasterise, OCR, rebuild the table grid, map columns to schema fields. This is the
weakest link and we expect a meaningful failure rate, so anything from this path carries a
lower confidence flag and is sampled for manual checking.

This path is deliberately retained rather than avoided. It is where a prompted base model
degrades most, and therefore the clearest place to demonstrate what LoRA or QLoRA adaptation
adds over prompt engineering alone.

### 3.5 Voice and call centre derived text

Representative source: ICAR-IASRI Kisan Call Centre query and response archive
(KCC-CHAKSHU), covering farmer phone queries answered by Farm Tele Advisors, filterable to
Chhattisgarh district and month.

Tools: `tools.api_csv` for the distributed export, `tools.audio_transcribe` (Whisper) reserved
for raw recordings.
Work done: the archive ICAR distributes is already transcribed query and answer text keyed by
state, district, month, crop and query type, so it is read deterministically through the same
path as any other structured export, with no model in the loop. The voice and audio modality
itself is genuine, not manufactured: farmers place these as phone calls, and the transcription
step already happened upstream, at the source, rather than inside this pipeline. A
`voice_audio` router branch and a `tools.audio_transcribe` module exist for the case where raw
call recordings are obtained directly rather than this pre transcribed export; that path
transcribes with Whisper, including Hindi and regional language support to match the OCR
path's language coverage, then reuses the same model based field extractor as the PDF path.
Output from the raw audio path carries a low extraction confidence flag, for the same reason
as the OCR path: transcription error compounds with extraction error.

### 3.6 Supporting tool: district and commodity normaliser

Two lookup tables. The first maps every observed district spelling, in Hindi and in English,
to one canonical district code, and additionally maps pre 2022 districts onto the current
district set so that older data can be joined without silently losing rows. The second maps
commodity names and reporting units to canonical values, because procurement reports in
quintals and metric tonnes while prices report per quintal.

Every extractor calls both before writing. Without this the District plus Date join loses rows
silently, which is the failure mode that is hardest to notice later.

## 4. Validation layer

Nothing is written to the database until it clears these checks.

| Check | What it catches |
|---|---|
| Required fields present | Partial OCR rows and truncated API responses |
| Type and range check | Prices that are zero, negative or absurdly large; dates outside the collection window |
| Ordering check on prices | Rows where minimum exceeds modal, or modal exceeds maximum |
| District resolves to a canonical name | Spelling drift, Hindi and English variants, pre 2022 districts, stray header rows read as data |
| Unit resolves and converts | Quintal against metric tonne confusion in procurement figures |
| Duplicate key check | Repeated pulls of the same district, market, commodity and date |
| Provenance present | Any row that cannot name its source, document and page |

Rows that fail are not discarded. They go to a quarantine table with the failure reason, so the
failure rate itself becomes a reportable metric at the Phase 2 and Phase 3 gates.

A sample of scanned PDF output is additionally checked by hand against the original document,
and that manual agreement rate becomes our OCR accuracy estimate.

## 5. Provenance handling

Every row written to Procurement, Prices, Storage or Advisories carries a foreign key into the
Source and Document tables, holding source name, URL, document name, page number, modality,
language and collection date. This is what makes the Phase 3 provenance query answerable
directly rather than reconstructed afterwards.

## 6. Model plan

### 6.1 Baseline first

Phase 2 begins with a prompted base model and no adapter. The evaluation set is built and held
out before any training happens, and it is drawn deliberately across all four modalities rather
than only the easy ones, so that the with and without adapter comparison is not flattered by
clean CSV cases.

### 6.2 Training corpus

Adapter training data is built as paired examples, each one a source text span together with
the ground truth structured record a correct extraction should produce:

```
input   document text span, plus its modality and language
output  structured record conforming to the schema, with null for absent fields
```

Ground truth records are written by hand against the original document, not generated by the
base model, because a corpus labelled by the model being evaluated cannot measure whether
adaptation helped. Examples are weighted towards Hindi language and scanned document cases,
which is where prompting alone is weakest and therefore where an adapter has the most room to
show a difference.

### 6.3 Comparison

Two configurations are evaluated on the identical held out set:

| Configuration | Composition |
|---|---|
| Model A, baseline | Base LLM plus prompt plus schema |
| Model B, adapted | Base LLM plus LoRA or QLoRA adapter plus the same prompt and schema |

### 6.4 Metrics

| Metric | What it measures |
|---|---|
| Exact match | Whole record identical to ground truth |
| Field level accuracy | Correct fields as a proportion of all fields, so partial credit is visible |
| Precision, recall and F1 | Over extracted fields, to separate missed information from invented information |
| Numeric extraction accuracy | Correctness of the numbers specifically, since a wrong figure is worse than a missing one |
| Schema validity | Proportion of outputs that parse and conform to the schema without repair |

Reporting precision and recall separately matters here because the two failure modes are not
equivalent. Low recall means the extractor missed information that was present. Low precision
means it produced information that was not, which is the failure the null contract in section 1
exists to prevent.

If the adapter does not beat the baseline we report that result rather than adjusting the
evaluation set to make it look better.

Base model licence will be checked to confirm it permits fine tuning and redistribution of
adapters before training begins. Adapter weights are submitted, not the full base model.

## 7. Known risks in this plan

- Portal structure changes will break the HTML scrapers. Selectors live in configuration.
- Devanagari OCR quality on scanned government orders may make some tables unusable. Those
  documents then move to the documented gaps list rather than being silently dropped.
- Storage has no historical archive, so the storage time series is thin for the whole of
  Phase 2 and early analysis will lean more on the procurement, price and advisory relationship.
- Advisory bulletins are published twice a week and older ones may not remain retrievable, so
  advisory collection should begin at the start of Phase 2 rather than near its end.
