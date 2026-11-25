# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/build_presentation.py
Description: Builds the Canva EAG-QJ6Vos4 Graph-Paper Classroom TV Edition 22-slide (15-20 minute) presentation:
             - Alternating Dark Neon-Glow Grid slides (#0B0817 + magenta/violet aura + coral pills)
               and Light Cream Graph-Paper + macOS Window Chrome slides (#FAF8F3 + #D4E6F1 grid + #E2E5EC bar)
             - Classroom TV Large-Print readability floor (20-38pt titles, 14-16.5pt body/tables,
               30-40pt KPI numbers, max 3-4 cols per table, dedicated full-canvas large-print TV charts)
             - Dynamically synced from models/evaluation_report.json and data/expanded/*
             1. Google Slides (single batch API, embedded TV charts & QR, speaker notes)
             2. Local PowerPoint backup (presentation/Group2_AiNomally_CSE30_Deck.pptx via python-pptx)
             3. Timed 5-Speaker Script (presentation/speaker_script_15_20min.md + Google Drive Doc sync)
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import argparse
import csv
import json
import os
import re
import subprocess
from collections import Counter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Pt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
CHARTS_DIR = os.path.join(REPO_ROOT, "charts")
PRES_DIR = os.path.join(REPO_ROOT, "presentation")
EXPANDED_DIR = os.path.join(REPO_ROOT, "data", "expanded")
EVAL_REPORT_PATH = os.path.join(REPO_ROOT, "models", "evaluation_report.json")
SCRATCH = "/Users/chazerodriguez/.gemini/antigravity/brain/1cb302af-b0c5-465c-a595-27c16ec8c63f/scratch"
SCRIPT_DOC_ID = "12mEnNUJsdP4etsm0VRn38-v6Xu2GOXg270IMv2O0V3s"

# Canva EAG-QJ6Vos4 Palette (Light Cream Graph-Paper + Dark Neon-Glow Grid)
C_CREAM_BG = "#FAF8F3"
C_PAPER_GRID = "#D4E6F1"
C_CHROME_BAR = "#E2E5EC"
C_DOT_RED = "#FF5F57"
C_DOT_YELLOW = "#FEBC2E"
C_DOT_GREEN = "#28C840"

C_DARK_BG = "#0B0817"
C_DARK_GRID = "#231C3D"
C_DARK_CARD = "#16112B"
C_DARK_CARD_ALT = "#1E163B"
C_DARK_BORDER = "#4C1D95"

C_INK = "#0D0A1A"
C_VIOLET = "#6D28D9"
C_VIOLET_BRIGHT = "#A855F7"
C_MAGENTA = "#EC4899"
C_AURA_PURPLE = "#9333EA"
C_AURA_LIGHT = "#F472B6"
C_CORAL = "#EB6A48"
C_TEAL = "#0E7490"
C_NAVY = "#002855"
C_ROYAL = "#004B87"
C_INDIGO = "#1E3A8A"
C_GOLD_BRIGHT = "#FACC15"
C_GOLD_LIGHT = "#FEF3C7"
C_WHITE = "#FFFFFF"
C_MUTED = "#475569"
C_LIGHT_MUTED = "#CBD5E1"
C_GREEN_BG = "#DCFCE7"
C_GREEN_FG = "#166534"
C_RED_FG = "#B91C1C"
C_AMBER = "#B45309"
C_ROW_ALT = "#F1EFFA"

TOTAL_SLIDES = 22


def load_live_metrics():
    """Load real-time metrics from evaluation_report.json and data/expanded/*."""
    with open(EVAL_REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
    with open(os.path.join(EXPANDED_DIR, "slu_official_policies_v2.json"), "r", encoding="utf-8") as f:
        policies = json.load(f)
    with open(os.path.join(EXPANDED_DIR, "heldout_benchmark.json"), "r", encoding="utf-8") as f:
        benchmark = json.load(f)
    lex_lang = Counter()
    with open(os.path.join(EXPANDED_DIR, "slu_car_domain_lexicon_v2.csv"), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lex_lang[row["Language_ISO"]] += 1

    csum = report["corpus_summary"]
    cv = report["stratified_5fold_cv"]
    abl = report["heldout_ablation"]

    best_name = report["best_model"]
    best_stats = cv[best_name]
    svm_stats = cv["Linear SVM (One-vs-Rest Hinge)"]
    nb_stats = cv["Multinomial Naive Bayes"]
    lr_stats = cv["Logistic Regression (L2 Softmax)"]
    svm_cm = svm_stats["confusion_matrix"]
    svm_diag_hits = sum(svm_cm[i][i] for i in range(len(svm_cm)))
    svm_perfect = [
        cls for i, cls in enumerate(svm_stats["classes"])
        if svm_cm[i][i] == sum(svm_cm[i])
    ]

    return {
        "docs": csum["total_documents"],
        "docs_per_class": csum["docs_per_intent"],
        "intents": csum["intent_classes"],
        "policies": len(policies),
        "lex_total": sum(lex_lang.values()),
        "lex_ilo": lex_lang.get("ilo", 0),
        "lex_kne": lex_lang.get("kne", 0),
        "lex_ibl": lex_lang.get("ibl", 0),
        "lex_slu": sum(v for k, v in lex_lang.items() if k not in ("ilo", "kne", "ibl")),
        "en_docs": csum["code_switching_counts"].get("EN", 0),
        "tl_docs": csum["code_switching_counts"].get("TL-EN", 0),
        "car_docs": csum["code_switching_counts"].get("CAR-TL-EN", 0),
        "official_docs": csum["source_type_counts"].get("OFFICIAL_SLU_POLICY", 0),
        "uro_docs": csum["source_type_counts"].get("OFFICIAL_URO_FAQ_Q", 0),
        "fw_docs": csum["source_type_counts"].get("HARVESTED_FREEDOM_WALL", 0),
        "curated_docs": csum["source_type_counts"].get("CURATED_MULTILINGUAL_INQUIRY", 0),
        "bench_total": len(benchmark),
        "bench_in_domain": abl["D_full_hybrid"]["in_domain_queries"],
        "bench_ood": len(benchmark) - abl["D_full_hybrid"]["in_domain_queries"],
        "best_name": best_name,
        "best_acc": best_stats["accuracy"] * 100.0,
        "best_f1": best_stats["macro_f1"] * 100.0,
        "best_std": best_stats["std_macro_f1"] * 100.0,
        "svm_acc": svm_stats["accuracy"] * 100.0,
        "svm_f1": svm_stats["macro_f1"] * 100.0,
        "svm_std": svm_stats["std_macro_f1"] * 100.0,
        "svm_hits": svm_diag_hits,
        "svm_perfect": svm_perfect,
        "nb_acc": nb_stats["accuracy"] * 100.0,
        "nb_f1": nb_stats["macro_f1"] * 100.0,
        "nb_std": nb_stats["std_macro_f1"] * 100.0,
        "lr_acc": lr_stats["accuracy"] * 100.0,
        "lr_f1": lr_stats["macro_f1"] * 100.0,
        "lr_std": lr_stats["std_macro_f1"] * 100.0,
        "abl_a": abl["A_raw_tfidf"],
        "abl_b": abl["B_clean_morph"],
        "abl_c": abl["C_lexicon_boost"],
        "abl_d": abl["D_full_hybrid"],
    }


def build_speaker_notes(m):
    """Timed 22-slide speaker notes (~18.8 min balanced across 5 presenters)."""
    return {
        1: (
            "[Speaker 1: Chaze Rodriguez | Target: 0:40]\n"
            "Good afternoon, Professor Dalos Miguel and fellow Louisian computer scientists! "
            "We are Group 2, AiNomally—John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, "
            "Erick James Sibayan, and I am Chaze Ezkys Rodriguez. Today we present our CSE 30 NLP Term Project: "
            "the SLU eGovernance Multilingual Chatbot and Cordillera Administrative Region Electronic Lexicon, "
            f"now upgraded to {m['policies']} verified SLU policies—including Latin honors GWA thresholds and dropped versus "
            "permanently dropped FDA rules—paired with leak-free supervised machine learning and our Canva graph-paper portal."
        ),
        2: (
            "[Speaker 1: Chaze Rodriguez | Target: 1:00]\n"
            "Slide 2 frames the dual problem motivating our research right here in Baguio City. "
            "First, critical Saint Louis University rules—like exact Latin honors GWA cutoffs or when a withdrawal becomes permanent FDA—"
            "are scattered across the 2015 Student Handbook PDF, URO website, OSAS circulars, and Finance channels. Students turn to "
            "#SLUFreedomWall in urgent Taglish using SAMCIS, dp, QE, and FDA, which keyword search misses. "
            "Second, SLU serves a vibrant Cordillera student body speaking Ilocano, Northern Kankanaey, and Ibaloi, where English NLP "
            "breaks on affixes like ag-, panag-, and man-, and ignores cultural roots like inayan, dap-ay, and tongtong."
        ),
        3: (
            "[Speaker 1: Chaze Rodriguez | Target: 0:55]\n"
            f"Slide 3 aligns our work directly with both CSE 30 tracks. Under Track A, we built a {m['lex_total']}-entry machine-readable "
            "SLU and CAR Electronic Lexicon tagged with ISO 639-3 codes, morphological roots, affixes, and Native versus Semantic alias separation. "
            f"Under Track B, we engineered a hybrid eGovernance chatbot covering {m['policies']} verified SLU policy provisions across {m['intents']} domains. "
            f"Four pillars guided every commit: single-command reproducibility, TDD security hardening, balanced scaling to {m['docs']} annotated docs, "
            f"and leak-free benchmarking on {m['bench_total']} unseen queries. Over to Keith Hernandez for architecture and data cleaning."
        ),
        4: (
            "[Speaker 2: Keith Hernandez | Target: 1:00]\n"
            "Thank you, Chaze. Slide 4 shows our end-to-end 5-stage NLP pipeline runnable from a clean checkout via python3 scripts/build_all.py. "
            f"Stage 1 unifies #SLUFreedomWall student posts with {m['policies']} official SLU rules covering URO, the Student Handbook, Latin honors, "
            "absences, Finance, Counseling, and Libraries. Stage 2 runs deterministic acronym-safe cleaning, protecting acronyms and CAR hyphens. "
            "Stage 3 applies our guarded bilingual and Cordilleran morphological analyzer with 265 stopwords and bigrams. "
            f"Stage 4 trains pure-Python Linear SVM, Naive Bayes, and Logistic Regression fused with our {m['lex_total']}-entry lexicon and OOD safety gate. "
            "Stage 5 compiles identical model weights into our zero-XSS Canva graph-paper portal, verified by 22 automated tests."
        ),
        5: (
            "[Speaker 2: Keith Hernandez | Target: 1:00]\n"
            "Slide 5 visualizes our scaling from Midterm to Finals. "
            f"Our annotated corpus grew 14.6 times from 24 to {m['docs']} strictly balanced documents—{m['docs_per_class']} per class across {m['intents']} operational intents. "
            f"Authoritative SLU policies grew 4.3 times from 12 to {m['policies']}, now explicitly covering niche high-demand Handbook provisions like Latin Honors GWA requirements "
            "(93, 91, 88 percent), Voluntary Dropping versus 20% Permanent FDA, Promissory Notes, and Petition Classes. "
            f"Our CAR lexicon expanded 7.0 times from 25 to {m['lex_total']} entries, Cordilleran documents jumped 45 times from 2 to {m['car_docs']}, "
            f"and held-out evaluation expanded from 8 to {m['bench_total']} strictly unseen queries with zero leakage."
        ),
        6: (
            "[Speaker 2: Keith Hernandez | Target: 1:00]\n"
            "Before scaling, we ran a forensic audit across every local file and Google Drive deliverable, summarized on Slide 6. "
            "We resolved five concrete mismatches: Midterm unique stems corrected from 352 to the verified 426 stems (TTR 0.6827); "
            "semester corrected from 9 to 8 occurrences (1.28%), restoring year at Rank 19; Google Sheet Tab 1 replaced stale Prelim counts "
            "with verified Top 30 counts plus a live Finals Summary tab; two fabricated bigrams were removed from the portal leaving the 19 real "
            "recurring bigrams; and Doc #6 was unified everywhere to raw Freedom Wall ID #25604."
        ),
        7: (
            "[Speaker 2: Keith Hernandez | Target: 0:50]\n"
            "Slide 7 highlights Stage 2 deterministic text cleaning in scripts/data_cleaning.py. "
            "Naive regex previously stripped parenthesized acronyms like (SAMCIS) and (TOR), turned medical 'feeling ill' into 'feeling i will', "
            "and turned 'SLU's Registrar's Office' into 'slu is registrar is office'. Our hardened context-aware rules expand 'ill' only before modal verbs, "
            "strip possessive 's cleanly, normalize Taglish slang like dp and ngaun, and preserve Cordilleran hyphens such as dap-ay and man-obla. "
            "Passing to Earold Delin for morphology and our Track A CAR lexicon."
        ),
        8: (
            "[Speaker 3: Earold Delin | Target: 1:05]\n"
            "Thank you, Keith. Slide 8 examines Stage 3: our guarded bilingual and CAR morphological analyzer in scripts/car_morphology.py. "
            "On the left, unguarded affix rules historically mangled 'management' into 'nage', 'campus' into 'campu', 'magnify' into 'nify', "
            "and 'magician' into 'ician'. Curated PREFIX_EXCEPTIONS and English suffix guards (-tion, -ment, -ify, -ician, -ably) eliminate corruption completely. "
            "We also refined niche lemmatizers so 'honors' normalizes to 'honor' and 'permanently' to 'permanent'. On the right, authentic Filipino (magtanong -> tanong), "
            "Ilocano (agadal, panagadal -> adal; agpaagas -> agas), and Kankanaey (man-obla -> obla) inflections normalize reliably."
        ),
        9: (
            "[Speaker 3: Earold Delin | Target: 0:55]\n"
            "Slide 9 presents our verified Midterm Top 10 Bag of Words lexical profile across the 24 consolidated baseline documents. "
            "Across 624 filtered tokens and 426 unique stems, 'student' leads at 16 occurrences (2.56%), followed by 'slu' (10), 'examination' (9), "
            "and in coral-orange, our audited 'semester' count at exactly 8 (1.28%), followed by 'grade', 'requirement', and 'subject' at 7 each. "
            "Our 19 recurring institutional bigrams ('official transcript', 'qualifying examination', 'failure due') stay 100% synced across CLI, Sheet, and UI."
        ),
        10: (
            "[Speaker 3: Earold Delin | Target: 1:00]\n"
            f"Now let's examine Track A on Slide 10: our {m['lex_total']}-entry SLU and CAR Electronic Lexicon. "
            f"It comprises {m['lex_ilo']} Ilocano (ilo), {m['lex_kne']} Northern Kankanaey (kne), {m['lex_slu']} SLU institutional and Taglish terms, "
            f"and {m['lex_ibl']} Ibaloi (ibl) entries—recently enriched with academic honorifics, dropping/withdrawal roots, dean's list awards, "
            "and promissory notes such as karim/kari, panagikkat, and panagabak. Every entry separates Native_Aliases from Semantic_Aliases "
            "and follows Constantino, Rubino, Vanoverbergh, Ballard, and SIL Philippines—achieving 0.0% false-positive regional detections."
        ),
        11: (
            "[Speaker 3: Earold Delin | Target: 0:50]\n"
            "Slide 11 displays five representative rows from data/expanded/slu_car_domain_lexicon_v2.csv. "
            "Each record encodes Entry_ID, normalized lemma, ISO 639-3 tag, part of speech, morphological root and affix, English/Filipino glosses, "
            "separated alias columns, and intent mappings—from SLU academic acronyms like samcis and niche Handbook terms like summa_cum_laude, "
            "to Ilocano agadal (ag- + adal), Kankanaey inayan, Ibaloi tongtong mediation, and the distinctive Ibaloi sh- cognate shanom. "
            "I will now hand it over to Erick Sibayan for our balanced corpus and ML evaluation."
        ),
        12: (
            "[Speaker 4: Erick Sibayan | Target: 0:55]\n"
            f"Thank you, Earold. Slide 12 details our expanded {m['docs']}-document multi-layer corpus built for statistically sound 5-Fold Cross-Validation. "
            f"Every one of our {m['intents']} operational intent domains contains exactly {m['docs_per_class']} balanced documents and 5 to 6 official SLU policies. "
            f"Across registers, we cover {m['en_docs']} English, {m['tl_docs']} Taglish, and {m['car_docs']} Cordilleran code-switched utterances. "
            f"Every row preserves honest Source_Type provenance: {m['official_docs']} verified SLU policies, {m['uro_docs']} URO FAQs, {m['fw_docs']} #SLUFreedomWall posts, "
            f"and {m['curated_docs']} curated multilingual queries."
        ),
        13: (
            "[Speaker 4: Erick Sibayan | Target: 1:00]\n"
            "Slide 13 reports our pure-Python Supervised Intent Classification benchmarks under leak-free Stratified 5-Fold CV with fold-local "
            f"sublinear TF-IDF (1 + log tf). Look closely: after adopting sublinear TF scaling across our expanded {m['docs']}-doc dataset, "
            f"One-vs-Rest Linear SVM with Hinge Loss emerged as our Best Model at {m['svm_acc']:.2f}% accuracy and {m['svm_f1']:.2f}% Macro F1! "
            f"Multinomial Naive Bayes and L2 Logistic Regression both tied tightly at {m['nb_acc']:.2f}% accuracy and {m['nb_f1']:.2f}% Macro F1. "
            "Sublinear TF prevents repeated policy phrases from skewing decision margins between closely related Handbook sub-rules."
        ),
        14: (
            "[Speaker 4: Erick Sibayan | Target: 0:55]\n"
            f"Slide 14 shows the 10-by-10 out-of-fold confusion matrix for our winning Linear SVM classifier across all {m['docs']} documents. "
            f"Out of {m['docs']} unseen fold predictions, {m['svm_hits']} ({m['svm_acc']:.2f}%) sit cleanly on the green main diagonal, with both Shifting and Facilities & Labs "
            "achieving a spotless 35 out of 35, and Health, Exam Integrity, Grading/FDA, and Subject Adjustment scoring 34 out of 35! "
            "Only subtle cross-office ambiguities remain—such as tuition refund adjustments overlapping Finance and Subject Adjustment—which our hybrid policy ranker resolves cleanly."
        ),
        15: (
            "[Speaker 4: Erick Sibayan | Target: 1:00]\n"
            "Slide 15 shows how our hybrid ranking and ML upgrades work together inside slu_chatbot_engine.py. "
            "We paired sublinear TF-IDF cosine similarity and moderated lexicon intent boosting with probabilistic multi-intent ML routing—converting "
            "One-vs-Rest Linear SVM hinge margins via softmax so any candidate class above 0.16 receives calibrated support. "
            "For two-part questions using comparative markers like 'vs' or 'difference between', the engine synthesizes the primary and secondary policies together, "
            "reinforced by numeric and Handbook phrase anchors for 88/91/93 Latin honors, 11th MWF / 8th TTh absence ceilings, and OSAS Readmission Slips. "
            "Passing to John Andrew Angcaway for ablations and live niche demos."
        ),
        16: (
            "[Speaker 5: John Andrew Angcaway | Target: 1:00]\n"
            f"Thank you, Erick. Slide 16 reports our 4-stage ablation on {m['bench_total']} strictly unseen queries ({m['bench_in_domain']} in-domain plus "
            f"{m['bench_ood']} OOD traps and greetings, with zero training overlap). "
            f"Stage A raw TF-IDF starts at {m['abl_a']['top1_policy_accuracy']*100:.1f}% Top-1 and 0% OOD rejection. "
            f"Stage B cleaning and CAR morphology raises Top-1 to {m['abl_b']['top1_policy_accuracy']*100:.1f}% and {m['abl_b']['mrr']:.3f} MRR. "
            f"Stage C adds our {m['lex_total']}-entry lexicon and calibrated OOD gate—OOD rejection jumps immediately to {m['abl_c']['ood_rejection_rate']*100:.1f}% at {m['abl_c']['top1_policy_accuracy']*100:.1f}% Top-1. "
            f"Finally, Stage D fuses trained SVM routing, leaping +10.2 points to {m['abl_d']['top1_policy_accuracy']*100:.1f}% Top-1 (68/69), "
            f"{m['abl_d']['top3_policy_recall']*100:.1f}% Top-3 recall, {m['abl_d']['mrr']:.4f} MRR, 100% EN/Taglish, {m['abl_d']['by_register']['CAR-TL-EN']['top1_accuracy']*100:.1f}% CAR, and 0.0% false-positive CAR!"
        ),
        17: (
            "[Speaker 5: John Andrew Angcaway | Target: 1:00]\n"
            "Slide 17 covers production engineering in our redesigned Canva EAG-QJ6Vos4 graph-paper web portal. "
            "Security first: zero .innerHTML assignments across all dynamic views, safe textContent DOM nodes, strict CSP headers in netlify.toml, "
            "and verified defense against live XSS payloads. Second, single-source Py-to-JS parity: scripts/build_portal.py compiles the exact "
            f"{m['policies']} policies, {m['lex_total']} lexicon entries, and SVM/NB weights directly into JS, verified across all 78 test cases in Node.js and Python. "
            "Third, both Light Cream Graph Paper and Dark Neon-Glow modes preserve WCAG 2.1 AA contrast and full keyboard ARIA tablists."
        ),
        18: (
            "[Speaker 5: John Andrew Angcaway | Target: 0:55]\n"
            "Slides 18 and 19 showcase the exact high-demand niche SLU policies added to our engine. "
            "On Slide 18, Case 1 asks directly: 'What are the specific grades you need for Latin honors?' "
            "Our hybrid engine routes to HANDBOOK_GRADING_FDA Doc 133: Summa Cum Laude requires a GWA of 93% or higher with no grade below 85%; "
            "Magna Cum Laude requires 91.00% to 92.99% with no grade below 80%; and Cum Laude requires 88.00% to 90.99% with no grade below 78%—plus zero failures or drops and at least 75% residency at SLU. "
            "Case 2 asks: 'How many absences do I have before I become dropped vs. permanently dropped?' Comparative synthesis clearly separates voluntary official dropping (WP/DRP before finals, non-failing) "
            "from permanent Failure Due to Absences—exceeding 20% of 54 semester hours (11th absence on MWF or 8th on TTh)—plus the 3-consecutive-absence OSAS Readmission Slip."
        ),
        19: (
            "[Speaker 5: John Andrew Angcaway | Target: 0:55]\n"
            "Slide 19 continues with regional Cordilleran code-switching and out-of-domain safety. "
            "Case 3 tests Northern Kankanaey academic integrity: 'Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?' "
            "Our engine detects genuine native Kankanaey roots, replies 'Gawis ay agew!', and retrieves Article II Disciplinary Board sanctions—while an English-only plagiarism query suppresses regional greetings cleanly (0% FP-CAR). "
            "Case 4 demonstrates our OOD gate on 'Baguio strawberry sinigang', returning zero hallucination and guiding students to URO and OSAS contacts."
        ),
        20: (
            "[Speaker 5: John Andrew Angcaway | Target: 0:50]\n"
            "Slide 20 shares our honest provenance and RA 10173 Data Privacy compliance. "
            f"All {m['curated_docs']} synthetic utterances in annotated_corpus_expanded.csv are transparently tagged CURATED_MULTILINGUAL_INQUIRY rather than claiming they were live-scraped, "
            "and formal validation with native Ilocano, Northern Kankanaey, and Ibaloi speakers is Milestone 1 of our roadmap. "
            "For RA 10173 compliance, zero student names, IDs, or private identifiers are collected, and 100% client-side browser inference ensures student questions never leave their device. Back to Chaze!"
        ),
        21: (
            "[Speaker 1: Chaze Rodriguez | Target: 0:45]\n"
            "Thank you, John Andrew. Slide 21 outlines our three-step roadmap beyond CSE 30. "
            "Step 1 partners with native CAR linguists and SLU student organizations to validate idioms, diacritics, and expand toward Bontok and Ifugao. "
            "Step 2 benchmarks compact multilingual sentence embeddings like mE5 and LaBSE paired with strict Handbook-grounded RAG that never fabricates citations. "
            "Step 3 connects live iSLU enrollment calendars, OSAS advisories, and official URO ticketing queues."
        ),
        22: (
            "[Speaker 1: Chaze Rodriguez & All Members | Target: 0:45]\n"
            "To close on Slide 22: Group 2 AiNomally delivered an audited, security-hardened, Canva graph-paper SLU eGovernance ecosystem. "
            f"From {m['docs']} balanced documents, {m['policies']} verified SLU policies, and {m['lex_total']} CAR lexicon entries to {m['svm_f1']:.2f}% 5-Fold CV Macro F1, "
            f"{m['abl_d']['top1_policy_accuracy']*100:.1f}% unseen Top-1 accuracy, 100% OOD safety, and 22 passing automated tests across Python and Node.js—every claim is deterministically reproducible. "
            "Agyamanak! Iyaman! Dakel a iyaman! Scan the QR code to try the live portal, and we welcome your questions!"
        ),
    }


def hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class ClassroomTVDeckBuilder:
    """Simultaneously emits Google Slides batch JSON operations and builds a matching local .pptx."""

    def __init__(self):
        self.ops = [
            {"op": "delete-element", "element": "i0"},
            {"op": "delete-element", "element": "i1"},
        ]
        self.image_inserts = []  # (slide_placeholder_id, img_path, x, y, w, h)
        self.prs = Presentation()
        self.prs.slide_width = Pt(720)
        self.prs.slide_height = Pt(405)
        self.blank_layout = self.prs.slide_layouts[6]
        self.pptx_slides = {}
        self.slide_order = []

    def add_slide(self, slide_id, bg_hex=C_CREAM_BG, notes_text=""):
        if slide_id != "p":
            self.ops.append({"op": "add-slide", "layout": "BLANK", "id": slide_id})
        self.ops.append({"op": "set-background", "slide": slide_id, "color": bg_hex})
        if notes_text:
            self.ops.append({"op": "set-notes", "slide": slide_id, "text": notes_text})

        ps = self.prs.slides.add_slide(self.blank_layout)
        fill = ps.background.fill
        fill.solid()
        fill.fore_color.rgb = hex_to_rgb(bg_hex)
        if notes_text:
            ps.notes_slide.notes_text_frame.text = notes_text
        self.pptx_slides[slide_id] = ps
        self.slide_order.append(slide_id)

    def rect(self, slide_id, x, y, w, h, bg_hex, outline_hex=None, alpha=None, pptx_bg=None):
        op = {
            "op": "add-shape",
            "slide": slide_id,
            "shape_type": "RECTANGLE",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "background_color": bg_hex,
        }
        if alpha is not None:
            op["alpha"] = alpha
        self.ops.append(op)

        ps = self.pptx_slides[slide_id]
        shp = ps.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
        shp.fill.solid()
        shp.fill.fore_color.rgb = hex_to_rgb(pptx_bg or bg_hex)
        if outline_hex:
            shp.line.color.rgb = hex_to_rgb(outline_hex)
            shp.line.width = Pt(1.25)
        else:
            shp.line.fill.background()

    def circle(self, slide_id, x, y, d, bg_hex):
        self.ops.append({
            "op": "add-shape",
            "slide": slide_id,
            "shape_type": "ELLIPSE",
            "x": x, "y": y, "width": d, "height": d,
            "background_color": bg_hex,
        })
        ps = self.pptx_slides[slide_id]
        shp = ps.shapes.add_shape(MSO_SHAPE.OVAL, Pt(x), Pt(y), Pt(d), Pt(d))
        shp.fill.solid()
        shp.fill.fore_color.rgb = hex_to_rgb(bg_hex)
        shp.line.fill.background()

    def graph_grid(self, slide_id, grid_hex, alpha=0.55):
        """Draw Canva-style 60pt engineering graph-paper grid lines cleanly using hairline rects."""
        for gx in range(60, 720, 60):
            self.rect(slide_id, gx, 0, 0.75, 405, grid_hex, alpha=alpha, pptx_bg=grid_hex)
        for gy in range(60, 405, 60):
            self.rect(slide_id, 0, gy, 720, 0.75, grid_hex, alpha=alpha, pptx_bg=grid_hex)

    def dark_neon_aura(self, slide_id):
        """Top magenta-pink-violet Canva EAG-QJ6Vos4 neon aura glow + subtle bottom coral wash."""
        self.rect(slide_id, 0, 0, 720, 44, C_AURA_PURPLE, alpha=0.22, pptx_bg="#26133B")
        self.rect(slide_id, 0, 0, 720, 24, C_MAGENTA, alpha=0.28, pptx_bg="#491746")
        self.rect(slide_id, 0, 0, 720, 10, C_AURA_LIGHT, alpha=0.36, pptx_bg="#782765")
        self.rect(slide_id, 520, 365, 200, 40, C_CORAL, alpha=0.14, pptx_bg="#2B151D")

    def textbox(
        self,
        slide_id,
        text,
        x,
        y,
        w,
        h,
        font_size=15,
        bold=False,
        italic=False,
        color=C_INK,
        bg_hex=None,
        align="left",
        valign="TOP",
        line_spacing=128,
        font_family="Roboto",
    ):
        op = {
            "op": "add-textbox",
            "slide": slide_id,
            "text": text,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "font_size": font_size,
            "bold": bold,
            "italic": italic,
            "color": color,
            "font_family": font_family,
            "alignment": align,
            "content_alignment": valign,
            "line_spacing": line_spacing,
        }
        if bg_hex:
            op["background_color"] = bg_hex
        self.ops.append(op)

        ps = self.pptx_slides[slide_id]
        tb = ps.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
        if bg_hex:
            tb.fill.solid()
            tb.fill.fore_color.rgb = hex_to_rgb(bg_hex)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Pt(7)
        tf.margin_right = Pt(7)
        tf.margin_top = Pt(4)
        tf.margin_bottom = Pt(4)
        tf.vertical_anchor = (
            MSO_ANCHOR.MIDDLE if valign == "MIDDLE" else (MSO_ANCHOR.BOTTOM if valign == "BOTTOM" else MSO_ANCHOR.TOP)
        )
        p_align = PP_ALIGN.CENTER if align == "center" else (PP_ALIGN.RIGHT if align == "right" else PP_ALIGN.LEFT)
        pptx_font = "Courier New" if font_family == "Roboto Mono" else "Arial"
        for idx, ln in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.alignment = p_align
            p.line_spacing = line_spacing / 100.0
            run = p.add_run()
            run.text = ln
            run.font.name = pptx_font
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = hex_to_rgb(color)

    def light_chrome(self, slide_id, slide_num, title, speaker_label):
        """Canva EAG-QJ6Vos4 Light Paper Grid + macOS Chrome Window Bar + crisp footer."""
        self.graph_grid(slide_id, C_PAPER_GRID, alpha=0.65)
        self.rect(slide_id, 0, 0, 720, 48, C_CHROME_BAR)
        self.rect(slide_id, 0, 48, 720, 2, C_INK)
        self.circle(slide_id, 18, 19, 10, C_DOT_RED)
        self.circle(slide_id, 34, 19, 10, C_DOT_YELLOW)
        self.circle(slide_id, 50, 19, 10, C_DOT_GREEN)
        # Centered white macOS address bar pill containing large crisp title
        self.textbox(
            slide_id, title,
            76, 7, 558, 34,
            font_size=20, bold=True, color=C_INK, bg_hex=C_WHITE, align="center", valign="MIDDLE",
        )
        # Slide index pill on right
        self.textbox(
            slide_id, f"{slide_num:02d}/{TOTAL_SLIDES}",
            642, 7, 62, 34,
            font_size=14, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE", font_family="Roboto Mono",
        )
        # Minimal high-contrast footer
        self.rect(slide_id, 0, 383, 720, 22, C_WHITE)
        self.rect(slide_id, 0, 382, 720, 1.5, C_INK)
        self.textbox(
            slide_id,
            "SLU SAMCIS  •  CSE 30 NLP  •  GROUP 2 AINOMALLY",
            20, 383, 415, 21, font_size=10.5, bold=True, color=C_MUTED, valign="MIDDLE", font_family="Roboto Mono",
        )
        self.textbox(
            slide_id,
            speaker_label,
            440, 383, 260, 21, font_size=11, bold=True, color=C_INK, align="right", valign="MIDDLE",
        )

    def dark_chrome(self, slide_id, slide_num, title, speaker_label):
        """Canva EAG-QJ6Vos4 Dark Obsidian Grid + Magenta Aura header + coral badge."""
        self.dark_neon_aura(slide_id)
        self.graph_grid(slide_id, C_DARK_GRID, alpha=0.80)
        self.textbox(
            slide_id, f"{slide_num:02d} / {TOTAL_SLIDES}",
            612, 14, 86, 28,
            font_size=13, bold=True, color=C_WHITE, bg_hex=C_CORAL, align="center", valign="MIDDLE", font_family="Roboto Mono",
        )
        self.textbox(
            slide_id, title,
            24, 14, 570, 44,
            font_size=23, bold=True, color=C_WHITE, valign="MIDDLE",
        )
        self.rect(slide_id, 24, 60, 110, 3, C_CORAL)
        self.textbox(
            slide_id,
            "SLU SAMCIS  •  CSE 30 NLP  •  GROUP 2 AINOMALLY",
            24, 383, 415, 20, font_size=10.5, bold=True, color=C_LIGHT_MUTED, valign="MIDDLE", font_family="Roboto Mono",
        )
        self.textbox(
            slide_id,
            speaker_label,
            440, 383, 256, 20, font_size=11, bold=True, color=C_CORAL, align="right", valign="MIDDLE",
        )

    def card(
        self,
        slide_id,
        x, y, w, h,
        title, body,
        header_bg=C_INK,
        title_color=C_WHITE,
        title_size=16,
        header_h=34,
        body_size=15,
        line_spacing=132,
        body_bold=False,
        dark_mode=False,
    ):
        card_bg = C_DARK_CARD if dark_mode else C_WHITE
        border_col = C_DARK_BORDER if dark_mode else C_INK
        text_col = C_WHITE if dark_mode else C_INK
        self.rect(slide_id, x, y, w, h, card_bg, outline_hex=border_col)
        # Crisp tactile 1.5pt border lines in Google Slides (which omits outline on add-shape)
        self.rect(slide_id, x, y, w, 1.5, border_col)
        self.rect(slide_id, x, y + h - 1.5, w, 1.5, border_col)
        self.rect(slide_id, x, y, 1.5, h, border_col)
        self.rect(slide_id, x + w - 1.5, y, 1.5, h, border_col)
        self.textbox(slide_id, title, x + 1, y + 1, w - 2, header_h, font_size=title_size, bold=True, color=title_color, bg_hex=header_bg, valign="MIDDLE")
        self.textbox(
            slide_id, body,
            x + 8, y + header_h + 7, w - 16, h - header_h - 12,
            font_size=body_size, bold=body_bold, color=text_col, line_spacing=line_spacing,
        )

    def arrow(self, slide_id, x, y, width, color=C_CORAL):
        self.ops.append({
            "op": "add-line",
            "slide": slide_id,
            "line_category": "STRAIGHT",
            "x": x, "y": y, "width": width, "height": 0,
            "color": color, "line_weight": 2.6, "end_arrow": "FILL_ARROW",
        })
        ps = self.pptx_slides[slide_id]
        shp = ps.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Pt(x), Pt(y - 5), Pt(width), Pt(10))
        shp.fill.solid()
        shp.fill.fore_color.rgb = hex_to_rgb(color)
        shp.line.fill.background()

    def stat_card(self, slide_id, x, y, w, h, num, label, bg=C_DARK_CARD, num_col=C_CORAL, num_size=34, lbl_size=13.5):
        self.rect(slide_id, x, y, w, h, bg, outline_hex=C_CORAL)
        self.rect(slide_id, x, y + h - 4, w, 4, C_CORAL)
        self.rect(slide_id, x, y, w, 1.5, C_DARK_BORDER)
        self.textbox(slide_id, num, x + 4, y + 8, w - 8, int(h * 0.54), font_size=num_size, bold=True, color=num_col, align="center", valign="MIDDLE")
        self.textbox(slide_id, label, x + 6, y + int(h * 0.54), w - 12, int(h * 0.40), font_size=lbl_size, bold=True, color=C_WHITE, align="center", valign="TOP", line_spacing=118)

    def table(self, slide_id, table_id, x, y, w, h, data, font_size=14, header_bg=C_INK, col_widths=None):
        rows, cols = len(data), len(data[0])
        self.ops.append({"op": "add-table", "slide": slide_id, "rows": rows, "cols": cols, "id": table_id, "x": x, "y": y, "width": w, "height": h})
        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                is_hdr = r_idx == 0
                bg = header_bg if is_hdr else (C_WHITE if r_idx % 2 == 1 else C_ROW_ALT)
                fg = C_WHITE if is_hdr else C_INK
                self.ops.append({
                    "op": "set-table-cell",
                    "table": table_id,
                    "row": r_idx,
                    "col": c_idx,
                    "text": str(val),
                    "font_size": font_size,
                    "bold": is_hdr or c_idx == 0,
                    "color": fg,
                    "background_color": bg,
                    "font_family": "Roboto",
                })
        if col_widths:
            for c_idx, cw in enumerate(col_widths):
                self.ops.append({
                    "op": "updateTableColumnProperties",
                    "updateTableColumnProperties": {
                        "objectId": table_id,
                        "columnIndices": [c_idx],
                        "tableColumnProperties": {"columnWidth": {"magnitude": cw, "unit": "PT"}},
                        "fields": "columnWidth",
                    },
                })

        ps = self.pptx_slides[slide_id]
        tbl_shp = ps.shapes.add_table(rows, cols, Pt(x), Pt(y), Pt(w), Pt(h))
        tbl = tbl_shp.table
        if col_widths:
            for c_idx, cw in enumerate(col_widths):
                tbl.columns[c_idx].width = Pt(cw)
        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                cell = tbl.cell(r_idx, c_idx)
                is_hdr = r_idx == 0
                cell.fill.solid()
                cell.fill.fore_color.rgb = hex_to_rgb(header_bg if is_hdr else (C_WHITE if r_idx % 2 == 1 else C_ROW_ALT))
                cell.text = str(val)
                for p in cell.text_frame.paragraphs:
                    for run in p.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(font_size)
                        run.font.bold = is_hdr or c_idx == 0
                        run.font.color.rgb = hex_to_rgb(C_WHITE if is_hdr else C_INK)

    def image(self, slide_id, img_path, x, y, w, h):
        self.image_inserts.append((slide_id, img_path, x, y, w, h))
        ps = self.pptx_slides[slide_id]
        ps.shapes.add_picture(img_path, Pt(x), Pt(y), width=Pt(w), height=Pt(h))


def build_deck_content(b, m, notes):
    # ==================== SLIDE 1: TITLE (DARK NEON-GLOW GRID HERO) ====================
    b.add_slide("p", C_DARK_BG, notes[1])
    b.dark_neon_aura("p")
    b.graph_grid("p", C_DARK_GRID, alpha=0.82)
    b.textbox(
        "p", "SAINT LOUIS UNIVERSITY  •  BAGUIO CITY  •  SAMCIS",
        30, 32, 660, 26, font_size=13.5, bold=True, color=C_AURA_LIGHT, align="center", valign="MIDDLE", font_family="Roboto Mono",
    )
    b.textbox(
        "p", "SLU eGovernance Chatbot\n& CAR Electronic Lexicon",
        30, 68, 660, 114, font_size=38, bold=True, color=C_WHITE, align="center", valign="MIDDLE", line_spacing=110,
    )
    b.textbox(
        "p",
        f"{m['policies']} Verified SLU Policies (Honors & Drop/FDA)  •  {m['lex_total']}-Entry CAR Lexicon  •  {m['svm_f1']:.2f}% 5-Fold SVM",
        20, 188, 680, 38, font_size=13.5, color=C_LIGHT_MUTED, align="center", valign="MIDDLE", line_spacing=118,
    )
    b.rect("p", 260, 240, 200, 3, C_CORAL)
    b.textbox(
        "p", "GROUP 2 – AINOMALLY   →",
        220, 252, 280, 34, font_size=16, bold=True, color=C_WHITE, bg_hex=C_CORAL, align="center", valign="MIDDLE", font_family="Roboto Mono",
    )
    b.textbox(
        "p", "John Andrew Angcaway  •  Earold Jan Delin  •  Keith Russel Hernandez\nChaze Ezkys M. Rodriguez  •  Erick James Sibayan",
        30, 294, 660, 48, font_size=14.5, bold=True, color=C_WHITE, align="center", valign="MIDDLE", line_spacing=130,
    )
    b.textbox(
        "p", "CSE 30 (Natural Language Processing)   |   Class 9712   |   Prof. Dalos D. Miguel",
        30, 352, 660, 26, font_size=13, color=C_LIGHT_MUTED, align="center", valign="MIDDLE", font_family="Roboto Mono",
    )

    # ==================== SLIDE 2: THE PROBLEM (LIGHT PAPER GRID) ====================
    b.add_slide("S02", C_CREAM_BG, notes[2])
    b.light_chrome("S02", 2, "Why SLU Needs a CAR-Aware Chatbot", "Speaker: Chaze Rodriguez")
    b.card(
        "S02", 24, 68, 326, 224,
        "1. Niche Policy Bottlenecks",
        "• Honors cutoffs & drop vs. FDA rules split\n"
        "• Urgent Taglish queries on #SLUFreedomWall\n"
        "• Keyword search fails on SAMCIS, dp, QE, FDA",
        header_bg=C_INK, title_size=16, body_size=15, line_spacing=148,
    )
    b.card(
        "S02", 370, 68, 326, 224,
        "2. CAR Language Resource Gap",
        "• Baguio hosts Ilocano, Kankanaey & Ibaloi\n"
        "• Affixes (ag-, panag-, man-) break English NLP\n"
        "• Cultural terms (inayan, dap-ay) ignored",
        header_bg=C_VIOLET, title_size=16, body_size=15, line_spacing=148,
    )
    b.textbox(
        "S02",
        f"THESIS: Unify {m['policies']} verified SLU policies with a {m['lex_total']}-entry CAR lexicon in one fast assistant.",
        24, 306, 672, 60, font_size=15, bold=True, color=C_WHITE, bg_hex=C_CORAL, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 3: TRACKS & OBJECTIVES (DARK NEON GRID) ====================
    b.add_slide("S03", C_DARK_BG, notes[3])
    b.dark_chrome("S03", 3, "Dual CSE 30 Tracks & Core Objectives", "Speaker: Chaze Rodriguez")
    b.card(
        "S03", 24, 74, 326, 114,
        "Track A • CAR Electronic Lexicon",
        f"{m['lex_total']} verified SLU, Ilocano, Kankanaey & Ibaloi entries with roots, affixes & glosses.",
        header_bg=C_VIOLET, title_size=16, header_h=34, body_size=14.5, line_spacing=128, dark_mode=True,
    )
    b.card(
        "S03", 370, 74, 326, 114,
        "Track B • SLU eGovernance Chatbot",
        f"{m['policies']} verified SLU policies across {m['intents']} domains via Hybrid TF-IDF + Linear SVM.",
        header_bg=C_MAGENTA, title_size=16, header_h=34, body_size=14.5, line_spacing=128, dark_mode=True,
    )
    objs = [
        ("1. Reproducible", "One command\n(build_all.py)\n0 Drive drift", C_DARK_CARD_ALT),
        ("2. Hardened", "TDD fixes for\nCAR, OOD &\nZero XSS", C_VIOLET),
        ("3. Balanced", f"{m['docs']} docs\n({m['docs_per_class']} / intent)\n{m['policies']} SLU rules", C_TEAL),
        ("4. Rigorous", f"5-Fold CV\nSVM / NB / LR\n{m['bench_total']} unseen tests", C_CORAL),
    ]
    for idx, (ot, ob, col) in enumerate(objs):
        ox = 24 + idx * 171
        b.card("S03", ox, 202, 159, 166, ot, ob, header_bg=col, title_size=15, header_h=34, body_size=14.5, line_spacing=134, dark_mode=True)

    # ==================== SLIDE 4: 5-STAGE ARCHITECTURE (LIGHT PAPER GRID) ====================
    b.add_slide("S04", C_CREAM_BG, notes[4])
    b.light_chrome("S04", 4, "5-Stage Reproducible NLP Architecture", "Speaker: Keith Hernandez")
    stages = [
        ("Stage 1\nAcquire", f"• 8 FW posts\n• {m['policies']} SLU rules\n• Honors & FDA\n• URO & OSAS", C_INK),
        ("Stage 2\nClean", "• Keep SAMCIS\n• Fix 'ill' & 's\n• Taglish slang\n• CAR hyphens", C_VIOLET),
        ("Stage 3\nMorph", "• 265 stopwords\n• Safe English\n• CAR affixes\n• 19 Bigrams", C_TEAL),
        ("Stage 4\nML Core", f"• 5-Fold SVM\n• {m['lex_total']} Lexicon\n• Comparatives\n• OOD Gate", C_INK),
        ("Stage 5\nPortal", "• Canva Web UI\n• Zero XSS\n• Py↔JS Parity\n• WCAG 2.1 AA", C_CORAL),
    ]
    for idx, (st_hdr, st_body, col) in enumerate(stages):
        sx = 20 + idx * 138
        b.rect("S04", sx, 68, 126, 224, C_WHITE, outline_hex=C_INK)
        b.rect("S04", sx, 68, 126, 1.5, C_INK)
        b.rect("S04", sx, 290.5, 126, 1.5, C_INK)
        b.textbox("S04", st_hdr, sx, 68, 126, 48, font_size=14, bold=True, color=C_WHITE, bg_hex=col, align="center", valign="MIDDLE", line_spacing=112)
        b.textbox("S04", st_body, sx + 4, 124, 118, 162, font_size=14, bold=True, color=C_INK, line_spacing=142)
        if idx < 4:
            b.arrow("S04", sx + 127, 178, 8, color=C_CORAL)
    b.textbox(
        "S04",
        "ZERO EXTERNAL ML PACKAGES: Pure Python 3.14 + JSON weights • 22 / 22 automated tests passing.",
        20, 306, 680, 60, font_size=14.5, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 5: SCALING CHART (LIGHT PAPER GRID) ====================
    b.add_slide("S05", C_CREAM_BG, notes[5])
    b.light_chrome("S05", 5, "Corpus & Lexicon Scaling (Midterm → Finals)", "Speaker: Keith Hernandez")
    b.image("S05", os.path.join(CHARTS_DIR, "tv_02_corpus_scaling.png"), 64, 58, 592, 272)
    b.textbox(
        "S05",
        f"Every intent has {m['docs_per_class']} balanced docs and 5–6 verified policies ({m['policies']} total).",
        24, 336, 672, 38, font_size=14.5, bold=True, color=C_WHITE, bg_hex=C_VIOLET, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 6: DATA AUDIT (LIGHT PAPER GRID) ====================
    b.add_slide("S06", C_CREAM_BG, notes[6])
    b.light_chrome("S06", 6, "End-to-End Audit: Five Discrepancies Fixed", "Speaker: Keith Hernandez")
    b.table("S06", "TBL_AUDIT", 24, 66, 672, 250, [
        ["Audit Finding", "Legacy Error (Before)", "Verified Fix (After)"],
        ["Unique Stems", "352 stems (TTR 0.56)", "426 stems (TTR 0.6827)"],
        ["BoW Counts", "semester = 9; year lost", "semester = 8; year = 4 (#19)"],
        ["Google Sheet", "Old Prelim (like = 12)", "Synced Top 30 + Finals Tab 2"],
        ["Bigram List", "2 fabricated bigrams", "19 verified bigrams (freq = 2)"],
        ["Doc #6 ID", "Mismatched #25582", "Unified #25604 everywhere"],
    ], font_size=14, col_widths=[172, 232, 268])
    b.textbox(
        "S06",
        "Verification Gate: test_pipeline.py reproduces cleaned_corpus.txt with 0 line diffs.",
        24, 326, 672, 44, font_size=14.5, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 7: STAGE 2 TEXT CLEANING (LIGHT PAPER GRID) ====================
    b.add_slide("S07", C_CREAM_BG, notes[7])
    b.light_chrome("S07", 7, "Stage 2: Hardened Acronym-Safe Cleaning", "Speaker: Keith Hernandez")
    b.table("S07", "TBL_CLEAN", 24, 66, 672, 248, [
        ["Cleaning Rule", "Raw Student / Policy Input", "Hardened Clean Output"],
        ["Acronyms", "[#SLUFW25604] (SAMCIS) (TOR)", "samcis tor (intact!)"],
        ["Context 'ill'", "feeling ill  /  ill answer", "feeling ill  /  i will answer"],
        ["Possessive 's", "SLU's Registrar's Office", "slu registrar office"],
        ["Taglish & CAR", "dp? ngaun? dap-ay man-obla", "downpayment ngayon dap-ay"],
    ], font_size=14, col_widths=[152, 266, 254])
    b.textbox(
        "S07",
        "Protects SLU acronyms, punctuation polarity & CAR hyphens with 0 Midterm drift.",
        24, 324, 672, 46, font_size=14.5, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 8: STAGE 3 CAR MORPHOLOGY (LIGHT PAPER GRID) ====================
    b.add_slide("S08", C_CREAM_BG, notes[8])
    b.light_chrome("S08", 8, "Stage 3: Guarded CAR Morphological Analysis", "Speaker: Earold Delin")
    b.card(
        "S08", 24, 66, 326, 302,
        "Blocked Over-Stemming",
        "Naive errors eliminated:\n"
        "• management → NOT nage\n"
        "• campus → NOT campu\n"
        "• magnify / magician → safe!\n\n"
        "Niche fixes: honors→honor, permanently→permanent via PREFIX_EXCEPTIONS.",
        header_bg=C_RED_FG, title_size=16, header_h=36, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S08", 370, 66, 326, 302,
        "Normalized CAR & Taglish",
        "Filipino / Taglish:\n"
        "• magtanong / tinanong → tanong\n"
        "• tumataas → taas\n\n"
        "Ilocano / Kankanaey / Ibaloi:\n"
        "• agadal / panagadal → adal\n"
        "• man-obla / men-obla → obla\n"
        "• agpaagas → agas",
        header_bg=C_TEAL, title_size=16, header_h=36, body_size=14.5, line_spacing=128,
    )

    # ==================== SLIDE 9: MIDTERM BOW TOP 10 CHART (LIGHT PAPER GRID) ====================
    b.add_slide("S09", C_CREAM_BG, notes[9])
    b.light_chrome("S09", 9, "Verified Midterm Top 10 Bag of Words Stems", "Speaker: Earold Delin")
    b.image("S09", os.path.join(CHARTS_DIR, "tv_01_bow_top10.png"), 64, 58, 592, 272)
    b.textbox(
        "S09",
        "624 filtered tokens  •  426 unique stems  •  19 verified bigrams (official transcript, failure due)",
        24, 336, 672, 38, font_size=14.5, bold=True, color=C_WHITE, bg_hex=C_CORAL, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 10: TRACK A LEXICON OVERVIEW (DARK NEON GRID) ====================
    b.add_slide("S10", C_DARK_BG, notes[10])
    b.dark_chrome("S10", 10, f"Track A: {m['lex_total']}-Entry SLU & CAR Lexicon", "Speaker: Earold Delin")
    b.stat_card("S10", 24, 74, 159, 142, str(m["lex_ilo"]), "Ilocano\n(ISO: ilo)", bg=C_DARK_CARD_ALT, num_col=C_VIOLET_BRIGHT, num_size=40, lbl_size=14)
    b.stat_card("S10", 195, 74, 159, 142, str(m["lex_kne"]), "Kankanaey\n(ISO: kne)", bg=C_DARK_CARD_ALT, num_col=C_AURA_LIGHT, num_size=40, lbl_size=14)
    b.stat_card("S10", 366, 74, 159, 142, str(m["lex_slu"]), "SLU & Taglish\n(en / tl-SLU)", bg=C_DARK_CARD_ALT, num_col=C_CORAL, num_size=40, lbl_size=14)
    b.stat_card("S10", 537, 74, 159, 142, str(m["lex_ibl"]), "Ibaloi\n(ISO: ibl)", bg=C_DARK_CARD_ALT, num_col=C_GOLD_BRIGHT, num_size=40, lbl_size=14)

    b.card(
        "S10", 24, 230, 326, 138,
        "Cognates & Honors / Drop Roots",
        "• danum (ilo) • danom (kne) • shanom (ibl)\n"
        "• Honors/Drop: karim, panagikkat, inayan",
        header_bg=C_VIOLET, title_size=15.5, header_h=34, body_size=14.5, line_spacing=140, dark_mode=True,
    )
    b.card(
        "S10", 370, 230, 326, 138,
        "0.0% False-Positive Safeguard",
        "• Native_Aliases vs. Semantic_Aliases split\n"
        "• Verified: Rubino, Vanoverbergh & Ballard",
        header_bg=C_GREEN_FG, title_size=15.5, header_h=34, body_size=14.5, line_spacing=140, dark_mode=True,
    )

    # ==================== SLIDE 11: LEXICON SAMPLES TABLE (LIGHT PAPER GRID) ====================
    b.add_slide("S11", C_CREAM_BG, notes[11])
    b.light_chrome("S11", 11, "Authentic SLU & CAR Lexicon Samples", "Speaker: Earold Delin")
    b.table("S11", "TBL_LEX", 24, 66, 672, 254, [
        ["Lemma", "ISO", "Root / Affix", "Institutional / Regional Gloss"],
        ["samcis", "en-SLU", "Acronym", "School of Accountancy, Mgmt. & Computing"],
        ["agadal", "ilo", "adal (ag-)", "To study; pursue university coursework"],
        ["inayan", "kne", "Root", "Ethical restraint vs. academic dishonesty"],
        ["tongtong", "ibl", "Root", "Customary mediation & disciplinary council"],
        ["karim", "ilo", "Root (Loan)", "Academic honors merit; promissory pledge"],
    ], font_size=14, col_widths=[108, 76, 136, 352])
    b.textbox(
        "S11",
        "CSV Schema: Entry_ID, Lemma, ISO, POS, Root, Affix, EN/FIL Gloss, Native vs. Semantic Aliases.",
        24, 330, 672, 40, font_size=14, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 12: 350-DOC CORPUS & 10 INTENTS (LIGHT PAPER GRID) ====================
    b.add_slide("S12", C_CREAM_BG, notes[12])
    b.light_chrome("S12", 12, f"{m['docs']}-Doc Balanced Corpus & {m['intents']} Intents", "Speaker: Erick Sibayan")
    b.textbox("S12", f"{m['docs']} Docs  •  {m['docs_per_class']} / Class", 24, 64, 214, 46, font_size=15.5, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE")
    b.textbox("S12", f"{m['en_docs']} EN • {m['tl_docs']} TL • {m['car_docs']} CAR", 253, 64, 214, 46, font_size=15.5, bold=True, color=C_WHITE, bg_hex=C_VIOLET, align="center", valign="MIDDLE")
    b.textbox("S12", f"{m['policies']} Official SLU Policies", 482, 64, 214, 46, font_size=15.5, bold=True, color=C_WHITE, bg_hex=C_CORAL, align="center", valign="MIDDLE")

    left_intents = [
        "1. TOR, COG & Dismissal (5 pol)",
        "2. iSLU Portal & Enrollment (5 pol)",
        "3. Add / Drop & Petitions (5 pol)",
        "4. Shifting & Qualifying Exam (6 pol)",
        "5. Honors, 75% & 20% FDA (6 pol)",
    ]
    right_intents = [
        "6. Exam Permit & Integrity (5 pol)",
        "7. Uniform, Org & Decorum (5 pol)",
        "8. Clinic, CCW, Seismic & DPA (5 pol)",
        "9. Tuition, Promissory & Grants (5 pol)",
        "10. UNL Library, Labs & Wifi (5 pol)",
    ]
    for i, txt in enumerate(left_intents):
        py = 124 + i * 40
        b.rect("S12", 24, py, 7, 34, C_INK)
        b.textbox("S12", txt, 31, py, 321, 34, font_size=14, bold=True, color=C_INK, bg_hex=C_WHITE, valign="MIDDLE")
    for i, txt in enumerate(right_intents):
        py = 124 + i * 40
        b.rect("S12", 368, py, 7, 34, C_VIOLET)
        b.textbox("S12", txt, 375, py, 321, 34, font_size=14, bold=True, color=C_INK, bg_hex=C_WHITE, valign="MIDDLE")

    b.textbox(
        "S12",
        f"Source Provenance:  {m['official_docs']} Official Policies  •  {m['uro_docs'] + m['fw_docs']} Harvested/URO  •  {m['curated_docs']} Curated Multilingual",
        24, 332, 672, 38, font_size=14.5, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 13: 5-FOLD CV BENCHMARK CHART (DARK NEON GRID) ====================
    b.add_slide("S13", C_DARK_BG, notes[13])
    b.dark_chrome("S13", 13, f"Supervised 5-Fold CV Benchmarks (N = {m['docs']})", "Speaker: Erick Sibayan")
    b.rect("S13", 58, 66, 604, 232, C_CREAM_BG, outline_hex=C_MAGENTA)
    b.image("S13", os.path.join(CHARTS_DIR, "tv_03_cv_comparison.png"), 64, 70, 592, 224)
    b.stat_card("S13", 24, 304, 214, 70, f"{m['svm_f1']:.2f}%", f"Linear SVM ★ (±{m['svm_std']:.2f}%)", bg=C_DARK_CARD_ALT, num_col=C_CORAL, num_size=26, lbl_size=12.5)
    b.stat_card("S13", 253, 304, 214, 70, f"{m['nb_f1']:.2f}%", f"Multinomial NB (±{m['nb_std']:.2f}%)", bg=C_DARK_CARD_ALT, num_col=C_AURA_LIGHT, num_size=26, lbl_size=12.5)
    b.stat_card("S13", 482, 304, 214, 70, f"{m['lr_f1']:.2f}%", f"Logistic Reg. (±{m['lr_std']:.2f}%)", bg=C_DARK_CARD_ALT, num_col=C_VIOLET_BRIGHT, num_size=26, lbl_size=12.5)

    # ==================== SLIDE 14: 10x10 CONFUSION MATRIX (LIGHT PAPER GRID) ====================
    b.add_slide("S14", C_CREAM_BG, notes[14])
    b.light_chrome("S14", 14, "10×10 Confusion Matrix (Linear SVM ★)", "Speaker: Erick Sibayan")
    b.image("S14", os.path.join(CHARTS_DIR, "tv_04_confusion_matrix.png"), 64, 58, 592, 272)
    b.textbox(
        "S14",
        f"{m['svm_hits']} / {m['docs']} Exact Hits ({m['svm_acc']:.2f}%)  •  100% Perfect: SHIFTING & LABS (35 / 35)",
        24, 336, 672, 38, font_size=14.5, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 15: HYBRID SCORING & NICHE UPGRADES (LIGHT PAPER GRID) ====================
    b.add_slide("S15", C_CREAM_BG, notes[15])
    b.light_chrome("S15", 15, "Hybrid Ranker & Comparative ML Upgrades", "Speaker: Erick Sibayan")
    b.textbox(
        "S15",
        "Score  =  Sublinear TF-IDF  +  Lexicon Boost  +  0.34·P_SVM(intent)  +  Niche Anchors",
        24, 64, 672, 42, font_size=14.5, bold=True, color=C_WHITE, bg_hex=C_INK, align="center", valign="MIDDLE",
    )
    b.card(
        "S15", 24, 118, 326, 120,
        "1. Probabilistic SVM Routing",
        "Softmax on Linear SVM margins enables multi-intent boosts whenever P(intent) ≥ 0.16.",
        header_bg=C_VIOLET, title_size=15.5, header_h=34, body_size=14.5, line_spacing=128,
    )
    b.card(
        "S15", 370, 118, 326, 120,
        "2. Comparative Synthesis",
        "Detects 'vs' & 'difference between' queries to fuse primary + secondary SLU rules.",
        header_bg=C_CORAL, title_size=15.5, header_h=34, body_size=14.5, line_spacing=128,
    )
    b.card(
        "S15", 24, 248, 326, 120,
        "3. Niche Handbook Anchors",
        "Pinpoints 88/91/93 Latin Honors, 11th MWF / 8th TTh FDA & 3-consec OSAS Readmission Slip.",
        header_bg=C_TEAL, title_size=15.5, header_h=34, body_size=14.5, line_spacing=128,
    )
    b.card(
        "S15", 370, 248, 326, 120,
        "4. Strong OOD + CAR Guard",
        "Native_Aliases suppress false CAR greetings (0%); gibberish hits OUT_OF_DOMAIN (100%).",
        header_bg=C_INK, title_size=15.5, header_h=34, body_size=14.5, line_spacing=128,
    )

    # ==================== SLIDE 16: 4-STAGE ABLATION STUDY (DARK NEON GRID) ====================
    b.add_slide("S16", C_DARK_BG, notes[16])
    b.dark_chrome("S16", 16, f"4-Stage Held-Out Ablation ({m['bench_total']} Unseen)", "Speaker: John Andrew Angcaway")
    b.rect("S16", 58, 66, 604, 268, C_CREAM_BG, outline_hex=C_CORAL)
    b.image("S16", os.path.join(CHARTS_DIR, "tv_05_ablation.png"), 64, 70, 592, 260)
    reg = m["abl_d"]["by_register"]
    b.textbox(
        "S16",
        f"Full Hybrid (D): {m['abl_d']['top1_policy_accuracy']*100:.1f}% Top-1 ({m['abl_d']['mrr']:.4f} MRR)  •  EN {reg['EN']['top1_accuracy']*100:.1f}%  •  TL {reg['TL-EN']['top1_accuracy']*100:.1f}%  •  CAR {reg['CAR-TL-EN']['top1_accuracy']*100:.1f}%",
        24, 340, 672, 34, font_size=14, bold=True, color=C_WHITE, bg_hex=C_CORAL, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 17: SECURITY, PARITY & WCAG UI (LIGHT PAPER GRID) ====================
    b.add_slide("S17", C_CREAM_BG, notes[17])
    b.light_chrome("S17", 17, "Security, Py↔JS Parity & Canva UI", "Speaker: John Andrew Angcaway")
    b.card(
        "S17", 24, 68, 214, 300,
        "Zero XSS Defense",
        "• Zero .innerHTML calls\n\n• Safe textContent DOM\n\n• Strict CSP + Netlify headers\n\n• Passed <img onerror> test",
        header_bg=C_RED_FG, title_size=16, header_h=36, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S17", 253, 68, 214, 300,
        "100% Py↔JS Parity",
        "• Single build_portal.py\n\n• Same SVM/NB weights\n\n• Verified via Node.js\n\n• 78 / 78 identical outputs",
        header_bg=C_INK, title_size=16, header_h=36, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S17", 482, 68, 214, 300,
        "Canva Paper + Dark UI",
        "• Cream Grid & Neon Glow\n\n• ≥ 4.5:1 WCAG AA ratio\n\n• Live 6-stage inspector\n\n• Keyboard ARIA tablist",
        header_bg=C_VIOLET, title_size=16, header_h=36, body_size=14.5, line_spacing=130,
    )

    # ==================== SLIDE 18: LIVE DEMO 1 (NICHE HANDBOOK QUERIES) ====================
    b.add_slide("S18", C_CREAM_BG, notes[18])
    b.light_chrome("S18", 18, "Live Demo 1: Latin Honors & Absences", "Speaker: John Andrew Angcaway")
    b.card(
        "S18", 24, 68, 326, 300,
        "Case 1 • Latin Honors GWA (Doc 133)",
        "Query:\n\"What are the specific grades you need for Latin honors?\"\n\n"
        "Exact Cutoffs Returned:\n"
        "• Summa: ≥ 93% (no grade < 85%)\n"
        "• Magna: 91–92.99% (no < 80%)\n"
        "• Cum Laude: 88–90.99% (< 78%)",
        header_bg=C_INK, title_size=15.5, header_h=36, body_size=14.5, line_spacing=128,
    )
    b.card(
        "S18", 370, 68, 326, 300,
        "Case 2 • Dropped vs. FDA (Doc 134)",
        "Query:\n\"How many absences do I have before I become dropped vs. permanently dropped?\"\n\n"
        "Comparative Synthesis:\n"
        "• Drop (WP/DRP): before finals (non-F)\n"
        "• Permanent FDA: 11th MWF / 8th TTh\n"
        "• 3 consec. absences → OSAS Slip",
        header_bg=C_CORAL, title_size=15.5, header_h=36, body_size=14.5, line_spacing=124,
    )

    # ==================== SLIDE 19: LIVE DEMO 2 (CAR & OOD SAFETY) ====================
    b.add_slide("S19", C_CREAM_BG, notes[19])
    b.light_chrome("S19", 19, "Live Demo 2: Cordilleran CAR & OOD Safety", "Speaker: John Andrew Angcaway")
    b.card(
        "S19", 24, 68, 326, 300,
        "Case 3 • Kankanaey Integrity (CAR)",
        "Query:\n\"Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?\"\n\n"
        "Greeting:\n• Gawis ay agew! (kne)\n\n"
        "Matched Policy:\n• Art. II Disciplinary Board (0% FP-CAR)",
        header_bg=C_TEAL, title_size=15.5, header_h=36, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S19", 370, 68, 326, 300,
        "Case 4 • Out-of-Domain Safety Gate",
        "Query:\n\"What is the best recipe for Baguio strawberry sinigang?\"\n\n"
        "Status:\n• OUT_OF_DOMAIN (Score < threshold)\n\n"
        "Result:\n• Zero hallucination → URO/OSAS guide",
        header_bg=C_AMBER, title_size=15.5, header_h=36, body_size=14.5, line_spacing=130,
    )

    # ==================== SLIDE 20: LIMITATIONS & PRIVACY (LIGHT PAPER GRID) ====================
    b.add_slide("S20", C_CREAM_BG, notes[20])
    b.light_chrome("S20", 20, "Honest Limitations & RA 10173 Privacy", "Speaker: John Andrew Angcaway")
    b.card(
        "S20", 24, 68, 326, 300,
        "Transparent Provenance",
        f"• {m['curated_docs']} expanded queries tagged CURATED_MULTILINGUAL\n\n"
        "• Next: Formal validation with native ilo, kne & ibl linguists\n\n"
        "• Expand to Bontok & Ifugao idioms",
        header_bg=C_INK, title_size=16, header_h=36, body_size=15, line_spacing=132,
    )
    b.card(
        "S20", 370, 68, 326, 300,
        "RA 10173 Data Privacy",
        "• Zero student names, IDs, or private metadata stored\n\n"
        "• 100% client-side inference — queries stay on user device\n\n"
        "• Static Netlify deploy eliminates DB breach risk",
        header_bg=C_VIOLET, title_size=16, header_h=36, body_size=15, line_spacing=132,
    )

    # ==================== SLIDE 21: FUTURE ROADMAP (LIGHT PAPER GRID) ====================
    b.add_slide("S21", C_CREAM_BG, notes[21])
    b.light_chrome("S21", 21, "Future Roadmap for SLU & CAR NLP", "Speaker: Chaze Rodriguez")
    milestones = [
        ("01", "Native CAR Community Validation", "Audit idioms, diacritics, and anonymized student logs with SLU & CAR speakers.", C_INK),
        ("02", "Compact Multilingual Embeddings + RAG", "Benchmark mE5 / LaBSE semantic retrieval with verbatim Handbook citations.", C_VIOLET),
        ("03", "Live iSLU & Institutional Integration", "Connect live URO academic calendars, OSAS advisories, and official ticketing.", C_CORAL),
    ]
    for idx, (num, title, desc, col) in enumerate(milestones):
        my = 68 + idx * 102
        b.rect("S21", 24, my, 672, 88, C_WHITE, outline_hex=C_INK)
        b.rect("S21", 24, my, 672, 1.5, C_INK)
        b.rect("S21", 24, my + 86.5, 672, 1.5, C_INK)
        b.textbox("S21", num, 24, my, 84, 88, font_size=30, bold=True, color=C_WHITE, bg_hex=col, align="center", valign="MIDDLE", font_family="Roboto Mono")
        b.textbox("S21", title, 120, my + 8, 564, 32, font_size=18, bold=True, color=C_INK, valign="MIDDLE")
        b.textbox("S21", desc, 120, my + 40, 564, 42, font_size=14.5, color=C_INK, valign="TOP", line_spacing=124)

    # ==================== SLIDE 22: IMPACT SUMMARY & Q&A (DARK NEON-GLOW HERO) ====================
    b.add_slide("S22", C_DARK_BG, notes[22])
    b.dark_neon_aura("S22")
    b.graph_grid("S22", C_DARK_GRID, alpha=0.82)
    b.textbox("S22", "Impact Summary & Open Q&A", 30, 18, 660, 44, font_size=32, bold=True, color=C_WHITE, align="center", valign="MIDDLE")
    b.textbox(
        "S22",
        "Group 2 – AiNomally  •  Reproducible, Audited & Canva-Redesigned SLU Multilingual NLP",
        30, 62, 660, 26, font_size=14, color=C_LIGHT_MUTED, align="center", valign="MIDDLE",
    )

    b.stat_card("S22", 26, 98, 156, 122, f"{m['docs']} / {m['policies']}", "Balanced Docs\n& SLU Policies", bg=C_DARK_CARD_ALT, num_col=C_CORAL, num_size=28, lbl_size=13)
    b.stat_card("S22", 196, 98, 156, 122, str(m["lex_total"]), "Verified SLU +\nCAR Lexicon", bg=C_DARK_CARD_ALT, num_col=C_VIOLET_BRIGHT, num_size=34, lbl_size=13)
    b.stat_card("S22", 366, 98, 156, 122, f"{m['svm_f1']:.2f}%", "5-Fold CV\nMacro F1 (SVM)", bg=C_DARK_CARD_ALT, num_col=C_AURA_LIGHT, num_size=28, lbl_size=13)
    b.stat_card("S22", 536, 98, 156, 122, f"{m['abl_d']['top1_policy_accuracy']*100:.1f}%", "Unseen Top-1\n100% OOD Safe", bg=C_DARK_CARD_ALT, num_col=C_GOLD_BRIGHT, num_size=30, lbl_size=13)

    b.textbox("S22", "22 / 22 Automated Tests Passing  •  GitHub, Netlify & Drive Synced", 26, 234, 514, 28, font_size=14, bold=True, color=C_WHITE, align="left", valign="MIDDLE")
    b.rect("S22", 26, 268, 210, 3, C_CORAL)
    b.textbox("S22", "Agyamanak! • Iyaman! • Thank You!", 26, 278, 514, 38, font_size=22, bold=True, color=C_AURA_LIGHT, align="left", valign="MIDDLE")
    b.textbox("S22", "Live Portal  →  slu-egovernance-chatbot.netlify.app", 26, 322, 514, 26, font_size=14.5, bold=True, color=C_CORAL, align="left", valign="MIDDLE")
    b.textbox("S22", "github.com/ChazeRodriguez/slu-egovernance-chatbot-car-lexicon", 26, 352, 514, 22, font_size=12, color=C_LIGHT_MUTED, align="left", valign="MIDDLE", font_family="Roboto Mono")

    # Crisp QR code card on bottom-right for instant classroom phone scan
    qr_path = os.path.join(PRES_DIR, "portal_qr.png")
    b.rect("S22", 556, 232, 136, 154, C_WHITE, outline_hex=C_CORAL)
    if os.path.exists(qr_path):
        b.image("S22", qr_path, 564, 238, 120, 120)
    b.textbox("S22", "SCAN LIVE DEMO →", 556, 360, 136, 24, font_size=10.5, bold=True, color=C_INK, align="center", valign="MIDDLE", font_family="Roboto Mono")


def export_speaker_script_md(notes):
    os.makedirs(PRES_DIR, exist_ok=True)
    lines = [
        "# Group 2 – AiNomally | CSE 30 Classroom TV Presentation Script (22 Slides, 15–20 Minutes)",
        "",
        "**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  ",
        "**Institution:** Saint Louis University (SAMCIS – Department of Computer Science), Baguio City  ",
        "**Instructor:** Prof. Dalos D. Miguel  ",
        "**Deck Format:** 22-Slide Canva EAG-QJ6Vos4 Graph-Paper Classroom TV Edition (minimum 14pt body/table type, full-canvas large-print TV charts)",
        "",
        "| Speaker | Slides Covered | Target Time |",
        "|---|---|---|",
        "| **Chaze Ezkys M. Rodriguez** | Slides 1–3, 21–22 (5 slides) | ~3:50 |",
        "| **Keith Russel Hernandez** | Slides 4–7 (4 slides) | ~3:50 |",
        "| **Earold Jan Delin** | Slides 8–11 (4 slides) | ~3:50 |",
        "| **Erick James Sibayan** | Slides 12–15 (4 slides) | ~3:50 |",
        "| **John Andrew Angcaway** | Slides 16–20 (5 slides) | ~3:55 |",
        "",
        "---",
        "",
    ]
    total_words = 0
    for s_num in range(1, TOTAL_SLIDES + 1):
        note = notes[s_num]
        total_words += len(note.split())
        lines.append(f"## Slide {s_num}")
        lines.append("")
        lines.append(note)
        lines.append("")

    est_min = total_words / 135.0
    lines.insert(6, f"**Total Spoken Word Count:** {total_words:,} words (~{est_min:.1f} minutes at 135 wpm + live Q&A)")

    md_path = os.path.join(PRES_DIR, "speaker_script_15_20min.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Saved speaker script -> {md_path} ({total_words:,} words, ~{est_min:.1f} min)")
    return md_path, lines


def sync_drive_presentation_script(lines):
    ops = [{"op": "set-default-style", "font_family": "Arial", "font_size": 10.5, "text_color": "#1E293B", "line_spacing": 115}]
    for ln in lines:
        if not ln.strip() or ln.startswith("|") or ln == "---":
            continue
        if ln.startswith("# "):
            ops.append({"op": "heading", "level": "1", "text": ln[2:], "text_color": "#002855", "bold": True})
        elif ln.startswith("## "):
            ops.append({"op": "heading", "level": "2", "text": ln[3:], "text_color": "#004B87", "bold": True})
        else:
            clean_ln = ln.replace("**", "")
            ops.append({"op": "append", "text": clean_ln})
    batch_file = os.path.join(SCRATCH, "presentation_script_batch.json")
    with open(batch_file, "w", encoding="utf-8") as f:
        json.dump(ops, f, ensure_ascii=False, indent=2)
    subprocess.run(["gdocs", "mutate", "batch", SCRIPT_DOC_ID, "--replace-all", "-f", batch_file], check=True)
    print(f"[OK] Synced 22-slide speaker script to Drive Doc {SCRIPT_DOC_ID}")


def main():
    parser = argparse.ArgumentParser(description="Build Group 2 AiNomally 22-slide Canva Grid Classroom TV CSE 30 deck.")
    parser.add_argument("--pptx-only", action="store_true", help="Only regenerate local .pptx and speaker script without creating a new Google Slides deck.")
    parser.add_argument("--sync-script-doc", action="store_true", help="Also sync speaker script to Google Drive Doc when using --pptx-only.")
    args = parser.parse_args()

    os.makedirs(PRES_DIR, exist_ok=True)
    metrics = load_live_metrics()
    notes = build_speaker_notes(metrics)
    builder = ClassroomTVDeckBuilder()
    build_deck_content(builder, metrics, notes)

    # 1. Save local PowerPoint backup
    pptx_path = os.path.join(PRES_DIR, "Group2_AiNomally_CSE30_Deck.pptx")
    builder.prs.save(pptx_path)
    print(f"[OK] Saved local PowerPoint -> {pptx_path}")

    # 2. Save local speaker script (+ optional Drive sync)
    _, script_lines = export_speaker_script_md(notes)
    if args.pptx_only:
        if args.sync_script_doc:
            sync_drive_presentation_script(script_lines)
        return
    sync_drive_presentation_script(script_lines)

    # 3. Create fresh Canva Grid Classroom TV Edition Google Slides presentation
    create_res = subprocess.run(
        [
            "gslides", "mutate", "create", "--title",
            "CSE 30 Final Presentation (Canva Grid TV Edition) — SLU eGovernance Chatbot & CAR Lexicon (Group 2 AiNomally)",
        ],
        capture_output=True, text=True, check=True,
    )
    print(create_res.stdout.strip())
    m_id = re.search(r"presentation/d/([A-Za-z0-9_-]+)|ID:\s*([A-Za-z0-9_-]+)", create_res.stdout)
    if not m_id:
        raise RuntimeError(f"Could not parse presentation ID from: {create_res.stdout}")
    pres_id = m_id.group(1) or m_id.group(2)
    print(f"[OK] Created Canva Grid Classroom TV Google Slides Deck ID: {pres_id}")

    # 4. Execute single-batch layout + tables + speaker notes
    batch_path = os.path.join(SCRATCH, "slides_canva_batch.json")
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(builder.ops, f, ensure_ascii=False, indent=2)

    batch_res = subprocess.run(
        ["gslides", "mutate", "batch", pres_id, "-f", batch_path, "--json"],
        capture_output=True, text=True, check=True,
    )
    batch_json = json.loads(batch_res.stdout)
    resolved = batch_json.get("resolved_ids", {})
    resolved["p"] = "p"
    print(f"[OK] Batch built {len(builder.slide_order)} Canva Grid TV slides ({batch_json.get('api_requests')} API requests)")

    # 5. Insert large-print TV charts & QR code onto their exact target slides
    for placeholder_id, img_path, x, y, w, h in builder.image_inserts:
        real_slide_id = resolved.get(placeholder_id, placeholder_id)
        subprocess.run(
            [
                "gslides", "mutate", "insert-image-from-file", pres_id,
                "--slide", real_slide_id,
                "--file", img_path,
                "--x", str(x), "--y", str(y),
                "--width", str(w), "--height", str(h),
            ],
            check=True,
        )
        print(f"[OK] Embedded {os.path.basename(img_path)} on {placeholder_id} ({real_slide_id})")

    meta = {
        "presentation_id": pres_id,
        "url": f"https://docs.google.com/presentation/d/{pres_id}/edit",
        "resolved_ids": resolved,
        "slide_order": builder.slide_order,
    }
    meta_path = os.path.join(SCRATCH, "slides_canva_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[OK] Saved Canva Grid TV deck metadata -> {meta_path}")
    print(f"[URL] {meta['url']}")


if __name__ == "__main__":
    main()
