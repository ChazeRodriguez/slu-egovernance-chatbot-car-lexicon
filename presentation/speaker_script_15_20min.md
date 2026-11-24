# Group 2 – AiNomally | CSE 30 Complete Project Presentation Script (15–20 Minutes)

**Course:** CSE 30 – CS Special Topics (Natural Language Processing)  
**Institution:** Saint Louis University (SAMCIS – Department of Computer Science), Baguio City  
**Instructor:** Prof. Dalos D. Miguel  
**Total Target Delivery Time:** ~18.5 minutes + Q&A (18 slides, evenly balanced across all 5 members ~3.5 min each)
**Total Spoken Word Count:** 2,544 words (~18.8 minutes at 135 wpm + live Q&A)

| Speaker | Slides Covered | Target Time |
|---|---|---|
| **Chaze Ezkys M. Rodriguez** | Slides 1–3, 16–18 | ~6:15 (Intro + Demo/Close) |
| **Keith Russel Hernandez** | Slides 4–6 | ~3:30 |
| **Earold Jan Delin** | Slides 7–9 | ~3:30 |
| **Erick James Sibayan** | Slides 10–12 | ~4:00 |
| **John Andrew Angcaway** | Slides 13–15 | ~3:30 |

---

## Slide 1

[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 0:45]
Good afternoon, Professor Dalos Miguel, and fellow Louisians. We are Group 2, AiNomally—composed of John Andrew Angcaway, Earold Jan Delin, Keith Russel Hernandez, Erick James Sibayan, and myself, Chaze Rodriguez. Today we present our complete CSE 30 NLP Term Project: a Multilingual Domain-Specific Electronic Lexicon, Supervised Intent Classifier, and Hardened eGovernance Student Support Chatbot built specifically for Saint Louis University in Baguio City. Over the next 18 minutes, we will walk you through our journey from raw data collection and Midterm audit verification all the way to our Finals expansion—scaling to 250 balanced documents, 156 SLU and Cordilleran lexicon entries, leak-free 5-fold cross-validated machine learning models, and a security-hardened interactive web portal.

## Slide 2

[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:15]
Let us begin with why this project matters here in Baguio City and the Cordillera Administrative Region. We are tackling two intersecting challenges simultaneously. On the institutional side, Saint Louis University serves tens of thousands of students, yet critical policies—ranging from URO transcript requests and shifting rules to 20 percent Failure Due to Absences thresholds, exam permits, clinic clearances, and financial aid—are fragmented across static PDF handbooks, separate office webpages, and informal public forums like the SLU Freedom Wall. Students routinely rely on unverified peer advice because standard English keyword searches fail when queries mix Taglish clitics like 'ngaun' or 'dp' with local expressions. On the linguistic side, regional CAR languages—specifically Ilocano, Northern Kankanaey, and Ibaloi—face severe digital resource scarcity. By embedding authentic Cordilleran vocabulary directly into an institutional eGovernance chatbot, we make campus services more accessible while preserving local languages in active computational infrastructure.

## Slide 3

[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:00]
Our design aligns directly with both tracks of the CSE 30 term project requirements. Under Track A, we engineered a machine-readable electronic lexicon linking SLU institutional acronyms and campus Taglish with validated Ilocano, Northern Kankanaey, and Ibaloi lemmas, complete with ISO 639-3 tags, parts of speech, morphological roots, and bilingual glosses. Under Track B, we built an end-to-end eGovernance chatbot application capable of resolving multilingual student questions against verified SLU regulations. To accomplish this rigorously, we committed to four engineering objectives: first, a single-command reproducible local pipeline; second, test-driven bug and security hardening; third, scaling our CAR lexicon and balanced corpus with transparent provenance; and fourth, empirical benchmarking via leak-free Stratified 5-Fold Cross-Validation and held-out retrieval ablations. I will now turn the floor to Keith to present our system architecture, corpus scaling, and data audit.

## Slide 4

[Speaker 2: Keith Russel Hernandez | Target: 1:15]
Thank you, Chaze. Slide 4 shows our complete five-stage deterministic NLP architecture. Everything starts in Stage 1 with multi-source data acquisition: harvesting authentic #SLUFreedomWall posts via slu_web_scraper.py and verifying official SLU policy provisions directly from slu.edu.ph, dataprotection.slu.edu.ph, and the 2015 Student Handbook. In Stage 2, data_cleaning.py executes acronym-safe normalization without deleting parenthetical acronyms like SAMCIS or TOR. Stage 3 runs car_morphology.py and data_preprocessing.py for guarded English, Filipino, and CAR lemmatization and bigram extraction. Stage 4 trains our zero-dependency pure-Python supervised classifiers—Multinomial Naive Bayes, Logistic Regression, and Linear SVM—and feeds serialized model weights into our hybrid retrieval engine alongside our 156-entry lexicon. Finally, Stage 5 uses build_portal.py as a single source of truth to inject verified JSON data and model weights directly into our 4-tab web portal and Netlify deployment bundle, eliminating manual drift across files.

## Slide 5

[Speaker 2: Keith Russel Hernandez | Target: 1:15]
Moving to Slide 5, you can see the quantitative leap from our Midterm baseline to our Finals expansion. Our Midterm baseline established 24 consolidated documents, 12 authoritative policies, and 25 lexicon entries—which was great for a proof of concept, but left zero authoritative policy coverage for Tuition/Finance or Campus Facilities/Labs, and had only two CAR-tagged posts. For Finals, we expanded authoritative SLU policies from 12 to 32 verified provisions covering all 10 operational intents, including Finance payment channels, SLU Entrance and Academic Scholarships, Center for Counseling and Wellness support, and Msgr. Charles Vath University Libraries borrowing rules. We scaled the annotated corpus over tenfold to 250 perfectly balanced documents—25 per intent—with 40.4% English, 31.6% Taglish, and 28.0% authentic CAR-TL-EN inquiries, all transparently labeled by Source_Type provenance.

## Slide 6

[Speaker 2: Keith Russel Hernandez | Target: 1:00]
One of the most valuable CS engineering practices we applied was an unbiased end-to-end data audit across our local files and Google Drive deliverables. Before scaling up, we ran automated reproducibility checks and uncovered six real discrepancies that could have compromised our defense. Our earlier paper and script still reported 352 stems and 9 occurrences of 'semester' when the verified corpus actually had 426 unique stems and 8 occurrences of 'semester'. Two bigrams—'bonifacio campus' and 'minimum grade'—were mistakenly listed with frequency 2 when both occurred once. Doc 6 was labeled #25582 instead of its real raw post ID #25604, and the Google Sheet still contained uncleaned Prelim rows. We fixed every single mismatch, synced Drive and Sheets, and built build_all.py so one command regenerates and tests every artifact with zero discrepancies. Next, Earold will detail our cleaning and morphological engineering.

## Slide 7

[Speaker 3: Earold Jan Delin | Target: 1:15]
Thank you, Keith. Slide 7 highlights how we engineered and hardened Stage 2—our deterministic acronym-safe text cleaner in data_cleaning.py. Standard regex cleaning pipelines often strip all parenthetical text, which would wipe out vital SLU identifiers like SAMCIS, TOR, COG, MLS, QE, FDA, and PATHFIT. Our targeted timestamp filter strips only scrape metadata while protecting every acronym. During our Phase 2 hardening audit, we caught and fixed five subtle real-world defects shown in this transformation table: replacing naive '\bill\b' so 'I am feeling ill' is never corrupted to 'i am feeling i will' while 'ill still answer' still expands properly; stripping possessive apostrophe-s cleanly so 'SLU's Registrar's Office' does not turn into 'slu is registrar is office'; preserving question marks when collapsing '??'; adding 'niyo' to 'ninyo' and arbitrary laughter collapse; and protecting hyphenated Cordilleran lemmas like 'dap-ay' and 'man-obla' so they survive tokenization intact.

## Slide 8

[Speaker 3: Earold Jan Delin | Target: 1:15]
On Slide 8, we address one of the hardest challenges in Philippine NLP: bilingual and Cordilleran morphological analysis. In our early Prelim prototype, unguarded prefix and suffix stripping severely damaged English words—turning 'campus' into 'campu', 'department' into 'depart', and 'management' into 'nage'. Even with a basic prefix guard, unseen words like 'magnify', 'magician', 'magical', and Tagalog 'maganda' still got corrupted because they start with 'mag-'. In car_morphology.py, we solved this with a three-layer architecture: first, a verified English, Filipino, and CAR lemma lookup covering infixed verbs like 'tumataas' to 'taas' and 'sumulat' to 'sulat'; second, explicit English root exceptions plus suffix guards blocking Filipino prefix stripping on Latinate words; and third, clean Austronesian affix normalization across Tagalog mag-/nag-/pag-, Ilocano ag-/panag-/na-, Kankanaey man-/men-, and Ibaloi ma-/man-.

## Slide 9

[Speaker 3: Earold Jan Delin | Target: 1:00]
Slide 9 presents our verified Midterm lexical profiling chart generated directly from corpus_bow_summary.csv and preprocessed_tokens.json. Across all 24 consolidated Midterm documents, filtering 265 English and Filipino stopwords yields exactly 624 content tokens, 457 unique surface forms, and 426 unique verified stems—a type-token ratio of 0.6827 with zero corrupted roots. Institutional terms clearly lead the vocabulary: 'student' appears 16 times at 2.56% coverage, followed by 'slu' at 10, 'examination' at 9, 'semester' at 8 highlighted in gold, and 'grade', 'requirement', and 'subject' at 7 each. On the right, we verified all 19 truly recurring contiguous bigrams such as 'official transcript', 'qualifying examination', 'student portal', 'failure due', and 'examination permit'—removing stale singleton claims. I now hand the presentation to Erick for our expanded CAR lexicon, annotations, and supervised machine learning benchmarks.

## Slide 10

[Speaker 4: Erick James Sibayan | Target: 1:30]
Thank you, Earold. Slide 10 showcases our flagship Track A contribution: scaling the SLU and CAR Multilingual Electronic Lexicon from 25 baseline items to 156 verified entries—comprising 36 SLU institutional acronyms and Taglish terms, 48 Ilocano entries, 40 Northern Kankanaey entries, and 32 Ibaloi entries grounded in Constantino, Rubino, Vanoverbergh, Ballard, and SIL Philippines dictionaries. Notice the linguistic richness captured here: look at the cognate row for 'water'—Ilocano 'danum', Kankanaey 'danom', and Ibaloi 'shanom', reflecting Ibaloi's signature postalveolar shift. Equally important, we preserve deeply cultural Cordilleran governance concepts: Kankanaey 'inayan' (ethical restraint against wrongdoing), 'dap-ay' (communal council), 'ubbo' (mutual cooperative work), and Ibaloi 'tongtong' (customary dispute mediation). Crucially, we architected separate Native_Aliases and Semantic_Aliases columns so English synonyms assist policy retrieval without ever falsely triggering indigenous language greetings.

## Slide 11

[Speaker 4: Erick James Sibayan | Target: 1:00]
On Slide 11, we detail the multi-layer annotation schema behind our 250-document Finals corpus. Every single document is tagged across four transparent dimensions: one of 10 balanced operational intent classes with exactly 25 documents each; sentiment and urgency polarity distinguishing authoritative policy from neutral inquiries and urgent student grievances; code-switching register across EN, TL-EN, and CAR-TL-EN; and an explicit Source_Type provenance tag separating official SLU policies, harvested Freedom Wall threads, and curated multilingual benchmark utterances. Ensuring 25 examples per class across all 10 intents is what makes rigorous Stratified 5-Fold Cross-Validation mathematically valid—giving every single validation fold exactly 5 unseen samples per intent class.

## Slide 12

[Speaker 4: Erick James Sibayan | Target: 1:30]
Slide 12 presents the centerpiece of our supervised NLP experiments. We implemented three classic text classifiers completely from scratch in zero-dependency pure Python—Multinomial Naive Bayes with Lidstone smoothing, L2-regularized Multinomial Logistic Regression, and One-vs-Rest Linear SVM—and benchmarked them via leak-free Stratified 5-Fold Cross-Validation where TF-IDF vocabularies and IDF weights are fitted strictly inside each training fold. As shown on the left chart, all three models achieve strong generalization over 10 multilingual classes: Multinomial Naive Bayes leads with 95.60% Accuracy and 95.61% Macro F1 plus-or-minus 1.47%; Logistic Regression follows closely at 95.18% Macro F1 with the lowest cross-fold variance at 0.90%; and Linear SVM scores 93.97% Macro F1. On the right, the 10-by-10 confusion matrix confirms crisp diagonal precision—achieving perfect 25-of-25 recall on Shifting, Facilities/Labs, and Tuition/Finance, with only 11 minor misclassifications across all 250 out-of-fold predictions. Next, John Andrew will present our hybrid retrieval engine, ablation findings, and security engineering.

## Slide 13

[Speaker 5: John Andrew Angcaway | Target: 1:15]
Thank you, Erick. Slide 13 explains how we combined our supervised Naive Bayes classifier, 156-entry lexicon, and TF-IDF cosine engine into a hardened hybrid retrieval architecture—and the real bugs we eliminated through Test-Driven Development. In our earlier prototype, asking plain English 'What is the punishment for plagiarism?' triggered a false-positive Kankanaey greeting because 'plagiarism' was mixed into 'inayan's' alias list, and gibberish queries silently hallucinated Freedom Wall Doc 1 as an official SLU policy. We wrote 12 failing regression tests first, then implemented four core safeguards: native-only CAR greeting triggers; a calibrated out-of-domain confidence gate plus conversational greeting handler; numeric policy anchoring so asking 'What happens if I get 74?' retrieves the 75% passing grade rule instead of dropping subjects; and moderated lexicon boosting so holistic Naive Bayes intent leads whenever a student mentions entities from two different offices in one sentence.

## Slide 14

[Speaker 5: John Andrew Angcaway | Target: 1:15]
Slide 14 shows the empirical payoff in our 4-Stage Held-Out Retrieval Ablation Study across 48 strictly unseen queries with zero text overlap against our 250-document training corpus—covering 42 in-domain multilingual queries, 4 OOD traps, and 2 greetings. Look at the compelling scientific story in the chart. Stage A, Raw TF-IDF Cosine alone, scores 83.3% Top-1 accuracy, 0.893 MRR, and 0% OOD rejection because it hallucinates on gibberish. Stage B adds acronym-safe cleaning and CAR morphology, jumping nearly 10 percentage points to 92.9% Top-1 and 0.960 MRR. Stage C adds our 156-entry lexicon and OOD gate—pushing OOD rejection from 0% to 100%, but revealing an honest trade-off: greedy single-keyword rules slightly dipped Top-1 to 90.5% on multi-entity queries like RFID validation after paying tuition. Stage D, our Full Hybrid adding the trained Naive Bayes classifier, resolves those multi-entity collisions to achieve the highest overall result: 95.2% Top-1 Policy Accuracy, 97.6% Top-3 Recall, 0.9643 MRR, 100% OOD Rejection, and 0.0% False-Positive CAR greetings.

## Slide 15

[Speaker 5: John Andrew Angcaway | Target: 1:00]
On Slide 15, we highlight the software engineering and security hardening that transforms this from a classroom script into a production-grade eGovernance portal. First, during our security audit we spotted DOM XSS where raw user queries were inserted via .innerHTML; we eliminated every single .innerHTML call in favor of safe DOM node construction and textContent, added strict Content-Security-Policy headers and dist/netlify.toml security headers, and capped input lengths. Second, we eliminated Python-versus-JavaScript drift by compiling verified JSON data and trained Naive Bayes weights directly from build_portal.py—and verified 100% identical outputs across all 51 held-out and XSS test queries by running the HTML portal's actual JavaScript inside Node.js against Python. Third, the 4-tab portal meets WCAG 2.1 AA standards with ARIA tablists, arrow-key navigation, aria-live regions, and mobile-to-desktop responsiveness. I will now turn it back to Chaze for our live walkthrough, limitations, and closing.

## Slide 16

[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:30]
Thank you, John Andrew. On Slide 16, let us walk through four live multilingual query traces from our 4-tab interactive portal—and if time permits during Q&A, we can also open the live portal directly. First, a Taglish shifting query from SAMCIS to SEAIT cleanly normalizes acronyms, predicts ACADEMIC_SHIFTING_TRANSFER, and returns both internal shifting guidelines and Qualifying Examination rules with direct slu.edu.ph links. Second, an Ilocano-Taglish query—'Naimbag a bigat! Agadal ak idiay SAMCIS—mano a porsiento ti absent sakbay ma-FDA?'—recognizes native Ilocano lemmas, replies with a genuine Ilocano greeting, and cites Handbook Article I, Section 2's 20% FDA threshold. Third, a Kankanaey query using 'Gawis ay agsapa! Inayan ti plagiarism' retrieves Handbook Article II, Section 4 on academic dishonesty. Finally, an out-of-domain trap asking for a Baguio strawberry sinigang recipe is safely caught by our confidence gate with an honest redirect to URO, OSAS, Finance, Clinic, and Security offices—zero hallucination.

## Slide 17

[Speaker 1: Chaze Ezkys M. Rodriguez | Target: 1:00]
In the spirit of rigorous academic honesty, Slide 17 outlines our project's current limitations, data privacy safeguards, and next-step roadmap. First, regarding provenance: while our 32 SLU policies and harvested Freedom Wall threads are primary institutional and community texts, the 210 expanded multilingual training utterances are transparently flagged as curated benchmark examples; a critical next step before campus-wide rollout is formal validation with native Ilocano, Northern Kankanaey, and Ibaloi speakers and linguists alongside anonymized real student chat logs. Second, under Republic Act 10173, our portal runs 100% client-side in the browser—meaning student questions never leave their device and zero personal identifiers are stored. Third, future iterations can extend our zero-dependency linear stack with lightweight multilingual dense embeddings and strictly policy-grounded retrieval-augmented generation.

## Slide 18

[All Members / Chaze Closing | Target: 0:45]
To conclude on Slide 18: Group 2 AiNomally delivered a fully reproducible, audited, security-hardened multilingual NLP ecosystem for Saint Louis University. From 250 balanced multi-layer annotated documents and 156 verified SLU and CAR lexicon entries to 95.61% Stratified 5-Fold CV Macro F1, 95.2% unseen Top-1 retrieval accuracy, 100% OOD safety, and 21 passing automated unit, classifier, parity, and security tests, every claim in our paper, spreadsheet, and web portal is backed by runnable code. All repository scripts, data, charts, and synced Google Drive deliverables are ready for inspection. Thank you very much, Professor Dalos Miguel and classmates—we are now open for your questions and live demo requests!
