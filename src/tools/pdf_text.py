"""PDF documents that carry a text layer.

Text and table structure are pulled per page, and the page number travels with
every unit so provenance is never reconstructed afterwards. The model is then
asked to map the text onto schema fields, which is genuine semantic work: the
figure has to be associated with the entity it describes rather than read off
a grid.
"""

from __future__ import annotations

from src.tools.base import ExtractionUnit, ModalityTool, register


@register
class PdfTextTool(ModalityTool):
    name = "pdf_text"
    needs_llm = True

    def read(self, path: str, **kwargs) -> list[ExtractionUnit]:
        raise NotImplementedError("Phase 2 implementation.")
