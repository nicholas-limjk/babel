#!/usr/bin/env python3
"""
Pull and normalize open Bible translations from Midvash bible-data.

Usage:
    python scripts/pull_open_bibles.py --out data/bible_dataset --nt-only

Outputs:
    processed/verses.csv
    processed/verses.parquet
    processed/versions.csv
    reports/coverage_by_version.csv
    reports/nt_coverage_by_version.csv
    splits/*.json

Notes:
    This script uses the public/free Midvash bible-data repository:
    https://github.com/midvash/bible-data
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


MIDVASH_REPO = "https://github.com/midvash/bible-data.git"

BOOK_ORDER = [
    "GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT","1SA","2SA","1KI","2KI",
    "1CH","2CH","EZR","NEH","EST","JOB","PSA","PRO","ECC","SNG","ISA","JER",
    "LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP",
    "HAG","ZEC","MAL","MAT","MRK","LUK","JHN","ACT","ROM","1CO","2CO","GAL",
    "EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT","PHM","HEB","JAS","1PE",
    "2PE","1JN","2JN","3JN","JUD","REV"
]

NT_BOOKS = set(BOOK_ORDER[39:])
GOSPEL_BOOKS = {"MAT", "MRK", "LUK", "JHN"}

BOOK_MAP = {
    # Common OSIS / English names
    "Gen": "GEN", "Genesis": "GEN", "GEN": "GEN",
    "Exod": "EXO", "Exo": "EXO", "Exodus": "EXO", "EXO": "EXO",
    "Lev": "LEV", "Leviticus": "LEV", "LEV": "LEV",
    "Num": "NUM", "Numbers": "NUM", "NUM": "NUM",
    "Deut": "DEU", "Deu": "DEU", "Deuteronomy": "DEU", "DEU": "DEU",
    "Josh": "JOS", "Jos": "JOS", "Joshua": "JOS", "JOS": "JOS",
    "Judg": "JDG", "Jdg": "JDG", "Judges": "JDG", "JDG": "JDG",
    "Ruth": "RUT", "Rut": "RUT", "RUT": "RUT",
    "1Sam": "1SA", "1 Samuel": "1SA", "1SA": "1SA",
    "2Sam": "2SA", "2 Samuel": "2SA", "2SA": "2SA",
    "1Kgs": "1KI", "1Kings": "1KI", "1 Kings": "1KI", "1KI": "1KI",
    "2Kgs": "2KI", "2Kings": "2KI", "2 Kings": "2KI", "2KI": "2KI",
    "1Chr": "1CH", "1 Chronicles": "1CH", "1CH": "1CH",
    "2Chr": "2CH", "2 Chronicles": "2CH", "2CH": "2CH",
    "Ezra": "EZR", "Ezr": "EZR", "EZR": "EZR",
    "Neh": "NEH", "Nehemiah": "NEH", "NEH": "NEH",
    "Esth": "EST", "Est": "EST", "Esther": "EST", "EST": "EST",
    "Job": "JOB", "JOB": "JOB",
    "Ps": "PSA", "Psa": "PSA", "Psalms": "PSA", "Psalm": "PSA", "PSA": "PSA",
    "Prov": "PRO", "Pro": "PRO", "Proverbs": "PRO", "PRO": "PRO",
    "Eccl": "ECC", "Ecc": "ECC", "Ecclesiastes": "ECC", "ECC": "ECC",
    "Song": "SNG", "Song of Songs": "SNG", "Cant": "SNG", "SNG": "SNG",
    "Isa": "ISA", "Isaiah": "ISA", "ISA": "ISA",
    "Jer": "JER", "Jeremiah": "JER", "JER": "JER",
    "Lam": "LAM", "Lamentations": "LAM", "LAM": "LAM",
    "Ezek": "EZK", "Eze": "EZK", "Ezekiel": "EZK", "EZK": "EZK",
    "Dan": "DAN", "Daniel": "DAN", "DAN": "DAN",
    "Hos": "HOS", "Hosea": "HOS", "HOS": "HOS",
    "Joel": "JOL", "Joe": "JOL", "JOL": "JOL",
    "Amos": "AMO", "Amo": "AMO", "AMO": "AMO",
    "Obad": "OBA", "Oba": "OBA", "Obadiah": "OBA", "OBA": "OBA",
    "Jonah": "JON", "Jon": "JON", "JON": "JON",
    "Mic": "MIC", "Micah": "MIC", "MIC": "MIC",
    "Nah": "NAM", "Nahum": "NAM", "NAM": "NAM",
    "Hab": "HAB", "Habakkuk": "HAB", "HAB": "HAB",
    "Zeph": "ZEP", "Zep": "ZEP", "Zephaniah": "ZEP", "ZEP": "ZEP",
    "Hag": "HAG", "Haggai": "HAG", "HAG": "HAG",
    "Zech": "ZEC", "Zec": "ZEC", "Zechariah": "ZEC", "ZEC": "ZEC",
    "Mal": "MAL", "Malachi": "MAL", "MAL": "MAL",
    "Matt": "MAT", "Mat": "MAT", "Matthew": "MAT", "MAT": "MAT",
    "Mark": "MRK", "Mrk": "MRK", "Mar": "MRK", "MRK": "MRK",
    "Luke": "LUK", "Luk": "LUK", "LUK": "LUK",
    "John": "JHN", "Jhn": "JHN", "Joh": "JHN", "JHN": "JHN",
    "Acts": "ACT", "Act": "ACT", "ACT": "ACT",
    "Rom": "ROM", "Romans": "ROM", "ROM": "ROM",
    "1Cor": "1CO", "1 Corinthians": "1CO", "1CO": "1CO",
    "2Cor": "2CO", "2 Corinthians": "2CO", "2CO": "2CO",
    "Gal": "GAL", "Galatians": "GAL", "GAL": "GAL",
    "Eph": "EPH", "Ephesians": "EPH", "EPH": "EPH",
    "Phil": "PHP", "Php": "PHP", "Philippians": "PHP", "PHP": "PHP",
    "Col": "COL", "Colossians": "COL", "COL": "COL",
    "1Thess": "1TH", "1 Thessalonians": "1TH", "1TH": "1TH",
    "2Thess": "2TH", "2 Thessalonians": "2TH", "2TH": "2TH",
    "1Tim": "1TI", "1 Timothy": "1TI", "1TI": "1TI",
    "2Tim": "2TI", "2 Timothy": "2TI", "2TI": "2TI",
    "Titus": "TIT", "Tit": "TIT", "TIT": "TIT",
    "Phlm": "PHM", "Philemon": "PHM", "PHM": "PHM",
    "Heb": "HEB", "Hebrews": "HEB", "HEB": "HEB",
    "Jas": "JAS", "James": "JAS", "JAS": "JAS",
    "1Pet": "1PE", "1 Peter": "1PE", "1PE": "1PE",
    "2Pet": "2PE", "2 Peter": "2PE", "2PE": "2PE",
    "1John": "1JN", "1 John": "1JN", "1JN": "1JN",
    "2John": "2JN", "2 John": "2JN", "2JN": "2JN",
    "3John": "3JN", "3 John": "3JN", "3JN": "3JN",
    "Jude": "JUD", "Jud": "JUD", "JUD": "JUD",
    "Rev": "REV", "Revelation": "REV", "Apoc": "REV", "REV": "REV",
}


@dataclass
class VerseRow:
    verse_id: str
    book: str
    chapter: int
    verse: int
    language: str
    version: str
    text: str
    source: str
    license: str
    testament: str
    raw_book: str
    raw_path: str


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def clone_repo(raw_dir: Path, force: bool) -> Path:
    repo_dir = raw_dir / "bible-data"
    if repo_dir.exists() and force:
        shutil.rmtree(repo_dir)
    if not repo_dir.exists():
        raw_dir.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", MIDVASH_REPO, str(repo_dir)])
    return repo_dir


def norm_book(raw: str) -> Optional[str]:
    if raw is None:
        return None
    s = str(raw).strip()
    if s in BOOK_MAP:
        return BOOK_MAP[s]
    s2 = s.replace("_", " ").replace("-", " ")
    if s2 in BOOK_MAP:
        return BOOK_MAP[s2]
    s3 = s2.replace(" ", "")
    return BOOK_MAP.get(s3)


def make_verse_id(book: str, chapter: int, verse: int) -> str:
    return f"{book}_{chapter:03d}_{verse:03d}"


def infer_language_version(path: Path, repo_dir: Path) -> tuple[str, str]:
    rel = path.relative_to(repo_dir)
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "versions":
        return parts[1], parts[2]
    return "unknown", path.parent.name


def read_metadata(version_dir: Path) -> dict[str, Any]:
    for name in ["metadata.json", "meta.json"]:
        p = version_dir / name
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


def add_row(
    rows: list[VerseRow],
    raw_book: str,
    chapter: int,
    verse_num: int,
    text: str,
    language: str,
    version: str,
    license_name: str,
    path: Path,
    repo_dir: Path,
) -> None:
    book = norm_book(raw_book)
    if not book:
        return
    text = str(text or "").strip()
    if not text:
        return
    rows.append(
        VerseRow(
            verse_id=make_verse_id(book, int(chapter), int(verse_num)),
            book=book,
            chapter=int(chapter),
            verse=int(verse_num),
            language=language,
            version=version,
            text=text,
            source="midvash/bible-data",
            license=license_name,
            testament="NT" if book in NT_BOOKS else "OT",
            raw_book=str(raw_book),
            raw_path=str(path.relative_to(repo_dir)),
        )
    )


def parse_json_file(path: Path, repo_dir: Path) -> list[VerseRow]:
    language, version = infer_language_version(path, repo_dir)
    metadata = read_metadata(path.parent)
    license_name = str(metadata.get("license", metadata.get("license_name", "unknown")))
    rows: list[VerseRow] = []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return rows

    # Per-book JSON: list[chapter][verse]
    if isinstance(data, list) and data and all(isinstance(ch, list) for ch in data):
        raw_book = path.stem
        if norm_book(raw_book):
            for c_idx, chapter in enumerate(data, start=1):
                if isinstance(chapter, list):
                    for v_idx, text in enumerate(chapter, start=1):
                        add_row(rows, raw_book, c_idx, v_idx, text, language, version, license_name, path, repo_dir)
            return rows

    # Whole Bible JSON: list[book][chapter][verse]
    if path.name.lower() in {"bible.json", "full.json"} and isinstance(data, list):
        for b_idx, book_data in enumerate(data):
            if b_idx >= len(BOOK_ORDER):
                break
            raw_book = BOOK_ORDER[b_idx]
            if isinstance(book_data, list):
                for c_idx, chapter in enumerate(book_data, start=1):
                    if isinstance(chapter, list):
                        for v_idx, text in enumerate(chapter, start=1):
                            add_row(rows, raw_book, c_idx, v_idx, text, language, version, license_name, path, repo_dir)
        return rows

    # Dict/list-of-dicts layout.
    items = None
    if isinstance(data, dict):
        if isinstance(data.get("verses"), list):
            items = data["verses"]
        elif isinstance(data.get("data"), list):
            items = data["data"]
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        items = data

    if items:
        for item in items:
            raw_book = item.get("book") or item.get("book_id") or item.get("osis") or item.get("book_name")
            chapter = item.get("chapter") or item.get("chapter_number")
            verse_num = item.get("verse") or item.get("number") or item.get("verse_number")
            text = item.get("text") or item.get("content")
            try:
                add_row(rows, raw_book, int(chapter), int(verse_num), text, language, version, license_name, path, repo_dir)
            except Exception:
                continue

    return rows


def parse_sqlite_file(path: Path, repo_dir: Path) -> list[VerseRow]:
    language, version = infer_language_version(path, repo_dir)
    metadata = read_metadata(path.parent)
    license_name = str(metadata.get("license", metadata.get("license_name", "unknown")))
    rows: list[VerseRow] = []

    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        if "verses" not in tables:
            return rows
        cols = [r[1] for r in cur.execute("PRAGMA table_info(verses)")]
        colset = set(cols)

        book_col = "book" if "book" in colset else "book_id" if "book_id" in colset else "osis" if "osis" in colset else None
        chapter_col = "chapter" if "chapter" in colset else "chapter_number" if "chapter_number" in colset else None
        verse_col = "number" if "number" in colset else "verse" if "verse" in colset else "verse_number" if "verse_number" in colset else None
        text_col = "text" if "text" in colset else "content" if "content" in colset else None

        if not all([book_col, chapter_col, verse_col, text_col]):
            return rows

        query = f"SELECT {book_col}, {chapter_col}, {verse_col}, {text_col} FROM verses"
        for raw_book, chapter, verse_num, text in cur.execute(query):
            if isinstance(raw_book, int):
                idx = int(raw_book) - 1
                raw_book = BOOK_ORDER[idx] if 0 <= idx < len(BOOK_ORDER) else str(raw_book)
            add_row(rows, str(raw_book), int(chapter), int(verse_num), text, language, version, license_name, path, repo_dir)

    except Exception as e:
        print(f"Warning: failed to parse SQLite {path}: {e}", file=sys.stderr)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return rows


def discover_and_parse(repo_dir: Path) -> list[VerseRow]:
    rows: list[VerseRow] = []

    json_files = [
        p for p in repo_dir.rglob("*.json")
        if p.name.lower() not in {"metadata.json", "meta.json", "package.json"}
    ]
    sqlite_files = list(repo_dir.rglob("*.sqlite")) + list(repo_dir.rglob("*.db"))

    for path in json_files:
        parsed = parse_json_file(path, repo_dir)
        if parsed:
            print(f"Parsed JSON {path.relative_to(repo_dir)}: {len(parsed)}")
            rows.extend(parsed)

    for path in sqlite_files:
        parsed = parse_sqlite_file(path, repo_dir)
        if parsed:
            print(f"Parsed SQLite {path.relative_to(repo_dir)}: {len(parsed)}")
            rows.extend(parsed)

    if not rows:
        raise RuntimeError("No verse rows parsed. Check source repo layout.")

    seen: set[tuple[str, str, str, str]] = set()
    deduped: list[VerseRow] = []
    for row in rows:
        key = (row.verse_id, row.language, row.version, row.text)
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def write_splits(rows: list[VerseRow], out_dir: Path) -> None:
    splits_dir = out_dir / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)

    nt_ids = sorted({row.verse_id for row in rows if row.book in NT_BOOKS})
    mark_ids = sorted({row.verse_id for row in rows if row.book == "MRK"})
    gospel_ids = sorted({row.verse_id for row in rows if row.book in GOSPEL_BOOKS})

    def write(name: str, seed: list[str], eval_ids: list[str], desc: str) -> None:
        payload = {"name": name, "description": desc, "seed_verse_ids": sorted(seed), "eval_verse_ids": sorted(eval_ids)}
        (splits_dir / f"{name}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    write("mark_only", mark_ids, sorted(set(nt_ids) - set(mark_ids)), "Only Mark is visible. Evaluate on rest of NT.")

    random.seed(42)
    for n in [50, 100, 250]:
        sample = sorted(random.sample(mark_ids, min(n, len(mark_ids))))
        write(f"seed_{n}_random_mark", sample, sorted(set(nt_ids) - set(sample)), f"{n} random Mark verses visible.")

    write("gospels_only", gospel_ids, sorted(set(nt_ids) - set(gospel_ids)), "Gospels visible. Evaluate on Acts, Epistles, Revelation.")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_optional_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except Exception as e:
        print(f"Warning: could not write parquet: {e}", file=sys.stderr)
        return
    if not rows:
        return
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)


def write_outputs(rows: list[VerseRow], out_dir: Path) -> None:
    processed = out_dir / "processed"
    reports = out_dir / "reports"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    row_dicts = [row.__dict__ for row in rows]
    fieldnames = list(VerseRow.__dataclass_fields__.keys())
    write_csv(processed / "verses.csv", row_dicts, fieldnames)
    write_optional_parquet(processed / "verses.parquet", row_dicts)

    version_counts: dict[tuple[str, str, str, str], set[str]] = {}
    coverage_counts: dict[tuple[str, str, str], set[str]] = {}
    for row in rows:
        version_counts.setdefault((row.language, row.version, row.source, row.license), set()).add(row.verse_id)
        coverage_counts.setdefault((row.language, row.version, row.book), set()).add(row.verse_id)

    versions = [
        {
            "language": language,
            "version": version,
            "source": source,
            "license": license_name,
            "total_verses": len(verse_ids),
        }
        for (language, version, source, license_name), verse_ids in sorted(version_counts.items())
    ]
    write_csv(processed / "versions.csv", versions, ["language", "version", "source", "license", "total_verses"])

    coverage = [
        {
            "language": language,
            "version": version,
            "book": book,
            "verse_count": len(verse_ids),
        }
        for (language, version, book), verse_ids in sorted(coverage_counts.items())
    ]
    write_csv(reports / "coverage_by_version.csv", coverage, ["language", "version", "book", "verse_count"])
    nt_coverage = [row for row in coverage if row["book"] in NT_BOOKS]
    write_csv(reports / "nt_coverage_by_version.csv", nt_coverage, ["language", "version", "book", "verse_count"])

    write_splits(rows, out_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/bible_dataset"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--nt-only", action="store_true")
    args = parser.parse_args()

    repo_dir = clone_repo(args.out / "raw", args.force)
    rows = discover_and_parse(repo_dir)

    if args.nt_only:
        rows = [row for row in rows if row.testament == "NT"]

    write_outputs(rows, args.out)

    print("\nDone.")
    print(f"Rows: {len(rows):,}")
    print(f"Versions: {len({(row.language, row.version) for row in rows}):,}")
    print(f"Output: {args.out.resolve()}")


if __name__ == "__main__":
    main()
