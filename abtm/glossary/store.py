"""Manual glossary loading and compliance helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GlossaryEntry:
    english_term: str
    target_term: str
    category: str = "other"
    locked: bool = False
    confidence: float = 1.0
    source_verse_ids: str = ""
    notes: str = ""


class GlossaryStore:
    def __init__(self, entries: Optional[list[GlossaryEntry]] = None) -> None:
        self.entries = entries or []

    @classmethod
    def from_csv(cls, path: Path) -> "GlossaryStore":
        if not path.exists():
            return cls()
        entries: list[GlossaryEntry] = []
        with path.open("r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                entries.append(
                    GlossaryEntry(
                        english_term=row.get("english_term", "").strip(),
                        target_term=row.get("target_term", "").strip(),
                        category=row.get("category", "other").strip() or "other",
                        locked=str(row.get("locked", "")).strip().lower() in {"1", "true", "yes"},
                        confidence=float(row.get("confidence", 1.0) or 1.0),
                        source_verse_ids=row.get("source_verse_ids", ""),
                        notes=row.get("notes", ""),
                    )
                )
        return cls([entry for entry in entries if entry.english_term and entry.target_term])

    def relevant_to(self, source_text: str) -> list[GlossaryEntry]:
        lower = source_text.lower()
        return [entry for entry in self.entries if entry.english_term.lower() in lower]

    def locked_entries(self) -> list[GlossaryEntry]:
        return [entry for entry in self.entries if entry.locked]
