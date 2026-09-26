"""Commodity and unit normalisation.

The same commodity appears as Rice, RICE, Paddy, paddy and धान across our
sources, and market sources may use a trade grade instead of a crop name.
Without a canonical row plus an alias list the crop splits into several
entities and every aggregate undercounts.

Units are the second half of the problem. Procurement volumes are published in
metric tonnes, prices per quintal, and minor forest produce per standard bag.
The conversion factor is stored rather than applied at extraction time, so the
original figure stays auditable against the source document.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

QUINTAL_KG = 100.0


@dataclass(frozen=True)
class Commodity:
    key: str
    name: str
    name_hi: str
    group: str
    reporting_unit: str
    aliases: tuple[str, ...] = field(default=())
    procurement_floor: bool = False   # does the state buy it at a declared rate


# Phase 1 frozen scope. The pulse is deliberately a commodity with NO
# procurement floor: it is the control case. Without it every commodity in
# the study has an administered price and the central comparison has no baseline.
COMMODITIES: tuple[Commodity, ...] = (
    Commodity("paddy", "Paddy", "धान", "cereal", "quintal",
              ("rice", "dhan", "paddy common", "paddy grade a", "धान", "चावल"),
              procurement_floor=True),
    Commodity("maize", "Maize", "मक्का", "cereal", "quintal",
              ("makka", "corn", "मक्का"),
              procurement_floor=True),
    Commodity("chana", "Chana", "चना", "pulse", "quintal",
              ("gram", "bengal gram", "chick pea", "chickpea", "चना"),
              procurement_floor=False),
    Commodity("tendu", "Tendu Leaf", "तेंदूपत्ता", "minor_forest_produce", "standard_bag",
              ("tendu patta", "tendu leaves", "kendu leaf", "तेंदू", "तेंदूपत्ता"),
              procurement_floor=True),
)

# Unit conversions to the canonical unit (quintal) where a conversion exists.
# A standard bag of tendu leaves is 1000 bundles of 50 leaves and is a count,
# not a mass, so it has no mass conversion. Storing None is correct; inventing
# a factor would silently corrupt every tendu aggregate.
UNIT_TO_QUINTAL: dict[str, float | None] = {
    "quintal": 1.0,
    "qtl": 1.0,
    "metric_tonne": 10.0,
    "tonne": 10.0,
    "mt": 10.0,
    "kg": 1.0 / QUINTAL_KG,
    "lakh_tonne": 1_000_000.0,
    "standard_bag": None,
}


def _key(text: str) -> str:
    if text is None:
        return ""
    t = unicodedata.normalize("NFKC", str(text)).strip().casefold()
    return " ".join(t.split())


_LOOKUP: dict[str, Commodity] = {}
for _c in COMMODITIES:
    for _v in (_c.key, _c.name, _c.name_hi, *_c.aliases):
        _LOOKUP[_key(_v)] = _c


def resolve(raw: str) -> Commodity | None:
    """Canonical commodity, or None. None sends the row to quarantine."""
    return _LOOKUP.get(_key(raw))


def in_scope(raw: str) -> bool:
    return resolve(raw) is not None


def to_quintal(value: float, unit: str) -> float | None:
    """Convert to quintals. Returns None where no conversion exists, which
    the caller must handle rather than defaulting to the raw number."""
    factor = UNIT_TO_QUINTAL.get(_key(unit).replace(" ", "_"))
    if factor is None:
        return None
    return value * factor


def control_commodities() -> list[Commodity]:
    """Commodities with no administered price. These are what make the
    procurement comparison interpretable."""
    return [c for c in COMMODITIES if not c.procurement_floor]
