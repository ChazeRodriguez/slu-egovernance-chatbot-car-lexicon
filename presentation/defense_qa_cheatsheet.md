# CSE 30 Panel Defense Q&A Cheat Sheet — Group 2 AiNomally

**Project:** SLU eGovernance Multilingual Chatbot & CAR Electronic Lexicon  
**Course:** CSE 30 (Natural Language Processing) • SAMCIS, Saint Louis University, Baguio City  
**Rule of Thumb:** Answer in **20–30 seconds**, cite the **exact verified metric**, and hand off cleanly if a follow-up belongs to a teammate.

---

## Speaker Ownership Quick Map
| Teammate | Primary Defense Topics |
|---|---|
| **Chaze Rodriguez** | Project Vision, Dual-Track CSE 30 Alignment, Roadmap, Final Impact & Live Demo |
| **Keith Hernandez** | 5-Stage Architecture, Single-Command Reproducibility, Forensic Audit & Stage 2 Text Cleaning |
| **Earold Delin** | Stage 3 Guarded Morphology, Midterm BoW/Bigrams & Track A 176-Entry CAR Electronic Lexicon |
| **Erick Sibayan** | 350-Doc Balanced Corpus, Stratified 5-Fold CV (SVM/NB/LR), Confusion Matrix & Hybrid Scoring |
| **John Andrew Angcaway** | 4-Stage Held-Out Ablation, TDD Bug Hardening, Zero-XSS Canva UI, Py↔JS Parity & RA 10173 Privacy |

---

## Top 12 Expected Panel Questions & 20-Second Answers

### Q1. Why did One-vs-Rest Linear SVM (`95.43%` Macro F1) beat Multinomial Naive Bayes (`94.89%`) and Logistic Regression (`94.89%`)? *(Owner: Erick)*
> **Answer:** When we expanded to `350` balanced documents (`35` per intent across `10` classes) and adopted **sublinear TF-IDF scaling (`1 + log tf`)**, repetitive legal terms inside long Student Handbook policies no longer distorted term frequencies. Under sublinear TF, **One-vs-Rest Linear SVM with Hinge Loss** found cleaner maximum-margin boundaries across adjacent sub-policies, hitting **`95.43%` Accuracy and `95.43%` Macro F1** (`334/350` exact hits), edging out both Multinomial Naive Bayes and L2 Logistic Regression (`94.86%` Acc / `94.89%` F1). Converting SVM margins via softmax also lets us emit calibrated multi-intent probabilities directly inside the browser.

### Q2. How did you guarantee zero data leakage in your 5-Fold CV and your 75-query benchmark? *(Owner: Erick / John Andrew)*
> **Answer:** Two strict walls: First, in `scripts/train_and_evaluate.py`, TF-IDF vocabulary fitting and sublinear IDF scaling run **strictly inside each training fold** (`280` train docs) before transforming the `70` validation docs—never on the full `350`-doc corpus. Second, `data/expanded/heldout_benchmark.json` (`75` unseen queries: `69` in-domain + `6` OOD/greeting traps) is programmatically verified by `tests/test_classifiers.py` to assert **zero exact-text overlap** with the `350` training utterances.

### Q3. In your 4-stage ablation, why does Full Hybrid (Stage D) jump +10.2 points over Stage C (`88.4% -> 98.6%`)? *(Owner: John Andrew)*
> **Answer:** Stage C enables our **`176`-entry lexicon** and strict **OOD Safety Gate** (`0% -> 100%` OOD rejection immediately), reaching `88.4%` Top-1, where multi-entity queries containing secondary keywords (e.g., asking about exam permits/RFID while mentioning "tuition" or asking a comparative policy question) can pull single-keyword lexical scores slightly off-target. Stage D fuses **probabilistic SVM intent routing** (`P_ML >= 0.16`) and Handbook numeric/phrase anchors, jumping Top-1 accuracy to **`98.6%` (`68/69`)**, **`100.0%` Top-3 recall**, **`0.9928` MRR**, and **`100.0%` OOD rejection** (`100%` EN, `100%` TL-EN, `96.3%` CAR-TL-EN).

### Q4. Where do the 16 errors in your 10×10 Linear SVM Confusion Matrix come from? *(Owner: Erick)*
> **Answer:** Out of `350` out-of-fold predictions, **`334` (`95.43%`) are exact hits**, and both `ACADEMIC_SHIFTING_TRANSFER` and `CAMPUS_FACILITIES_LAB` scored a spotless **`35/35` (`100%`)**, while `HEALTH_SAFETY`, `EXAM_PERMIT_INTEGRITY`, `HANDBOOK_GRADING_FDA`, and `SUBJECT_ADJUSTMENT` each hit **`34/35`**. All `16` off-diagonal errors sit on real administrative overlaps—such as tuition refund adjustments bridging `TUITION_FINANCE` and `URO_SUBJECT_ADJUSTMENT` (`4` docs), or RFID lanyard clearance sitting near `EXAM_PERMIT_INTEGRITY` (`2` docs). Our multi-intent SVM routing + hybrid policy ranker resolves those cleanly at retrieval time.

### Q5. How does the chatbot handle the niche Latin Honors GWA question? *(Owner: Chaze / Erick)*
> **Answer:** Querying `"What are the specific grades you need for Latin honors?"` triggers `HANDBOOK_GRADING_FDA` and pins **Policy `doc_id 133`** (`>= 93.00%` **Summa Cum Laude** with no grade `< 85%`; `91.00%–92.99%` **Magna Cum Laude** with no `< 80%`; `88.00%–90.99%` **Cum Laude** with no `< 78%`), plus the disqualifiers: zero failing/dropped marks (`F`/`FDA`/`WP`/`DRP`) and at least `75%` of total credit units completed at SLU.

### Q6. How does it distinguish between "dropped" vs. "permanently dropped" absences? *(Owner: John Andrew / Erick)*
> **Answer:** Our **Comparative Multi-Policy Synthesis** detects comparative markers like `vs` / `difference between` and surfaces **Policy `doc_id 134`** alongside paired policies: **Voluntary Official Dropping (`WP`/`DRP`)** is student-initiated through URO/SAMCIS before final examinations (non-failing, can retake cleanly), whereas **Permanently Dropped (`FDA` — Failure Due to Absences)** occurs when unexcused absences exceed **`20%` of 54 semester hours** (`11th` absence in a 3-unit MWF class or `8th` absence in a TTh class) and is permanently recorded as failing **`D`**. We also surface the `3 consecutive` absences rule requiring an **OSAS Readmission Slip**.

### Q7. Why didn't English words like "plagiarism" or "disciplinary" trigger false CAR greetings? *(Owner: Earold / John Andrew)*
> **Answer:** By splitting the `176`-entry lexicon schema into **`Native_Aliases`** (strictly authentic Ilocano, Kankanaey, and Ibaloi tokens like `inayan`, `agadal`, `tongtong`, `karim`) versus **`Semantic_Aliases`** (English/Taglish cross-lingual bridges). Regional greetings fire strictly on `Native_Aliases`, guaranteeing **`0.0%` false-positive CAR detection** on English-only queries.

### Q8. How does your morphological analyzer strip CAR affixes without breaking English words? *(Owner: Earold)*
> **Answer:** Our hardened `scripts/car_morphology.py` guards English words with **`PREFIX_EXCEPTIONS`** and suffix checks (`-tion`, `-ment`, `-ify`, `-ical`, `-ician`, `-ium`) plus domain-safe normalization (`honors -> honor`, `permanently -> permanent`, `petitions -> petition`) before stripping productive Filipino (`mag-`, `nag-`, `-um-`, `-in-`), Ilocano (`ag-`, `panag-`, `agpa-`, `na-`), and Kankanaey/Ibaloi (`man-`, `men-`) affixes—eliminating legacy bugs like `management -> nage` and `magnify -> nify`.

### Q9. How did you verify the 176 CAR lexicon entries and the 52 SLU policies? *(Owner: Earold / Keith)*
> **Answer:** All **`52` SLU policies** cite official institutional publications (`slu.edu.ph` URO Services, 2015 Revised SLU Student Handbook, Finance/Scholarship/Promissory guidelines, CCW Counseling, UNL Library, and `dataprotection.slu.edu.ph`). The **`176`-entry lexicon** (`52` Ilocano `ilo`, `48` SLU/Taglish, `42` Northern Kankanaey `kne`, `34` Ibaloi `ibl`) draws from Constantino (1971), Rubino (2000), Vanoverbergh (1933), Ballard (2011), and SIL Philippines—preserving documented cognates (`danum`, `danom`, `shanom`) and academic honorific/drop terms (`karim`, `panagikkat`).

### Q10. Be honest about your 350-document corpus: how much was scraped vs. curated? *(Owner: Chaze / John Andrew)*
> **Answer:** Every row in `annotated_corpus_expanded.csv` carries an explicit `Source_Type` column: **`52`** documents are official SLU policy provisions, **`8`** are authentic Midterm `#SLUFreedomWall` / URO inquiries, and **`290`** are transparently labeled `CURATED_MULTILINGUAL_INQUIRY` utterances written to achieve strict **`35`-per-class balance** across English (`151`), Taglish (`109`), and CAR (`90`). Formal community validation with native `ilo`/`kne`/`ibl` speakers is Milestone 1 on Slide 21.

### Q11. How do you protect student privacy (RA 10173) and prevent web vulnerabilities like XSS? *(Owner: John Andrew)*
> **Answer:** For **RA 10173**, zero student names, IDs, or personal metadata are stored, and our Canva-styled web portal runs **100% client-side in the browser** so queries never leave the user's device. For **XSS Security**, we eliminated **100% of `.innerHTML` assignments** (building all DOM nodes with `textContent`), enforce strict CSP headers in `netlify.toml`, and verify live `<img src=x onerror=alert(1)>` defense plus **`78/78` Python↔Node.js parity** in `tests/test_parity_and_security.py`.

### Q12. Why build pure-Python ML + TF-IDF instead of calling ChatGPT or an external LLM API? *(Owner: Chaze / Keith)*
> **Answer:** Three practical eGovernance guarantees: **Zero hallucination** (100% policy-grounded retrieval with `100.0%` OOD rejection on non-SLU questions), **zero API cost or latency** (runs offline in Python 3.14 stdlib or static browser JS with zero external ML dependencies), and **strict RA 10173 privacy** (sensitive counseling, shifting, or FDA queries never go to third-party LLM servers).

---

## Live Demo Quick Prompts (Copy-Paste Ready for Presentation)
1. **Niche Latin Honors Cutoffs:** `What are the specific grades you need for Latin honors?`
2. **Dropped vs. Permanently Dropped (Comparative):** `How many absences do I have before I become dropped vs. permanently dropped?`
3. **Taglish Shifting:** `Paano po process ng shifting from SAMCIS to SEAIT? May QE ba?`
4. **Ilocano Attendance:** `Naimbag a bigat! Agadal ak idiay SAMCIS—mano absent sakbay ma-FDA?`
5. **Northern Kankanaey Integrity:** `Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?`
6. **English CAR Trap (0% FP):** `What is the SLU disciplinary sanction for plagiarism?`
7. **Out-of-Domain Safety Gate:** `What is the best recipe for Baguio strawberry sinigang?`
8. **Live XSS Defense:** `<img src=x onerror=alert(1)> How do I request TOR?`
