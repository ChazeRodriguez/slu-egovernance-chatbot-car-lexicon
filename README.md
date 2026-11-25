# SLU eGovernance Multilingual Chatbot & CAR Electronic Lexicon

**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  
**Institution:** Department of Computer Science (SAMCIS), Saint Louis University, Baguio City  
**Group:** Group 2 – AiNomally (John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, Chaze Ezkys M. Rodriguez, Erick James Sibayan)  
**Instructor:** Prof. Dalos D. Miguel  
**Live Hardened Web Portal:** https://slu-egovernance-chatbot.netlify.app  
**Source Repository:** https://github.com/ChazeRodriguez/slu-egovernance-chatbot-car-lexicon

---

## One-Command Reproducible Build

Every local deliverable (Midterm CSV/JSON baseline, Expanded SLU Policies, 176-entry SLU+CAR Electronic Lexicon, 350-doc balanced corpus, Stratified 5-Fold CV supervised ML models, Canva-palette high-DPI charts, Canva `EAG-QJ6Vos4` 4-tab web portal, and `dist/` deploy bundle) is generated deterministically with zero external ML dependencies:

```bash
python3 scripts/build_all.py
```

---

## Repository Structure

| Path | Description |
|---|---|
| `data/raw_midterm/` | Exact 4 original Drive raw `.txt` files (`#SLUFreedomWall`, URO FAQs, SLU Handbook, Safety Guide) |
| `data/expanded/` | `52` verified SLU official policy provisions (including Latin Honors GWA thresholds `doc_id 133`, Voluntary Dropping `WP/DRP` vs. Permanent `FDA` `doc_id 134`, Promissory Notes, Petition Classes & Honorable Dismissal vs. LOA), `176`-entry SLU+CAR lexicon (`52 ilo`, `48 SLU/Taglish`, `42 kne`, `34 ibl`), `350`-doc balanced annotated corpus (`35`/intent), and `75` strictly held-out unseen queries (`69` in-domain + `6` OOD/greeting traps) |
| `scripts/slu_web_scraper.py` | Stage 1 `#SLUFreedomWall` & static SLU page parser |
| `scripts/data_cleaning.py` | Stage 2 deterministic acronym-safe text cleaner (fixes `"ill"`, possessive `'s`, `niyo`, `??`, laughter) |
| `scripts/data_preprocessing.py` | Stage 3 tokenizer, 265-word stopwords, guarded lemmatizer, Top 30 BoW (`semester=8`), 19 bigrams |
| `scripts/car_morphology.py` | Guarded English, Filipino & CAR (`ilo`, `kne`, `ibl`) morphological analyzer |
| `scripts/train_and_evaluate.py` | Pure-Python Linear SVM, Multinomial NB, L2 Logistic Regression + leak-free Stratified 5-Fold CV + 4-stage held-out ablation study |
| `scripts/build_portal.py` | Single-source builder compiling verified policies, lexicon & serialized ML weights into Canva `EAG-QJ6Vos4` Light Graph-Paper + Dark Neon-Glow `slu_egovernance_chatbot_ui.html` and `dist/` |
| `scripts/generate_charts.py` | High-DPI Pillow chart generator (`charts/*.png` + `charts/tv_*.png`) |
| `slu_chatbot_engine.py` | Hardened CLI & hybrid sublinear TF-IDF + Lexicon + Probabilistic SVM ML + Comparative Synthesis chatbot engine (`--dataset auto\|midterm\|expanded`, `--query`, `--evaluate`, `--interactive`) |
| `slu_egovernance_chatbot_ui.html` | Hardened, XSS-free, WCAG 2.1 AA 4-tab Canva `EAG-QJ6Vos4` interactive web portal |
| `dist/` | Static deployment bundle (`index.html` + `netlify.toml` security headers) |
| `tests/` | Automated unit, regression, classifier, Python↔Node.js parity, and XSS security tests (`22` tests) |
| `scripts/build_presentation.py` | Dual builder for the 22-slide Canva Grid Classroom TV Google Slides deck, local `.pptx`, and timed 5-speaker script (`--pptx-only`) |
| `presentation/` | Local PowerPoint (`Group2_AiNomally_CSE30_Deck.pptx`), timed 15–20 min 5-speaker script (`speaker_script_15_20min.md`), Panel Defense Q&A (`defense_qa_cheatsheet.md`), and portal QR (`portal_qr.png`) |

---

## Verified Benchmark Highlights

- **Midterm Baseline Reproducibility:** `24` docs · `624` filtered tokens · `457` unique surface tokens · `426` unique stems · `19` recurring bigrams · Doc #6 unified to `#25604` · `100.0%` Top-1 / `1.0000` MRR on 8-query Midterm benchmark.
- **Stratified 5-Fold Cross-Validation (`350` balanced multilingual docs, `10` intents, fold-local sublinear TF-IDF):**
  - **Linear SVM (One-vs-Rest Hinge, ★ Best):** **`95.43%` Accuracy** · **`95.66%` Macro Precision** · **`95.43%` Macro Recall** · **`95.43%` Macro F1 (±3.79%)** (`334/350` exact out-of-fold hits)
  - **Multinomial Naive Bayes (Laplace):** `94.86%` Accuracy · `95.22%` Macro Precision · `94.86%` Macro Recall · `94.89%` Macro F1 (±4.22%)
  - **Logistic Regression (L2 Softmax):** `94.86%` Accuracy · `95.13%` Macro Precision · `94.86%` Macro Recall · `94.89%` Macro F1 (±3.67%)
- **4-Stage Held-Out Retrieval Ablation (`75` strictly unseen queries: `69` in-domain + `6` OOD/greeting/trap, 0 train/test leakage):**
  - Stage A — Raw TF-IDF Cosine Only: `84.1%` Top-1 · `98.6%` Top-3 · `0.9082` MRR · `0.0%` OOD Rejection
  - Stage B — + Acronym-Safe Cleaning & CAR Morphology: `87.0%` Top-1 · `100.0%` Top-3 · `0.9324` MRR · `0.0%` OOD Rejection
  - Stage C — + 176-Entry Lexicon & OOD Gate: `88.4%` Top-1 · `95.7%` Top-3 · `0.9203` MRR · `100.0%` OOD Rejection
  - **Stage D — Full Hybrid (+ Probabilistic SVM Intent + OOD Gate):** **`98.6%` (`68/69`) Top-1 · `100.0%` Top-3 · `0.9928` MRR · `100.0%` OOD Rejection · `0.0%` False-Positive CAR Rate** (`100.0%` EN · `100.0%` TL-EN · `96.3%` CAR-TL-EN)

---

## Flagship Niche Policy Queries

- **Latin Honors GWA Cutoffs (`doc_id 133`):** `What are the specific grades you need for Latin honors?` → Summa Cum Laude (`>= 93%`, no grade `< 85%`), Magna Cum Laude (`91.00%–92.99%`, no grade `< 80%`), Cum Laude (`88.00%–90.99%`, no grade `< 78%`), zero failing/dropped marks, and `>= 75%` SLU unit residency.
- **Dropped vs. Permanently Dropped (`doc_id 134`, Comparative Synthesis):** `How many absences do I have before I become dropped vs. permanently dropped?` → Voluntary Official Dropping (`WP`/`DRP` via URO/SAMCIS before final exams, non-failing) vs. Permanent Failure Due to Absences (`FDA`, `> 20%` of `54` semester hours: `11th` absence in MWF / `8th` in TTh, recorded as failing `D`) + `3 consecutive` absences OSAS Readmission Slip rule.

---

## Quick CLI Usage

```bash
# Niche Latin Honors or Attendance policy query
python3 slu_chatbot_engine.py --query "What are the specific grades you need for Latin honors?"
python3 slu_chatbot_engine.py --query "How many absences do I have before I become dropped vs. permanently dropped?"

# Multilingual CAR code-switched query
python3 slu_chatbot_engine.py --query "Naimbag a bigat! Agadal ak idiay SAMCIS, mano absent sakbay ma-FDA?"

# Interactive CLI chat
python3 slu_chatbot_engine.py --interactive

# Run complete test suite (22 tests: Python unit + Node.js Py↔JS parity + XSS checks)
python3 -m unittest discover -s tests -v
```
