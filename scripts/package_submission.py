# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/package_submission.py
Description: Builds a clean, verifiable Finals submission bundle ZIP at
             submission/Group2_AiNomally_CSE30_Finals_Bundle.zip containing all
             runnable source scripts, tests, Midterm + Finals datasets, trained
             models, charts, hardened portal + dist/, presentation deck, speaker
             script, Q&A cheat sheet, and Turnitin PDF/DOCX exports (strictly
             excluding .git/, __pycache__/, .netlify/, and temp files).
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import os
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(REPO_ROOT, "submission")
ZIP_PATH = os.path.join(OUT_DIR, "Group2_AiNomally_CSE30_Finals_Bundle.zip")

EXCLUDE_DIRS = {".git", "__pycache__", ".netlify", ".venv", "venv", ".pytest_cache"}
EXCLUDE_FILES = {".DS_Store"}


def should_include(rel_path):
    parts = rel_path.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return False
    base = os.path.basename(rel_path)
    if base in EXCLUDE_FILES or base.endswith(".pyc") or base.endswith(".zip"):
        return False
    return True


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    added = []
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for fname in sorted(files):
                abs_path = os.path.join(root, fname)
                rel_path = os.path.relpath(abs_path, REPO_ROOT)
                if not should_include(rel_path):
                    continue
                arcname = os.path.join("Group2_AiNomally_CSE30_Resources", rel_path)
                zf.write(abs_path, arcname)
                added.append(rel_path)

    size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"[OK] Packaged {len(added)} files -> {ZIP_PATH} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
