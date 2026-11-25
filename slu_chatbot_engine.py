# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: slu_chatbot_engine.py
Description: Hardened End-to-End Multilingual eGovernance Student Support Chatbot Engine.
             Integrates:
               - Deterministic Acronym-Safe Text Cleaning (scripts/data_cleaning.py)
               - Guarded English/Filipino/CAR Morphological Analysis (scripts/car_morphology.py)
               - SLU & CAR Multilingual Electronic Lexicon (25 Midterm or 150+ Expanded entries)
                 with strict separation of native CAR tokens vs. English semantic aliases
               - Hybrid Unigram+Bigram TF-IDF Cosine Retrieval + Optional Supervised ML Intent
                 Classifier (models/intent_classifier.json) + Calibrated Confidence Thresholding
               - Conversational Greeting Handler & Honest Out-of-Domain Fallback
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
Instructor: Prof. Dalos D. Miguel
"""

import os
import re
import math
import json
import csv
import argparse
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
import sys

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from data_cleaning import clean_text as _base_clean_text
from data_preprocessing import (
    STOPWORDS as MIDTERM_STOPWORDS,
    LEMMA_MAP as MIDTERM_LEMMA_MAP,
    PREFIX_EXCEPTIONS,
    INSTITUTIONAL_PRIORITY_STEMS,
)
from car_morphology import (
    QUERY_STOPWORDS,
    LEMMA_MAP,
    bilingual_stemmer,
    analyze_morphology,
)

# Preserve backward-compatible module exports
STOPWORDS = QUERY_STOPWORDS

# ==============================================================================
# 1. QUERY SYNONYM EXPANSION, GREETING SETS & POLICY NUMERIC ANCHORS
# ==============================================================================

QUERY_SYNONYMS = {
    "phone": ["mobile", "device", "dishonesty", "unauthorized", "plagiarism", "cheating", "disciplinary"],
    "cellphone": ["mobile", "device", "dishonesty", "unauthorized", "plagiarism", "cheating", "disciplinary"],
    "cp": ["mobile", "device", "dishonesty", "unauthorized"],
    "gadget": ["mobile", "device", "unauthorized"],
    "bawal": ["forbidden", "unauthorized", "strictly", "dishonesty"],
    "cheating": ["dishonesty", "plagiarism", "unauthorized", "disciplinary", "suspension", "dismissal"],
    "cheat": ["cheating", "dishonesty", "plagiarism", "disciplinary"],
    "kopyahan": ["cheating", "collaboration", "unauthorized", "dishonesty"],
    "earthquake": ["seismic", "calamity", "evacuation", "duck", "cover", "oval"],
    "lindol": ["seismic", "calamity", "evacuation", "duck", "cover", "oval"],
    "shifting": ["shifting", "internal", "qualifying", "examination", "qe", "evaluation", "dean", "accepting", "degree", "program"],
    "shift": ["shifting", "internal", "qualifying", "examination", "qe", "evaluation", "dean", "accepting", "crediting"],
    "transfer": ["transferee", "qualifying", "examination", "qe", "credential", "honorable", "dismissal"],
    "credit": ["credit", "credited", "crediting", "equivalence", "general", "education", "nstp", "pathfit", "shiftee", "internal"],
    "credited": ["credit", "credited", "crediting", "equivalence", "general", "education", "nstp", "pathfit", "shiftee", "internal"],
    "ge": ["general", "education", "nstp", "pathfit", "credit", "crediting", "equivalence", "shiftee"],
    "refund": ["tuition", "refund", "prorated", "withdrawal", "finance", "schedule"],
    "validate": ["validate", "validation", "rfid", "library", "posted", "registration", "enrolled"],
    "absent": ["absence", "fda", "unexcused", "dropped", "attendance"],
    "liban": ["absence", "fda", "unexcused", "dropped", "attendance"],
    "enroll": ["enrollment", "advising", "continuing", "portal", "downpayment", "schedule"],
    "kuha": ["request", "official", "transcript", "tor", "cog", "online", "portal", "clearance"],
    "kumuha": ["request", "official", "transcript", "tor", "cog", "online", "portal", "clearance"],
    "cyberbullying": ["harassment", "libelous", "social", "media", "digital", "platform", "privacy", "10173", "sanction"],
    "bullying": ["harassment", "libelous", "social", "media", "digital", "platform", "sanction"],
    "libel": ["libelous", "rumors", "harassment", "social", "media", "digital", "platform", "10173", "sanction"],
    "defamation": ["libelous", "rumors", "harassment", "social", "media", "digital", "platform", "10173"],
    "privacy": ["10173", "data", "digital", "platform", "social", "media", "sanction"],
    "dpa": ["10173", "data", "privacy", "digital", "platform"],
    "ill": ["clinic", "medical", "consultation", "first", "aid", "health"],
    "sick": ["clinic", "medical", "consultation", "first", "aid", "health"],
    "fever": ["clinic", "medical", "consultation", "first", "aid", "health"],
    "dental": ["clinic", "medical", "dental", "consultation", "bonifacio", "maryheights"],
    "drop": ["dropping", "adding", "adjustment", "form", "two", "week", "endorsed", "chair", "registrar"],
    "add": ["adding", "dropping", "adjustment", "form", "two", "week", "endorsed", "chair", "registrar"],
    "shorts": ["uniform", "dress", "code", "wash", "day", "civilian", "attire", "slipper", "sando"],
    "attire": ["uniform", "dress", "code", "wash", "day", "civilian", "slipper", "sando"],
    "fail": ["failure", "grade", "75", "minimum", "passing", "retention"],
    "bagsak": ["failure", "grade", "75", "minimum", "passing", "fda"],
    "scholarship": ["scholar", "dean", "list", "academic", "honor", "discount", "financial", "aid"],
    "tuition": ["downpayment", "fee", "payment", "accounting", "cashier", "installment", "finance"],
    "bayad": ["payment", "downpayment", "tuition", "fee", "cashier", "bank"],
    "mental": ["counseling", "guidance", "wellness", "clinic", "health", "support"],
    "stress": ["counseling", "guidance", "wellness", "mental", "health", "support"],
    "counseling": ["guidance", "wellness", "mental", "health", "center", "support"],
    "pipette": ["laboratory", "lab", "equipment", "safety", "mls", "facility"],
    "library": ["clearance", "book", "borrow", "resource", "learning"],
    "latin": ["latin", "honor", "laude", "summa", "magna", "cum", "gwa", "93", "91", "88", "residency"],
    "laude": ["latin", "honor", "laude", "summa", "magna", "cum", "gwa", "93", "91", "88"],
    "summa": ["latin", "honor", "summa", "cum", "laude", "93", "residency"],
    "magna": ["latin", "honor", "magna", "cum", "laude", "91", "93", "residency"],
    "dean": ["dean", "list", "lister", "honor", "92", "88", "scholarship", "approval"],
    "deanslist": ["dean", "list", "first", "second", "honor", "92", "88", "scholarship"],
    "permanent": ["permanent", "fda", "20", "percent", "11th", "8th", "54", "hours", "dropped"],
    "permanently": ["permanent", "fda", "20", "percent", "11th", "8th", "54", "hours", "dropped"],
    "consecutive": ["consecutive", "3", "osas", "readmission", "slip", "excuse", "clinic"],
    "readmission": ["readmission", "slip", "osas", "consecutive", "returnee", "balik"],
    "promissory": ["promissory", "note", "installment", "finance", "guardian", "permit"],
    "petition": ["petition", "special", "class", "irregular", "graduating", "chair", "dean"],
    "shortterm": ["short", "term", "summer", "6", "9", "units", "advising"],
    "summer": ["short", "term", "summer", "6", "9", "units", "advising"],
    "loa": ["leave", "absence", "loa", "returnee", "balik", "aral", "dean", "readmission"],
    "returnee": ["returnee", "balik", "aral", "loa", "readmission", "dean"],
    "crossenroll": ["cross", "enrollment", "permit", "ched", "external", "dean", "registrar"],
    "probation": ["probation", "qpi", "delinquency", "retention", "bsa", "mls", "bsn"],
    "qpi": ["qpi", "probation", "delinquency", "retention", "weighted", "average"],
    "typhoon": ["typhoon", "monsoon", "suspension", "baguio", "mayor", "pagasa", "ched"],
    "hair": ["hair", "color", "grooming", "piercing", "clinical", "practicum", "sonahbs"],
    "dorm": ["residence", "hall", "dormitory", "curfew", "visitor", "ladies", "men"],
    "dormitory": ["residence", "hall", "dormitory", "curfew", "visitor", "ladies", "men"],
    "breakage": ["laboratory", "breakage", "accountability", "slip", "custodian", "clearance"],
}

GREETING_WORDS = {
    "hello", "hi", "hey", "good", "morning", "afternoon", "evening", "kumusta",
    "kamusta", "musta", "mabuhay", "naimbag", "bigat", "aldaw", "rabii",
    "gawis", "agew", "mapteng", "agsapa", "thanks", "thank", "salamat", "agyamanak",
}

POLICY_NUMERIC_TOKENS = {
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11",
    "20", "36", "54", "75", "80", "82", "84", "88", "90", "91", "92", "93", "99",
    "120", "126", "2012", "6900", "10173", "11200",
}

COMPARATIVE_MARKERS = {
    "vs", "versus", "difference", "differences", "compare",
    "pinagkaiba", "kaibahan", "distinction",
}

FILIPINO_MARKERS = {
    "po", "ba", "pa", "lang", "naman", "kasi", "mga", "sa", "ng", "na",
    "paano", "bakit", "ano", "anong", "saan", "ilan", "pwede", "puwede",
    "mag", "nag", "pag", "kailangan", "bawal", "tayo", "kami", "namin",
    "ambigat", "kumuha", "magkano", "bagsak", "bayad", "tanong", "tulungan",
}

CAR_NATIVE_GREETING_MAP = {
    "ilo": "Naimbag a bigat/aldaw! (Ilocano recognized) ",
    "kne": "Gawis ay agew! (Northern Kankanaey recognized) ",
    "ibl": "Mapteng ja agsapa! (Ibaloi recognized) ",
}

# ==============================================================================
# 2. DEFAULT MIDTERM MULTILINGUAL DOMAIN LEXICON (25 Verified Entries)
#    Strictly separates native_aliases (trigger language/CAR greeting) from
#    semantic_aliases (assist retrieval without spoofing CAR language identity).
# ==============================================================================

DOMAIN_LEXICON = [
    {"lexicon_id": "SLU-001", "lemma": "samcis", "lang": "en-SLU", "pos": "PROPN", "root": "samcis", "affix": "Acronym", "en_gloss": "School of Accountancy, Management, Computing and Information Studies", "fil_gloss": "Paaralan ng Accountancy Management Computing at Information Studies", "intent": "ACADEMIC_SHIFTING_TRANSFER", "native_aliases": ["samcis"], "semantic_aliases": []},
    {"lexicon_id": "SLU-002", "lemma": "seait", "lang": "en-SLU", "pos": "PROPN", "root": "seait", "affix": "Acronym", "en_gloss": "School of Engineering, Architecture, and Information Technology", "fil_gloss": "Paaralan ng Inhinyeriya Arkitektura at Teknolohiyang Pang-impormasyon", "intent": "ACADEMIC_SHIFTING_TRANSFER", "native_aliases": ["seait"], "semantic_aliases": ["engineering"]},
    {"lexicon_id": "SLU-003", "lemma": "sonahbs", "lang": "en-SLU", "pos": "PROPN", "root": "sonahbs", "affix": "Acronym", "en_gloss": "School of Nursing, Allied Health, and Biological Sciences", "fil_gloss": "Paaralan ng Nursing Allied Health at Agham Biyolohikal", "intent": "ACADEMIC_SHIFTING_TRANSFER", "native_aliases": ["sonahbs"], "semantic_aliases": ["nursing"]},
    {"lexicon_id": "SLU-004", "lemma": "mls", "lang": "en-SLU", "pos": "PROPN", "root": "mls", "affix": "Acronym", "en_gloss": "Bachelor of Science in Medical Laboratory Science", "fil_gloss": "Batsilyer ng Agham sa Medical Laboratory Science", "intent": "ACADEMIC_SHIFTING_TRANSFER", "native_aliases": ["mls"], "semantic_aliases": ["medtech"]},
    {"lexicon_id": "SLU-005", "lemma": "uro", "lang": "en-SLU", "pos": "PROPN", "root": "uro", "affix": "Acronym", "en_gloss": "University Registrar's Office", "fil_gloss": "Tanggapan ng Tagapagrehistro ng Unibersidad", "intent": "URO_ENROLLMENT_TOR", "native_aliases": ["uro"], "semantic_aliases": ["registrar"]},
    {"lexicon_id": "SLU-006", "lemma": "tor", "lang": "en-SLU", "pos": "NOUN", "root": "tor", "affix": "Acronym", "en_gloss": "Official Transcript of Records", "fil_gloss": "Opisyal na Talaan ng mga Marka", "intent": "URO_ENROLLMENT_TOR", "native_aliases": ["tor"], "semantic_aliases": ["transcript", "transcripts"]},
    {"lexicon_id": "SLU-007", "lemma": "cog", "lang": "en-SLU", "pos": "NOUN", "root": "cog", "affix": "Acronym", "en_gloss": "Certificate of Grades", "fil_gloss": "Katibayan ng mga Marka", "intent": "URO_ENROLLMENT_TOR", "native_aliases": ["cog"], "semantic_aliases": []},
    {"lexicon_id": "SLU-008", "lemma": "qe", "lang": "en-SLU", "pos": "NOUN", "root": "qe", "affix": "Acronym", "en_gloss": "Qualifying Examination for Transferees and Shiftees", "fil_gloss": "Pagsusulit sa Kwalipikasyon", "intent": "ACADEMIC_SHIFTING_TRANSFER", "native_aliases": ["qe"], "semantic_aliases": ["qualifying"]},
    {"lexicon_id": "SLU-009", "lemma": "fda", "lang": "en-SLU", "pos": "NOUN", "root": "fda", "affix": "Acronym", "en_gloss": "Failure Due to Absences (exceeding 20 percent of class hours)", "fil_gloss": "Bagsak Dahil sa Pagliban", "intent": "HANDBOOK_GRADING_FDA", "native_aliases": ["fda"], "semantic_aliases": ["absence", "absences", "absent"]},
    {"lexicon_id": "SLU-010", "lemma": "pathfit", "lang": "en-SLU", "pos": "PROPN", "root": "pathfit", "affix": "Acronym", "en_gloss": "Physical Activity Towards Health and Fitness Course", "fil_gloss": "Asignaturang Edukasyong Pisikal at Kalusugan", "intent": "CAMPUS_HEALTH_SAFETY", "native_aliases": ["pathfit"], "semantic_aliases": ["clinic", "medical"]},
    {"lexicon_id": "SLU-011", "lemma": "rfid", "lang": "en-SLU", "pos": "NOUN", "root": "rfid", "affix": "Acronym", "en_gloss": "Validated SLU Radio-Frequency Identification Student Card", "fil_gloss": "Opisyal na ID Card ng Estudyante sa SLU", "intent": "EXAM_PERMIT_INTEGRITY", "native_aliases": ["rfid"], "semantic_aliases": ["permit", "permits"]},
    {"lexicon_id": "SLU-012", "lemma": "dp", "lang": "tl-SLU", "pos": "NOUN", "root": "downpayment", "affix": "Abbreviation", "en_gloss": "Required Enrollment Downpayment via SLU Portal or Partner Banks", "fil_gloss": "Paunang Bayad sa Matrikula", "intent": "TUITION_FINANCE", "native_aliases": ["dp", "downpayment"], "semantic_aliases": ["tuition"]},
    {"lexicon_id": "SLU-013", "lemma": "ambilat", "lang": "kne-tl", "pos": "ADJ", "root": "bigat", "affix": "Phonetic_Variant", "en_gloss": "Heavy emotional or academic workload burden (Baguio/Cordilleran Taglish variant of ambigat)", "fil_gloss": "Mabigat sa pakiramdam dahil sa sabay-sabay na pagsusulit", "intent": "CAMPUS_HEALTH_SAFETY", "native_aliases": ["ambilat", "ambigat"], "semantic_aliases": []},
    {"lexicon_id": "ILO-001", "lemma": "naimbag", "lang": "ilo", "pos": "ADJ", "root": "imbag", "affix": "na-", "en_gloss": "Good; pleasant; courteous greeting in Ilocano student inquiries", "fil_gloss": "Mabuti; maganda", "intent": "CAR_REGIONAL_LEXICON", "native_aliases": ["naimbag"], "semantic_aliases": []},
    {"lexicon_id": "ILO-002", "lemma": "agadal", "lang": "ilo", "pos": "VERB", "root": "adal", "affix": "ag-", "en_gloss": "To study; to pursue academic coursework at the university", "fil_gloss": "Mag-aral sa unibersidad", "intent": "URO_ENROLLMENT_PORTAL", "native_aliases": ["agadal", "nagadal", "panagadal", "adal"], "semantic_aliases": []},
    {"lexicon_id": "ILO-003", "lemma": "agsurat", "lang": "ilo", "pos": "VERB", "root": "surat", "affix": "ag-", "en_gloss": "To write; to file a formal written application or petition", "fil_gloss": "Sumulat; maghain ng kahilingan", "intent": "URO_ENROLLMENT_TOR", "native_aliases": ["agsurat", "nagsurat", "surat"], "semantic_aliases": []},
    {"lexicon_id": "ILO-004", "lemma": "agsao", "lang": "ilo", "pos": "VERB", "root": "sao", "affix": "ag-", "en_gloss": "To speak; to inquire or communicate in Ilocano", "fil_gloss": "Magsalita; magtanong", "intent": "CAR_REGIONAL_LEXICON", "native_aliases": ["agsao", "nagsao", "sao"], "semantic_aliases": []},
    {"lexicon_id": "ILO-005", "lemma": "danum", "lang": "ilo", "pos": "NOUN", "root": "danum", "affix": "Root", "en_gloss": "Water; campus utility and sanitation resource", "fil_gloss": "Tubig", "intent": "CAMPUS_FACILITIES_LAB", "native_aliases": ["danum"], "semantic_aliases": []},
    {"lexicon_id": "KNE-001", "lemma": "gawis", "lang": "kne", "pos": "ADJ", "root": "gawis", "affix": "Root", "en_gloss": "Good; well; fine (Northern Kankanaey greeting and well-being marker)", "fil_gloss": "Mabuti; maayos", "intent": "CAR_REGIONAL_LEXICON", "native_aliases": ["gawis"], "semantic_aliases": []},
    {"lexicon_id": "KNE-002", "lemma": "inayan", "lang": "kne", "pos": "INTJ", "root": "inayan", "affix": "Root", "en_gloss": "Cordilleran ethical restraint against academic dishonesty or misconduct", "fil_gloss": "Katutubong konseptong moral laban sa pandaraya o masamang gawa", "intent": "EXAM_PERMIT_INTEGRITY", "native_aliases": ["inayan"], "semantic_aliases": ["cheating", "plagiarism", "dishonesty"]},
    {"lexicon_id": "KNE-003", "lemma": "dap-ay", "lang": "kne", "pos": "NOUN", "root": "dap-ay", "affix": "Root", "en_gloss": "Indigenous communal council and peer consultation center", "fil_gloss": "Katutubong sentro ng sanggunian at talakayan", "intent": "GENERAL_COMMUNITY", "native_aliases": ["dap-ay", "dapay"], "semantic_aliases": []},
    {"lexicon_id": "KNE-004", "lemma": "man-obla", "lang": "kne", "pos": "VERB", "root": "obla", "affix": "man-", "en_gloss": "To work; to complete academic or laboratory tasks diligently", "fil_gloss": "Magtrabaho; gumawa ng gawain", "intent": "CAMPUS_FACILITIES_LAB", "native_aliases": ["man-obla", "men-obla", "manobla", "obla"], "semantic_aliases": []},
    {"lexicon_id": "KNE-005", "lemma": "ubbo", "lang": "kne", "pos": "NOUN", "root": "ubbo", "affix": "Root", "en_gloss": "Mutual cooperative peer assistance and group study labor", "fil_gloss": "Bayanihan; tulungang paggawa", "intent": "GENERAL_COMMUNITY", "native_aliases": ["ubbo"], "semantic_aliases": []},
    {"lexicon_id": "IBL-001", "lemma": "mapteng", "lang": "ibl", "pos": "ADJ", "root": "peteng", "affix": "ma-", "en_gloss": "Good; pleasant; well (Ibaloi campus greeting and welfare term)", "fil_gloss": "Mabuti; maganda; maayos", "intent": "CAR_REGIONAL_LEXICON", "native_aliases": ["mapteng"], "semantic_aliases": []},
    {"lexicon_id": "IBL-002", "lemma": "tongtong", "lang": "ibl", "pos": "NOUN", "root": "tongtong", "affix": "Root", "en_gloss": "Customary dispute resolution and disciplinary council mediation", "fil_gloss": "Katutubong paglilitis at pag-aayos ng sigalot", "intent": "EXAM_PERMIT_INTEGRITY", "native_aliases": ["tongtong"], "semantic_aliases": ["disciplinary"]},
]

# ==============================================================================
# 3. DATA LOADERS (MIDTERM BASELINE & EXPANDED FINALS CORPUS / LEXICON / ML)
# ==============================================================================

def clean_text(text):
    """Hardened acronym-safe cleaning preserving CAR hyphenated lemmas, 'ill', and '?'."""
    return _base_clean_text(text, preserve_car_hyphens=True)


def tokenize(text):
    """Splits string into lowercase alphanumeric/CAR-hyphenated tokens."""
    return re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+)?\b", text.lower())


def generate_ngrams(tokens, n=2):
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def load_midterm_corpus():
    csv_path = os.path.join(REPO_ROOT, "annotated_corpus_midterm.csv")
    docs = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            docs.append({
                "doc_id": int(row["Doc_ID"]),
                "source_file": row["Source_File"],
                "section_ref": row["Section_Reference"],
                "intent_label": row["Intent_Category"],
                "sentiment_polarity": row["Sentiment_Urgency"],
                "code_switching": row["Code_Switching"],
                "raw_text": row["Cleaned_Text"],
                "source_url": "",
            })
    return docs


def load_expanded_policies_and_corpus():
    pol_path = os.path.join(REPO_ROOT, "data", "expanded", "slu_official_policies_v2.json")
    corp_path = os.path.join(REPO_ROOT, "data", "expanded", "annotated_corpus_expanded.csv")
    if not (os.path.exists(pol_path) and os.path.exists(corp_path)):
        return load_midterm_corpus()

    with open(pol_path, "r", encoding="utf-8") as f:
        policies = json.load(f)

    docs = []
    for p in policies:
        docs.append({
            "doc_id": int(p["doc_id"]),
            "source_file": p["source_file"],
            "section_ref": p["section_ref"],
            "intent_label": p["intent_label"],
            "sentiment_polarity": "AUTHORITATIVE_POLICY",
            "code_switching": "EN",
            "raw_text": clean_text(p["raw_text"]),
            "display_text": p["raw_text"],
            "source_url": p.get("source_url", ""),
        })
    return docs


def load_expanded_lexicon():
    lex_path = os.path.join(REPO_ROOT, "data", "expanded", "slu_car_domain_lexicon_v2.csv")
    if not os.path.exists(lex_path):
        return DOMAIN_LEXICON
    entries = []
    with open(lex_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            native_aliases = [a.strip().lower() for a in row.get("Native_Aliases", "").split("|") if a.strip()]
            semantic_aliases = [a.strip().lower() for a in row.get("Semantic_Aliases", "").split("|") if a.strip()]
            lemma = row["Lemma_Entry"].strip().lower()
            if lemma not in native_aliases:
                native_aliases.insert(0, lemma)
            entries.append({
                "lexicon_id": row["Lexicon_ID"].strip(),
                "lemma": lemma,
                "lang": row["Language_ISO"].strip(),
                "pos": row["POS_Tag"].strip(),
                "root": row["Morphological_Root"].strip().lower(),
                "affix": row["Affix_or_Type"].strip(),
                "en_gloss": row["Institutional_or_English_Gloss"].strip(),
                "fil_gloss": row["Filipino_Gloss"].strip(),
                "intent": row["Domain_Intent_Mapping"].strip(),
                "native_aliases": native_aliases,
                "semantic_aliases": semantic_aliases,
            })
    return entries


def load_intent_classifier():
    model_path = os.path.join(REPO_ROOT, "models", "intent_classifier.json")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Default compatibility alias
ANNOTATED_CORPUS = load_midterm_corpus()

# ==============================================================================
# 4. HYBRID TF-IDF + LEXICON + SUPERVISED ML RETRIEVAL ENGINE
# ==============================================================================

class SLUChatbotEngine:
    def __init__(
        self,
        dataset="auto",
        annotated_docs=None,
        lexicon=None,
        intent_boost_alpha=0.25,
        ml_boost_beta=0.30,
        min_confidence=0.14,
        enable_ood_gate=True,
        use_cleaning_morph=True,
        use_lexicon_boost=True,
        use_ml_intent=True,
    ):
        self.dataset_mode = dataset
        if annotated_docs is not None:
            self.docs = [dict(d) for d in annotated_docs]
        elif dataset == "midterm":
            self.docs = load_midterm_corpus()
        elif dataset == "expanded":
            self.docs = load_expanded_policies_and_corpus()
        else:
            # auto: prefer expanded policy KB if present, else midterm
            pol_path = os.path.join(REPO_ROOT, "data", "expanded", "slu_official_policies_v2.json")
            self.docs = load_expanded_policies_and_corpus() if os.path.exists(pol_path) else load_midterm_corpus()

        if lexicon is not None:
            self.lexicon = lexicon
        elif dataset == "midterm":
            self.lexicon = DOMAIN_LEXICON
        else:
            self.lexicon = load_expanded_lexicon()

        self.ml_model = load_intent_classifier() if (use_ml_intent and dataset != "midterm") else None
        self.alpha = intent_boost_alpha
        self.beta = ml_boost_beta
        self.min_confidence = min_confidence
        self.enable_ood_gate = enable_ood_gate
        self.use_cleaning_morph = use_cleaning_morph
        self.use_lexicon_boost = use_lexicon_boost
        self.use_ml_intent = use_ml_intent

        self.N = len(self.docs)
        self.df = Counter()
        self.doc_vectors = []
        self.doc_norms = []
        self.all_stems = []
        self.all_bigrams = []
        self._build_index()

    def _extract_tokens_and_stems(self, text, for_query=False):
        raw_tokens = tokenize(text)
        stopset = QUERY_STOPWORDS if for_query else MIDTERM_STOPWORDS
        filtered = []
        for t in raw_tokens:
            if t in stopset:
                continue
            if len(t) <= 1:
                continue
            if t.isdigit():
                # Keep key policy numbers during live queries (grades, percentages, RA 10173)
                if for_query and (t in POLICY_NUMERIC_TOKENS or (50 <= int(t) <= 99)):
                    filtered.append(t)
                continue
            filtered.append(t)
        if self.use_cleaning_morph:
            stems = [bilingual_stemmer(t) for t in filtered]
        else:
            stems = list(filtered)
        return raw_tokens, filtered, stems

    def _build_index(self):
        for doc in self.docs:
            _, filtered, stems = self._extract_tokens_and_stems(doc["raw_text"], for_query=False)
            bigrams = generate_ngrams(stems, n=2)
            doc["tokens"] = filtered
            doc["stems"] = stems
            doc["bigrams"] = bigrams
            self.all_stems.extend(stems)
            self.all_bigrams.extend(bigrams)

            for feat in set(stems + bigrams):
                self.df[feat] += 1

        for doc in self.docs:
            tf_counts = Counter(doc["stems"] + doc["bigrams"])
            vec = {}
            norm_sq = 0.0
            for feat, tf in tf_counts.items():
                idf = math.log((1.0 + self.N) / (1.0 + self.df[feat])) + 1.0
                tf_w = (1.0 + math.log(tf)) if self.dataset_mode != "midterm" else float(tf)
                w = tf_w * idf
                vec[feat] = w
                norm_sq += w * w
            self.doc_vectors.append(vec)
            self.doc_norms.append(math.sqrt(norm_sq) if norm_sq > 0 else 1.0)

    def match_lexicon(self, raw_query, query_tokens, query_stems):
        """
        Matches lexicon entries and records match_type ('native' vs 'semantic').
        Only 'native' matches on CAR languages trigger CAR register & regional greetings.
        """
        matched = []
        raw_lower = raw_query.lower()
        raw_tok_set = set(tokenize(raw_lower))
        token_set = set(query_tokens) | set(query_stems) | raw_tok_set

        for entry in self.lexicon:
            native_aliases = set(entry.get("native_aliases", [entry["lemma"]]))
            semantic_aliases = set(entry.get("semantic_aliases", []))

            is_native = bool(
                (entry["lemma"] in token_set)
                or (native_aliases & token_set)
                or re.search(r"(?<![a-z0-9])" + re.escape(entry["lemma"]) + r"(?![a-z0-9])", raw_lower)
            )
            is_semantic = (not is_native) and bool(semantic_aliases & token_set)

            if is_native or is_semantic:
                rec = dict(entry)
                rec["match_type"] = "native" if is_native else "semantic"
                matched.append(rec)
        return matched

    def detect_code_switching(self, raw_tokens, matched_lex):
        car_langs = {"ilo", "kne", "ibl", "kne-tl"}
        # CRITICAL FIX: Only genuine native CAR lexical matches trigger CAR-TL-EN
        has_native_car = any(
            e["lang"] in car_langs and e.get("match_type") == "native"
            for e in matched_lex
        )
        has_fil = any(t in FILIPINO_MARKERS for t in raw_tokens)
        if has_native_car:
            return "CAR-TL-EN"
        if has_fil:
            return "TL-EN"
        return "EN"

    def predict_ml_intent(self, stems, bigrams):
        """Runs serialized linear/NB supervised model weights and returns full class probabilities."""
        if not self.ml_model:
            return None, 0.0, {}
        model_type = self.ml_model.get("model_type")
        classes = self.ml_model["classes"]
        vocab = self.ml_model["vocab"]
        idf = self.ml_model["idf"]
        features = Counter(stems + bigrams)

        # Build L2-normalized sublinear TF-IDF sparse dict (matches SparseTfidfVectorizer)
        vec = {}
        norm_sq = 0.0
        for feat, tf in features.items():
            idx = vocab.get(feat)
            if idx is not None:
                w = (1.0 + math.log(tf)) * idf[idx]
                vec[idx] = w
                norm_sq += w * w
        if norm_sq <= 0.0:
            return None, 0.0, {}
        inv_norm = 1.0 / math.sqrt(norm_sq)
        for idx in vec:
            vec[idx] *= inv_norm

        if model_type in ("logistic_regression", "linear_svm"):
            weights = self.ml_model["weights"]
            biases = self.ml_model["biases"]
            logits = []
            for c_idx in range(len(classes)):
                score = biases[c_idx]
                c_w = weights[c_idx]
                for f_idx, val in vec.items():
                    score += c_w[f_idx] * val
                logits.append(score)
            max_l = max(logits)
            exps = [math.exp(l - max_l) for l in logits]
            denom = sum(exps)
            probs = [e / denom for e in exps]
            best_i = max(range(len(classes)), key=lambda i: probs[i])
            probs_map = {c: probs[i] for i, c in enumerate(classes)}
            return classes[best_i], probs[best_i], probs_map

        if model_type == "multinomial_nb":
            log_priors = self.ml_model["log_priors"]
            log_probs = self.ml_model["log_probs"]
            scores = []
            for c_idx in range(len(classes)):
                s = log_priors[c_idx]
                c_lp = log_probs[c_idx]
                for f_idx, val in vec.items():
                    s += val * c_lp[f_idx]
                scores.append(s)
            max_s = max(scores)
            exps = [math.exp(s - max_s) for s in scores]
            denom = sum(exps)
            probs = [e / denom for e in exps]
            best_i = max(range(len(classes)), key=lambda i: probs[i])
            probs_map = {c: probs[i] for i, c in enumerate(classes)}
            return classes[best_i], probs[best_i], probs_map

        return None, 0.0, {}

    def _is_pure_greeting(self, raw_tokens, filtered_tokens, matched_lex):
        if not raw_tokens:
            return False
        non_greeting_content = [
            t for t in filtered_tokens
            if t not in GREETING_WORDS and t not in FILIPINO_MARKERS
        ]
        has_greeting_token = any(t in GREETING_WORDS for t in raw_tokens)
        has_non_greeting_lex = any(
            e["intent"] != "CAR_REGIONAL_LEXICON" for e in matched_lex
        )
        return has_greeting_token and not non_greeting_content and not has_non_greeting_lex

    def _car_greeting_prefix(self, matched_lex):
        for lang_code in ("ilo", "kne", "ibl"):
            if any(
                e["lang"] == lang_code and e.get("match_type") == "native"
                for e in matched_lex
            ):
                return CAR_NATIVE_GREETING_MAP[lang_code]
        return ""

    def answer_query(self, user_query, top_k=3):
        cleaned = clean_text(user_query) if self.use_cleaning_morph else user_query.lower().strip()
        raw_tokens, filtered_tokens, stems = self._extract_tokens_and_stems(cleaned, for_query=True)
        bigrams = generate_ngrams(stems, n=2)
        morphology_trace = [analyze_morphology(t) for t in filtered_tokens]

        matched_lex = self.match_lexicon(user_query, raw_tokens, stems) if self.use_lexicon_boost else []
        code_switching = self.detect_code_switching(raw_tokens, matched_lex)
        car_greeting = self._car_greeting_prefix(matched_lex)

        # Handle pure conversational greetings cleanly without querying policy docs
        if self._is_pure_greeting(raw_tokens, filtered_tokens, matched_lex):
            greeting_msg = (
                (car_greeting or "Hello, Louisian! ")
                + "I am the SLU eGovernance Student Support Assistant. Ask me in English, Taglish, "
                "Ilocano, Northern Kankanaey, or Ibaloi about URO enrollment, TOR/COG requests, "
                "shifting & qualifying exams, grading/FDA rules, exam permits & academic integrity, "
                "dress code, tuition/finance, clinic/PATHFIT, campus safety, or student welfare."
            )
            return {
                "raw_query": user_query,
                "cleaned_query": cleaned,
                "filtered_tokens": filtered_tokens,
                "stems": stems,
                "bigrams": bigrams,
                "morphology": morphology_trace,
                "code_switching": code_switching,
                "predicted_intent": "GREETING",
                "ml_intent": None,
                "ml_confidence": 0.0,
                "matched_lexicon": matched_lex,
                "top_documents": [],
                "is_greeting": True,
                "is_fallback": False,
                "confidence": 1.0,
                "synthesized_response": greeting_msg,
                "citations": [],
            }

        # 1. Expand query features using CAR/SLU lexicon and domain synonyms
        expanded_stems = list(stems)
        lex_intents = set()
        raw_tok_set = set(raw_tokens)
        stem_only_set = set(stems)
        is_comparative = bool(raw_tok_set & COMPARATIVE_MARKERS)

        # Numeric grade detection & policy anchors
        for tok in filtered_tokens:
            if tok.isdigit():
                val = int(tok)
                if 50 <= val < 75:
                    expanded_stems.extend(["grade", "below", "75", "failure", "minimum", "passing", "retention"])
                    lex_intents.add("HANDBOOK_GRADING_FDA")
                elif val == 75:
                    expanded_stems.extend(["grade", "75", "minimum", "passing", "retention"])
                    lex_intents.add("HANDBOOK_GRADING_FDA")
                elif val in (88, 91, 93) and (stem_only_set & {"honor", "latin", "laude", "summa", "magna", "cum", "gwa", "graduate", "graduation", "grade"}):
                    expanded_stems.extend(["latin", "honor", "summa", "magna", "cum", "laude", "93", "91", "88", "residency"])
                    lex_intents.add("HANDBOOK_GRADING_FDA")
                elif val == 20 and (stem_only_set & {"absence", "absent", "fda", "percent", "class"}):
                    expanded_stems.extend(["absence", "fda", "20", "percent", "dropped"])
                    lex_intents.add("HANDBOOK_GRADING_FDA")
                elif val == 10173:
                    expanded_stems.extend(["republic", "act", "data", "privacy", "digital", "platform"])
                    lex_intents.add("CAMPUS_HEALTH_SAFETY")

        # Targeted SLU sub-policy anchors for Latin Honors, Dean's List, and Absence Limits
        if self.use_cleaning_morph:
            q_all = raw_tok_set | stem_only_set
            if (q_all & {"latin", "laude", "summa", "magna"}) or (("cum" in q_all) and ("laude" in q_all or "honor" in q_all)) or ("pammadayaw" in q_all):
                expanded_stems.extend(["latin", "honor", "summa", "magna", "cum", "laude", "93", "91", "88", "residency", "120"])
                lex_intents.add("HANDBOOK_GRADING_FDA")
            if ("dean" in q_all and (q_all & {"list", "lister", "honor", "honors", "gwa", "discount", "scholar", "scholarship"})) or ("deanslist" in q_all):
                expanded_stems.extend(["dean", "list", "first", "second", "honor", "92", "88", "scholarship"])
                lex_intents.add("TUITION_FINANCE")
            has_abs_word = bool(q_all & {"absent", "absence", "absences", "drop", "dropped", "fda", "liway", "liwat"})
            has_spec_abs = bool(q_all & {"permanent", "permanently", "mwf", "tth", "mth", "54", "consecutive", "readmission", "hour", "hours", "11th", "8th"})
            has_cnt_abs = bool(q_all & {"absent", "absence", "absences", "liway", "liwat"}) and bool(q_all & {"many", "ilan", "mano", "hour", "hours", "oras", "day", "days", "araw", "limit", "before", "sakbay", "bago"})
            if (has_abs_word and has_spec_abs) or has_cnt_abs:
                expanded_stems.extend(["54", "11th", "8th", "mwf", "tth", "consecutive", "readmission", "slip", "permanent", "fda", "20"])
                lex_intents.add("HANDBOOK_GRADING_FDA")
                if is_comparative or ("voluntary" in q_all) or ("official" in q_all):
                    lex_intents.add("URO_SUBJECT_ADJUSTMENT")

        if self.use_lexicon_boost:
            for entry in matched_lex:
                if entry["intent"] != "CAR_REGIONAL_LEXICON":
                    # Context-aware disambiguation for multi-domain terms (MLS lab vs. shifting; Gate 1 RFID vs. exam permit)
                    if entry["lemma"] == "mls" and (stem_only_set & {"laboratory", "pipette", "material", "budget", "equipment", "litmus", "breakage"}):
                        lex_intents.add("CAMPUS_FACILITIES_LAB")
                    elif entry["lemma"] == "rfid" and (raw_tok_set & {"gate", "gates", "enter", "entering", "borrow", "lending", "lent", "agipabulod"}):
                        lex_intents.add("CAMPUS_DECORUM_DRESSCODE")
                    elif entry["lemma"] == "rfid" and (raw_tok_set & {"validate", "validation", "deposit", "posted"}):
                        lex_intents.add("URO_ENROLLMENT_PORTAL")
                    elif entry["lemma"] in ("laude", "liway", "liwat", "pammadayaw"):
                        lex_intents.add("HANDBOOK_GRADING_FDA")
                    else:
                        lex_intents.add(entry["intent"])
                if entry["lemma"] == "agadal":
                    expanded_stems.extend(["course", "subject", "study"])
                elif entry["lemma"] == "agsurat":
                    expanded_stems.extend(["request", "official", "transcript", "form"])
                elif entry["lemma"] == "inayan":
                    expanded_stems.extend(["academic", "integrity", "dishonesty", "cheating", "plagiarism"])
                elif entry["lemma"] == "tongtong":
                    expanded_stems.extend(["disciplinary", "board", "conduct", "mediation"])
                elif entry["lemma"] == "dp":
                    expanded_stems.extend(["downpayment", "tuition", "payment"])
                elif entry["lemma"] == "fda":
                    expanded_stems.extend(["fda", "absence", "failure", "dropped"])
                elif entry["lemma"] == "agbayad":
                    expanded_stems.extend(["payment", "downpayment", "tuition", "cashier"])
                elif entry["lemma"] == "agpaagas":
                    expanded_stems.extend(["clinic", "medical", "health", "consultation"])
                elif entry["lemma"] in ("liway", "liwat"):
                    expanded_stems.extend(["absence", "fda", "20", "percent", "dropped", "readmission"])
                elif entry["lemma"] in ("pammadayaw", "laude"):
                    expanded_stems.extend(["latin", "honor", "summa", "magna", "cum", "laude", "93", "91", "88"])
                elif entry["lemma"] in ("kasera", "agawid"):
                    expanded_stems.extend(["residence", "hall", "dormitory", "curfew"])

        if self.use_cleaning_morph:
            for tok in sorted(raw_tok_set | stem_only_set):
                if tok in QUERY_SYNONYMS:
                    expanded_stems.extend(QUERY_SYNONYMS[tok])

        # 2. Domain intent detection (only activates on concrete operational signals)
        stem_set = set(expanded_stems)
        if self.use_lexicon_boost:
            if stem_set & {"shifting", "shift", "transferee", "qe", "qualifying", "seait", "sonahbs", "probation", "qpi"}:
                lex_intents.add("ACADEMIC_SHIFTING_TRANSFER")
                if stem_set & {"submission", "window", "adding", "dropping", "adjustment"}:
                    lex_intents.add("URO_SUBJECT_ADJUSTMENT")
            if stem_set & {"adding", "dropping", "drop", "add", "adjustment", "petition", "crossenroll"}:
                lex_intents.add("URO_SUBJECT_ADJUSTMENT")
            if stem_set & {"tor", "cog", "transcript", "clearance", "graduation", "honorable", "dismissal", "cgmc", "cav"}:
                lex_intents.add("URO_ENROLLMENT_TOR")
            if stem_set & {"portal", "advising", "continuing", "enrollment", "enroll", "loa", "returnee", "shortterm", "summer", "validate", "validation"}:
                lex_intents.add("URO_ENROLLMENT_PORTAL")
            if stem_set & {"grade", "passing", "retention", "fda", "absence", "bagsak", "laude", "latin", "readmission", "inc", "nfe"}:
                lex_intents.add("HANDBOOK_GRADING_FDA")
            if (stem_set & {"permit", "proctor", "plagiarism", "cheating", "dishonesty", "mobile", "phone", "device", "disciplinary"}) or (
                "rfid" in stem_set and not (stem_set & {"gate", "gates", "borrow", "lending", "validate", "validation"})
            ):
                lex_intents.add("EXAM_PERMIT_INTEGRITY")
            if stem_set & {"clinic", "medical", "pathfit", "evacuation", "seismic", "calamity", "oval", "privacy", "10173", "libelous", "harassment", "ill", "sick", "dental", "security", "typhoon", "monsoon", "suspension"}:
                lex_intents.add("CAMPUS_HEALTH_SAFETY")
            if stem_set & {"uniform", "dress", "wash", "slipper", "sando", "attire", "shorts", "hair", "grooming", "piercing"} or (
                "rfid" in stem_set and bool(stem_set & {"gate", "gates", "borrow", "lending"})
            ):
                lex_intents.add("CAMPUS_DECORUM_DRESSCODE")
            if stem_set & {"tuition", "downpayment", "fee", "installment", "accounting", "cashier", "promissory", "deanslist", "refund"}:
                lex_intents.add("TUITION_FINANCE")
                if "validate" in stem_set and "rfid" in stem_set:
                    lex_intents.discard("TUITION_FINANCE")
                    lex_intents.add("URO_ENROLLMENT_PORTAL")
                if "refund" in stem_set:
                    lex_intents.discard("URO_SUBJECT_ADJUSTMENT")
            if stem_set & {"laboratory", "pipette", "litmus", "facility", "equipment", "library", "breakage", "dormitory", "residence", "curfew"}:
                lex_intents.add("CAMPUS_FACILITIES_LAB")
            if stem_set & {"scholarship", "scholar", "counseling", "guidance", "mental", "wellness", "ambigat"}:
                if stem_set & {"scholarship", "scholar", "deanslist"}:
                    lex_intents.add("TUITION_FINANCE")
                elif any(d["intent_label"] == "STUDENT_WELFARE_SCHOLARSHIP" for d in self.docs):
                    lex_intents.add("STUDENT_WELFARE_SCHOLARSHIP")
                else:
                    lex_intents.add("CAMPUS_HEALTH_SAFETY")

        # 3. Optional Supervised ML Intent Prediction (full probability distribution over classes)
        ml_intent, ml_conf, ml_probs = self.predict_ml_intent(stems, bigrams)
        ml_top_intents = [
            {"intent": c, "confidence": round(p, 4)}
            for c, p in sorted(ml_probs.items(), key=lambda kv: kv[1], reverse=True)[:2]
            if p >= 0.10
        ]

        # 4. Build query TF-IDF vector
        expanded_bigrams = generate_ngrams(expanded_stems, n=2)
        query_features = expanded_stems + bigrams + expanded_bigrams
        q_tf = Counter(query_features)
        q_vec = {}
        q_norm_sq = 0.0
        for feat, tf in q_tf.items():
            idf = math.log((1.0 + self.N) / (1.0 + self.df.get(feat, 0))) + 1.0
            tf_w = (1.0 + math.log(tf)) if self.dataset_mode != "midterm" else float(tf)
            w = tf_w * idf
            q_vec[feat] = w
            q_norm_sq += w * w
        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0

        # Probabilistic ML moderation lets trained classifier collaborate with lexical rules across multi-intent queries
        eff_alpha = 0.14 if (self.ml_model and ml_intent and ml_conf >= 0.25) else self.alpha

        scored_docs = []
        for idx, doc in enumerate(self.docs):
            d_vec = self.doc_vectors[idx]
            d_norm = self.doc_norms[idx]
            dot = sum(w * d_vec.get(feat, 0.0) for feat, w in q_vec.items())
            cosine = dot / (q_norm * d_norm)

            intent_match = 1.0 if (self.use_lexicon_boost and doc["intent_label"] in lex_intents) else 0.0
            ml_prob = ml_probs.get(doc["intent_label"], 0.0) if (self.use_ml_intent and ml_probs) else 0.0
            ml_term = (self.beta * ml_prob) if ml_prob >= 0.16 else 0.0
            is_policy = doc["sentiment_polarity"] == "AUTHORITATIVE_POLICY"

            # Only award authority bonus when there is real lexical or intent evidence
            auth_bonus = 0.15 if (is_policy and (cosine > 0.02 or intent_match > 0 or ml_term > 0)) else 0.0
            boost = (eff_alpha * intent_match) + ml_term + auth_bonus
            final_score = cosine + boost

            scored_docs.append({
                "doc_id": doc["doc_id"],
                "source_file": doc["source_file"],
                "section_ref": doc["section_ref"],
                "source_url": doc.get("source_url", ""),
                "intent_label": doc["intent_label"],
                "sentiment_polarity": doc["sentiment_polarity"],
                "cosine_similarity": round(cosine, 4),
                "intent_boost": round(boost, 4),
                "final_score": round(final_score, 4),
                "raw_text": doc.get("display_text", doc["raw_text"]),
            })

        policy_candidates = [
            d for d in scored_docs
            if d["sentiment_polarity"] == "AUTHORITATIVE_POLICY" and d["final_score"] > 0
        ]
        policy_candidates.sort(key=lambda x: (x["final_score"], x["cosine_similarity"], -x["doc_id"]), reverse=True)
        scored_docs.sort(key=lambda x: (x["final_score"], x["cosine_similarity"], -x["doc_id"]), reverse=True)

        # Calibrated OOD / low-confidence gate (prevents hallucinating irrelevant Freedom Wall docs)
        best_policy = policy_candidates[0] if policy_candidates else None
        if not self.enable_ood_gate:
            top_matches = policy_candidates[:top_k] if policy_candidates else scored_docs[:top_k]
            has_evidence = True
        else:
            # Require genuine domain evidence: if neither lexicon nor ML intent activated (boost <= 0.16),
            # demand stronger direct lexical cosine (>= 0.08) so generic words like "study" trigger OOD fallback.
            strong_boost = bool(best_policy and best_policy["intent_boost"] > 0.16)
            has_evidence = bool(
                best_policy
                and best_policy["final_score"] >= self.min_confidence
                and (
                    (strong_boost and (best_policy["cosine_similarity"] >= 0.025 or best_policy["intent_boost"] >= 0.35))
                    or (best_policy["cosine_similarity"] >= 0.08)
                )
            )

        if not has_evidence:
            fallback_msg = (
                (car_greeting or "")
                + "I could not find an authoritative Saint Louis University policy matching your query "
                "with sufficient confidence. Please rephrase with specific SLU terms (e.g., TOR, COG, "
                "shifting, QE, FDA, RFID, exam permit, wash day, clinic, tuition) or contact the "
                "relevant office directly: University Registrar's Office (URO), Office of Student Affairs "
                "(OSA), Finance/Accounting Office, Center for Health Services, or SLU Security (Gates 1 & 2)."
            )
            return {
                "raw_query": user_query,
                "cleaned_query": cleaned,
                "filtered_tokens": filtered_tokens,
                "stems": stems,
                "bigrams": bigrams,
                "morphology": morphology_trace,
                "code_switching": code_switching,
                "predicted_intent": "OUT_OF_DOMAIN",
                "ml_intent": ml_intent,
                "ml_confidence": round(ml_conf, 4),
                "matched_lexicon": matched_lex,
                "top_documents": [],
                "is_greeting": False,
                "is_fallback": True,
                "confidence": round(best_policy["final_score"], 4) if best_policy else 0.0,
                "synthesized_response": fallback_msg,
                "citations": [],
            }

        top_matches = policy_candidates[:top_k] if policy_candidates else scored_docs[:top_k]
        primary_intent = top_matches[0]["intent_label"]
        # Comparative queries or close runner-up scores include second contrasted policy
        chosen_docs = [top_matches[0]]
        runner_up_min = max(0.30, top_matches[0]["final_score"] * 0.58) if is_comparative else max(0.35, top_matches[0]["final_score"] * 0.72)
        if len(top_matches) > 1 and top_matches[1]["final_score"] >= runner_up_min:
            chosen_docs.append(top_matches[1])

        citations = [f"{d['source_file']} ({d['section_ref']})" for d in chosen_docs]
        synthesized = (
            car_greeting
            + "Based on official Saint Louis University regulations: "
            + " | ".join(
                [
                    f"[{d['section_ref']}] {d['raw_text'][0].upper() + d['raw_text'][1:]}"
                    for d in chosen_docs
                ]
            )
        )

        return {
            "raw_query": user_query,
            "cleaned_query": cleaned,
            "filtered_tokens": filtered_tokens,
            "stems": stems,
            "bigrams": bigrams,
            "morphology": morphology_trace,
            "code_switching": code_switching,
            "predicted_intent": primary_intent,
            "ml_intent": ml_intent,
            "ml_confidence": round(ml_conf, 4),
            "ml_top_intents": ml_top_intents,
            "is_comparative": is_comparative,
            "matched_lexicon": matched_lex,
            "top_documents": top_matches,
            "is_greeting": False,
            "is_fallback": False,
            "confidence": top_matches[0]["final_score"],
            "synthesized_response": synthesized,
            "citations": citations,
        }


def evaluate_benchmark(dataset="midterm"):
    """Evaluates Top-1 Accuracy, Top-2 Recall, and Mean Reciprocal Rank (MRR) on the 8-query Midterm benchmark."""
    engine = SLUChatbotEngine(dataset=dataset)
    benchmark = [
        {"query": "Pwede mag tanong? Paano po ba process ng shifting from SAMCIS to SEAIT or SONAHBS? May qualifying exams po ba ulit or direct submission lang sa URO window?", "expected_docs": {18, 24}},
        {"query": "Naimbag a bigat! Agadal ak idiay SAMCIS—ilan po ang absences bago ma-FDA at bawal ba ang phone sa exam?", "expected_docs": {13, 15}},
        {"query": "Paano kumuha ng TOR at COG sa URO portal at ano ang clearance requirements?", "expected_docs": {20}},
        {"query": "Magkano ang downpayment (dp) sa SLU student portal at paano mag-enroll ang continuing students?", "expected_docs": {22}},
        {"query": "Gawis ay agew! Inayan ang cheating o plagiarism sa SLU exams di'ba? Ano po ang sanction at kailangan ba ng RFID at exam permit?", "expected_docs": {15, 14}},
        {"query": "Saan po ang university clinic para sa PATHFIT medical certificate at saan ang evacuation area kapag may earthquake sa Baguio?", "expected_docs": {10, 11}},
        {"query": "Ano po ang minimum passing grade sa SLU at retention grade sa SAMCIS?", "expected_docs": {12}},
        {"query": "Bawal ba ang slippers at sando sa SLU campus kapag Wash Day (Fridays and Saturdays)?", "expected_docs": {16}},
    ]
    top1_hits = 0
    rr_sum = 0.0
    for idx, item in enumerate(benchmark, 1):
        res = engine.answer_query(item["query"], top_k=3)
        returned_ids = [d["doc_id"] for d in res["top_documents"]]
        hit_ranks = [r for r, doc_id in enumerate(returned_ids, 1) if doc_id in item["expected_docs"]]
        if hit_ranks and hit_ranks[0] == 1:
            top1_hits += 1
        if hit_ranks:
            rr_sum += 1.0 / hit_ranks[0]
        print(
            f"Bench #{idx}: Returned Docs={returned_ids} | Expected={sorted(item['expected_docs'])} | "
            f"Top-1 Hit={bool(hit_ranks and hit_ranks[0] == 1)}"
        )
    n = len(benchmark)
    print(f"\n[Benchmark Summary] Queries={n} | Top-1 Policy Accuracy={(top1_hits / n) * 100:.1f}% | MRR={rr_sum / n:.4f}")


def run_demo(dataset="auto"):
    engine = SLUChatbotEngine(dataset=dataset)
    print("=" * 78)
    print("  SLU eGOVERNANCE MULTILINGUAL CHATBOT ENGINE (CSE 30 - GROUP 2 AiNomally)")
    print(
        f"  Mode: {dataset} | Indexed Docs: {engine.N} | Lexicon Entries: {len(engine.lexicon)} | "
        f"ML Intent Model: {'ACTIVE' if engine.ml_model else 'OFF'}"
    )
    print("=" * 78)

    sample_queries = [
        "Pwede mag tanong? Paano po ba process ng shifting from SAMCIS to SEAIT or SONAHBS? May qualifying exams po ba ulit or direct submission lang sa URO window?",
        "Naimbag a bigat! Agadal ak idiay SAMCIS—ilan po ang absences bago ma-FDA at bawal ba ang phone sa exam?",
        "Paano kumuha ng TOR at COG sa URO portal at ano ang clearance requirements?",
        "What happens if I get 74 in a subject?",
        "Is cyberbullying or libel on Freedom Wall punishable?",
        "random gibberish xyzzy qwerty",
    ]

    for idx, q in enumerate(sample_queries, start=1):
        res = engine.answer_query(q)
        print(f"\n[Test Case {idx}] Query: {res['raw_query']}")
        print(f"  -> Cleaned:          {res['cleaned_query']}")
        print(f"  -> Normalized Stems: {res['stems']}")
        print(f"  -> Code-Switching:   {res['code_switching']} | Intent: {res['predicted_intent']} (ML={res['ml_intent']})")
        if res["matched_lexicon"]:
            lex_str = ", ".join(
                [f"{e['lexicon_id']}:{e['lemma']}({e['lang']},{e['match_type']})" for e in res["matched_lexicon"]]
            )
            print(f"  -> Lexicon Matches:  {lex_str}")
        for rank, d in enumerate(res["top_documents"], start=1):
            print(
                f"  -> Match #{rank}: Doc {d['doc_id']} [{d['section_ref']}] | "
                f"Score={d['final_score']} (Cos={d['cosine_similarity']}, Boost={d['intent_boost']})"
            )
        print(f"  -> Response: {res['synthesized_response']}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SLU eGovernance Multilingual Chatbot Engine")
    parser.add_argument("--dataset", choices=["auto", "midterm", "expanded"], default="auto", help="Dataset mode")
    parser.add_argument("--query", type=str, help="Run a single student query")
    parser.add_argument("--evaluate", action="store_true", help="Run 8-query Midterm retrieval benchmark")
    parser.add_argument("--interactive", action="store_true", help="Run interactive CLI chat loop")
    args = parser.parse_args()

    if args.query:
        bot = SLUChatbotEngine(dataset=args.dataset)
        out = bot.answer_query(args.query)
        print(json.dumps(out, indent=2, ensure_ascii=False))
    elif args.evaluate:
        evaluate_benchmark(dataset="midterm")
    elif args.interactive:
        bot = SLUChatbotEngine(dataset=args.dataset)
        print(f"SLU eGovernance Chatbot Interactive Mode [{args.dataset}] (type 'exit' to quit)")
        while True:
            try:
                q = input("\nAsk SLU Bot: ").strip()
                if not q or q.lower() in ("exit", "quit"):
                    break
                res = bot.answer_query(q)
                print(f"[Intent: {res['predicted_intent']} | Lang: {res['code_switching']} | Conf: {res['confidence']}]")
                print(res["synthesized_response"])
            except EOFError:
                break
    else:
        run_demo(dataset=args.dataset)
