# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/build_portal.py
Description: Single-source-of-truth static web portal generator (Canva EAG-QJ6Vos4
             Graph-Grid & Neon-Glow Dual-Theme Edition).
             Injects verified Midterm analytics, Expanded SLU Policies (52),
             176-entry SLU+CAR Electronic Lexicon, 350-doc Annotated Corpus,
             serialized Linear SVM / NB weights, and 5-fold CV / ablation
             evaluation metrics directly into slu_egovernance_chatbot_ui.html
             and dist/index.html (+ dist/netlify.toml security headers).
             Guarantees zero Python <-> Browser JS drift and strict DOM XSS safety.
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import csv
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPT_DIR)

import slu_chatbot_engine as eng
from car_morphology import (
    QUERY_STOPWORDS,
    LEMMA_MAP,
    PREFIX_EXCEPTIONS,
    SAFE_FIL_CAR_PREFIXES,
    ENGLISH_SUFFIX_HINTS,
)
from data_preprocessing import STOPWORDS as MIDTERM_STOPWORDS


def _safe_json_for_script(obj):
    """Serializes JSON safely for embedding inside HTML <script> tags (escapes '</' and U+2028/2029)."""
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return raw.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def load_portal_bundle():
    with open(os.path.join(REPO_ROOT, "preprocessed_tokens.json"), encoding="utf-8") as f:
        midterm_pt = json.load(f)
    with open(os.path.join(REPO_ROOT, "corpus_bow_summary.csv"), encoding="utf-8") as f:
        midterm_bow = list(csv.DictReader(f))
    with open(os.path.join(REPO_ROOT, "data", "expanded", "slu_official_policies_v2.json"), encoding="utf-8") as f:
        policies_v2 = json.load(f)
    with open(os.path.join(REPO_ROOT, "data", "expanded", "annotated_corpus_expanded.csv"), encoding="utf-8-sig") as f:
        corpus_v2 = list(csv.DictReader(f))
    with open(os.path.join(REPO_ROOT, "models", "intent_classifier.json"), encoding="utf-8") as f:
        ml_model = json.load(f)
    with open(os.path.join(REPO_ROOT, "models", "evaluation_report.json"), encoding="utf-8") as f:
        eval_report = json.load(f)

    lexicon_v2 = eng.load_expanded_lexicon()

    # Format policies exactly as Python SLUChatbotEngine(dataset='expanded') loads them
    engine_docs = [
        {
            "doc_id": int(p["doc_id"]),
            "source_file": p["source_file"],
            "source_url": p.get("source_url", ""),
            "section_ref": p["section_ref"],
            "intent_label": p["intent_label"],
            "sentiment_polarity": "AUTHORITATIVE_POLICY",
            "code_switching": "EN",
            "raw_text": eng.clean_text(p["raw_text"]),
            "display_text": p["raw_text"],
        }
        for p in policies_v2
    ]

    bundle = {
        "engineConfig": {
            "queryStopwords": sorted(QUERY_STOPWORDS),
            "midtermStopwords": sorted(MIDTERM_STOPWORDS),
            "lemmaMap": LEMMA_MAP,
            "prefixExceptions": sorted(PREFIX_EXCEPTIONS),
            "englishSuffixHints": list(ENGLISH_SUFFIX_HINTS),
            "safePrefixes": [p for p, _ in SAFE_FIL_CAR_PREFIXES if "-" not in p],
            "querySynonyms": eng.QUERY_SYNONYMS,
            "greetingWords": sorted(eng.GREETING_WORDS),
            "policyNumericTokens": sorted(eng.POLICY_NUMERIC_TOKENS),
            "comparativeMarkers": sorted(eng.COMPARATIVE_MARKERS),
            "filipinoMarkers": sorted(eng.FILIPINO_MARKERS),
            "carGreetingMap": eng.CAR_NATIVE_GREETING_MAP,
            "alpha": 0.25,
            "beta": 0.30,
            "minConfidence": 0.14,
        },
        "policies": engine_docs,
        "lexicon": lexicon_v2,
        "mlModel": ml_model,
        "midtermStats": {
            "totalDocuments": midterm_pt["total_documents"],
            "totalTokens": midterm_pt["total_tokens"],
            "uniqueSurface": midterm_pt["unique_surface_tokens"],
            "uniqueStems": midterm_pt["unique_vocabulary_size"],
            "bowTop30": [
                {
                    "rank": int(r["Rank"]),
                    "term": r["Stem_Term"],
                    "freq": int(r["Frequency"]),
                    "cov": r["Percentage_Coverage"],
                }
                for r in midterm_bow
            ],
            "topBigrams": midterm_pt["top_bigrams"],
        },
        "expandedCorpus": [
            {
                "id": int(r["Doc_ID"]),
                "sourceType": r["Source_Type"],
                "ref": r["Section_Reference"],
                "intent": r["Intent_Category"],
                "sent": r["Sentiment_Urgency"],
                "lang": r["Code_Switching"],
                "text": r["Cleaned_Text"],
            }
            for r in corpus_v2
        ],
        "evalReport": eval_report,
    }
    return bundle


ENGINE_JS_CODE = r"""
// ============================================================================
// DETERMINISTIC CLIENT-SIDE NLP + HYBRID ML ENGINE (PARITY WITH PYTHON ENGINE)
// ============================================================================
function createSLUChatbotEngine(BUNDLE) {
  const CFG = BUNDLE.engineConfig;
  const QUERY_STOPWORDS = new Set(CFG.queryStopwords);
  const MIDTERM_STOPWORDS = new Set(CFG.midtermStopwords);
  const LEMMA_MAP = CFG.lemmaMap;
  const PREFIX_EXCEPTIONS = new Set(CFG.prefixExceptions);
  const ENGLISH_SUFFIX_HINTS = CFG.englishSuffixHints;
  const SAFE_PREFIXES = CFG.safePrefixes;
  const QUERY_SYNONYMS = CFG.querySynonyms;
  const GREETING_WORDS = new Set(CFG.greetingWords);
  const POLICY_NUMERIC_TOKENS = new Set(CFG.policyNumericTokens);
  const COMPARATIVE_MARKERS = new Set(CFG.comparativeMarkers || []);
  const FILIPINO_MARKERS = new Set(CFG.filipinoMarkers);
  const CAR_GREETING_MAP = CFG.carGreetingMap;
  const CAR_HYPHENS = ["dap-ay", "man-obla", "men-obla", "pan-adal", "man-adal"];

  const EXPLICIT_CONTRACTIONS = [
    [/\bi'll\b/g, "i will"],
    [/\bill\b(?=\s+(?:still|be|just|never|always|go|send|call|wait|try|ask|do|have|get|make|take|see|tell|give|come|check|submit|pay|enroll|shift|transfer)\b)/g, "i will"],
    [/\bi'm\b/g, "i am"],
    [/\bit's\b/g, "it is"],
    [/\bthat's\b/g, "that is"],
    [/\bwhat's\b/g, "what is"],
    [/\bwhere's\b/g, "where is"],
    [/\bwho's\b/g, "who is"],
    [/\bthere's\b/g, "there is"],
    [/\bhere's\b/g, "here is"],
    [/\bhe's\b/g, "he is"],
    [/\bshe's\b/g, "she is"],
    [/\blet's\b/g, "let us"],
    [/\bcan't\b/g, "can not"],
    [/\bwon't\b/g, "will not"],
    [/\bdon't\b/g, "do not"],
    [/\bdoesn't\b/g, "does not"],
    [/\bdidn't\b/g, "did not"],
    [/n't\b/g, " not"],
    [/'re\b/g, " are"],
    [/'d\b/g, " would"],
    [/'ll\b/g, " will"],
    [/'ve\b/g, " have"],
    [/([a-z0-9]+)'s\b/g, "$1"]
  ];

  const FIL_CLITICS = [
    [/\bba't\b/g, "bakit"],
    [/\bdi'ba\b|\bdiba\b/g, "hindi ba"],
    [/\bsa'kin\b|\bsakin\b/g, "sa akin"],
    [/\bsa'yo\b|\bsayo\b/g, "sa iyo"],
    [/\bn'yo\b|\bnyo\b|\bniyo\b/g, "ninyo"],
    [/\bano't\b/g, "ano at"],
    [/\bsamin\b/g, "sa amin"],
    [/\bnung\b/g, "noong"],
    [/\bngaun\b/g, "ngayon"],
    [/\bung\b/g, "yung"],
    [/\bnalang\b/g, "na lang"],
    [/\bambilat\b/g, "ambigat"],
    [/\brember\b/g, "remember"],
    [/\bmake\s+tawad\b/g, "make tawid"],
    [/\bpedxing\b/g, "pedestrian crossing"],
    [/\bihyk\b/g, "i hope you know"],
    [/\bconvo\b/g, "conversation"],
    [/\bwth\b/g, "what the hell"],
    [/\bfr\b/g, "for real"],
    [/\bdp\b/g, "downpayment"],
    [/\blike{2,}\b/g, "like"],
    [/\bh+a+(?:h+a+)+h*\b/g, "haha"]
  ];

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function cleanText(raw) {
    let t = String(raw || "").replace(/\ufeff/g, "").toLowerCase();
    t = t.replace(/\[.*?\]/g, " ");
    t = t.replace(/#slufreedomwall\d+/g, " ");
    t = t.replace(/https?:\/\/\S+|www\.\S+/g, " ");
    t = t.replace(/\((submitted:.*?|public post archive)\)/g, " ");
    t = t.replace(/^(q\d+|a\d+)\s*:\s*/g, "");
    t = t.replace(/^section\s+\d+\.\s*/g, "");
    t = t.replace(/(?<=\d),(?=\d)/g, "");
    t = t.replace(/(\d+)\s*%/g, "$1 percent");
    t = t.replace(/\u2019/g, "'").replace(/\u2018/g, "'").replace(/\u2014/g, " ").replace(/\u2013/g, " ");
    for (const [pat, rep] of FIL_CLITICS) t = t.replace(pat, rep);
    for (const [pat, rep] of EXPLICIT_CONTRACTIONS) t = t.replace(pat, rep);
    for (const tok of CAR_HYPHENS) {
      const ph = tok.replace(/-/g, "carhyphen");
      t = t.replace(new RegExp("\\b" + escapeRegex(tok) + "\\b", "g"), ph);
    }
    t = t.replace(/[^a-z0-9\s\.\?\!]/g, " ");
    for (const tok of CAR_HYPHENS) {
      const ph = tok.replace(/-/g, "carhyphen");
      t = t.split(ph).join(tok);
    }
    t = t.replace(/\b(downpayment|samcis|seait|sonahbs|tor|cog|fda|mls|qe|pathfit|rfid)\s+\1\b/g, "$1");
    t = t.replace(/\?{2,}/g, "?");
    t = t.replace(/!{2,}/g, "!");
    t = t.replace(/\.{2,}/g, ".");
    t = t.replace(/[\.\?\!]{2,}/g, ".");
    t = t.replace(/\s+([\.\?\!])/g, "$1");
    t = t.replace(/\s+/g, " ").trim();
    return t;
  }

  function tokenize(text) {
    return (text.toLowerCase().match(/\b[a-z0-9]+(?:-[a-z0-9]+)?\b/g) || []);
  }

  function looksEnglishRoot(word) {
    if (PREFIX_EXCEPTIONS.has(word)) return true;
    for (const suf of ENGLISH_SUFFIX_HINTS) {
      if (word.endsWith(suf) && word.length >= suf.length + 3) return true;
    }
    return false;
  }

  function bilingualStemmer(word) {
    const w = word.toLowerCase().trim();
    if (!w) return w;
    if (Object.prototype.hasOwnProperty.call(LEMMA_MAP, w)) return LEMMA_MAP[w];
    if (PREFIX_EXCEPTIONS.has(w)) return w;
    for (const hp of ["man-", "men-", "mag-", "nag-", "pag-", "ag-", "panag-"]) {
      if (w.startsWith(hp) && w.length >= hp.length + 3) {
        const stem = w.slice(hp.length);
        return Object.prototype.hasOwnProperty.call(LEMMA_MAP, stem) ? LEMMA_MAP[stem] : stem;
      }
    }
    if (looksEnglishRoot(w)) return w;
    for (const p of SAFE_PREFIXES) {
      if (w.startsWith(p) && w.length >= p.length + 4) {
        const cand = w.slice(p.length);
        return Object.prototype.hasOwnProperty.call(LEMMA_MAP, cand) ? LEMMA_MAP[cand] : cand;
      }
    }
    return w;
  }

  function generateBigrams(tokens) {
    const out = [];
    for (let i = 0; i < tokens.length - 1; i++) out.push(tokens[i] + " " + tokens[i + 1]);
    return out;
  }

  function extractTokensAndStems(text, forQuery) {
    const rawTokens = tokenize(text);
    const stopset = forQuery ? QUERY_STOPWORDS : MIDTERM_STOPWORDS;
    const filtered = [];
    for (const t of rawTokens) {
      if (stopset.has(t) || t.length <= 1) continue;
      if (/^\d+$/.test(t)) {
        const n = parseInt(t, 10);
        if (forQuery && (POLICY_NUMERIC_TOKENS.has(t) || (n >= 50 && n <= 99))) {
          filtered.push(t);
        }
        continue;
      }
      filtered.push(t);
    }
    const stems = filtered.map(bilingualStemmer);
    return { rawTokens, filtered, stems };
  }

  // Build policy TF-IDF index
  const docs = BUNDLE.policies.map(d => ({ ...d }));
  const N = docs.length;
  const df = Object.create(null);
  const docVecs = [];
  const docNorms = [];

  for (const d of docs) {
    const { filtered, stems } = extractTokensAndStems(d.raw_text, false);
    const bigrams = generateBigrams(stems);
    d.tokens = filtered;
    d.stems = stems;
    d.bigrams = bigrams;
    const uniq = new Set([...stems, ...bigrams]);
    uniq.forEach(f => { df[f] = (df[f] || 0) + 1; });
  }
  for (const d of docs) {
    const tfMap = Object.create(null);
    for (const f of [...d.stems, ...d.bigrams]) tfMap[f] = (tfMap[f] || 0) + 1;
    const vec = Object.create(null);
    let normSq = 0;
    for (const [f, tf] of Object.entries(tfMap)) {
      const idf = Math.log((1 + N) / (1 + (df[f] || 0))) + 1;
      const tfW = 1 + Math.log(tf);
      const w = tfW * idf;
      vec[f] = w;
      normSq += w * w;
    }
    docVecs.push(vec);
    docNorms.push(normSq > 0 ? Math.sqrt(normSq) : 1);
  }

  function matchLexicon(rawQuery, rawTokens, stems) {
    const matched = [];
    const rawLower = rawQuery.toLowerCase();
    const tokSet = new Set([...rawTokens, ...stems, ...tokenize(rawLower)]);
    for (const e of BUNDLE.lexicon) {
      const natSet = new Set(e.native_aliases || [e.lemma]);
      const semSet = new Set(e.semantic_aliases || []);
      let isNative = tokSet.has(e.lemma);
      if (!isNative) {
        for (const a of natSet) { if (tokSet.has(a)) { isNative = true; break; } }
      }
      if (!isNative) {
        const re = new RegExp("(?<![a-z0-9])" + escapeRegex(e.lemma) + "(?![a-z0-9])");
        if (re.test(rawLower)) isNative = true;
      }
      let isSemantic = false;
      if (!isNative) {
        for (const a of semSet) { if (tokSet.has(a)) { isSemantic = true; break; } }
      }
      if (isNative || isSemantic) {
        matched.push({ ...e, match_type: isNative ? "native" : "semantic" });
      }
    }
    return matched;
  }

  function detectCodeSwitching(rawTokens, matchedLex) {
    const carLangs = new Set(["ilo", "kne", "ibl", "kne-tl"]);
    const hasNativeCar = matchedLex.some(e => carLangs.has(e.lang) && e.match_type === "native");
    const hasFil = rawTokens.some(t => FILIPINO_MARKERS.has(t));
    if (hasNativeCar) return "CAR-TL-EN";
    if (hasFil) return "TL-EN";
    return "EN";
  }

  function predictMlIntent(stems, bigrams) {
    const m = BUNDLE.mlModel;
    if (!m) return { intent: null, confidence: 0, probs: {}, topIntents: [] };
    const counts = Object.create(null);
    for (const f of [...stems, ...bigrams]) counts[f] = (counts[f] || 0) + 1;
    const vec = Object.create(null);
    let normSq = 0;
    for (const [feat, tf] of Object.entries(counts)) {
      const idx = m.vocab[feat];
      if (idx !== undefined) {
        const w = (1 + Math.log(tf)) * m.idf[idx];
        vec[idx] = w;
        normSq += w * w;
      }
    }
    if (normSq <= 0) return { intent: null, confidence: 0, probs: {}, topIntents: [] };
    const inv = 1 / Math.sqrt(normSq);
    for (const idx of Object.keys(vec)) vec[idx] *= inv;

    const classes = m.classes;
    const scores = [];
    if (m.model_type === "multinomial_nb") {
      for (let ci = 0; ci < classes.length; ci++) {
        let s = m.log_priors[ci];
        const lp = m.log_probs[ci];
        for (const [idxStr, val] of Object.entries(vec)) s += val * lp[Number(idxStr)];
        scores.push(s);
      }
    } else {
      for (let ci = 0; ci < classes.length; ci++) {
        let s = m.biases[ci];
        const cw = m.weights[ci];
        for (const [idxStr, val] of Object.entries(vec)) s += cw[Number(idxStr)] * val;
        scores.push(s);
      }
    }
    const maxS = Math.max(...scores);
    const exps = scores.map(s => Math.exp(s - maxS));
    const denom = exps.reduce((a, b) => a + b, 0);
    const probs = exps.map(e => e / denom);
    const probsMap = Object.create(null);
    const ranked = [];
    let bestI = 0;
    for (let i = 0; i < classes.length; i++) {
      probsMap[classes[i]] = probs[i];
      if (probs[i] >= 0.10) ranked.push({ intent: classes[i], confidence: Number(probs[i].toFixed(4)) });
      if (probs[i] > probs[bestI]) bestI = i;
    }
    ranked.sort((a, b) => b.confidence - a.confidence);
    return { intent: classes[bestI], confidence: probs[bestI], probs: probsMap, topIntents: ranked.slice(0, 2) };
  }

  function answerQuery(userQuery, topK = 3) {
    const cleaned = cleanText(userQuery);
    const { rawTokens, filtered, stems } = extractTokensAndStems(cleaned, true);
    const bigrams = generateBigrams(stems);
    const matchedLex = matchLexicon(userQuery, rawTokens, stems);
    const codeSwitching = detectCodeSwitching(rawTokens, matchedLex);

    let carGreeting = "";
    for (const lc of ["ilo", "kne", "ibl"]) {
      if (matchedLex.some(e => e.lang === lc && e.match_type === "native")) {
        carGreeting = CAR_GREETING_MAP[lc];
        break;
      }
    }

    // Pure greeting check
    const nonGreeting = filtered.filter(t => !GREETING_WORDS.has(t) && !FILIPINO_MARKERS.has(t));
    const hasGreeting = rawTokens.some(t => GREETING_WORDS.has(t));
    const hasNonGreetLex = matchedLex.some(e => e.intent !== "CAR_REGIONAL_LEXICON");
    if (rawTokens.length > 0 && hasGreeting && nonGreeting.length === 0 && !hasNonGreetLex) {
      return {
        raw_query: userQuery,
        cleaned_query: cleaned,
        filtered_tokens: filtered,
        stems,
        bigrams,
        code_switching: codeSwitching,
        predicted_intent: "GREETING",
        ml_intent: null,
        ml_confidence: 0,
        matched_lexicon: matchedLex,
        top_documents: [],
        is_greeting: true,
        is_fallback: false,
        confidence: 1.0,
        car_greeting: carGreeting,
        synthesized_response:
          (carGreeting || "Hello, Louisian! ") +
          "I am the SLU eGovernance Student Support Assistant. Ask me in English, Taglish, Ilocano, Northern Kankanaey, or Ibaloi about URO enrollment, TOR/COG requests, shifting & qualifying exams, grading/FDA rules, exam permits & academic integrity, dress code, tuition/finance, clinic/PATHFIT, campus safety, or libraries & labs."
      };
    }

    const expandedStems = [...stems];
    const lexIntents = new Set();
    const rawTokSet = new Set(rawTokens);
    const rawStemSet = new Set(stems);
    const isComparative = rawTokens.some(t => COMPARATIVE_MARKERS.has(t));

    for (const tok of filtered) {
      if (/^\d+$/.test(tok)) {
        const val = parseInt(tok, 10);
        if (val >= 50 && val < 75) {
          expandedStems.push("grade", "below", "75", "failure", "minimum", "passing", "retention");
          lexIntents.add("HANDBOOK_GRADING_FDA");
        } else if (val === 75) {
          expandedStems.push("grade", "75", "minimum", "passing", "retention");
          lexIntents.add("HANDBOOK_GRADING_FDA");
        } else if ((val === 88 || val === 91 || val === 93) && ["honor","latin","laude","summa","magna","cum","gwa","graduate","graduation","grade"].some(k => rawStemSet.has(k))) {
          expandedStems.push("latin", "honor", "summa", "magna", "cum", "laude", "93", "91", "88", "residency");
          lexIntents.add("HANDBOOK_GRADING_FDA");
        } else if (val === 20 && ["absence","absent","fda","percent","class"].some(k => rawStemSet.has(k))) {
          expandedStems.push("absence", "fda", "20", "percent", "dropped");
          lexIntents.add("HANDBOOK_GRADING_FDA");
        } else if (val === 10173) {
          expandedStems.push("republic", "act", "data", "privacy", "digital", "platform");
          lexIntents.add("CAMPUS_HEALTH_SAFETY");
        }
      }
    }

    const qAll = new Set([...rawTokens, ...stems]);
    if (["latin","laude","summa","magna"].some(k => qAll.has(k)) || (qAll.has("cum") && (qAll.has("laude") || qAll.has("honor"))) || qAll.has("pammadayaw")) {
      expandedStems.push("latin", "honor", "summa", "magna", "cum", "laude", "93", "91", "88", "residency", "120");
      lexIntents.add("HANDBOOK_GRADING_FDA");
    }
    if ((qAll.has("dean") && ["list","lister","honor","honors","gwa","discount","scholar","scholarship"].some(k => qAll.has(k))) || qAll.has("deanslist")) {
      expandedStems.push("dean", "list", "first", "second", "honor", "92", "88", "scholarship");
      lexIntents.add("TUITION_FINANCE");
    }
    const hasAbsWord = ["absent","absence","absences","drop","dropped","fda","liway","liwat"].some(k => qAll.has(k));
    const hasSpecAbs = ["permanent","permanently","mwf","tth","mth","54","consecutive","readmission","hour","hours","11th","8th"].some(k => qAll.has(k));
    const hasCntAbs = ["absent","absence","absences","liway","liwat"].some(k => qAll.has(k)) && ["many","ilan","mano","hour","hours","oras","day","days","araw","limit","before","sakbay","bago"].some(k => qAll.has(k));
    if ((hasAbsWord && hasSpecAbs) || hasCntAbs) {
      expandedStems.push("54", "11th", "8th", "mwf", "tth", "consecutive", "readmission", "slip", "permanent", "fda", "20");
      lexIntents.add("HANDBOOK_GRADING_FDA");
      if (isComparative || qAll.has("voluntary") || qAll.has("official")) {
        lexIntents.add("URO_SUBJECT_ADJUSTMENT");
      }
    }

    for (const e of matchedLex) {
      if (e.intent !== "CAR_REGIONAL_LEXICON") {
        if (e.lemma === "mls" && ["laboratory","pipette","material","budget","equipment","litmus","breakage"].some(k => rawStemSet.has(k))) {
          lexIntents.add("CAMPUS_FACILITIES_LAB");
        } else if (e.lemma === "rfid" && ["gate","gates","enter","entering","borrow","lending","lent","agipabulod"].some(k => rawTokSet.has(k))) {
          lexIntents.add("CAMPUS_DECORUM_DRESSCODE");
        } else if (e.lemma === "rfid" && ["validate","validation","deposit","posted"].some(k => rawTokSet.has(k))) {
          lexIntents.add("URO_ENROLLMENT_PORTAL");
        } else if (["laude","liway","liwat","pammadayaw"].includes(e.lemma)) {
          lexIntents.add("HANDBOOK_GRADING_FDA");
        } else {
          lexIntents.add(e.intent);
        }
      }
      if (e.lemma === "agadal") expandedStems.push("course", "subject", "study");
      else if (e.lemma === "agsurat") expandedStems.push("request", "official", "transcript", "form");
      else if (e.lemma === "inayan") expandedStems.push("academic", "integrity", "dishonesty", "cheating", "plagiarism");
      else if (e.lemma === "tongtong") expandedStems.push("disciplinary", "board", "conduct", "mediation");
      else if (e.lemma === "dp") expandedStems.push("downpayment", "tuition", "payment");
      else if (e.lemma === "fda") expandedStems.push("fda", "absence", "failure", "dropped");
      else if (e.lemma === "agbayad") expandedStems.push("payment", "downpayment", "tuition", "cashier");
      else if (e.lemma === "agpaagas") expandedStems.push("clinic", "medical", "health", "consultation");
      else if (e.lemma === "liway" || e.lemma === "liwat") expandedStems.push("absence", "fda", "20", "percent", "dropped", "readmission");
      else if (e.lemma === "pammadayaw" || e.lemma === "laude") expandedStems.push("latin", "honor", "summa", "magna", "cum", "laude", "93", "91", "88");
      else if (e.lemma === "kasera" || e.lemma === "agawid") expandedStems.push("residence", "hall", "dormitory", "curfew");
    }

    for (const tok of [...new Set([...rawTokens, ...stems])].sort()) {
      if (Object.prototype.hasOwnProperty.call(QUERY_SYNONYMS, tok)) {
        expandedStems.push(...QUERY_SYNONYMS[tok]);
      }
    }

    const sSet = new Set(expandedStems);
    if (["shifting","shift","transferee","qe","qualifying","seait","sonahbs","probation","qpi"].some(k => sSet.has(k))) {
      lexIntents.add("ACADEMIC_SHIFTING_TRANSFER");
      if (["submission","window","adding","dropping","adjustment"].some(k => sSet.has(k))) {
        lexIntents.add("URO_SUBJECT_ADJUSTMENT");
      }
    }
    if (["adding","dropping","drop","add","adjustment","petition","crossenroll"].some(k => sSet.has(k))) lexIntents.add("URO_SUBJECT_ADJUSTMENT");
    if (["tor","cog","transcript","clearance","graduation","honorable","dismissal","cgmc","cav"].some(k => sSet.has(k))) lexIntents.add("URO_ENROLLMENT_TOR");
    if (["portal","advising","continuing","enrollment","enroll","loa","returnee","shortterm","summer","validate","validation"].some(k => sSet.has(k))) lexIntents.add("URO_ENROLLMENT_PORTAL");
    if (["grade","passing","retention","fda","absence","bagsak","laude","latin","readmission","inc","nfe"].some(k => sSet.has(k))) lexIntents.add("HANDBOOK_GRADING_FDA");
    if (["permit","proctor","plagiarism","cheating","dishonesty","mobile","phone","device","disciplinary"].some(k => sSet.has(k)) || (sSet.has("rfid") && !["gate","gates","borrow","lending","validate","validation"].some(k => sSet.has(k)))) lexIntents.add("EXAM_PERMIT_INTEGRITY");
    if (["clinic","medical","pathfit","evacuation","seismic","calamity","oval","privacy","10173","libelous","harassment","ill","sick","dental","security","typhoon","monsoon","suspension"].some(k => sSet.has(k))) lexIntents.add("CAMPUS_HEALTH_SAFETY");
    if (["uniform","dress","wash","slipper","sando","attire","shorts","hair","grooming","piercing"].some(k => sSet.has(k)) || (sSet.has("rfid") && ["gate","gates","borrow","lending"].some(k => sSet.has(k)))) lexIntents.add("CAMPUS_DECORUM_DRESSCODE");
    if (["tuition","downpayment","fee","installment","accounting","cashier","promissory","deanslist","refund"].some(k => sSet.has(k))) {
      lexIntents.add("TUITION_FINANCE");
      if (sSet.has("validate") && sSet.has("rfid")) {
        lexIntents.delete("TUITION_FINANCE");
        lexIntents.add("URO_ENROLLMENT_PORTAL");
      }
      if (sSet.has("refund")) {
        lexIntents.delete("URO_SUBJECT_ADJUSTMENT");
      }
    }
    if (["laboratory","pipette","litmus","facility","equipment","library","breakage","dormitory","residence","curfew"].some(k => sSet.has(k))) lexIntents.add("CAMPUS_FACILITIES_LAB");
    if (["scholarship","scholar","counseling","guidance","mental","wellness","ambigat"].some(k => sSet.has(k))) {
      if (["scholarship","scholar","deanslist"].some(k => sSet.has(k))) lexIntents.add("TUITION_FINANCE");
      else lexIntents.add("CAMPUS_HEALTH_SAFETY");
    }

    const mlPred = predictMlIntent(stems, bigrams);
    const expandedBigrams = generateBigrams(expandedStems);
    const qTf = Object.create(null);
    for (const f of [...expandedStems, ...bigrams, ...expandedBigrams]) qTf[f] = (qTf[f] || 0) + 1;
    const qVec = Object.create(null);
    let qNormSq = 0;
    for (const [f, tf] of Object.entries(qTf)) {
      const idf = Math.log((1 + N) / (1 + (df[f] || 0))) + 1;
      const tfW = 1 + Math.log(tf);
      const w = tfW * idf;
      qVec[f] = w;
      qNormSq += w * w;
    }
    const qNorm = qNormSq > 0 ? Math.sqrt(qNormSq) : 1;

    const effAlpha = (BUNDLE.mlModel && mlPred.intent && mlPred.confidence >= 0.25) ? 0.14 : CFG.alpha;

    const scored = docs.map((d, idx) => {
      const dVec = docVecs[idx];
      const dNorm = docNorms[idx];
      let dot = 0;
      for (const [f, w] of Object.entries(qVec)) {
        if (dVec[f]) dot += w * dVec[f];
      }
      const cos = dot / (qNorm * dNorm);
      const intentMatch = lexIntents.has(d.intent_label) ? 1 : 0;
      const mlProb = (mlPred.probs && mlPred.probs[d.intent_label]) ? mlPred.probs[d.intent_label] : 0;
      const mlTerm = (mlProb >= 0.16) ? (CFG.beta * mlProb) : 0;
      const isPol = d.sentiment_polarity === "AUTHORITATIVE_POLICY";
      const authBonus = (isPol && (cos > 0.02 || intentMatch > 0 || mlTerm > 0)) ? 0.15 : 0;
      const boost = (effAlpha * intentMatch) + mlTerm + authBonus;
      const finalScore = cos + boost;
      return {
        doc_id: d.doc_id,
        source_file: d.source_file,
        source_url: d.source_url,
        section_ref: d.section_ref,
        intent_label: d.intent_label,
        sentiment_polarity: d.sentiment_polarity,
        cosine_similarity: Number(cos.toFixed(4)),
        intent_boost: Number(boost.toFixed(4)),
        final_score: Number(finalScore.toFixed(4)),
        raw_text: d.display_text || d.raw_text
      };
    });

    const policyCands = scored
      .filter(d => d.sentiment_polarity === "AUTHORITATIVE_POLICY" && d.final_score > 0)
      .sort((a, b) => (b.final_score - a.final_score) || (b.cosine_similarity - a.cosine_similarity) || (a.doc_id - b.doc_id));

    const bestPolicy = policyCands[0] || null;
    const strongBoost = Boolean(bestPolicy && bestPolicy.intent_boost > 0.16);
    const hasEvidence = Boolean(
      bestPolicy &&
      bestPolicy.final_score >= CFG.minConfidence &&
      (
        (strongBoost && (bestPolicy.cosine_similarity >= 0.025 || bestPolicy.intent_boost >= 0.35)) ||
        (bestPolicy.cosine_similarity >= 0.08)
      )
    );

    if (!hasEvidence) {
      return {
        raw_query: userQuery,
        cleaned_query: cleaned,
        filtered_tokens: filtered,
        stems,
        bigrams,
        code_switching: codeSwitching,
        predicted_intent: "OUT_OF_DOMAIN",
        ml_intent: mlPred.intent,
        ml_confidence: Number(mlPred.confidence.toFixed(4)),
        ml_top_intents: mlPred.topIntents || [],
        is_comparative: isComparative,
        matched_lexicon: matchedLex,
        top_documents: [],
        is_greeting: false,
        is_fallback: true,
        confidence: bestPolicy ? bestPolicy.final_score : 0,
        car_greeting: carGreeting,
        synthesized_response:
          (carGreeting || "") +
          "I could not find an authoritative Saint Louis University policy matching your query with sufficient confidence. Please rephrase with specific SLU terms (e.g., Latin honors, FDA, TOR, COG, shifting, QE, RFID, promissory note, wash day, clinic, tuition) or contact URO, OSAS, Finance Office, Health Services, or Security (Gates 1 & 2)."
      };
    }

    const topMatches = policyCands.slice(0, topK);
    const chosen = [topMatches[0]];
    const runnerMin = isComparative ? Math.max(0.30, topMatches[0].final_score * 0.58) : Math.max(0.35, topMatches[0].final_score * 0.72);
    if (topMatches.length > 1 && topMatches[1].final_score >= runnerMin) {
      chosen.push(topMatches[1]);
    }

    return {
      raw_query: userQuery,
      cleaned_query: cleaned,
      filtered_tokens: filtered,
      stems,
      bigrams,
      code_switching: codeSwitching,
      predicted_intent: topMatches[0].intent_label,
      ml_intent: mlPred.intent,
      ml_confidence: Number(mlPred.confidence.toFixed(4)),
      ml_top_intents: mlPred.topIntents || [],
      is_comparative: isComparative,
      matched_lexicon: matchedLex,
      top_documents: topMatches,
      chosen_documents: chosen,
      is_greeting: false,
      is_fallback: false,
      confidence: topMatches[0].final_score,
      car_greeting: carGreeting,
      synthesized_response:
        carGreeting +
        "Based on official Saint Louis University regulations: " +
        chosen.map(d => "[" + d.section_ref + "] " + d.raw_text.charAt(0).toUpperCase() + d.raw_text.slice(1)).join(" | ")
    };
  }

  return { cleanText, tokenize, bilingualStemmer, generateBigrams, answerQuery };
}
"""


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none';">
<title>SLU eGovernance Multilingual Chatbot &amp; CAR Electronic Lexicon Portal | Group 2 – AiNomally</title>
<style>
  :root {
    --slu-navy: #0D0A1A;
    --slu-indigo: #002855;
    --slu-royal: #4F46E5;
    --accent-coral: #EB6A48;
    --accent-coral-hover: #C84B2B;
    --accent-pink: #DB2777;
    --slu-gold: #D97706;
    --slu-gold-bright: #FACC15;
    --bg-canvas: #FAF8F3;
    --grid-line: rgba(142, 194, 222, 0.42);
    --surface: #FFFFFF;
    --surface-subtle: #F3F0E8;
    --chrome-bg: #E2E5EC;
    --chrome-border: #CBD5E1;
    --text-primary: #0D0A1A;
    --text-secondary: #334155;
    --text-muted: #475569;
    --border: #CBD5E1;
    --border-strong: #94A3B8;
    --shadow-card: 4px 4px 0px #0D0A1A;
    --mono-font: ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Courier New', monospace;
    --success-bg: #DCFCE7;
    --success-fg: #14532D;
    --warn-bg: #FEF3C7;
    --warn-fg: #78350F;
    --info-bg: #EDE9FE;
    --info-fg: #4C1D95;
    --danger-bg: #FCE7F3;
    --danger-fg: #831843;
    --focus-ring: 0 0 0 3px rgba(235, 106, 72, 0.45);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
  }
  [data-theme="dark"] {
    --slu-navy: #141026;
    --slu-indigo: #1E163B;
    --slu-royal: #7C3AED;
    --accent-coral: #EB6A48;
    --accent-coral-hover: #F97316;
    --accent-pink: #EC4899;
    --bg-canvas: #0B0817;
    --grid-line: rgba(139, 92, 246, 0.19);
    --surface: #141026;
    --surface-subtle: #1C1735;
    --chrome-bg: #18122E;
    --chrome-border: #342A5E;
    --text-primary: #F8FAFC;
    --text-secondary: #E2E8F0;
    --text-muted: #CBD5E1;
    --border: #342A5E;
    --border-strong: #6D5BAE;
    --shadow-card: 4px 4px 0px rgba(236, 72, 153, 0.45);
    --success-bg: #064E3B;
    --success-fg: #A7F3D0;
    --warn-bg: #78350F;
    --warn-fg: #FEF3C7;
    --info-bg: #3B0764;
    --info-fg: #F5D0FE;
    --danger-bg: #831843;
    --danger-fg: #FCE7F3;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-canvas);
    background-image:
      linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
      linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
    background-size: 32px 32px;
    color: var(--text-primary);
    line-height: 1.5;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
  }
  [data-theme="dark"] body {
    background-image:
      radial-gradient(ellipse 85% 240px at 50% -20px, rgba(236, 72, 153, 0.36), rgba(126, 34, 206, 0.18) 48%, transparent 78%),
      radial-gradient(circle 340px at 94% 96%, rgba(235, 106, 72, 0.16), transparent 72%),
      linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
      linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
  }
  .skip-link {
    position: absolute;
    left: -9999px;
    top: 0;
    background: var(--slu-gold-bright);
    color: #0D0A1A;
    padding: 0.75rem 1rem;
    font-weight: 700;
    z-index: 1000;
  }
  .skip-link:focus { left: 0.5rem; top: 0.5rem; }

  /* macOS Browser Window Top Bar (Canva EAG-QJ6Vos4 Image 1) */
  .window-chrome {
    background: var(--chrome-bg);
    border-bottom: 2px solid var(--border);
    padding: 0.55rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
  }
  .mac-dots { display: flex; align-items: center; gap: 0.45rem; }
  .dot { width: 13px; height: 13px; border-radius: 50%; display: inline-block; border: 1px solid rgba(0,0,0,0.12); }
  .dot.r { background: #FF5F57; }
  .dot.y { background: #FEBC2E; }
  .dot.g { background: #28C840; }
  .url-pill {
    flex: 1;
    max-width: 440px;
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 999px;
    padding: 0.28rem 1rem;
    font-family: var(--mono-font);
    font-size: 0.74rem;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .theme-toggle {
    background: var(--surface);
    color: var(--text-primary);
    border: 2px solid var(--accent-coral);
    border-radius: 999px;
    padding: 0.28rem 0.9rem;
    font-family: var(--mono-font);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
  }
  .theme-toggle:hover { background: var(--accent-coral); color: #FFFFFF; }

  /* Editorial Hero Header */
  header {
    padding: 1.35rem 2rem 1.15rem;
    max-width: 1440px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1.25rem;
  }
  .hero-left { flex: 1.1; min-width: 280px; }
  .mono-kicker {
    font-family: var(--mono-font);
    font-size: 0.76rem;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    color: var(--text-secondary);
    line-height: 1.55;
    max-width: 580px;
  }
  .hero-subline {
    font-family: var(--mono-font);
    font-size: 0.71rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 0.45rem;
  }
  .hero-right { text-align: right; flex: 1; min-width: 280px; }
  .hero-display {
    font-size: 2.05rem;
    font-weight: 300;
    letter-spacing: -0.02em;
    line-height: 1.08;
    color: var(--text-primary);
  }
  .hero-display strong {
    font-weight: 900;
    font-style: italic;
    letter-spacing: -0.04em;
    color: var(--text-primary);
  }
  [data-theme="dark"] .hero-display strong {
    color: #FFFFFF;
    text-shadow: 0 0 18px rgba(236, 72, 153, 0.55);
  }
  .header-badges { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 0.45rem; margin-top: 0.75rem; }
  .h-badge {
    background: var(--surface);
    border: 1.5px solid var(--text-primary);
    color: var(--text-primary);
    padding: 0.25rem 0.72rem;
    border-radius: 6px;
    font-family: var(--mono-font);
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .h-badge.gold {
    background: #FCE7F3;
    border: 2px solid #DB2777;
    color: #831843;
  }
  [data-theme="dark"] .h-badge { border-color: var(--border-strong); color: #F8FAFC; }
  [data-theme="dark"] .h-badge.gold { background: #831843; border-color: #EC4899; color: #FFFFFF; }

  .nav-tabs {
    background: var(--surface);
    border-top: 2px solid var(--border);
    border-bottom: 2px solid var(--border);
    padding: 0.5rem 2rem;
    display: flex;
    gap: 0.55rem;
    overflow-x: auto;
  }
  .tab-btn {
    background: transparent;
    border: 2px solid transparent;
    border-radius: 999px;
    padding: 0.52rem 1.15rem;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-muted);
    cursor: pointer;
    white-space: nowrap;
  }
  .tab-btn:hover { color: var(--text-primary); background: var(--surface-subtle); }
  .tab-btn:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {
    outline: none;
    box-shadow: var(--focus-ring);
  }
  .tab-btn[aria-selected="true"] {
    color: var(--text-primary);
    border-color: var(--accent-coral);
    background: var(--surface-subtle);
  }
  [data-theme="dark"] .tab-btn[aria-selected="true"] {
    color: #FFFFFF;
    background: rgba(235, 106, 72, 0.16);
  }

  main {
    flex: 1;
    width: 100%;
    max-width: 1440px;
    margin: 0 auto;
    padding: 1.5rem 2rem;
  }
  .tab-panel[hidden] { display: none; }
  .grid-2 { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.5rem; align-items: start; }
  .grid-equal { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; align-items: start; }
  @media (max-width: 1024px) {
    .grid-2, .grid-equal { grid-template-columns: 1fr; }
    main { padding: 1rem; }
    header, .nav-tabs, .window-chrome { padding-left: 1rem; padding-right: 1rem; }
    .hero-right { text-align: left; }
    .header-badges { justify-content: flex-start; }
  }
  .card {
    background: var(--surface);
    border: 2px solid var(--text-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-card);
    overflow: hidden;
  }
  [data-theme="dark"] .card { border-color: var(--border-strong); }
  .card-head {
    background: var(--slu-navy);
    color: #FFFFFF;
    padding: 0.85rem 1.25rem;
    border-bottom: 2px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  [data-theme="dark"] .card-head {
    background: linear-gradient(90deg, #1E163B 0%, #3B125E 100%);
  }
  .card-head h2 { font-size: 0.96rem; font-weight: 800; letter-spacing: -0.01em; }
  .card-head .sub {
    font-family: var(--mono-font);
    font-size: 0.69rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
  }
  .presets-bar {
    padding: 0.85rem 1rem;
    background: var(--surface-subtle);
    border-bottom: 1.5px solid var(--border);
  }
  .presets-label {
    font-family: var(--mono-font);
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
    display: block;
  }
  .preset-chips { display: flex; flex-wrap: wrap; gap: 0.42rem; }
  .chip-btn {
    background: var(--surface);
    border: 1.5px solid var(--border-strong);
    color: var(--text-primary);
    padding: 0.34rem 0.75rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    cursor: pointer;
  }
  .chip-btn:hover { background: var(--accent-coral); color: #FFFFFF; border-color: var(--accent-coral); }
  .chat-log {
    height: 440px;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    background: var(--surface);
  }
  .msg { max-width: 90%; padding: 0.85rem 1rem; border-radius: var(--radius-md); font-size: 0.89rem; }
  .msg.user { align-self: flex-end; background: #002855; color: #FFFFFF; border-bottom-right-radius: 3px; }
  [data-theme="dark"] .msg.user { background: #5B21B6; }
  .msg.bot { align-self: flex-start; background: var(--surface-subtle); border: 1.5px solid var(--border); border-bottom-left-radius: 3px; color: var(--text-primary); }
  .msg.fallback { background: var(--warn-bg); border-color: #F59E0B; color: var(--warn-fg); }
  .msg-meta { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.5rem; }
  .tag {
    display: inline-block;
    padding: 0.16rem 0.52rem;
    border-radius: 6px;
    font-family: var(--mono-font);
    font-size: 0.69rem;
    font-weight: 700;
  }
  .tag.intent { background: var(--info-bg); color: var(--info-fg); }
  .tag.lang { background: var(--warn-bg); color: var(--warn-fg); }
  .tag.cite { background: var(--success-bg); color: var(--success-fg); }
  .tag.warn { background: var(--danger-bg); color: var(--danger-fg); }
  .policy-item { margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed var(--border-strong); }
  .policy-item:first-child { margin-top: 0.25rem; padding-top: 0; border-top: none; }
  .policy-ref { font-weight: 800; color: var(--accent-coral-hover); }
  [data-theme="dark"] .policy-ref { color: #FCA5A5; }
  .policy-link { display: inline-block; margin-top: 0.25rem; font-size: 0.76rem; color: var(--slu-royal); text-decoration: underline; }
  [data-theme="dark"] .policy-link { color: #93C5FD; }
  .chat-form {
    display: flex;
    gap: 0.65rem;
    padding: 0.85rem 1rem;
    background: var(--surface-subtle);
    border-top: 1.5px solid var(--border);
  }
  .chat-form input {
    flex: 1;
    padding: 0.65rem 0.95rem;
    border: 1.5px solid var(--border-strong);
    border-radius: 999px;
    font-size: 0.9rem;
    color: var(--text-primary);
    background: var(--surface);
  }
  /* Outlined Coral Pill CTA (Canva Image 3 motif) */
  .send-btn {
    background: var(--surface);
    color: var(--text-primary);
    border: 2.5px solid var(--accent-coral);
    padding: 0 1.4rem;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.88rem;
    cursor: pointer;
    white-space: nowrap;
  }
  .send-btn:hover { background: var(--accent-coral); color: #FFFFFF; }
  .inspector-body { padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
  .trace-step {
    background: var(--surface-subtle);
    border: 1.5px solid var(--border);
    border-left: 4px solid var(--slu-royal);
    border-radius: var(--radius-sm);
    padding: 0.7rem 0.9rem;
  }
  .trace-step.gold { border-left-color: var(--accent-coral); }
  .trace-step h3 {
    font-family: var(--mono-font);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-secondary);
    margin-bottom: 0.35rem;
  }
  .trace-step p, .trace-step code { font-size: 0.82rem; color: var(--text-primary); word-break: break-word; }
  .pill-list { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.25rem; }
  .pill {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    color: var(--text-primary);
    font-family: var(--mono-font);
    font-size: 0.74rem;
    padding: 0.16rem 0.5rem;
    border-radius: 4px;
  }
  .pill.native { background: #FEF08A; color: #713F12; border-color: #CA8A04; font-weight: 700; }
  .pill.semantic { background: #E0F2FE; color: #0C4A6E; border-color: #0284C7; }
  .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.25rem; }
  @media (max-width: 768px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
  .kpi-card {
    background: var(--slu-navy);
    color: #FFFFFF;
    padding: 1.1rem 1rem;
    border-radius: var(--radius-md);
    border: 2px solid var(--border-strong);
    border-bottom: 4px solid var(--accent-coral);
    text-align: center;
  }
  .kpi-card .num { font-size: 1.75rem; font-weight: 900; color: var(--slu-gold-bright); line-height: 1.2; }
  .kpi-card .lbl {
    font-family: var(--mono-font);
    font-size: 0.71rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #E2E8F0;
    margin-top: 0.35rem;
  }
  .filter-bar {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    align-items: center;
    padding: 0.85rem 1rem;
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: var(--radius-md);
    margin-bottom: 1rem;
  }
  .filter-bar label { font-family: var(--mono-font); font-size: 0.76rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; }
  .filter-bar input, .filter-bar select {
    padding: 0.5rem 0.75rem;
    border: 1.5px solid var(--border-strong);
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    color: var(--text-primary);
    background: var(--surface);
  }
  .filter-bar input { flex: 1; min-width: 210px; }
  .table-wrap { overflow-x: auto; background: var(--surface); border: 2px solid var(--border); border-radius: var(--radius-md); }
  .table-wrap.flush { border: none; border-radius: 0; max-height: 430px; overflow-y: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 0.83rem; color: var(--text-primary); }
  th {
    background: var(--slu-navy);
    color: #FFFFFF;
    text-align: left;
    padding: 0.72rem 0.85rem;
    font-weight: 700;
    white-space: nowrap;
    position: sticky;
    top: 0;
  }
  td { padding: 0.62rem 0.85rem; border-bottom: 1px solid var(--border); vertical-align: top; }
  tbody tr:nth-child(even) td { background: var(--surface-subtle); }
  .bar-track {
    width: 110px;
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    display: inline-block;
    vertical-align: middle;
    margin-right: 0.4rem;
  }
  .bar-fill { background: var(--slu-royal); height: 100%; }
  .cm-cell { text-align: center; font-weight: 700; font-size: 0.78rem; padding: 0.45rem 0.5rem; }
  .empty-state { padding: 2rem; text-align: center; color: var(--text-muted); font-size: 0.9rem; }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }
  footer {
    text-align: center;
    padding: 1rem;
    font-family: var(--mono-font);
    font-size: 0.74rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    background: var(--surface);
    border-top: 2px solid var(--border);
    margin-top: 2rem;
  }
</style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>

<div class="window-chrome">
  <div class="mac-dots" aria-hidden="true">
    <span class="dot r"></span>
    <span class="dot y"></span>
    <span class="dot g"></span>
  </div>
  <div class="url-pill">slu://egovernance-portal/ai-nomally &bull; graph-grid v3</div>
  <button type="button" id="theme-toggle" class="theme-toggle" aria-pressed="false">Dark Glow Mode</button>
</div>

<header>
  <div class="hero-left">
    <p class="mono-kicker">A digitized collection of 52 verified SLU Student Handbook &amp; URO policies plus 176 CAR lexicon entries engineered with zero hallucination.</p>
    <p class="hero-subline">SLU Baguio SAMCIS &bull; CSE 30 NLP &bull; Group 2 – AiNomally &bull; Prof. Dalos D. Miguel</p>
  </div>
  <div class="hero-right">
    <div class="hero-display">welcome to the SLU <strong>brain</strong></div>
    <div class="header-badges" id="header-badges"></div>
  </div>
</header>

<nav class="nav-tabs" role="tablist" aria-label="SLU eGovernance Portal Sections">
  <button class="tab-btn" role="tab" id="btn-chat" aria-controls="tab-chat" aria-selected="true" tabindex="0">1. Live Chatbot &amp; NLP Inspector</button>
  <button class="tab-btn" role="tab" id="btn-lexicon" aria-controls="tab-lexicon" aria-selected="false" tabindex="-1">2. CAR &amp; SLU Lexicon (176)</button>
  <button class="tab-btn" role="tab" id="btn-corpus" aria-controls="tab-corpus" aria-selected="false" tabindex="-1">3. Corpus &amp; BoW Analytics</button>
  <button class="tab-btn" role="tab" id="btn-ml" aria-controls="tab-ml" aria-selected="false" tabindex="-1">4. ML Benchmarks &amp; Ablation</button>
</nav>

<main id="main-content">
  <!-- TAB 1: LIVE CHATBOT & NLP PIPELINE -->
  <section id="tab-chat" class="tab-panel" role="tabpanel" aria-labelledby="btn-chat">
    <div class="grid-2">
      <div class="card">
        <div class="card-head">
          <h2>SLU Student Support Assistant (Probabilistic ML + Lexicon + TF-IDF)</h2>
          <span class="sub">EN &bull; Taglish &bull; ilo &bull; kne &bull; ibl</span>
        </div>
        <div class="presets-bar">
          <span class="presets-label">Try Flagship Niche Handbook, Multilingual &amp; Safety Queries:</span>
          <div class="preset-chips" id="preset-chips"></div>
        </div>
        <div id="chat-box" class="chat-log" role="log" aria-live="polite" aria-label="Chatbot conversation"></div>
        <form class="chat-form" id="chat-form">
          <label for="user-input" class="sr-only">Enter student question</label>
          <input type="text" id="user-input" maxlength="400" autocomplete="off" placeholder="Ask about Latin honors, dropped vs. permanently dropped, TOR, shifting, or CAR terms...">
          <button type="submit" class="send-btn">Send &rarr;</button>
        </form>
      </div>

      <div class="card">
        <div class="card-head">
          <h2>Live 6-Stage NLP + ML Execution Trace</h2>
          <span class="sub">Py &harr; JS Parity Verified</span>
        </div>
        <div id="inspector-content" class="inspector-body" aria-live="polite"></div>
      </div>
    </div>
  </section>

  <!-- TAB 2: MULTILINGUAL ELECTRONIC LEXICON -->
  <section id="tab-lexicon" class="tab-panel" role="tabpanel" aria-labelledby="btn-lexicon" hidden>
    <div class="kpi-row" id="lex-kpis"></div>
    <div class="filter-bar">
      <label for="lex-search">Search:</label>
      <input type="search" id="lex-search" placeholder="Search lemma, root, English/Filipino gloss, or ID (e.g., laude, liway, samcis, agadal, inayan)...">
      <label for="lex-lang">Language:</label>
      <select id="lex-lang">
        <option value="ALL">All Languages (176 Entries)</option>
        <option value="en-SLU">SLU Institutional Acronyms &amp; Honors (en-SLU)</option>
        <option value="tl-SLU">Campus Taglish / Baguio Variant (tl-SLU / kne-tl)</option>
        <option value="ilo">CAR Local: Ilocano (ilo)</option>
        <option value="kne">CAR Local: Northern Kankanaey (kne)</option>
        <option value="ibl">CAR Local: Ibaloi (ibl)</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Lemma</th>
            <th>ISO</th>
            <th>POS</th>
            <th>Root &amp; Affix</th>
            <th>English / Institutional Gloss</th>
            <th>Filipino Gloss</th>
            <th>Intent Mapping</th>
          </tr>
        </thead>
        <tbody id="lex-tbody"></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 3: CORPUS & BOW ANALYTICS -->
  <section id="tab-corpus" class="tab-panel" role="tabpanel" aria-labelledby="btn-corpus" hidden>
    <div class="kpi-row" id="corpus-kpis"></div>
    <div class="grid-equal" style="margin-bottom: 1.5rem;">
      <div class="card">
        <div class="card-head">
          <h2>Verified Midterm Top 30 Bag of Words (corpus_bow_summary.csv)</h2>
          <span class="sub">624 Tokens &bull; 426 Stems &bull; semester=8</span>
        </div>
        <div class="table-wrap flush">
          <table>
            <thead><tr><th>Rank</th><th>Stem / Lemma</th><th>Freq</th><th>Coverage (%)</th></tr></thead>
            <tbody id="bow-tbody"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-head">
          <h2>Verified Recurring Midterm Bigrams (n=2, freq &ge; 2)</h2>
          <span class="sub">19 Real Collocations (preprocessed_tokens.json)</span>
        </div>
        <div class="table-wrap flush">
          <table>
            <thead><tr><th>#</th><th>Bigram Collocation</th><th>Freq</th></tr></thead>
            <tbody id="bigram-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h2>Expanded Multi-Layer Annotated Corpus (350 Balanced Docs &bull; 10 Intents)</h2>
        <span class="sub">Transparent Source_Type Provenance</span>
      </div>
      <div class="filter-bar" style="margin:0;border:none;border-bottom:1px solid var(--border);border-radius:0;">
        <label for="doc-search">Filter:</label>
        <input type="search" id="doc-search" placeholder="Search document text, reference, or acronym...">
        <label for="doc-intent">Intent:</label>
        <select id="doc-intent"><option value="ALL">All 10 Intents (350 Docs)</option></select>
        <label for="doc-lang">Register:</label>
        <select id="doc-lang">
          <option value="ALL">All Registers</option>
          <option value="EN">EN</option>
          <option value="TL-EN">TL-EN</option>
          <option value="CAR-TL-EN">CAR-TL-EN</option>
        </select>
      </div>
      <div class="table-wrap flush" style="max-height: 460px;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Provenance &amp; Reference</th>
              <th>Intent</th>
              <th>Register</th>
              <th>Cleaned Document Text</th>
            </tr>
          </thead>
          <tbody id="corpus-tbody"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TAB 4: ML BENCHMARKS & ABLATION STUDY -->
  <section id="tab-ml" class="tab-panel" role="tabpanel" aria-labelledby="btn-ml" hidden>
    <div class="kpi-row" id="ml-kpis"></div>
    <div class="grid-equal" style="margin-bottom: 1.5rem;">
      <div class="card">
        <div class="card-head">
          <h2>Stratified 5-Fold Cross-Validation (350 Balanced Docs)</h2>
          <span class="sub">Leak-Free Fold-Local Sublinear TF-IDF</span>
        </div>
        <div class="table-wrap flush">
          <table>
            <thead><tr><th>Classifier</th><th>Accuracy</th><th>Macro P</th><th>Macro R</th><th>Macro F1</th></tr></thead>
            <tbody id="cv-tbody"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-head">
          <h2>4-Stage Held-Out Retrieval Ablation (75 Unseen Queries)</h2>
          <span class="sub">Zero Train/Test Leakage</span>
        </div>
        <div class="table-wrap flush">
          <table>
            <thead><tr><th>Pipeline Stage</th><th>Top-1</th><th>Top-3</th><th>MRR</th><th>OOD Reject</th><th>FP-CAR</th></tr></thead>
            <tbody id="ablation-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h2>Best Classifier 10&times;10 Confusion Matrix (Stratified 5-Fold Aggregate)</h2>
        <span class="sub" id="cm-model-badge"></span>
      </div>
      <div class="table-wrap flush" style="max-height:none;">
        <table id="cm-table"></table>
      </div>
    </div>
  </section>
</main>

<footer>
  Saint Louis University &bull; Department of Computer Science (SAMCIS) &bull; CSE 30: CS Special Topics (NLP) &bull; Group 2 – AiNomally
</footer>

<script id="slu-portal-bundle" type="application/json">__PORTAL_BUNDLE_JSON__</script>
<script>
__ENGINE_JS_CODE__

// ============================================================================
// SAFE DOM HELPERS (ZERO RAW USER INPUT IN innerHTML)
// ============================================================================
function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

const PORTAL_BUNDLE = JSON.parse(document.getElementById("slu-portal-bundle").textContent);
const ENGINE = createSLUChatbotEngine(PORTAL_BUNDLE);

const PRESET_QUERIES = [
  { label: "Latin Honors: Summa / Magna / Cum Laude GWA", q: "What are the specific grades you need for Summa, Magna, and Cum Laude Latin honors at SLU?" },
  { label: "Absences: Dropped vs. Permanently Dropped (FDA)", q: "How many absences do I have in MWF or TTh classes before I become dropped vs. permanently dropped?" },
  { label: "3 Consecutive Absences & OSAS Slip", q: "What happens if I am absent for 3 consecutive meetings in my class?" },
  { label: "Promissory Note & Exam Permit", q: "Paano kumuha ng Finance Promissory Note para makakuha ng exam permit?" },
  { label: "Petition Class & Short Term Load", q: "How do graduating students open a Petition Class or enroll in the 6-week Short Term?" },
  { label: "Taglish: SAMCIS to SEAIT Shifting & QE", q: "Pwede mag tanong? Paano po ba process ng shifting from SAMCIS to SEAIT or SONAHBS? May qualifying exams po ba ulit?" },
  { label: "Ilocano: Agadal, 20% FDA & Exam Rules", q: "Naimbag a bigat! Agadal ak idiay SAMCIS—mano a porsiento ti absent sakbay ma-FDA?" },
  { label: "Kankanaey: Gawis & Inayan Plagiarism", q: "Gawis ay agsapa! Inayan ti plagiarism ken cheating sa exam, ania parusa ti Disciplinary Board?" },
  { label: "Privacy: Freedom Wall Cyberbullying", q: "May parusa po ba kapag may nag-post ng cyberbullying, libel, at private info under RA 10173 sa Freedom Wall?" },
  { label: "OOD Safety Test: Unrelated Query", q: "What is the best recipe for Baguio strawberry sinigang?" }
];

function appendChatMessage(role, textOrRes) {
  const box = document.getElementById("chat-box");
  const wrapper = el("div", "msg " + role + (textOrRes && textOrRes.is_fallback ? " fallback" : ""));

  if (role === "user") {
    wrapper.appendChild(el("div", "", textOrRes));
  } else {
    const res = textOrRes;
    const meta = el("div", "msg-meta");
    meta.appendChild(el("span", "tag " + (res.is_fallback ? "warn" : "intent"), "Intent: " + res.predicted_intent));
    meta.appendChild(el("span", "tag lang", "Register: " + res.code_switching));
    if (res.ml_intent && !res.is_greeting && !res.is_fallback) {
      meta.appendChild(el("span", "tag cite", "ML: " + res.ml_intent + " (" + Math.round(res.ml_confidence * 100) + "%)"));
    }
    if (!res.is_greeting && !res.is_fallback) {
      meta.appendChild(el("span", "tag cite", "Confidence: " + res.confidence.toFixed(2)));
    }
    wrapper.appendChild(meta);

    if (res.is_greeting || res.is_fallback) {
      wrapper.appendChild(el("p", "", res.synthesized_response));
    } else {
      if (res.car_greeting) {
        const gEl = el("p", "", res.car_greeting);
        gEl.style.fontWeight = "700";
        gEl.style.marginBottom = "0.35rem";
        wrapper.appendChild(gEl);
      }
      const chosen = res.chosen_documents || res.top_documents.slice(0, 2);
      for (const d of chosen) {
        const item = el("div", "policy-item");
        item.appendChild(el("div", "policy-ref", "[" + d.section_ref + "] (Score " + d.final_score.toFixed(2) + ")"));
        item.appendChild(el("p", "", d.raw_text));
        if (d.source_url && /^https:\/\//.test(d.source_url)) {
          const link = el("a", "policy-link", "Official Source: " + d.source_url);
          link.href = d.source_url;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          item.appendChild(link);
        }
        wrapper.appendChild(item);
      }
    }
  }
  box.appendChild(wrapper);
  box.scrollTop = box.scrollHeight;
}

function renderInspector(res) {
  const box = document.getElementById("inspector-content");
  box.textContent = "";

  const mkStep = (title, isGold) => {
    const step = el("div", "trace-step" + (isGold ? " gold" : ""));
    step.appendChild(el("h3", "", title));
    return step;
  };

  const s1 = mkStep("Stage 1 • Raw Query, Register & ML Intent");
  const s1Meta = el("p");
  s1Meta.appendChild(el("strong", "", "Register: "));
  s1Meta.appendChild(el("code", "", res.code_switching));
  s1Meta.appendChild(document.createTextNode(" | "));
  s1Meta.appendChild(el("strong", "", "Resolved Intent: "));
  s1Meta.appendChild(el("code", "", res.predicted_intent));
  if (res.ml_intent) {
    s1Meta.appendChild(document.createTextNode(" | "));
    s1Meta.appendChild(el("strong", "", "NB Classifier: "));
    s1Meta.appendChild(el("code", "", res.ml_intent + " (" + (res.ml_confidence * 100).toFixed(1) + "%)"));
  }
  s1.appendChild(s1Meta);
  s1.appendChild(el("p", "", '"' + res.raw_query + '"'));
  box.appendChild(s1);

  const s2 = mkStep("Stage 2 • Acronym-Safe Text Cleaning (data_cleaning.py)");
  s2.appendChild(el("code", "", res.cleaned_query));
  box.appendChild(s2);

  const s3 = mkStep("Stage 3 • Guarded Bilingual & CAR Lemmatization");
  const p3 = el("div", "pill-list");
  if (res.stems.length) {
    res.stems.forEach(st => p3.appendChild(el("span", "pill", st)));
  } else {
    p3.appendChild(el("em", "", "No content stems extracted"));
  }
  s3.appendChild(p3);
  box.appendChild(s3);

  const s4 = mkStep("Stage 4 • Extracted Contiguous Bigrams (n=2)");
  const p4 = el("div", "pill-list");
  if (res.bigrams.length) {
    res.bigrams.forEach(bg => p4.appendChild(el("span", "pill", bg)));
  } else {
    p4.appendChild(el("em", "", "No contiguous bigrams"));
  }
  s4.appendChild(p4);
  box.appendChild(s4);

  const s5 = mkStep("Stage 5 • Matched SLU & CAR Lexicon (Native vs. Semantic)", true);
  const p5 = el("div", "pill-list");
  if (res.matched_lexicon.length) {
    res.matched_lexicon.forEach(e => {
      const cls = e.match_type === "native" ? "pill native" : "pill semantic";
      p5.appendChild(el("span", cls, e.lexicon_id + ": " + e.lemma + " (" + e.lang + ", " + e.match_type + ") → " + e.en_gloss));
    });
  } else {
    p5.appendChild(el("em", "", "General vocabulary (no specialized lexicon trigger)"));
  }
  s5.appendChild(p5);
  box.appendChild(s5);

  const s6 = mkStep("Stage 6 • Top Ranked Policy Documents (Hybrid Score)");
  if (res.top_documents.length) {
    res.top_documents.forEach((d, idx) => {
      const row = el("p");
      row.appendChild(el("strong", "", "#" + (idx + 1) + " Doc " + d.doc_id + " [" + d.section_ref + "] "));
      row.appendChild(el("code", "", "Score=" + d.final_score.toFixed(4) + " (Cos=" + d.cosine_similarity.toFixed(4) + " + Boost=" + d.intent_boost.toFixed(4) + ")"));
      s6.appendChild(row);
    });
  } else {
    s6.appendChild(el("p", "", res.is_greeting ? "Handled directly by multilingual greeting handler." : "Safely rejected by OOD confidence gate (no policy hallucination)."));
  }
  box.appendChild(s6);
}

function processQuery(q) {
  const trimmed = String(q || "").trim().slice(0, 400);
  if (!trimmed) return;
  appendChatMessage("user", trimmed);
  const res = ENGINE.answerQuery(trimmed, 3);
  appendChatMessage("bot", res);
  renderInspector(res);
}

function renderStaticDashboards() {
  const ev = PORTAL_BUNDLE.evalReport;
  const ms = PORTAL_BUNDLE.midtermStats;
  const bestName = ev.best_model;
  const bestCv = ev.stratified_5fold_cv[bestName];
  const fullAb = ev.heldout_ablation.D_full_hybrid;

  // Header badges
  const hb = document.getElementById("header-badges");
  [
    ["Finals Verified Build", "h-badge gold"],
    [PORTAL_BUNDLE.policies.length + " Official Policies", "h-badge"],
    [PORTAL_BUNDLE.lexicon.length + " SLU & CAR Lexicon Entries", "h-badge"],
    ["5-Fold CV F1: " + (bestCv.macro_f1 * 100).toFixed(1) + "%", "h-badge"]
  ].forEach(([txt, cls]) => hb.appendChild(el("span", cls, txt)));

  // Preset chips
  const chips = document.getElementById("preset-chips");
  PRESET_QUERIES.forEach(item => {
    const b = el("button", "chip-btn", item.label);
    b.type = "button";
    b.addEventListener("click", () => processQuery(item.q));
    chips.appendChild(b);
  });

  // Lexicon KPIs
  const langCounts = {};
  PORTAL_BUNDLE.lexicon.forEach(e => { langCounts[e.lang] = (langCounts[e.lang] || 0) + 1; });
  const lk = document.getElementById("lex-kpis");
  [
    [PORTAL_BUNDLE.lexicon.length, "Total Verified Lexicon Entries"],
    [(langCounts["en-SLU"] || 0) + (langCounts["tl-SLU"] || 0) + (langCounts["kne-tl"] || 0), "SLU Acronyms & Campus Taglish"],
    [(langCounts.ilo || 0) + " / " + (langCounts.kne || 0), "Ilocano (ilo) / Kankanaey (kne)"],
    [langCounts.ibl || 0, "Ibaloi (ibl) Regional Entries"]
  ].forEach(([n, l]) => {
    const c = el("div", "kpi-card");
    c.appendChild(el("div", "num", n));
    c.appendChild(el("div", "lbl", l));
    lk.appendChild(c);
  });

  // Corpus KPIs
  const ck = document.getElementById("corpus-kpis");
  [
    [ms.totalDocuments + " → " + ev.corpus_summary.total_documents, "Midterm → Finals Annotated Docs"],
    [ms.totalTokens, "Midterm Filtered Content Tokens"],
    [ms.uniqueStems, "Midterm Verified Unique Stems"],
    [ev.corpus_summary.code_switching_counts["CAR-TL-EN"] || 0, "Expanded CAR-TL-EN Corpus Docs"]
  ].forEach(([n, l]) => {
    const c = el("div", "kpi-card");
    c.appendChild(el("div", "num", n));
    c.appendChild(el("div", "lbl", l));
    ck.appendChild(c);
  });

  // BoW Top 30
  const bowBody = document.getElementById("bow-tbody");
  const maxFreq = ms.bowTop30[0] ? ms.bowTop30[0].freq : 16;
  ms.bowTop30.forEach(r => {
    const tr = el("tr");
    tr.appendChild(el("td", "", "#" + r.rank));
    const tdTerm = el("td"); tdTerm.appendChild(el("code", "", r.term)); tr.appendChild(tdTerm);
    tr.appendChild(el("td", "", String(r.freq)));
    const tdCov = el("td");
    const track = el("span", "bar-track");
    const fill = el("span", "bar-fill");
    fill.style.display = "block";
    fill.style.width = Math.round((r.freq / maxFreq) * 100) + "%";
    track.appendChild(fill);
    tdCov.appendChild(track);
    tdCov.appendChild(el("span", "", r.cov));
    tr.appendChild(tdCov);
    bowBody.appendChild(tr);
  });

  // Real 19 Bigrams
  const bgBody = document.getElementById("bigram-tbody");
  ms.topBigrams.forEach((b, i) => {
    const tr = el("tr");
    tr.appendChild(el("td", "", String(i + 1)));
    const tdB = el("td"); tdB.appendChild(el("code", "", b.bigram)); tr.appendChild(tdB);
    tr.appendChild(el("td", "", String(b.frequency)));
    bgBody.appendChild(tr);
  });

  // Intent filter dropdown
  const intentSel = document.getElementById("doc-intent");
  Object.keys(ev.corpus_summary.intent_counts).sort().forEach(intent => {
    const opt = el("option", "", intent + " (" + ev.corpus_summary.intent_counts[intent] + ")");
    opt.value = intent;
    intentSel.appendChild(opt);
  });

  // ML KPIs
  const mk = document.getElementById("ml-kpis");
  [
    [(bestCv.macro_f1 * 100).toFixed(2) + "%", "Best 5-Fold CV Macro F1 (" + bestName.split(" ")[0] + ")"],
    [(fullAb.top1_policy_accuracy * 100).toFixed(1) + "%", "Held-Out Unseen Top-1 Accuracy"],
    [fullAb.mrr.toFixed(4), "Held-Out Mean Reciprocal Rank"],
    [(fullAb.ood_rejection_rate * 100).toFixed(0) + "% / 0%", "OOD Rejection / FP-CAR Rate"]
  ].forEach(([n, l]) => {
    const c = el("div", "kpi-card");
    c.appendChild(el("div", "num", n));
    c.appendChild(el("div", "lbl", l));
    mk.appendChild(c);
  });

  // CV Table
  const cvBody = document.getElementById("cv-tbody");
  Object.entries(ev.stratified_5fold_cv).forEach(([name, m]) => {
    const tr = el("tr");
    const tdN = el("td");
    tdN.appendChild(el("strong", "", name + (name === bestName ? " ★" : "")));
    tr.appendChild(tdN);
    tr.appendChild(el("td", "", (m.accuracy * 100).toFixed(2) + "%"));
    tr.appendChild(el("td", "", (m.macro_precision * 100).toFixed(2) + "%"));
    tr.appendChild(el("td", "", (m.macro_recall * 100).toFixed(2) + "%"));
    tr.appendChild(el("td", "", (m.macro_f1 * 100).toFixed(2) + "% (±" + (m.std_macro_f1 * 100).toFixed(2) + "%)"));
    cvBody.appendChild(tr);
  });

  // Ablation Table
  const abBody = document.getElementById("ablation-tbody");
  Object.values(ev.heldout_ablation).forEach(a => {
    const tr = el("tr");
    tr.appendChild(el("td", "", a.label));
    tr.appendChild(el("td", "", (a.top1_policy_accuracy * 100).toFixed(1) + "%"));
    tr.appendChild(el("td", "", (a.top3_policy_recall * 100).toFixed(1) + "%"));
    tr.appendChild(el("td", "", a.mrr.toFixed(4)));
    tr.appendChild(el("td", "", (a.ood_rejection_rate * 100).toFixed(0) + "%"));
    tr.appendChild(el("td", "", (a.false_positive_car_rate * 100).toFixed(0) + "%"));
    abBody.appendChild(tr);
  });

  // Confusion Matrix
  document.getElementById("cm-model-badge").textContent = bestName + " (Macro F1 = " + (bestCv.macro_f1 * 100).toFixed(2) + "%)";
  const cmTable = document.getElementById("cm-table");
  const shortLabel = s => s.replace("URO_ENROLLMENT_", "URO_").replace("URO_SUBJECT_", "SUBJ_").replace("ACADEMIC_SHIFTING_", "SHIFT_").replace("HANDBOOK_GRADING_", "GRADE_").replace("EXAM_PERMIT_", "EXAM_").replace("CAMPUS_DECORUM_", "DECOR_").replace("CAMPUS_HEALTH_", "HEALTH_").replace("CAMPUS_FACILITIES_", "FACIL_").replace("TUITION_", "TUIT_");
  const thead = el("thead");
  const hr = el("tr");
  hr.appendChild(el("th", "", "True \\ Pred"));
  bestCv.classes.forEach(c => hr.appendChild(el("th", "", shortLabel(c))));
  thead.appendChild(hr);
  cmTable.appendChild(thead);
  const tb = el("tbody");
  bestCv.confusion_matrix.forEach((row, rIdx) => {
    const tr = el("tr");
    const thCell = el("td");
    thCell.appendChild(el("strong", "", shortLabel(bestCv.classes[rIdx])));
    tr.appendChild(thCell);
    row.forEach((val, cIdx) => {
      const td = el("td", "cm-cell", String(val));
      if (rIdx === cIdx && val > 0) {
        td.style.background = "#dcfce7";
        td.style.color = "#14532d";
      } else if (val > 0) {
        td.style.background = "#fee2e2";
        td.style.color = "#7f1d1d";
      }
      tr.appendChild(td);
    });
    tb.appendChild(tr);
  });
  cmTable.appendChild(tb);
}

function renderLexiconTable() {
  const q = document.getElementById("lex-search").value.toLowerCase().trim();
  const lang = document.getElementById("lex-lang").value;
  const tbody = document.getElementById("lex-tbody");
  tbody.textContent = "";
  const rows = PORTAL_BUNDLE.lexicon.filter(e => {
    const okLang = lang === "ALL" || (lang === "tl-SLU" ? (e.lang === "tl-SLU" || e.lang === "kne-tl") : e.lang === lang);
    const okQ = !q || e.lemma.includes(q) || e.root.includes(q) || e.en_gloss.toLowerCase().includes(q) || e.fil_gloss.toLowerCase().includes(q) || e.lexicon_id.toLowerCase().includes(q);
    return okLang && okQ;
  });
  if (!rows.length) {
    const tr = el("tr");
    const td = el("td", "empty-state", "No lexicon entries match your search filter.");
    td.colSpan = 8;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  rows.forEach(e => {
    const tr = el("tr");
    const td0 = el("td"); td0.appendChild(el("code", "", e.lexicon_id)); tr.appendChild(td0);
    const td1 = el("td"); td1.appendChild(el("strong", "", e.lemma)); tr.appendChild(td1);
    const td2 = el("td"); td2.appendChild(el("span", "tag lang", e.lang)); tr.appendChild(td2);
    const td3 = el("td"); td3.appendChild(el("code", "", e.pos)); tr.appendChild(td3);
    const td4 = el("td"); td4.appendChild(el("code", "", e.root)); td4.appendChild(document.createTextNode(" (" + e.affix + ")")); tr.appendChild(td4);
    tr.appendChild(el("td", "", e.en_gloss));
    tr.appendChild(el("td", "", e.fil_gloss));
    const td7 = el("td"); td7.appendChild(el("span", "tag intent", e.intent)); tr.appendChild(td7);
    tbody.appendChild(tr);
  });
}

function renderCorpusTable() {
  const q = document.getElementById("doc-search").value.toLowerCase().trim();
  const intent = document.getElementById("doc-intent").value;
  const lang = document.getElementById("doc-lang").value;
  const tbody = document.getElementById("corpus-tbody");
  tbody.textContent = "";
  const rows = PORTAL_BUNDLE.expandedCorpus.filter(d => {
    const okI = intent === "ALL" || d.intent === intent;
    const okL = lang === "ALL" || d.lang === lang;
    const okQ = !q || d.text.includes(q) || d.ref.toLowerCase().includes(q) || d.sourceType.toLowerCase().includes(q);
    return okI && okL && okQ;
  });
  if (!rows.length) {
    const tr = el("tr");
    const td = el("td", "empty-state", "No annotated corpus documents match your filter.");
    td.colSpan = 5;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  rows.forEach(d => {
    const tr = el("tr");
    tr.appendChild(el("td", "", "#" + d.id));
    const tdRef = el("td");
    tdRef.appendChild(el("span", "tag cite", d.sourceType));
    tdRef.appendChild(el("div", "", d.ref));
    tr.appendChild(tdRef);
    const tdI = el("td"); tdI.appendChild(el("span", "tag intent", d.intent)); tr.appendChild(tdI);
    const tdL = el("td"); tdL.appendChild(el("span", "tag lang", d.lang)); tr.appendChild(tdL);
    tr.appendChild(el("td", "", d.text));
    tbody.appendChild(tr);
  });
}

function setupAccessibleTabs() {
  const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
  const activate = (tab) => {
    tabs.forEach(t => {
      const active = t === tab;
      t.setAttribute("aria-selected", active ? "true" : "false");
      t.tabIndex = active ? 0 : -1;
      const panel = document.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !active;
    });
  };
  tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); const n = tabs[(idx + 1) % tabs.length]; activate(n); n.focus(); }
      if (e.key === "ArrowLeft") { e.preventDefault(); const p = tabs[(idx - 1 + tabs.length) % tabs.length]; activate(p); p.focus(); }
      if (e.key === "Home") { e.preventDefault(); activate(tabs[0]); tabs[0].focus(); }
      if (e.key === "End") { e.preventDefault(); activate(tabs[tabs.length - 1]); tabs[tabs.length - 1].focus(); }
    });
  });
}

window.addEventListener("DOMContentLoaded", () => {
  setupAccessibleTabs();
  renderStaticDashboards();
  renderLexiconTable();
  renderCorpusTable();

  document.getElementById("lex-search").addEventListener("input", renderLexiconTable);
  document.getElementById("lex-lang").addEventListener("change", renderLexiconTable);
  document.getElementById("doc-search").addEventListener("input", renderCorpusTable);
  document.getElementById("doc-intent").addEventListener("change", renderCorpusTable);
  document.getElementById("doc-lang").addEventListener("change", renderCorpusTable);

  document.getElementById("chat-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const inp = document.getElementById("user-input");
    const q = inp.value;
    inp.value = "";
    processQuery(q);
  });

  // Theme toggle (Light Graph-Paper <-> Dark Neon-Glow Grid)
  const themeBtn = document.getElementById("theme-toggle");
  themeBtn.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    if (isDark) {
      document.documentElement.removeAttribute("data-theme");
      themeBtn.setAttribute("aria-pressed", "false");
      themeBtn.textContent = "Dark Glow Mode";
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
      themeBtn.setAttribute("aria-pressed", "true");
      themeBtn.textContent = "Paper Grid Mode";
    }
  });

  // Populate initial trace with Latin Honors GWA showcase query
  processQuery(PRESET_QUERIES[0].q);
});
</script>
</body>
</html>
"""

NETLIFY_TOML = """[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
    Content-Security-Policy = "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'none';"
"""


def build_portal():
    bundle = load_portal_bundle()
    bundle_json = _safe_json_for_script(bundle)
    html = HTML_TEMPLATE.replace("__PORTAL_BUNDLE_JSON__", bundle_json).replace("__ENGINE_JS_CODE__", ENGINE_JS_CODE)

    root_html = os.path.join(REPO_ROOT, "slu_egovernance_chatbot_ui.html")
    dist_dir = os.path.join(REPO_ROOT, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    dist_html = os.path.join(dist_dir, "index.html")
    dist_toml = os.path.join(dist_dir, "netlify.toml")

    with open(root_html, "w", encoding="utf-8") as f:
        f.write(html)
    with open(dist_html, "w", encoding="utf-8") as f:
        f.write(html)
    with open(dist_toml, "w", encoding="utf-8") as f:
        f.write(NETLIFY_TOML)

    print(f"[OK] Built hardened 4-tab portal -> {root_html} ({len(html):,} bytes)")
    print(f"[OK] Built production deploy bundle -> {dist_html} + {dist_toml}")


if __name__ == "__main__":
    build_portal()
