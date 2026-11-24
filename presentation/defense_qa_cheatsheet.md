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
| **Earold Delin** | Stage 3 Guarded Morphology, Midterm BoW/Bigrams & Track A 156-Entry CAR Electronic Lexicon |
| **Erick Sibayan** | 250-Doc Balanced Corpus, Stratified 5-Fold CV (NB/LR/SVM), Confusion Matrix & Hybrid Scoring |
| **John Andrew Angcaway** | 4-Stage Held-Out Ablation, TDD Bug Hardening, Zero-XSS Security, Py↔JS Parity & RA 10173 Privacy |

---

## Top 10 Expected Panel Questions & 20-Second Answers

### Q1. Why did Multinomial Naive Bayes (`95.61%` Macro F1) beat Linear SVM (`93.97%`) and Logistic Regression (`95.18%`)? *(Owner: Erick)*
> **Answer:** On a compact, balanced, high-dimensional sparse text dataset (`250` docs, `25` per class across `10` intents using TF-IDF unigrams + bigrams), generative **Multinomial Naive Bayes with Laplace smoothing** has lower variance and strong inductive bias on short code-switched utterances where exact keyword co-occurrences (like `tor`, `fda`, `qe`, `agadal`, `inayan`) are highly discriminative. Logistic Regression came within `0.43` points (`95.18%`, lowest std `±0.90%`), and Linear SVM reached `93.97%`. We selected NB both for peak Macro F1 and its compact JSON weight matrix that executes identically inside the browser.

### Q2. How did you guarantee zero data leakage in your 5-Fold CV and your 48-query benchmark? *(Owner: Erick / John Andrew)*
> **Answer:** Two strict walls: First, in `scripts/train_and_evaluate.py`, TF-IDF vocabulary fitting and IDF scaling run **strictly inside each training fold** (`200` train docs) before transforming the `50` held-out validation docs—never on the full corpus. Second, `data/expanded/heldout_benchmark.json` (`48` unseen queries) is programmatically checked by `tests/test_classifiers.py` to assert **zero exact-text overlap** with the `250` training documents, and uses freshly phrased EN, Taglish, CAR, OOD, and trap queries.

### Q3. In your 4-stage ablation, why did Stage C (`90.5%`) dip slightly below Stage B (`92.9%`) before Stage D recovered to `95.2%`? *(Owner: John Andrew)*
> **Answer:** That dip is actually our most valuable empirical finding! Stage C introduced two things: our calibrated **OOD Safety Gate** (which immediately raised OOD rejection from `0.0%` to `100.0%`) and single-keyword **lexicon intent boosting** (`156` entries). On multi-entity questions—such as asking about an exam permit/RFID while mentioning "tuition"—a single-keyword lexicon rule can over-boost a secondary intent. Stage D adds holistic **Multinomial NB intent probabilities** (`β = 0.30`) while moderating lexicon weight (`α_eff = 0.14`), resolving those collisions and delivering our peak **`95.2%` Top-1**, **`97.6%` Top-3**, **`0.9643` MRR**, and **`100.0%` OOD rejection**.

### Q4. Where do the 11 errors in your 10×10 Confusion Matrix come from? *(Owner: Erick)*
> **Answer:** Out of `250` out-of-fold predictions, **`239` (`95.6%`) are exact hits**, and three domains—`ACADEMIC_SHIFTING_TRANSFER`, `CAMPUS_FACILITIES_LAB`, and `TUITION_FINANCE`—scored a perfect `25/25`. All `11` misclassifications sit on genuine SLU administrative boundaries—for example, RFID lanyard rules overlapping between `CAMPUS_DECORUM_DRESSCODE` and `EXAM_PERMIT_INTEGRITY`, or portal clearance steps sitting near `URO_ENROLLMENT_TOR`. Pairing NB with TF-IDF policy ranking resolves those edge cases at retrieval time.

### Q5. Why didn't English words like "plagiarism" or "disciplinary" trigger false CAR greetings? *(Owner: Earold / John Andrew)*
> **Answer:** In our Midterm baseline, English semantic keywords were mixed into the same alias list as Kankanaey `inayan` and Ibaloi `tongtong`, causing pure English queries to falsely trigger regional greetings. We fixed this architecturally by splitting the lexicon CSV schema into **`Native_Aliases`** (strictly authentic Ilocano/Kankanaey/Ibaloi tokens) and **`Semantic_Aliases`** (English/Taglish cross-lingual bridges). Regional greetings fire strictly on `Native_Aliases`, achieving **`0.0%` false-positive CAR rate** on our regression traps and held-out benchmark.

### Q6. How does your morphological analyzer strip CAR affixes without breaking English words? *(Owner: Earold)*
> **Answer:** Naive prefix/suffix stripping corrupts English academic words—for example `management → nage`, `campus → campu`, `magnify → nify`, and `magician → ician`. Our hardened `scripts/car_morphology.py` protects English words via a curated **`PREFIX_EXCEPTIONS`** set plus **English suffix guards** (`-tion`, `-ment`, `-ify`, `-ical`, `-ician`, `-ium`) before normalizing productive Filipino (`mag-`, `nag-`, `-um-`, `-in-`), Ilocano (`ag-`, `panag-`, `agpa-`, `na-`), and Kankanaey/Ibaloi (`man-`, `men-`, hyphenated `man-obla`) affixes. `tests/test_engine.py` guards against regressions on every build.

### Q7. How did you verify the authenticity of the 156 CAR lexicon entries and the 32 SLU policies? *(Owner: Earold / Keith)*
> **Answer:** All **32 SLU policies** are grounded in official institutional publications (`slu.edu.ph` URO Services, 2015 Revised SLU Student Handbook, Finance/Scholarship guidelines, CCW Counseling, UNL Library, and `dataprotection.slu.edu.ph` RA 10173 policies). The **156-entry lexicon** (`48` Ilocano `ilo`, `40` Northern Kankanaey `kne`, `36` SLU/Taglish, `32` Ibaloi `ibl`) is grounded in Constantino (1971), Rubino (2000), Vanoverbergh (1933), Ballard (2011), and SIL Philippines—preserving documented cognates like `danum` (`ilo`), `danom` (`kne`), and `shanom` (`ibl`).

### Q8. Be honest about your 250-document corpus: how much was scraped vs. curated? *(Owner: Chaze / John Andrew)*
> **Answer:** We enforce 100% provenance transparency via an explicit `Source_Type` column in `annotated_corpus_expanded.csv`: **`32`** documents are official SLU policy provisions, **`8`** are authentic Midterm `#SLUFreedomWall` / URO inquiries, and **`210`** are explicitly tagged `CURATED_MULTILINGUAL_INQUIRY` utterances written to achieve strict `25`-per-class balance across English (`101`), Taglish (`79`), and CAR (`70`). We state this openly in our paper and Slide 20, and make native-speaker community validation Milestone 1 of our roadmap.

### Q9. How do you protect student privacy (RA 10173) and prevent web vulnerabilities like XSS? *(Owner: John Andrew)*
> **Answer:** Two layers: For **RA 10173 Data Privacy**, our Freedom Wall ingestion stores zero student names, IDs, or private identifiers, and the web portal runs **100% client-side in the browser**—meaning student queries never leave the user's device and there is no backend database to breach. For **Security**, we eliminated **100% of `.innerHTML` assignments** (using safe `textContent` DOM builders), enforced a strict Content-Security-Policy header (`netlify.toml`), and verify live XSS safety (`<img src=x onerror=alert(1)>`) plus **`51/51` Python↔Node.js parity** in `tests/test_parity_and_security.py`.

### Q10. Why build pure-Python ML + TF-IDF instead of calling ChatGPT or a hosted LLM API? *(Owner: Chaze / Keith)*
> **Answer:** Three practical eGovernance reasons: **Zero hallucination** (every response cites an exact verified SLU policy and triggers an honest `OUT_OF_DOMAIN` fallback at `100%` accuracy on gibberish/recipes), **zero API cost or latency** (runs instantaneously offline inside any browser or Python 3.14 stdlib with zero external ML libraries), and **strict RA 10173 privacy** (sensitive counseling or disciplinary questions never go to third-party cloud LLM servers). In our roadmap (Slide 21), we outline benchmarking compact local multilingual embeddings (`mE5`/`LaBSE`) with strict citation-grounded RAG as a next phase.

---

## Live Demo Quick Prompts (Copy-Paste Ready for Presentation)
1. **Taglish Shifting:** `Paano po process ng shifting from SAMCIS to SEAIT? May QE ba?`
2. **Ilocano Attendance:** `Naimbag a bigat! Agadal ak idiay SAMCIS—mano absent sakbay ma-FDA?`
3. **Northern Kankanaey Integrity:** `Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?`
4. **English CAR Trap (0% FP):** `What is the SLU disciplinary sanction for plagiarism?`
5. **Numeric Grade Rule:** `What happens if my final grade is 74?`
6. **Out-of-Domain Safety Gate:** `What is the best recipe for Baguio strawberry sinigang?`
7. **Live XSS Defense:** `<img src=x onerror=alert(1)> How do I request TOR?`
