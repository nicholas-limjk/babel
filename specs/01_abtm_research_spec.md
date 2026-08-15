# Adaptive Bible Translation Memory (ABTM)
## Unified Research and Engineering Specification

## 1. Project objective

Build and evaluate a system that can bootstrap Bible translation for a target language `L` using only a small visible seed corpus, such as the Gospel of Mark.

The core research question is:

> How much translated Scripture is required to bootstrap useful translation of the rest of the New Testament?

The system should support controlled experiments where a complete Bible translation exists, but the system is artificially limited to only part of it.

---

## 2. Updated research framing

This project is **not** primarily about training a universal multilingual embedding model.

The MVP is:

> An adaptive, verse-indexed Bible translation memory that grows through retrieval, glossary extraction, phrase memory, LLM generation, verification, and human or automatic approval.

The LLM remains frozen. The system “learns” by adding approved verses, glossary entries, and phrases to memory.

---

## 3. Main hypothesis

A small seed translation, especially Mark, contains enough stylistic, lexical, and theological signal to bootstrap translation of the remainder of the New Testament using retrieval-augmented generation.

---

## 4. High-level flow

```text
Open Bible Data
      │
      ▼
Canonical Verse Store
      │
      ▼
Artificial Limitation Split
      │
      ├── Visible seed: Mark / 50 verses / 100 verses / etc.
      └── Hidden eval: remaining NT
      │
      ▼
Language L Translation Memory
      │
      ├── verse_id → L text
      ├── glossary
      ├── phrase memory
      └── style profile
      │
      ▼
English Semantic Retriever
      │
      ▼
Prompt Builder
      │
      ▼
Translator LLM
      │
      ▼
Verifier / QA
      │
      ▼
Approved Output
      │
      ▼
Memory Growth
```

---

## 5. Core components

### 5.1 Canonical Verse Store

Stores source Bible text, preferably a public-domain or openly licensed English translation.

Fields:

```text
verse_id
book
chapter
verse
language
version
text
testament
license
```

Canonical verse ID format:

```text
{BOOK}_{CHAPTER_PADDED_3}_{VERSE_PADDED_3}
```

Examples:

```text
MRK_001_001
JHN_003_016
ROM_008_028
REV_022_021
```

---

### 5.2 Translation Memory

Stores all visible and generated target-language verses.

Fields:

```text
verse_id
language
version
text
quality_tier       # gold | silver | bronze
source_type        # official | asr | generated | human_reviewed
review_status      # seed | approved | needs_review | rejected
created_at
```

Seed translations are treated as `gold`.

Generated translations are initially `bronze`, upgraded after review.

---

### 5.3 English Semantic Retriever

For a source verse, retrieve semantically similar English verses.

This does **not** require UBES.

Flow:

```text
English target verse
  → English embedding
  → nearest English verses
  → canonical verse IDs
  → lookup L translations
```

Recommended models:

```text
sentence-transformers/all-mpnet-base-v2
intfloat/e5-large-v2
BAAI/bge-large-en-v1.5
```

The first version can use `sentence-transformers/all-MiniLM-L6-v2` for speed.

---

### 5.4 Retrieval Policy

Retrieve examples using a mixed score:

```text
final_score =
  0.60 * semantic_similarity
+ 0.20 * term_coverage
+ 0.10 * book_or_genre_proximity
+ 0.10 * quality_score
```

Priority rules:

1. Prefer target-language verses already in translation memory.
2. Prefer gold over silver over bronze.
3. Always include 1–2 Mark style anchors during early bootstrapping.
4. For Epistles, increase weight on term coverage.
5. For Revelation, increase weight on phrase and imagery anchors.

---

### 5.5 Glossary Store

Stores approved mappings from English terms to language L terms.

Fields:

```text
english_term
target_term
category              # proper_name | place | theological | church | legal | other
locked                # true / false
confidence
source_verse_ids
notes
```

Hard-locked terms must be enforced by the verifier.

Examples:

```text
Jesus → <L term>
God → <L term>
Holy Spirit → <L term>
kingdom of God → <L term>
faith → <L term>
righteousness → <L term>
grace → <L term>
law → <L term>
```

---

### 5.6 Phrase Memory

Stores recurring phrase translations.

Fields:

```text
english_phrase
target_phrase
source_verse_ids
frequency
confidence
scope             # Mark | Gospels | NT-wide | book-specific
```

Examples:

```text
And he said to them → <L phrase>
The kingdom of God → <L phrase>
Truly, I say to you → <L phrase>
```

---

### 5.7 Style Profile

Inferred from seed translations.

Tracks:

```text
punctuation style
quotation style
capitalization
sentence length
conjunction usage
name spelling patterns
paragraph / verse formatting
```

The style profile is passed to the prompt builder.

---

### 5.8 Prompt Builder

Inputs:

```text
source verse
retrieved examples
glossary entries
phrase memory
style profile
optional previous/next verse context
```

Output:

A structured LLM prompt that instructs the model to:

```text
translate only the target verse
follow glossary exactly
match seed style
preserve meaning
avoid commentary
```

---

### 5.9 Translator LLM

The translator may be a hosted or open-weight LLM.

It must support:

```text
strong instruction following
few-shot pattern imitation
long enough context for 3–8 examples
stable output formatting
```

The LLM does not need to be fine-tuned in the MVP.

---

### 5.10 Verifier / QA

Checks:

```text
glossary compliance
proper-name consistency
missing clauses
added hallucinated clauses
verse formatting
length anomalies
repeated phrase consistency
```

Optional checks:

```text
back-translation similarity
LLM-as-judge
human review
```

---

## 6. Language onboarding in ABTM

Onboarding a new language means creating a language-specific memory:

```text
Language L Translation Memory
Language L Glossary
Language L Phrase Memory
Language L Style Profile
```

No embedding model is retrained.

Example:

```text
Mark in L
  → translation memory
  → glossary
  → phrase memory
  → style profile
  → translate Matthew
  → approve Matthew
  → memory grows
  → translate Luke
  → memory grows
  → translate Acts
  → memory grows
  → translate Epistles
```

---

## 7. Research experiments

### Experiment 1: Seed-size curve

Conditions:

```text
50 Mark verses
100 Mark verses
250 Mark verses
Full Mark
Mark + Matthew
Four Gospels
```

Measure translation quality on hidden NT verses.

---

### Experiment 2: Retrieval ablation

Compare:

```text
zero-shot LLM
static few-shot examples
random examples
BM25 examples
English semantic retrieval
semantic retrieval + glossary
semantic retrieval + glossary + verifier
```

---

### Experiment 3: Memory growth

Sequentially translate:

```text
Mark seed
→ Matthew
→ Luke
→ John
→ Acts
→ Epistles
→ Revelation
```

After each approved book, insert new verses into memory and measure whether later books improve.

---

### Experiment 4: Cross-language robustness

Run the same artificial limitation experiment across many languages.

Group results by:

```text
script
language family
available Bible coverage
resource proxy
translation age / style
```

---

## 8. Success criteria

The system is successful if:

```text
ABTM > zero-shot LLM
ABTM > random few-shot
ABTM > static Mark examples
ABTM improves as memory grows
ABTM has higher glossary consistency
ABTM reduces proper-name drift
```

Human evaluation should confirm that automatic metrics reflect meaningful improvements.

---

## 9. Non-goals for MVP

The MVP does not:

```text
train a multilingual embedding model
train a machine translation model
require ASR
require ESV
guarantee publishable theological translation
```

---

## 10. Future work

Potential future modules:

```text
Omnilingual ASR onboarding
UBES multilingual embedding space
human review UI
active learning
OT bootstrapping from NT
fine-tuned verifier
```
