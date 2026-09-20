import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.router.router import Modality, Router
from src.validation.validators import (
    validate_extraction_contract,
    validate_price_row,
    validate_procurement_row,
)

VALID_PRICE = {
    "district": "Kawardha", "commodity": "Rice", "price_date": "2026-01-10",
    "price_min": 2800, "price_modal": 3000, "price_max": 3200,
    "source_id": "agmarknet", "modality": "html_table",
}


def test_valid_price_row_passes_and_normalises():
    r = validate_price_row(VALID_PRICE)
    assert r.ok
    assert r.normalised["district_code"] == "CG-KAB"


def test_price_ordering_violation_caught():
    row = dict(VALID_PRICE, price_min=3500)
    assert "ordering:min_exceeds_modal" in validate_price_row(row).reasons


def test_missing_provenance_caught():
    row = dict(VALID_PRICE, source_id="")
    assert "provenance_missing:source_id" in validate_price_row(row).reasons


def test_personal_data_rejected():
    row = {"district": "Raipur", "commodity": "Paddy", "kms_year": "2025-26",
           "source_id": "cg_fcs", "farmer_name": "X"}
    assert "personal_data_present:farmer_name" in validate_procurement_row(row).reasons


def test_contract_requires_null_not_omission():
    reasons = validate_extraction_contract({"crop": "Paddy"}, ["crop", "district"]).reasons
    assert any("field_omitted_instead_of_null" in r for r in reasons)


def test_structured_data_never_routed_to_the_model():
    r = Router()
    assert r.classify("prices.csv").needs_llm is False
    assert r.classify("mandi.html").needs_llm is False


def test_pdf_without_text_layer_goes_to_ocr_with_low_confidence():
    d = Router().classify("policy.pdf", text_layer_chars=12)
    assert d.modality is Modality.SCANNED_PDF_OCR
    assert d.confidence == "low"


def test_unroutable_input_raises_rather_than_guessing():
    try:
        Router().classify("mystery.bin")
    except ValueError:
        return
    raise AssertionError("unroutable input should raise")
