# Evaluation

Owned by the Evaluation Lead. This directory is deliberately separate from
`models/` so that the person training the adapter is not the person measuring it.

## Why one harness and not two directories

An earlier layout had `evaluation/baseline/` and `evaluation/lora/` as separate
trees. That was rejected. Two copies of evaluation code drift: one gets a bug
fix, one normalises whitespace before comparing, one uses a different prompt.
The reported gap between the models then reflects the harness as much as the
adapter, and there is no way to tell how much of it is real.

The gate requires both models on the same held out set. One harness, one metrics
module, one eval file, and a single config field that differs.

## Running

```
python evaluation/harness.py --config evaluation/configs/baseline.yaml --dry-run
python evaluation/harness.py --config evaluation/configs/baseline.yaml
python evaluation/harness.py --config evaluation/configs/adapted.yaml
python evaluation/metrics.py evaluation/results/baseline.json \
                             evaluation/results/adapted.json
```

## Contamination guard

`harness.py` refuses to run if any record in the eval set also appears under
`data/processed/`. The brief names eval set contamination as a red flag
requiring a fresh held out set, so the check runs before every evaluation
rather than being left to discipline.

Each results file records a fingerprint of the eval set. If the baseline and
adapted results carry different fingerprints, the comparison is void.

## Reporting

If the adapter does not beat the baseline, that result is reported. Adjusting
the eval set until the adapter looks better is the exact failure the held out
set exists to prevent.
