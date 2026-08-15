# Optional Future Work: Universal Bible Embedding Space (UBES)

## Status

UBES is not part of the MVP.

The simplified ABTM system retrieves examples using English embeddings and canonical verse IDs.

This is sufficient for English → L translation experiments.

---

## Why UBES was deprioritized

For translation retrieval, English-only retrieval is enough:

```text
English verse
  → English embedding
  → nearest English verses
  → verse IDs
  → target-language examples
```

A reviewer could reasonably ask why a multilingual embedding model is needed.

---

## Where UBES may still be useful

UBES becomes useful for:

```text
ASR transcript → verse ID alignment
cross-language semantic search
terminology mining across many languages
direct target-language retrieval
language onboarding with audio-only data
semantic consistency evaluation
```

---

## Future research question

> Can a Bible-specific multilingual embedding space rapidly adapt to a new language using only a small number of verse-aligned examples?

This should be treated as a second paper or optional module after ABTM is validated.
