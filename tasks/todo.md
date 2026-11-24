# Task Checklist — Group 2 AiNomally CSE 30 Complete Overhaul

## Phase 1: Reproducible Local Repo & Google Drive Sync
- [x] Task 1.0: Initialize git repo, directory layout, and ingest 4 raw Midterm files into `data/raw_midterm/`
- [ ] Task 1.1: Build deterministic `scripts/slu_web_scraper.py`, `scripts/data_cleaning.py`, `scripts/data_preprocessing.py` + `tests/test_pipeline.py`
- [ ] Task 1.2: Sync Google Sheet (`corpus_bow_summary.csv` Tab 1) and Drive scripts (`slu_web_scraper.py`, `data_cleaning.py`, `data_preprocessing.py`, `cleaned_corpus.txt`)

## Checkpoint 1: Foundation & Midterm Reproducibility
- [ ] `python3 -m unittest tests/test_pipeline.py` passes with 0 diffs
- [ ] Drive Sheet & scripts verified synced

## Phase 2: Engine & Portal Hardening (TDD + Security + Accessibility)
- [ ] Task 2.1: Write failing TDD regression tests in `tests/test_engine.py` (RED phase)
- [ ] Task 2.2: Harden `scripts/car_morphology.py` and `slu_chatbot_engine.py` (GREEN phase)
- [ ] Task 2.3: Build `scripts/build_portal.py` + hardened WCAG-accessible `slu_egovernance_chatbot_ui.html` + `tests/test_parity_and_security.py`

## Checkpoint 2: Hardened Engine & Portal Verified
- [ ] All Python + Node.js parity & XSS tests pass
- [ ] Browser verification confirms zero console errors and responsive layout

## Phase 3: Finals Expansion (SLU Policies, 150+ CAR Lexicon, 240+ Corpus, Supervised ML)
- [ ] Task 3.1: Verify official SLU policies via `search_web` & build `data/expanded/slu_official_policies_v2.json` (30+ policies, all 10 intents)
- [ ] Task 3.2: Scale CAR & SLU Lexicon to 150+ verified entries (`data/expanded/slu_car_domain_lexicon_v2.csv`)
- [ ] Task 3.3: Build balanced 240+ annotated corpus (`data/expanded/annotated_corpus_expanded.csv`) & strictly held-out 40+ query benchmark (`data/expanded/heldout_benchmark.json`)
- [ ] Task 3.4: Implement pure-Python NB, Logistic Regression & Linear SVM with Stratified 5-Fold CV + 4-stage Retrieval Ablation (`scripts/train_and_evaluate.py` + `tests/test_classifiers.py`)
- [ ] Task 3.5: Generate Pillow charts (`scripts/generate_charts.py`), wire `scripts/build_all.py`, rebuild portal + `dist/`, update Drive Research Paper & Sheet Tab 2

## Checkpoint 3: Full System & ML Benchmarks Verified
- [ ] `python3 scripts/build_all.py` passes cleanly end-to-end
- [ ] All unit, classifier, parity, and security tests pass
- [ ] Research Paper & Google Sheet numerically consistent with `models/evaluation_report.json`

## Phase 4: 15–20 Minute Presentation Deck (Google Slides + PPTX)
- [ ] Task 4.1: Create 18-slide SLU-themed Google Slides deck with embedded charts & timed 5-member speaker notes + export local `.pptx` + update Drive Presentation Script
- [ ] Task 4.2: Export thumbnails for all 18 slides and visually inspect every PNG for layout/contrast/overflow polish
