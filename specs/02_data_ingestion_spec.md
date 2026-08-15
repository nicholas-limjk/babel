# Open Bible Dataset Ingestion Spec

## Goal

Create a reproducible dataset of openly licensed Bible translations for ABTM experiments.

The dataset must support:

```text
artificial limitation experiments
Mark-only bootstrapping
cross-language evaluation
hidden-reference comparison
```

---

## Recommended source

Primary:

```text
https://github.com/midvash/bible-data
```

Reason:

```text
public-domain / freely redistributable texts
JSON and SQLite formats
multiple languages
OSIS-style book identifiers
metadata included
```

Other possible sources:

```text
Open English Bible
Open.Bible
BibleTTS for later audio experiments
API.Bible, only if licensing permits
```

---

## Output table

Produce:

```text
processed/verses.csv
processed/verses.parquet
processed/versions.csv
reports/coverage_by_version.csv
reports/nt_coverage_by_version.csv
```

Main schema:

```text
verse_id
book
chapter
verse
language
version
text
source
license
testament
raw_book
raw_path
```

---

## Canonical verse ID

```text
BOOK_CHAPTER_VERSE
```

Examples:

```text
MAT_001_001
MRK_001_001
LUK_002_014
JHN_003_016
ROM_008_028
REV_022_021
```

---

## Required splits

Generate:

```text
mark_only.json
seed_50_random_mark.json
seed_100_random_mark.json
seed_250_random_mark.json
gospels_only.json
```

Each split:

```json
{
  "name": "mark_only",
  "description": "Only Mark is visible. Rest of NT is hidden.",
  "seed_verse_ids": ["MRK_001_001"],
  "eval_verse_ids": ["MAT_001_001"]
}
```

---

## Minimum first dataset

Success criteria:

```text
at least one English public-domain source
at least 10 target languages
complete NT coverage for several versions
Mark-only split generated
coverage report generated
```

---

## Copyright requirements

Do not redistribute copyrighted translations.

Avoid:

```text
ESV
NIV
NLT
CSB
NASB
```

Use:

```text
WEB
ASV
KJV
OEB
public-domain translations
Creative Commons translations
```
