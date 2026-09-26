"""LoRA or QLoRA adapter training.

Owned by the Model Lead. Deliberately separate from evaluation/, so that the
person training the adapter is not the person measuring it.

Hard rule enforced below: this script must never read data/eval/. The held out
set is not used for training and not used for early stopping either. Using it
to decide when to stop is a subtler form of the same contamination and would
make the reported comparison meaningless.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVAL_DIR = (ROOT / "data" / "eval").resolve()


def assert_eval_untouched(cfg: dict) -> None:
    for key in ("train_file", "validation_file"):
        p = cfg.get("data", {}).get(key)
        if not p:
            continue
        if EVAL_DIR in (ROOT / p).resolve().parents or (ROOT / p).resolve() == EVAL_DIR:
            raise SystemExit(
                f"REFUSED: {key} points inside data/eval/. The held out set is "
                "never used for training or early stopping."
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="models/configs/lora_default.yaml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    assert_eval_untouched(cfg)

    print(f"base model : {cfg['base_model']}")
    print(f"output     : {cfg['output_dir']}")
    print(f"train file : {cfg['data']['train_file']}")
    print(f"quantised  : {cfg['quantisation']['load_in_4bit']}")
    print("eval set   : not read (enforced)")

    if args.dry_run:
        print("dry run complete")
        return

    if not cfg["base_model"]:
        raise SystemExit(
            "base_model is not set. Confirm the model licence permits fine "
            "tuning and adapter redistribution before training."
        )

    raise NotImplementedError("Phase 2. Load base model, apply peft LoRA config, train.")


if __name__ == "__main__":
    main()
