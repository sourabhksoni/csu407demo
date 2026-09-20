"""HTML tables and portal listings.

Deterministic parse first. Selectors come from config/selectors.yaml so that a
portal redesign is a config edit rather than a code change. Escalated to the
model only when the deterministic parse fails, and that escalation is logged
so the rate is visible.

Scraping respects robots.txt and the rate limits in config/selectors.yaml, and
prefers an official bulk download wherever one exists.
"""

from __future__ import annotations

from src.tools.base import ExtractionUnit, ModalityTool, register


@register
class HtmlTableTool(ModalityTool):
    name = "html_table"
    needs_llm = False

    def read(self, path: str, **kwargs) -> list[ExtractionUnit]:
        raise NotImplementedError("Phase 2 implementation.")
