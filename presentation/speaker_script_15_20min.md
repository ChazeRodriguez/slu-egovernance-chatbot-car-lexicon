# Group 2 – AiNomally | CSE 30 Classroom TV Presentation Script (22 Slides, 15–20 Minutes)

**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  
**Institution:** Saint Louis University (SAMCIS – Department of Computer Science), Baguio City  
**Instructor:** Prof. Dalos D. Miguel  
**Deck Format:** 22-Slide Large-Print Classroom TV Edition (minimum 14–16pt body/table type, full-canvas large-print charts)
**Total Spoken Word Count:** 2,589 words (~19.2 minutes at 135 wpm + live Q&A)

| Speaker | Slides Covered | Target Time |
|---|---|---|
| **Chaze Ezkys M. Rodriguez** | Slides 1–3, 21–22 (5 slides) | ~3:50 |
| **Keith Russel Hernandez** | Slides 4–7 (4 slides) | ~3:50 |
| **Earold Jan Delin** | Slides 8–11 (4 slides) | ~3:50 |
| **Erick James Sibayan** | Slides 12–15 (4 slides) | ~3:50 |
| **John Andrew Angcaway** | Slides 16–20 (5 slides) | ~3:55 |

---

## Slide 1

[Speaker 1: Chaze Rodriguez | Target: 0:40]
Good afternoon, Professor Dalos Miguel and fellow Louisian computer scientists! We are Group 2, AiNomally—John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, Erick James Sibayan, and I am Chaze Ezkys Rodriguez. Today we present our CSE 30 NLP Term Project: the SLU eGovernance Multilingual Chatbot and Cordillera Administrative Region Electronic Lexicon. Over the next eighteen minutes, we will walk you through how we unified verified Saint Louis University policies, Cordilleran linguistic preservation, leak-free supervised machine learning, and a hardened browser portal into one fully reproducible pipeline.

## Slide 2

[Speaker 1: Chaze Rodriguez | Target: 1:00]
Slide 2 frames the dual problem motivating our research right here in Baguio City. First, institutional guidance at SLU is scattered across the 2015 Student Handbook PDF, the University Registrar's website, OSAS circulars, Finance payment channels, and clinic notices. As a result, students turn to #SLUFreedomWall using informal Taglish and acronyms like SAMCIS, SEAIT, SONAHBS, dp, QE, and FDA—which standard English keyword search misses. Second, SLU serves a vibrant Cordillera Administrative Region student body speaking Ilocano, Northern Kankanaey, and Ibaloi. Off-the-shelf English NLP pipelines fail on Austronesian affixation like ag-, panag-, and man-, and ignore cultural governance concepts like inayan, dap-ay, and tongtong. Our thesis is simple: unifying verified SLU policies with a structured CAR lexicon solves campus support bottlenecks while preserving regional languages.

## Slide 3

[Speaker 1: Chaze Rodriguez | Target: 0:55]
Slide 3 aligns our work directly with both CSE 30 tracks. Under Track A, we built a 156-entry machine-readable SLU and CAR Electronic Lexicon tagged with ISO 639-3 codes, morphological roots, affixes, bilingual glosses, and strict Native versus Semantic alias separation. Under Track B, we engineered a hybrid eGovernance chatbot covering 32 verified SLU policy provisions across 10 domains, deployed in both a Python CLI and an accessible 4-tab web portal. Four core objectives guided every commit: single-command reproducibility, test-driven bug and security hardening, balanced scaling to 250 annotated documents, and leak-free empirical benchmarking via Stratified 5-Fold CV and 48 unseen test queries. I now turn it over to Keith Hernandez to walk through our architecture and data pipeline.

## Slide 4

[Speaker 2: Keith Hernandez | Target: 1:00]
Thank you, Chaze. Slide 4 shows our end-to-end 5-stage NLP pipeline, runnable from a clean checkout using one command: python3 scripts/build_all.py. Stage 1 acquires multi-source student discourse from #SLUFreedomWall alongside 32 verified SLU institutional policies across URO, the Student Handbook, Finance, Scholarships, Counseling, and Libraries. Stage 2 runs deterministic acronym-safe cleaning, protecting SLU acronyms, English contractions, and Cordilleran hyphens. Stage 3 applies our guarded bilingual and CAR morphological analyzer with 265 stopwords and bigram extraction. Stage 4 trains and benchmarks pure-Python Multinomial Naive Bayes, Logistic Regression, and Linear SVM models combined with our 156-entry lexicon and OOD safety gate. Finally, Stage 5 compiles the identical model weights and policies into our zero-XSS web portal. Notice we require zero external ML packages—pure Python 3.14 verified by 21 automated tests.

## Slide 5

[Speaker 2: Keith Hernandez | Target: 1:00]
Slide 5 visualizes our corpus and resource scaling from our Midterm baseline to Finals. Our annotated corpus grew 10.4 times from 24 to 250 strictly balanced documents—25 per class across 10 operational intents. Verified official SLU policies more than doubled from 12 to 32, filling critical Midterm blind spots like Tuition and Bank Payment Channels, Entrance and Academic Scholarships, the Center for Counseling and Wellness, and the UNL Vath Library. Our CAR and SLU lexicon grew 6.2 times from 25 to 156 entries, Cordilleran code-switched documents expanded 35 times from 2 to 70, and our evaluation expanded from 8 Midterm queries to 48 strictly held-out unseen queries with zero training leakage.

## Slide 6

[Speaker 2: Keith Hernandez | Target: 1:00]
Before scaling anything, we ran an exhaustive forensic audit across every local file and Google Drive deliverable, summarized on Slide 6. We caught and resolved six real discrepancies: First, unique Midterm stems were corrected from an outdated 352 to the verified 426 stems (TTR 0.6827). Second, 'semester' was corrected from 9 to 8 occurrences (1.28%), restoring 'year' at Rank 19. Third, the Drive Google Sheet still held old Prelim counts like 'like=12' and 'campu=4'—we replaced Tab 1 with the verified Top 30 and added a new Finals Tab 2. Fourth, we removed two fabricated bigrams from the portal, keeping strictly the 19 verified recurring bigrams. Fifth, Doc #6's mismatched Freedom Wall ID #25582 was unified everywhere to the true raw ID #25604. Our automated test_pipeline.py now proves 0-diff reproduction on every build.

## Slide 7

[Speaker 2: Keith Hernandez | Target: 0:50]
Slide 7 highlights how we hardened Stage 2 text cleaning in scripts/data_cleaning.py. Earlier cleaning stripped parenthesized SLU acronyms like (SAMCIS) and (TOR) along with timestamps—our acronym-safe regex deletes submission headers while keeping every institutional acronym intact. During our code audit, we also caught two subtle real-world bugs: naive expansion turned medical 'feeling ill' into 'feeling i will', and 'SLU's Registrar's Office' into 'slu is registrar is office'. We replaced those with context-aware regex rules that expand 'ill' only before modal verbs and strip possessive 's cleanly. Finally, Taglish clitics like dp and ngaun normalize cleanly while preserving punctuation polarity and Cordilleran hyphens like dap-ay and man-obla. Passing it to Earold Delin for morphology and our Track A CAR lexicon.

## Slide 8

[Speaker 3: Earold Delin | Target: 1:05]
Thank you, Keith. Slide 8 examines Stage 3: our guarded bilingual and Cordilleran morphological analyzer in scripts/car_morphology.py. On the left in red, you see why naive affix stripping fails on bilingual academic text. Early runs corrupted 'management' into 'nage' and 'campus' into 'campu', and an unguarded Tagalog 'mag-' prefix rule mangled English words like 'magnify' into 'nify' and 'magician' into 'ician'. We fixed this permanently using curated PREFIX_EXCEPTIONS plus English suffix guards such as -tion, -ment, -ify, and -ician. On the right in teal, authentic Philippine and Cordilleran affixes normalize reliably: Filipino magtanong and tinanong collapse to tanong, Ilocano agadal and panagadal collapse to adal, agpaagas collapses to agas, and Northern Kankanaey man-obla and men-obla normalize to obla.

## Slide 9

[Speaker 3: Earold Delin | Target: 0:55]
Slide 9 presents our verified Midterm Top 10 Bag of Words lexical profile across the 24 consolidated baseline documents. After removing stopwords and running our guarded lemmatizer, we obtain 624 filtered tokens, 457 unique surface forms, and 426 unique verified stems—with zero corrupted roots. 'student' leads at 16 occurrences (2.56%), followed by 'slu' at 10, 'examination' at 9, and highlighted in SLU Gold, our audited 'semester' count at exactly 8 (1.28%), followed by 'grade', 'requirement', and 'subject' at 7 each. Across contiguous bigrams, 19 true institutional phrases recur at frequency 2, including 'official transcript', 'qualifying examination', and 'failure due'. Every chart, CSV, Google Sheet cell, and portal counter is 100% synced.

## Slide 10

[Speaker 3: Earold Delin | Target: 1:00]
Now let's examine Track A on Slide 10: our 156-entry SLU and CAR Electronic Lexicon. We scaled from 25 Midterm entries to 156 curated records: 48 Ilocano (ISO 639-3: ilo), 40 Northern Kankanaey (kne), 36 SLU institutional acronyms and Taglish student slang, and 32 Ibaloi (ibl). Every entry is linguistically grounded in standard lexicographic authorities—Constantino and Rubino for Ilocano, Vanoverbergh for Kankanaey, Ballard for Ibaloi, and SIL Philippines—capturing cross-language cognates like danum, danom, and shanom for water, alongside cultural governance terms like inayan, dap-ay, and tongtong. Crucially, separating Native_Aliases from English Semantic_Aliases guarantees 0.0% false-positive regional language detection.

## Slide 11

[Speaker 3: Earold Delin | Target: 0:50]
Slide 11 shows five representative rows from our machine-readable CSV schema in data/expanded/slu_car_domain_lexicon_v2.csv. Each record captures its Entry ID, normalized lemma, ISO 639-3 tag, part of speech, root and affix structure, English and Filipino glosses, separated native and semantic alias arrays, and mapped SLU intent. For instance, SLU-001 maps samcis to shifting and enrollment; ILO-008 records Ilocano agadal with prefix ag- on root adal; KNE-002 preserves Kankanaey inayan mapped to academic integrity; IBL-002 maps Ibaloi tongtong to customary mediation and disciplinary councils; and IBL-007 documents the distinctive Ibaloi postalveolar sh- reflex in shanom. I will now hand it over to Erick Sibayan for our balanced corpus and supervised machine learning benchmarks.

## Slide 12

[Speaker 4: Erick Sibayan | Target: 0:55]
Thank you, Earold. Slide 12 details our expanded 250-document multi-layer annotated corpus built specifically to make Stratified 5-Fold Cross-Validation statistically sound. Every one of our 10 SLU operational intent domains—from TOR and iSLU Enrollment to Shifting, Grading/FDA, Exam Integrity, Dress Code, Health & Counseling, Tuition & Scholarships, and Libraries & Labs—contains exactly 25 annotated documents and at least 3 verified official SLU policy provisions. Across registers, we maintain rich multilingual balance: 101 English (40.4%), 79 Taglish (31.6%), and 70 Cordilleran code-switched documents (28.0%). For full academic transparency, every row carries a Source_Type tag distinguishing our 32 official policies, 8 authentic Midterm Freedom Wall/URO queries, and 210 curated multilingual queries.

## Slide 13

[Speaker 4: Erick Sibayan | Target: 1:00]
Slide 13 presents our supervised intent classification results implemented from scratch in pure Python in scripts/train_and_evaluate.py. To prevent data leakage, TF-IDF unigram and bigram vectorizers are refit strictly inside each training fold of Stratified 5-Fold CV. We benchmarked three classical linear and probabilistic models: Multinomial Naive Bayes with Laplace smoothing led the field at 95.60% accuracy and 95.61% Macro F1 (±1.47%). L2-regularized Softmax Logistic Regression placed a remarkably close second at 95.20% accuracy and 95.18% Macro F1 with the tightest variance (±0.90%). One-vs-Rest Linear SVM with Hinge Loss achieved 94.00% accuracy and 93.97% Macro F1. We selected Multinomial Naive Bayes as our deployed production intent classifier for its peak F1 and compact JSON weight footprint.

## Slide 14

[Speaker 4: Erick Sibayan | Target: 0:55]
Slide 14 shows the aggregated 10-by-10 out-of-fold confusion matrix for our winning Multinomial Naive Bayes classifier across all 250 documents. Notice how clean the green main diagonal is: 239 out of 250 documents are classified accurately, with three domains—Shifting, Facilities & Labs, and Tuition & Finance—achieving a spotless 25 out of 25! Only 11 errors occur across the entire 250-document corpus, shown in light crimson, and every single one reflects genuine administrative boundary overlap—such as RFID lanyard rules sitting between Dress Code and Exam Permit Integrity. That error analysis directly confirmed why pairing Naive Bayes with lexical policy scoring produces superior retrieval.

## Slide 15

[Speaker 4: Erick Sibayan | Target: 1:00]
Slide 15 shows how we fuse all NLP components in our hybrid policy ranker and harden every edge case using Test-Driven Development. Each candidate official SLU policy is scored by combining expanded TF-IDF cosine similarity, a moderated lexicon intent boost of 0.14, our trained Multinomial Naive Bayes posterior weighted at 0.30, and a small policy-authority prior. Before touching code, we wrote 12 regression tests—11 initially failed on the Midterm baseline, exposing four critical bugs we fixed cleanly: native-only CAR greeting triggers, a calibrated OOD safety gate, numeric grade preservation so '74' hits the 75% rule alongside RA 10173 cyberbullying routing, and holistic NB moderation to resolve multi-keyword collisions. Passing to John Andrew Angcaway for our ablation study and portal demo.

## Slide 16

[Speaker 5: John Andrew Angcaway | Target: 1:00]
Thank you, Erick. Slide 16 reports our 4-stage ablation study evaluated on 48 strictly held-out unseen queries—42 in-domain queries across English, Taglish, and CAR languages, plus 4 out-of-domain traps and 2 greetings, with zero text overlap against training data. Look at the progression: Stage A (raw TF-IDF cosine) starts at 83.3% Top-1 accuracy and 0% OOD safety. Stage B adds acronym-safe cleaning and CAR morphology, leaping +9.6 points to 92.9% Top-1 and 0.960 MRR. Stage C turns on the 156-entry lexicon and OOD gate—OOD rejection jumps immediately from 0% to 100%, while exposing a slight 90.5% dip caused by single-keyword collisions. Finally, Stage D adds our trained Naive Bayes classifier, resolving collisions and achieving our best marks: 95.2% Top-1 accuracy, 97.6% Top-3, 0.964 MRR, 100% OOD safety, and 0.0% false-positive CAR detections—including 100% accuracy on Taglish and 95% on Cordilleran queries!

## Slide 17

[Speaker 5: John Andrew Angcaway | Target: 1:00]
Slide 17 covers production engineering: security, cross-runtime parity, and accessibility. First, on security: our audit flagged DOM XSS vectors in the original HTML portal. We eliminated 100% of .innerHTML assignments, rebuilt every chat bubble, trace card, and table using safe textContent DOM nodes, added a strict Content-Security-Policy meta tag plus Netlify security headers, and tested live against an <img onerror=alert(1)> payload. Second, on parity: scripts/build_portal.py compiles the exact same policies, lexicon, and Naive Bayes weights into the browser UI, and our automated Node.js test confirms 51 out of 51 identical outputs between Python and JavaScript. Third, our 4-tab portal meets WCAG 2.1 AA contrast with full keyboard ARIA tablist navigation.

## Slide 18

[Speaker 5: John Andrew Angcaway | Target: 0:55]
Slides 18 and 19 walk through four live multilingual query traces verified identically in our CLI and browser portal. On Slide 18, Case 1 tests a real Taglish shifting question: 'Paano process ng shifting from SAMCIS to SEAIT? May QE ba?' Our hybrid engine preserves all three SLU acronyms, classifies ACADEMIC_SHIFTING_TRANSFER, and returns the exact URO internal shifting and Qualifying Examination procedure. Case 2 tests an Ilocano code-switched attendance question: 'Naimbag a bigat! Agadal ak idiay SAMCIS—mano absent sakbay ma-FDA?' The engine recognizes native Ilocano, responds warmly with 'Naimbag a bigat/aldaw!', normalizes agadal to adal, and cites Student Handbook Article I's 20% unexcused absence FDA ceiling.

## Slide 19

[Speaker 5: John Andrew Angcaway | Target: 0:55]
Continuing our walkthrough on Slide 19: Case 3 tests Northern Kankanaey academic integrity—'Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?' Because 'gawis' and 'inayan' are genuine native Kankanaey entries, the assistant greets the student with 'Gawis ay agew!' and retrieves Student Handbook Article II, Section 4 on SLU Disciplinary Board sanctions—whereas a plain English plagiarism query cleanly suppresses regional greetings. Case 4 demonstrates our safety gate: asking for a 'Baguio strawberry sinigang' recipe scores below our 0.14 threshold, triggering OUT_OF_DOMAIN with zero hallucination and politely directing the user to official SLU offices.

## Slide 20

[Speaker 5: John Andrew Angcaway | Target: 0:50]
Slide 20 shares our honest engineering limitations and Data Privacy Act (RA 10173) safeguards. We openly tag all 210 expanded multilingual training utterances as CURATED_MULTILINGUAL_INQUIRY rather than claiming they were all scraped live, and our next linguistic milestone is formal community validation with native Ilocano, Northern Kankanaey, and Ibaloi speakers. On privacy, our Freedom Wall scraper stores zero student names, IDs, or private identifiers, and because the web portal executes 100% client-side in the browser with static hosting, student questions never leave their own device. Back to Chaze for our roadmap and closing!

## Slide 21

[Speaker 1: Chaze Rodriguez | Target: 0:45]
Thank you, John Andrew. Slide 21 maps our three-step roadmap beyond CSE 30. Step 1 is partnering with native CAR linguists and student organizations at SLU to validate idioms, diacritics, and anonymized real-world queries while expanding toward Bontok and Ifugao. Step 2 is benchmarking compact multilingual sentence embeddings like mE5 or LaBSE alongside our fast Naive Bayes baseline, paired with strict policy-grounded RAG summarization that never fabricates citations. Step 3 is institutional integration with live iSLU academic calendars, OSAS advisories, and official URO ticketing workflows.

## Slide 22

[Speaker 1: Chaze Rodriguez & All Members | Target: 0:45]
To close on Slide 22: Group 2 AiNomally delivered a fully reproducible, audited, security-hardened multilingual NLP ecosystem for Saint Louis University. From 250 balanced corpus documents, 32 official SLU policies, and 156 verified CAR lexicon entries to 95.61% Stratified 5-Fold CV Macro F1, 95.2% unseen Top-1 policy accuracy, 100% OOD safety, and 21 passing automated tests, every single metric in our paper, spreadsheet, and portal is backed by deterministic code. Agyamanak! Iyaman! Dakel a iyaman! Thank you very much, Professor Dalos Miguel and classmates—we are now ready for your questions and live portal demo!
