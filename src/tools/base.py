"""Common interface for modality tools.

Adding a modality is a new module plus one registry entry, not a router
rewrite. That matters because the Phase 2 gate supplies unseen documents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionUnit:
    """One addressable chunk of a source, carrying its own provenance.

    page_number travels with the text from the moment it is read. Provenance
    reconstructed after the fact is provenance that cannot be trusted, and the
    Phase 3 gate asks which source and page a number came from.
    """
    text: str
    document_name: str
    document_url: str
    page_number: int | None = None
    language: str | None = None
    tables: list[Any] = field(default_factory=list)
    extraction_confidence: str = "high"


class ModalityTool(ABC):
    name: str = "base"
    needs_llm: bool = False

    @abstractmethod
    def read(self, path: str, **kwargs) -> list[ExtractionUnit]:
        """Return extraction units. Never returns partial text silently:
        a failure raises so the caller can quarantine it with a reason."""
        raise NotImplementedError


REGISTRY: dict[str, type[ModalityTool]] = {}


def register(cls: type[ModalityTool]) -> type[ModalityTool]:
    REGISTRY[cls.name] = cls
    return cls
