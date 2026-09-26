"""Extraction metrics for the with and without adapter comparison.

One implementation, used by both configurations. The whole point of a single
harness is that baseline and adapted numbers cannot differ because of the
measuring code.

Metric choices follow docs/phase1/agent_tool_plan.md section 6.4. Precision and
recall are reported separately because the two failure modes are not equivalent:
low recall means information present in the document was missed, low precision
means information was produced that was not there. The second is the failure the
null contract exists to prevent, and averaging them away hides it.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict, field
from typing import Any, Iterable

NUMERIC_TOLERANCE = 1e-6


def _is_blank(v: Any) -> bool:
    """A field the extractor declined to fill. Null is a valid answer."""
    return v is None or (isinstance(v, str) and v.strip() == "")


def _numeric(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        cleaned = v.replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def values_equal(pred: Any, truth: Any) -> bool:
    """Compare one field. Numbers compare numerically, text compares
    case insensitively after whitespace collapse."""
    if _is_blank(pred) and _is_blank(truth):
        return True
    if _is_blank(pred) or _is_blank(truth):
        return False

    p_num, t_num = _numeric(pred), _numeric(truth)
    if p_num is not None and t_num is not None:
        return math.isclose(p_num, t_num, rel_tol=NUMERIC_TOLERANCE, abs_tol=NUMERIC_TOLERANCE)

    return " ".join(str(pred).split()).casefold() == " ".join(str(truth).split()).casefold()


@dataclass
class Counters:
    records: int = 0
    exact_matches: int = 0

    fields_total: int = 0        # every schema field across every record
    fields_correct: int = 0

    # Precision and recall are computed over populated fields.
    true_positive: int = 0       # populated in both, and equal
    false_positive: int = 0      # populated by model, wrong or absent in truth
    false_negative: int = 0      # populated in truth, blank or wrong in model

    numeric_total: int = 0
    numeric_correct: int = 0

    schema_valid: int = 0

    per_field: dict = field(default_factory=dict)


class ExtractionEvaluator:
    def __init__(self, schema_fields: Iterable[str], numeric_fields: Iterable[str]):
        self.schema_fields = list(schema_fields)
        self.numeric_fields = set(numeric_fields)
        self.c = Counters()
        for f in self.schema_fields:
            self.c.per_field[f] = {"total": 0, "correct": 0}

    def _schema_valid(self, pred: Any) -> bool:
        """Parses as an object and contains no key outside the schema.
        Missing keys are treated as null, which the contract permits."""
        if not isinstance(pred, dict):
            return False
        return all(k in self.schema_fields for k in pred.keys())

    def add(self, pred: Any, truth: dict) -> None:
        self.c.records += 1

        valid = self._schema_valid(pred)
        if valid:
            self.c.schema_valid += 1
        else:
            # Unparseable output still counts as a record, with every field wrong.
            self.c.fields_total += len(self.schema_fields)
            for f in self.schema_fields:
                self.c.per_field[f]["total"] += 1
                if not _is_blank(truth.get(f)):
                    self.c.false_negative += 1
            return

        all_correct = True
        for f in self.schema_fields:
            p, t = pred.get(f), truth.get(f)
            ok = values_equal(p, t)

            self.c.fields_total += 1
            self.c.per_field[f]["total"] += 1
            if ok:
                self.c.fields_correct += 1
                self.c.per_field[f]["correct"] += 1
            else:
                all_correct = False

            p_blank, t_blank = _is_blank(p), _is_blank(t)
            if not p_blank and not t_blank:
                if ok:
                    self.c.true_positive += 1
                else:
                    self.c.false_positive += 1
                    self.c.false_negative += 1
            elif not p_blank and t_blank:
                self.c.false_positive += 1      # invented a value
            elif p_blank and not t_blank:
                self.c.false_negative += 1      # missed a value

            if f in self.numeric_fields and not t_blank:
                self.c.numeric_total += 1
                if ok:
                    self.c.numeric_correct += 1

        if all_correct:
            self.c.exact_matches += 1

    def report(self) -> dict:
        c = self.c
        tp, fp, fn = c.true_positive, c.false_positive, c.false_negative
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        def pct(n, d):
            return round(n / d, 4) if d else 0.0

        return {
            "records": c.records,
            "exact_match": pct(c.exact_matches, c.records),
            "field_accuracy": pct(c.fields_correct, c.fields_total),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "numeric_accuracy": pct(c.numeric_correct, c.numeric_total),
            "schema_validity": pct(c.schema_valid, c.records),
            "counts": {k: v for k, v in asdict(c).items() if k != "per_field"},
            "per_field_accuracy": {
                f: pct(v["correct"], v["total"]) for f, v in c.per_field.items()
            },
        }


def compare(baseline: dict, adapted: dict) -> dict:
    """Side by side with deltas. Reported honestly, including negative deltas."""
    keys = ["exact_match", "field_accuracy", "precision", "recall",
            "f1", "numeric_accuracy", "schema_validity"]
    rows = []
    for k in keys:
        b, a = baseline.get(k, 0.0), adapted.get(k, 0.0)
        rows.append({"metric": k, "baseline": b, "adapted": a, "delta": round(a - b, 4)})
    return {"comparison": rows}


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        b = json.load(open(sys.argv[1]))
        a = json.load(open(sys.argv[2]))
        print(json.dumps(compare(b, a), indent=2))
    else:
        print("usage: python metrics.py baseline_results.json adapted_results.json")
