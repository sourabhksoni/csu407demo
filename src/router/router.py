"""Router agent.

Classifies an incoming artifact by modality and dispatches it to a tool.

Governing principle, from docs/phase1/agent_tool_plan.md:
use deterministic tools wherever deterministic processing is sufficient, and
use the language model only where semantic interpretation is required.

That principle is implemented here as routing policy: api_csv and html_table
never reach the model, digital_pdf and scanned_pdf_ocr do. An already
structured numerical table gains nothing from a language model and pays for it
in cost, latency and hallucination risk.

Classification is by artifact properties, not by source identity. The Phase 2
gate supplies unseen documents, so a router keyed on a list of known sources
would fail exactly the test it needs to pass.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from enum import Enum


class Modality(str, Enum):
    API_CSV = "api_csv"
    HTML_TABLE = "html_table"
    DIGITAL_PDF = "digital_pdf"
    SCANNED_PDF_OCR = "scanned_pdf_ocr"
    VOICE_AUDIO = "voice_audio"


# Which modalities require the language model. Everything else is deterministic.
NEEDS_LLM: frozenset[Modality] = frozenset(
    {Modality.DIGITAL_PDF, Modality.SCANNED_PDF_OCR, Modality.VOICE_AUDIO}
)

# Raw call recordings route to Whisper based transcription before any field
# extraction can happen. Most Phase 1 voice sources, including the ICAR
# KCC-CHAKSHU archive, are distributed as already transcribed query and
# answer text and therefore arrive as .csv/.json and take the api_csv path
# instead. This branch exists for the case where raw recordings are obtained
# directly, for example a call centre audio export or a field interview.
AUDIO_SUFFIXES: frozenset[str] = frozenset({".mp3", ".wav", ".m4a", ".ogg", ".flac"})

# A PDF page with fewer than this many extractable characters is treated as an
# image and routed to OCR. Tuned in Phase 2 against real documents.
TEXT_LAYER_MIN_CHARS = 100


@dataclass
class RoutingDecision:
    modality: Modality
    tool: str
    needs_llm: bool
    reason: str
    confidence: str = "high"


class Router:
    def classify(self, path: str | pathlib.Path, text_layer_chars: int | None = None,
                 content_type: str | None = None) -> RoutingDecision:
        p = pathlib.Path(path)
        suffix = p.suffix.lower()

        if suffix in {".csv", ".tsv", ".json", ".xml"} or (
            content_type and "json" in content_type
        ):
            return RoutingDecision(
                Modality.API_CSV, "tools.api_csv", False,
                "Structured tabular or serialised data. Parsed deterministically, "
                "no model in the loop.")

        if suffix in {".html", ".htm"} or (content_type and "html" in content_type):
            return RoutingDecision(
                Modality.HTML_TABLE, "tools.html_table", False,
                "Markup with table structure. Parsed deterministically, escalated "
                "to the model only if parsing fails.")

        if suffix == ".pdf":
            if text_layer_chars is None:
                return RoutingDecision(
                    Modality.DIGITAL_PDF, "tools.pdf_text", True,
                    "PDF with unknown text layer. Probe the text layer before "
                    "committing to a path.", confidence="low")
            if text_layer_chars >= TEXT_LAYER_MIN_CHARS:
                return RoutingDecision(
                    Modality.DIGITAL_PDF, "tools.pdf_text", True,
                    f"PDF with a text layer ({text_layer_chars} chars). Layout aware "
                    "extraction, then model based field extraction.")
            return RoutingDecision(
                Modality.SCANNED_PDF_OCR, "tools.ocr", True,
                f"PDF with little or no text layer ({text_layer_chars} chars). "
                "OCR with Devanagari support, then model based extraction. "
                "Output carries low extraction confidence.", confidence="low")

        if suffix in {".xlsx", ".xls"}:
            return RoutingDecision(
                Modality.API_CSV, "tools.api_csv", False,
                "Spreadsheet. Read as a table, no model required.")

        if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            return RoutingDecision(
                Modality.SCANNED_PDF_OCR, "tools.ocr", True,
                "Raster document image. OCR path.", confidence="low")

        if suffix in AUDIO_SUFFIXES:
            return RoutingDecision(
                Modality.VOICE_AUDIO, "tools.audio_transcribe", True,
                "Raw call or voice recording. Whisper based transcription, "
                "then the same model based field extraction used for PDF "
                "text. Output carries low extraction confidence until the "
                "transcription step is validated against a manual sample.",
                confidence="low")

        raise ValueError(
            f"Unrecognised artifact type {suffix!r}. Unroutable inputs are "
            "quarantined rather than guessed at.")
