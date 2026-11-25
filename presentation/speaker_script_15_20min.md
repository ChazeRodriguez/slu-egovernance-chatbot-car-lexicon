# Group 2 – AiNomally | CSE 30 Classroom TV Presentation Script (22 Slides, 15–20 Minutes)

**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  
**Institution:** Saint Louis University (SAMCIS – Department of Computer Science), Baguio City  
**Instructor:** Prof. Dalos D. Miguel  
**Deck Format:** 22-Slide Canva EAG-QJ6Vos4 Graph-Paper Classroom TV Edition (minimum 14pt body/table type, full-canvas large-print TV charts)
**Total Spoken Word Count:** 2,074 words (~15.4 minutes at 135 wpm + live Q&A)

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
Good afternoon, Professor Dalos Miguel and fellow Louisian computer scientists! We are Group 2, AiNomally—John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, Erick James Sibayan, and I am Chaze Ezkys Rodriguez. Today we present our CSE 30 NLP Term Project: the SLU eGovernance Multilingual Chatbot and Cordillera Administrative Region Electronic Lexicon, now upgraded to 52 verified SLU policies—including Latin honors GWA thresholds and dropped versus permanently dropped FDA rules—paired with leak-free supervised machine learning and our Canva graph-paper portal.

## Slide 2

[Speaker 1: Chaze Rodriguez | Target: 1:00]
Slide 2 frames the dual problem motivating our research right here in Baguio City. First, critical Saint Louis University rules—like exact Latin honors GWA cutoffs or when a withdrawal becomes permanent FDA—are scattered across the 2015 Student Handbook PDF, URO website, OSAS circulars, and Finance channels. Students turn to #SLUFreedomWall in urgent Taglish using SAMCIS, dp, QE, and FDA, which keyword search misses. Second, SLU serves a vibrant Cordillera student body speaking Ilocano, Northern Kankanaey, and Ibaloi, where English NLP breaks on affixes like ag-, panag-, and man-, and ignores cultural roots like inayan, dap-ay, and tongtong.

## Slide 3

[Speaker 1: Chaze Rodriguez | Target: 0:55]
Slide 3 aligns our work directly with both CSE 30 tracks. Under Track A, we built a 176-entry machine-readable SLU and CAR Electronic Lexicon tagged with ISO 639-3 codes, morphological roots, affixes, and Native versus Semantic alias separation. Under Track B, we engineered a hybrid eGovernance chatbot covering 52 verified SLU policy provisions across 10 domains. Four pillars guided every commit: single-command reproducibility, TDD security hardening, balanced scaling to 350 annotated docs, and leak-free benchmarking on 75 unseen queries. Over to Keith Hernandez for architecture and data cleaning.

## Slide 4

[Speaker 2: Keith Hernandez | Target: 1:00]
Thank you, Chaze. Slide 4 shows our end-to-end 5-stage NLP pipeline runnable from a clean checkout via python3 scripts/build_all.py. Stage 1 unifies #SLUFreedomWall student posts with 52 official SLU rules covering URO, the Student Handbook, Latin honors, absences, Finance, Counseling, and Libraries. Stage 2 runs deterministic acronym-safe cleaning, protecting acronyms and CAR hyphens. Stage 3 applies our guarded bilingual and Cordilleran morphological analyzer with 265 stopwords and bigrams. Stage 4 trains pure-Python Linear SVM, Naive Bayes, and Logistic Regression fused with our 176-entry lexicon and OOD safety gate. Stage 5 compiles identical model weights into our zero-XSS Canva graph-paper portal, verified by 22 automated tests.

## Slide 5

[Speaker 2: Keith Hernandez | Target: 1:00]
Slide 5 visualizes our scaling from Midterm to Finals. Our annotated corpus grew 14.6 times from 24 to 350 strictly balanced documents—35 per class across 10 operational intents. Authoritative SLU policies grew 4.3 times from 12 to 52, now explicitly covering niche high-demand Handbook provisions like Latin Honors GWA requirements (93, 91, 88 percent), Voluntary Dropping versus 20% Permanent FDA, Promissory Notes, and Petition Classes. Our CAR lexicon expanded 7.0 times from 25 to 176 entries, Cordilleran documents jumped 45 times from 2 to 90, and held-out evaluation expanded from 8 to 75 strictly unseen queries with zero leakage.

## Slide 6

[Speaker 2: Keith Hernandez | Target: 1:00]
Before scaling, we ran a forensic audit across every local file and Google Drive deliverable, summarized on Slide 6. We resolved five concrete mismatches: Midterm unique stems corrected from 352 to the verified 426 stems (TTR 0.6827); semester corrected from 9 to 8 occurrences (1.28%), restoring year at Rank 19; Google Sheet Tab 1 replaced stale Prelim counts with verified Top 30 counts plus a live Finals Summary tab; two fabricated bigrams were removed from the portal leaving the 19 real recurring bigrams; and Doc #6 was unified everywhere to raw Freedom Wall ID #25604.

## Slide 7

[Speaker 2: Keith Hernandez | Target: 0:50]
Slide 7 highlights Stage 2 deterministic text cleaning in scripts/data_cleaning.py. Naive regex previously stripped parenthesized acronyms like (SAMCIS) and (TOR), turned medical 'feeling ill' into 'feeling i will', and turned 'SLU's Registrar's Office' into 'slu is registrar is office'. Our hardened context-aware rules expand 'ill' only before modal verbs, strip possessive 's cleanly, normalize Taglish slang like dp and ngaun, and preserve Cordilleran hyphens such as dap-ay and man-obla. Passing to Earold Delin for morphology and our Track A CAR lexicon.

## Slide 8

[Speaker 3: Earold Delin | Target: 1:05]
Thank you, Keith. Slide 8 examines Stage 3: our guarded bilingual and CAR morphological analyzer in scripts/car_morphology.py. On the left, unguarded affix rules historically mangled 'management' into 'nage', 'campus' into 'campu', 'magnify' into 'nify', and 'magician' into 'ician'. Curated PREFIX_EXCEPTIONS and English suffix guards (-tion, -ment, -ify, -ician, -ably) eliminate corruption completely. We also refined niche lemmatizers so 'honors' normalizes to 'honor' and 'permanently' to 'permanent'. On the right, authentic Filipino (magtanong -> tanong), Ilocano (agadal, panagadal -> adal; agpaagas -> agas), and Kankanaey (man-obla -> obla) inflections normalize reliably.

## Slide 9

[Speaker 3: Earold Delin | Target: 0:55]
Slide 9 presents our verified Midterm Top 10 Bag of Words lexical profile across the 24 consolidated baseline documents. Across 624 filtered tokens and 426 unique stems, 'student' leads at 16 occurrences (2.56%), followed by 'slu' (10), 'examination' (9), and in coral-orange, our audited 'semester' count at exactly 8 (1.28%), followed by 'grade', 'requirement', and 'subject' at 7 each. Our 19 recurring institutional bigrams ('official transcript', 'qualifying examination', 'failure due') stay 100% synced across CLI, Sheet, and UI.

## Slide 10

[Speaker 3: Earold Delin | Target: 1:00]
Now let's examine Track A on Slide 10: our 176-entry SLU and CAR Electronic Lexicon. It comprises 52 Ilocano (ilo), 42 Northern Kankanaey (kne), 48 SLU institutional and Taglish terms, and 34 Ibaloi (ibl) entries—recently enriched with academic honorifics, dropping/withdrawal roots, dean's list awards, and promissory notes such as karim/kari, panagikkat, and panagabak. Every entry separates Native_Aliases from Semantic_Aliases and follows Constantino, Rubino, Vanoverbergh, Ballard, and SIL Philippines—achieving 0.0% false-positive regional detections.

## Slide 11

[Speaker 3: Earold Delin | Target: 0:50]
Slide 11 displays five representative rows from data/expanded/slu_car_domain_lexicon_v2.csv. Each record encodes Entry_ID, normalized lemma, ISO 639-3 tag, part of speech, morphological root and affix, English/Filipino glosses, separated alias columns, and intent mappings—from SLU academic acronyms like samcis and niche Handbook terms like summa_cum_laude, to Ilocano agadal (ag- + adal), Kankanaey inayan, Ibaloi tongtong mediation, and the distinctive Ibaloi sh- cognate shanom. I will now hand it over to Erick Sibayan for our balanced corpus and ML evaluation.

## Slide 12

[Speaker 4: Erick Sibayan | Target: 0:55]
Thank you, Earold. Slide 12 details our expanded 350-document multi-layer corpus built for statistically sound 5-Fold Cross-Validation. Every one of our 10 operational intent domains contains exactly 35 balanced documents and 5 to 6 official SLU policies. Across registers, we cover 151 English, 109 Taglish, and 90 Cordilleran code-switched utterances. Every row preserves honest Source_Type provenance: 52 verified SLU policies, 4 URO FAQs, 4 #SLUFreedomWall posts, and 290 curated multilingual queries.

## Slide 13

[Speaker 4: Erick Sibayan | Target: 1:00]
Slide 13 reports our pure-Python Supervised Intent Classification benchmarks under leak-free Stratified 5-Fold CV with fold-local sublinear TF-IDF (1 + log tf). Look closely: after adopting sublinear TF scaling across our expanded 350-doc dataset, One-vs-Rest Linear SVM with Hinge Loss emerged as our Best Model at 95.43% accuracy and 95.43% Macro F1! Multinomial Naive Bayes and L2 Logistic Regression both tied tightly at 94.86% accuracy and 94.89% Macro F1. Sublinear TF prevents repeated policy phrases from skewing decision margins between closely related Handbook sub-rules.

## Slide 14

[Speaker 4: Erick Sibayan | Target: 0:55]
Slide 14 shows the 10-by-10 out-of-fold confusion matrix for our winning Linear SVM classifier across all 350 documents. Out of 350 unseen fold predictions, 334 (95.43%) sit cleanly on the green main diagonal, with both Shifting and Facilities & Labs achieving a spotless 35 out of 35, and Health, Exam Integrity, Grading/FDA, and Subject Adjustment scoring 34 out of 35! Only subtle cross-office ambiguities remain—such as tuition refund adjustments overlapping Finance and Subject Adjustment—which our hybrid policy ranker resolves cleanly.

## Slide 15

[Speaker 4: Erick Sibayan | Target: 1:00]
Slide 15 shows how our hybrid ranking and ML upgrades work together inside slu_chatbot_engine.py. We paired sublinear TF-IDF cosine similarity and moderated lexicon intent boosting with probabilistic multi-intent ML routing—converting One-vs-Rest Linear SVM hinge margins via softmax so any candidate class above 0.16 receives calibrated support. For two-part questions using comparative markers like 'vs' or 'difference between', the engine synthesizes the primary and secondary policies together, reinforced by numeric and Handbook phrase anchors for 88/91/93 Latin honors, 11th MWF / 8th TTh absence ceilings, and OSAS Readmission Slips. Passing to John Andrew Angcaway for ablations and live niche demos.

## Slide 16

[Speaker 5: John Andrew Angcaway | Target: 1:00]
Thank you, Erick. Slide 16 reports our 4-stage ablation on 75 strictly unseen queries (69 in-domain plus 6 OOD traps and greetings, with zero training overlap). Stage A raw TF-IDF starts at 84.1% Top-1 and 0% OOD rejection. Stage B cleaning and CAR morphology raises Top-1 to 87.0% and 0.932 MRR. Stage C adds our 176-entry lexicon and calibrated OOD gate—OOD rejection jumps immediately to 100.0% at 88.4% Top-1. Finally, Stage D fuses trained SVM routing, leaping +10.2 points to 98.6% Top-1 (68/69), 100.0% Top-3 recall, 0.9928 MRR, 100% EN/Taglish, 96.3% CAR, and 0.0% false-positive CAR!

## Slide 17

[Speaker 5: John Andrew Angcaway | Target: 1:00]
Slide 17 covers production engineering in our redesigned Canva EAG-QJ6Vos4 graph-paper web portal. Security first: zero .innerHTML assignments across all dynamic views, safe textContent DOM nodes, strict CSP headers in netlify.toml, and verified defense against live XSS payloads. Second, single-source Py-to-JS parity: scripts/build_portal.py compiles the exact 52 policies, 176 lexicon entries, and SVM/NB weights directly into JS, verified across all 78 test cases in Node.js and Python. Third, both Light Cream Graph Paper and Dark Neon-Glow modes preserve WCAG 2.1 AA contrast and full keyboard ARIA tablists.

## Slide 18

[Speaker 5: John Andrew Angcaway | Target: 0:55]
Slides 18 and 19 showcase the exact high-demand niche SLU policies added to our engine. On Slide 18, Case 1 asks directly: 'What are the specific grades you need for Latin honors?' Our hybrid engine routes to HANDBOOK_GRADING_FDA Doc 133: Summa Cum Laude requires a GWA of 93% or higher with no grade below 85%; Magna Cum Laude requires 91.00% to 92.99% with no grade below 80%; and Cum Laude requires 88.00% to 90.99% with no grade below 78%—plus zero failures or drops and at least 75% residency at SLU. Case 2 asks: 'How many absences do I have before I become dropped vs. permanently dropped?' Comparative synthesis clearly separates voluntary official dropping (WP/DRP before finals, non-failing) from permanent Failure Due to Absences—exceeding 20% of 54 semester hours (11th absence on MWF or 8th on TTh)—plus the 3-consecutive-absence OSAS Readmission Slip.

## Slide 19

[Speaker 5: John Andrew Angcaway | Target: 0:55]
Slide 19 continues with regional Cordilleran code-switching and out-of-domain safety. Case 3 tests Northern Kankanaey academic integrity: 'Gawis ay agsapa! Inayan ti plagiarism ken cheating, ania parusa?' Our engine detects genuine native Kankanaey roots, replies 'Gawis ay agew!', and retrieves Article II Disciplinary Board sanctions—while an English-only plagiarism query suppresses regional greetings cleanly (0% FP-CAR). Case 4 demonstrates our OOD gate on 'Baguio strawberry sinigang', returning zero hallucination and guiding students to URO and OSAS contacts.

## Slide 20

[Speaker 5: John Andrew Angcaway | Target: 0:50]
Slide 20 shares our honest provenance and RA 10173 Data Privacy compliance. All 290 synthetic utterances in annotated_corpus_expanded.csv are transparently tagged CURATED_MULTILINGUAL_INQUIRY rather than claiming they were live-scraped, and formal validation with native Ilocano, Northern Kankanaey, and Ibaloi speakers is Milestone 1 of our roadmap. For RA 10173 compliance, zero student names, IDs, or private identifiers are collected, and 100% client-side browser inference ensures student questions never leave their device. Back to Chaze!

## Slide 21

[Speaker 1: Chaze Rodriguez | Target: 0:45]
Thank you, John Andrew. Slide 21 outlines our three-step roadmap beyond CSE 30. Step 1 partners with native CAR linguists and SLU student organizations to validate idioms, diacritics, and expand toward Bontok and Ifugao. Step 2 benchmarks compact multilingual sentence embeddings like mE5 and LaBSE paired with strict Handbook-grounded RAG that never fabricates citations. Step 3 connects live iSLU enrollment calendars, OSAS advisories, and official URO ticketing queues.

## Slide 22

[Speaker 1: Chaze Rodriguez & All Members | Target: 0:45]
To close on Slide 22: Group 2 AiNomally delivered an audited, security-hardened, Canva graph-paper SLU eGovernance ecosystem. From 350 balanced documents, 52 verified SLU policies, and 176 CAR lexicon entries to 95.43% 5-Fold CV Macro F1, 98.6% unseen Top-1 accuracy, 100% OOD safety, and 22 passing automated tests across Python and Node.js—every claim is deterministically reproducible. Agyamanak! Iyaman! Dakel a iyaman! Scan the QR code to try the live portal, and we welcome your questions!
