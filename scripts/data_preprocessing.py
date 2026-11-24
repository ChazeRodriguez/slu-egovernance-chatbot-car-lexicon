# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/data_preprocessing.py
Description: Deterministic Midterm Baseline preprocessing pipeline:
             - Regex lexical tokenization
             - 265-word bilingual English & Filipino/Taglish stopword filter
             - Guarded bilingual lemmatizer/stemmer with PREFIX_EXCEPTIONS
             - Contiguous bigram (n=2) generation (all bigrams with freq >= 2)
             - Bag of Words (BoW) Top 30 matrix with institutional-priority tie-breaking
             - Verified Midterm CSV/JSON artifact generation (with Doc #6 unified to #25604)
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
Instructor: Prof. Dalos D. Miguel
"""

import os
import re
import json
import csv
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_INPUT_FILE = os.path.join(REPO_ROOT, "outputs", "cleaned_corpus.txt")
DEFAULT_TOKENS_JSON = os.path.join(REPO_ROOT, "preprocessed_tokens.json")
DEFAULT_BOW_CSV = os.path.join(REPO_ROOT, "corpus_bow_summary.csv")
DEFAULT_ANNOTATED_CSV = os.path.join(REPO_ROOT, "annotated_corpus_midterm.csv")

# Verified 265-word bilingual stopword list (English + Filipino/Taglish)
STOPWORDS = set([
    # English
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am', 'this', 'that', 'these',
    'those', 'from', 'by', 'it', 'its', 'as', 'if', 'what', 'who', 'when', 'where',
    'how', 'why', 'all', 'any', 'can', 'will', 'would', 'should', 'could', 'must',
    'may', 'shall', 'have', 'has', 'had', 'do', 'does', 'did', 'not', 'no', 'nor',
    'but', 'so', 'because', 'about', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'under', 'within', 'without', 'upon', 'toward',
    'until', 'since', 'while', 'only', 'also', 'very', 'still', 'even', 'just',
    'more', 'most', 'than', 'other', 'such', 'own', 'same', 'some', 'each', 'every',
    'both', 'few', 'many', 'much', 'now', 'then', 'here', 'there', 'up', 'down',
    'out', 'off', 'over', 'again', 'further', 'once', 'you', 'your', 'yours',
    'yourself', 'me', 'my', 'mine', 'myself', 'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself', 'we', 'us', 'our', 'ours', 'ourselves',
    'they', 'them', 'their', 'theirs', 'themselves', 'one', 'two', 'first', 'second',
    '1st', 'like', 'yes', 'please', 'hello', 'hi', 'lowkey', 'haha', 'sis', 'guys',
    'real', 'hell', 'let', 'get', 'got', 'gave', 'make', 'made', 'know', 'knows',
    'said', 'told', 'met', 'went', 'go', 'going', 'looking', 'look', 'see', 'seen',
    # Filipino / Taglish
    'ang', 'mga', 'sa', 'ng', 'na', 'ay', 'si', 'sina', 'ni', 'nina', 'kay', 'kina',
    'po', 'ko', 'mo', 'nila', 'natin', 'namin', 'ninyo', 'niyo', 'inyo', 'akin',
    'aking', 'iyo', 'kanila', 'kaniya', 'kanya', 'kami', 'tayo', 'kayo', 'sila',
    'siya', 'ako', 'ikaw', 'ka', 'kong', 'ba', 'pa', 'din', 'rin', 'raw', 'daw',
    'lang', 'lamang', 'naman', 'kasi', 'kung', 'at', 'o', 'para', 'dahil', 'upang',
    'kapag', 'pag', 'nag', 'nang', 'may', 'meron', 'wala', 'walang', 'hindi', 'oo',
    'ito', 'iyan', 'iyon', 'yan', 'yun', 'yung', 'dito', 'diyan', 'doon', 'ganito',
    'ganyan', 'ganoon', 'ata', 'atang', 'pala', 'muna', 'talaga', 'dati', 'ngayon',
    'noong', 'tapos', 'pero', 'kaya', 'ulit', 'ano', 'anong', 'paano', 'bakit',
    'saan', 'sino', 'kailan', 'alin', 'ilan', 'magkano', 'pwede', 'puwede', 'kuya', 'ate'
])

LEMMA_MAP = {
    'students': 'student',
    'sem': 'semester',
    'semesters': 'semester',
    'exams': 'examination',
    'exam': 'examination',
    'examinations': 'examination',
    'subjects': 'subject',
    'grades': 'grade',
    'grading': 'grade',
    'grad': 'graduation',
    'requirements': 'requirement',
    'required': 'requirement',
    'certificates': 'certificate',
    'certifications': 'certificate',
    'certification': 'certificate',
    'campuses': 'campus',
    'departments': 'department',
    'portals': 'portal',
    'transferees': 'transferee',
    'transcripts': 'transcript',
    'absences': 'absence',
    'activities': 'activity',
    'deadlines': 'deadline',
    'courses': 'course',
    'programs': 'program',
    'documents': 'document',
    'requests': 'request',
    'guidelines': 'guideline',
    'policies': 'policy',
    'platforms': 'platform',
    'services': 'service',
    'consultations': 'consultation',
    'checks': 'check',
    'practicums': 'practicum',
    'calamities': 'calamity',
    'events': 'event',
    'wardens': 'warden',
    'areas': 'area',
    'courts': 'court',
    'concerns': 'concern',
    'hours': 'hour',
    'permits': 'permit',
    'proctors': 'proctor',
    'rooms': 'room',
    'credentials': 'credential',
    'notes': 'note',
    'devices': 'device',
    'mondays': 'monday',
    'thursdays': 'thursday',
    'fridays': 'friday',
    'saturdays': 'saturday',
    'days': 'day',
    'slippers': 'slipper',
    'sandos': 'sando',
    'locations': 'location',
    'banks': 'bank',
    'cashiers': 'cashier',
    'weeks': 'week',
    'labs': 'laboratory',
    'lab': 'laboratory',
    'materials': 'material',
    'pipettes': 'pipette',
    'tips': 'tip',
    'projects': 'project',
    'cars': 'car',
    'drivers': 'driver',
    'pedestrians': 'pedestrian',
    'issues': 'issue',
    'children': 'child',
    'families': 'family',
    'encounters': 'encounter',
    'strangers': 'stranger',
    'pesos': 'peso',
    'thousands': 'thousand',
    'years': 'year',
    'tumataas': 'taas',
    'tumawid': 'tawid',
    'tatawid': 'tawid',
    'magreklamo': 'reklamo',
    'magtiis': 'tiis',
    'tinipid': 'tipid',
    'sinasabi': 'sabi',
    'sinabi': 'sabi',
    'ginagamit': 'gamit',
    'bibilisan': 'bilis',
    'umakyat': 'akyat',
    'nakakahalata': 'halata',
    'nasanay': 'sanay',
}

# Verified exception list preventing Filipino prefix rules from corrupting English/root words
PREFIX_EXCEPTIONS = {
    'management', 'manager', 'mandatory', 'mandated', 'magnifying', 'magnify',
    'magnetic', 'magnet', 'magnitude', 'magnificent', 'magazine', 'magistrate',
    'magician', 'magical', 'magnesium', 'manganese', 'magnate', 'maganda',
    'magulang', 'magkano', 'pageant', 'pagoda', 'pagination', 'paginated',
    'nagging', 'mangled', 'mangrove', 'pangalan', 'manggagawa',
}

INSTITUTIONAL_PRIORITY_STEMS = {
    'student', 'slu', 'examination', 'semester', 'grade', 'requirement', 'subject',
    'university', 'academic', 'certificate', 'official', 'baguio', 'department',
    'laboratory', 'samcis', 'campus', 'portal', 'medical', 'course', 'class',
    'absence', 'transferee', 'transcript', 'request', 'online', 'school',
}

# Verified multi-layer annotations for the 24 Midterm baseline documents.
# Note: Doc #6 unified to Freedom Wall #25604 matching slu_community_inquiries_raw.txt.
MIDTERM_METADATA = [
    (1, "slu_community_inquiries_raw.txt", "Freedom Wall #25689", "GENERAL_COMMUNITY", "NEUTRAL_PERSONAL", "EN"),
    (2, "slu_community_inquiries_raw.txt", "Freedom Wall #25628", "TUITION_FINANCE", "NEGATIVE_URGENT", "TL-EN"),
    (3, "slu_community_inquiries_raw.txt", "Freedom Wall #25599", "CAMPUS_FACILITIES_LAB", "NEGATIVE_URGENT", "TL-EN"),
    (4, "slu_community_inquiries_raw.txt", "Freedom Wall #25606", "GENERAL_COMMUNITY", "NEUTRAL_INQUIRY", "TL-EN"),
    (5, "slu_community_inquiries_raw.txt", "Freedom Wall #25605", "ACADEMIC_SHIFTING_TRANSFER", "NEUTRAL_INQUIRY", "TL-EN"),
    (6, "slu_community_inquiries_raw.txt", "Freedom Wall #25604", "CAMPUS_HEALTH_SAFETY", "NEGATIVE_URGENT", "CAR-TL-EN"),
    (7, "slu_community_inquiries_raw.txt", "Freedom Wall #5275", "GENERAL_COMMUNITY", "POSITIVE_REFLECTIVE", "CAR-TL-EN"),
    (8, "slu_community_inquiries_raw.txt", "Freedom Wall #25510", "GENERAL_COMMUNITY", "POSITIVE_REFLECTIVE", "TL-EN"),
    (9, "slu_safety_and_support_guide.txt", "Section 1: Digital Platforms & RA 10173", "CAMPUS_HEALTH_SAFETY", "AUTHORITATIVE_POLICY", "EN"),
    (10, "slu_safety_and_support_guide.txt", "Section 2: University Clinic & PATHFIT", "CAMPUS_HEALTH_SAFETY", "AUTHORITATIVE_POLICY", "EN"),
    (11, "slu_safety_and_support_guide.txt", "Section 3: Seismic Evacuation & Security", "CAMPUS_HEALTH_SAFETY", "AUTHORITATIVE_POLICY", "EN"),
    (12, "slu_student_handbook_regulations.txt", "Article I, Section 1: Minimum Grade & Retention", "HANDBOOK_GRADING_FDA", "AUTHORITATIVE_POLICY", "EN"),
    (13, "slu_student_handbook_regulations.txt", "Article I, Section 2: Failure Due to Absences (FDA)", "HANDBOOK_GRADING_FDA", "AUTHORITATIVE_POLICY", "EN"),
    (14, "slu_student_handbook_regulations.txt", "Article II, Section 3: Examination Permits & RFID", "EXAM_PERMIT_INTEGRITY", "AUTHORITATIVE_POLICY", "EN"),
    (15, "slu_student_handbook_regulations.txt", "Article II, Section 4: Academic Integrity", "EXAM_PERMIT_INTEGRITY", "AUTHORITATIVE_POLICY", "EN"),
    (16, "slu_student_handbook_regulations.txt", "Article III, Section 5: Uniform & Wash Day Dress Code", "CAMPUS_DECORUM_DRESSCODE", "AUTHORITATIVE_POLICY", "EN"),
    (17, "slu_uro_enrollment_faqs.txt", "URO FAQ Q1: Transferee Admission Query", "ACADEMIC_SHIFTING_TRANSFER", "NEUTRAL_INQUIRY", "EN"),
    (18, "slu_uro_enrollment_faqs.txt", "URO FAQ A1: Transferee & Qualifying Exam Rules", "ACADEMIC_SHIFTING_TRANSFER", "AUTHORITATIVE_POLICY", "EN"),
    (19, "slu_uro_enrollment_faqs.txt", "URO FAQ Q2: Transcript & Certification Query", "URO_ENROLLMENT_TOR", "NEUTRAL_INQUIRY", "EN"),
    (20, "slu_uro_enrollment_faqs.txt", "URO FAQ A2: Online TOR, COG & Clearance", "URO_ENROLLMENT_TOR", "AUTHORITATIVE_POLICY", "EN"),
    (21, "slu_uro_enrollment_faqs.txt", "URO FAQ Q3: Continuing Enrollment Query", "URO_ENROLLMENT_PORTAL", "NEUTRAL_INQUIRY", "EN"),
    (22, "slu_uro_enrollment_faqs.txt", "URO FAQ A3: Student Portal Advising & Downpayment", "URO_ENROLLMENT_PORTAL", "AUTHORITATIVE_POLICY", "EN"),
    (23, "slu_uro_enrollment_faqs.txt", "URO FAQ Q4: Adding/Dropping Subjects Query", "URO_SUBJECT_ADJUSTMENT", "NEUTRAL_INQUIRY", "EN"),
    (24, "slu_uro_enrollment_faqs.txt", "URO FAQ A4: Two-Week Adjustment Form & Chair Endorsement", "URO_SUBJECT_ADJUSTMENT", "AUTHORITATIVE_POLICY", "EN"),
]


def tokenize(text):
    """Splits string into lowercase alphanumeric tokens."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def bilingual_stemmer(word):
    """Guarded bilingual lemmatizer and prefix-stripping stemmer."""
    if word in LEMMA_MAP:
        return LEMMA_MAP[word]
    if word in PREFIX_EXCEPTIONS:
        return word
    for prefix in ("magpa", "mang", "nang", "mag", "nag", "pag", "nakaka", "pinaka"):
        if word.startswith(prefix) and len(word) >= len(prefix) + 4:
            return word[len(prefix):]
    return word


def generate_ngrams(tokens, n=2):
    """Generates contiguous n-grams from a sequence of tokens."""
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def rank_bow_terms(bow_counts, top_n=30):
    """Ranks stems by frequency descending, breaking ties with institutional priority then alphabetically."""
    ranked = sorted(
        bow_counts.items(),
        key=lambda item: (-item[1], 0 if item[0] in INSTITUTIONAL_PRIORITY_STEMS else 1, item[0]),
    )
    return ranked[:top_n]


def preprocess_corpus(
    input_file=None,
    out_tokens_json=None,
    out_bow_csv=None,
    out_annotated_csv=None,
):
    if input_file is None:
        input_file = DEFAULT_INPUT_FILE
    if out_tokens_json is None:
        out_tokens_json = DEFAULT_TOKENS_JSON
    if out_bow_csv is None:
        out_bow_csv = DEFAULT_BOW_CSV
    if out_annotated_csv is None:
        out_annotated_csv = DEFAULT_ANNOTATED_CSV

    with open(input_file, "r", encoding="utf-8-sig") as f:
        documents = [line.strip() for line in f if line.strip()]

    all_tokens = []
    all_stems = []
    all_bigrams = []
    doc_records = []

    for idx, doc in enumerate(documents):
        raw_tokens = tokenize(doc)
        filtered_tokens = [
            t for t in raw_tokens if t not in STOPWORDS and len(t) > 1 and not t.isdigit()
        ]
        stems = [bilingual_stemmer(t) for t in filtered_tokens]
        bigrams = generate_ngrams(stems, n=2)

        all_tokens.extend(filtered_tokens)
        all_stems.extend(stems)
        all_bigrams.extend(bigrams)

        if idx < len(MIDTERM_METADATA):
            doc_id, src_file, sec_ref, intent, sentiment, cs = MIDTERM_METADATA[idx]
        else:
            doc_id, src_file, sec_ref, intent, sentiment, cs = (
                idx + 1, "unknown.txt", f"Doc #{idx + 1}", "GENERAL_COMMUNITY", "NEUTRAL_INQUIRY", "EN"
            )

        doc_records.append(
            {
                "doc_id": doc_id,
                "source_file": src_file,
                "section_ref": sec_ref,
                "intent_label": intent,
                "sentiment_polarity": sentiment,
                "code_switching": cs,
                "raw_text": doc,
                "tokens": filtered_tokens,
                "stems": stems,
                "bigrams": bigrams,
            }
        )

    bow_counts = Counter(all_stems)
    bigram_counts = Counter(all_bigrams)
    top_bigrams = [
        {"bigram": bg, "frequency": count}
        for bg, count in bigram_counts.items()
        if count >= 2
    ]
    top_bigrams.sort(key=lambda x: -x["frequency"])

    payload = {
        "project_title": "Curated Natural Language Resources and Multilingual Domain Lexicon for an SLU Institutional eGovernance Chatbot",
        "proponents": "Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)",
        "total_documents": len(documents),
        "total_tokens": len(all_tokens),
        "unique_surface_tokens": len(set(all_tokens)),
        "unique_vocabulary_size": len(bow_counts),
        "top_bigrams": top_bigrams,
        "documents": doc_records,
    }

    with open(out_tokens_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    total_freq = sum(bow_counts.values())
    top30 = rank_bow_terms(bow_counts, top_n=30)
    with open(out_bow_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Stem_Term", "Frequency", "Percentage_Coverage"])
        for rank, (term, count) in enumerate(top30, start=1):
            coverage = (count / total_freq) * 100.0
            writer.writerow([rank, term, count, f"{coverage:.2f}%"])

    with open(out_annotated_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Doc_ID",
            "Source_File",
            "Section_Reference",
            "Intent_Category",
            "Sentiment_Urgency",
            "Code_Switching",
            "Token_Count",
            "Cleaned_Text",
        ])
        for rec in doc_records:
            writer.writerow([
                rec["doc_id"],
                rec["source_file"],
                rec["section_ref"],
                rec["intent_label"],
                rec["sentiment_polarity"],
                rec["code_switching"],
                len(rec["tokens"]),
                rec["raw_text"],
            ])

    print(
        f"[OK] Preprocessed {len(documents)} docs | {len(all_tokens)} tokens | "
        f"{len(set(all_tokens))} unique surface | {len(bow_counts)} unique stems | "
        f"{len(top_bigrams)} recurring bigrams"
    )
    return payload, top30


if __name__ == "__main__":
    preprocess_corpus()
