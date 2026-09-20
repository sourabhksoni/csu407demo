"""Structured tabular and API data. No language model in the loop.

This is the deterministic path. Pagination, type coercion on dates and numbers,
and deduplication on the natural key. Sending an already structured numerical
table through a model would add cost, latency and hallucination risk in
exchange for nothing.
"""

from __future__ import annotations

from src.tools.base import ExtractionUnit, ModalityTool, register


@register
class ApiCsvTool(ModalityTool):
    name = "api_csv"
    needs_llm = False

    def read(self, path: str, **kwargs) -> list[ExtractionUnit]:
        raise NotImplementedError("Phase 2 implementation.")
