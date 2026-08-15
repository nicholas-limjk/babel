"""Lightweight verifier checks for generated translations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from abtm.glossary import GlossaryEntry


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    issues: list[str]
    length_ratio: float
    glossary_pass_rate: float


def length_ratio(source_text: str, candidate_text: str) -> float:
    source_len = max(1, len(source_text.split()))
    return len(candidate_text.split()) / source_len


def glossary_pass_rate(candidate_text: str, entries: list[GlossaryEntry]) -> float:
    locked = [entry for entry in entries if entry.locked]
    if not locked:
        return 1.0
    lower = candidate_text.lower()
    passed = sum(1 for entry in locked if entry.target_term.lower() in lower)
    return passed / len(locked)


def verify_translation(source_text: str, candidate_text: str, glossary: Optional[list[GlossaryEntry]] = None) -> VerificationResult:
    issues: list[str] = []
    if not candidate_text.strip():
        issues.append("empty_output")
    ratio = length_ratio(source_text, candidate_text)
    if ratio < 0.35:
        issues.append("length_too_short")
    if ratio > 2.75:
        issues.append("length_too_long")
    pass_rate = glossary_pass_rate(candidate_text, glossary or [])
    if pass_rate < 1.0:
        issues.append("locked_glossary_missing")
    return VerificationResult(passed=not issues, issues=issues, length_ratio=ratio, glossary_pass_rate=pass_rate)
