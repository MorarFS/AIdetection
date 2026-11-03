#!/usr/bin/env python3
"""Report transparent, interpretable diagnostics for academic prose."""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
from pathlib import Path


WORD_RE = re.compile(r"\b[\w'’.-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"'’”)]*)\s+(?=[A-Z\"'“])")
VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)
HEDGES = {
    "apparently", "approximately", "arguably", "could", "likely", "may",
    "might", "perhaps", "possible", "possibly", "seem", "seems", "suggest",
    "suggests", "tend", "tends", "unlikely",
}
BOOSTERS = {
    "certainly", "clearly", "demonstrate", "demonstrates", "establish",
    "establishes", "evidently", "indeed", "must", "obviously", "show",
    "shows", "undoubtedly",
}
FIRST_PERSON = {"i", "me", "my", "mine", "we", "us", "our", "ours"}


def coefficient_of_variation(values: list[int]) -> float | None:
    if not values:
        return None
    mean = sum(values) / len(values)
    if mean == 0:
        return None
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance) / mean


def percentile(values: list[int], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def mtld(tokens: list[str], threshold: float = 0.72) -> float | None:
    """Compute bidirectional MTLD using the standard partial-factor rule."""

    def factors(sequence: list[str]) -> float:
        seen: set[str] = set()
        count = 0
        factor_count = 0.0
        for token in sequence:
            count += 1
            seen.add(token)
            ttr = len(seen) / count
            if ttr <= threshold:
                factor_count += 1
                seen.clear()
                count = 0
        if count:
            ttr = len(seen) / count
            factor_count += (1 - ttr) / (1 - threshold)
        return len(sequence) / factor_count if factor_count else float(len(sequence))

    if not tokens:
        return None
    return (factors(tokens) + factors(list(reversed(tokens)))) / 2


def syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    groups = len(VOWEL_GROUP_RE.findall(cleaned))
    if cleaned.endswith("e") and not cleaned.endswith(("le", "ye")) and groups > 1:
        groups -= 1
    return max(1, groups)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    text = args.path.read_text(encoding="utf-8").strip()
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    sentences = [part.strip() for part in SENTENCE_RE.split(text) if part.strip()]
    sentence_words = [WORD_RE.findall(sentence) for sentence in sentences]
    sentence_lengths = [len(words) for words in sentence_words]
    paragraph_lengths = [len(WORD_RE.findall(paragraph)) for paragraph in paragraphs]
    openings = [" ".join(words[:3]).lower() for words in sentence_words if words]
    opening_counts = collections.Counter(openings)

    all_words = WORD_RE.findall(text)
    normalized = [word.lower().strip(".-") for word in all_words if word.strip(".-")]
    unique_words = set(normalized)
    word_count = len(normalized)
    syllable_count = sum(syllables(word) for word in normalized)
    complex_words = sum(syllables(word) >= 3 for word in normalized)
    per_thousand = lambda count: round(count * 1000 / word_count, 3) if word_count else None
    punctuation = {
        "semicolon": text.count(";"),
        "colon": text.count(":"),
        "parenthetical_open": text.count("("),
        "question_mark": text.count("?"),
        "dash": len(re.findall(r"[—–]|(?<=\s)-(?:\s)", text)),
    }

    result = {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "sentence_length": {
            "mean": round(sum(sentence_lengths) / len(sentence_lengths), 3) if sentence_lengths else None,
            "median": round(percentile(sentence_lengths, 0.5), 3) if sentence_lengths else None,
            "p90": round(percentile(sentence_lengths, 0.9), 3) if sentence_lengths else None,
            "min": min(sentence_lengths) if sentence_lengths else None,
            "max": max(sentence_lengths) if sentence_lengths else None,
            "cv": round(coefficient_of_variation(sentence_lengths), 3) if sentence_lengths else None,
        },
        "paragraph_length": {
            "mean": round(sum(paragraph_lengths) / len(paragraph_lengths), 3)
            if paragraph_lengths
            else None,
            "min": min(paragraph_lengths) if paragraph_lengths else None,
            "max": max(paragraph_lengths) if paragraph_lengths else None,
            "cv": round(coefficient_of_variation(paragraph_lengths), 3)
            if paragraph_lengths
            else None,
        },
        "paragraph_length_cv": round(coefficient_of_variation(paragraph_lengths), 3)
        if paragraph_lengths
        else None,
        "lexical": {
            "type_token_ratio": round(len(unique_words) / word_count, 4) if word_count else None,
            "root_ttr": round(len(unique_words) / math.sqrt(word_count), 4) if word_count else None,
            "mtld": round(mtld(normalized), 3) if normalized else None,
            "mean_word_length": round(sum(map(len, normalized)) / word_count, 3)
            if word_count
            else None,
        },
        "readability": {
            "flesch_reading_ease": round(
                206.835 - 1.015 * (word_count / len(sentences))
                - 84.6 * (syllable_count / word_count),
                3,
            )
            if word_count and sentences
            else None,
            "flesch_kincaid_grade": round(
                0.39 * (word_count / len(sentences))
                + 11.8 * (syllable_count / word_count) - 15.59,
                3,
            )
            if word_count and sentences
            else None,
            "gunning_fog": round(
                0.4 * ((word_count / len(sentences)) + 100 * complex_words / word_count),
                3,
            )
            if word_count and sentences
            else None,
        },
        "punctuation_per_1000_words": {
            key: per_thousand(value) for key, value in punctuation.items()
        },
        "stance_per_1000_words": {
            "first_person_pronouns": per_thousand(sum(word in FIRST_PERSON for word in normalized)),
            "hedge_markers": per_thousand(sum(word in HEDGES for word in normalized)),
            "booster_markers": per_thousand(sum(word in BOOSTERS for word in normalized)),
        },
        "evidence_signals": {
            "sentences_with_digits_fraction": round(
                sum(bool(re.search(r"\d", sentence)) for sentence in sentences) / len(sentences), 4
            )
            if sentences
            else None,
            "parenthetical_year_mentions": len(re.findall(r"\((?:[^)]*?\b(?:1[5-9]|20)\d{2}\b[^)]*?)\)", text)),
        },
        "repeated_three_word_openings": {
            opening: count for opening, count in opening_counts.items() if count > 1
        },
        "limits": [
            "Metrics are diagnostics, not universal quality thresholds.",
            "Sentence splitting is heuristic and may treat abbreviations imperfectly.",
            "Readability uses heuristic syllable counts and measures processing demand, not quality.",
            "Hedge, booster, and pronoun counts use small transparent lexicons, not full discourse parsing.",
            "Type-token ratio remains text-length sensitive; compare MTLD on length-matched samples.",
            "These metrics do not establish authorship.",
        ],
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
