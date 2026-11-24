# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/build_all.py
Description: Master single-command reproducible build script for Group 2 - AiNomally.
             Executes every stage sequentially and runs the complete verification suite:
               1. Stage 1 verification (slu_web_scraper.py --verify-only)
               2. Stage 2 deterministic text cleaning (data_cleaning.py)
               3. Stage 3 Midterm preprocessing, BoW & bigrams (data_preprocessing.py)
               4. Phase 3 expanded SLU policy KB, 156-entry CAR lexicon & 250-doc corpus
               5. Supervised ML 5-Fold CV training & 48-query retrieval ablation study
               6. High-DPI Pillow chart generation (charts/)
               7. Hardened 4-tab web portal & Netlify dist/ build (build_portal.py)
               8. Full unittest + Python<->Node.js parity & XSS security verification
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


def run_step(title, cmd):
    print(f"\n{'=' * 72}\n[*] {title}\n{'=' * 72}")
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def main():
    py = sys.executable
    run_step("Stage 1: Verify Authentic Raw Midterm Corpus", [py, "scripts/slu_web_scraper.py", "--verify-only"])
    run_step("Stage 2: Deterministic Acronym-Safe Text Cleaning", [py, "scripts/data_cleaning.py"])
    run_step("Stage 3: Midterm Preprocessing, BoW & Bigrams", [py, "scripts/data_preprocessing.py"])
    run_step("Phase 3A: Build Verified Expanded SLU Policies (32), Lexicon (156) & Corpus (250)", [py, "scripts/build_expanded_datasets.py"])
    run_step("Phase 3B: Train & Benchmark NB, LogReg, Linear SVM (5-Fold CV) + 48-Query Ablations", [py, "scripts/train_and_evaluate.py"])
    run_step("Phase 3C: Render Publication-Grade Charts (Pillow)", [py, "scripts/generate_charts.py"])
    run_step("Phase 2/3D: Build Hardened Accessible 4-Tab Web Portal & dist/", [py, "scripts/build_portal.py"])
    run_step("Verification: Run Complete Unit, Classifier, Parity & Security Test Suite", [py, "-m", "unittest", "discover", "-s", "tests", "-v"])
    run_step("Verification: Run Midterm 8-Query Benchmark", [py, "slu_chatbot_engine.py", "--evaluate"])
    print("\n[SUCCESS] Full Group 2 AiNomally CSE 30 pipeline built and verified with 0 errors.")


if __name__ == "__main__":
    main()
