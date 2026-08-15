# Cursor / Codex Implementation Instructions

## Read first

Read these files in order:

```text
specs/01_abtm_research_spec.md
specs/02_data_ingestion_spec.md
specs/03_experiment_eval_spec.md
```

Do not implement UBES first. UBES is optional future work.

---

## Build order

### Milestone 1: Dataset ingestion

Implement or improve:

```text
scripts/pull_open_bibles.py
scripts/create_splits.py
```

Expected outputs:

```text
data/bible_dataset/processed/verses.csv
data/bible_dataset/processed/verses.parquet
data/bible_dataset/processed/versions.csv
data/bible_dataset/splits/mark_only.json
```

---

### Milestone 2: ABTM core package

Create package:

```text
abtm/
  canonical/
  retrieval/
  memory/
  glossary/
  phrase_memory/
  prompting/
  verification/
  evaluation/
```

Start with clean interfaces and stub LLM calls.

---

### Milestone 3: English retriever

Implement:

```text
English verse embeddings
nearest-neighbor retrieval
verse_id lookup
target-language example lookup
```

Use sentence-transformers.

---

### Milestone 4: Translation memory

Implement:

```text
load seed memory
lookup verse_id → target text
insert generated output
quality tiers
```

---

### Milestone 5: Glossary and phrase extraction

Start simple:

```text
proper noun list
frequent repeated phrases
manual glossary CSV support
```

Avoid overengineering.

---

### Milestone 6: Prompt builder

Implement prompt construction with:

```text
source verse
retrieved examples
glossary
phrase memory
style rules
```

LLM call can be a placeholder at first.

---

### Milestone 7: Evaluation

Implement:

```text
chrF
BLEU
glossary pass rate
name consistency
length ratio
```

Human evaluation can be CSV-based.

---

## Coding constraints

- Keep all modules independent.
- Use canonical `verse_id` everywhere.
- Avoid copyrighted translations.
- Make experiments reproducible.
- Add unit tests for verse ID normalization and split generation.
- Do not hard-code one language.
- Use configuration files for source version, target versions, and seed split.

---

## First command to support

```bash
python scripts/pull_open_bibles.py --out data/bible_dataset --nt-only
```

## Second command to support

```bash
python scripts/create_splits.py \
  --verses data/bible_dataset/processed/verses.csv \
  --out data/bible_dataset/splits
```

## Third command to eventually support

```bash
python -m abtm.experiments.run_bootstrap \
  --dataset data/bible_dataset/processed/verses.csv \
  --source-version web \
  --target-version <target_version> \
  --split data/bible_dataset/splits/mark_only.json \
  --method semantic_glossary_verifier
```
