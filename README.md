# Adaptive Bible Translation Memory (ABTM)

A starter research project for testing whether a small translated seed corpus, such as the Gospel of Mark, can bootstrap translation of the rest of the New Testament for extremely low-resource languages.

## Core idea

The system does **not** train a new MT model first.

Instead, it builds a growing, verse-indexed translation memory:

```text
English source verse
  → English semantic retrieval
  → canonical verse IDs
  → target-language examples
  → glossary + phrase memory
  → translator LLM
  → verifier
  → approved verse added back to memory
```

Every approved translation becomes future supervision.

## What this project contains

```text
abtm/
  canonical/        canonical book codes and verse IDs
  retrieval/        English TF-IDF retrieval baseline
  memory/           translation memory store
  glossary/         manual glossary support
  phrase_memory/    recurring phrase memory
  prompting/        structured prompt builder
  verification/     lightweight QA checks
  evaluation/       chrF / unigram BLEU style metrics
  experiments/      bootstrap experiment runner

specs/
  01_abtm_research_spec.md
  02_data_ingestion_spec.md
  03_experiment_eval_spec.md
  04_cursor_codex_instructions.md
  05_optional_ubes_future_work.md

scripts/
  pull_open_bibles.py
  create_splits.py

configs/
  dataset_config.example.yaml
  experiment_config.example.yaml

requirements.txt
```

## First milestone

1. Pull open Bible translations.
2. Normalize to a verse-level table.
3. Create artificial limitation splits.
4. Run Mark-only experiments.
5. Compare against hidden target-language references.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python scripts/pull_open_bibles.py --out data/bible_dataset --nt-only
python scripts/create_splits.py --verses data/bible_dataset/processed/verses.csv --out data/bible_dataset/splits
```

Run a first-pass bootstrap experiment:

```bash
python -m abtm.experiments.run_bootstrap \
  --dataset data/bible_dataset/processed/verses.csv \
  --source-version web \
  --target-version <target_version> \
  --split data/bible_dataset/splits/mark_only.json \
  --out runs/mark_only
```

The experiment runner currently uses deterministic nearest-memory placeholder
generation instead of an LLM call. It still exercises retrieval, prompt
construction, glossary/phrase hooks, verification, and reference metrics.

Run tests:

```bash
python -m unittest discover -s tests
```

## Recommended first experiment

For each target language with complete NT coverage:

```text
Visible:
  Mark in target language

Hidden:
  Matthew, Luke, John, Acts, Epistles, Revelation

Task:
  Translate hidden NT books from English into target language.

Evaluation:
  Compare generated output against hidden reference translation.
```

## Important copyright note

Do not redistribute copyrighted translations such as ESV, NIV, NLT, CSB, etc. Use public-domain or openly licensed sources for experiments.

Recommended open English sources:
- World English Bible
- American Standard Version
- King James Version
- Open English Bible
