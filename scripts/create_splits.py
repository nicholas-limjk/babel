#!/usr/bin/env python3
"""
Create ABTM artificial limitation splits from a normalized verses.csv file.

Usage:
    python scripts/create_splits.py \
      --verses data/bible_dataset/processed/verses.csv \
      --out data/bible_dataset/splits
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path


NT_BOOKS = {
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH",
    "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB",
    "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
}

GOSPEL_BOOKS = {"MAT", "MRK", "LUK", "JHN"}


def write_split(out_dir: Path, name: str, seed_ids: list[str], eval_ids: list[str], description: str) -> None:
    payload = {
        "name": name,
        "description": description,
        "seed_verse_ids": sorted(seed_ids),
        "eval_verse_ids": sorted(eval_ids),
    }
    (out_dir / f"{name}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verses", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--random-seed", type=int, default=42)
    args = parser.parse_args()

    with args.verses.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    args.out.mkdir(parents=True, exist_ok=True)

    nt_ids = sorted({row["verse_id"] for row in rows if row.get("book") in NT_BOOKS and row.get("verse_id")})
    mark_ids = sorted({row["verse_id"] for row in rows if row.get("book") == "MRK" and row.get("verse_id")})
    gospel_ids = sorted({row["verse_id"] for row in rows if row.get("book") in GOSPEL_BOOKS and row.get("verse_id")})

    if not mark_ids:
        raise ValueError("No Mark verses found. Check book normalization.")

    write_split(
        args.out,
        "mark_only",
        mark_ids,
        sorted(set(nt_ids) - set(mark_ids)),
        "Only Mark is visible. Evaluate on the rest of the New Testament.",
    )

    random.seed(args.random_seed)
    for n in [50, 100, 250]:
        sample = sorted(random.sample(mark_ids, min(n, len(mark_ids))))
        write_split(
            args.out,
            f"seed_{n}_random_mark",
            sample,
            sorted(set(nt_ids) - set(sample)),
            f"{n} random verses from Mark are visible. Evaluate on the rest of the New Testament.",
        )

    write_split(
        args.out,
        "gospels_only",
        gospel_ids,
        sorted(set(nt_ids) - set(gospel_ids)),
        "The four Gospels are visible. Evaluate on Acts, Epistles, and Revelation.",
    )

    print(f"Wrote splits to {args.out.resolve()}")


if __name__ == "__main__":
    main()
