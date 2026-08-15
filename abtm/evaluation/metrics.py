"""Small dependency-light evaluation metrics for the MVP."""

from __future__ import annotations

from collections import Counter

from abtm.verification import length_ratio


def _char_ngrams(text: str, n: int) -> Counter[str]:
    padded = f" {text.lower()} "
    return Counter(padded[idx:idx + n] for idx in range(0, max(0, len(padded) - n + 1)))


def sentence_chrf(candidate: str, reference: str, max_n: int = 6, beta: float = 2.0) -> float:
    if not candidate.strip() or not reference.strip():
        return 0.0
    scores = []
    for n in range(1, max_n + 1):
        cand = _char_ngrams(candidate, n)
        ref = _char_ngrams(reference, n)
        overlap = sum((cand & ref).values())
        precision = overlap / max(1, sum(cand.values()))
        recall = overlap / max(1, sum(ref.values()))
        if precision == 0.0 and recall == 0.0:
            scores.append(0.0)
        else:
            beta2 = beta * beta
            scores.append((1 + beta2) * precision * recall / (beta2 * precision + recall))
    return sum(scores) / len(scores)


def sentence_bleu_unigram(candidate: str, reference: str) -> float:
    cand_tokens = candidate.lower().split()
    ref_tokens = reference.lower().split()
    if not cand_tokens or not ref_tokens:
        return 0.0
    overlap = sum((Counter(cand_tokens) & Counter(ref_tokens)).values())
    precision = overlap / len(cand_tokens)
    brevity = min(1.0, len(cand_tokens) / len(ref_tokens))
    return precision * brevity


def corpus_scores(rows: list[dict[str, str]]) -> dict[str, float]:
    if not rows:
        return {"chrf": 0.0, "bleu_unigram": 0.0, "length_ratio": 0.0}
    chrf = [sentence_chrf(row["candidate"], row["reference"]) for row in rows]
    bleu = [sentence_bleu_unigram(row["candidate"], row["reference"]) for row in rows]
    ratios = [length_ratio(row.get("source", ""), row["candidate"]) for row in rows]
    return {
        "chrf": sum(chrf) / len(chrf),
        "bleu_unigram": sum(bleu) / len(bleu),
        "length_ratio": sum(ratios) / len(ratios),
    }
