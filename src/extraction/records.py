"""Schema field definitions shared by the extractor, the prompt and the harness.

Single definition so the three cannot disagree. A mismatch between the prompt's
field list and the evaluator's field list would silently distort every
schema_validity figure.
"""

from __future__ import annotations

PRODUCTION_FIELDS = ["crop", "district", "season", "year",
                     "area", "production", "yield", "unit"]
PRODUCTION_NUMERIC = ["area", "production", "yield"]

PRICE_FIELDS = ["commodity", "district", "market", "price_date",
                "price_min", "price_modal", "price_max", "arrivals", "unit"]
PRICE_NUMERIC = ["price_min", "price_modal", "price_max", "arrivals"]

PROCUREMENT_FIELDS = ["commodity", "district", "kms_year", "declared_rate",
                      "quantity", "centre_count", "farmer_count", "unit"]
PROCUREMENT_NUMERIC = ["declared_rate", "quantity", "centre_count", "farmer_count"]


def empty(fields: list[str]) -> dict:
    """A record with every field null. The extractor starts here and fills
    only what the document actually states."""
    return {f: None for f in fields}
