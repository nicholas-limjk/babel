"""Canonical verse metadata used across ABTM.

The canonical ID format is ``BOOK_001_001`` where ``BOOK`` is a three-character
or OSIS-style Bible book code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


BOOK_ORDER = [
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA",
    "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO",
    "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOL", "AMO",
    "OBA", "JON", "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL", "MAT",
    "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH", "PHP",
    "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS", "1PE",
    "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
]

NT_BOOKS = set(BOOK_ORDER[39:])
GOSPEL_BOOKS = {"MAT", "MRK", "LUK", "JHN"}

BOOK_MAP = {
    "Genesis": "GEN", "Gen": "GEN", "GEN": "GEN",
    "Exodus": "EXO", "Exod": "EXO", "Exo": "EXO", "EXO": "EXO",
    "Leviticus": "LEV", "Lev": "LEV", "LEV": "LEV",
    "Numbers": "NUM", "Num": "NUM", "NUM": "NUM",
    "Deuteronomy": "DEU", "Deut": "DEU", "Deu": "DEU", "DEU": "DEU",
    "Joshua": "JOS", "Josh": "JOS", "Jos": "JOS", "JOS": "JOS",
    "Judges": "JDG", "Judg": "JDG", "Jdg": "JDG", "JDG": "JDG",
    "Ruth": "RUT", "Rut": "RUT", "RUT": "RUT",
    "1 Samuel": "1SA", "1Sam": "1SA", "1SA": "1SA",
    "2 Samuel": "2SA", "2Sam": "2SA", "2SA": "2SA",
    "1 Kings": "1KI", "1Kings": "1KI", "1Kgs": "1KI", "1KI": "1KI",
    "2 Kings": "2KI", "2Kings": "2KI", "2Kgs": "2KI", "2KI": "2KI",
    "1 Chronicles": "1CH", "1Chr": "1CH", "1CH": "1CH",
    "2 Chronicles": "2CH", "2Chr": "2CH", "2CH": "2CH",
    "Ezra": "EZR", "Ezr": "EZR", "EZR": "EZR",
    "Nehemiah": "NEH", "Neh": "NEH", "NEH": "NEH",
    "Esther": "EST", "Esth": "EST", "Est": "EST", "EST": "EST",
    "Job": "JOB", "JOB": "JOB",
    "Psalms": "PSA", "Psalm": "PSA", "Psa": "PSA", "Ps": "PSA", "PSA": "PSA",
    "Proverbs": "PRO", "Prov": "PRO", "Pro": "PRO", "PRO": "PRO",
    "Ecclesiastes": "ECC", "Eccl": "ECC", "Ecc": "ECC", "ECC": "ECC",
    "Song of Songs": "SNG", "Song": "SNG", "Cant": "SNG", "SNG": "SNG",
    "Isaiah": "ISA", "Isa": "ISA", "ISA": "ISA",
    "Jeremiah": "JER", "Jer": "JER", "JER": "JER",
    "Lamentations": "LAM", "Lam": "LAM", "LAM": "LAM",
    "Ezekiel": "EZK", "Ezek": "EZK", "Eze": "EZK", "EZK": "EZK",
    "Daniel": "DAN", "Dan": "DAN", "DAN": "DAN",
    "Hosea": "HOS", "Hos": "HOS", "HOS": "HOS",
    "Joel": "JOL", "Joe": "JOL", "JOL": "JOL",
    "Amos": "AMO", "Amo": "AMO", "AMO": "AMO",
    "Obadiah": "OBA", "Obad": "OBA", "Oba": "OBA", "OBA": "OBA",
    "Jonah": "JON", "Jon": "JON", "JON": "JON",
    "Micah": "MIC", "Mic": "MIC", "MIC": "MIC",
    "Nahum": "NAM", "Nah": "NAM", "NAM": "NAM",
    "Habakkuk": "HAB", "Hab": "HAB", "HAB": "HAB",
    "Zephaniah": "ZEP", "Zeph": "ZEP", "Zep": "ZEP", "ZEP": "ZEP",
    "Haggai": "HAG", "Hag": "HAG", "HAG": "HAG",
    "Zechariah": "ZEC", "Zech": "ZEC", "Zec": "ZEC", "ZEC": "ZEC",
    "Malachi": "MAL", "Mal": "MAL", "MAL": "MAL",
    "Matthew": "MAT", "Matt": "MAT", "Mat": "MAT", "MAT": "MAT",
    "Mark": "MRK", "Mrk": "MRK", "Mar": "MRK", "MRK": "MRK",
    "Luke": "LUK", "Luk": "LUK", "LUK": "LUK",
    "John": "JHN", "Jhn": "JHN", "Joh": "JHN", "JHN": "JHN",
    "Acts": "ACT", "Act": "ACT", "ACT": "ACT",
    "Romans": "ROM", "Rom": "ROM", "ROM": "ROM",
    "1 Corinthians": "1CO", "1Cor": "1CO", "1CO": "1CO",
    "2 Corinthians": "2CO", "2Cor": "2CO", "2CO": "2CO",
    "Galatians": "GAL", "Gal": "GAL", "GAL": "GAL",
    "Ephesians": "EPH", "Eph": "EPH", "EPH": "EPH",
    "Philippians": "PHP", "Phil": "PHP", "Php": "PHP", "PHP": "PHP",
    "Colossians": "COL", "Col": "COL", "COL": "COL",
    "1 Thessalonians": "1TH", "1Thess": "1TH", "1TH": "1TH",
    "2 Thessalonians": "2TH", "2Thess": "2TH", "2TH": "2TH",
    "1 Timothy": "1TI", "1Tim": "1TI", "1TI": "1TI",
    "2 Timothy": "2TI", "2Tim": "2TI", "2TI": "2TI",
    "Titus": "TIT", "Tit": "TIT", "TIT": "TIT",
    "Philemon": "PHM", "Phlm": "PHM", "PHM": "PHM",
    "Hebrews": "HEB", "Heb": "HEB", "HEB": "HEB",
    "James": "JAS", "Jas": "JAS", "JAS": "JAS",
    "1 Peter": "1PE", "1Pet": "1PE", "1PE": "1PE",
    "2 Peter": "2PE", "2Pet": "2PE", "2PE": "2PE",
    "1 John": "1JN", "1John": "1JN", "1JN": "1JN",
    "2 John": "2JN", "2John": "2JN", "2JN": "2JN",
    "3 John": "3JN", "3John": "3JN", "3JN": "3JN",
    "Jude": "JUD", "Jud": "JUD", "JUD": "JUD",
    "Revelation": "REV", "Rev": "REV", "Apoc": "REV", "REV": "REV",
}


@dataclass(frozen=True, order=True)
class VerseRef:
    book: str
    chapter: int
    verse: int

    @property
    def verse_id(self) -> str:
        return make_verse_id(self.book, self.chapter, self.verse)


def norm_book(raw: object) -> Optional[str]:
    if raw is None:
        return None
    value = str(raw).strip()
    if value in BOOK_MAP:
        return BOOK_MAP[value]
    spaced = value.replace("_", " ").replace("-", " ")
    if spaced in BOOK_MAP:
        return BOOK_MAP[spaced]
    compact = spaced.replace(" ", "")
    return BOOK_MAP.get(compact)


def make_verse_id(book: str, chapter: int, verse: int) -> str:
    canonical_book = norm_book(book) or book
    if canonical_book not in BOOK_ORDER:
        raise ValueError(f"Unknown Bible book: {book!r}")
    if int(chapter) < 1 or int(verse) < 1:
        raise ValueError("chapter and verse must be positive integers")
    return f"{canonical_book}_{int(chapter):03d}_{int(verse):03d}"


def parse_verse_id(verse_id: str) -> VerseRef:
    parts = str(verse_id).split("_")
    if len(parts) != 3:
        raise ValueError(f"Invalid verse_id: {verse_id!r}")
    book = norm_book(parts[0])
    if not book:
        raise ValueError(f"Invalid Bible book in verse_id: {verse_id!r}")
    try:
        chapter = int(parts[1])
        verse = int(parts[2])
    except ValueError as exc:
        raise ValueError(f"Invalid chapter or verse in verse_id: {verse_id!r}") from exc
    return VerseRef(book, chapter, verse)


def verse_sort_key(verse_id: str) -> tuple[int, int, int]:
    ref = parse_verse_id(verse_id)
    return (BOOK_ORDER.index(ref.book), ref.chapter, ref.verse)
