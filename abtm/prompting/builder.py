"""Structured translation prompt builder."""

from __future__ import annotations

from typing import Optional

from abtm.glossary import GlossaryEntry
from abtm.memory import MemoryEntry
from abtm.phrase_memory import PhraseEntry


class PromptBuilder:
    def build(
        self,
        source_verse_id: str,
        source_text: str,
        target_language: str,
        examples: list[tuple[str, str, MemoryEntry]],
        glossary: Optional[list[GlossaryEntry]] = None,
        phrases: Optional[list[PhraseEntry]] = None,
        style_profile: Optional[str] = None,
    ) -> str:
        lines = [
            "You are translating Scripture verse by verse.",
            f"Target language: {target_language}",
            "Return only the translated target verse. Do not add commentary.",
            "Preserve meaning, names, clauses, and verse-level formatting.",
        ]
        if style_profile:
            lines.extend(["", "Style profile:", style_profile])
        if glossary:
            lines.append("")
            lines.append("Locked glossary and terminology:")
            for entry in glossary:
                lock = "locked" if entry.locked else "suggested"
                lines.append(f"- {entry.english_term} => {entry.target_term} ({lock})")
        if phrases:
            lines.append("")
            lines.append("Recurring phrase memory:")
            for phrase in phrases:
                if phrase.target_phrase:
                    lines.append(f"- {phrase.english_phrase} => {phrase.target_phrase}")
                else:
                    lines.append(f"- {phrase.english_phrase}")
        if examples:
            lines.append("")
            lines.append("Examples:")
            for verse_id, english_text, target_entry in examples:
                lines.append(f"[{verse_id}] English: {english_text}")
                lines.append(f"[{verse_id}] Target: {target_entry.text}")
        lines.extend(["", f"Translate [{source_verse_id}]:", source_text])
        return "\n".join(lines)
