"""Run a first-pass ABTM bootstrap experiment.

This runner is intentionally conservative: it performs retrieval, prompt
construction, verification, and reference comparison, but uses a deterministic
nearest-memory placeholder instead of calling an LLM.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Optional

from abtm.evaluation import corpus_scores
from abtm.glossary import GlossaryStore
from abtm.memory import TranslationMemory
from abtm.phrase_memory import PhraseMemory
from abtm.prompting import PromptBuilder
from abtm.retrieval import TfidfEnglishRetriever
from abtm.verification import verify_translation


def read_csv_rows(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def choose_rows(rows: list[dict[str, object]], language: Optional[str], version: str) -> list[dict[str, object]]:
    chosen = [row for row in rows if str(row.get("version", "")).lower() == version.lower()]
    if language:
        chosen = [row for row in chosen if str(row.get("language", "")).lower() == language.lower()]
    return chosen


def generate_placeholder(examples: list[tuple[str, str, object]]) -> str:
    if not examples:
        return ""
    return examples[0][2].text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--source-version", required=True)
    parser.add_argument("--target-version", required=True)
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("runs/bootstrap"))
    parser.add_argument("--source-language", default=None)
    parser.add_argument("--target-language", default=None)
    parser.add_argument("--examples-k", type=int, default=8)
    parser.add_argument("--max-verses", type=int, default=0)
    parser.add_argument("--glossary", type=Path, default=None)
    args = parser.parse_args()

    rows = read_csv_rows(args.dataset)
    split = json.loads(args.split.read_text(encoding="utf-8"))

    source_rows = choose_rows(rows, args.source_language, args.source_version)
    target_rows = choose_rows(rows, args.target_language, args.target_version)
    source_by_id = {str(row["verse_id"]): row for row in source_rows}
    target_by_id = {str(row["verse_id"]): row for row in target_rows}

    memory = TranslationMemory.from_rows(
        target_rows,
        split["seed_verse_ids"],
        language=str(target_rows[0].get("language", args.target_language or "")) if target_rows else args.target_language or "",
        version=args.target_version,
    )
    retriever = TfidfEnglishRetriever(source_rows)
    glossary_store = GlossaryStore.from_csv(args.glossary) if args.glossary else GlossaryStore()
    phrase_memory = PhraseMemory.from_parallel_seed(
        [source_by_id[vid] for vid in split["seed_verse_ids"] if vid in source_by_id],
        [target_by_id[vid] for vid in split["seed_verse_ids"] if vid in target_by_id],
    )
    prompt_builder = PromptBuilder()

    eval_ids = [vid for vid in split["eval_verse_ids"] if vid in source_by_id and vid in target_by_id]
    if args.max_verses:
        eval_ids = eval_ids[:args.max_verses]

    args.out.mkdir(parents=True, exist_ok=True)
    detail_rows: list[dict[str, str]] = []
    for verse_id in eval_ids:
        source_text = str(source_by_id[verse_id].get("text", ""))
        retrieved = retriever.query(source_text, top_k=args.examples_k * 4, exclude_verse_ids={verse_id})
        example_triples = []
        for item in retrieved:
            entry = memory.get(item.verse_id)
            if entry:
                example_triples.append((item.verse_id, item.text, entry))
            if len(example_triples) >= args.examples_k:
                break
        relevant_glossary = glossary_store.relevant_to(source_text)
        prompt = prompt_builder.build(
            source_verse_id=verse_id,
            source_text=source_text,
            target_language=args.target_language or str(target_by_id[verse_id].get("language", "")),
            examples=example_triples,
            glossary=relevant_glossary,
            phrases=phrase_memory.relevant_to(source_text),
        )
        candidate = generate_placeholder(example_triples)
        verification = verify_translation(source_text, candidate, relevant_glossary)
        detail_rows.append(
            {
                "verse_id": verse_id,
                "source": source_text,
                "candidate": candidate,
                "reference": str(target_by_id[verse_id].get("text", "")),
                "prompt": prompt,
                "passed_verification": str(verification.passed),
                "issues": ",".join(verification.issues),
                "length_ratio": f"{verification.length_ratio:.4f}",
                "glossary_pass_rate": f"{verification.glossary_pass_rate:.4f}",
            }
        )

    detail_path = args.out / "outputs.csv"
    with detail_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(detail_rows[0].keys()) if detail_rows else ["verse_id"])
        writer.writeheader()
        writer.writerows(detail_rows)

    summary = {
        "dataset": str(args.dataset),
        "split": split["name"],
        "source_version": args.source_version,
        "target_version": args.target_version,
        "seed_memory_size": len(memory),
        "evaluated_verses": len(detail_rows),
        "metrics": corpus_scores(detail_rows),
        "outputs": str(detail_path),
    }
    (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
