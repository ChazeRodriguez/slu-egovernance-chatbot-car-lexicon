# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/build_presentation.py
Description: Builds the Classroom TV Large-Print Edition 22-slide (15-20 minute) presentation:
             - Optimized for big classrooms with a regular-sized TV (23pt+ titles, 14-17pt body/tables,
               32-40pt KPI numbers, max 3-4 cols per table, dedicated full-canvas large-print TV charts)
             1. Google Slides (SLU Louisian Executive Theme, single batch API, embedded TV charts, speaker notes)
             2. Local PowerPoint backup (presentation/Group2_AiNomally_CSE30_Deck.pptx via python-pptx)
             3. Timed 5-Speaker Script (presentation/speaker_script_15_20min.md + Google Drive Doc sync)
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import argparse
import json
import os
import re
import subprocess
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Pt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
CHARTS_DIR = os.path.join(REPO_ROOT, "charts")
PRES_DIR = os.path.join(REPO_ROOT, "presentation")
SCRATCH = "/Users/chazerodriguez/.gemini/antigravity/brain/1cb302af-b0c5-465c-a595-27c16ec8c63f/scratch"
SCRIPT_DOC_ID = "12mEnNUJsdP4etsm0VRn38-v6Xu2GOXg270IMv2O0V3s"

# High-Contrast SLU Classroom TV Brand Palette
C_NAVY = "#002855"
C_ROYAL = "#004B87"
C_TEAL = "#0E7490"
C_INDIGO = "#1E3A8A"
C_GOLD = "#D4AF37"
C_GOLD_BRIGHT = "#FACC15"
C_GOLD_LIGHT = "#FEF3C7"
C_ICE = "#DBEAFE"
C_BG_LIGHT = "#F1F5F9"
C_WHITE = "#FFFFFF"
C_TEXT = "#0F172A"
C_MUTED = "#475569"
C_BORDER = "#CBD5E1"
C_GREEN_BG = "#DCFCE7"
C_GREEN_FG = "#166534"
C_RED_FG = "#B91C1C"
C_AMBER = "#B45309"

TOTAL_SLIDES = 22

# ==============================================================================
# TIMED SPEAKER NOTES (22 SLIDES, ~18.8 MINUTES TOTAL, EVENLY SPLIT ACROSS 5 MEMBERS)
#   Chaze Rodriguez      : Slides 1-3, 21-22  (5 slides, ~3:50)
#   Keith Hernandez      : Slides 4-7         (4 slides, ~3:50)
#   Earold Delin         : Slides 8-11        (4 slides, ~3:50)
#   Erick Sibayan        : Slides 12-15       (4 slides, ~3:50)
#   John Andrew Angcaway : Slides 16-20       (5 slides, ~3:55)
# ==============================================================================
SPEAKER_NOTES = {
    1: (
        "[Speaker 1: Chaze Rodriguez | Target: 0:40]\n"
        "Good afternoon, Professor Dalos Miguel and fellow Louisian computer scientists! "
        "We are Group 2, AiNomally—John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, "
        "Erick James Sibayan, and I am Chaze Ezkys Rodriguez. Today we present our CSE 30 NLP Term Project: "
        "the SLU eGovernance Multilingual Chatbot and Cordillera Administrative Region Electronic Lexicon. "
        "Over the next eighteen minutes, we will walk you through how we unified verified Saint Louis University policies, "
        "Cordilleran linguistic preservation, leak-free supervised machine learning, and a hardened browser portal into "
        "one fully reproducible pipeline."
    ),
    2: (
        "[Speaker 1: Chaze Rodriguez | Target: 1:00]\n"
        "Slide 2 frames the dual problem motivating our research right here in Baguio City. "
        "First, institutional guidance at SLU is scattered across the 2015 Student Handbook PDF, the University Registrar's "
        "website, OSAS circulars, Finance payment channels, and clinic notices. As a result, students turn to #SLUFreedomWall "
        "using informal Taglish and acronyms like SAMCIS, SEAIT, SONAHBS, dp, QE, and FDA—which standard English keyword search misses. "
        "Second, SLU serves a vibrant Cordillera Administrative Region student body speaking Ilocano, Northern Kankanaey, and Ibaloi. "
        "Off-the-shelf English NLP pipelines fail on Austronesian affixation like ag-, panag-, and man-, and ignore cultural governance "
        "concepts like inayan, dap-ay, and tongtong. Our thesis is simple: unifying verified SLU policies with a structured CAR lexicon "
        "solves campus support bottlenecks while preserving regional languages."
    ),
    3: (
        "[Speaker 1: Chaze Rodriguez | Target: 0:55]\n"
        "Slide 3 aligns our work directly with both CSE 30 tracks. Under Track A, we built a 156-entry machine-readable "
        "SLU and CAR Electronic Lexicon tagged with ISO 639-3 codes, morphological roots, affixes, bilingual glosses, and strict "
        "Native versus Semantic alias separation. Under Track B, we engineered a hybrid eGovernance chatbot covering 32 verified SLU "
        "policy provisions across 10 domains, deployed in both a Python CLI and an accessible 4-tab web portal. "
        "Four core objectives guided every commit: single-command reproducibility, test-driven bug and security hardening, "
        "balanced scaling to 250 annotated documents, and leak-free empirical benchmarking via Stratified 5-Fold CV and 48 unseen test queries. "
        "I now turn it over to Keith Hernandez to walk through our architecture and data pipeline."
    ),
    4: (
        "[Speaker 2: Keith Hernandez | Target: 1:00]\n"
        "Thank you, Chaze. Slide 4 shows our end-to-end 5-stage NLP pipeline, runnable from a clean checkout using one command: "
        "python3 scripts/build_all.py. Stage 1 acquires multi-source student discourse from #SLUFreedomWall alongside 32 verified "
        "SLU institutional policies across URO, the Student Handbook, Finance, Scholarships, Counseling, and Libraries. "
        "Stage 2 runs deterministic acronym-safe cleaning, protecting SLU acronyms, English contractions, and Cordilleran hyphens. "
        "Stage 3 applies our guarded bilingual and CAR morphological analyzer with 265 stopwords and bigram extraction. "
        "Stage 4 trains and benchmarks pure-Python Multinomial Naive Bayes, Logistic Regression, and Linear SVM models combined with "
        "our 156-entry lexicon and OOD safety gate. Finally, Stage 5 compiles the identical model weights and policies into our zero-XSS "
        "web portal. Notice we require zero external ML packages—pure Python 3.14 verified by 21 automated tests."
    ),
    5: (
        "[Speaker 2: Keith Hernandez | Target: 1:00]\n"
        "Slide 5 visualizes our corpus and resource scaling from our Midterm baseline to Finals. "
        "Our annotated corpus grew 10.4 times from 24 to 250 strictly balanced documents—25 per class across 10 operational intents. "
        "Verified official SLU policies more than doubled from 12 to 32, filling critical Midterm blind spots like Tuition and Bank "
        "Payment Channels, Entrance and Academic Scholarships, the Center for Counseling and Wellness, and the UNL Vath Library. "
        "Our CAR and SLU lexicon grew 6.2 times from 25 to 156 entries, Cordilleran code-switched documents expanded 35 times from 2 "
        "to 70, and our evaluation expanded from 8 Midterm queries to 48 strictly held-out unseen queries with zero training leakage."
    ),
    6: (
        "[Speaker 2: Keith Hernandez | Target: 1:00]\n"
        "Before scaling anything, we ran an exhaustive forensic audit across every local file and Google Drive deliverable, summarized "
        "on Slide 6. We caught and resolved six real discrepancies: First, unique Midterm stems were corrected from an outdated 352 "
        "to the verified 426 stems (TTR 0.6827). Second, 'semester' was corrected from 9 to 8 occurrences (1.28%), restoring 'year' at Rank 19. "
        "Third, the Drive Google Sheet still held old Prelim counts like 'like=12' and 'campu=4'—we replaced Tab 1 with the verified Top 30 "
        "and added a new Finals Tab 2. Fourth, we removed two fabricated bigrams from the portal, keeping strictly the 19 verified recurring "
        "bigrams. Fifth, Doc #6's mismatched Freedom Wall ID #25582 was unified everywhere to the true raw ID #25604. "
        "Our automated test_pipeline.py now proves 0-diff reproduction on every build."
    ),
    7: (
        "[Speaker 2: Keith Hernandez | Target: 0:50]\n"
        "Slide 7 highlights how we hardened Stage 2 text cleaning in scripts/data_cleaning.py. "
        "Earlier cleaning stripped parenthesized SLU acronyms like (SAMCIS) and (TOR) along with timestamps—our acronym-safe regex "
        "deletes submission headers while keeping every institutional acronym intact. During our code audit, we also caught two subtle "
        "real-world bugs: naive expansion turned medical 'feeling ill' into 'feeling i will', and 'SLU's Registrar's Office' into "
        "'slu is registrar is office'. We replaced those with context-aware regex rules that expand 'ill' only before modal verbs and "
        "strip possessive 's cleanly. Finally, Taglish clitics like dp and ngaun normalize cleanly while preserving punctuation polarity "
        "and Cordilleran hyphens like dap-ay and man-obla. Passing it to Earold Delin for morphology and our Track A CAR lexicon."
    ),
    8: (
        "[Speaker 3: Earold Delin | Target: 1:05]\n"
        "Thank you, Keith. Slide 8 examines Stage 3: our guarded bilingual and Cordilleran morphological analyzer in scripts/car_morphology.py. "
        "On the left in red, you see why naive affix stripping fails on bilingual academic text. Early runs corrupted 'management' into 'nage' "
        "and 'campus' into 'campu', and an unguarded Tagalog 'mag-' prefix rule mangled English words like 'magnify' into 'nify' and 'magician' "
        "into 'ician'. We fixed this permanently using curated PREFIX_EXCEPTIONS plus English suffix guards such as -tion, -ment, -ify, and -ician. "
        "On the right in teal, authentic Philippine and Cordilleran affixes normalize reliably: Filipino magtanong and tinanong collapse to tanong, "
        "Ilocano agadal and panagadal collapse to adal, agpaagas collapses to agas, and Northern Kankanaey man-obla and men-obla normalize to obla."
    ),
    9: (
        "[Speaker 3: Earold Delin | Target: 0:55]\n"
        "Slide 9 presents our verified Midterm Top 10 Bag of Words lexical profile across the 24 consolidated baseline documents. "
        "After removing stopwords and running our guarded lemmatizer, we obtain 624 filtered tokens, 457 unique surface forms, "
        "and 426 unique verified stems—with zero corrupted roots. 'student' leads at 16 occurrences (2.56%), followed by 'slu' at 10, "
        "'examination' at 9, and highlighted in SLU Gold, our audited 'semester' count at exactly 8 (1.28%), followed by 'grade', "
        "'requirement', and 'subject' at 7 each. Across contiguous bigrams, 19 true institutional phrases recur at frequency 2, including "
        "'official transcript', 'qualifying examination', and 'failure due'. Every chart, CSV, Google Sheet cell, and portal counter is 100% synced."
    ),
    10: (
        "[Speaker 3: Earold Delin | Target: 1:00]\n"
        "Now let's examine Track A on Slide 10: our 156-entry SLU and CAR Electronic Lexicon. "
        "We scaled from 25 Midterm entries to 156 curated records: 48 Ilocano (ISO 639-3: ilo), 40 Northern Kankanaey (kne), "
        "36 SLU institutional acronyms and Taglish student slang, and 32 Ibaloi (ibl). "
        "Every entry is linguistically grounded in standard lexicographic authorities—Constantino and Rubino for Ilocano, Vanoverbergh for "
        "Kankanaey, Ballard for Ibaloi, and SIL Philippines—capturing cross-language cognates like danum, danom, and shanom for water, "
        "alongside cultural governance terms like inayan, dap-ay, and tongtong. Crucially, separating Native_Aliases from English Semantic_Aliases "
        "guarantees 0.0% false-positive regional language detection."
    ),
    11: (
        "[Speaker 3: Earold Delin | Target: 0:50]\n"
        "Slide 11 shows five representative rows from our machine-readable CSV schema in data/expanded/slu_car_domain_lexicon_v2.csv. "
        "Each record captures its Entry ID, normalized lemma, ISO 639-3 tag, part of speech, root and affix structure, English and Filipino "
        "glosses, separated native and semantic alias arrays, and mapped SLU intent. For instance, SLU-001 maps samcis to shifting and enrollment; "
        "ILO-008 records Ilocano agadal with prefix ag- on root adal; KNE-002 preserves Kankanaey inayan mapped to academic integrity; "
        "IBL-002 maps Ibaloi tongtong to customary mediation and disciplinary councils; and IBL-007 documents the distinctive Ibaloi postalveolar "
        "sh- reflex in shanom. I will now hand it over to Erick Sibayan for our balanced corpus and supervised machine learning benchmarks."
    ),
    12: (
        "[Speaker 4: Erick Sibayan | Target: 0:55]\n"
        "Thank you, Earold. Slide 12 details our expanded 250-document multi-layer annotated corpus built specifically to make Stratified 5-Fold "
        "Cross-Validation statistically sound. Every one of our 10 SLU operational intent domains—from TOR and iSLU Enrollment to Shifting, "
        "Grading/FDA, Exam Integrity, Dress Code, Health & Counseling, Tuition & Scholarships, and Libraries & Labs—contains exactly 25 annotated "
        "documents and at least 3 verified official SLU policy provisions. Across registers, we maintain rich multilingual balance: 101 English "
        "(40.4%), 79 Taglish (31.6%), and 70 Cordilleran code-switched documents (28.0%). For full academic transparency, every row carries a "
        "Source_Type tag distinguishing our 32 official policies, 8 authentic Midterm Freedom Wall/URO queries, and 210 curated multilingual queries."
    ),
    13: (
        "[Speaker 4: Erick Sibayan | Target: 1:00]\n"
        "Slide 13 presents our supervised intent classification results implemented from scratch in pure Python in scripts/train_and_evaluate.py. "
        "To prevent data leakage, TF-IDF unigram and bigram vectorizers are refit strictly inside each training fold of Stratified 5-Fold CV. "
        "We benchmarked three classical linear and probabilistic models: Multinomial Naive Bayes with Laplace smoothing led the field at "
        "95.60% accuracy and 95.61% Macro F1 (±1.47%). L2-regularized Softmax Logistic Regression placed a remarkably close second at 95.20% "
        "accuracy and 95.18% Macro F1 with the tightest variance (±0.90%). One-vs-Rest Linear SVM with Hinge Loss achieved 94.00% accuracy and "
        "93.97% Macro F1. We selected Multinomial Naive Bayes as our deployed production intent classifier for its peak F1 and compact JSON weight footprint."
    ),
    14: (
        "[Speaker 4: Erick Sibayan | Target: 0:55]\n"
        "Slide 14 shows the aggregated 10-by-10 out-of-fold confusion matrix for our winning Multinomial Naive Bayes classifier across all 250 documents. "
        "Notice how clean the green main diagonal is: 239 out of 250 documents are classified accurately, with three domains—Shifting, Facilities & Labs, "
        "and Tuition & Finance—achieving a spotless 25 out of 25! Only 11 errors occur across the entire 250-document corpus, shown in light crimson, "
        "and every single one reflects genuine administrative boundary overlap—such as RFID lanyard rules sitting between Dress Code and Exam Permit "
        "Integrity. That error analysis directly confirmed why pairing Naive Bayes with lexical policy scoring produces superior retrieval."
    ),
    15: (
        "[Speaker 4: Erick Sibayan | Target: 1:00]\n"
        "Slide 15 shows how we fuse all NLP components in our hybrid policy ranker and harden every edge case using Test-Driven Development. "
        "Each candidate official SLU policy is scored by combining expanded TF-IDF cosine similarity, a moderated lexicon intent boost of 0.14, "
        "our trained Multinomial Naive Bayes posterior weighted at 0.30, and a small policy-authority prior. "
        "Before touching code, we wrote 12 regression tests—11 initially failed on the Midterm baseline, exposing four critical bugs we fixed cleanly: "
        "native-only CAR greeting triggers, a calibrated OOD safety gate, numeric grade preservation so '74' hits the 75% rule alongside RA 10173 "
        "cyberbullying routing, and holistic NB moderation to resolve multi-keyword collisions. Passing to John Andrew Angcaway for our ablation study and portal demo."
    ),
    16: (
        "[Speaker 5: John Andrew Angcaway | Target: 1:00]\n"
        "Thank you, Erick. Slide 16 reports our 4-stage ablation study evaluated on 48 strictly held-out unseen queries—42 in-domain queries across "
        "English, Taglish, and CAR languages, plus 4 out-of-domain traps and 2 greetings, with zero text overlap against training data. "
        "Look at the progression: Stage A (raw TF-IDF cosine) starts at 83.3% Top-1 accuracy and 0% OOD safety. Stage B adds acronym-safe cleaning "
        "and CAR morphology, leaping +9.6 points to 92.9% Top-1 and 0.960 MRR. Stage C turns on the 156-entry lexicon and OOD gate—OOD rejection "
        "jumps immediately from 0% to 100%, while exposing a slight 90.5% dip caused by single-keyword collisions. Finally, Stage D adds our trained "
        "Naive Bayes classifier, resolving collisions and achieving our best marks: 95.2% Top-1 accuracy, 97.6% Top-3, 0.964 MRR, 100% OOD safety, "
        "and 0.0% false-positive CAR detections—including 100% accuracy on Taglish and 95% on Cordilleran queries!"
    ),
    17: (
        "[Speaker 5: John Andrew Angcaway | Target: 1:00]\n"
        "Slide 17 covers production engineering: security, cross-runtime parity, and accessibility. "
        "First, on security: our audit flagged DOM XSS vectors in the original HTML portal. We eliminated 100% of .innerHTML assignments, rebuilt "
        "every chat bubble, trace card, and table using safe textContent DOM nodes, added a strict Content-Security-Policy meta tag plus Netlify "
        "security headers, and tested live against an <img onerror=alert(1)> payload. Second, on parity: scripts/build_portal.py compiles the exact "
        "same policies, lexicon, and Naive Bayes weights into the browser UI, and our automated Node.js test confirms 51 out of 51 identical outputs "
        "between Python and JavaScript. Third, our 4-tab portal meets WCAG 2.1 AA contrast with full keyboard ARIA tablist navigation."
    ),
    18: (
        "[Speaker 5: John Andrew Angcaway | Target: 0:55]\n"
        "Slides 18 and 19 walk through four live multilingual query traces verified identically in our CLI and browser portal. "
        "On Slide 18, Case 1 tests a real Taglish shifting question: 'Paano process ng shifting from SAMCIS to SEAIT? May QE ba?' "
        "Our hybrid engine preserves all three SLU acronyms, classifies ACADEMIC_SHIFTING_TRANSFER, and returns the exact URO internal shifting "
        "and Qualifying Examination procedure. Case 2 tests an Ilocano code-switched attendance question: 'Naimbag a bigat! Agadal ak idiay SAMCIS—mano "
        "absent sakbay ma-FDA?' The engine recognizes native Ilocano, responds warmly with 'Naimbag a bigat/aldaw!', normalizes agadal to adal, "
        "and cites Student Handbook Article I's 20% unexcused absence FDA ceiling."
    ),
    19: (
        "[Speaker 5: John Andrew Angcaway | Target: 0:55]\n"
        "Continuing our walkthrough on Slide 19: Case 3 tests Northern Kankanaey academic integrity—'Gawis ay agsapa! Inayan ti plagiarism ken cheating, "
        "ania parusa?' Because 'gawis' and 'inayan' are genuine native Kankanaey entries, the assistant greets the student with 'Gawis ay agew!' and "
        "retrieves Student Handbook Article II, Section 4 on SLU Disciplinary Board sanctions—whereas a plain English plagiarism query cleanly suppresses "
        "regional greetings. Case 4 demonstrates our safety gate: asking for a 'Baguio strawberry sinigang' recipe scores below our 0.14 threshold, "
        "triggering OUT_OF_DOMAIN with zero hallucination and politely directing the user to official SLU offices."
    ),
    20: (
        "[Speaker 5: John Andrew Angcaway | Target: 0:50]\n"
        "Slide 20 shares our honest engineering limitations and Data Privacy Act (RA 10173) safeguards. "
        "We openly tag all 210 expanded multilingual training utterances as CURATED_MULTILINGUAL_INQUIRY rather than claiming they were all scraped "
        "live, and our next linguistic milestone is formal community validation with native Ilocano, Northern Kankanaey, and Ibaloi speakers. "
        "On privacy, our Freedom Wall scraper stores zero student names, IDs, or private identifiers, and because the web portal executes 100% "
        "client-side in the browser with static hosting, student questions never leave their own device. "
        "Back to Chaze for our roadmap and closing!"
    ),
    21: (
        "[Speaker 1: Chaze Rodriguez | Target: 0:45]\n"
        "Thank you, John Andrew. Slide 21 maps our three-step roadmap beyond CSE 30. "
        "Step 1 is partnering with native CAR linguists and student organizations at SLU to validate idioms, diacritics, and anonymized real-world "
        "queries while expanding toward Bontok and Ifugao. Step 2 is benchmarking compact multilingual sentence embeddings like mE5 or LaBSE alongside "
        "our fast Naive Bayes baseline, paired with strict policy-grounded RAG summarization that never fabricates citations. "
        "Step 3 is institutional integration with live iSLU academic calendars, OSAS advisories, and official URO ticketing workflows."
    ),
    22: (
        "[Speaker 1: Chaze Rodriguez & All Members | Target: 0:45]\n"
        "To close on Slide 22: Group 2 AiNomally delivered a fully reproducible, audited, security-hardened multilingual NLP ecosystem for Saint Louis "
        "University. From 250 balanced corpus documents, 32 official SLU policies, and 156 verified CAR lexicon entries to 95.61% Stratified 5-Fold CV "
        "Macro F1, 95.2% unseen Top-1 policy accuracy, 100% OOD safety, and 21 passing automated tests, every single metric in our paper, spreadsheet, "
        "and portal is backed by deterministic code. Agyamanak! Iyaman! Dakel a iyaman! Thank you very much, Professor Dalos Miguel and classmates—"
        "we are now ready for your questions and live portal demo!"
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

    def add_slide(self, slide_id, bg_hex=C_BG_LIGHT, notes_text=""):
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

    def rect(self, slide_id, x, y, w, h, bg_hex, outline_hex=None):
        self.ops.append({
            "op": "add-shape",
            "slide": slide_id,
            "shape_type": "RECTANGLE",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "background_color": bg_hex,
        })
        ps = self.pptx_slides[slide_id]
        shp = ps.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
        shp.fill.solid()
        shp.fill.fore_color.rgb = hex_to_rgb(bg_hex)
        if outline_hex:
            shp.line.color.rgb = hex_to_rgb(outline_hex)
            shp.line.width = Pt(1.25)
        else:
            shp.line.fill.background()

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
        color=C_TEXT,
        bg_hex=None,
        align="left",
        valign="TOP",
        line_spacing=128,
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
            "font_family": "Roboto",
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
        for idx, ln in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.alignment = p_align
            p.line_spacing = line_spacing / 100.0
            run = p.add_run()
            run.text = ln
            run.font.name = "Arial"
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = hex_to_rgb(color)

    def header_chrome(self, slide_id, slide_num, title, speaker_label):
        """Big, uncluttered Classroom TV header: 23pt bold white title, no tiny subtitle."""
        self.rect(slide_id, 0, 0, 720, 58, C_NAVY)
        self.rect(slide_id, 0, 58, 720, 4, C_GOLD)
        self.textbox(slide_id, title, 24, 9, 608, 42, font_size=23, bold=True, color=C_WHITE, valign="MIDDLE")
        self.textbox(
            slide_id,
            f"{slide_num} / {TOTAL_SLIDES}",
            632, 11, 68, 38,
            font_size=15, bold=True, color=C_GOLD_BRIGHT, align="right", valign="MIDDLE",
        )
        # Clean footer
        self.rect(slide_id, 0, 382, 720, 23, C_WHITE)
        self.textbox(
            slide_id,
            "SLU SAMCIS • CSE 30 NLP • Group 2 – AiNomally",
            24, 383, 405, 20, font_size=10.5, color=C_MUTED, valign="MIDDLE",
        )
        self.textbox(
            slide_id,
            speaker_label,
            435, 383, 261, 20, font_size=11, bold=True, color=C_NAVY, align="right", valign="MIDDLE",
        )

    def card(
        self,
        slide_id,
        x, y, w, h,
        title, body,
        header_bg=C_NAVY,
        title_color=C_WHITE,
        title_size=16,
        header_h=34,
        body_size=15,
        line_spacing=132,
        body_bold=False,
    ):
        self.rect(slide_id, x, y, w, h, C_WHITE, outline_hex=C_BORDER)
        self.textbox(slide_id, title, x, y, w, header_h, font_size=title_size, bold=True, color=title_color, bg_hex=header_bg, valign="MIDDLE")
        self.textbox(
            slide_id, body,
            x + 6, y + header_h + 6, w - 12, h - header_h - 10,
            font_size=body_size, bold=body_bold, color=C_TEXT, line_spacing=line_spacing,
        )

    def arrow(self, slide_id, x, y, width, color=C_GOLD):
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

    def stat_card(self, slide_id, x, y, w, h, num, label, bg=C_NAVY, num_size=36, lbl_size=13.5):
        self.rect(slide_id, x, y, w, h, bg)
        self.rect(slide_id, x, y + h - 5, w, 5, C_GOLD)
        self.textbox(slide_id, num, x + 4, y + 8, w - 8, int(h * 0.54), font_size=num_size, bold=True, color=C_GOLD_BRIGHT, align="center", valign="MIDDLE")
        self.textbox(slide_id, label, x + 6, y + int(h * 0.54), w - 12, int(h * 0.40), font_size=lbl_size, bold=True, color=C_WHITE, align="center", valign="TOP", line_spacing=118)

    def table(self, slide_id, table_id, x, y, w, h, data, font_size=14, header_bg=C_NAVY, col_widths=None):
        rows, cols = len(data), len(data[0])
        self.ops.append({"op": "add-table", "slide": slide_id, "rows": rows, "cols": cols, "id": table_id, "x": x, "y": y, "width": w, "height": h})
        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                is_hdr = r_idx == 0
                bg = header_bg if is_hdr else (C_WHITE if r_idx % 2 == 1 else "#EBF1F8")
                fg = C_WHITE if is_hdr else C_TEXT
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
                cell.fill.fore_color.rgb = hex_to_rgb(header_bg if is_hdr else (C_WHITE if r_idx % 2 == 1 else "#EBF1F8"))
                cell.text = str(val)
                for p in cell.text_frame.paragraphs:
                    for run in p.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(font_size)
                        run.font.bold = is_hdr or c_idx == 0
                        run.font.color.rgb = hex_to_rgb(C_WHITE if is_hdr else C_TEXT)

    def image(self, slide_id, img_path, x, y, w, h):
        self.image_inserts.append((slide_id, img_path, x, y, w, h))
        ps = self.pptx_slides[slide_id]
        ps.shapes.add_picture(img_path, Pt(x), Pt(y), width=Pt(w), height=Pt(h))


def build_deck_content(b):
    # ==================== SLIDE 1: TITLE (DARK NAVY HERO) ====================
    b.add_slide("p", C_NAVY, SPEAKER_NOTES[1])
    b.rect("p", 0, 0, 720, 8, C_GOLD)
    b.rect("p", 0, 397, 720, 8, C_GOLD)
    b.textbox("p", "SAINT LOUIS UNIVERSITY  •  BAGUIO CITY  •  SAMCIS", 30, 26, 660, 28, font_size=14, bold=True, color=C_GOLD_BRIGHT, align="center", valign="MIDDLE")
    b.textbox("p", "SLU eGovernance Chatbot\n& CAR Electronic Lexicon", 30, 66, 660, 108, font_size=38, bold=True, color=C_WHITE, align="center", valign="MIDDLE", line_spacing=112)
    b.textbox("p", "Multilingual NLP Resources, Guarded CAR Morphology\n& Supervised Intent Classification", 40, 180, 640, 50, font_size=16, color=C_ICE, align="center", valign="MIDDLE", line_spacing=122)
    b.rect("p", 250, 240, 220, 4, C_GOLD)
    b.textbox("p", "Group 2 – AiNomally", 40, 254, 640, 30, font_size=20, bold=True, color=C_GOLD_BRIGHT, align="center", valign="MIDDLE")
    b.textbox("p", "John Andrew Angcaway  •  Earold Jan Delin  •  Keith Russel Hernandez\nChaze Ezkys M. Rodriguez  •  Erick James Sibayan", 30, 290, 660, 48, font_size=14.5, bold=True, color=C_WHITE, align="center", valign="MIDDLE", line_spacing=130)
    b.textbox("p", "CSE 30 (Natural Language Processing)   |   Class 9712   |   Prof. Dalos D. Miguel", 30, 348, 660, 28, font_size=13, color=C_ICE, align="center", valign="MIDDLE")

    # ==================== SLIDE 2: THE PROBLEM ====================
    b.add_slide("S02", C_BG_LIGHT, SPEAKER_NOTES[2])
    b.header_chrome("S02", 2, "Why SLU Needs a CAR-Aware Chatbot", "Speaker: Chaze Rodriguez")
    b.card(
        "S02", 24, 74, 326, 224,
        "1. SLU Support Bottlenecks",
        "• Rules split across Handbook, URO & OSAS\n"
        "• Urgent Taglish queries on #SLUFreedomWall\n"
        "• English search fails on SAMCIS, dp, QE & FDA",
        header_bg=C_NAVY, title_size=16.5, body_size=15, line_spacing=148,
    )
    b.card(
        "S02", 370, 74, 326, 224,
        "2. CAR Language Resource Gap",
        "• Baguio hosts Ilocano, Kankanaey & Ibaloi\n"
        "• Affixes (ag-, panag-, man-) break English NLP\n"
        "• Cultural terms (inayan, dap-ay) ignored",
        header_bg=C_ROYAL, title_size=16.5, body_size=15, line_spacing=148,
    )
    b.textbox(
        "S02",
        "Thesis: Unify verified SLU policies with a 156-entry CAR lexicon in one fast multilingual assistant.",
        24, 310, 672, 58, font_size=15.5, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 3: TRACKS & OBJECTIVES ====================
    b.add_slide("S03", C_BG_LIGHT, SPEAKER_NOTES[3])
    b.header_chrome("S03", 3, "Dual CSE 30 Tracks & Four Objectives", "Speaker: Chaze Rodriguez")
    b.card(
        "S03", 24, 74, 326, 114,
        "Track A • CAR Electronic Lexicon",
        "156 verified SLU, Ilocano, Kankanaey & Ibaloi entries with roots, affixes & glosses.",
        header_bg=C_ROYAL, title_size=16, header_h=34, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S03", 370, 74, 326, 114,
        "Track B • SLU eGovernance Chatbot",
        "32 verified SLU policies across 10 domains via Hybrid TF-IDF + Naive Bayes + Web UI.",
        header_bg=C_TEAL, title_size=16, header_h=34, body_size=14.5, line_spacing=130,
    )
    objs = [
        ("1. Reproducible", "One command\n(build_all.py)\n0 Drive drift", C_NAVY),
        ("2. Hardened", "TDD fixes for\nCAR, OOD &\nZero XSS", C_ROYAL),
        ("3. Balanced", "250 docs\n(25 / intent)\n32 SLU rules", C_TEAL),
        ("4. Rigorous", "5-Fold CV\nNB / LR / SVM\n48 unseen tests", C_NAVY),
    ]
    for idx, (ot, ob, col) in enumerate(objs):
        ox = 24 + idx * 171
        b.card("S03", ox, 202, 159, 168, ot, ob, header_bg=col, title_size=15, header_h=34, body_size=14.5, line_spacing=135)

    # ==================== SLIDE 4: 5-STAGE ARCHITECTURE ====================
    b.add_slide("S04", C_BG_LIGHT, SPEAKER_NOTES[4])
    b.header_chrome("S04", 4, "5-Stage Reproducible NLP Architecture", "Speaker: Keith Hernandez")
    stages = [
        ("Stage 1\nAcquire", "• 8 FW posts\n• 32 SLU rules\n• URO & OSAS\n• Handbook", C_NAVY),
        ("Stage 2\nClean", "• Keep SAMCIS\n• Fix 'ill' & 's\n• Taglish slang\n• CAR hyphens", C_ROYAL),
        ("Stage 3\nMorph", "• 265 stopwords\n• Safe English\n• CAR affixes\n• 19 Bigrams", C_TEAL),
        ("Stage 4\nML Core", "• 5-Fold CV\n• Naive Bayes\n• 156 Lexicon\n• OOD Gate", C_NAVY),
        ("Stage 5\nPortal", "• 4-Tab Web UI\n• Zero XSS\n• Py↔JS Parity\n• WCAG 2.1 AA", C_ROYAL),
    ]
    for idx, (st_hdr, st_body, col) in enumerate(stages):
        sx = 20 + idx * 138
        b.rect("S04", sx, 76, 126, 224, C_WHITE, outline_hex=C_BORDER)
        b.textbox("S04", st_hdr, sx, 76, 126, 48, font_size=14, bold=True, color=C_WHITE, bg_hex=col, align="center", valign="MIDDLE", line_spacing=112)
        b.textbox("S04", st_body, sx + 4, 132, 118, 162, font_size=13.5, bold=True, color=C_TEXT, line_spacing=145)
        if idx < 4:
            b.arrow("S04", sx + 127, 186, 8)
    b.textbox(
        "S04",
        "Zero External ML Dependencies: Pure Python 3.14 + JSON weights • 21 / 21 automated tests passing.",
        20, 314, 680, 56, font_size=15, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 5: SCALING CHART ====================
    b.add_slide("S05", C_BG_LIGHT, SPEAKER_NOTES[5])
    b.header_chrome("S05", 5, "Corpus & Lexicon Scaling (Midterm → Finals)", "Speaker: Keith Hernandez")
    b.image("S05", os.path.join(CHARTS_DIR, "tv_02_corpus_scaling.png"), 73, 68, 574, 265)
    b.textbox(
        "S05",
        "Every operational intent now has 25 balanced docs and ≥ 3 verified SLU policies.",
        24, 338, 672, 36, font_size=14.5, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 6: DATA AUDIT ====================
    b.add_slide("S06", C_BG_LIGHT, SPEAKER_NOTES[6])
    b.header_chrome("S06", 6, "End-to-End Audit: Six Discrepancies Fixed", "Speaker: Keith Hernandez")
    b.table("S06", "TBL_AUDIT", 24, 72, 672, 248, [
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
        24, 330, 672, 42, font_size=14.5, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 7: STAGE 2 TEXT CLEANING ====================
    b.add_slide("S07", C_BG_LIGHT, SPEAKER_NOTES[7])
    b.header_chrome("S07", 7, "Stage 2: Hardened Acronym-Safe Cleaning", "Speaker: Keith Hernandez")
    b.table("S07", "TBL_CLEAN", 24, 72, 672, 246, [
        ["Cleaning Rule", "Raw Student / Policy Input", "Hardened Clean Output"],
        ["Acronyms", "[#SLUFW25604] (SAMCIS) (TOR)", "samcis tor (intact!)"],
        ["Context 'ill'", "feeling ill  /  ill answer", "feeling ill  /  i will answer"],
        ["Possessive 's", "SLU's Registrar's Office", "slu registrar office"],
        ["Taglish & CAR", "dp? ngaun? dap-ay man-obla", "downpayment ngayon dap-ay"],
    ], font_size=14, col_widths=[152, 266, 254])
    b.textbox(
        "S07",
        "Protects SLU acronyms, punctuation polarity, and Cordilleran hyphens with 0 Midterm drift.",
        24, 328, 672, 44, font_size=14.5, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 8: STAGE 3 CAR MORPHOLOGY ====================
    b.add_slide("S08", C_BG_LIGHT, SPEAKER_NOTES[8])
    b.header_chrome("S08", 8, "Stage 3: Guarded CAR Morphological Analysis", "Speaker: Earold Delin")
    b.card(
        "S08", 24, 74, 326, 296,
        "Blocked Over-Stemming",
        "Naive errors eliminated:\n"
        "• management → NOT nage\n"
        "• campus → NOT campu\n"
        "• magnify → NOT nify\n"
        "• magician → NOT ician\n\n"
        "Protected by PREFIX_EXCEPTIONS & English suffix rules.",
        header_bg=C_RED_FG, title_size=16.5, header_h=36, body_size=15, line_spacing=132,
    )
    b.card(
        "S08", 370, 74, 326, 296,
        "Normalized CAR & Taglish",
        "Filipino / Taglish:\n"
        "• magtanong / tinanong → tanong\n"
        "• tumataas → taas\n\n"
        "Ilocano / Kankanaey / Ibaloi:\n"
        "• agadal / panagadal → adal\n"
        "• man-obla / men-obla → obla\n"
        "• agpaagas → agas",
        header_bg=C_TEAL, title_size=16.5, header_h=36, body_size=15, line_spacing=130,
    )

    # ==================== SLIDE 9: MIDTERM BOW TOP 10 CHART ====================
    b.add_slide("S09", C_BG_LIGHT, SPEAKER_NOTES[9])
    b.header_chrome("S09", 9, "Verified Midterm Top 10 Bag of Words Stems", "Speaker: Earold Delin")
    b.image("S09", os.path.join(CHARTS_DIR, "tv_01_bow_top10.png"), 73, 68, 574, 265)
    b.textbox(
        "S09",
        "624 filtered tokens  •  426 unique stems  •  19 verified bigrams (official transcript, failure due)",
        24, 338, 672, 36, font_size=14.5, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 10: TRACK A 156 LEXICON OVERVIEW ====================
    b.add_slide("S10", C_BG_LIGHT, SPEAKER_NOTES[10])
    b.header_chrome("S10", 10, "Track A: 156-Entry SLU & CAR Lexicon", "Speaker: Earold Delin")
    b.stat_card("S10", 24, 76, 159, 142, "48", "Ilocano\n(ISO: ilo)", bg=C_ROYAL, num_size=40, lbl_size=14)
    b.stat_card("S10", 195, 76, 159, 142, "40", "Kankanaey\n(ISO: kne)", bg=C_TEAL, num_size=40, lbl_size=14)
    b.stat_card("S10", 366, 76, 159, 142, "36", "SLU & Taglish\n(en / tl-SLU)", bg=C_NAVY, num_size=40, lbl_size=14)
    b.stat_card("S10", 537, 76, 159, 142, "32", "Ibaloi\n(ISO: ibl)", bg=C_INDIGO, num_size=40, lbl_size=14)

    b.card(
        "S10", 24, 234, 326, 136,
        "Cognates & Cultural Roots",
        "• danum (ilo) • danom (kne) • shanom (ibl)\n"
        "• Governance: inayan • dap-ay • tongtong",
        header_bg=C_NAVY, title_size=15.5, header_h=34, body_size=14.5, line_spacing=145,
    )
    b.card(
        "S10", 370, 234, 326, 136,
        "0.0% False-Positive Safeguard",
        "• Separates Native_Aliases vs. Semantic_Aliases\n"
        "• Grounded in Rubino, Vanoverbergh & Ballard",
        header_bg=C_GREEN_FG, title_size=15.5, header_h=34, body_size=14.5, line_spacing=135,
    )

    # ==================== SLIDE 11: LEXICON SAMPLES TABLE ====================
    b.add_slide("S11", C_BG_LIGHT, SPEAKER_NOTES[11])
    b.header_chrome("S11", 11, "Authentic SLU & CAR Lexicon Samples", "Speaker: Earold Delin")
    b.table("S11", "TBL_LEX", 24, 72, 672, 254, [
        ["Lemma", "ISO", "Root / Affix", "Institutional / Regional Gloss"],
        ["samcis", "en-SLU", "Acronym", "School of Accountancy, Mgmt. & Computing"],
        ["agadal", "ilo", "adal (ag-)", "To study; pursue university coursework"],
        ["inayan", "kne", "Root", "Ethical restraint vs. academic dishonesty"],
        ["tongtong", "ibl", "Root", "Customary mediation & disciplinary council"],
        ["shanom", "ibl", "Root", "Water (Ibaloi sh- cognate of danum/danom)"],
    ], font_size=14, col_widths=[108, 76, 136, 352])
    b.textbox(
        "S11",
        "CSV Schema: Entry_ID, Lemma, ISO, POS, Root, Affix, EN/FIL Gloss, Native vs. Semantic Aliases.",
        24, 336, 672, 36, font_size=14, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 12: 250-DOC CORPUS & 10 INTENTS ====================
    b.add_slide("S12", C_BG_LIGHT, SPEAKER_NOTES[12])
    b.header_chrome("S12", 12, "250-Doc Balanced Corpus & 10 Intents", "Speaker: Erick Sibayan")
    b.textbox("S12", "250 Docs  •  25 / Class", 24, 72, 214, 48, font_size=15.5, bold=True, color=C_WHITE, bg_hex=C_NAVY, align="center", valign="MIDDLE")
    b.textbox("S12", "101 EN • 79 TL • 70 CAR", 253, 72, 214, 48, font_size=15.5, bold=True, color=C_WHITE, bg_hex=C_ROYAL, align="center", valign="MIDDLE")
    b.textbox("S12", "32 Official SLU Policies", 482, 72, 214, 48, font_size=15.5, bold=True, color=C_WHITE, bg_hex=C_TEAL, align="center", valign="MIDDLE")

    left_intents = [
        "1. TOR, COG & Credentials (3 pol)",
        "2. iSLU Portal & Enrollment (3 pol)",
        "3. Add / Drop & Overload (3 pol)",
        "4. Shifting & Qualifying Exam (4 pol)",
        "5. Grading, 75% & 20% FDA (3 pol)",
    ]
    right_intents = [
        "6. Exam Permit & Integrity (3 pol)",
        "7. Uniform & Campus Decorum (3 pol)",
        "8. Clinic, CCW, Seismic & DPA (4 pol)",
        "9. Tuition, Banks & Grants (3 pol)",
        "10. UNL Library, Labs & IT (3 pol)",
    ]
    for i, txt in enumerate(left_intents):
        py = 134 + i * 39
        b.rect("S12", 24, py, 7, 33, C_NAVY)
        b.textbox("S12", txt, 31, py, 321, 33, font_size=14, bold=True, color=C_TEXT, bg_hex=C_WHITE, valign="MIDDLE")
    for i, txt in enumerate(right_intents):
        py = 134 + i * 39
        b.rect("S12", 368, py, 7, 33, C_ROYAL)
        b.textbox("S12", txt, 375, py, 321, 33, font_size=14, bold=True, color=C_TEXT, bg_hex=C_WHITE, valign="MIDDLE")

    b.textbox(
        "S12",
        "Explicit Source_Type provenance:  32 Official  •  8 Harvested  •  210 Curated Multilingual",
        24, 336, 672, 36, font_size=14.5, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 13: 5-FOLD CV BENCHMARK CHART ====================
    b.add_slide("S13", C_BG_LIGHT, SPEAKER_NOTES[13])
    b.header_chrome("S13", 13, "Supervised 5-Fold CV Benchmarks (N = 250)", "Speaker: Erick Sibayan")
    b.image("S13", os.path.join(CHARTS_DIR, "tv_03_cv_comparison.png"), 66, 68, 588, 228)
    b.stat_card("S13", 24, 302, 214, 72, "95.61%", "Multinomial NB ★ (±1.47%)", bg=C_NAVY, num_size=26, lbl_size=12.5)
    b.stat_card("S13", 253, 302, 214, 72, "95.18%", "Logistic Reg. (±0.90%)", bg=C_ROYAL, num_size=26, lbl_size=12.5)
    b.stat_card("S13", 482, 302, 214, 72, "93.97%", "Linear SVM (±2.60%)", bg=C_TEAL, num_size=26, lbl_size=12.5)

    # ==================== SLIDE 14: 10x10 CONFUSION MATRIX ====================
    b.add_slide("S14", C_BG_LIGHT, SPEAKER_NOTES[14])
    b.header_chrome("S14", 14, "10×10 Confusion Matrix (Multinomial NB)", "Speaker: Erick Sibayan")
    b.image("S14", os.path.join(CHARTS_DIR, "tv_04_confusion_matrix.png"), 73, 68, 574, 265)
    b.textbox(
        "S14",
        "239 / 250 Exact Hits (95.6%)  •  3 Perfect Classes: SHIFT, LABS & FINANCE (25 / 25)",
        24, 338, 672, 36, font_size=14.5, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 15: HYBRID SCORING & TDD FIXES ====================
    b.add_slide("S15", C_BG_LIGHT, SPEAKER_NOTES[15])
    b.header_chrome("S15", 15, "Hybrid Retrieval & TDD Bug Hardening", "Speaker: Erick Sibayan")
    b.textbox(
        "S15",
        "Score  =  TF-IDF Cosine  +  0.14·Lexicon  +  0.30·P_NB(intent)  +  Policy Prior",
        24, 72, 672, 42, font_size=15, bold=True, color=C_GOLD_BRIGHT, bg_hex=C_NAVY, align="center", valign="MIDDLE",
    )
    b.card(
        "S15", 24, 126, 326, 116,
        "1. Native-Only CAR Detection",
        "English 'plagiarism' & 'disciplinary' no longer trigger false CAR greetings.",
        header_bg=C_ROYAL, title_size=15.5, header_h=34, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S15", 370, 126, 326, 116,
        "2. Calibrated OOD Safety Gate",
        "Gibberish & 'hello' never return personal posts (100% OOD rejection).",
        header_bg=C_TEAL, title_size=15.5, header_h=34, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S15", 24, 254, 326, 116,
        "3. Numeric & Legal Anchors",
        "Grade '74' hits 75% passing rule; cyberbullying routes to RA 10173.",
        header_bg=C_NAVY, title_size=15.5, header_h=34, body_size=14.5, line_spacing=130,
    )
    b.card(
        "S15", 370, 254, 326, 116,
        "4. Holistic NB Moderation",
        "Trained Naive Bayes resolves multi-keyword collisions cleanly.",
        header_bg=C_ROYAL, title_size=15.5, header_h=34, body_size=14.5, line_spacing=130,
    )

    # ==================== SLIDE 16: 4-STAGE ABLATION STUDY ====================
    b.add_slide("S16", C_BG_LIGHT, SPEAKER_NOTES[16])
    b.header_chrome("S16", 16, "4-Stage Retrieval Ablation (48 Unseen)", "Speaker: John Andrew Angcaway")
    b.image("S16", os.path.join(CHARTS_DIR, "tv_05_ablation.png"), 67, 68, 586, 264)
    b.textbox(
        "S16",
        "Full Hybrid by Register:   EN 91.7%   •   Taglish 100.0%   •   CAR 95.0%   •   0% FP-CAR",
        24, 338, 672, 36, font_size=14.5, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE",
    )

    # ==================== SLIDE 17: SECURITY, PARITY & WCAG UI ====================
    b.add_slide("S17", C_BG_LIGHT, SPEAKER_NOTES[17])
    b.header_chrome("S17", 17, "Security, Py↔JS Parity & Accessible UI", "Speaker: John Andrew Angcaway")
    b.card(
        "S17", 24, 74, 214, 296,
        "Zero XSS Defense",
        "• Zero .innerHTML calls\n\n• Safe textContent DOM\n\n• Strict CSP + Netlify headers\n\n• Passed <img onerror> test",
        header_bg=C_RED_FG, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )
    b.card(
        "S17", 253, 74, 214, 296,
        "100% Py↔JS Parity",
        "• Single build_portal.py\n\n• Same NB JSON weights\n\n• Verified via Node.js\n\n• 51 / 51 identical results",
        header_bg=C_NAVY, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )
    b.card(
        "S17", 482, 74, 214, 296,
        "WCAG 2.1 AA UI",
        "• SLU contrast ≥ 4.5:1\n\n• Keyboard ARIA tablist\n\n• Live 6-stage inspector\n\n• 4 interactive data tabs",
        header_bg=C_TEAL, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )

    # ==================== SLIDE 18: LIVE DEMO 1 (TAGLISH & ILOCANO) ====================
    b.add_slide("S18", C_BG_LIGHT, SPEAKER_NOTES[18])
    b.header_chrome("S18", 18, "Live Demo 1: Taglish & Ilocano Traces", "Speaker: John Andrew Angcaway")
    b.card(
        "S18", 24, 74, 326, 296,
        "Case 1 • Taglish Shifting (TL-EN)",
        "Query:\n\"Paano process ng shifting from SAMCIS to SEAIT? May QE ba?\"\n\n"
        "Intent:\n• ACADEMIC_SHIFTING_TRANSFER\n\n"
        "Matched Policy:\n• Internal Shifting & URO QE Rules",
        header_bg=C_NAVY, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )
    b.card(
        "S18", 370, 74, 326, 296,
        "Case 2 • Ilocano Attendance (CAR)",
        "Query:\n\"Naimbag a bigat! Agadal ak idiay SAMCIS—mano absent sakbay ma-FDA?\"\n\n"
        "Greeting:\n• Naimbag a bigat/aldaw! (ilo)\n\n"
        "Matched Policy:\n• Handbook Art. I (>20% → FDA)",
        header_bg=C_ROYAL, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )

    # ==================== SLIDE 19: LIVE DEMO 2 (KANKANAEY & OOD) ====================
    b.add_slide("S19", C_BG_LIGHT, SPEAKER_NOTES[19])
    b.header_chrome("S19", 19, "Live Demo 2: Kankanaey & OOD Safety", "Speaker: John Andrew Angcaway")
    b.card(
        "S19", 24, 74, 326, 296,
        "Case 3 • Kankanaey Integrity (CAR)",
        "Query:\n\"Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?\"\n\n"
        "Greeting:\n• Gawis ay agew! (kne)\n\n"
        "Matched Policy:\n• Handbook Art. II (Disciplinary Board)",
        header_bg=C_TEAL, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )
    b.card(
        "S19", 370, 74, 326, 296,
        "Case 4 • Out-of-Domain Safety Gate",
        "Query:\n\"What is the best recipe for Baguio strawberry sinigang?\"\n\n"
        "Status:\n• OUT_OF_DOMAIN (Score < 0.14)\n\n"
        "Result:\n• Zero hallucination → SLU Office Guide",
        header_bg=C_AMBER, title_size=16, header_h=36, body_size=14.5, line_spacing=132,
    )

    # ==================== SLIDE 20: LIMITATIONS & PRIVACY ====================
    b.add_slide("S20", C_BG_LIGHT, SPEAKER_NOTES[20])
    b.header_chrome("S20", 20, "Honest Limitations & RA 10173 Privacy", "Speaker: John Andrew Angcaway")
    b.card(
        "S20", 24, 74, 326, 296,
        "Transparent Provenance",
        "• 210 expanded queries explicitly tagged CURATED_MULTILINGUAL\n\n"
        "• Next: Formal validation with native ilo, kne & ibl linguists\n\n"
        "• Expand to Bontok & Ifugao idioms",
        header_bg=C_NAVY, title_size=16.5, header_h=36, body_size=15.5, line_spacing=134,
    )
    b.card(
        "S20", 370, 74, 326, 296,
        "RA 10173 Data Privacy",
        "• Zero student names, IDs, or private metadata stored\n\n"
        "• 100% client-side browser inference — queries stay on device\n\n"
        "• Static hosting eliminates DB breach risk",
        header_bg=C_ROYAL, title_size=16.5, header_h=36, body_size=15.5, line_spacing=134,
    )

    # ==================== SLIDE 21: FUTURE ROADMAP ====================
    b.add_slide("S21", C_BG_LIGHT, SPEAKER_NOTES[21])
    b.header_chrome("S21", 21, "Future Roadmap for SLU & CAR NLP", "Speaker: Chaze Rodriguez")
    milestones = [
        ("01", "Native CAR Community Validation", "Audit idioms, diacritics, and anonymized student logs with SLU & CAR speakers.", C_NAVY),
        ("02", "Compact Multilingual Embeddings + RAG", "Benchmark mE5 / LaBSE semantic retrieval with verbatim Handbook citations.", C_ROYAL),
        ("03", "Live iSLU & Institutional Integration", "Connect live URO academic calendars, OSAS advisories, and official ticketing.", C_TEAL),
    ]
    for idx, (num, title, desc, col) in enumerate(milestones):
        my = 76 + idx * 102
        b.rect("S21", 24, my, 672, 88, C_WHITE, outline_hex=C_BORDER)
        b.textbox("S21", num, 24, my, 84, 88, font_size=30, bold=True, color=C_GOLD_BRIGHT, bg_hex=col, align="center", valign="MIDDLE")
        b.textbox("S21", title, 120, my + 8, 564, 32, font_size=18, bold=True, color=C_NAVY, valign="MIDDLE")
        b.textbox("S21", desc, 120, my + 40, 564, 42, font_size=14.5, color=C_TEXT, valign="TOP", line_spacing=124)

    # ==================== SLIDE 22: IMPACT SUMMARY & Q&A (DARK NAVY HERO) ====================
    b.add_slide("S22", C_NAVY, SPEAKER_NOTES[22])
    b.rect("S22", 0, 0, 720, 8, C_GOLD)
    b.rect("S22", 0, 397, 720, 8, C_GOLD)
    b.textbox("S22", "Impact Summary & Open Q&A", 30, 22, 660, 44, font_size=32, bold=True, color=C_WHITE, align="center", valign="MIDDLE")
    b.textbox("S22", "Group 2 – AiNomally  •  Reproducible, Audited & Hardened SLU Multilingual NLP", 30, 66, 660, 26, font_size=14.5, color=C_ICE, align="center", valign="MIDDLE")

    b.stat_card("S22", 26, 104, 156, 122, "250 / 32", "Balanced Docs\n& SLU Policies", bg=C_ROYAL, num_size=30, lbl_size=13)
    b.stat_card("S22", 196, 104, 156, 122, "156", "Verified SLU +\nCAR Lexicon", bg=C_ROYAL, num_size=34, lbl_size=13)
    b.stat_card("S22", 366, 104, 156, 122, "95.61%", "5-Fold CV\nMacro F1 (NB)", bg=C_ROYAL, num_size=30, lbl_size=13)
    b.stat_card("S22", 536, 104, 156, 122, "95.2%", "Unseen Top-1\n100% OOD Safe", bg=C_ROYAL, num_size=32, lbl_size=13)

    b.textbox("S22", "21 / 21 Tests Passing  •  All Drive Docs & GitHub Synced", 26, 240, 514, 30, font_size=14, bold=True, color=C_WHITE, align="left", valign="MIDDLE")
    b.rect("S22", 26, 276, 220, 4, C_GOLD)
    b.textbox("S22", "Agyamanak! • Iyaman! • Thank You!", 26, 288, 514, 38, font_size=21, bold=True, color=C_GOLD_BRIGHT, align="left", valign="MIDDLE")
    b.textbox("S22", "Live Portal:  slu-egovernance-chatbot.netlify.app", 26, 330, 514, 24, font_size=14.5, bold=True, color=C_ICE, align="left", valign="MIDDLE")
    b.textbox("S22", "Code:  github.com/ChazeRodriguez/slu-egovernance-chatbot-car-lexicon", 26, 356, 514, 22, font_size=11.5, color="#CBD5E1", align="left", valign="MIDDLE")

    # Crisp high-contrast QR Code card on bottom-right for instant classroom phone scan
    qr_path = os.path.join(PRES_DIR, "portal_qr.png")
    b.rect("S22", 556, 234, 136, 152, C_WHITE, outline_hex=C_GOLD)
    if os.path.exists(qr_path):
        b.image("S22", qr_path, 564, 240, 120, 120)
    b.textbox("S22", "SCAN LIVE DEMO", 556, 360, 136, 22, font_size=11, bold=True, color=C_NAVY, align="center", valign="MIDDLE")


def export_speaker_script_md():
    os.makedirs(PRES_DIR, exist_ok=True)
    lines = [
        "# Group 2 – AiNomally | CSE 30 Classroom TV Presentation Script (22 Slides, 15–20 Minutes)",
        "",
        "**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  ",
        "**Institution:** Saint Louis University (SAMCIS – Department of Computer Science), Baguio City  ",
        "**Instructor:** Prof. Dalos D. Miguel  ",
        "**Deck Format:** 22-Slide Large-Print Classroom TV Edition (minimum 14–16pt body/table type, full-canvas large-print charts)",
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
        note = SPEAKER_NOTES[s_num]
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
    parser = argparse.ArgumentParser(description="Build Group 2 AiNomally 22-slide Classroom TV CSE 30 deck.")
    parser.add_argument("--pptx-only", action="store_true", help="Only regenerate local .pptx and speaker script without creating a new Google Slides deck.")
    parser.add_argument("--sync-script-doc", action="store_true", help="Also sync speaker script to Google Drive Doc when using --pptx-only.")
    args = parser.parse_args()

    os.makedirs(PRES_DIR, exist_ok=True)
    builder = ClassroomTVDeckBuilder()
    build_deck_content(builder)

    # 1. Save local PowerPoint backup
    pptx_path = os.path.join(PRES_DIR, "Group2_AiNomally_CSE30_Deck.pptx")
    builder.prs.save(pptx_path)
    print(f"[OK] Saved local PowerPoint -> {pptx_path}")

    # 2. Save local speaker script (+ optional Drive sync)
    _, script_lines = export_speaker_script_md()
    if args.pptx_only:
        if args.sync_script_doc:
            sync_drive_presentation_script(script_lines)
        return
    sync_drive_presentation_script(script_lines)

    # 3. Create fresh Classroom TV Edition Google Slides presentation
    create_res = subprocess.run(
        [
            "gslides", "mutate", "create", "--title",
            "CSE 30 Final Presentation (Classroom TV Edition) — SLU eGovernance Chatbot & CAR Lexicon (Group 2 AiNomally)",
        ],
        capture_output=True, text=True, check=True,
    )
    print(create_res.stdout.strip())
    m_id = re.search(r"presentation/d/([A-Za-z0-9_-]+)|ID:\s*([A-Za-z0-9_-]+)", create_res.stdout)
    if not m_id:
        raise RuntimeError(f"Could not parse presentation ID from: {create_res.stdout}")
    pres_id = m_id.group(1) or m_id.group(2)
    print(f"[OK] Created Classroom TV Google Slides Deck ID: {pres_id}")

    # 4. Execute single-batch layout + tables + speaker notes
    batch_path = os.path.join(SCRATCH, "slides_tv_batch.json")
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(builder.ops, f, ensure_ascii=False, indent=2)

    batch_res = subprocess.run(
        ["gslides", "mutate", "batch", pres_id, "-f", batch_path, "--json"],
        capture_output=True, text=True, check=True,
    )
    batch_json = json.loads(batch_res.stdout)
    resolved = batch_json.get("resolved_ids", {})
    resolved["p"] = "p"
    print(f"[OK] Batch built {len(builder.slide_order)} TV slides ({batch_json.get('api_requests')} API requests)")

    # 5. Insert large-print TV charts onto their exact target slides
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

    # Save presentation metadata for visual QA pass
    meta = {
        "presentation_id": pres_id,
        "url": f"https://docs.google.com/presentation/d/{pres_id}/edit",
        "resolved_ids": resolved,
        "slide_order": builder.slide_order,
    }
    meta_path = os.path.join(SCRATCH, "slides_tv_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[OK] Saved Classroom TV deck metadata -> {meta_path}")
    print(f"[URL] {meta['url']}")


if __name__ == "__main__":
    main()
