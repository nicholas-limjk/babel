# ABTM Experiment and Evaluation Spec

## Core evaluation setup

Use complete Bible translations as hidden references.

Artificially limit the system by exposing only a seed subset.

Example:

```text
Visible to system:
  English full NT
  Language L Mark

Hidden:
  Language L Matthew–Revelation
```

The system translates hidden verses, then outputs are compared to hidden references.

---

## Seed conditions

Run at least:

```text
50 random Mark verses
100 random Mark verses
250 random Mark verses
Full Mark
Mark + Matthew
Four Gospels
```

Use fixed random seeds.

---

## Target sections

Evaluate separately:

```text
Other Gospels
Acts
Pauline Epistles
General Epistles
Revelation
```

Expected difficulty:

```text
Other Gospels < Acts < General Epistles < Pauline Epistles < Revelation
```

---

## Baselines

Compare:

### B0: Zero-shot LLM

No target-language examples.

### B1: Static Mark few-shot

Always use the same fixed Mark examples.

### B2: Random few-shot

Random visible target-language verses.

### B3: BM25 retrieval

Keyword retrieval over English source.

### B4: English semantic retrieval

English embedding → nearest English verses → target-language examples.

### B5: Semantic retrieval + glossary

Adds glossary constraints.

### B6: Full ABTM

Semantic retrieval + glossary + phrase memory + verifier + memory growth.

---

## Metrics

### Automatic MT metrics

```text
chrF
BLEU
COMET / COMETKiwi if available
BERTScore if useful
```

### Consistency metrics

```text
proper-name consistency
glossary pass rate
forbidden variant rate
phrase reuse consistency
```

### Structural metrics

```text
length ratio
missing verse count
empty output count
formatting validity
```

### Human evaluation

Rate 1–5:

```text
meaning accuracy
fluency
completeness
terminology consistency
style match
```

---

## Memory growth experiment

Sequential order:

```text
Seed: Mark
Translate Matthew
Approve / insert Matthew
Translate Luke
Approve / insert Luke
Translate John
Approve / insert John
Translate Acts
Approve / insert Acts
Translate Epistles
Approve / insert Epistles
Translate Revelation
```

Measure whether later book quality improves as memory grows.

---

## Reporting tables

### Seed-size curve

| Language | Seed | Target Section | chrF | BLEU | Glossary Pass | Human Score |
|---|---|---|---:|---:|---:|---:|

### Ablation table

| Method | chrF | BLEU | Glossary Pass | Name Consistency | Human Score |
|---|---:|---:|---:|---:|---:|

### Section difficulty table

| Section | Method | Score |
|---|---|---:|

---

## Minimum publishable result

A strong result would show:

```text
Full ABTM consistently beats zero-shot, random examples, and static few-shot.
Translation quality improves with seed size.
Translation quality improves with memory growth.
Glossary and name consistency improve substantially.
```
