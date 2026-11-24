import csv
import json
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import data_cleaning as dc
import data_preprocessing as dp


class TestMidtermReproducibility(unittest.TestCase):
    def test_stage2_and_stage3_reproduce_verified_midterm_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cleaned_path = os.path.join(tmpdir, "cleaned_corpus.txt")
            tokens_json = os.path.join(tmpdir, "preprocessed_tokens.json")
            bow_csv = os.path.join(tmpdir, "corpus_bow_summary.csv")
            annot_csv = os.path.join(tmpdir, "annotated_corpus_midterm.csv")

            docs, _ = dc.process_all_files(
                os.path.join(REPO_ROOT, "data", "raw_midterm"),
                cleaned_path,
            )
            self.assertEqual(len(docs), 24)
            # Verify specific Stage 2 fixes against raw Drive sources
            self.assertIn("ninyo", docs[1])
            self.assertNotIn("niyo", docs[1])
            self.assertIn("slu?", docs[2])
            self.assertIn("like haha", docs[3])
            self.assertIn("i will still answer", docs[0])

            payload, top30 = dp.preprocess_corpus(
                cleaned_path, tokens_json, bow_csv, annot_csv
            )
            self.assertEqual(payload["total_documents"], 24)
            self.assertEqual(payload["total_tokens"], 624)
            self.assertEqual(payload["unique_surface_tokens"], 457)
            self.assertEqual(payload["unique_vocabulary_size"], 426)
            self.assertEqual(len(payload["top_bigrams"]), 19)

            # Verify Top BoW terms (student=16, slu=10, examination=9, semester=8, year=4)
            bow_map = dict(top30)
            self.assertEqual(bow_map["student"], 16)
            self.assertEqual(bow_map["slu"], 10)
            self.assertEqual(bow_map["examination"], 9)
            self.assertEqual(bow_map["semester"], 8)
            self.assertEqual(bow_map["year"], 4)

            # Verify Doc #6 Freedom Wall ID unified to #25604 matching raw_community.txt
            with open(annot_csv, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 24)
            self.assertEqual(rows[5]["Section_Reference"], "Freedom Wall #25604")

    def test_root_artifacts_match_fresh_pipeline_run(self):
        with open(os.path.join(REPO_ROOT, "preprocessed_tokens.json"), encoding="utf-8") as f:
            pt = json.load(f)
        self.assertEqual(pt["total_documents"], 24)
        self.assertEqual(pt["total_tokens"], 624)
        self.assertEqual(pt["unique_vocabulary_size"], 426)
        self.assertEqual(pt["documents"][5]["section_ref"], "Freedom Wall #25604")

        with open(os.path.join(REPO_ROOT, "corpus_bow_summary.csv"), encoding="utf-8") as f:
            bow_rows = list(csv.DictReader(f))
        self.assertEqual(len(bow_rows), 30)
        self.assertEqual(bow_rows[3]["Stem_Term"], "semester")
        self.assertEqual(bow_rows[3]["Frequency"], "8")
        self.assertEqual(bow_rows[3]["Percentage_Coverage"], "1.28%")

    def test_cleaning_protects_ill_and_possessive_nouns(self):
        self.assertEqual(
            dc.clean_text("I am feeling ill today, where is SLU's Registrar's Office??"),
            "i am feeling ill today where is slu registrar office?",
        )
        self.assertEqual(
            dc.clean_text("ill still answer if you call me"),
            "i will still answer if you call me",
        )


if __name__ == "__main__":
    unittest.main()
