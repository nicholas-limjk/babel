"""Recurring phrase memory."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class PhraseEntry:
    english_phrase: str
    target_phrase: str
    source_verse_ids: str
    frequency: int
    confidence: float = 0.5
    scope: str = "seed"


class PhraseMemory:
    def __init__(self, entries: Optional[list[PhraseEntry]] = None) -> None:
        self.entries = entries or []

    @classmethod
    def from_parallel_seed(
        cls,
        english_rows: list[dict[str, object]],
        target_rows: list[dict[str, object]],
        min_frequency: int = 2,
    ) -> "PhraseMemory":
        target_by_id = {str(row["verse_id"]): str(row.get("text", "")) for row in target_rows}
        phrase_counts: Counter[str] = Counter()
        phrase_verses: dict[str, list[str]] = {}

        for row in english_rows:
            verse_id = str(row.get("verse_id", ""))
            if verse_id not in target_by_id:
                continue
            tokens = re.findall(r"[A-Za-z']+", str(row.get("text", "")).lower())
            for width in (3, 4, 5):
                for idx in range(0, max(0, len(tokens) - width + 1)):
                    phrase = " ".join(tokens[idx:idx + width])
                    phrase_counts[phrase] += 1
                    phrase_verses.setdefault(phrase, []).append(verse_id)

        entries = [
            PhraseEntry(
                english_phrase=phrase,
                target_phrase="",
                source_verse_ids=",".join(sorted(set(phrase_verses[phrase]))),
                frequency=count,
            )
            for phrase, count in phrase_counts.items()
            if count >= min_frequency
        ]
        entries.sort(key=lambda entry: (-entry.frequency, entry.english_phrase))
        return cls(entries)

    def relevant_to(self, source_text: str, limit: int = 12) -> list[PhraseEntry]:
        lower = source_text.lower()
        matches = [entry for entry in self.entries if entry.english_phrase in lower]
        return matches[:limit]
