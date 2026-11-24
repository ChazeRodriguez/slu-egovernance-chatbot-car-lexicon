# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Module: scripts/car_morphology.py
Description: Guarded multilingual morphological analyzer and lemmatizer spanning
             English, Filipino/Taglish, and Cordillera Administrative Region (CAR)
             languages (Ilocano, Northern Kankanaey, Ibaloi).
             Prevents English/Tagalog over-stemming while normalizing productive
             Philippine and Cordilleran affixes (ag-, panag-, man-, men-, na-, ma-,
             mag-, nag-, pag-, -um-, -in-).
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import re

# Base 265-word Midterm stopwords plus standalone Filipino verbal marker 'mag' and Ilocano/CAR particles
QUERY_STOPWORDS = set([
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
    '1st', 'like', 'yes', 'please', 'lowkey', 'haha', 'sis', 'guys',
    'real', 'hell', 'let', 'get', 'got', 'gave', 'make', 'made', 'know', 'knows',
    'said', 'told', 'met', 'went', 'go', 'going', 'looking', 'look', 'see', 'seen',
    # Filipino / Taglish (includes standalone 'mag' to prevent stem pollution)
    'ang', 'mga', 'sa', 'ng', 'na', 'ay', 'si', 'sina', 'ni', 'nina', 'kay', 'kina',
    'po', 'ko', 'mo', 'nila', 'natin', 'namin', 'ninyo', 'niyo', 'inyo', 'akin',
    'aking', 'iyo', 'kanila', 'kaniya', 'kanya', 'kami', 'tayo', 'kayo', 'sila',
    'siya', 'ako', 'ikaw', 'ka', 'kong', 'ba', 'pa', 'din', 'rin', 'raw', 'daw',
    'lang', 'lamang', 'naman', 'kasi', 'kung', 'at', 'o', 'para', 'dahil', 'upang',
    'kapag', 'pag', 'mag', 'nag', 'nang', 'may', 'meron', 'wala', 'walang', 'hindi', 'oo',
    'ito', 'iyan', 'iyon', 'yan', 'yun', 'yung', 'dito', 'diyan', 'doon', 'ganito',
    'ganyan', 'ganoon', 'ata', 'atang', 'pala', 'muna', 'talaga', 'dati', 'ngayon',
    'noong', 'tapos', 'pero', 'kaya', 'ulit', 'ano', 'anong', 'paano', 'bakit',
    'saan', 'sino', 'kailan', 'alin', 'ilan', 'magkano', 'pwede', 'puwede', 'kuya', 'ate',
    # High-frequency CAR function particles (preserve content lemmas in lexicon!)
    'ti', 'iti', 'ken', 'ket', 'ni', 'dagiti', 'kuma', 'nga', 'met', 'pay', 'laeng',
    'ja', 'nan', 'san', 'sin',
])

# Verified morphological lemma map (English + Filipino + CAR inflected forms)
LEMMA_MAP = {
    # English domain lemmas
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
    'shiftees': 'shiftee',
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
    'fees': 'fee',
    'payments': 'payment',
    'scholarships': 'scholarship',
    'scholars': 'scholar',
    'sanctions': 'sanction',
    'violations': 'violation',
    'offenses': 'offense',
    'counselors': 'counselor',
    'uniforms': 'uniform',
    'records': 'record',
    'windows': 'window',
    'classes': 'class',
    'books': 'book',
    'borrowing': 'borrow',
    'fines': 'fine',
    # Filipino inflected / infixed forms (-um-, -in-, reduplicated stems)
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
    'sumulat': 'sulat',
    'sinulat': 'sulat',
    'tinanong': 'tanong',
    'nagtanong': 'tanong',
    'magtanong': 'tanong',
    'bumagsak': 'bagsak',
    'lumiban': 'liban',
    'kumuha': 'kuha',
    'nagbayad': 'bayad',
    'magbayad': 'bayad',
    'pagbabayad': 'bayad',
    'pumasa': 'pasa',
    'nagpasa': 'pasa',
    'magpasa': 'pasa',
    'magpapasa': 'pasa',
    'nagtatanong': 'tanong',
    'magaaral': 'aral',
    'nag-aaral': 'aral',
    # Ilocano (ilo) verbal/nominal inflections -> canonical root
    'agadal': 'adal',
    'nagadal': 'adal',
    'panagadal': 'adal',
    'agsurat': 'surat',
    'nagsurat': 'surat',
    'panagsurat': 'surat',
    'agsao': 'sao',
    'nagsao': 'sao',
    'agbayad': 'bayad',
    'nagbayad': 'bayad',
    'panagbayad': 'bayad',
    'agkiddaw': 'kiddaw',
    'agdamag': 'damag',
    'agbasa': 'basa',
    'agtrabaho': 'trabaho',
    'agpaagas': 'agas',
    'agsubli': 'subli',
    'agsaludsod': 'saludsod',
    'agpalista': 'lista',
    'naimbag': 'imbag',
    'nasayaat': 'sayaat',
    'narigat': 'rigat',
    'nalaka': 'laka',
    # Northern Kankanaey (kne) verbal/nominal forms -> root
    'man-obla': 'obla',
    'men-obla': 'obla',
    'manobla': 'obla',
    'man-adal': 'adal',
    'men-adal': 'adal',
    'mensulat': 'sulat',
    'mansulat': 'sulat',
    'menbayad': 'bayad',
    'manbayad': 'bayad',
    'menkiddaw': 'kiddaw',
    'mensaludsod': 'saludsod',
    'men-enroll': 'enroll',
    'makisali': 'sali',
    # Ibaloi (ibl) verbal/nominal forms -> root
    'mapteng': 'peteng',
    'man-adal': 'adal',
    'manbayad': 'bayad',
    'mansulat': 'sulat',
    'mankalkali': 'kali',
    'man-obda': 'obda',
    'manobda': 'obda',
}

# Verified protection list preventing Filipino/CAR prefix rules from corrupting English or Tagalog roots
PREFIX_EXCEPTIONS = {
    'management', 'manager', 'mandatory', 'mandated', 'magnifying', 'magnify',
    'magnetic', 'magnet', 'magnitude', 'magnificent', 'magazine', 'magistrate',
    'magician', 'magical', 'magnesium', 'manganese', 'magnate', 'maggot',
    'maganda', 'magulang', 'magkano', 'magkakaroon', 'magiting', 'maginoo',
    'pageant', 'pagoda', 'pagination', 'paginated', 'pagan', 'paganism',
    'nagging', 'nagged', 'mangled', 'mangrove', 'mango', 'mangoes', 'manger',
    'pangalan', 'manggagawa', 'agency', 'agenda', 'agent', 'agents', 'aggregate',
    'aggressive', 'agile', 'agitate', 'agony', 'agree', 'agreed', 'agreement',
    'agriculture', 'agricultural', 'manuscript', 'manual', 'manually', 'manner',
    'maintain', 'maintenance', 'mental', 'mention', 'mentioned', 'mentor',
    'mentoring', 'menu', 'menus', 'material', 'materials', 'matter', 'mature',
    'maximum', 'major', 'majority', 'making', 'natural', 'nature', 'national',
    'nation', 'native', 'navigate', 'navigation', 'narrow', 'narrative',
}

# Productive Filipino & Cordilleran prefixes (ordered longest-first)
SAFE_FIL_CAR_PREFIXES = (
    ('panag', 'ilo'),
    ('pinaka', 'tl'),
    ('nakaka', 'tl'),
    ('magpa', 'tl'),
    ('nagpa', 'tl'),
    ('pagpa', 'tl'),
    ('mang', 'tl'),
    ('nang', 'tl'),
    ('man-', 'kne/ibl'),
    ('men-', 'kne'),
    ('mag-', 'tl'),
    ('nag-', 'tl'),
    ('pag-', 'tl'),
    ('mag', 'tl'),
    ('nag', 'tl'),
    ('pag', 'tl'),
)

# English endings that should NOT be prefix-stripped by Filipino rules
ENGLISH_SUFFIX_HINTS = (
    'tion', 'sion', 'ment', 'ness', 'ity', 'ify', 'ical', 'ician',
    'ium', 'ese', 'ate', 'ous', 'ive', 'able', 'ible', 'ing', 'ed',
)


def _looks_english_root(word):
    if word in PREFIX_EXCEPTIONS:
        return True
    for suf in ENGLISH_SUFFIX_HINTS:
        if word.endswith(suf) and len(word) >= len(suf) + 3:
            return True
    return False


def bilingual_stemmer(word):
    """
    Guarded multilingual lemmatizer & stemmer for English, Filipino/Taglish,
    and CAR languages (Ilocano, Northern Kankanaey, Ibaloi).
    """
    w = word.lower().strip()
    if not w:
        return w
    if w in LEMMA_MAP:
        return LEMMA_MAP[w]
    if w in PREFIX_EXCEPTIONS:
        return w

    # Check hyphenated Filipino/CAR prefixes first (always safe morphological boundary)
    for hyph_prefix in ('man-', 'men-', 'mag-', 'nag-', 'pag-', 'ag-', 'panag-'):
        if w.startswith(hyph_prefix) and len(w) >= len(hyph_prefix) + 3:
            stem = w[len(hyph_prefix):]
            return LEMMA_MAP.get(stem, stem)

    # Guard against corrupting English words with Filipino prefixes
    if _looks_english_root(w):
        return w

    for prefix, _lang in SAFE_FIL_CAR_PREFIXES:
        if '-' in prefix:
            continue
        if w.startswith(prefix) and len(w) >= len(prefix) + 4:
            candidate = w[len(prefix):]
            return LEMMA_MAP.get(candidate, candidate)

    return w


def analyze_morphology(word):
    """Returns structured morphological breakdown for UI inspection and lexicon QA."""
    w = word.lower().strip()
    stem = bilingual_stemmer(w)
    if stem == w:
        return {"surface": w, "lemma": w, "affix": "Root/Unchanged", "changed": False}
    if w in LEMMA_MAP:
        return {"surface": w, "lemma": stem, "affix": "Lexical/Infix Lemma Map", "changed": True}
    for prefix, lang in SAFE_FIL_CAR_PREFIXES:
        if w.startswith(prefix) and w[len(prefix):] == stem:
            return {"surface": w, "lemma": stem, "affix": f"{prefix} ({lang})", "changed": True}
    return {"surface": w, "lemma": stem, "affix": "Morphological Rule", "changed": True}
