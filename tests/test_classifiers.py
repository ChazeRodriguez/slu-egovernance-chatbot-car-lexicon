import csv
import json
import os
import sys
import unittest
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import train_and_evaluate as te
import slu_chatbot_engine as eng


class TestClassifiersAndExpandedDatasets(unittest.TestCase):
    def test_expanded_datasets_balance_and_zero_leakage(self):
        corp_path = os.path.join(REPO_ROOT, "data", "expanded", "annotated_corpus_expanded.csv")
        bench_path = os.path.join(REPO_ROOT, "data", "expanded", "heldout_benchmark.json")
        lex_path = os.path.join(REPO_ROOT, "data", "expanded", "slu_car_domain_lexicon_v2.csv")
        pol_path = os.path.join(REPO_ROOT, "data", "expanded", "slu_official_policies_v2.json")

        with open(corp_path, encoding="utf-8-sig") as f:
            corp = list(csv.DictReader(f))
        with open(bench_path, encoding="utf-8") as f:
            bench = json.load(f)
        with open(lex_path, encoding="utf-8-sig") as f:
            lex = list(csv.DictReader(f))
        with open(pol_path, encoding="utf-8") as f:
            pols = json.load(f)

        self.assertEqual(len(corp), 350)
        self.assertGreaterEqual(len(lex), 170)
        self.assertGreaterEqual(len(pols), 50)
        self.assertGreaterEqual(len(bench), 70)

        intent_counts = Counter(r["Intent_Category"] for r in corp)
        self.assertEqual(len(intent_counts), 10)
        for intent, cnt in intent_counts.items():
            self.assertEqual(cnt, 35, f"Unbalanced intent {intent}: {cnt}")

        # Verify every intent has >= 5 official policies
        pol_counts = Counter(p["intent_label"] for p in pols)
        for intent in intent_counts:
            self.assertGreaterEqual(pol_counts[intent], 5, f"Low policy count for {intent}")

        # Verify zero exact-text train/test leakage
        corp_texts = {r["Cleaned_Text"] for r in corp}
        for b in bench:
            self.assertNotIn(eng.clean_text(b["query"]), corp_texts, f"Leakage on {b['id']}")

    def test_stratified_folds_exact_balance(self):
        labels = [f"C{i}" for i in range(10) for _ in range(25)]
        folds = te.make_stratified_folds(labels, k=5, seed=42)
        self.assertEqual(len(folds), 5)
        seen = set()
        for fold in folds:
            self.assertEqual(len(fold), 50)
            fold_counts = Counter(labels[idx] for idx in fold)
            for c in range(10):
                self.assertEqual(fold_counts[f"C{c}"], 5)
            seen.update(fold)
        self.assertEqual(len(seen), 250)

    def test_trained_models_and_ablation_report_meet_rigor_bars(self):
        report_path = os.path.join(REPO_ROOT, "models", "evaluation_report.json")
        model_path = os.path.join(REPO_ROOT, "models", "intent_classifier.json")
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(os.path.exists(model_path))

        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)

        cv = report["stratified_5fold_cv"]
        self.assertEqual(len(cv), 3)
        for name, m in cv.items():
            self.assertGreater(m["macro_f1"], 0.85, f"{name} Macro F1 unexpectedly low: {m['macro_f1']}")
            self.assertEqual(len(m["confusion_matrix"]), 10)

        ab = report["heldout_ablation"]
        full = ab["D_full_hybrid"]
        raw = ab["A_raw_tfidf"]
        self.assertGreater(full["top1_policy_accuracy"], raw["top1_policy_accuracy"])
        self.assertGreaterEqual(full["top1_policy_accuracy"], 0.90)
        self.assertEqual(full["ood_rejection_rate"], 1.0)
        self.assertEqual(full["false_positive_car_rate"], 0.0)

    def test_expanded_engine_loads_ml_model_and_answers_new_intents(self):
        bot = eng.SLUChatbotEngine(dataset="expanded")
        self.assertIsNotNone(bot.ml_model)
        self.assertEqual(len(bot.docs), 52)
        self.assertEqual(len(bot.lexicon), 176)

        # Test previously uncovered intents (Tuition/Scholarship & Lab/Library)
        r_fin = bot.answer_query("How do I apply for SLU Entrance Scholarship for Valedictorians?")
        self.assertEqual(r_fin["predicted_intent"], "TUITION_FINANCE")
        self.assertEqual(r_fin["top_documents"][0]["doc_id"], 129)

        r_lib = bot.answer_query("How many books can undergraduates borrow from Vath library?")
        self.assertEqual(r_lib["predicted_intent"], "CAMPUS_FACILITIES_LAB")
        self.assertEqual(r_lib["top_documents"][0]["doc_id"], 130)

        # Test zero false-positive CAR on English plagiarism/disciplinary in expanded mode too
        r_trap = bot.answer_query("What is the punishment for plagiarism?")
        self.assertEqual(r_trap["code_switching"], "EN")
        self.assertNotIn("Kankanaey", r_trap["synthesized_response"])


if __name__ == "__main__":
    unittest.main()
