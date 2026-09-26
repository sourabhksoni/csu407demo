# Intelligent Agriculture Information System: Chhattisgarh

**Course:** CS F/U 407, Artificial Intelligence, Class Project (30%)
**Team:** Team 10
**State:** Chhattisgarh
**Repository:** https://github.com/sourabhsoni0104/cs-u407

## Team and roles

| Name | BITS ID | Role |
|---|---|---|
| Pushti Amish Shah | 2024A7PS0514P | Source and Data Engineering Lead |
| Sourabh Kumar Soni | 2025A7PS0642P | Model Lead |
| Priyanshu Khandal | 2025PHXP0406P | Evaluation Lead |

## Project overview

Chhattisgarh is a Decentralized Procurement state. The government buys paddy
from farmers at a declared support price through cooperative society run
purchase centres in every district, while an open wholesale market operates
alongside it under the state Mandi Board. Every district therefore carries two
price signals at the same time, one administered and fixed, one moving, with
storage capacity and weather advisories sitting between them and deciding
whether a farmer can afford to wait.

None of these four things are published together. This project consolidates
them into a single queryable database in which every stored number can be
traced back to the document and page it came from, using an agentic AI pipeline
whose underlying language model is adapted with LoRA or QLoRA and measured
against its own un adapted baseline.

## Repository structure

```
config/              Source registry and scraper selectors, kept out of code
  sources.yaml         Every fetchable source, mirrors Sheet 2 of the workbook
  selectors.yaml       Scraper selectors and the global scraping policy

data/
  manifest.csv         Provenance row per collected file. Gate artifact.
  raw/                 Collected documents, gitignored
  processed/           Derived training data, gitignored, rebuildable
  eval/                Held out evaluation set. Evaluation Lead owns this.
  sentinel/            Sentinel-2 derived indicators, optional, gitignored

db/
  schema.sql           Knowledge base schema
  data_dictionary.md   Field level documentation
  migrations/          Ordered schema changes
  queries/             The ten sample queries with expected results

src/
  router/              Modality classification and tool dispatch
  tools/               api_csv, html_table, pdf_text, ocr, audio_transcribe
  extraction/          Schema mapping from text to records
  normalisation/       District and commodity canonicalisation
  validation/          Checks that gate every write, quarantine on failure
  analytics/           Phase 3 spatio temporal analysis

models/
  train_lora.py        Adapter training. Never reads data/eval/.
  configs/             LoRA config and the extraction prompt
  adapters/            Trained weights, gitignored

evaluation/
  harness.py           One harness, two configs. Baseline and adapted.
  metrics.py           Exact match, field accuracy, P/R/F1, numeric, schema validity
  configs/             baseline.yaml and adapted.yaml differ in one field
  results/             Comparison output, version controlled

docs/                  Phase 1 submission documents and schema documentation
logs/                  Dated progress log
tests/                 Normalisation and validation tests
reports/               Interim and final reports

Team10_Chhattisgarh_Source_Inventory_Phase1.xlsx    Phase 1 workbook
```

## Structural decisions worth knowing

**One evaluation harness, not two directories.** An earlier layout had separate
`evaluation/baseline/` and `evaluation/lora/` trees. Two copies of evaluation
code drift, and the reported gap between the models then reflects the harness as
much as the adapter. One harness, one metrics module, one eval file, and a single
config field that differs.

**The eval set has its own path and its own owner.** `data/eval/` is read by the
evaluation harness and by nothing else. `models/train_lora.py` refuses to run if
its config points inside it, and `evaluation/harness.py` refuses to run if any
eval record also appears under `data/processed/`. The brief names eval set
contamination as a red flag, so the guard is structural rather than a matter of
discipline.

**Normalisation is its own module.** District and commodity canonicalisation is
load bearing: Chhattisgarh reorganised its districts in 2022, so pre 2022 data
reports a district set that no longer matches, and joining across that boundary
without a predecessor mapping silently drops or double counts rows. If this logic
lived inside each extractor the copies would drift and the loss would be invisible
until November.

**Deterministic first.** The router sends `api_csv` and `html_table` down paths
with no language model in the loop, and reserves the model for `digital_pdf` and
`scanned_pdf_ocr`. An already structured numerical table gains nothing from a
model and pays for it in cost, latency and hallucination risk.

**Failures are counted, not dropped.** Rows failing validation go to the
`quarantine` table with a reason. The failure rate is a reportable metric.

## Getting started

```
pip install -r requirements.txt
python -m pytest tests/ -q

python evaluation/harness.py --config evaluation/configs/baseline.yaml --dry-run
python models/train_lora.py --dry-run
sqlite3 agri.db < db/schema.sql
```

## Phase 1 status

- 36 candidate sources reviewed: 26 verified live, 8 needing verification, 2
  retained as documented data gaps. Verified means the source page was checked
  against live evidence; it does not mean a file has been downloaded. That is
  tracked separately and is currently N on every row.
- Knowledge base schema designed and frozen
- Agent and tool architecture drafted, now including a voice/audio modality
  and a Whisper based `tools.audio_transcribe` stage
- Commodity scope frozen to four — Paddy, Maize, Chana (Bengal gram) and
  Tendu leaf — including one control commodity with no administered price
- Crop stages extended to cover seed and farm planning information, alongside
  monitoring, production, aggregation/storage/logistics and market/supply
  chain, closing the Phase 1 stage-coverage gap (see
  `docs/phase1/statement_of_purpose.md`, section 4b)
- Evaluation harness and metrics implemented and tested
- District and commodity normalisation implemented and tested, 20 tests passing

