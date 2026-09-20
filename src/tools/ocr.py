"""Scanned documents, including Hindi.

Devanagari OCR is required, not optional: the Phase 2 gate tests at least one
non English document, and the procurement policy orders and Federation tendu
notices are the state's primary Hindi sources.

This is the weakest link in the pipeline. Everything from this path is written
with extraction_confidence = low, so that Phase 3 analysis can be re run
excluding it and the difference reported rather than assumed away.
"""

from __future__ import annotations

from src.tools.base import ExtractionUnit, ModalityTool, register


@register
class OcrTool(ModalityTool):
    name = "ocr"
    needs_llm = True

    def read(self, path: str, **kwargs) -> list[ExtractionUnit]:
        raise NotImplementedError("Phase 2 implementation.")
