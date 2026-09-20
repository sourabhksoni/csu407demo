"""Validation layer.

Nothing reaches the database until it clears these checks. Rows that fail are
not discarded: they go to the quarantine table with a reason, so the failure
rate itself becomes a reportable metric at the Phase 2 and Phase 3 gates.

The brief treats silently dropped rows as a red flag, and a pipeline that
hides its failures cannot be audited.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.normalisation import commodities as cm
from src.normalisation.districts import default as districts


@dataclass
class ValidationResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    normalised: dict = field(default_factory=dict)

    def fail(self, reason: str) -> "ValidationResult":
        self.ok = False
        self.reasons.append(reason)
        return self


def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def validate_price_row(row: dict) -> ValidationResult:
    r = ValidationResult(ok=True)

    for f in ("district", "commodity", "price_date"):
        if _blank(row.get(f)):
            r.fail(f"required_field_missing:{f}")

    d = districts().resolve(row.get("district", ""))
    if d is None and not _blank(row.get("district")):
        r.fail("district_unresolved")
    elif d:
        r.normalised["district_code"] = d.code

    c = cm.resolve(row.get("commodity", ""))
    if c is None and not _blank(row.get("commodity")):
        r.fail("commodity_out_of_scope_or_unresolved")
    elif c:
        r.normalised["commodity_key"] = c.key

    lo, mo, hi = row.get("price_min"), row.get("price_modal"), row.get("price_max")
    for label, v in (("price_min", lo), ("price_modal", mo), ("price_max", hi)):
        if v is not None:
            if not isinstance(v, (int, float)):
                r.fail(f"non_numeric:{label}")
            elif v <= 0:
                r.fail(f"non_positive:{label}")
            elif v > 1_000_000:
                r.fail(f"implausible_magnitude:{label}")

    if all(isinstance(v, (int, float)) for v in (lo, mo)) and lo > mo:
        r.fail("ordering:min_exceeds_modal")
    if all(isinstance(v, (int, float)) for v in (mo, hi)) and mo > hi:
        r.fail("ordering:modal_exceeds_max")

    if _blank(row.get("source_id")):
        r.fail("provenance_missing:source_id")
    if row.get("document_id") is None and row.get("modality") in (
        "digital_pdf", "scanned_pdf_ocr"
    ):
        r.fail("provenance_missing:document_id_required_for_document_sources")

    return r


def validate_procurement_row(row: dict) -> ValidationResult:
    r = ValidationResult(ok=True)

    for f in ("district", "commodity", "kms_year"):
        if _blank(row.get(f)):
            r.fail(f"required_field_missing:{f}")

    d = districts().resolve(row.get("district", ""))
    if d is None and not _blank(row.get("district")):
        r.fail("district_unresolved")
    elif d:
        r.normalised["district_code"] = d.code

    c = cm.resolve(row.get("commodity", ""))
    if c is None and not _blank(row.get("commodity")):
        r.fail("commodity_out_of_scope_or_unresolved")
    elif c:
        r.normalised["commodity_key"] = c.key

    qty, unit = row.get("quantity"), row.get("unit")
    if qty is not None and unit:
        converted = cm.to_quintal(qty, unit)
        if converted is None:
            r.fail(f"no_unit_conversion:{unit}")
        else:
            r.normalised["quantity_quintal"] = converted

    if row.get("farmer_count") is not None and row.get("farmer_count") < 0:
        r.fail("non_positive:farmer_count")

    for forbidden in ("farmer_name", "aadhaar", "account_number", "beneficiary_id"):
        if forbidden in row:
            r.fail(f"personal_data_present:{forbidden}")

    if _blank(row.get("source_id")):
        r.fail("provenance_missing:source_id")

    return r


def validate_extraction_contract(record: dict, schema_fields: list[str]) -> ValidationResult:
    """The extractor must emit null for absent fields rather than guessing.

    A null is a correct answer. A plausible guess is a silent data error that
    propagates into every downstream query and cannot be detected later
    without re reading the original document.
    """
    r = ValidationResult(ok=True)
    unknown = set(record) - set(schema_fields)
    if unknown:
        r.fail(f"schema_violation:unexpected_fields:{sorted(unknown)}")
    for f in schema_fields:
        if f not in record:
            r.fail(f"contract_violation:field_omitted_instead_of_null:{f}")
    return r
