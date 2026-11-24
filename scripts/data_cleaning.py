# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/data_cleaning.py
Description: Deterministic, acronym-safe bilingual & Cordilleran text cleaning pipeline.
             Performs case normalization, selective metadata stripping (preserving parenthetical
             SLU acronyms), word-bounded Filipino/Taglish clitic & slang normalization,
             context-aware contraction expansion (protecting 'ill' and possessive 's),
             and structural header filtering.
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
Instructor: Prof. Dalos D. Miguel
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_INPUT_DIR = os.path.join(REPO_ROOT, "data", "raw_midterm")
DEFAULT_OUTPUT_FILE = os.path.join(REPO_ROOT, "outputs", "cleaned_corpus.txt")

HEADER_LINE_PATTERN = re.compile(
    r"^(article\s+[ivx]+\b|[123]\.\s+(slu guidelines|center for health|emergency and evacuation))",
    re.IGNORECASE,
)

# Explicit contraction mappings (avoids corrupting possessive nouns like "SLU's" -> "slu is")
EXPLICIT_CONTRACTIONS = (
    (r"\bi'll\b", "i will"),
    # Context-aware expansion for missing-apostrophe "ill" (e.g., "ill still answer"),
    # while leaving medical/clinical "ill" ("I am feeling ill") untouched.
    (
        r"\bill\b(?=\s+(?:still|be|just|never|always|go|send|call|wait|try|ask|do|have|get|make|take|see|tell|give|come|check|submit|pay|enroll|shift|transfer)\b)",
        "i will",
    ),
    (r"\bi'm\b", "i am"),
    (r"\bit's\b", "it is"),
    (r"\bthat's\b", "that is"),
    (r"\bwhat's\b", "what is"),
    (r"\bwhere's\b", "where is"),
    (r"\bwho's\b", "who is"),
    (r"\bthere's\b", "there is"),
    (r"\bhere's\b", "here is"),
    (r"\bhe's\b", "he is"),
    (r"\bshe's\b", "she is"),
    (r"\blet's\b", "let us"),
    (r"\bcan't\b", "can not"),
    (r"\bwon't\b", "will not"),
    (r"\bdon't\b", "do not"),
    (r"\bdoesn't\b", "does not"),
    (r"\bdidn't\b", "did not"),
    (r"n't\b", " not"),
    (r"'re\b", " are"),
    (r"'d\b", " would"),
    (r"'ll\b", " will"),
    (r"'ve\b", " have"),
    # Strip remaining possessive "'s" cleanly (e.g., "SLU's Registrar's Office" -> "slu registrar office")
    (r"([a-z0-9]+)'s\b", r"\1"),
)

FIL_CLITICS = (
    (r"\bba't\b", "bakit"),
    (r"\bdi'ba\b|\bdiba\b", "hindi ba"),
    (r"\bsa'kin\b|\bsakin\b", "sa akin"),
    (r"\bsa'yo\b|\bsayo\b", "sa iyo"),
    (r"\bn'yo\b|\bnyo\b|\bniyo\b", "ninyo"),
    (r"\bano't\b", "ano at"),
    (r"\bsamin\b", "sa amin"),
    (r"\bnung\b", "noong"),
    (r"\bngaun\b", "ngayon"),
    (r"\bung\b", "yung"),
    (r"\bnalang\b", "na lang"),
    (r"\bambilat\b", "ambigat"),
    (r"\brember\b", "remember"),
    (r"\bmake\s+tawad\b", "make tawid"),
    (r"\bpedxing\b", "pedestrian crossing"),
    (r"\bihyk\b", "i hope you know"),
    (r"\bconvo\b", "conversation"),
    (r"\bwth\b", "what the hell"),
    (r"\bfr\b", "for real"),
    (r"\bdp\b", "downpayment"),
    (r"\blike{2,}\b", "like"),
    (r"\bh+a+(?:h+a+)+h*\b", "haha"),
)

# Hyphenated Cordilleran (CAR) lemmas preserved across cleaning if requested
CAR_HYPHENATED_TOKENS = ("dap-ay", "man-obla", "men-obla", "pan-adal", "man-adal")


def clean_text(text, preserve_car_hyphens=False):
    """
    Deterministic acronym-safe text normalization.
    - Preserves parenthetical SLU acronyms: (SAMCIS), (TOR), (COG), (MLS), (QE), (FDA), (PATHFIT).
    - Protects English 'ill' and possessive nouns ('SLU's' -> 'slu').
    - Preserves terminal question/exclamation polarity when collapsing repeated punctuation ('??' -> '?').
    """
    text = text.replace("\ufeff", "").lower()

    # 1. Strip bracketed tags/citations and inline #SLUFreedomWall hashtags
    text = re.sub(r"\[.*?\]", " ", text)
    text = re.sub(r"#slufreedomwall\d+", " ", text)

    # 2. Strip URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # 3. Strip only submission/archive metadata parentheses (keep acronyms like (SAMCIS), (TOR))
    text = re.sub(r"\((submitted:.*?|public post archive)\)", " ", text)

    # 4. Strip structural prefixes (Q1:, A1:, Section 1.)
    text = re.sub(r"^(q\d+|a\d+)\s*:\s*", "", text)
    text = re.sub(r"^section\s+\d+\.\s*", "", text)

    # 5. Standardize comma-separated numbers (6,900 -> 6900) and percentages (20% -> 20 percent)
    text = re.sub(r"(?<=\d),(?=\d)", "", text)
    text = re.sub(r"(\d+)\s*%", r"\1 percent", text)

    # 6. Normalize smart quotes/apostrophes before clitic & contraction expansion
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u2014", " ").replace("\u2013", " ")

    # 7. Word-bounded Filipino/Taglish clitic and informal slang normalization
    for pattern, replacement in FIL_CLITICS:
        text = re.sub(pattern, replacement, text)

    # 8. Context-aware English contraction expansion & possessive stripping
    for pattern, replacement in EXPLICIT_CONTRACTIONS:
        text = re.sub(pattern, replacement, text)

    # 9. Protect hyphenated CAR lemmas if enabled (used by hardened chatbot query pipeline)
    if preserve_car_hyphens:
        for token in CAR_HYPHENATED_TOKENS:
            placeholder = token.replace("-", "carhyphen")
            text = re.sub(r"\b" + re.escape(token) + r"\b", placeholder, text)

    # 10. Remove non-alphanumeric noise while preserving sentence boundaries
    text = re.sub(r"[^a-z0-9\s\.\?\!]", " ", text)

    if preserve_car_hyphens:
        for token in CAR_HYPHENATED_TOKENS:
            placeholder = token.replace("-", "carhyphen")
            text = text.replace(placeholder, token)

    # 11. Collapse adjacent duplicate expansions (e.g., "downpayment (dp)" -> "downpayment")
    text = re.sub(
        r"\b(downpayment|samcis|seait|sonahbs|tor|cog|fda|mls|qe|pathfit|rfid)\s+\1\b",
        r"\1",
        text,
    )

    # 12. Collapse repeated terminal punctuation while preserving '?' vs '!' vs '.'
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"[\.\?\!]{2,}", ".", text)
    text = re.sub(r"\s+([\.\?\!])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def process_all_files(input_dir=None, output_file=None):
    """Cleans all .txt files in input_dir and writes consolidated line-per-doc output."""
    if input_dir is None:
        input_dir = DEFAULT_INPUT_DIR
    if output_file is None:
        output_file = DEFAULT_OUTPUT_FILE

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    cleaned_documents = []
    source_records = []

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".txt"):
            continue
        file_path = os.path.join(input_dir, filename)
        with open(file_path, "r", encoding="utf-8-sig") as f:
            raw_lines = f.readlines()

        pending_post_id = None
        for line in raw_lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or line_str.startswith("="):
                continue
            post_header = re.match(r"^\[#SLUFreedomWall(\d+)\]", line_str)
            if post_header and len(clean_text(line_str)) <= 15:
                pending_post_id = post_header.group(1)
                continue
            if HEADER_LINE_PATTERN.match(line_str):
                continue
            cleaned = clean_text(line_str)
            if len(cleaned) > 15:
                cleaned_documents.append(cleaned)
                source_records.append(
                    {
                        "source_file": filename,
                        "post_id": pending_post_id,
                        "cleaned_text": cleaned,
                    }
                )
                pending_post_id = None

    with open(output_file, "w", encoding="utf-8") as f:
        for doc in cleaned_documents:
            f.write(doc + "\n")

    print(f"[OK] Cleaned {len(cleaned_documents)} documents from {input_dir} -> {output_file}")
    return cleaned_documents, source_records


if __name__ == "__main__":
    process_all_files()
