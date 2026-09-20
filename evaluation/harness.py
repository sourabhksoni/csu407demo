"""One evaluation harness, two configurations.

Baseline and adapted runs execute identical code on the identical held out set.
The only difference is the adapter named in the config file. Two parallel
evaluation trees were deliberately rejected: they drift, and then the reported
gap between the models is partly the harness rather than the adapter.

Usage:
    python evaluation/harness.py --config evaluation/configs/baseline.yaml
    python evaluation/harness.py --config evaluation/configs/adapted.yaml
    python evaluation/metrics.py evaluation/results/baseline.json \
                                 evaluation/results/adapted.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from evaluation.metrics import ExtractionEvaluator  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRAIN_DIR = ROOT / "data" / "processed"
EVAL_DIR = ROOT / "data" / "eval"


def load_eval_set(path: pathlib.Path) -> list[dict]:
    """Load the held out set and fingerprint it.

    The fingerprint is written into the results file so that a reviewer can
    confirm both runs saw the same data. If the two result files carry
    different fingerprints the comparison is void.
    """
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return records, digest


def assert_not_contaminated(eval_path: pathlib.Path) -> None:
    """Refuse to run if the eval set also appears under the training directory.

    The brief names eval set contamination as a red flag requiring a fresh
    held out set. Catching it here is cheaper than discovering it at the gate.
    """
    if not TRAIN_DIR.exists():
        return
    eval_hashes = {
        hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
        for r in (json.loads(l) for l in eval_path.read_text().splitlines() if l.strip())
    }
    for train_file in TRAIN_DIR.rglob("*.jsonl"):
        for line in train_file.read_text().splitlines():
            if not line.strip():
                continue
            h = hashlib.sha256(json.dumps(json.loads(line), sort_keys=True).encode()).hexdigest()
            if h in eval_hashes:
                raise SystemExit(
                    f"CONTAMINATION: an eval record also appears in {train_file}. "
                    "Build a fresh held out set before reporting any comparison."
                )


def load_model(cfg: dict):
    """Return a callable mapping document text to a predicted record.

    Implemented in Phase 2. The adapter path is the only difference between
    the two configurations, which is what keeps the comparison fair.
    """
    raise NotImplementedError(
        "Phase 2. Load cfg['base_model'], attach cfg['adapter_path'] when set, "
        "and return a callable taking (text, modality, language) to a dict."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate config and eval set without loading a model.")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    eval_path = ROOT / cfg["eval_set"]

    if not eval_path.exists():
        raise SystemExit(
            f"Eval set not found at {eval_path}.\n"
            "The held out set is built by the Evaluation Lead before any adapter "
            "training begins. See data/eval/README.md."
        )

    assert_not_contaminated(eval_path)
    records, digest = load_eval_set(eval_path)

    print(f"config          : {cfg['name']}")
    print(f"base model      : {cfg['base_model']}")
    print(f"adapter         : {cfg.get('adapter_path') or 'none (baseline)'}")
    print(f"eval set        : {cfg['eval_set']}  ({len(records)} records)")
    print(f"eval fingerprint: {digest}")

    if args.dry_run:
        print("dry run complete, no model loaded")
        return

    model = load_model(cfg)
    ev = ExtractionEvaluator(cfg["schema_fields"], cfg["numeric_fields"])

    for rec in records:
        pred = model(rec["input_text"], rec.get("modality"), rec.get("language"))
        ev.add(pred, rec["ground_truth"])

    report = ev.report()
    report["run"] = {
        "config_name": cfg["name"],
        "base_model": cfg["base_model"],
        "adapter_path": cfg.get("adapter_path"),
        "eval_set": cfg["eval_set"],
        "eval_fingerprint": digest,
        "run_at": datetime.now(timezone.utc).isoformat(),
    }

    out = ROOT / "evaluation" / "results" / f"{cfg['name']}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nwrote {out}")
    for k in ("exact_match", "field_accuracy", "precision", "recall", "f1",
              "numeric_accuracy", "schema_validity"):
        print(f"  {k:18s} {report[k]}")


if __name__ == "__main__":
    main()
