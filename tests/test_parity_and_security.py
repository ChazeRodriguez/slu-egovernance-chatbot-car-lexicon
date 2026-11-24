import json
import os
import re
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import slu_chatbot_engine as eng


class TestPortalParityAndSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html_path = os.path.join(REPO_ROOT, "slu_egovernance_chatbot_ui.html")
        with open(html_path, "r", encoding="utf-8") as f:
            cls.html = f.read()

    def test_no_unsafe_innerhtml_or_fabricated_bigrams(self):
        # Zero innerHTML assignments anywhere in portal script
        self.assertNotIn(".innerHTML", self.html)
        # Strict CSP meta tag present
        self.assertIn("Content-Security-Policy", self.html)
        # No fabricated bonifacio campus=2 or minimum grade=2 bigram entries
        m = re.search(r'<script id="slu-portal-bundle" type="application/json">(.*?)</script>', self.html, re.S)
        self.assertIsNotNone(m)
        bundle = json.loads(m.group(1).replace("<\\/", "</"))
        bg_map = {b["bigram"]: b["frequency"] for b in bundle["midtermStats"]["topBigrams"]}
        self.assertEqual(len(bg_map), 19)
        self.assertNotIn("bonifacio campus", bg_map)
        self.assertNotIn("minimum grade", bg_map)
        self.assertEqual(bundle["midtermStats"]["uniqueStems"], 426)

    def test_exact_python_vs_browser_js_parity_across_48_heldout_and_xss_queries(self):
        with open(os.path.join(REPO_ROOT, "data", "expanded", "heldout_benchmark.json"), encoding="utf-8") as f:
            bench = json.load(f)

        queries = [b["query"] for b in bench] + [
            "<img src=x onerror=alert(1)> How do I request TOR?",
            "dap-ay and man-obla in Kankanaey",
            "I am feeling ill, where is SLU's clinic?",
        ]

        # Extract embedded bundle + engine JS from the actual HTML file and run in Node.js
        m_bundle = re.search(r'<script id="slu-portal-bundle" type="application/json">(.*?)</script>', self.html, re.S)
        m_engine = re.search(
            r"(function createSLUChatbotEngine\(BUNDLE\) \{.*?\n  return \{ cleanText, tokenize, bilingualStemmer, generateBigrams, answerQuery \};\n\})",
            self.html,
            re.S,
        )
        self.assertIsNotNone(m_bundle)
        self.assertIsNotNone(m_engine)

        node_script = (
            "const bundle = " + m_bundle.group(1).replace("<\\/", "</") + ";\n"
            + m_engine.group(1) + "\n"
            + "const engine = createSLUChatbotEngine(bundle);\n"
            + "const queries = JSON.parse(process.argv[1]);\n"
            + "const out = queries.map(q => engine.answerQuery(q, 3));\n"
            + "process.stdout.write(JSON.stringify(out));\n"
        )
        proc = subprocess.run(
            ["node", "-e", node_script, json.dumps(queries)],
            capture_output=True,
            text=True,
            check=True,
        )
        js_results = json.loads(proc.stdout)

        py_bot = eng.SLUChatbotEngine(dataset="expanded")
        for q, js_r in zip(queries, js_results):
            py_r = py_bot.answer_query(q, top_k=3)
            self.assertEqual(js_r["cleaned_query"], py_r["cleaned_query"], f"cleaned mismatch on {q}")
            self.assertEqual(js_r["stems"], py_r["stems"], f"stems mismatch on {q}")
            self.assertEqual(js_r["code_switching"], py_r["code_switching"], f"register mismatch on {q}")
            self.assertEqual(js_r["predicted_intent"], py_r["predicted_intent"], f"intent mismatch on {q}")
            self.assertEqual(js_r["ml_intent"], py_r["ml_intent"], f"ml_intent mismatch on {q}")
            self.assertEqual(js_r["is_fallback"], py_r["is_fallback"], f"fallback mismatch on {q}")
            self.assertEqual(js_r["is_greeting"], py_r["is_greeting"], f"greeting mismatch on {q}")
            py_top = [d["doc_id"] for d in py_r["top_documents"]]
            js_top = [d["doc_id"] for d in js_r["top_documents"]]
            self.assertEqual(js_top, py_top, f"top_docs mismatch on {q}: py={py_top} js={js_top}")


if __name__ == "__main__":
    unittest.main()
