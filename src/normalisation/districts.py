"""District normalisation for Chhattisgarh.

Load bearing. Every extractor calls this before writing a row.

Two problems this solves:

1. Transliteration drift. The same district appears as Kawardha and Kabirdham,
   Korea and Koriya, Janjgir-Champa and Janjgir Champa, plus Devanagari spellings.
   Without canonicalisation the same district becomes several entities and every
   district level aggregate silently undercounts.

2. The 2022 reorganisation. Chhattisgarh created several new districts in 2022,
   carved out of existing ones. A dataset published before that reports a
   district set that no longer matches the current one. Joining across that
   boundary without an explicit predecessor mapping either drops rows or double
   counts them, and neither failure is visible in the output.

WARNING: district codes here are project internal, not official LGD codes, and
the predecessor mapping must be confirmed against the state gazette notifications
before any pre 2022 data is loaded. Treat it as a working table pending
verification, which is recorded as an open item in logs/progress_log.md.
"""

from __future__ import annotations

import csv
import pathlib
import unicodedata
from dataclasses import dataclass

_CSV = pathlib.Path(__file__).with_name("districts.csv")
REORGANISATION_YEAR = 2022


@dataclass(frozen=True)
class District:
    code: str
    name: str
    name_hi: str
    created_year: int
    predecessor_code: str | None


def _key(text: str) -> str:
    """Fold a district string to a comparison key.

    Strips accents, punctuation and spacing so that Janjgir-Champa,
    Janjgir Champa and JANJGIRCHAMPA all collapse to one key.
    """
    if text is None:
        return ""
    t = unicodedata.normalize("NFKC", str(text)).strip().casefold()
    return "".join(ch for ch in t if ch.isalnum())


class DistrictNormaliser:
    def __init__(self, csv_path: pathlib.Path = _CSV):
        self._by_code: dict[str, District] = {}
        self._lookup: dict[str, str] = {}

        with open(csv_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                pred = row["predecessor_district_code"].strip() or None
                d = District(
                    code=row["district_code"].strip(),
                    name=row["district_name"].strip(),
                    name_hi=row["district_name_hi"].strip(),
                    created_year=int(row["created_year"]),
                    predecessor_code=pred,
                )
                self._by_code[d.code] = d
                for variant in (d.code, d.name, d.name_hi,
                                *filter(None, row["aliases"].split(";"))):
                    k = _key(variant)
                    if k:
                        self._lookup[k] = d.code

    def __len__(self) -> int:
        return len(self._by_code)

    def resolve(self, raw: str) -> District | None:
        """Return the canonical district, or None if it cannot be resolved.

        Returning None is correct. The caller sends unresolved rows to
        quarantine rather than guessing, because a wrong district is worse
        than a rejected row.
        """
        return self._by_code.get(self._lookup.get(_key(raw), ""), None)

    def resolve_for_year(self, raw: str, data_year: int) -> District | None:
        """Resolve a district as reported in a dataset of a given year.

        A district created in 2022 cannot appear in 2019 data. If a caller
        asks for one anyway, the row is suspect and is not silently accepted.
        """
        d = self.resolve(raw)
        if d is None:
            return None
        if d.created_year > data_year:
            return None
        return d

    def map_to_current(self, raw: str) -> tuple[District | None, bool]:
        """Map a possibly historical district onto the current set.

        Returns (district, is_split_attribution). The flag is True when the
        source district was later split, meaning the value carries an
        attribution assumption and should be marked as such in analysis.
        """
        d = self.resolve(raw)
        if d is None:
            return None, False
        successors = [x for x in self._by_code.values() if x.predecessor_code == d.code]
        return d, bool(successors)

    def successors(self, code: str) -> list[District]:
        return [d for d in self._by_code.values() if d.predecessor_code == code]

    def created_after_reorganisation(self) -> list[District]:
        return [d for d in self._by_code.values()
                if d.created_year >= REORGANISATION_YEAR]


_default: DistrictNormaliser | None = None


def default() -> DistrictNormaliser:
    global _default
    if _default is None:
        _default = DistrictNormaliser()
    return _default
