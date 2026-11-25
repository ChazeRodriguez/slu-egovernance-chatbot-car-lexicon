import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import slu_chatbot_engine as eng


class TestChatbotEngineHardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Explicitly test midterm mode for baseline policy Doc IDs (9-24)
        try:
            cls.bot = eng.SLUChatbotEngine(dataset="midterm")
        except TypeError:
            cls.bot = eng.SLUChatbotEngine()

    def test_no_false_positive_kankanaey_on_english_plagiarism(self):
        res = self.bot.answer_query("What is the punishment for plagiarism?")
        self.assertEqual(res["code_switching"], "EN")
        self.assertNotIn("Kankanaey", res["synthesized_response"])
        self.assertEqual(res["top_documents"][0]["doc_id"], 15)

    def test_no_false_positive_ibaloi_on_english_disciplinary(self):
        res = self.bot.answer_query("Who is on the disciplinary board?")
        self.assertEqual(res["code_switching"], "EN")
        self.assertNotIn("Ibaloi", res["synthesized_response"])
        self.assertEqual(res["top_documents"][0]["doc_id"], 15)

    def test_genuine_car_languages_trigger_correct_greetings(self):
        ilo = self.bot.answer_query("Naimbag a bigat! Agadal ak idiay SAMCIS, ilan absences bago FDA?")
        self.assertEqual(ilo["code_switching"], "CAR-TL-EN")
        self.assertIn("Ilocano", ilo["synthesized_response"])

        kne = self.bot.answer_query("Gawis ay agew! Inayan ang cheating sa exam")
        self.assertEqual(kne["code_switching"], "CAR-TL-EN")
        self.assertIn("Kankanaey", kne["synthesized_response"])

        ibl = self.bot.answer_query("Mapteng ja agsapa! Ano ang tongtong sa disciplinary board?")
        self.assertEqual(ibl["code_switching"], "CAR-TL-EN")
        self.assertIn("Ibaloi", ibl["synthesized_response"])

    def test_ill_and_possessive_cleaning_not_corrupted(self):
        cleaned = eng.clean_text("I am feeling ill today, where is SLU's Registrar's Office??")
        self.assertIn("feeling ill", cleaned)
        self.assertNotIn("i will", cleaned)
        self.assertNotIn("slu is", cleaned)
        self.assertTrue(cleaned.endswith("?"))

    def test_out_of_domain_gibberish_returns_safe_fallback_not_doc1(self):
        res = self.bot.answer_query("random gibberish xyzzy qwerty foobar")
        self.assertTrue(res.get("is_fallback", False))
        self.assertEqual(res["predicted_intent"], "OUT_OF_DOMAIN")
        self.assertNotIn("to my samcis guy", res["synthesized_response"].lower())

    def test_simple_greeting_returns_greeting_not_kind_mother_doc(self):
        res = self.bot.answer_query("hello good morning")
        self.assertEqual(res["predicted_intent"], "GREETING")
        self.assertNotIn("amputated", res["synthesized_response"].lower())

    def test_cyberbullying_and_libel_retrieve_ra10173_policy(self):
        res = self.bot.answer_query("Is cyberbullying or libel on Freedom Wall punishable?")
        self.assertFalse(res.get("is_fallback", False))
        self.assertEqual(res["top_documents"][0]["doc_id"], 9)

    def test_numeric_grade_74_retrieves_passing_grade_policy(self):
        res = self.bot.answer_query("What happens if I get 74 in a subject?")
        self.assertEqual(res["top_documents"][0]["doc_id"], 12)

    def test_shifting_queries_rank_transferee_qe_first(self):
        for q in [
            "How do I shift from SAMCIS to Nursing?",
            "Paano mag-shift? May qualifying exam ba?",
        ]:
            res = self.bot.answer_query(q)
            self.assertEqual(res["top_documents"][0]["doc_id"], 18, f"Failed for: {q}")

    def test_bilingual_and_car_stemmer_no_english_corruption(self):
        protected = [
            "magnify", "magician", "magical", "maganda",
            "magnesium", "manganese", "magnate", "paginated",
            "management", "mandatory", "department", "campus",
        ]
        for word in protected:
            self.assertEqual(eng.bilingual_stemmer(word), word, f"Corrupted '{word}'")

        self.assertEqual(eng.bilingual_stemmer("magtanong"), "tanong")
        self.assertEqual(eng.bilingual_stemmer("nagbayad"), "bayad")
        self.assertEqual(eng.bilingual_stemmer("agadal"), "adal")
        self.assertEqual(eng.bilingual_stemmer("agsurat"), "surat")
        self.assertEqual(eng.bilingual_stemmer("man-obla"), "obla")

    def test_standalone_mag_removed_from_query_stems(self):
        res = self.bot.answer_query("Pwede mag tanong paano mag enroll?")
        self.assertNotIn("mag", res["stems"])

    def test_doc6_freedom_wall_id_unified_to_25604(self):
        doc6 = next(d for d in self.bot.docs if d["doc_id"] == 6)
        self.assertEqual(doc6["section_ref"], "Freedom Wall #25604")

    def test_niche_latin_honors_absences_and_special_policies_expanded(self):
        exp_bot = eng.SLUChatbotEngine(dataset="expanded")

        r_latin = exp_bot.answer_query("What are the specific grades you need for Latin honors?")
        self.assertEqual(r_latin["top_documents"][0]["doc_id"], 133)
        self.assertIn("93", r_latin["synthesized_response"])
        self.assertIn("91", r_latin["synthesized_response"])
        self.assertIn("88", r_latin["synthesized_response"])

        r_abs = exp_bot.answer_query("How many absences do I have before I become dropped vs. permanently dropped?")
        self.assertEqual(r_abs["top_documents"][0]["doc_id"], 134)
        self.assertTrue(r_abs.get("is_comparative"))
        self.assertIn("11th", r_abs["synthesized_response"])

        r_consec = exp_bot.answer_query("What happens if I am absent for 3 consecutive meetings in my class?")
        self.assertEqual(r_consec["top_documents"][0]["doc_id"], 134)
        self.assertIn("OSAS Readmission Slip", r_consec["synthesized_response"])

        r_prom = exp_bot.answer_query("Paano kumuha ng Finance Promissory Note para makapag-exam?")
        self.assertEqual(r_prom["top_documents"][0]["doc_id"], 150)

        r_pet = exp_bot.answer_query("How do irregular graduating students open a Petition Class?")
        self.assertEqual(r_pet["top_documents"][0]["doc_id"], 139)

        r_hd = exp_bot.answer_query("Is Honorable Dismissal permanent compared to an LOA?")
        self.assertEqual(r_hd["top_documents"][0]["doc_id"], 136)
        self.assertIn("Leave of Absence", r_hd["synthesized_response"])


if __name__ == "__main__":
    unittest.main()
