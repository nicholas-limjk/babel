"""English verse retrieval.

This backend intentionally uses TF-IDF by default so the MVP can run without
downloading embedding models. A sentence-transformer retriever can be added
behind the same interface later.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Optional


@dataclass(frozen=True)
class RetrievedVerse:
    verse_id: str
    text: str
    score: float


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


class TfidfEnglishRetriever:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = [row for row in rows if str(row.get("text", "")).strip()]
        self._build()

    def _build(self) -> None:
        self._doc_tokens = [_tokens(str(row.get("text", ""))) for row in self.rows]
        document_count = max(1, len(self._doc_tokens))
        document_frequency: dict[str, int] = {}
        for toks in self._doc_tokens:
            for token in set(toks):
                document_frequency[token] = document_frequency.get(token, 0) + 1
        self._idf = {
            token: math.log((1 + document_count) / (1 + freq)) + 1.0
            for token, freq in document_frequency.items()
        }
        self._vectors = [self._vectorize_tokens(toks) for toks in self._doc_tokens]

    def _vectorize_tokens(self, toks: list[str]) -> dict[str, float]:
        counts: dict[str, int] = {}
        for token in toks:
            counts[token] = counts.get(token, 0) + 1
        return {token: count * self._idf.get(token, 1.0) for token, count in counts.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(value * right.get(token, 0.0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        return dot / (left_norm * right_norm)

    def query(self, source_text: str, top_k: int = 8, exclude_verse_ids: Optional[set[str]] = None) -> list[RetrievedVerse]:
        exclude = exclude_verse_ids or set()
        query_vec = self._vectorize_tokens(_tokens(source_text))
        scored: list[RetrievedVerse] = []
        for row, vec in zip(self.rows, self._vectors):
            verse_id = str(row.get("verse_id", ""))
            if verse_id in exclude:
                continue
            score = self._cosine(query_vec, vec)
            if score > 0.0:
                scored.append(RetrievedVerse(verse_id=verse_id, text=str(row.get("text", "")), score=score))
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
