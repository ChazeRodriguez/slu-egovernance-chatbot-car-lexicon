# Task Checklist — Group 2 AiNomally CSE 30 Complete Overhaul

## Phase 1: Reproducible Local Repo & Google Drive Sync
- [x] Task 1.0: Initialize git repo, directory layout, and ingest 4 raw Midterm files into `data/raw_midterm/`
- [x] Task 1.1: Build deterministic `scripts/slu_web_scraper.py`, `scripts/data_cleaning.py`, `scripts/data_preprocessing.py` + `tests/test_pipeline.py`
- [x] Task 1.2: Sync Google Sheet (`corpus_bow_summary.csv` Tab 1) and Drive scripts (`slu_web_scraper.py`, `data_cleaning.py`, `data_preprocessing.py`, `cleaned_corpus.txt`)

## Checkpoint 1: Foundation & Midterm Reproducibility
- [x] `python3 -m unittest tests/test_pipeline.py` passes with 0 diffs
- [x] Drive Sheet & scripts verified synced

## Phase 2: Engine & Portal Hardening (TDD + Security + Accessibility)
- [x] Task 2.1: Write failing TDD regression tests in `tests/test_engine.py` (RED phase: 11/12 failed before fixes)
- [x] Task 2.2: Harden `scripts/car_morphology.py` and `slu_chatbot_engine.py` (GREEN phase: 15/15 passing)
- [x] Task 2.3: Build `scripts/build_portal.py` + hardened WCAG-accessible `slu_egovernance_chatbot_ui.html` + `tests/test_parity_and_security.py`

## Checkpoint 2: Hardened Engine & Portal Verified
- [x] All Python + Node.js parity (51 queries) & XSS tests pass (`21/21` total suite passing)
- [x] DOM ID bindings, WCAG ARIA landmarks, and JS runtime verified via Node.js + HTML parser (note: live Chrome DevTools attach unavailable without Chrome remote-debugging enabled)

## Phase 3: Finals Expansion (SLU Policies, 156 CAR Lexicon, 250 Corpus, Supervised ML)
- [x] Task 3.1: Verify official SLU policies via `search_web` & build `data/expanded/slu_official_policies_v2.json` (32 policies, all 10 intents)
- [x] Task 3.2: Scale CAR & SLU Lexicon to 156 verified entries (`data/expanded/slu_car_domain_lexicon_v2.csv`)
- [x] Task 3.3: Build balanced 250 annotated corpus (`data/expanded/annotated_corpus_expanded.csv`) & strictly held-out 48-query benchmark (`data/expanded/heldout_benchmark.json`)
- [x] Task 3.4: Implement pure-Python NB, Logistic Regression & Linear SVM with Stratified 5-Fold CV + 4-stage Retrieval Ablation (`scripts/train_and_evaluate.py` + `tests/test_classifiers.py`)
- [x] Task 3.5: Generate 5 high-DPI Pillow charts (`scripts/generate_charts.py`), wire `scripts/build_all.py`, rebuild portal + `dist/`, update Drive Research Paper (with embedded charts) & Sheet Tab 2

## Checkpoint 3: Full System & ML Benchmarks Verified
- [x] `python3 scripts/build_all.py` passes cleanly end-to-end
- [x] All 21 unit, classifier, parity, and security tests pass
- [x] Research Paper & Google Sheet numerically consistent with `models/evaluation_report.json`

## Phase 4: 15–20 Minute Presentation Deck (Google Slides + PPTX)
- [x] Task 4.1: Create 18-slide SLU-themed Google Slides deck (`1iNS_Sc7_M05wmcsYoHOAFeKORWOtluJL4PRxLKaVsp0`) with embedded charts & timed 5-member speaker notes + export local `.pptx` + sync Drive Presentation Script
- [x] Task 4.2: Export thumbnails for all 18 slides and visually inspect every PNG; fixed Slides 4, 10, & 11 and re-verified 18/18 spotless
