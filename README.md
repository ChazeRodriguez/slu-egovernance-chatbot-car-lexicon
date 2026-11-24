# SLU eGovernance Multilingual Chatbot & CAR Electronic Lexicon

**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  
**Institution:** Department of Computer Science (SAMCIS), Saint Louis University, Baguio City  
**Group:** Group 2 – AiNomally (John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, Chaze Ezkys M. Rodriguez, Erick James Sibayan)  
**Instructor:** Prof. Dalos D. Miguel

---

## One-Command Reproducible Build

Every local deliverable (Midterm CSV/JSON baseline, Expanded SLU Policies, 156-entry SLU+CAR Electronic Lexicon, 250-doc balanced corpus, Stratified 5-Fold CV supervised ML models, high-DPI charts, hardened 4-tab web portal, and `dist/` deploy bundle) is generated deterministically with zero external ML dependencies:

```bash
python3 scripts/build_all.py
```

---

## Repository Structure

| Path | Description |
|---|---|
| `data/raw_midterm/` | Exact 4 original Drive raw `.txt` files (`#SLUFreedomWall`, URO FAQs, SLU Handbook, Safety Guide) |
| `data/expanded/` | 32 verified SLU official policy provisions, 156-entry SLU+CAR lexicon (`en-SLU`, `tl-SLU`, `ilo`, `kne`, `ibl`), 250-doc balanced annotated corpus (`25`/intent), and 48 strictly held-out unseen queries |
| `scripts/slu_web_scraper.py` | Stage 1 `#SLUFreedomWall` & static SLU page parser |
| `scripts/data_cleaning.py` | Stage 2 deterministic acronym-safe text cleaner (fixes `"ill"`, possessive `'s`, `niyo`, `??`, laughter) |
| `scripts/data_preprocessing.py` | Stage 3 tokenizer, 265-word stopwords, guarded lemmatizer, Top 30 BoW (`semester=8`), 19 bigrams |
| `scripts/car_morphology.py` | Guarded English, Filipino & CAR (`ilo`, `kne`, `ibl`) morphological analyzer |
| `scripts/train_and_evaluate.py` | Pure-Python Multinomial NB, L2 Logistic Regression, One-vs-Rest Linear SVM + leak-free Stratified 5-Fold CV + 4-stage held-out ablation study |
| `scripts/build_portal.py` | Single-source builder injecting verified data + serialized NB weights into `slu_egovernance_chatbot_ui.html` and `dist/` |
| `scripts/generate_charts.py` | High-DPI Pillow chart generator (`charts/*.png`) |
| `slu_chatbot_engine.py` | Hardened CLI & hybrid TF-IDF + Lexicon + Supervised ML chatbot engine (`--dataset auto\|midterm\|expanded`, `--query`, `--evaluate`, `--interactive`) |
| `slu_egovernance_chatbot_ui.html` | Hardened, XSS-free, WCAG 2.1 AA 4-tab interactive web portal |
| `dist/` | Static deployment bundle (`index.html` + `netlify.toml` security headers) |
| `tests/` | Automated unit, regression, classifier, Python↔Node.js parity, and XSS security tests (`21` tests) |
| `scripts/build_presentation.py` | Dual builder for the 18-slide Google Slides deck, local `.pptx`, and timed 5-speaker script (`--pptx-only`) |
| `presentation/` | Local PowerPoint (`Group2_AiNomally_CSE30_Deck.pptx`) + timed 15–20 min 5-speaker script (`speaker_script_15_20min.md`) |

---

## Verified Benchmark Highlights

- **Midterm Baseline Reproducibility:** `24` docs · `624` filtered tokens · `457` unique surface tokens · `426` unique stems · `19` recurring bigrams · Doc #6 unified to `#25604` · `100.0%` Top-1 / `1.0000` MRR on 8-query Midterm benchmark.
- **Stratified 5-Fold Cross-Validation (250 balanced multilingual docs, 10 intents, fold-local TF-IDF):**
  - **Multinomial Naive Bayes (★ Best):** `95.60%` Accuracy · `95.69%` Macro Precision · `95.60%` Macro Recall · **`95.61%` Macro F1 (±1.47%)**
  - **Logistic Regression (L2 Softmax):** `95.20%` Accuracy · `95.18%` Macro F1 (±0.90%)
  - **Linear SVM (One-vs-Rest Hinge):** `94.00%` Accuracy · `93.97%` Macro F1 (±2.60%)
- **4-Stage Held-Out Retrieval Ablation (48 strictly unseen queries, 0 train/test leakage):**
  - Raw TF-IDF Only: `83.3%` Top-1 · `0.8929` MRR · `0.0%` OOD Rejection
  - + Acronym-Safe Cleaning & CAR Morphology: `92.9%` Top-1 · `0.9603` MRR · `0.0%` OOD Rejection
  - + 156-Entry Lexicon & OOD Gate: `90.5%` Top-1 · `0.9167` MRR · `100.0%` OOD Rejection
  - **Full Hybrid (+ Trained NB Intent + OOD Gate):** **`95.2%` Top-1 · `97.6%` Top-3 · `0.9643` MRR · `100.0%` OOD Rejection · `0.0%` False-Positive CAR Rate**

---

## Quick CLI Usage

```bash
# Run a single multilingual query (expanded Finals knowledge base + ML classifier)
python3 slu_chatbot_engine.py --query "Naimbag a bigat! Agadal ak idiay SAMCIS, mano absent sakbay ma-FDA?"

# Interactive CLI chat
python3 slu_chatbot_engine.py --interactive

# Run complete test suite (Python + Node.js JS parity + XSS checks)
python3 -m unittest discover -s tests -v
```
