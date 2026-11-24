# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/build_presentation.py
Description: Builds the complete 18-slide (15-20 minute) presentation across:
             1. Google Slides (SLU Louisian Executive Theme, batch API, embedded charts, speaker notes)
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

# SLU Brand Colors
C_NAVY = "#002855"
C_ROYAL = "#004B87"
C_TEAL = "#0E7490"
C_GOLD = "#D4AF37"
C_GOLD_BRIGHT = "#FACC15"
C_GOLD_LIGHT = "#FEF9C3"
C_BG_LIGHT = "#F8FAFC"
C_WHITE = "#FFFFFF"
C_TEXT = "#0F172A"
C_MUTED = "#475569"
C_ICE = "#DBEAFE"
C_GREEN_BG = "#DCFCE7"
C_GREEN_FG = "#14532D"
C_RED_BG = "#FEE2E2"
C_RED_FG = "#991B1B"

# ==============================================================================
# SLIDE DEFINITIONS + TIMED 5-SPEAKER NOTES (~18.5 MIN TOTAL + Q&A)
# ==============================================================================

SPEAKER_NOTES = {
    1: (
        "[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 0:45]\n"
        "Good afternoon, Professor Dalos Miguel, and fellow Louisians. We are Group 2, AiNomally—composed of "
        "John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, Erick James Sibayan, and myself, Chaze Rodriguez. "
        "Today we present our complete CSE 30 NLP Term Project: a Multilingual Domain-Specific Electronic Lexicon, "
        "Supervised Intent Classifier, and Hardened eGovernance Student Support Chatbot built specifically for "
        "Saint Louis University in Baguio City. Over the next 18 minutes, we will walk you through our journey from "
        "raw data collection and Midterm audit verification all the way to our Finals expansion—scaling to 250 balanced "
        "documents, 156 SLU and Cordilleran lexicon entries, leak-free 5-fold cross-validated machine learning models, "
        "and a security-hardened interactive web portal."
    ),
    2: (
        "[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:15]\n"
        "Let us begin with why this project matters here in Baguio City and the Cordillera Administrative Region. "
        "We are tackling two intersecting challenges simultaneously. On the institutional side, Saint Louis University "
        "serves tens of thousands of students, yet critical policies—ranging from URO transcript requests and shifting rules "
        "to 20 percent Failure Due to Absences thresholds, exam permits, clinic clearances, and financial aid—are fragmented "
        "across static PDF handbooks, separate office webpages, and informal public forums like the SLU Freedom Wall. "
        "Students routinely rely on unverified peer advice because standard English keyword searches fail when queries mix "
        "Taglish clitics like 'ngaun' or 'dp' with local expressions. On the linguistic side, regional CAR languages—specifically "
        "Ilocano, Northern Kankanaey, and Ibaloi—face severe digital resource scarcity. By embedding authentic Cordilleran "
        "vocabulary directly into an institutional eGovernance chatbot, we make campus services more accessible while preserving "
        "local languages in active computational infrastructure."
    ),
    3: (
        "[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:00]\n"
        "Our design aligns directly with both tracks of the CSE 30 term project requirements. Under Track A, we engineered "
        "a machine-readable electronic lexicon linking SLU institutional acronyms and campus Taglish with validated Ilocano, "
        "Northern Kankanaey, and Ibaloi lemmas, complete with ISO 639-3 tags, parts of speech, morphological roots, and "
        "bilingual glosses. Under Track B, we built an end-to-end eGovernance chatbot application capable of resolving "
        "multilingual student questions against verified SLU regulations. To accomplish this rigorously, we committed to four "
        "engineering objectives: first, a single-command reproducible local pipeline; second, test-driven bug and security "
        "hardening; third, scaling our CAR lexicon and balanced corpus with transparent provenance; and fourth, empirical "
        "benchmarking via leak-free Stratified 5-Fold Cross-Validation and held-out retrieval ablations. I will now turn the "
        "floor to Keith to present our system architecture, corpus scaling, and data audit."
    ),
    4: (
        "[Speaker 2: Keith Russel Hernandez | Target: 1:15]\n"
        "Thank you, Chaze. Slide 4 shows our complete five-stage deterministic NLP architecture. Everything starts in Stage 1 "
        "with multi-source data acquisition: harvesting authentic #SLUFreedomWall posts via slu_web_scraper.py and verifying "
        "official SLU policy provisions directly from slu.edu.ph, dataprotection.slu.edu.ph, and the 2015 Student Handbook. "
        "In Stage 2, data_cleaning.py executes acronym-safe normalization without deleting parenthetical acronyms like SAMCIS "
        "or TOR. Stage 3 runs car_morphology.py and data_preprocessing.py for guarded English, Filipino, and CAR lemmatization "
        "and bigram extraction. Stage 4 trains our zero-dependency pure-Python supervised classifiers—Multinomial Naive Bayes, "
        "Logistic Regression, and Linear SVM—and feeds serialized model weights into our hybrid retrieval engine alongside our "
        "156-entry lexicon. Finally, Stage 5 uses build_portal.py as a single source of truth to inject verified JSON data and "
        "model weights directly into our 4-tab web portal and Netlify deployment bundle, eliminating manual drift across files."
    ),
    5: (
        "[Speaker 2: Keith Russel Hernandez | Target: 1:15]\n"
        "Moving to Slide 5, you can see the quantitative leap from our Midterm baseline to our Finals expansion. Our Midterm "
        "baseline established 24 consolidated documents, 12 authoritative policies, and 25 lexicon entries—which was great for a "
        "proof of concept, but left zero authoritative policy coverage for Tuition/Finance or Campus Facilities/Labs, and had "
        "only two CAR-tagged posts. For Finals, we expanded authoritative SLU policies from 12 to 32 verified provisions covering "
        "all 10 operational intents, including Finance payment channels, SLU Entrance and Academic Scholarships, Center for "
        "Counseling and Wellness support, and Msgr. Charles Vath University Libraries borrowing rules. We scaled the annotated "
        "corpus over tenfold to 250 perfectly balanced documents—25 per intent—with 40.4% English, 31.6% Taglish, and 28.0% "
        "authentic CAR-TL-EN inquiries, all transparently labeled by Source_Type provenance."
    ),
    6: (
        "[Speaker 2: Keith Russel Hernandez | Target: 1:00]\n"
        "One of the most valuable CS engineering practices we applied was an unbiased end-to-end data audit across our local "
        "files and Google Drive deliverables. Before scaling up, we ran automated reproducibility checks and uncovered six real "
        "discrepancies that could have compromised our defense. Our earlier paper and script still reported 352 stems and 9 "
        "occurrences of 'semester' when the verified corpus actually had 426 unique stems and 8 occurrences of 'semester'. Two "
        "bigrams—'bonifacio campus' and 'minimum grade'—were mistakenly listed with frequency 2 when both occurred once. Doc 6 "
        "was labeled #25582 instead of its real raw post ID #25604, and the Google Sheet still contained uncleaned Prelim rows. "
        "We fixed every single mismatch, synced Drive and Sheets, and built build_all.py so one command regenerates and tests "
        "every artifact with zero discrepancies. Next, Earold will detail our cleaning and morphological engineering."
    ),
    7: (
        "[Speaker 3: Earold Jan Delin | Target: 1:15]\n"
        "Thank you, Keith. Slide 7 highlights how we engineered and hardened Stage 2—our deterministic acronym-safe text cleaner "
        "in data_cleaning.py. Standard regex cleaning pipelines often strip all parenthetical text, which would wipe out vital "
        "SLU identifiers like SAMCIS, TOR, COG, MLS, QE, FDA, and PATHFIT. Our targeted timestamp filter strips only scrape "
        "metadata while protecting every acronym. During our Phase 2 hardening audit, we caught and fixed five subtle real-world "
        "defects shown in this transformation table: replacing naive '\\bill\\b' so 'I am feeling ill' is never corrupted to "
        "'i am feeling i will' while 'ill still answer' still expands properly; stripping possessive apostrophe-s cleanly so "
        "'SLU's Registrar's Office' does not turn into 'slu is registrar is office'; preserving question marks when collapsing "
        "'??'; adding 'niyo' to 'ninyo' and arbitrary laughter collapse; and protecting hyphenated Cordilleran lemmas like "
        "'dap-ay' and 'man-obla' so they survive tokenization intact."
    ),
    8: (
        "[Speaker 3: Earold Jan Delin | Target: 1:15]\n"
        "On Slide 8, we address one of the hardest challenges in Philippine NLP: bilingual and Cordilleran morphological "
        "analysis. In our early Prelim prototype, unguarded prefix and suffix stripping severely damaged English words—turning "
        "'campus' into 'campu', 'department' into 'depart', and 'management' into 'nage'. Even with a basic prefix guard, "
        "unseen words like 'magnify', 'magician', 'magical', and Tagalog 'maganda' still got corrupted because they start with "
        "'mag-'. In car_morphology.py, we solved this with a three-layer architecture: first, a verified English, Filipino, and "
        "CAR lemma lookup covering infixed verbs like 'tumataas' to 'taas' and 'sumulat' to 'sulat'; second, explicit English "
        "root exceptions plus suffix guards blocking Filipino prefix stripping on Latinate words; and third, clean Austronesian "
        "affix normalization across Tagalog mag-/nag-/pag-, Ilocano ag-/panag-/na-, Kankanaey man-/men-, and Ibaloi ma-/man-."
    ),
    9: (
        "[Speaker 3: Earold Jan Delin | Target: 1:00]\n"
        "Slide 9 presents our verified Midterm lexical profiling chart generated directly from corpus_bow_summary.csv and "
        "preprocessed_tokens.json. Across all 24 consolidated Midterm documents, filtering 265 English and Filipino stopwords "
        "yields exactly 624 content tokens, 457 unique surface forms, and 426 unique verified stems—a type-token ratio of "
        "0.6827 with zero corrupted roots. Institutional terms clearly lead the vocabulary: 'student' appears 16 times at 2.56% "
        "coverage, followed by 'slu' at 10, 'examination' at 9, 'semester' at 8 highlighted in gold, and 'grade', 'requirement', "
        "and 'subject' at 7 each. On the right, we verified all 19 truly recurring contiguous bigrams such as 'official transcript', "
        "'qualifying examination', 'student portal', 'failure due', and 'examination permit'—removing stale singleton claims. "
        "I now hand the presentation to Erick for our expanded CAR lexicon, annotations, and supervised machine learning benchmarks."
    ),
    10: (
        "[Speaker 4: Erick James Sibayan | Target: 1:30]\n"
        "Thank you, Earold. Slide 10 showcases our flagship Track A contribution: scaling the SLU and CAR Multilingual Electronic "
        "Lexicon from 25 baseline items to 156 verified entries—comprising 36 SLU institutional acronyms and Taglish terms, "
        "48 Ilocano entries, 40 Northern Kankanaey entries, and 32 Ibaloi entries grounded in Constantino, Rubino, Vanoverbergh, "
        "Ballard, and SIL Philippines dictionaries. Notice the linguistic richness captured here: look at the cognate row for "
        "'water'—Ilocano 'danum', Kankanaey 'danom', and Ibaloi 'shanom', reflecting Ibaloi's signature postalveolar shift. "
        "Equally important, we preserve deeply cultural Cordilleran governance concepts: Kankanaey 'inayan' (ethical restraint "
        "against wrongdoing), 'dap-ay' (communal council), 'ubbo' (mutual cooperative work), and Ibaloi 'tongtong' (customary "
        "dispute mediation). Crucially, we architected separate Native_Aliases and Semantic_Aliases columns so English synonyms "
        "assist policy retrieval without ever falsely triggering indigenous language greetings."
    ),
    11: (
        "[Speaker 4: Erick James Sibayan | Target: 1:00]\n"
        "On Slide 11, we detail the multi-layer annotation schema behind our 250-document Finals corpus. Every single document "
        "is tagged across four transparent dimensions: one of 10 balanced operational intent classes with exactly 25 documents "
        "each; sentiment and urgency polarity distinguishing authoritative policy from neutral inquiries and urgent student "
        "grievances; code-switching register across EN, TL-EN, and CAR-TL-EN; and an explicit Source_Type provenance tag "
        "separating official SLU policies, harvested Freedom Wall threads, and curated multilingual benchmark utterances. "
        "Ensuring 25 examples per class across all 10 intents is what makes rigorous Stratified 5-Fold Cross-Validation "
        "mathematically valid—giving every single validation fold exactly 5 unseen samples per intent class."
    ),
    12: (
        "[Speaker 4: Erick James Sibayan | Target: 1:30]\n"
        "Slide 12 presents the centerpiece of our supervised NLP experiments. We implemented three classic text classifiers "
        "completely from scratch in zero-dependency pure Python—Multinomial Naive Bayes with Lidstone smoothing, L2-regularized "
        "Multinomial Logistic Regression, and One-vs-Rest Linear SVM—and benchmarked them via leak-free Stratified 5-Fold "
        "Cross-Validation where TF-IDF vocabularies and IDF weights are fitted strictly inside each training fold. As shown on "
        "the left chart, all three models achieve strong generalization over 10 multilingual classes: Multinomial Naive Bayes "
        "leads with 95.60% Accuracy and 95.61% Macro F1 plus-or-minus 1.47%; Logistic Regression follows closely at 95.18% "
        "Macro F1 with the lowest cross-fold variance at 0.90%; and Linear SVM scores 93.97% Macro F1. On the right, the 10-by-10 "
        "confusion matrix confirms crisp diagonal precision—achieving perfect 25-of-25 recall on Shifting, Facilities/Labs, and "
        "Tuition/Finance, with only 11 minor misclassifications across all 250 out-of-fold predictions. Next, John Andrew will "
        "present our hybrid retrieval engine, ablation findings, and security engineering."
    ),
    13: (
        "[Speaker 5: John Andrew Angcaway | Target: 1:15]\n"
        "Thank you, Erick. Slide 13 explains how we combined our supervised Naive Bayes classifier, 156-entry lexicon, and "
        "TF-IDF cosine engine into a hardened hybrid retrieval architecture—and the real bugs we eliminated through Test-Driven "
        "Development. In our earlier prototype, asking plain English 'What is the punishment for plagiarism?' triggered a "
        "false-positive Kankanaey greeting because 'plagiarism' was mixed into 'inayan's' alias list, and gibberish queries "
        "silently hallucinated Freedom Wall Doc 1 as an official SLU policy. We wrote 12 failing regression tests first, then "
        "implemented four core safeguards: native-only CAR greeting triggers; a calibrated out-of-domain confidence gate plus "
        "conversational greeting handler; numeric policy anchoring so asking 'What happens if I get 74?' retrieves the 75% "
        "passing grade rule instead of dropping subjects; and moderated lexicon boosting so holistic Naive Bayes intent leads "
        "whenever a student mentions entities from two different offices in one sentence."
    ),
    14: (
        "[Speaker 5: John Andrew Angcaway | Target: 1:15]\n"
        "Slide 14 shows the empirical payoff in our 4-Stage Held-Out Retrieval Ablation Study across 48 strictly unseen queries "
        "with zero text overlap against our 250-document training corpus—covering 42 in-domain multilingual queries, 4 OOD traps, "
        "and 2 greetings. Look at the compelling scientific story in the chart. Stage A, Raw TF-IDF Cosine alone, scores 83.3% "
        "Top-1 accuracy, 0.893 MRR, and 0% OOD rejection because it hallucinates on gibberish. Stage B adds acronym-safe cleaning "
        "and CAR morphology, jumping nearly 10 percentage points to 92.9% Top-1 and 0.960 MRR. Stage C adds our 156-entry lexicon "
        "and OOD gate—pushing OOD rejection from 0% to 100%, but revealing an honest trade-off: greedy single-keyword rules "
        "slightly dipped Top-1 to 90.5% on multi-entity queries like RFID validation after paying tuition. Stage D, our Full Hybrid "
        "adding the trained Naive Bayes classifier, resolves those multi-entity collisions to achieve the highest overall result: "
        "95.2% Top-1 Policy Accuracy, 97.6% Top-3 Recall, 0.9643 MRR, 100% OOD Rejection, and 0.0% False-Positive CAR greetings."
    ),
    15: (
        "[Speaker 5: John Andrew Angcaway | Target: 1:00]\n"
        "On Slide 15, we highlight the software engineering and security hardening that transforms this from a classroom script "
        "into a production-grade eGovernance portal. First, during our security audit we spotted DOM XSS where raw user queries "
        "were inserted via .innerHTML; we eliminated every single .innerHTML call in favor of safe DOM node construction and "
        "textContent, added strict Content-Security-Policy headers and dist/netlify.toml security headers, and capped input lengths. "
        "Second, we eliminated Python-versus-JavaScript drift by compiling verified JSON data and trained Naive Bayes weights "
        "directly from build_portal.py—and verified 100% identical outputs across all 51 held-out and XSS test queries by running "
        "the HTML portal's actual JavaScript inside Node.js against Python. Third, the 4-tab portal meets WCAG 2.1 AA standards "
        "with ARIA tablists, arrow-key navigation, aria-live regions, and mobile-to-desktop responsiveness. I will now turn it "
        "back to Chaze for our live walkthrough, limitations, and closing."
    ),
    16: (
        "[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:30]\n"
        "Thank you, John Andrew. On Slide 16, let us walk through four live multilingual query traces from our 4-tab interactive "
        "portal—and if time permits during Q&A, we can also open the live portal directly. First, a Taglish shifting query from "
        "SAMCIS to SEAIT cleanly normalizes acronyms, predicts ACADEMIC_SHIFTING_TRANSFER, and returns both internal shifting "
        "guidelines and Qualifying Examination rules with direct slu.edu.ph links. Second, an Ilocano-Taglish query—'Naimbag a "
        "bigat! Agadal ak idiay SAMCIS—mano a porsiento ti absent sakbay ma-FDA?'—recognizes native Ilocano lemmas, replies with "
        "a genuine Ilocano greeting, and cites Handbook Article I, Section 2's 20% FDA threshold. Third, a Kankanaey query using "
        "'Gawis ay agsapa! Inayan ti plagiarism' retrieves Handbook Article II, Section 4 on academic dishonesty. Finally, an "
        "out-of-domain trap asking for a Baguio strawberry sinigang recipe is safely caught by our confidence gate with an honest "
        "redirect to URO, OSAS, Finance, Clinic, and Security offices—zero hallucination."
    ),
    17: (
        "[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:00]\n"
        "In the spirit of rigorous academic honesty, Slide 17 outlines our project's current limitations, data privacy safeguards, "
        "and next-step roadmap. First, regarding provenance: while our 32 SLU policies and harvested Freedom Wall threads are "
        "primary institutional and community texts, the 210 expanded multilingual training utterances are transparently flagged "
        "as curated benchmark examples; a critical next step before campus-wide rollout is formal validation with native Ilocano, "
        "Northern Kankanaey, and Ibaloi speakers and linguists alongside anonymized real student chat logs. Second, under Republic "
        "Act 10173, our portal runs 100% client-side in the browser—meaning student questions never leave their device and zero "
        "personal identifiers are stored. Third, future iterations can extend our zero-dependency linear stack with lightweight "
        "multilingual dense embeddings and strictly policy-grounded retrieval-augmented generation."
    ),
    18: (
        "[All Members / Chaze Closing | Target: 0:45]\n"
        "To conclude on Slide 18: Group 2 AiNomally delivered a fully reproducible, audited, security-hardened multilingual NLP "
        "ecosystem for Saint Louis University. From 250 balanced multi-layer annotated documents and 156 verified SLU and CAR "
        "lexicon entries to 95.61% Stratified 5-Fold CV Macro F1, 95.2% unseen Top-1 retrieval accuracy, 100% OOD safety, and "
        "21 passing automated unit, classifier, parity, and security tests, every claim in our paper, spreadsheet, and web portal "
        "is backed by runnable code. All repository scripts, data, charts, and synced Google Drive deliverables are ready for "
        "inspection. Thank you very much, Professor Dalos Miguel and classmates—we are now open for your questions and live demo "
        "requests!"
    ),
}

# ==============================================================================
# HELPER FUNCTIONS FOR GOOGLE SLIDES BATCH JSON + PARALLEL PYTHON-PPTX BUILD
# ==============================================================================

def hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class DualDeckBuilder:
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
        self.ops.append(op)
        ps = self.pptx_slides[slide_id]
        shp = ps.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
        shp.fill.solid()
        shp.fill.fore_color.rgb = hex_to_rgb(bg_hex)
        if outline_hex:
            shp.line.color.rgb = hex_to_rgb(outline_hex)
            shp.line.width = Pt(1)
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
        font_size=12,
        bold=False,
        italic=False,
        color=C_TEXT,
        bg_hex=None,
        align="left",
        valign="TOP",
        line_spacing=125,
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
        tf.margin_left = Pt(6)
        tf.margin_right = Pt(6)
        tf.margin_top = Pt(4)
        tf.margin_bottom = Pt(4)
        tf.vertical_anchor = (
            MSO_ANCHOR.MIDDLE if valign == "MIDDLE" else (MSO_ANCHOR.BOTTOM if valign == "BOTTOM" else MSO_ANCHOR.TOP)
        )
        p_align = PP_ALIGN.CENTER if align == "center" else (PP_ALIGN.RIGHT if align == "right" else PP_ALIGN.LEFT)
        lines = text.split("\n")
        for idx, ln in enumerate(lines):
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

    def header_chrome(self, slide_id, slide_num, title, subtitle, speaker_label):
        self.rect(slide_id, 0, 0, 720, 56, C_NAVY)
        self.rect(slide_id, 0, 56, 720, 3, C_GOLD)
        self.textbox(slide_id, title, 22, 6, 600, 26, font_size=18, bold=True, color=C_WHITE)
        self.textbox(slide_id, subtitle, 22, 31, 610, 20, font_size=10, color=C_ICE)
        self.textbox(
            slide_id,
            f"{slide_num} / 18",
            640,
            15,
            60,
            24,
            font_size=11,
            bold=True,
            color=C_GOLD_BRIGHT,
            align="right",
            valign="MIDDLE",
        )
        # Footer
        self.rect(slide_id, 0, 386, 720, 19, C_WHITE)
        self.textbox(
            slide_id,
            "Saint Louis University (SAMCIS) • CSE 30 NLP • Group 2 – AiNomally",
            22,
            387,
            430,
            16,
            font_size=8.5,
            color=C_MUTED,
            valign="MIDDLE",
        )
        self.textbox(
            slide_id,
            speaker_label,
            460,
            387,
            238,
            16,
            font_size=8.5,
            bold=True,
            color=C_NAVY,
            align="right",
            valign="MIDDLE",
        )

    def card(self, slide_id, x, y, w, h, title, body, header_bg=C_NAVY, title_color=C_WHITE, body_size=10.5, line_spacing=130, header_h=26, title_size=11.5):
        self.rect(slide_id, x, y, w, h, C_WHITE, outline_hex="#CBD5E1")
        self.textbox(slide_id, title, x, y, w, header_h, font_size=title_size, bold=True, color=title_color, bg_hex=header_bg, valign="MIDDLE")
        self.textbox(slide_id, body, x + 4, y + header_h + 2, w - 8, h - header_h - 6, font_size=body_size, color=C_TEXT, line_spacing=line_spacing)

    def arrow(self, slide_id, x, y, width, color=C_GOLD):
        self.ops.append({
            "op": "add-line",
            "slide": slide_id,
            "line_category": "STRAIGHT",
            "x": x,
            "y": y,
            "width": width,
            "height": 0,
            "color": color,
            "line_weight": 2.2,
            "end_arrow": "FILL_ARROW",
        })
        ps = self.pptx_slides[slide_id]
        shp = ps.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Pt(x), Pt(y - 4), Pt(width), Pt(8))
        shp.fill.solid()
        shp.fill.fore_color.rgb = hex_to_rgb(color)
        shp.line.fill.background()

    def stat_card(self, slide_id, x, y, w, h, num, label, bg=C_NAVY, num_color=C_GOLD_BRIGHT, lbl_color=C_WHITE):
        self.rect(slide_id, x, y, w, h, bg)
        self.rect(slide_id, x, y + h - 4, w, 4, C_GOLD)
        self.textbox(slide_id, num, x + 4, y + 6, w - 8, int(h * 0.52), font_size=24, bold=True, color=num_color, align="center", valign="MIDDLE")
        self.textbox(slide_id, label, x + 6, y + int(h * 0.54), w - 12, int(h * 0.38), font_size=9.5, bold=True, color=lbl_color, align="center", valign="TOP")

    def table(self, slide_id, table_id, x, y, w, h, data, font_size=9.2, header_bg=C_NAVY, col_widths=None):
        rows, cols = len(data), len(data[0])
        self.ops.append({"op": "add-table", "slide": slide_id, "rows": rows, "cols": cols, "id": table_id, "x": x, "y": y, "width": w, "height": h})
        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                is_hdr = r_idx == 0
                bg = header_bg if is_hdr else (C_WHITE if r_idx % 2 == 1 else "#F1F5F9")
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
                cell.fill.fore_color.rgb = hex_to_rgb(header_bg if is_hdr else (C_WHITE if r_idx % 2 == 1 else "#F1F5F9"))
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
    # ==================== SLIDE 1: TITLE (DARK NAVY) ====================
    b.add_slide("p", C_NAVY, SPEAKER_NOTES[1])
    b.rect("p", 0, 0, 720, 8, C_GOLD)
    b.rect("p", 0, 397, 720, 8, C_GOLD)
    b.textbox("p", "SAINT LOUIS UNIVERSITY • BAGUIO CITY • SAMCIS DEPARTMENT OF COMPUTER SCIENCE", 40, 32, 640, 24, font_size=10.5, bold=True, color=C_GOLD_BRIGHT, align="center")
    b.textbox("p", "SLU eGovernance Multilingual Chatbot\n& CAR Electronic Lexicon", 40, 74, 640, 96, font_size=32, bold=True, color=C_WHITE, align="center", line_spacing=115)
    b.textbox("p", "Curated Natural Language Resources, Guarded Cordilleran Morphology,\nLeak-Free Supervised Intent Classification & Hardened Web Deployment", 55, 178, 610, 46, font_size=13.5, color=C_ICE, align="center", line_spacing=125)
    b.rect("p", 260, 236, 200, 3, C_GOLD)
    b.textbox("p", "Group 2 – AiNomally", 40, 252, 640, 26, font_size=16, bold=True, color=C_GOLD_BRIGHT, align="center")
    b.textbox("p", "John Andrew Angcaway  •  Earold Jan Delin  •  Keith Russel Hernandez  •  Chaze Ezkys M. Rodriguez  •  Erick James Sibayan", 35, 282, 650, 26, font_size=10.5, color=C_WHITE, align="center")
    b.textbox("p", "CSE 30: CS Special Topics (Natural Language Processing)  |  Class Code 9712 (01:30–03:00 MTh)  |  Instructor: Prof. Dalos D. Miguel", 35, 344, 650, 24, font_size=9.5, color=C_ICE, align="center")

    # ==================== SLIDE 2: PROBLEM & CONTEXT ====================
    b.add_slide("S02", C_BG_LIGHT, SPEAKER_NOTES[2])
    b.header_chrome("S02", 2, "The Problem: Fragmented Governance & Regional Language Gap", "Why Saint Louis University in Baguio City needs a multilingual CAR-aware NLP assistant", "Speaker 1: Chaze Rodriguez (1:15)")
    b.card(
        "S02", 24, 72, 326, 232,
        "1. Institutional Support Bottlenecks at SLU",
        "• Authoritative rules are scattered across the 2015 Student Handbook PDF, URO pages, OSAS/Finance circulars, and clinic notices.\n\n"
        "• Students ask urgent questions in informal Taglish on #SLUFreedomWall (shifting, tuition dp, 20% FDA, TOR clearance, lab supplies).\n\n"
        "• Standard English keyword search fails on clitics (ngaun, di'ba, dp, ambilat) and SLU acronyms (SAMCIS, SEAIT, SONAHBS, QE, PATHFIT).",
        header_bg=C_NAVY, body_size=10.5
    )
    b.card(
        "S02", 370, 72, 326, 232,
        "2. Cordilleran (CAR) Digital Resource Scarcity",
        "• Baguio City and CAR host thriving Ilocano (ilo), Northern Kankanaey (kne), and Ibaloi (ibl) student populations.\n\n"
        "• Rich Austronesian affixation (ag-, panag-, man-, men-, -um-, -in-) is unsupported by off-the-shelf English NLP pipelines.\n\n"
        "• Cultural concepts like inayan, dap-ay, ubbo, and tongtong carry governance meaning that English-only chatbots completely miss.",
        header_bg=C_ROYAL, body_size=10.5
    )
    b.textbox(
        "S02",
        "Core Thesis: Unifying verified SLU institutional policies with a structured CAR electronic lexicon solves student support bottlenecks while advancing digital preservation of Cordilleran languages.",
        24, 318, 672, 54, font_size=11, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, valign="MIDDLE", align="center"
    )

    # ==================== SLIDE 3: CSE 30 ALIGNMENT & OBJECTIVES ====================
    b.add_slide("S03", C_BG_LIGHT, SPEAKER_NOTES[3])
    b.header_chrome("S03", 3, "CSE 30 Research Alignment & Four Engineering Objectives", "Bridging Track A (CAR Electronic Lexicons) and Track B (eGovernance NLP Applications)", "Speaker 1: Chaze Rodriguez (1:00)")
    b.card(
        "S03", 24, 72, 326, 118,
        "Track A • CAR Electronic Lexicon",
        "• 156 machine-readable lexical entries (SLU + Ilocano + Kankanaey + Ibaloi).\n"
        "• ISO 639-3 tags, POS, morphological roots, affixes, bilingual EN/FIL glosses, and Native vs. Semantic alias separation.",
        header_bg=C_ROYAL, body_size=10.2
    )
    b.card(
        "S03", 370, 72, 326, 118,
        "Track B • SLU eGovernance Chatbot",
        "• Hybrid TF-IDF + Lexicon + Supervised Naive Bayes intent assistant covering 10 SLU operational domains & 32 verified policies.\n"
        "• Zero-dependency CLI engine + accessible 4-tab browser portal with live source citations.",
        header_bg=C_TEAL, body_size=10.2
    )
    objs = [
        ("Obj. 1: Reproducibility", "Single-command local pipeline (build_all.py) reproducing Midterm & Finals with 0 Drive drift."),
        ("Obj. 2: TDD Hardening", "Eliminate false CAR greetings, 'ill'/possessive bugs, OOD hallucinations, and DOM XSS."),
        ("Obj. 3: Scaling & Balance", "Scale to 250 balanced docs (25/intent), 32 official SLU policies, and 156 CAR lexicon entries."),
        ("Obj. 4: Empirical Rigor", "Leak-free Stratified 5-Fold CV (NB/LR/SVM) + 4-stage ablation on 48 unseen queries."),
    ]
    for idx, (ot, ob) in enumerate(objs):
        ox = 24 + idx * 171
        b.card("S03", ox, 204, 159, 168, ot, ob, header_bg=C_NAVY if idx % 2 == 0 else C_ROYAL, body_size=9.5, line_spacing=125)

    # ==================== SLIDE 4: 5-STAGE NLP ARCHITECTURE ====================
    b.add_slide("S04", C_BG_LIGHT, SPEAKER_NOTES[4])
    b.header_chrome("S04", 4, "End-to-End 5-Stage Reproducible NLP Architecture", "From raw multi-source ingestion to zero-drift browser inference (scripts/build_all.py)", "Speaker 2: Keith Hernandez (1:15)")
    stages = [
        ("Stage 1\nData Acquisition", "slu_web_scraper.py\n\n• 8 Freedom Wall posts\n• 32 verified SLU policies (URO, Handbook, OSAS, Finance, CCW, UNL)", C_NAVY),
        ("Stage 2\nText Cleaning", "data_cleaning.py\n\n• Acronym-safe regex\n• Clitic/slang expansion\n• Protects 'ill', 's, & CAR hyphens", C_ROYAL),
        ("Stage 3\nCAR Morphology", "car_morphology.py\n\n• 265+ stopwords\n• Guarded EN/FIL/CAR lemmatizer\n• Unigrams + Bigrams", C_TEAL),
        ("Stage 4\nML + Hybrid Core", "train_and_evaluate.py\n\n• 5-Fold CV NB/LR/SVM\n• 156-entry Lexicon\n• OOD Confidence Gate", C_NAVY),
        ("Stage 5\nHardened Portal", "build_portal.py\n\n• Single-source HTML\n• Zero .innerHTML XSS\n• Python↔Node parity", C_ROYAL),
    ]
    for idx, (st_hdr, st_body, col) in enumerate(stages):
        sx = 20 + idx * 138
        b.rect("S04", sx, 78, 126, 224, C_WHITE, outline_hex="#CBD5E1")
        b.textbox("S04", st_hdr, sx, 78, 126, 40, font_size=10, bold=True, color=C_WHITE, bg_hex=col, align="center", valign="MIDDLE")
        b.textbox("S04", st_body, sx + 4, 124, 118, 172, font_size=8.8, color=C_TEXT, line_spacing=125)
        if idx < 4:
            b.arrow("S04", sx + 127, 186, 8)
    b.textbox(
        "S04",
        "Zero External ML Dependencies: Pure Python 3.14 stdlib + serialized JSON model weights (models/intent_classifier.json) executed identically in Python CLI and browser JS — verified by 21 automated unit, classifier, parity, and security tests.",
        20, 316, 680, 56, font_size=10, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE"
    )

    # ==================== SLIDE 5: CORPUS SCALING CHART ====================
    b.add_slide("S05", C_BG_LIGHT, SPEAKER_NOTES[5])
    b.header_chrome("S05", 5, "Corpus Construction & Scaling (Midterm → Finals)", "10.4× corpus growth with balanced 10-intent coverage and transparent provenance", "Speaker 2: Keith Hernandez (1:15)")
    b.image("S05", os.path.join(CHARTS_DIR, "02_corpus_scaling_registers.png"), 20, 70, 498, 280)
    b.card(
        "S05", 528, 70, 172, 280,
        "Verified Coverage Gains",
        "• Added 20 new SLU policies filling Midterm gaps:\n  - Finance & Payment Channels\n  - Entrance & Academic Scholarships\n  - CCW Counseling & Mental Health\n  - UNL Vath Library & Lab Safety\n\n"
        "• Provenance Tags:\n  - 32 Official SLU Policies\n  - 8 Authentic Midterm Queries\n  - 210 Curated EN/TL/CAR Queries",
        header_bg=C_NAVY, body_size=8.8, line_spacing=122
    )
    b.textbox("S05", "Every operational intent now has ≥ 3 authoritative policy documents and exactly 25 annotated documents.", 20, 355, 680, 24, font_size=9.5, bold=True, color=C_ROYAL, align="center", valign="MIDDLE")

    # ==================== SLIDE 6: DATA AUDIT & REPRODUCIBILITY ====================
    b.add_slide("S06", C_BG_LIGHT, SPEAKER_NOTES[6])
    b.header_chrome("S06", 6, "End-to-End Audit & Single-Source Reproducibility", "Six real discrepancies detected and resolved across local files and Google Drive", "Speaker 2: Keith Hernandez (1:00)")
    b.table("S06", "TBL_AUDIT", 24, 72, 672, 248, [
        ["Audit Finding", "Legacy State (Before)", "Verified Fix (After)", "Affected Artifacts"],
        ["Unique Stems & TTR", "352 stems (TTR 0.5641)", "426 unique stems (TTR 0.6827)", "Paper, Script, HTML"],
        ["BoW Rank #4 & #19", "semester=9; year missing", "semester=8 (1.28%); year=4 (#19)", "Sheet, Paper, CSV, HTML"],
        ["Google Sheet Data", "Old Prelim (like=12, campu=4)", "Midterm Top 30 + Finals Tab 2", "Google Sheet (2 Tabs)"],
        ["Recurring Bigrams", "bonifacio campus=2, min grade=2", "19 true bigrams (freq ≥ 2 only)", "HTML Portal, Paper"],
        ["Doc #6 Freedom Wall ID", "Mismatched #25582", "Unified to raw #25604 everywhere", "CSV, JSON, Engine, Paper"],
        ["Stage 2/3 Repro Drift", "niyo/??/haha diffs; no guards", "0-diff repro via scripts/build_all.py", "Drive & Local Scripts"],
    ], font_size=8.8)
    b.textbox("S06", "Verification Gate: tests/test_pipeline.py re-runs cleaning & preprocessing from data/raw_midterm/ into a temp folder and asserts 0 diffs.", 24, 332, 672, 40, font_size=10, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE")

    # ==================== SLIDE 7: STAGE 2 TEXT CLEANING ====================
    b.add_slide("S07", C_BG_LIGHT, SPEAKER_NOTES[7])
    b.header_chrome("S07", 7, "Stage 2: Hardened Acronym-Safe Text Cleaning", "Preserving institutional acronyms while fixing real-world contraction & punctuation bugs", "Speaker 3: Earold Delin (1:15)")
    b.table("S07", "TBL_CLEAN", 24, 72, 672, 246, [
        ["Normalization Rule", "Raw Student / Policy Input", "Hardened Output (data_cleaning.py)"],
        ["Acronym-Safe Metadata", "[#SLUFreedomWall25604] (Submitted: ...) (SAMCIS) (TOR)", "samcis tor (timestamps removed; acronyms intact)"],
        ["Context-Aware 'ill'", "I am feeling ill today / ill still answer", "i am feeling ill today / i will still answer"],
        ["Possessive 's Strip", "SLU's Registrar's Office (URO)", "slu registrar office uro (no bogus 'is')"],
        ["Taglish Clitics & Slang", "Gusto niyo ng dp? Ngaun? likeeee hahahahahaahhhahaha", "gusto ninyo ng downpayment? ngayon? like haha"],
        ["Punctuation Polarity", "reused pipette tips?? have some shame!!", "reused pipette tips? have some shame!"],
        ["CAR Hyphen Retention", "Kankanaey dap-ay and man-obla rules", "kankanaey dap-ay and man-obla rules"],
    ], font_size=8.8)
    b.textbox("S07", "Midterm Reproducibility Preserved: All 24 raw lines in data/raw_midterm/ reproduce outputs/cleaned_corpus.txt with 0 line diffs.", 24, 330, 672, 42, font_size=10, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE")

    # ==================== SLIDE 8: STAGE 3 CAR MORPHOLOGY ====================
    b.add_slide("S08", C_BG_LIGHT, SPEAKER_NOTES[8])
    b.header_chrome("S08", 8, "Stage 3: Guarded Bilingual & CAR Morphological Analysis", "Zero English root corruption alongside Austronesian affix normalization (car_morphology.py)", "Speaker 3: Earold Delin (1:15)")
    b.card(
        "S08", 24, 72, 326, 298,
        "Eliminating Over-Stemming Failures",
        "Naive Affix Stripping (Prelim Errors):\n"
        "• management → nage   |   campus → campu\n"
        "• department → depart  |   during → dur\n\n"
        "Unguarded 'mag-' Prefix Bug (Midterm Audit):\n"
        "• magnify → nify       |   magician → ician\n"
        "• magical → ical       |   maganda → anda\n"
        "• magnesium → nesium   |   paginated → inated\n\n"
        "Hardened Protection (car_morphology.py):\n"
        "• Curated PREFIX_EXCEPTIONS + English suffix hints (-tion, -ment, -ify, -ical, -ician, -ium) block false stripping.\n"
        "• Standalone 'mag' added to QUERY_STOPWORDS.",
        header_bg=C_RED_FG, body_size=9.5, line_spacing=122
    )
    b.card(
        "S08", 370, 72, 326, 298,
        "Productive Philippine & CAR Affix Normalization",
        "Filipino / Taglish Verbal & Infix Roots:\n"
        "• magtanong / tinanong → tanong   |   nagbayad → bayad\n"
        "• tumataas → taas  |  tumawid / tatawid → tawid\n"
        "• sumulat → sulat  |  bumagsak → bagsak\n\n"
        "Ilocano (ilo) Prefixes (ag-, panag-, na-, agpa-):\n"
        "• agadal / panagadal → adal   |   agsurat → surat\n"
        "• agbayad → bayad  |  agpaagas → agas  |  naimbag → imbag\n\n"
        "Northern Kankanaey (kne) & Ibaloi (ibl):\n"
        "• man-obla / men-obla → obla  |  man-adal → adal\n"
        "• menbayad → bayad  |  mapteng → peteng\n"
        "• man-obda → obda   |  mankalkali → kali",
        header_bg=C_TEAL, body_size=9.5, line_spacing=122
    )

    # ==================== SLIDE 9: BOW & BIGRAMS CHART ====================
    b.add_slide("S09", C_BG_LIGHT, SPEAKER_NOTES[9])
    b.header_chrome("S09", 9, "Verified Midterm Lexical Profiling: BoW & Bigrams", "624 filtered tokens • 426 unique stems (TTR = 0.6827) • 19 recurring bigrams (freq = 2)", "Speaker 3: Earold Delin (1:00)")
    b.image("S09", os.path.join(CHARTS_DIR, "01_midterm_bow_top15.png"), 20, 70, 488, 274)
    b.card(
        "S09", 518, 70, 182, 274,
        "Top Verified Bigrams (n=2)",
        "All 19 recurring bigrams (freq=2) verified in preprocessed_tokens.json:\n\n"
        "• official transcript\n"
        "• transcript records\n"
        "• records tor\n"
        "• qualifying examination\n"
        "• examination permit\n"
        "• failure due / due absence\n"
        "• student portal / slu student\n"
        "• academic department\n"
        "• degree program\n"
        "• mid semester / semester taas\n"
        "• request official",
        header_bg=C_ROYAL, body_size=8.8, line_spacing=120
    )
    b.textbox("S09", "Synced identically across corpus_bow_summary.csv, Google Sheet Tab 1, HTML Portal, and Research Paper.", 20, 352, 680, 24, font_size=9.5, bold=True, color=C_NAVY, align="center", valign="MIDDLE")

    # ==================== SLIDE 10: TRACK A 156-ENTRY CAR LEXICON ====================
    b.add_slide("S10", C_BG_LIGHT, SPEAKER_NOTES[10])
    b.header_chrome("S10", 10, "Track A: 156-Entry Multilingual SLU & CAR Electronic Lexicon", "36 SLU/Taglish • 48 Ilocano (ilo) • 40 Northern Kankanaey (kne) • 32 Ibaloi (ibl)", "Speaker 4: Erick Sibayan (1:30)")
    b.table("S10", "TBL_LEX", 24, 68, 672, 236, [
        ["ID", "Lemma", "ISO", "Root / Affix", "English / Institutional Gloss", "Domain Intent"],
        ["SLU-001", "samcis", "en-SLU", "samcis (Acronym)", "School of Accountancy, Mgmt., Computing & Info Studies", "SHIFTING_TRANSFER"],
        ["SLU-011", "ccw", "en-SLU", "ccw (Acronym)", "Center for Counseling & Wellness (Mental Health)", "HEALTH_SAFETY"],
        ["ILO-008", "agadal", "ilo", "adal (ag-)", "To study; pursue university coursework (Ilocano)", "ENROLLMENT_PORTAL"],
        ["ILO-037", "danum", "ilo", "danum (Root)", "Water — Ilocano cognate (vs. kne danom / ibl shanom)", "FACILITIES_LAB"],
        ["KNE-002", "inayan", "kne", "inayan (Root)", "Cordilleran ethical restraint vs. academic dishonesty", "EXAM_INTEGRITY"],
        ["KNE-022", "danom", "kne", "danom (Root)", "Water — Northern Kankanaey campus utility cognate", "FACILITIES_LAB"],
        ["IBL-002", "tongtong", "ibl", "tongtong (Root)", "Customary dispute mediation & disciplinary council", "EXAM_INTEGRITY"],
        ["IBL-007", "shanom", "ibl", "shanom (Root)", "Water — Ibaloi postalveolar sh- reflex cognate", "FACILITIES_LAB"],
    ], font_size=8.4, col_widths=[56, 62, 46, 98, 286, 124])
    b.textbox(
        "S10",
        "Linguistic Grounding: Constantino (1971), Rubino (2000), Vanoverbergh (1933), Ballard (2011), & SIL Philippines.\n"
        "Engineering Safeguard: Strict separation of Native_Aliases vs. Semantic_Aliases guarantees 0.0% false-positive CAR language tagging.",
        24, 326, 672, 48, font_size=9.5, bold=True, color=C_NAVY, bg_hex=C_GOLD_LIGHT, align="center", valign="MIDDLE"
    )

    # ==================== SLIDE 11: MULTI-LAYER ANNOTATION SCHEMA ====================
    b.add_slide("S11", C_BG_LIGHT, SPEAKER_NOTES[11])
    b.header_chrome("S11", 11, "Multi-Layer Corpus Annotation & 10 Balanced Intents", "250 annotated documents (25 per class) enabling statistically valid Stratified 5-Fold CV", "Speaker 4: Erick Sibayan (1:00)")
    b.card("S11", 24, 66, 212, 106, "Layer 1 • Intent Class", "10 balanced SLU domains\nExactly 25 docs / class\nEvery class has ≥ 3 official verified SLU policies.", header_bg=C_NAVY, body_size=9.2, line_spacing=122, header_h=24, title_size=10.5)
    b.card("S11", 254, 66, 212, 106, "Layer 2 • Register & Sentiment", "101 EN (40.4%) • 79 TL-EN (31.6%)\n70 CAR-TL-EN (28.0%)\nPolarity: Policy, Inquiry, Urgent", header_bg=C_ROYAL, body_size=9.2, line_spacing=122, header_h=24, title_size=10.5)
    b.card("S11", 484, 66, 212, 106, "Layer 3 • Provenance", "Explicit Source_Type tag:\n• 32 OFFICIAL_SLU_POLICY\n• 8 HARVESTED / URO_Q\n• 210 CURATED_MULTILINGUAL", header_bg=C_TEAL, body_size=9.2, line_spacing=122, header_h=24, title_size=10.5)

    b.table("S11", "TBL_INTENTS", 24, 182, 672, 186, [
        ["Operational Intent Class", "Docs", "Pol", "Operational Intent Class", "Docs", "Pol"],
        ["URO_ENROLLMENT_TOR (TOR/COG/CGMC)", "25", "3", "EXAM_PERMIT_INTEGRITY (RFID/Cheating)", "25", "3"],
        ["URO_ENROLLMENT_PORTAL (iSLU/Advising)", "25", "3", "CAMPUS_DECORUM_DRESSCODE (Uniform/Wash)", "25", "3"],
        ["URO_SUBJECT_ADJUSTMENT (Add/Drop/WP)", "25", "3", "CAMPUS_HEALTH_SAFETY (Clinic/CCW/DPA)", "25", "4"],
        ["ACADEMIC_SHIFTING_TRANSFER (Shift/QE)", "25", "4", "TUITION_FINANCE (Banks/Scholarships)", "25", "3"],
        ["HANDBOOK_GRADING_FDA (75%/FDA/INC)", "25", "3", "CAMPUS_FACILITIES_LAB (UNL/Labs/IT)", "25", "3"],
    ], font_size=8.3, col_widths=[256, 40, 40, 256, 40, 40])

    # ==================== SLIDE 12: SUPERVISED 5-FOLD CV BENCHMARKS ====================
    b.add_slide("S12", C_BG_LIGHT, SPEAKER_NOTES[12])
    b.header_chrome("S12", 12, "Supervised Intent Classification (Stratified 5-Fold CV)", "Leak-free fold-local TF-IDF benchmarking of NB, Logistic Regression & Linear SVM", "Speaker 4: Erick Sibayan (1:30)")
    b.image("S12", os.path.join(CHARTS_DIR, "03_cv_model_comparison.png"), 20, 72, 334, 188)
    b.image("S12", os.path.join(CHARTS_DIR, "04_confusion_matrix.png"), 366, 72, 334, 188)
    b.stat_card("S12", 20, 274, 218, 96, "95.61%", "Multinomial NB [BEST]\n95.60% Acc • ±1.47% F1", bg=C_NAVY)
    b.stat_card("S12", 251, 274, 218, 96, "95.18%", "Logistic Regression (L2)\n95.20% Acc • ±0.90% Std", bg=C_ROYAL)
    b.stat_card("S12", 482, 274, 218, 96, "93.97%", "Linear SVM (OvR Hinge)\n94.00% Acc • 239/250 NB Hits", bg=C_TEAL)

    # ==================== SLIDE 13: HYBRID RETRIEVAL & TDD HARDENING ====================
    b.add_slide("S13", C_BG_LIGHT, SPEAKER_NOTES[13])
    b.header_chrome("S13", 13, "Hybrid Retrieval Architecture & TDD Bug Hardening", "Turning 11 failing regression tests green with calibrated scoring and OOD safety", "Speaker 5: John Andrew Angcaway (1:15)")
    b.textbox(
        "S13",
        "Hybrid Policy Score(q, d) = Cosine_TFIDF(q_exp, d) + α_eff · I(d.intent ∈ LexIntents) + β · P_NB(d.intent | q) + γ_auth",
        24, 70, 672, 36, font_size=11.5, bold=True, color=C_WHITE, bg_hex=C_NAVY, align="center", valign="MIDDLE"
    )
    b.card(
        "S13", 24, 118, 326, 120,
        "1. Native-Only CAR Greeting Separation",
        "• Bug: English 'plagiarism' / 'disciplinary' falsely triggered Kankanaey & Ibaloi greetings.\n"
        "• Fix: Separated Native_Aliases from Semantic_Aliases — regional greetings fire strictly on genuine CAR tokens.",
        header_bg=C_ROYAL, body_size=9.5
    )
    b.card(
        "S13", 370, 118, 326, 120,
        "2. Calibrated OOD Gate & Greeting Handler",
        "• Bug: Gibberish & 'hello' silently returned Freedom Wall Doc #1/#8 as 'official SLU regulations'.\n"
        "• Fix: Dedicated greeting handler + minimum confidence gate redirecting cleanly to URO, OSAS, Finance, & Clinic.",
        header_bg=C_TEAL, body_size=9.5
    )
    b.card(
        "S13", 24, 248, 326, 124,
        "3. Numeric Anchors & Synonym Precision",
        "• Preserves policy numbers (grades 50–99, 20% FDA, RA 10173): 'What if I get 74?' now hits the 75% passing rule.\n"
        "• Added cyberbullying/libel/privacy mappings → RA 10173.\n"
        "• Decoupled shifting synonyms from add/drop forms.",
        header_bg=C_NAVY, body_size=9.5
    )
    b.card(
        "S13", 370, 248, 326, 124,
        "4. Holistic ML Moderation (α_eff = 0.14)",
        "• Single-keyword lexicon rules over-boost secondary mentions (e.g., 'tuition' inside an RFID validation question).\n"
        "• Letting holistic Multinomial NB lead (β = 0.30) resolves multi-entity collisions cleanly across all 10 intents.",
        header_bg=C_ROYAL, body_size=9.5
    )

    # ==================== SLIDE 14: 4-STAGE ABLATION STUDY ====================
    b.add_slide("S14", C_BG_LIGHT, SPEAKER_NOTES[14])
    b.header_chrome("S14", 14, "4-Stage Held-Out Retrieval Ablation (48 Unseen Queries)", "Zero train/test text overlap • Quantifying each NLP layer's exact empirical contribution", "Speaker 5: John Andrew Angcaway (1:15)")
    b.image("S14", os.path.join(CHARTS_DIR, "05_retrieval_ablation.png"), 20, 70, 488, 274)
    b.card(
        "S14", 518, 70, 182, 274,
        "Key Empirical Insights",
        "• Cleaning + CAR Morph (B):\n  +9.6 pts Top-1 (83.3→92.9%)\n  MRR 0.893 → 0.960\n\n"
        "• Lexicon + OOD Gate (C):\n  OOD Reject jumps 0→100%\n  Exposes keyword collision dip (90.5%)\n\n"
        "• Full Hybrid + NB (D) [BEST]:\n  95.2% Top-1 (40/42)\n  97.6% Top-3 • 0.9643 MRR\n  100% OOD • 0.0% FP-CAR",
        header_bg=C_NAVY, body_size=8.9, line_spacing=122
    )
    b.textbox("S14", "By Register (Full Hybrid): EN 91.7% Top-1  •  Taglish (TL-EN) 100.0% Top-1  •  Cordilleran (CAR-TL-EN) 95.0% Top-1", 20, 352, 680, 24, font_size=9.5, bold=True, color=C_GREEN_FG, bg_hex=C_GREEN_BG, align="center", valign="MIDDLE")

    # ==================== SLIDE 15: SECURITY, PARITY & WCAG UI ====================
    b.add_slide("S15", C_BG_LIGHT, SPEAKER_NOTES[15])
    b.header_chrome("S15", 15, "Security Hardening, Cross-Runtime Parity & Accessible UI", "Engineering production reliability across Python CLI, browser JS, and static hosting", "Speaker 5: John Andrew Angcaway (1:00)")
    b.card(
        "S15", 24, 74, 212, 294,
        "Security & XSS Defense",
        "• Eliminated 100% of .innerHTML assignments across the entire portal.\n\n"
        "• All user queries, tokens, & tables built via safe DOM nodes & textContent.\n\n"
        "• Tested live with <img src=x onerror=alert(1)> payload.\n\n"
        "• Strict CSP <meta> + dist/netlify.toml headers (X-Frame-Options, nosniff, Referrer-Policy) + 400-char input cap.",
        header_bg=C_RED_FG, body_size=9.4, line_spacing=124
    )
    b.card(
        "S15", 254, 74, 212, 294,
        "Zero-Drift Python↔JS Parity",
        "• Single-source scripts/build_portal.py compiles policies, 156 lexicon entries, Midterm BoW/bigrams, & NB weights into HTML.\n\n"
        "• Automated Node.js test executes the HTML's exact JS engine against Python.\n\n"
        "• Verified 100% identical outputs across 51 queries (48 held-out + XSS + CAR hyphens + illness).",
        header_bg=C_NAVY, body_size=9.4, line_spacing=124
    )
    b.card(
        "S15", 484, 74, 212, 294,
        "WCAG 2.1 AA 4-Tab Portal",
        "• Authentic SLU Navy/Gold palette with ≥ 4.5:1 contrast.\n\n"
        "• Accessible ARIA tablist, ArrowLeft/Right/Home/End keyboard navigation, skip link, & aria-live chat log.\n\n"
        "• 4 Interactive Tabs:\n  1. Chatbot & 6-Stage Trace\n  2. 156-Entry CAR Lexicon\n  3. Corpus & BoW Analytics\n  4. 5-Fold CV & Ablation",
        header_bg=C_TEAL, body_size=9.4, line_spacing=124
    )

    # ==================== SLIDE 16: LIVE MULTILINGUAL WALKTHROUGH ====================
    b.add_slide("S16", C_BG_LIGHT, SPEAKER_NOTES[16])
    b.header_chrome("S16", 16, "Live Portal Walkthrough: Four Multilingual Query Traces", "Real end-to-end outputs verified identically in Python CLI and browser portal", "Speaker 1: Chaze Rodriguez (1:30)")
    b.card(
        "S16", 24, 72, 326, 142,
        "Case 1 • Taglish Shifting (TL-EN)",
        "Query: \"Paano po process ng shifting from SAMCIS to SEAIT? May QE ba?\"\n"
        "• Intent: ACADEMIC_SHIFTING_TRANSFER (NB + Lexicon)\n"
        "• Lexicon: SLU-001 (samcis), SLU-002 (seait), SLU-018 (qe)\n"
        "• Policy: Internal Shifting + URO QE & Dean Approval (slu.edu.ph)",
        header_bg=C_NAVY, body_size=9.2, line_spacing=122
    )
    b.card(
        "S16", 370, 72, 326, 142,
        "Case 2 • Ilocano Attendance Query (CAR-TL-EN)",
        "Query: \"Naimbag a bigat! Agadal ak idiay SAMCIS—mano absent sakbay ma-FDA?\"\n"
        "• Greeting: Naimbag a bigat/aldaw! (Native Ilocano recognized)\n"
        "• Intent: HANDBOOK_GRADING_FDA (Score: 0.72)\n"
        "• Policy: Handbook Art. I, Sec. 2 (>20% unexcused → FDA)",
        header_bg=C_ROYAL, body_size=9.2, line_spacing=122
    )
    b.card(
        "S16", 24, 226, 326, 146,
        "Case 3 • Northern Kankanaey Integrity (CAR-TL-EN)",
        "Query: \"Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?\"\n"
        "• Greeting: Gawis ay agew! (Native Kankanaey recognized)\n"
        "• Intent: EXAM_PERMIT_INTEGRITY • Lexicon: KNE-001, KNE-002\n"
        "• Policy: Handbook Art. II, Sec. 4 (SLU Disciplinary Board)",
        header_bg=C_TEAL, body_size=9.2, line_spacing=122
    )
    b.card(
        "S16", 370, 226, 326, 146,
        "Case 4 • Out-of-Domain Safety Gate (OOD Trap)",
        "Query: \"What is the best recipe for Baguio strawberry sinigang?\"\n"
        "• Intent: OUT_OF_DOMAIN  |  Confidence below 0.14 threshold\n"
        "• Safeguard: Zero hallucination — never returns personal posts.\n"
        "• Response: Honest fallback guiding student to URO/OSAS/Finance/Clinic",
        header_bg="#B45309", body_size=9.2, line_spacing=122
    )

    # ==================== SLIDE 17: LIMITATIONS, PRIVACY & ROADMAP ====================
    b.add_slide("S17", C_BG_LIGHT, SPEAKER_NOTES[17])
    b.header_chrome("S17", 17, "Honest Limitations, RA 10173 Privacy & Future Roadmap", "Transparent academic reflection for campus-wide deployment and Cordilleran NLP", "Speaker 1: Chaze Rodriguez (1:00)")
    b.card(
        "S17", 24, 74, 212, 294,
        "Provenance & Linguistic QA",
        "• 210 expanded multilingual training utterances are transparently tagged as CURATED_MULTILINGUAL_INQUIRY.\n\n"
        "• Next Step: Formal community validation with native Ilocano, Northern Kankanaey, & Ibaloi linguists and anonymized live campus logs.\n\n"
        "• Expand to Ibaloi/Kankanaey multi-word idioms & Bontok/Ifugao.",
        header_bg=C_NAVY, body_size=9.4, line_spacing=125
    )
    b.card(
        "S17", 254, 74, 212, 294,
        "Data Privacy (RA 10173)",
        "• Public Freedom Wall harvesting stores zero student names, IDs, or private contact metadata.\n\n"
        "• 100% client-side browser inference ensures student questions never leave the user's device.\n\n"
        "• Static hosting (dist/netlify.toml) eliminates server-side credential or database breach surface.",
        header_bg=C_ROYAL, body_size=9.4, line_spacing=125
    )
    b.card(
        "S17", 484, 74, 212, 294,
        "Next-Gen NLP Architecture",
        "• Benchmark compact multilingual sentence embeddings (e.g., mE5 / LaBSE) alongside our fast NB+TF-IDF baseline.\n\n"
        "• Add strict policy-grounded RAG summarization with verbatim handbook citations.\n\n"
        "• Integrate live iSLU calendar sync & official URO/OSAS ticketing.",
        header_bg=C_TEAL, body_size=9.4, line_spacing=125
    )

    # ==================== SLIDE 18: CONCLUSION & Q&A (DARK NAVY) ====================
    b.add_slide("S18", C_NAVY, SPEAKER_NOTES[18])
    b.rect("S18", 0, 0, 720, 8, C_GOLD)
    b.rect("S18", 0, 397, 720, 8, C_GOLD)
    b.textbox("S18", "Impact Summary & Open Q&A", 40, 26, 640, 40, font_size=28, bold=True, color=C_WHITE, align="center")
    b.textbox("S18", "Group 2 – AiNomally • Reproducible, Audited & Hardened Multilingual eGovernance NLP for SLU Baguio", 40, 68, 640, 24, font_size=11.5, color=C_ICE, align="center")

    b.stat_card("S18", 28, 114, 155, 108, "250 / 32", "Balanced Corpus Docs\n& Official SLU Policies", bg=C_ROYAL)
    b.stat_card("S18", 198, 114, 155, 108, "156", "Verified SLU + CAR\nElectronic Lexicon", bg=C_ROYAL)
    b.stat_card("S18", 368, 114, 155, 108, "95.61%", "Stratified 5-Fold CV\nMacro F1 (Naive Bayes)", bg=C_ROYAL)
    b.stat_card("S18", 538, 114, 155, 108, "95.2%", "Unseen Top-1 Policy Acc\n100% OOD • 0% FP-CAR", bg=C_ROYAL)

    b.textbox(
        "S18",
        "All Deliverables Verified & Synced:  One-command build (python3 scripts/build_all.py)  •  21/21 Automated Tests Passing\n"
        "Google Drive Paper, Scripts & 2-Tab Sheet Synced  •  Hardened 4-Tab Web Portal Ready (dist/index.html)",
        35, 246, 650, 48, font_size=10.5, color=C_WHITE, align="center", line_spacing=135
    )
    b.rect("S18", 240, 304, 240, 3, C_GOLD)
    b.textbox("S18", "Agyamanak!  •  Iyaman!  •  Dakel a Iyaman!  •  Thank You!", 40, 318, 640, 28, font_size=16, bold=True, color=C_GOLD_BRIGHT, align="center")
    b.textbox("S18", "We welcome your questions and live portal demo requests.", 40, 350, 640, 22, font_size=11, color=C_ICE, align="center")


def export_speaker_script_md():
    os.makedirs(PRES_DIR, exist_ok=True)
    lines = [
        "# Group 2 – AiNomally | CSE 30 Complete Project Presentation Script (15–20 Minutes)",
        "",
        "**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  ",
        "**Institution:** Saint Louis University (SAMCIS – Department of Computer Science), Baguio City  ",
        "**Instructor:** Prof. Dalos D. Miguel  ",
        "**Total Target Delivery Time:** ~18.5 minutes + Q&A (18 slides, evenly balanced across all 5 members ~3.5 min each)",
        "",
        "| Speaker | Slides Covered | Target Time |",
        "|---|---|---|",
        "| **Chaze Ezkys M. Rodriguez** | Slides 1–3, 16–18 | ~6:15 (Intro + Demo/Close) |",
        "| **Keith Russel Hernandez** | Slides 4–6 | ~3:30 |",
        "| **Earold Jan Delin** | Slides 7–9 | ~3:30 |",
        "| **Erick James Sibayan** | Slides 10–12 | ~4:00 |",
        "| **John Andrew Angcaway** | Slides 13–15 | ~3:30 |",
        "",
        "---",
        "",
    ]
    total_words = 0
    for s_num in range(1, 19):
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
    print(f"[OK] Synced 18-slide speaker script to Drive Doc {SCRIPT_DOC_ID}")


def main():
    parser = argparse.ArgumentParser(description="Build Group 2 AiNomally 18-slide CSE 30 deck.")
    parser.add_argument("--pptx-only", action="store_true", help="Only regenerate local .pptx and speaker_script_15_20min.md without creating a new Google Slides deck.")
    parser.add_argument("--sync-script-doc", action="store_true", help="Also sync speaker script to Google Drive Doc when using --pptx-only.")
    args = parser.parse_args()

    os.makedirs(PRES_DIR, exist_ok=True)
    builder = DualDeckBuilder()
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

    # 3. Create live Google Slides presentation via gslides CLI
    create_res = subprocess.run(
        ["gslides", "mutate", "create", "--title", "CSE 30 Final Presentation — SLU eGovernance Multilingual Chatbot & CAR Lexicon (Group 2 AiNomally)"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(create_res.stdout.strip())
    m_id = re.search(r"presentation/d/([A-Za-z0-9_-]+)|ID:\s*([A-Za-z0-9_-]+)", create_res.stdout)
    if not m_id:
        raise RuntimeError(f"Could not parse presentation ID from: {create_res.stdout}")
    pres_id = m_id.group(1) or m_id.group(2)
    print(f"[OK] Created Google Slides Deck ID: {pres_id}")

    # 4. Execute single-batch layout + tables + speaker notes
    batch_path = os.path.join(SCRATCH, "slides_batch.json")
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(builder.ops, f, ensure_ascii=False, indent=2)

    batch_res = subprocess.run(
        ["gslides", "mutate", "batch", pres_id, "-f", batch_path, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    batch_json = json.loads(batch_res.stdout)
    resolved = batch_json.get("resolved_ids", {})
    resolved["p"] = "p"
    print(f"[OK] Batch built {len(builder.slide_order)} slides ({batch_json.get('api_requests')} API requests)")

    # 5. Insert high-DPI PNG charts onto their exact target slides
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
    meta_path = os.path.join(SCRATCH, "slides_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[OK] Saved deck metadata -> {meta_path}")
    print(f"[URL] {meta['url']}")


if __name__ == "__main__":
    main()
