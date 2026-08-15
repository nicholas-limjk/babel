"""In-memory translation memory for seed and generated verses."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class MemoryEntry:
    verse_id: str
    language: str
    version: str
    text: str
    quality_tier: str = "gold"
    source_type: str = "official"
    review_status: str = "seed"
    created_at: str = ""


class TranslationMemory:
    def __init__(self, entries: Optional[Iterable[MemoryEntry]] = None) -> None:
        self._entries: dict[str, MemoryEntry] = {}
        for entry in entries or []:
            self.insert(entry)

    def __len__(self) -> int:
        return len(self._entries)

    def insert(self, entry: MemoryEntry) -> None:
        created = entry.created_at or datetime.now(timezone.utc).isoformat()
        self._entries[entry.verse_id] = MemoryEntry(**{**entry.__dict__, "created_at": created})

    def add_generated(self, verse_id: str, language: str, version: str, text: str) -> None:
        self.insert(
            MemoryEntry(
                verse_id=verse_id,
                language=language,
                version=version,
                text=text,
                quality_tier="bronze",
                source_type="generated",
                review_status="needs_review",
            )
        )

    def get(self, verse_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(verse_id)

    def has(self, verse_id: str) -> bool:
        return verse_id in self._entries

    def examples_for(self, verse_ids: Iterable[str]) -> list[MemoryEntry]:
        return [self._entries[verse_id] for verse_id in verse_ids if verse_id in self._entries]

    def rows(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    @classmethod
    def from_rows(
        cls,
        rows: Iterable[dict[str, object]],
        seed_verse_ids: Iterable[str],
        language: str,
        version: str,
    ) -> "TranslationMemory":
        seed_set = set(seed_verse_ids)
        entries = []
        for row in rows:
            verse_id = str(row.get("verse_id", ""))
            if verse_id not in seed_set:
                continue
            if str(row.get("language", "")) != language or str(row.get("version", "")) != version:
                continue
            text = str(row.get("text", "")).strip()
            if text:
                entries.append(MemoryEntry(verse_id=verse_id, language=language, version=version, text=text))
        return cls(entries)

    def to_csv(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(MemoryEntry.__dataclass_fields__.keys()))
            writer.writeheader()
            for entry in self.rows():
                writer.writerow(entry.__dict__)
