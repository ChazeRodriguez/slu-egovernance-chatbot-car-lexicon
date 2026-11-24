# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/build_expanded_datasets.py
Description: Deterministically constructs and validates the Phase 3 Finals expanded datasets:
             1. data/expanded/slu_official_policies_v2.json (32 verified SLU policies across 10 intents)
             2. data/expanded/slu_car_domain_lexicon_v2.csv (156 validated SLU + Ilocano + Kankanaey + Ibaloi entries)
             3. data/expanded/annotated_corpus_expanded.csv (250 balanced docs: 25/intent across EN, TL-EN, CAR-TL-EN)
             4. data/expanded/heldout_benchmark.json (48 unseen multilingual, adversarial & OOD queries)
             Maintains transparent provenance tagging (Source_Type) and zero train/test text leakage.
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import csv
import json
import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
EXPANDED_DIR = os.path.join(REPO_ROOT, "data", "expanded")
sys.path.insert(0, SCRIPT_DIR)

from data_cleaning import clean_text

# ==============================================================================
# 1. VERIFIED SLU OFFICIAL POLICY KNOWLEDGE BASE (32 Provisions, 10 Intents)
#    Grounded in slu.edu.ph, dataprotection.slu.edu.ph, and SLU Student Handbook
# ==============================================================================

OFFICIAL_POLICIES_V2 = [
    # --- URO_ENROLLMENT_TOR (3) ---
    {
        "doc_id": 101,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO FAQ A2: Online TOR, COG & Clearance",
        "intent_label": "URO_ENROLLMENT_TOR",
        "raw_text": "Requests for Official Transcripts of Records (TOR), Certificates of Grades (COG), and Certificates of Graduation must be filed online through the URO Document Request portal. Clearance from the Accounting Department, Library Services, and Dean of Student Affairs must be completed before physical or electronic release.",
    },
    {
        "doc_id": 102,
        "source_file": "slu_osas_services.txt",
        "source_url": "https://www.slu.edu.ph/student-affairs/",
        "section_ref": "OSAS Guide: Certificate of Good Moral Character (CGMC)",
        "intent_label": "URO_ENROLLMENT_TOR",
        "raw_text": "Students and alumni requesting a Certificate of Good Moral Character (CGMC) for employment, board examinations, or transfer must file their application through the Office of Student Affairs and Services (OSAS) with a cleared disciplinary record and valid student or alumni identification.",
    },
    {
        "doc_id": 103,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO Records: Certified True Copies, Diploma & CAV",
        "intent_label": "URO_ENROLLMENT_TOR",
        "raw_text": "Certified true copies of diplomas, English medium of instruction certifications, honorable dismissal, and CHED Certification, Authentication, and Verification (CAV) packages are processed by the University Registrar's Office upon verification of cleared student ledgers and submission of documentary requirements.",
    },
    # --- URO_ENROLLMENT_PORTAL (3) ---
    {
        "doc_id": 104,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO FAQ A3: Continuing Enrollment & iSLU Portal Advising",
        "intent_label": "URO_ENROLLMENT_PORTAL",
        "raw_text": "Continuing undergraduate students must complete online advising of subjects through the SLU Student Portal (iSLU), settle the required downpayment through authorized payment partner banks or university cashiers, and finalize schedule confirmation within their assigned year-level enrollment window.",
    },
    {
        "doc_id": 105,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/admissions/",
        "section_ref": "SLU Admissions: Freshmen Enrollment & Orientation",
        "intent_label": "URO_ENROLLMENT_PORTAL",
        "raw_text": "Incoming freshmen admitted to Saint Louis University must submit original Senior High School Report Cards (Form 138), PSA Birth Certificate, Certificate of Good Moral Character, and medical clearance, complete the Center for Counseling and Wellness intake interview, and confirm enrollment via the iSLU portal.",
    },
    {
        "doc_id": 106,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO Registration: ID Validation & Enrollment Confirmation",
        "intent_label": "URO_ENROLLMENT_PORTAL",
        "raw_text": "After downpayment or tuition payment is posted to the student ledger, students must have their SLU RFID card validated at the University Library or designated validation stations before the registration period expires to confirm official enrolled status for the semester.",
    },
    # --- URO_SUBJECT_ADJUSTMENT (3) ---
    {
        "doc_id": 107,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO FAQ A4: Two-Week Subject Adding & Dropping",
        "intent_label": "URO_SUBJECT_ADJUSTMENT",
        "raw_text": "Adding or dropping of subjects is permitted only during the first two weeks of regular semesters upon submission of an accomplished Adjustment Form endorsed by the academic department chair and approved by the University Registrar.",
    },
    {
        "doc_id": 108,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO Policy: Official Subject Withdrawal (WP/DRP) & Dean Approval",
        "intent_label": "URO_SUBJECT_ADJUSTMENT",
        "raw_text": "Partial withdrawal or dropping of subjects must be filed for valid reasons within the official academic calendar using the Partial Withdrawal and Subject Adjustment Form with explicit approval from the School Dean. Stopping class attendance without official URO dropping results in failing marks.",
    },
    {
        "doc_id": 109,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO Policy: Subject Changing, Overload & Prerequisite Petitions",
        "intent_label": "URO_SUBJECT_ADJUSTMENT",
        "raw_text": "Requests to change class schedules, petition closed sections, or apply for graduating unit overloads must be endorsed by the Department Chair and School Dean prior to encoding at the University Registrar's Office during the designated adjustment window.",
    },
    # --- ACADEMIC_SHIFTING_TRANSFER (4) ---
    {
        "doc_id": 110,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/general-admission-requirements-and-enrollment/",
        "section_ref": "URO FAQ A1: Transferee Admission & Qualifying Exam (QE)",
        "intent_label": "ACADEMIC_SHIFTING_TRANSFER",
        "raw_text": "SLU admits transferees in undergraduate degree programs except Bachelor of Science in Medical Laboratory Science (MLS) and Bachelor of Science in Nursing (BSN), subject to compliance with pertinent guidelines. Transferees must undergo a Qualifying Examination (QE), personality evaluation, and dean interview, submitting an official TOR for evaluation, Honorable Dismissal, and PSA Birth Certificate.",
    },
    {
        "doc_id": 111,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/general-admission-requirements-and-enrollment/",
        "section_ref": "URO Policy: Transferee Academic Standing & Unit Limits",
        "intent_label": "ACADEMIC_SHIFTING_TRANSFER",
        "raw_text": "Transferee applicants must have no failing grades, non-passing marks, NFE, INC, or DROPPED marks from previous institutions, must not have attended more than two prior schools, and must not exceed 84 earned units for 4-year programs or 126 units for 5-year programs.",
    },
    {
        "doc_id": 112,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/registrars-office-services/",
        "section_ref": "URO & OSAS Policy: Internal Course Shifting Between SLU Schools",
        "intent_label": "ACADEMIC_SHIFTING_TRANSFER",
        "raw_text": "Current SLU students shifting across schools such as SAMCIS, SEAIT, SONAHBS, or STELA must accomplish the official shifting form, satisfy the target program's cut-off grades or qualifying examination, obtain approval from the accepting School Dean based on slot availability, and submit records to URO for subject crediting.",
    },
    {
        "doc_id": 113,
        "source_file": "slu_uro_enrollment_faqs.txt",
        "source_url": "https://www.slu.edu.ph/general-admission-requirements-and-enrollment/",
        "section_ref": "Program Screening: Allied Health & Specialized Transfer Cut-Offs",
        "intent_label": "ACADEMIC_SHIFTING_TRANSFER",
        "raw_text": "Specialized programs such as BS Pharmacy and BS Radiologic Technology require strict science screening with no failing marks in Mathematics, Physical Sciences, and Biological Sciences alongside a maintaining General Weighted Average (GWA) of at least 80 to 82 percent as determined by the accepting Dean.",
    },
    # --- HANDBOOK_GRADING_FDA (3) ---
    {
        "doc_id": 114,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. I, Sec. 1: Minimum Grade (75%) & Retention",
        "intent_label": "HANDBOOK_GRADING_FDA",
        "raw_text": "Saint Louis University operates under a standard numerical grading system from 75 to 99 percent. A grade of 75 is the minimum passing mark for any academic subject; grades below 75 indicate failure. For specialized degree programs under SAMCIS and SEAIT, higher retention grades may be mandated by the academic department.",
    },
    {
        "doc_id": 115,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. I, Sec. 2: Failure Due to Absences (FDA > 20%)",
        "intent_label": "HANDBOOK_GRADING_FDA",
        "raw_text": "Regular class attendance is required of all students. A student who incurs unexcused absences of more than 20 percent of the total class hours designated for a course during a term shall be automatically dropped from the course roll and given a grade of FDA (Failure Due to Absences).",
    },
    {
        "doc_id": 116,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Grading Rules: Incomplete (INC) & NFE Removal Period",
        "intent_label": "HANDBOOK_GRADING_FDA",
        "raw_text": "An Incomplete (INC) or No Final Examination (NFE) notation is granted only when a student holds satisfactory class standing but misses a major requirement or final exam for a valid documented reason. Students must complete INC requirements within the prescribed completion period following grade release or the grade converts to No Credit/Failure.",
    },
    # --- EXAM_PERMIT_INTEGRITY (3) ---
    {
        "doc_id": 117,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. II, Sec. 3: Examination Permits & Validated RFID",
        "intent_label": "EXAM_PERMIT_INTEGRITY",
        "raw_text": "Students are required to secure an official examination permit and present their validated SLU RFID card prior to taking Prelim, Midterm, and Final Examinations. Proctors reserve the right to bar any student from examination rooms without valid credentials.",
    },
    {
        "doc_id": 118,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. II, Sec. 4: Academic Integrity & Anti-Cheating",
        "intent_label": "EXAM_PERMIT_INTEGRITY",
        "raw_text": "Plagiarism, unauthorized collaboration, possession of unauthorized notes, use of mobile devices or cellphones during examinations, or contract cheating constitutes major academic dishonesty subject to suspension or dismissal under the SLU Disciplinary Board.",
    },
    {
        "doc_id": 119,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/student-affairs/",
        "section_ref": "OSAS Code of Conduct: Disciplinary Due Process & Sanctions",
        "intent_label": "EXAM_PERMIT_INTEGRITY",
        "raw_text": "Disciplinary infractions under the SLU Student Handbook are adjudicated through the Office of Student Affairs and Services (OSAS) and the SLU Disciplinary Board with formal due process, carrying graduated sanctions ranging from written warnings and reprimands to suspension or expulsion depending on offense gravity.",
    },
    # --- CAMPUS_DECORUM_DRESSCODE (3) ---
    {
        "doc_id": 120,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. III, Sec. 5: Prescribed Uniform & Wash Day Dress Code",
        "intent_label": "CAMPUS_DECORUM_DRESSCODE",
        "raw_text": "Students must strictly adhere to the university prescribed uniform code from Mondays to Thursdays. Modest civilian attire is permissible only during designated Wash Days on Fridays and Saturdays. Slippers, sandos, revealing attire, and apparel with obscene language are strictly forbidden within all SLU campus locations.",
    },
    {
        "doc_id": 121,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. III: Campus RFID Visibility & Gate Entry Protocol",
        "intent_label": "CAMPUS_DECORUM_DRESSCODE",
        "raw_text": "Every Louisian student must wear a validated SLU RFID identification card visibly upon entering Gates 1 and 2 and throughout all campus premises. Tampering with, lending, or borrowing another student's RFID card constitutes a disciplinary violation.",
    },
    {
        "doc_id": 122,
        "source_file": "slu_student_handbook_regulations.txt",
        "source_url": "https://www.slu.edu.ph/wp-content/uploads/2022/11/SLU-Student-Handbook-2015-Ed.pdf",
        "section_ref": "Handbook Art. III: Campus Decorum & Smoke-Free Environment",
        "intent_label": "CAMPUS_DECORUM_DRESSCODE",
        "raw_text": "Saint Louis University enforces respectful campus decorum, academic quiet zones, and a strict smoke-free, vape-free, and alcohol-free campus environment across Bonifacio, Maryheights, and Bakakeng campuses in compliance with university regulations and Baguio City ordinances.",
    },
    # --- CAMPUS_HEALTH_SAFETY (4) ---
    {
        "doc_id": 123,
        "source_file": "slu_safety_and_support_guide.txt",
        "source_url": "https://dataprotection.slu.edu.ph/guidelines-on-social-media-and-digital-platforms/",
        "section_ref": "Safety Guide Sec. 1: Digital Platforms, Anti-Libel & RA 10173",
        "intent_label": "CAMPUS_HEALTH_SAFETY",
        "raw_text": "The Louisian community is mandated to exercise caution and ethical judgment in using social media and digital platforms including university websites, SLU student portals, official email systems, and public online forums. Posting libelous remarks, unverified institutional rumors, cyberbullying or harassment, or violating Republic Act 10173 (Data Privacy Act of 2012) is subject to administrative sanctions.",
    },
    {
        "doc_id": 124,
        "source_file": "slu_safety_and_support_guide.txt",
        "source_url": "https://www.slu.edu.ph/health-services/",
        "section_ref": "Safety Guide Sec. 2: University Medical/Dental Clinic & PATHFIT",
        "intent_label": "CAMPUS_HEALTH_SAFETY",
        "raw_text": "The SLU Health Services Unit (University Clinic at Bonifacio and Maryheights campuses) provides emergency first aid, outpatient medical and nursing consultations, starter medicine doses, vaccinations, and routine dental checks. Annual medical exams and physical fitness certificates are mandatory for PATHFIT courses and laboratory practicums, and private physician excuse letters must be verified by the clinic.",
    },
    {
        "doc_id": 125,
        "source_file": "slu_safety_and_support_guide.txt",
        "source_url": "https://www.slu.edu.ph/",
        "section_ref": "Safety Guide Sec. 3: Baguio Seismic Evacuation & Gate Security",
        "intent_label": "CAMPUS_HEALTH_SAFETY",
        "raw_text": "In case of natural calamities or seismic earthquake events in Baguio City, students must execute Duck, Cover, and Hold and follow floor wardens toward designated open evacuation areas including the SLU Main Oval and open courts. Immediate security concerns or lost items should be reported to the Security Office located at Gate 1 and Gate 2.",
    },
    {
        "doc_id": 126,
        "source_file": "slu_safety_and_support_guide.txt",
        "source_url": "https://www.slu.edu.ph/center-for-counseling-and-wellness/",
        "section_ref": "CCW Policy: Center for Counseling and Wellness & Mental Health Support",
        "intent_label": "CAMPUS_HEALTH_SAFETY",
        "raw_text": "The SLU Center for Counseling and Wellness (CCW) provides confidential individual counseling in-person or via secure online video conferencing, psychological first aid, academic stress management, and anti-bullying advocacy. Students experiencing heavy workload anxiety or emotional distress may book sessions through CCW online intake or faculty/self-referral.",
    },
    # --- TUITION_FINANCE (3) ---
    {
        "doc_id": 127,
        "source_file": "slu_finance_guidelines.txt",
        "source_url": "https://www.slu.edu.ph/",
        "section_ref": "Finance Office: Authorized Tuition Payment Channels & Bank Posting",
        "intent_label": "TUITION_FINANCE",
        "raw_text": "Tuition fees and enrollment downpayments may be settled at university cashiers or through SLU authorized partner banks in Baguio City and La Trinidad via over-the-counter deposits or online mobile bills payment. Students must verify their enrollment ledger on iSLU and submit required proof of payment or accounting copies to the SLU Finance Office for posting.",
    },
    {
        "doc_id": 128,
        "source_file": "slu_finance_guidelines.txt",
        "source_url": "https://www.slu.edu.ph/",
        "section_ref": "Finance Office: Tuition Assessments, Adjustments & Financial Clearance",
        "intent_label": "TUITION_FINANCE",
        "raw_text": "The SLU Finance Office manages student billing, assessment adjustments after official adding or dropping of subjects, installment schedules prior to Prelim, Midterm, and Final exam permit issuance, and financial clearances required before transcript release or graduation.",
    },
    {
        "doc_id": 129,
        "source_file": "slu_finance_guidelines.txt",
        "source_url": "https://www.slu.edu.ph/scholarships/",
        "section_ref": "Finance & URO: SLU Scholarships, Dean's List Discounts & Grants",
        "intent_label": "TUITION_FINANCE",
        "raw_text": "SLU offers institutional tuition fee discounts including the SLU Entrance Scholarship for SHS Valedictorians and Salutatorians (via Finance Office), SLU Academic Scholarship for top-ranking Dean's Listers each semester, Activity and Service Grants (CCA Marching Band, Athletics, HRD Working Students), and external government scholarships such as CHED TES/PESFA, DOST, and Bukas Student Loans via the URO Government Scholarship Section.",
    },
    # --- CAMPUS_FACILITIES_LAB (3) ---
    {
        "doc_id": 130,
        "source_file": "slu_facilities_library_guide.txt",
        "source_url": "https://www.slu.edu.ph/university-libraries/",
        "section_ref": "University Libraries (UNL): Borrowing Privileges, Decorum & Fines",
        "intent_label": "CAMPUS_FACILITIES_LAB",
        "raw_text": "The SLU University Libraries (Msgr. Charles Vath Building and campus branches) provide print books, electronic research databases, and collaboration rooms upon presentation of a valid SLU RFID card. Undergraduates may borrow up to 3 books for 3 days while graduate students may borrow up to 5 books for 7 days; overdue fines and replacement liabilities apply to late, lost, or damaged library materials.",
    },
    {
        "doc_id": 131,
        "source_file": "slu_facilities_library_guide.txt",
        "source_url": "https://www.slu.edu.ph/",
        "section_ref": "Laboratory Operations: Safety Protocols, Consumables & Equipment Reporting",
        "intent_label": "CAMPUS_FACILITIES_LAB",
        "raw_text": "Students utilizing MLS, Science, Engineering, and Computing laboratories must wear prescribed laboratory coats and protective gear, follow biological and chemical disposal protocols, and formally report defective laboratory equipment, pipette or reagent shortages, or facility maintenance needs to the Laboratory Custodian and Department Chair.",
    },
    {
        "doc_id": 132,
        "source_file": "slu_facilities_library_guide.txt",
        "source_url": "https://www.slu.edu.ph/",
        "section_ref": "Campus IT & Support: iSLU Portal, Institutional Email & Wi-Fi Access",
        "intent_label": "CAMPUS_FACILITIES_LAB",
        "raw_text": "Enrolled Louisian students receive official SLU institutional email accounts and iSLU Student Portal credentials for academic advising, grade viewing, online learning platforms, and campus Wi-Fi access. Account lockouts, password resets, or laboratory workstation issues should be logged with SLU Information Technology support.",
    },
]

# ==============================================================================
# 2. SCALED 156-ENTRY MULTILINGUAL LEXICON (SLU + ILOCANO + KANKANAEY + IBALOI)
#    Format: (id, lemma, lang, pos, root, affix, en_gloss, fil_gloss, intent, native_aliases, semantic_aliases)
# ==============================================================================

EXPANDED_LEXICON_ROWS = [
    # --- SLU INSTITUTIONAL & CAMPUS TAGLISH (36 entries) ---
    ("SLU-001", "samcis", "en-SLU", "PROPN", "samcis", "Acronym", "School of Accountancy, Management, Computing and Information Studies", "Paaralan ng Accountancy Management Computing at Information Studies", "ACADEMIC_SHIFTING_TRANSFER", "samcis", ""),
    ("SLU-002", "seait", "en-SLU", "PROPN", "seait", "Acronym", "School of Engineering, Architecture, and Information Technology", "Paaralan ng Inhinyeriya Arkitektura at Teknolohiyang Pang-impormasyon", "ACADEMIC_SHIFTING_TRANSFER", "seait", "engineering|architecture"),
    ("SLU-003", "sonahbs", "en-SLU", "PROPN", "sonahbs", "Acronym", "School of Nursing, Allied Health, and Biological Sciences", "Paaralan ng Nursing Allied Health at Agham Biyolohikal", "ACADEMIC_SHIFTING_TRANSFER", "sonahbs", "nursing"),
    ("SLU-004", "stela", "en-SLU", "PROPN", "stela", "Acronym", "School of Teacher Education and Liberal Arts", "Paaralan ng Edukasyong Pangguro at Sining Liberal", "ACADEMIC_SHIFTING_TRANSFER", "stela", "liberal arts|education"),
    ("SLU-005", "sol", "en-SLU", "PROPN", "sol", "Acronym", "School of Law at Saint Louis University", "Paaralan ng Batas ng SLU", "ACADEMIC_SHIFTING_TRANSFER", "sol", ""),
    ("SLU-006", "som", "en-SLU", "PROPN", "som", "Acronym", "School of Medicine at Saint Louis University", "Paaralan ng Medisina ng SLU", "ACADEMIC_SHIFTING_TRANSFER", "som", ""),
    ("SLU-007", "mls", "en-SLU", "PROPN", "mls", "Acronym", "Bachelor of Science in Medical Laboratory Science (non-transferee program)", "Batsilyer ng Agham sa Medical Laboratory Science", "ACADEMIC_SHIFTING_TRANSFER", "mls|bmls", "medtech"),
    ("SLU-008", "bsn", "en-SLU", "PROPN", "bsn", "Acronym", "Bachelor of Science in Nursing (restricted transferee program)", "Batsilyer ng Agham sa Nursing", "ACADEMIC_SHIFTING_TRANSFER", "bsn", ""),
    ("SLU-009", "uro", "en-SLU", "PROPN", "uro", "Acronym", "University Registrar's Office", "Tanggapan ng Tagapagrehistro ng Unibersidad", "URO_ENROLLMENT_TOR", "uro", "registrar"),
    ("SLU-010", "osas", "en-SLU", "PROPN", "osas", "Acronym", "Office of Student Affairs and Services (formerly OSA)", "Tanggapan ng mga Gawaing Pang-estudyante", "EXAM_PERMIT_INTEGRITY", "osas|osa", "student affairs"),
    ("SLU-011", "ccw", "en-SLU", "PROPN", "ccw", "Acronym", "Center for Counseling and Wellness (Guidance and Mental Health)", "Sentro ng Pagpapayo at Kagalingan", "CAMPUS_HEALTH_SAFETY", "ccw", "guidance|counseling"),
    ("SLU-012", "unl", "en-SLU", "PROPN", "unl", "Acronym", "SLU University Libraries (Msgr. Charles Vath Building)", "Mga Aklatan ng Unibersidad", "CAMPUS_FACILITIES_LAB", "unl|vath", "library"),
    ("SLU-013", "islu", "en-SLU", "PROPN", "islu", "Acronym", "Official Saint Louis University Student Portal (iSLU)", "Opisyal na Portal ng Estudyante ng SLU", "URO_ENROLLMENT_PORTAL", "islu", "student portal"),
    ("SLU-014", "tor", "en-SLU", "NOUN", "tor", "Acronym", "Official Transcript of Records", "Opisyal na Talaan ng mga Marka", "URO_ENROLLMENT_TOR", "tor", "transcript|transcripts"),
    ("SLU-015", "cog", "en-SLU", "NOUN", "cog", "Acronym", "Certificate of Grades", "Katibayan ng mga Marka", "URO_ENROLLMENT_TOR", "cog", ""),
    ("SLU-016", "cgmc", "en-SLU", "NOUN", "cgmc", "Acronym", "Certificate of Good Moral Character issued by OSAS", "Katibayan ng Mabuting Asal", "URO_ENROLLMENT_TOR", "cgmc", "good moral"),
    ("SLU-017", "cav", "en-SLU", "NOUN", "cav", "Acronym", "CHED Certification, Authentication, and Verification of academic records", "Sertipikasyon at Beripikasyon ng CHED", "URO_ENROLLMENT_TOR", "cav", ""),
    ("SLU-018", "qe", "en-SLU", "NOUN", "qe", "Acronym", "Qualifying Examination for Transferees and Shiftees", "Pagsusulit sa Kwalipikasyon", "ACADEMIC_SHIFTING_TRANSFER", "qe", "qualifying"),
    ("SLU-019", "fda", "en-SLU", "NOUN", "fda", "Acronym", "Failure Due to Absences (exceeding 20 percent of class hours)", "Bagsak Dahil sa Pagliban", "HANDBOOK_GRADING_FDA", "fda", "absence|absences|absent"),
    ("SLU-020", "inc", "en-SLU", "NOUN", "inc", "Acronym", "Incomplete grade notation requiring timely removal", "Kulang na Marka na nangangailangan ng pagkumpleto", "HANDBOOK_GRADING_FDA", "inc", "incomplete"),
    ("SLU-021", "nfe", "en-SLU", "NOUN", "nfe", "Acronym", "No Final Examination grade notation", "Walang Pinal na Pagsusulit", "HANDBOOK_GRADING_FDA", "nfe", ""),
    ("SLU-022", "wp", "en-SLU", "NOUN", "wp", "Acronym", "Withdrawn with Permission official dropping notation", "Opisyal na Pag-alis sa Asignatura nang may Pahintulot", "URO_SUBJECT_ADJUSTMENT", "wp", ""),
    ("SLU-023", "drp", "en-SLU", "NOUN", "drp", "Acronym", "Dropped subject status recorded via URO adjustment", "Markang Dropped sa Asignatura", "URO_SUBJECT_ADJUSTMENT", "drp", ""),
    ("SLU-024", "gwa", "en-SLU", "NOUN", "gwa", "Acronym", "General Weighted Average used for honors, retention, and transfers", "Pangkalahatang Timbang na Marka", "HANDBOOK_GRADING_FDA", "gwa", ""),
    ("SLU-025", "pathfit", "en-SLU", "PROPN", "pathfit", "Acronym", "Physical Activity Towards Health and Fitness Course", "Asignaturang Edukasyong Pisikal at Kalusugan", "CAMPUS_HEALTH_SAFETY", "pathfit", "clinic|medical"),
    ("SLU-026", "nstp", "en-SLU", "PROPN", "nstp", "Acronym", "National Service Training Program (CWTS/ROTC/LTS)", "Programang Pambansang Pagsasanay sa Paglilingkod", "URO_ENROLLMENT_PORTAL", "nstp|cwts", ""),
    ("SLU-027", "ojt", "en-SLU", "NOUN", "ojt", "Acronym", "On-the-Job Training and Supervised Practicum", "Pagsasanay sa Aktwal na Trabaho", "CAMPUS_HEALTH_SAFETY", "ojt|practicum", ""),
    ("SLU-028", "rfid", "en-SLU", "NOUN", "rfid", "Acronym", "Validated SLU Radio-Frequency Identification Student Card", "Opisyal na ID Card ng Estudyante sa SLU", "EXAM_PERMIT_INTEGRITY", "rfid", "permit|permits"),
    ("SLU-029", "dpa", "en-SLU", "PROPN", "dpa", "Acronym", "Republic Act 10173 Data Privacy Act of 2012 compliance", "Batas sa Pagkapribado ng Datos", "CAMPUS_HEALTH_SAFETY", "dpa|ra10173", "data privacy"),
    ("SLU-030", "tes", "en-SLU", "PROPN", "tes", "Acronym", "CHED Tertiary Education Subsidy and external financial aid", "Tulong Pinansyal ng CHED para sa Kolehiyo", "TUITION_FINANCE", "tes|pesfa|dost", "scholarship"),
    ("SLU-031", "dp", "tl-SLU", "NOUN", "downpayment", "Abbreviation", "Required Enrollment Downpayment via SLU Portal or Partner Banks", "Paunang Bayad sa Matrikula", "TUITION_FINANCE", "dp|downpayment", "tuition"),
    ("SLU-032", "prelim", "en-SLU", "NOUN", "prelim", "Clipping", "Preliminary Examination grading period", "Unang Panahunang Pagsusulit", "EXAM_PERMIT_INTEGRITY", "prelim|prelims", ""),
    ("SLU-033", "midterm", "en-SLU", "NOUN", "midterm", "Compound", "Midterm Examination grading period", "Panggitnang Pagsusulit", "EXAM_PERMIT_INTEGRITY", "midterm|midterms", ""),
    ("SLU-034", "washday", "en-SLU", "NOUN", "washday", "Compound", "Designated Friday and Saturday modest civilian attire days", "Araw ng Sibil na Pananamit (Biyernes at Sabado)", "CAMPUS_DECORUM_DRESSCODE", "washday|wash", ""),
    ("SLU-035", "ambilat", "kne-tl", "ADJ", "bigat", "Phonetic_Variant", "Heavy emotional or academic workload burden (Baguio/Cordilleran variant of ambigat)", "Mabigat sa pakiramdam dahil sa sabay-sabay na pagsusulit", "CAMPUS_HEALTH_SAFETY", "ambilat|ambigat", ""),
    ("SLU-036", "louisian", "en-SLU", "NOUN", "louisian", "Demonym", "Member of the Saint Louis University academic community", "Kasapi ng komunidad ng Saint Louis University", "CAMPUS_DECORUM_DRESSCODE", "louisian|louisians", ""),

    # --- ILOCANO (ilo) — 48 verified entries (Constantino 1971; Rubino 2000) ---
    ("ILO-001", "naimbag", "ilo", "ADJ", "imbag", "na-", "Good; pleasant; courteous greeting in Ilocano student inquiries", "Mabuti; maganda", "CAR_REGIONAL_LEXICON", "naimbag", ""),
    ("ILO-002", "bigat", "ilo", "NOUN", "bigat", "Root", "Morning (used in 'naimbag a bigat' greeting)", "Umaga", "CAR_REGIONAL_LEXICON", "bigat", ""),
    ("ILO-003", "aldaw", "ilo", "NOUN", "aldaw", "Root", "Day; daytime; noon greeting", "Araw", "CAR_REGIONAL_LEXICON", "aldaw", ""),
    ("ILO-004", "malem", "ilo", "NOUN", "malem", "Root", "Afternoon (used in 'naimbag a malem')", "Hapon", "CAR_REGIONAL_LEXICON", "malem", ""),
    ("ILO-005", "rabii", "ilo", "NOUN", "rabii", "Root", "Evening; night (used in 'naimbag a rabii')", "Gabi", "CAR_REGIONAL_LEXICON", "rabii", ""),
    ("ILO-006", "agyamanak", "ilo", "INTJ", "yaman", "ag-...-ak", "Thank you; expression of gratitude in Ilocano", "Maraming salamat", "CAR_REGIONAL_LEXICON", "agyamanak|agyaman", ""),
    ("ILO-007", "kablaaw", "ilo", "NOUN", "kablaaw", "Root", "Formal greeting or salutation", "Pagbati", "CAR_REGIONAL_LEXICON", "kablaaw", ""),
    ("ILO-008", "agadal", "ilo", "VERB", "adal", "ag-", "To study; to pursue academic coursework at the university", "Mag-aral sa unibersidad", "URO_ENROLLMENT_PORTAL", "agadal|nagadal|panagadal|adal", ""),
    ("ILO-009", "pagadalan", "ilo", "NOUN", "adal", "pag-...-an", "School; university; place of learning", "Paaralan; unibersidad", "URO_ENROLLMENT_PORTAL", "pagadalan|eskuelaan", ""),
    ("ILO-010", "eskuela", "ilo", "NOUN", "eskuela", "Root", "School or class session", "Eskwela; paaralan", "URO_ENROLLMENT_PORTAL", "eskuela|skuela", ""),
    ("ILO-011", "maestro", "ilo", "NOUN", "maestro", "Root", "Teacher; professor; instructor", "Guro; propesor", "HANDBOOK_GRADING_FDA", "maestro|maestra|mannursuro", ""),
    ("ILO-012", "estudyante", "ilo", "NOUN", "estudyante", "Root", "Student; enrolled learner", "Estudyante; mag-aaral", "URO_ENROLLMENT_PORTAL", "estudyante|agdadamo", ""),
    ("ILO-013", "libro", "ilo", "NOUN", "libro", "Root", "Book; library textbook or reference volume", "Aklat; libro", "CAMPUS_FACILITIES_LAB", "libro|liblibro", ""),
    ("ILO-014", "agbasa", "ilo", "VERB", "basa", "ag-", "To read; to study library or handbook materials", "Magbasa", "CAMPUS_FACILITIES_LAB", "agbasa|nagbasa", ""),
    ("ILO-015", "agsurat", "ilo", "VERB", "surat", "ag-", "To write; to file a formal written application or petition", "Sumulat; maghain ng kahilingan", "URO_ENROLLMENT_TOR", "agsurat|nagsurat|isurat|surat", ""),
    ("ILO-016", "eksamen", "ilo", "NOUN", "eksamen", "Root", "Examination; academic test or qualifying exam", "Pagsusulit", "EXAM_PERMIT_INTEGRITY", "eksamen", ""),
    ("ILO-017", "grado", "ilo", "NOUN", "grado", "Root", "Academic grade or course mark", "Marka; grado", "HANDBOOK_GRADING_FDA", "grado", ""),
    ("ILO-018", "kurso", "ilo", "NOUN", "kurso", "Root", "Degree program or academic course", "Kurso; programa", "ACADEMIC_SHIFTING_TRANSFER", "kurso", ""),
    ("ILO-019", "klase", "ilo", "NOUN", "klase", "Root", "Class; scheduled course meeting", "Klase", "HANDBOOK_GRADING_FDA", "klase", ""),
    ("ILO-020", "agkiddaw", "ilo", "VERB", "kiddaw", "ag-", "To request; to formally apply for documents or certificates", "Humiling; mag-request ng dokumento", "URO_ENROLLMENT_TOR", "agkiddaw|kiddaw|kiddawen", ""),
    ("ILO-021", "agpalista", "ilo", "VERB", "lista", "agpa-", "To register; to enroll for a semester or subject", "Magpatala; mag-enroll", "URO_ENROLLMENT_PORTAL", "agpalista|palista|nagpalista", ""),
    ("ILO-022", "pirma", "ilo", "NOUN", "pirma", "Root", "Signature; official endorsement by Chair or Dean", "Lagda; pirma", "URO_SUBJECT_ADJUSTMENT", "pirma|agpirma", ""),
    ("ILO-023", "dokumento", "ilo", "NOUN", "dokumento", "Root", "Official academic or registrar document", "Dokumento", "URO_ENROLLMENT_TOR", "dokumento", ""),
    ("ILO-024", "tulong", "ilo", "NOUN", "tulong", "Root", "Assistance; student support or financial aid", "Tulong; suporta", "TUITION_FINANCE", "tulong|agtulong|tumulong", ""),
    ("ILO-025", "saludsod", "ilo", "NOUN", "saludsod", "Root", "Question; student inquiry", "Tanong; katanungan", "CAR_REGIONAL_LEXICON", "saludsod|agsaludsod", ""),
    ("ILO-026", "agsao", "ilo", "VERB", "sao", "ag-", "To speak; to inquire or communicate in Ilocano", "Magsalita; magtanong", "CAR_REGIONAL_LEXICON", "agsao|nagsao|sao", ""),
    ("ILO-027", "sungbat", "ilo", "NOUN", "sungbat", "Root", "Answer; official response or resolution", "Sagot; tugon", "CAR_REGIONAL_LEXICON", "sungbat|agsungbat", ""),
    ("ILO-028", "agdamag", "ilo", "VERB", "damag", "ag-", "To inquire; to ask for official information", "Magtanong; mag-usisa", "CAR_REGIONAL_LEXICON", "agdamag|damag", ""),
    ("ILO-029", "agbayad", "ilo", "VERB", "bayad", "ag-", "To pay tuition, downpayment, or campus fees", "Magbayad ng matrikula", "TUITION_FINANCE", "agbayad|nagbayad|bayadan", ""),
    ("ILO-030", "kuarta", "ilo", "NOUN", "kuarta", "Root", "Money; funds for tuition or fees", "Pera; salapi", "TUITION_FINANCE", "kuarta|kwarta", ""),
    ("ILO-031", "gatad", "ilo", "NOUN", "gatad", "Root", "Price; fee amount or tuition cost", "Halaga; bayarin", "TUITION_FINANCE", "gatad", ""),
    ("ILO-032", "utang", "ilo", "NOUN", "utang", "Root", "Unpaid balance or student loan obligation", "Utang; balanse", "TUITION_FINANCE", "utang", ""),
    ("ILO-033", "salun-at", "ilo", "NOUN", "salun-at", "Root", "Health; physical and mental wellness", "Kalusugan", "CAMPUS_HEALTH_SAFETY", "salun-at|salunat", ""),
    ("ILO-034", "sakit", "ilo", "NOUN", "sakit", "Root", "Illness; sickness requiring clinic consultation", "Sakit; karamdaman", "CAMPUS_HEALTH_SAFETY", "sakit|masakit", ""),
    ("ILO-035", "agas", "ilo", "NOUN", "agas", "Root", "Medicine; medical remedy provided at clinic", "Gamot", "CAMPUS_HEALTH_SAFETY", "agas", ""),
    ("ILO-036", "agpaagas", "ilo", "VERB", "agas", "agpa-", "To seek medical treatment or clinic consultation", "Magpagamot sa klinika", "CAMPUS_HEALTH_SAFETY", "agpaagas|nagpaagas", ""),
    ("ILO-037", "danum", "ilo", "NOUN", "danum", "Root", "Water; campus utility and sanitation resource", "Tubig", "CAMPUS_FACILITIES_LAB", "danum", ""),
    ("ILO-038", "gingined", "ilo", "NOUN", "gingined", "Root", "Earthquake; seismic event requiring Baguio evacuation drill", "Lindol", "CAMPUS_HEALTH_SAFETY", "gingined", ""),
    ("ILO-039", "bagyo", "ilo", "NOUN", "bagyo", "Root", "Typhoon; severe weather calamity affecting classes", "Bagyo", "CAMPUS_HEALTH_SAFETY", "bagyo", ""),
    ("ILO-040", "talna", "ilo", "NOUN", "talna", "Root", "Peace; safety; calm order on campus", "Kapayapaan; kaligtasan", "CAMPUS_HEALTH_SAFETY", "talna|natalna", ""),
    ("ILO-041", "bantay", "ilo", "NOUN", "bantay", "Root", "Guard; security personnel at campus gates", "Guwardiya; bantay", "CAMPUS_HEALTH_SAFETY", "bantay|agbantay", ""),
    ("ILO-042", "annad", "ilo", "NOUN", "annad", "Root", "Caution; carefulness in digital and campus safety", "Pag-iingat", "CAMPUS_HEALTH_SAFETY", "annad|agannad", ""),
    ("ILO-043", "linteg", "ilo", "NOUN", "linteg", "Root", "Law; university regulation or handbook rule", "Batas; alituntunin", "EXAM_PERMIT_INTEGRITY", "linteg|annuroten", ""),
    ("ILO-044", "bado", "ilo", "NOUN", "bado", "Root", "Clothing; university uniform or attire", "Damit; uniporme", "CAMPUS_DECORUM_DRESSCODE", "bado|pagbado", ""),
    ("ILO-045", "agsubli", "ilo", "VERB", "subli", "ag-", "To return; to return borrowed library books or re-enroll", "Bumalik; magbalik", "CAMPUS_FACILITIES_LAB", "agsubli|isubli", ""),
    ("ILO-046", "agbaliw", "ilo", "VERB", "baliw", "ag-", "To change or shift degree program or schedule", "Magpalit; lumipat ng kurso", "ACADEMIC_SHIFTING_TRANSFER", "agbaliw|agtransfer", ""),
    ("ILO-047", "idiay", "ilo", "ADV", "idiay", "Root", "There; at that place (e.g., idiay SAMCIS / idiay URO)", "Doon; sa", "CAR_REGIONAL_LEXICON", "idiay", ""),
    ("ILO-048", "kasano", "ilo", "ADV", "kasano", "Root", "How (Ilocano procedural interrogative)", "Paano", "CAR_REGIONAL_LEXICON", "kasano", ""),

    # --- NORTHERN KANKANAEY (kne) — 40 verified entries (SIL / Webonary / Cordilleran Studies) ---
    ("KNE-001", "gawis", "kne", "ADJ", "gawis", "Root", "Good; well; fine (Northern Kankanaey greeting and well-being marker)", "Mabuti; maayos", "CAR_REGIONAL_LEXICON", "gawis", ""),
    ("KNE-002", "inayan", "kne", "INTJ", "inayan", "Root", "Cordilleran ethical restraint against academic dishonesty, harm, or misconduct", "Katutubong konseptong moral laban sa pandaraya o masamang gawa", "EXAM_PERMIT_INTEGRITY", "inayan", "cheating|plagiarism|dishonesty"),
    ("KNE-003", "dap-ay", "kne", "NOUN", "dap-ay", "Root", "Indigenous communal council and peer consultation center", "Katutubong sentro ng sanggunian at talakayan", "EXAM_PERMIT_INTEGRITY", "dap-ay|dapay", ""),
    ("KNE-004", "man-obla", "kne", "VERB", "obla", "man-", "To work; to complete academic or laboratory tasks diligently", "Magtrabaho; gumawa ng gawain", "CAMPUS_FACILITIES_LAB", "man-obla|men-obla|manobla|obla", ""),
    ("KNE-005", "ubbo", "kne", "NOUN", "ubbo", "Root", "Mutual cooperative peer assistance and group study labor", "Bayanihan; tulungang paggawa", "CAMPUS_FACILITIES_LAB", "ubbo|ub-ubbo", ""),
    ("KNE-006", "binnadang", "kne", "NOUN", "badang", "binn-", "Communal helping and mutual student solidarity", "Pagtutulungan; bayanihan", "CAMPUS_HEALTH_SAFETY", "binnadang|badang", ""),
    ("KNE-007", "agsapa", "kne", "NOUN", "agsapa", "Root", "Morning (used in 'gawis ay agsapa')", "Umaga", "CAR_REGIONAL_LEXICON", "agsapa", ""),
    ("KNE-008", "masdem", "kne", "NOUN", "masdem", "Root", "Afternoon (used in 'gawis ay masdem')", "Hapon", "CAR_REGIONAL_LEXICON", "masdem", ""),
    ("KNE-009", "labi", "kne", "NOUN", "labi", "Root", "Evening; night (used in 'gawis ay labi')", "Gabi", "CAR_REGIONAL_LEXICON", "labi", ""),
    ("KNE-010", "agew", "kne", "NOUN", "agew", "Root", "Day; daytime (used in 'gawis ay agew')", "Araw", "CAR_REGIONAL_LEXICON", "agew", ""),
    ("KNE-011", "iyaman", "kne", "INTJ", "yaman", "i-", "Thank you; gratitude expression in Northern Kankanaey", "Salamat", "CAR_REGIONAL_LEXICON", "iyaman", ""),
    ("KNE-012", "entako", "kne", "VERB", "en", "en-tako", "Let us go (inclusive peer invitation)", "Tayo na", "CAR_REGIONAL_LEXICON", "entako", ""),
    ("KNE-013", "ngadan", "kne", "NOUN", "ngadan", "Root", "Name; student identification", "Pangalan", "URO_ENROLLMENT_PORTAL", "ngadan", ""),
    ("KNE-014", "ammo", "kne", "VERB", "ammo", "Root", "To know; knowledge or information", "Alam; kaalaman", "CAR_REGIONAL_LEXICON", "ammo|adak", ""),
    ("KNE-015", "man-adal", "kne", "VERB", "adal", "man-", "To study; to learn academic subjects", "Mag-aral", "URO_ENROLLMENT_PORTAL", "man-adal|men-adal", ""),
    ("KNE-016", "iskuela", "kne", "NOUN", "iskuela", "Root", "School; university campus", "Paaralan", "URO_ENROLLMENT_PORTAL", "iskuela", ""),
    ("KNE-017", "mensulat", "kne", "VERB", "sulat", "men-", "To write; to accomplish a written request or form", "Sumulat; magsulat", "URO_ENROLLMENT_TOR", "mensulat|mansulat|tudek", ""),
    ("KNE-018", "mensaludsod", "kne", "VERB", "saludsod", "men-", "To ask a question; to inquire at a university office", "Magtanong", "CAR_REGIONAL_LEXICON", "mensaludsod|saludsoden", ""),
    ("KNE-019", "menbayad", "kne", "VERB", "bayad", "men-", "To pay tuition fees or school assessment", "Magbayad", "TUITION_FINANCE", "menbayad|manbayad", ""),
    ("KNE-020", "menkiddaw", "kne", "VERB", "kiddaw", "men-", "To request documents, clearance, or permits", "Humiling ng dokumento", "URO_ENROLLMENT_TOR", "menkiddaw|mankiddaw", ""),
    ("KNE-021", "pilak", "kne", "NOUN", "pilak", "Root", "Money; tuition funds or payment", "Salapi; pera", "TUITION_FINANCE", "pilak", ""),
    ("KNE-022", "danom", "kne", "NOUN", "danom", "Root", "Water; campus laboratory and utility supply", "Tubig", "CAMPUS_FACILITIES_LAB", "danom", ""),
    ("KNE-023", "kapia", "kne", "NOUN", "kapia", "Root", "Peace; holistic well-being and safety", "Kapayapaan; kagalingan", "CAMPUS_HEALTH_SAFETY", "kapia|kappia", ""),
    ("KNE-024", "kinatalna", "kne", "NOUN", "talna", "kina-", "Safety; security; tranquility", "Kaligtasan; katiwasayan", "CAMPUS_HEALTH_SAFETY", "kinatalna", ""),
    ("KNE-025", "kinakamo", "kne", "NOUN", "kamo", "kina-", "Wellness; good health condition", "Kalusugan", "CAMPUS_HEALTH_SAFETY", "kinakamo", ""),
    ("KNE-026", "paniyew", "kne", "NOUN", "paniyew", "Root", "Sacred taboo or strict prohibition against wrongdoing", "Mahigpit na pagbabawal", "EXAM_PERMIT_INTEGRITY", "paniyew", ""),
    ("KNE-027", "turo", "kne", "NOUN", "turo", "Root", "Instruction; teaching or academic guidance", "Turo; pagtuturo", "HANDBOOK_GRADING_FDA", "turo|menturo", ""),
    ("KNE-028", "liblo", "kne", "NOUN", "liblo", "Root", "Book; library text or study material", "Aklat; libro", "CAMPUS_FACILITIES_LAB", "liblo", ""),
    ("KNE-029", "bado", "kne", "NOUN", "bado", "Root", "Attire; uniform or daily wear", "Damit; pananamit", "CAMPUS_DECORUM_DRESSCODE", "bado", ""),
    ("KNE-030", "yegyeg", "kne", "NOUN", "yegyeg", "Root", "Earthquake; tremor triggering campus evacuation", "Lindol", "CAMPUS_HEALTH_SAFETY", "yegyeg", ""),
    ("KNE-031", "udan", "kne", "NOUN", "udan", "Root", "Rain; inclement mountain weather in Baguio", "Ulan", "CAMPUS_HEALTH_SAFETY", "udan", ""),
    ("KNE-032", "dalan", "kne", "NOUN", "dalan", "Root", "Way; procedure; pathway or evacuation route", "Daan; proseso", "CAMPUS_HEALTH_SAFETY", "dalan", ""),
    ("KNE-033", "baey", "kne", "NOUN", "baey", "Root", "House; boarding home or campus building", "Bahay; gusali", "CAMPUS_FACILITIES_LAB", "baey", ""),
    ("KNE-034", "kasapulan", "kne", "NOUN", "sapul", "ka-...-an", "Requirement; essential needed document", "Pangangailangan; rekisito", "URO_ENROLLMENT_TOR", "kasapulan", ""),
    ("KNE-035", "ipapilit", "kne", "VERB", "pilit", "ipa-", "To mandate or require strictly under policy", "Ipag-utos; itakda", "CAMPUS_DECORUM_DRESSCODE", "ipapilit", ""),
    ("KNE-036", "nakdeng", "kne", "ADJ", "kedeng", "na-", "Finished; completed (e.g., completed clearance or work)", "Tapos na; nakumpleto", "URO_ENROLLMENT_TOR", "nakdeng", ""),
    ("KNE-037", "ad-ado", "kne", "ADJ", "ado", "CV-", "Many; numerous (e.g., many absences or deadlines)", "Marami", "HANDBOOK_GRADING_FDA", "ad-ado|ado", ""),
    ("KNE-038", "nasakit", "kne", "ADJ", "sakit", "na-", "Sick; painful; unwell requiring clinic care", "May sakit; masakit", "CAMPUS_HEALTH_SAFETY", "nasakit", ""),
    ("KNE-039", "men-enroll", "kne", "VERB", "enroll", "men-", "To enroll in university classes (Kankanaey-English blend)", "Mag-enroll", "URO_ENROLLMENT_PORTAL", "men-enroll|man-enroll", ""),
    ("KNE-040", "kaman", "kne", "ADV", "kaman", "Root", "How; like (used in Kankanaey procedural questions)", "Paano; tulad ng", "CAR_REGIONAL_LEXICON", "kaman|kaman-ano", ""),

    # --- IBALOI (ibl) — 32 verified entries (SIL / Ballard / Ibaloi Dictionary) ---
    ("IBL-001", "mapteng", "ibl", "ADJ", "peteng", "ma-", "Good; pleasant; well (Ibaloi campus greeting and welfare term)", "Mabuti; maganda; maayos", "CAR_REGIONAL_LEXICON", "mapteng", ""),
    ("IBL-002", "tongtong", "ibl", "NOUN", "tongtong", "Root", "Customary dispute resolution and disciplinary council mediation", "Katutubong paglilitis at pag-aayos ng sigalot", "EXAM_PERMIT_INTEGRITY", "tongtong", "disciplinary"),
    ("IBL-003", "shapa", "ibl", "NOUN", "shapa", "Root", "Morning (used in 'mapteng shapa')", "Umaga", "CAR_REGIONAL_LEXICON", "shapa", ""),
    ("IBL-004", "maabii", "ibl", "NOUN", "abii", "ma-", "Afternoon (used in 'mapteng maabii')", "Hapon", "CAR_REGIONAL_LEXICON", "maabii", ""),
    ("IBL-005", "malabi", "ibl", "NOUN", "labi", "ma-", "Evening; night (used in 'mapteng malabi')", "Gabi", "CAR_REGIONAL_LEXICON", "malabi", ""),
    ("IBL-006", "dakel", "ibl", "ADJ", "dakel", "Root", "Many; much (used in 'dakel a iyaman' — thank you very much)", "Marami; malaki", "CAR_REGIONAL_LEXICON", "dakel", ""),
    ("IBL-007", "shanom", "ibl", "NOUN", "shanom", "Root", "Water (Ibaloi sh- reflex of Cordilleran *danum)", "Tubig", "CAMPUS_FACILITIES_LAB", "shanom", ""),
    ("IBL-008", "kimey", "ibl", "NOUN", "kimey", "Root", "Work; labor; academic or laboratory task", "Trabaho; gawain", "CAMPUS_FACILITIES_LAB", "kimey|mankimey", ""),
    ("IBL-009", "man-obda", "ibl", "VERB", "obda", "man-", "To work; to perform academic or campus tasks", "Magtrabaho", "CAMPUS_FACILITIES_LAB", "man-obda|manobda|obda", ""),
    ("IBL-010", "isarong", "ibl", "VERB", "sarong", "i-", "To study; to attend and learn carefully", "Mag-aral", "URO_ENROLLMENT_PORTAL", "isarong|man-isarong", ""),
    ("IBL-011", "tulek", "ibl", "VERB", "tulek", "Root", "To write; written petition or registrar form", "Sumulat; kasulatan", "URO_ENROLLMENT_TOR", "tulek|mantulek", ""),
    ("IBL-012", "kali", "ibl", "NOUN", "kali", "Root", "Speech; language; oral inquiry or interview", "Wika; pananalita", "CAR_REGIONAL_LEXICON", "kali|mankalkali", ""),
    ("IBL-013", "kalinan", "ibl", "NOUN", "kalin", "-an", "Safety; peace; campus security", "Kaligtasan; katahimikan", "CAMPUS_HEALTH_SAFETY", "kalinan|katalna", ""),
    ("IBL-014", "baley", "ibl", "NOUN", "baley", "Root", "House; campus building or residence", "Bahay; gusali", "CAMPUS_FACILITIES_LAB", "baley", ""),
    ("IBL-015", "akad", "ibl", "VERB", "akad", "Root", "To walk; pedestrian evacuation movement", "Maglakad", "CAMPUS_HEALTH_SAFETY", "akad|man-akad", ""),
    ("IBL-016", "bain", "ibl", "NOUN", "bain", "Root", "Moral sense of shame/honor discouraging dishonesty or misconduct", "Hiya; dangal", "EXAM_PERMIT_INTEGRITY", "bain|mabain", ""),
    ("IBL-017", "en-ayos", "ibl", "ADJ", "ayos", "en-", "Well; in order (used in 'en-ayos ka kasi?' — how are you?)", "Maayos; mabuti", "CAR_REGIONAL_LEXICON", "en-ayos|enayos", ""),
    ("IBL-018", "afoy", "ibl", "NOUN", "afoy", "Root", "Fire; campus fire hazard or emergency safety", "Apoy", "CAMPUS_HEALTH_SAFETY", "afoy", ""),
    ("IBL-019", "shala", "ibl", "NOUN", "shala", "Root", "Blood; emergency first aid or medical lab specimen", "Dugo", "CAMPUS_HEALTH_SAFETY", "shala", ""),
    ("IBL-020", "makan", "ibl", "VERB", "kan", "ma-", "To eat; cafeteria/nutrition wellness", "Kumain", "CAMPUS_HEALTH_SAFETY", "makan", ""),
    ("IBL-021", "inom", "ibl", "VERB", "inom", "Root", "To drink; hydration and campus water stations", "Uminom", "CAMPUS_FACILITIES_LAB", "inom|man-inom", ""),
    ("IBL-022", "kala", "ibl", "VERB", "kala", "Root", "To come; to attend class or arrive at office", "Pumunta; dumating", "HANDBOOK_GRADING_FDA", "kala|makala", ""),
    ("IBL-023", "manbayad", "ibl", "VERB", "bayad", "man-", "To pay tuition or assessment fees", "Magbayad ng matrikula", "TUITION_FINANCE", "manbayad|ibayad", ""),
    ("IBL-024", "pagsurat", "ibl", "NOUN", "surat", "pag-", "Written application or formal filing at URO", "Pagsulat; aplikasyon", "URO_ENROLLMENT_TOR", "pagsurat", ""),
    ("IBL-025", "salun-at", "ibl", "NOUN", "salun-at", "Root", "Health and physical fitness for campus clinic & PATHFIT", "Kalusugan", "CAMPUS_HEALTH_SAFETY", "salun-at", ""),
    ("IBL-026", "pan-adal", "ibl", "NOUN", "adal", "pan-", "Education; university study program", "Pag-aaral; edukasyon", "URO_ENROLLMENT_PORTAL", "pan-adal", ""),
    ("IBL-027", "kafi", "ibl", "NOUN", "kafi", "Root", "Baguio/Ibaloi cultural community peace gathering", "Pagtitipon para sa kapayapaan", "CAMPUS_DECORUM_DRESSCODE", "kafi", ""),
    ("IBL-028", "ag-agto", "ibl", "VERB", "agto", "ag-", "To carry or bring required school credentials/ID", "Magdala", "EXAM_PERMIT_INTEGRITY", "ag-agto|agto", ""),
    ("IBL-029", "to-o", "ibl", "NOUN", "to-o", "Root", "Person; student or community member", "Tao", "CAR_REGIONAL_LEXICON", "to-o|too", ""),
    ("IBL-030", "balitok", "ibl", "NOUN", "balitok", "Root", "Gold; symbol of excellence and academic honors", "Ginto; karangalan", "TUITION_FINANCE", "balitok", ""),
    ("IBL-031", "ngaran", "ibl", "NOUN", "ngaran", "Root", "Name; official student record identifier", "Pangalan", "URO_ENROLLMENT_TOR", "ngaran", ""),
    ("IBL-032", "sakit", "ibl", "NOUN", "sakit", "Root", "Illness or pain requiring SLU clinic attention", "Sakit", "CAMPUS_HEALTH_SAFETY", "sakit", ""),
]

# ==============================================================================
# 3. BALANCED 250-DOCUMENT ANNOTATED CORPUS (25 docs x 10 operational intents)
#    Explicit Source_Type provenance:
#      - OFFICIAL_SLU_POLICY (32 docs)
#      - HARVESTED_FREEDOM_WALL / OFFICIAL_URO_FAQ_Q (Midterm authentic queries)
#      - CURATED_MULTILINGUAL_INQUIRY (Balanced EN, TL-EN, CAR-TL-EN student queries)
# ==============================================================================

CURATED_INQUIRIES_BY_INTENT = {
    "URO_ENROLLMENT_TOR": [
        # (source_type, section_ref, sentiment, code_switching, text)
        ("OFFICIAL_URO_FAQ_Q", "URO FAQ Q2: Transcript & Certification Query", "NEUTRAL_INQUIRY", "EN", "How does a student request official academic transcripts and certifications?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-01", "NEUTRAL_INQUIRY", "EN", "Where do I apply online for an Official Transcript of Records TOR and Certificate of Grades COG at SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-02", "NEUTRAL_INQUIRY", "EN", "Which university departments must sign my clearance before URO releases my TOR and diploma?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-03", "NEUTRAL_INQUIRY", "EN", "How can an SLU graduate request a Certificate of Good Moral Character CGMC from OSAS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-04", "NEUTRAL_INQUIRY", "EN", "Does the University Registrar process CHED CAV authentication and certified true copies of diplomas?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-05", "NEUTRAL_INQUIRY", "EN", "Can I request an electronic copy of my Certificate of Graduation through the URO document portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-06", "NEUTRAL_INQUIRY", "EN", "What clearance offices are required from accounting library and student affairs before TOR release?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-07", "NEUTRAL_INQUIRY", "TL-EN", "Paano po kumuha ng TOR at COG online sa URO document request portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-08", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba ng clearance sa Accounting, Library, at Dean of Student Affairs bago makuha ang TOR?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-09", "NEUTRAL_INQUIRY", "TL-EN", "Saan po mag-apply ng Certificate of Good Moral Character CGMC para sa board exam sa OSAS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-10", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba mag-request ng certified true copy ng diploma at CHED CAV sa URO?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-11", "NEUTRAL_INQUIRY", "TL-EN", "Gaano po katagal bago ma-release ang Certificate of Grades COG pagkatapos ng clearance?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-12", "NEUTRAL_INQUIRY", "TL-EN", "Anong requirements po para sa honorable dismissal at official transcript of records sa registrar?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-13", "NEUTRAL_INQUIRY", "TL-EN", "Online lang po ba ang filing ng certificate of graduation at transcript sa SLU URO?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-14", "NEUTRAL_INQUIRY", "TL-EN", "May clearance po ba sa library services bago ma-claim ang physical TOR sa registrar window?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Kasano agkiddaw ti TOR ken COG idiay URO document portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Agsurat ak kuma ti request para official transcript of records ken clearance idiay SLU URO."),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a malem, ania dagiti dokumento kasapulan tapno maala ti CGMC idiay OSAS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Menkiddaw ak kuma ti TOR ken Certificate of Grades, nakdeng kadi ti clearance?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mensulat ak ti request para CAV ken certified true copy ti diploma idiay URO."),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Pagsurat ko koma ni request para TOR tan COG idiyay URO registrar."),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #TOR-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng maabii, intoy tulek para honorable dismissal tan good moral certificate CGMC?"),
    ],
    "URO_ENROLLMENT_PORTAL": [
        ("OFFICIAL_URO_FAQ_Q", "URO FAQ Q3: Continuing Enrollment Query", "NEUTRAL_INQUIRY", "EN", "What is the enrollment procedure for continuing undergraduate students?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-01", "NEUTRAL_INQUIRY", "EN", "How do continuing students complete online advising of subjects in the iSLU student portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-02", "NEUTRAL_INQUIRY", "EN", "Where do I validate my SLU RFID card after my enrollment payment is posted?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-03", "NEUTRAL_INQUIRY", "EN", "What documents must incoming freshmen submit during SLU admission and enrollment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-04", "NEUTRAL_INQUIRY", "EN", "How do I finalize my class schedule confirmation within my assigned year-level window?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-05", "NEUTRAL_INQUIRY", "EN", "Is the Center for Counseling and Wellness intake interview required for freshmen enrollment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-06", "NEUTRAL_INQUIRY", "EN", "Do continuing students need Form 138 or just online advising and downpayment on iSLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-07", "NEUTRAL_INQUIRY", "TL-EN", "Paano po mag-enroll ang continuing students gamit ang SLU student portal iSLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-08", "NEUTRAL_INQUIRY", "TL-EN", "Saan po nagpapa-validate ng SLU ID card pagkatapos magbayad ng enrollment downpayment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-09", "NEUTRAL_INQUIRY", "TL-EN", "Anong original documents po ang kailangan ng incoming freshmen tulad ng Form 138 at PSA?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-10", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba tapusin ang online advising sa assigned year-level schedule window?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-11", "NEUTRAL_INQUIRY", "TL-EN", "Paano po makita kung confirmed na ang enrolled schedule ko sa iSLU portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-12", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba magpa-validate ng RFID sa University Library after mag-post ang payment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-13", "NEUTRAL_INQUIRY", "TL-EN", "Kasama po ba ang NSTP sa online advising ng subjects sa iSLU student portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-14", "NEUTRAL_INQUIRY", "TL-EN", "Paano po mag-confirm ng subjects ang regular continuing student ngayong semester?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Kasano agpalista ken agadal idiay SLU iSLU student portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Agadal ak idiay pagadalan SLU, kasano ti online advising ti continuing estudyante?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Saan nga i-validate ti ID card kalpasan ti panagpalista idiay eskuela?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Kaman-ano men-enroll ken man-adal isnan SLU student portal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kasapulan kadi ti Form 138 ken ngadan registration para freshmen isnan iskuela?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Pan-adal ko idiyay SLU, paano online advising tan ID validation?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ENR-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Isarong ko koma idiyay iskuela, kailangan ba confirmation sa year-level window?"),
    ],
    "URO_SUBJECT_ADJUSTMENT": [
        ("OFFICIAL_URO_FAQ_Q", "URO FAQ Q4: Adding/Dropping Subjects Query", "NEUTRAL_INQUIRY", "EN", "What is the procedure for dropping or adding subjects during the adjustment period?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-01", "NEUTRAL_INQUIRY", "EN", "How long is the official adding and dropping adjustment period at the start of a regular semester?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-02", "NEUTRAL_INQUIRY", "EN", "Whose endorsement and approval do I need on the Adjustment Form to drop a subject?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-03", "NEUTRAL_INQUIRY", "EN", "What happens if I stop attending a subject without filing an official withdrawal WP or DRP form?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-04", "NEUTRAL_INQUIRY", "EN", "How can a graduating student petition for a unit overload or closed section schedule change?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-05", "NEUTRAL_INQUIRY", "EN", "Does partial withdrawal of a course require explicit approval from the School Dean?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-06", "NEUTRAL_INQUIRY", "EN", "Can I still add or change class schedules after the first two weeks of the semester?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-07", "NEUTRAL_INQUIRY", "TL-EN", "Paano po mag-add o mag-drop ng subject sa loob ng first two weeks adjustment period?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-08", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba ng pirma ng department chair at registrar para sa adjustment form?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-09", "NEUTRAL_INQUIRY", "TL-EN", "Ano po ang mangyayari kung hindi ako nag-official drop at basta lang hindi pumasok?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-10", "NEUTRAL_INQUIRY", "TL-EN", "Paano mag-file ng partial withdrawal WP o DRP ng subject na may approval ng Dean?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-11", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba mag-petition ng overload units o magpalit ng schedule ng klase sa URO?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-12", "NEUTRAL_INQUIRY", "TL-EN", "Hanggang kailan po ang adding and dropping window para sa regular semester?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-13", "NEUTRAL_INQUIRY", "TL-EN", "Saan po ipapasa ang accomplished subject adjustment form pagkatapos i-endorse ng chair?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-14", "NEUTRAL_INQUIRY", "TL-EN", "Paano mag-change ng section kapag conflict ang class schedule sa adjustment period?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Kasano ag-drop wenno ag-add ti subject ken kasapulan kadi ti pirma ti chair?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Agsaludsod ak kuma no dua a lawas laeng ti subject adjustment period idiay URO?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Ania ti mapasamak no saan nga ag-file ti official dropping WP form iti Dean?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay masdem! Kaman-ano mag-drop ti subject ken pa-approve isnan department chair?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mensaludsod ak no mabalin mag-petition ti unit overload ken schedule adjustment isnan URO."),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Paano mag-drop tan mag-add ni subject using adjustment form sa Dean?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #ADJ-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Dakel a iyaman, kailangan kadi ni endorsement ng chair para subject change?"),
    ],
    "ACADEMIC_SHIFTING_TRANSFER": [
        ("HARVESTED_FREEDOM_WALL", "Freedom Wall #25605", "NEUTRAL_INQUIRY", "TL-EN", "pwede mag tanong? paano po ba process ng shifting from samcis to seait or sonahbs? may qualifying exams po ba ulit or direct submission lang sa uro window?"),
        ("OFFICIAL_URO_FAQ_Q", "URO FAQ Q1: Transferee Admission Query", "NEUTRAL_INQUIRY", "EN", "What are the admission requirements for transferee students at SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-01", "NEUTRAL_INQUIRY", "EN", "Does Saint Louis University accept transfer students into BS Medical Laboratory Science MLS or BS Nursing BSN?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-02", "NEUTRAL_INQUIRY", "EN", "What is the maximum number of earned units allowed for transferees in 4-year and 5-year courses?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-03", "NEUTRAL_INQUIRY", "EN", "Can a transferee with a failing grade, INC, or DROPPED mark from a prior college transfer to SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-04", "NEUTRAL_INQUIRY", "EN", "What steps are required for internal course shifting from SAMCIS to STELA or SEAIT?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-05", "NEUTRAL_INQUIRY", "EN", "What GWA and science grade screening apply for shifting or transferring to BS Pharmacy or Radiologic Technology?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-06", "NEUTRAL_INQUIRY", "EN", "Do all transferees have to pass the Qualifying Examination QE, personality evaluation, and dean interview?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-07", "NEUTRAL_INQUIRY", "TL-EN", "Tumatanggap po ba ang SLU ng transferees sa BS MLS medtech at BS Nursing BSN?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-08", "NEUTRAL_INQUIRY", "TL-EN", "Ilang maximum units po ang pwede sa transferee para sa 4-year at 5-year degree programs?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-09", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba mag-transfer sa SLU kung may bagsak o INC o Dropped grade sa dating school?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-10", "NEUTRAL_INQUIRY", "TL-EN", "Paano mag-shift ng course mula SAMCIS papuntang SEAIT engineering o STELA?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-11", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba ng dean interview, personality test, at qualifying exam QE sa pag-transfer?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-12", "NEUTRAL_INQUIRY", "TL-EN", "Ilang previous schools lang po ang allowed para sa transferee applicant sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-13", "NEUTRAL_INQUIRY", "TL-EN", "Maki-credit po ba ng URO ang general education subjects ko kapag nag-shift ako ng program?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-14", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Agbaliw ak kuma ti kurso manipud SAMCIS agingga SEAIT, adda kadi QE?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mabalin kadi agtransfer iti BS MLS wenno BSN idiay SLU SONAHBS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Ania dagiti requirements ken qualifying exam para transferee idiay SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Kaman-ano mag-shift ti kurso manipud SAMCIS papuntang STELA?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kasapulan kadi ti dean interview ken qualifying exam QE para transferee students?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #SHF-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Pwede kadi mag-transfer idiyay SLU kung lagpas 84 units?"),
    ],
    "HANDBOOK_GRADING_FDA": [
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-01", "NEUTRAL_INQUIRY", "EN", "What is the minimum passing grade under the Saint Louis University numerical grading system?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-02", "NEUTRAL_INQUIRY", "EN", "How many unexcused absences trigger an automatic Failure Due to Absences FDA grade?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-03", "NEUTRAL_INQUIRY", "EN", "Can SAMCIS and SEAIT set higher retention grades than the 75 percent minimum passing mark?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-04", "NEUTRAL_INQUIRY", "EN", "How do I remove an Incomplete INC or No Final Examination NFE grade before it turns into failure?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-05", "NEUTRAL_INQUIRY", "EN", "What happens to my course standing if I miss more than 20 percent of total class hours?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-06", "NEUTRAL_INQUIRY", "EN", "If I receive a final mark of 73 or 74 percent in a subject, is that considered a failing grade?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-07", "NEUTRAL_INQUIRY", "EN", "When is an INC grade allowed by a faculty member under SLU Student Handbook rules?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-08", "NEUTRAL_INQUIRY", "TL-EN", "Ano po ang minimum passing grade sa SLU at pwede bang mas mataas ang retention grade sa SAMCIS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-09", "NEUTRAL_INQUIRY", "TL-EN", "Ilang percent ng unexcused absences po bago ma-automatic drop at mabigyan ng FDA?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-10", "NEUTRAL_INQUIRY", "TL-EN", "Paano po ma-clear ang INC o NFE grade at ano ang mangyayari kapag lumampas sa removal period?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-11", "NEUTRAL_INQUIRY", "TL-EN", "Bagsak na po ba kapag 74 ang grade sa subject o 75 talaga ang passing mark?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-12", "NEUTRAL_INQUIRY", "TL-EN", "Automatic dropped po ba sa class roll kapag lagpas 20 percent ang unexcused absences?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-13", "NEUTRAL_INQUIRY", "TL-EN", "May sariling retention grade policy po ba ang specialized programs sa SAMCIS at Engineering?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-14", "NEUTRAL_INQUIRY", "TL-EN", "Hanggang kailan po pwedeng kumpletuhin ang Incomplete INC requirements sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-15", "NEUTRAL_INQUIRY", "TL-EN", "Paano kinocompute ang 20 percent FDA threshold sa regular class attendance?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Mano a porsiento ti absent iti klase sakbay nga agbalin nga FDA?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Ania ti minimum passing grado idiay SLU ken kasano i-remove ti INC mark manipud maestro?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Agsaludsod ak no 75 percent kadi ti passing grade ken mas nangato ti retention idiay SAMCIS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agew! Ad-ado di absent ko isnan klase, ma-FDA ak kadi no lagpas 20 percent?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kaman-ano ti grading system ken turo retention grade isnan SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Nu ad-ado absent tan ag-kala sa class, automatic FDA kadi?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #GRD-22", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng maabii, ania ti rule para INC ken NFE grade removal period?"),
    ],
    "EXAM_PERMIT_INTEGRITY": [
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-01", "NEUTRAL_INQUIRY", "EN", "What credentials must students present before entering Prelim, Midterm, and Final examination rooms?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-02", "NEUTRAL_INQUIRY", "EN", "Can an exam proctor bar a student who forgot their exam permit or validated SLU RFID card?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-03", "NEUTRAL_INQUIRY", "EN", "What are the penalties for plagiarism, unauthorized notes, or mobile phone use during examinations?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-04", "NEUTRAL_INQUIRY", "EN", "How does the SLU Disciplinary Board and OSAS handle major academic dishonesty and contract cheating?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-05", "NEUTRAL_INQUIRY", "EN", "Does unauthorized collaboration during an exam result in suspension or dismissal?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-06", "NEUTRAL_INQUIRY", "EN", "What disciplinary due process and graduated sanctions apply under the SLU Student Handbook?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-07", "NEUTRAL_INQUIRY", "EN", "Are cellphones and unauthorized gadgets strictly prohibited inside examination rooms?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-08", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba ng official examination permit at validated SLU RFID card bago mag-exam?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-09", "NEUTRAL_INQUIRY", "TL-EN", "Bawal po ba maglabas ng cellphone o mobile device habang nag-eexam sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-10", "NEUTRAL_INQUIRY", "TL-EN", "Ano po ang parusa ng SLU Disciplinary Board sa plagiarism, kopyahan, at contract cheating?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-11", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba akong hindi papasukin ng proctor kung naiwan ko ang RFID at exam permit?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-12", "NEUTRAL_INQUIRY", "TL-EN", "Paano po ang proseso ng due process at disciplinary sanctions sa OSAS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-13", "NEUTRAL_INQUIRY", "TL-EN", "Major academic dishonesty po ba ang unauthorized collaboration at kodigo notes sa exam?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-14", "NEUTRAL_INQUIRY", "TL-EN", "Required po ba ang exam permit sa lahat ng prelim, midterm, at final examinations?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-15", "NEUTRAL_INQUIRY", "TL-EN", "Suspension o dismissal po ba ang sanction sa malalang academic cheating sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Maiparit kadi ti cellphone bayat ti eksamen ken ania ti linteg ti SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kasapulan kadi ti exam permit ken validated RFID sakbay sumrek iti eksamen?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agew! Inayan ken paniyew ti cheating wenno plagiarism isnan exam, ania ti sanction?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kasapulan kadi ti RFID card ken permit, inayan no mang-kopya isnan exam?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kaman-ano ti disciplinary process kasla dap-ay sanggunian idiay SLU OSAS?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Ania ti proseso ti tongtong ken SLU Disciplinary Board para academic dishonesty?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #EXM-22", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Bain ti cheating tan plagiarism, kailangan ag-agto ni validated RFID tan exam permit?"),
    ],
    "CAMPUS_DECORUM_DRESSCODE": [
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-01", "NEUTRAL_INQUIRY", "EN", "On which days of the week is the official Saint Louis University student uniform strictly required?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-02", "NEUTRAL_INQUIRY", "EN", "What civilian clothes are permitted and forbidden during SLU Wash Days on Fridays and Saturdays?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-03", "NEUTRAL_INQUIRY", "EN", "Are slippers, sandos, revealing outfits, or obscene graphic shirts allowed on SLU campus?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-04", "NEUTRAL_INQUIRY", "EN", "Must students wear their validated SLU RFID card visibly while entering Gate 1 and Gate 2?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-05", "NEUTRAL_INQUIRY", "EN", "Is lending or borrowing another student's RFID identification card a disciplinary offense?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-06", "NEUTRAL_INQUIRY", "EN", "What is SLU's policy regarding smoking, vaping, and alcohol across Bonifacio and Maryheights campuses?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-07", "NEUTRAL_INQUIRY", "EN", "Can students wear modest civilian attire on Wednesdays or only on designated wash days?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-08", "NEUTRAL_INQUIRY", "TL-EN", "Anong araw po required magsuot ng university uniform at kailan ang Wash Day sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-09", "NEUTRAL_INQUIRY", "TL-EN", "Bawal po ba ang slippers, sando, at revealing clothes kahit Wash Day sa Biyernes at Sabado?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-10", "NEUTRAL_INQUIRY", "TL-EN", "Required po ba na suot palagi ang SLU RFID card pagpasok sa Gate 1 at Gate 2?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-11", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba magpahiram ng RFID ID card sa kaklase para makapasok sa campus?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-12", "NEUTRAL_INQUIRY", "TL-EN", "Bawal po ba ang vape at paninigarilyo sa loob ng SLU Bonifacio at Bakakeng campus?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-13", "NEUTRAL_INQUIRY", "TL-EN", "Monday to Thursday po ba talaga ang prescribed uniform dress code sa lahat ng SLU campus?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-14", "NEUTRAL_INQUIRY", "TL-EN", "Bawal po ba ang damit na may obscene language o bastos na print sa campus?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-15", "NEUTRAL_INQUIRY", "TL-EN", "Ano po ang tamang campus decorum at attire guidelines kapag Wash Day?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Ania nga aldaw ti prescribed uniform bado ken kaano ti Wash Day idiay SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Maiparit kadi ti tsinelas slippers ken sando nga pagbado idiay SLU campus?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kasapulan kadi nga agsuot ti SLU RFID card no sumrek iti Gate 1 ken Gate 2?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Ipapilit kadi ti uniform bado manipud Lunes agingga Huwebes?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Bawal kadi ti vape, sigarilyo, ken slippers isnan SLU campus locations?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Friday tan Saturday kadi ti washday modest civilian attire sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #DRS-22", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng maabii, ania ti Louisian campus decorum tan smoke-free rules?"),
    ],
    "CAMPUS_HEALTH_SAFETY": [
        ("HARVESTED_FREEDOM_WALL", "Freedom Wall #25604", "NEGATIVE_URGENT", "CAR-TL-EN", "ambigat sa pakiramdam kapag sabay sabay ang deadlines ng prelim activities at long exams sa engineering at computing. may mental health break po ba tayo this term?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-01", "NEUTRAL_INQUIRY", "EN", "Where is the SLU University Medical and Dental Clinic located and what first-aid services does it offer?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-02", "NEUTRAL_INQUIRY", "EN", "Are annual medical exams and physical fitness certificates required for PATHFIT and lab practicums?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-03", "NEUTRAL_INQUIRY", "EN", "What should students do during a Baguio City earthquake and where are the designated evacuation areas?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-04", "NEUTRAL_INQUIRY", "EN", "Where do I report urgent campus security incidents or lost items at SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-05", "NEUTRAL_INQUIRY", "EN", "How can I book confidential counseling or psychological first aid with the Center for Counseling and Wellness CCW?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-06", "NEUTRAL_INQUIRY", "EN", "What sanctions apply for cyberbullying, libelous posts, or Republic Act 10173 Data Privacy violations on social media?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-07", "NEUTRAL_INQUIRY", "TL-EN", "Saan po ang University Clinic sa Bonifacio at Maryheights para sa PATHFIT medical certificate?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-08", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba ipa-verify sa SLU clinic ang excuse letter mula sa private doctor?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-09", "NEUTRAL_INQUIRY", "TL-EN", "Saan po ang evacuation area tulad ng SLU Main Oval kapag may lindol earthquake sa Baguio?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-10", "NEUTRAL_INQUIRY", "TL-EN", "May libreng counseling o mental health support po ba sa Center for Counseling and Wellness CCW?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-11", "NEUTRAL_INQUIRY", "TL-EN", "May administrative sanction po ba sa libel, harassment, o RA 10173 data privacy violation sa online forums?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-12", "NEUTRAL_INQUIRY", "TL-EN", "Saan po pwedeng mag-report ng security concern sa Gate 1 at Gate 2 ng SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-13", "NEUTRAL_INQUIRY", "TL-EN", "Nagbibigay po ba ng starter medicine doses, dental check, at Hepa vaccine ang SLU Health Services?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-14", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Agpaagas ak kuma ta adda sakit ko, sadino ti clinic ken agas idiay SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Ania ti aramiden no adda gingined earthquake idiay Baguio ken sadino ti bantay security office?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kasapulan ti annad ken salun-at medical certificate para PATHFIT ken social media RA 10173."),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Nasakit ti ulok, sadino ti university clinic ken kinatalna evacuation dalan no adda yegyeg?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Kaman-ano mag-book ti counseling session para kapia ken kinakamo mental wellness idiay CCW?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Sadino ti clinic para salun-at tan PATHFIT medical exam nu adda sakit?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #HLT-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng maabii, ania ti kalinan evacuation protocol nu adda yegyeg wenno afoy emergency idiyay SLU?"),
    ],
    "TUITION_FINANCE": [
        ("HARVESTED_FREEDOM_WALL", "Freedom Wall #25628", "NEGATIVE_URGENT", "TL-EN", "why is slu lowkey increasing the total tuition fee recently mid sem? akala ata nila walang nakakahalata? last sem it was about 60 pesos ngayon naman 105 pesos it may be a small amount per person but multiply it to thousands of students. ano yun inflation mid sem? gusto ninyo rin atang ma arteks of lakandula. yes sis every sem tumataas sinasabi ko pa dati ang mura ng downpayment kasi 6900 first year first sem tapos noong nag second sem 1st year 11200 na haha same until now na pa grad na nasanay na lang na every sem ang pag taas tuition."),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-01", "NEUTRAL_INQUIRY", "EN", "How can students pay SLU tuition fees and enrollment downpayments via partner banks or mobile banking?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-02", "NEUTRAL_INQUIRY", "EN", "Do I need to submit my bank deposit slip or accounting copy to the SLU Finance Office after online payment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-03", "NEUTRAL_INQUIRY", "EN", "What institutional scholarships does SLU offer for Senior High School Valedictorians and Dean's Listers?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-04", "NEUTRAL_INQUIRY", "EN", "How do I apply for CHED TES, PESFA, DOST, or Bukas Student Loans at Saint Louis University?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-05", "NEUTRAL_INQUIRY", "EN", "How are tuition fee assessment adjustments processed after adding or dropping subjects?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-06", "NEUTRAL_INQUIRY", "EN", "Are there activity grants for SLU Marching Band, varsity athletes, or HRD working students?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-07", "NEUTRAL_INQUIRY", "EN", "Where can I check my remaining tuition installment balance and financial clearance status?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-08", "NEUTRAL_INQUIRY", "TL-EN", "Paano po magbayad ng tuition fee at downpayment dp gamit ang authorized partner banks?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-09", "NEUTRAL_INQUIRY", "TL-EN", "Kailangan po ba ipasa ang proof of payment o accounting copy sa SLU Finance Office?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-10", "NEUTRAL_INQUIRY", "TL-EN", "Ano po ang scholarship discounts para sa Dean's Listers at SHS Valedictorians sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-11", "NEUTRAL_INQUIRY", "TL-EN", "Saan po mag-inquire tungkol sa CHED TES, DOST scholarship, o Bukas student loan?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-12", "NEUTRAL_INQUIRY", "TL-EN", "May working student service grant o athletics varsity scholarship po ba sa SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-13", "NEUTRAL_INQUIRY", "TL-EN", "Paano po ma-adjust ang tuition ledger assessment kapag nag-drop ako ng subject?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-14", "NEUTRAL_INQUIRY", "TL-EN", "Saan po makikita ang financial clearance at installment balance bago ang midterm exam?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Kasano agbayad ti tuition gatad ken downpayment idiay partner banks?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Adda kadi scholarship tulong wenno discount para Dean's Listers ken kuarta student loan idiay SLU?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Sadino nga ipasa ti resibo kalpasan ti panagbayad ti utang ledger idiay Finance Office?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Kaman-ano menbayad ti tuition pilak ken downpayment isnan Finance Office?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Adda kadi CHED TES wenno SLU Academic Scholarship discount para scholars?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Paano manbayad ni tuition fee tan downpayment using online banking?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FIN-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng maabii, ania ti SLU Entrance Scholarship tan academic honors balitok discount?"),
    ],
    "CAMPUS_FACILITIES_LAB": [
        ("HARVESTED_FREEDOM_WALL", "Freedom Wall #25599", "NEGATIVE_URGENT", "TL-EN", "had to agree with like be for real slu? for years the department of mls gave you the greatest pride always bringing home the top performing school title pero what the hell kailangan namin magtiis sa mga tinipid na materials for lab? kapiranggot na litmus paper? reused pipette tips and pasteur pipettes? like what the hell! have some shame! beautification projects gusto? dadag ng budget for labs ayaw?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-01", "NEUTRAL_INQUIRY", "EN", "How many books can undergraduate and graduate students borrow from the SLU University Libraries UNL?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-02", "NEUTRAL_INQUIRY", "EN", "What are the overdue book fines and lost material rules at the Msgr. Charles Vath Library?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-03", "NEUTRAL_INQUIRY", "EN", "Where should MLS and Engineering students report shortages of lab consumables, pipettes, or defective equipment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-04", "NEUTRAL_INQUIRY", "EN", "What protective gear and safety disposal rules must students follow inside science laboratories?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-05", "NEUTRAL_INQUIRY", "EN", "Who handles iSLU portal account lockouts, SLU institutional email password resets, and campus Wi-Fi issues?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-06", "NEUTRAL_INQUIRY", "EN", "Do I need a valid SLU RFID card to enter library collaboration rooms and access electronic databases?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-07", "NEUTRAL_INQUIRY", "EN", "Who is the laboratory custodian responsible for checking lab workstations and reagents?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-08", "NEUTRAL_INQUIRY", "TL-EN", "Ilang libro po ang pwedeng hiramin ng undergraduate students sa SLU University Library sa Vath?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-09", "NEUTRAL_INQUIRY", "TL-EN", "May multa po ba kapag overdue o nawala ang hiniram na libro sa SLU library?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-10", "NEUTRAL_INQUIRY", "TL-EN", "Kanino po pwede i-report ang kulang na lab reagents, reused pipette tips, o sirang equipment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-11", "NEUTRAL_INQUIRY", "TL-EN", "Paano po magpa-reset ng nakalimutang password sa SLU institutional email at iSLU Wi-Fi?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-12", "NEUTRAL_INQUIRY", "TL-EN", "Required po ba magsuot ng lab coat at protective gear sa MLS at chemistry laboratories?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-13", "NEUTRAL_INQUIRY", "TL-EN", "Pwede po ba mag-reserve ng collaboration room at computer research station sa UNL library?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-14", "NEUTRAL_INQUIRY", "TL-EN", "Saan po mag-report ng sirang computer workstation sa SAMCIS computing laboratory?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-15", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Naimbag a bigat! Mano a libro ti mabalin buloden ken kaano agsubli idiay SLU Vath library?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-16", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Agbasa ak kuma idiay UNL library, kasapulan kadi ti RFID card ken adda danum utility station?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-17", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Sino ti pagreportan no kulang ti laboratory equipment wenno computer idiay department?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-18", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Gawis ay agsapa! Man-obla kami isnan laboratory, sino ti lab custodian para reagents ken danom?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-19", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Ubbo kami nga agbasa ti liblo isnan library baey, ilang araw pwede hiramin ang books?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-20", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng shapa! Mankimey tan man-obda kami sa lab, where to report defective pipette equipment?"),
        ("CURATED_MULTILINGUAL_INQUIRY", "Curated Inquiry #FAC-21", "NEUTRAL_INQUIRY", "CAR-TL-EN", "Mapteng maabii, paano IT support reset para iSLU email, campus Wi-Fi, tan library baley?"),
    ],
}

# ==============================================================================
# 4. STRICTLY HELD-OUT UNSEEN BENCHMARK (48 Queries: 40 In-Domain + 8 OOD/Trap)
#    Guaranteed 0 exact-string overlap with annotated_corpus_expanded.csv!
# ==============================================================================

HELDOUT_BENCHMARK = [
    # --- URO_ENROLLMENT_TOR (4) ---
    {"id": "B01", "query": "I graduated last year and need an authenticated TOR plus good moral certificate for my PRC licensure.", "expected_intent": "URO_ENROLLMENT_TOR", "expected_docs": [101, 102, 103], "register": "EN", "type": "in_domain"},
    {"id": "B02", "query": "Sir/Ma'am, online pa rin po ba yung pagkuha ng Certificate of Grades at clearance sa Accounting?", "expected_intent": "URO_ENROLLMENT_TOR", "expected_docs": [101], "register": "TL-EN", "type": "in_domain"},
    {"id": "B03", "query": "Naimbag nga aldaw, kayat ko agkiddaw ti CAV ken certified copy ti diplomak idiay URO.", "expected_intent": "URO_ENROLLMENT_TOR", "expected_docs": [103, 101], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B04", "query": "Gawis ay labi! Menkiddaw ak kuma ti CGMC idiay OSAS, ania kasapulan?", "expected_intent": "URO_ENROLLMENT_TOR", "expected_docs": [102], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- URO_ENROLLMENT_PORTAL (4) ---
    {"id": "B05", "query": "I already paid my tuition deposit; where do I go to validate my student RFID for this term?", "expected_intent": "URO_ENROLLMENT_PORTAL", "expected_docs": [106, 104], "register": "EN", "type": "in_domain"},
    {"id": "B06", "query": "Incoming freshman po ako, kailangan ba mag-submit ng original Form 138 at pumunta sa CCW intake?", "expected_intent": "URO_ENROLLMENT_PORTAL", "expected_docs": [105], "register": "TL-EN", "type": "in_domain"},
    {"id": "B07", "query": "Naimbag a malem! Agpalista akon para sumaruno a semestre, kasano online advising iti iSLU?", "expected_intent": "URO_ENROLLMENT_PORTAL", "expected_docs": [104], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B08", "query": "Mapteng shapa! Continuing student ak, paano schedule confirmation idiyay assigned year window?", "expected_intent": "URO_ENROLLMENT_PORTAL", "expected_docs": [104], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- URO_SUBJECT_ADJUSTMENT (4) ---
    {"id": "B09", "query": "Can I withdraw from a difficult math class during week 2 and who signs my adjustment paperwork?", "expected_intent": "URO_SUBJECT_ADJUSTMENT", "expected_docs": [107, 108], "register": "EN", "type": "in_domain"},
    {"id": "B10", "query": "Graduating student po ako, pwede bang mag-apply ng unit overload o magpalit ng closed section?", "expected_intent": "URO_SUBJECT_ADJUSTMENT", "expected_docs": [109], "register": "TL-EN", "type": "in_domain"},
    {"id": "B11", "query": "Agsaludsod ak no ania ti penalty no saan nga ag-file ti official dropping form iti Dean?", "expected_intent": "URO_SUBJECT_ADJUSTMENT", "expected_docs": [108], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B12", "query": "Gawis ay masdem! Pwede kadi mag-add ken mag-drop ti subjects using adjustment form?", "expected_intent": "URO_SUBJECT_ADJUSTMENT", "expected_docs": [107], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- ACADEMIC_SHIFTING_TRANSFER (4) ---
    {"id": "B13", "query": "I have 90 earned units from another university and want to transfer into a 4-year SLU program—am I eligible?", "expected_intent": "ACADEMIC_SHIFTING_TRANSFER", "expected_docs": [111, 110], "register": "EN", "type": "in_domain"},
    {"id": "B14", "query": "Gusto ko po lumipat from SAMCIS to BS Pharmacy o SEAIT, ano po GWA cut-off at kailangan ba QE?", "expected_intent": "ACADEMIC_SHIFTING_TRANSFER", "expected_docs": [112, 113, 110], "register": "TL-EN", "type": "in_domain"},
    {"id": "B15", "query": "Naimbag a bigat! Agbaliw ak kuma ti programa, tumatanggap kadi ti transferee iti BS Nursing BSN wenno MLS?", "expected_intent": "ACADEMIC_SHIFTING_TRANSFER", "expected_docs": [110, 112], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B16", "query": "Mapteng maabii, pwede ba mag-shift internal course if approved ng accepting Dean?", "expected_intent": "ACADEMIC_SHIFTING_TRANSFER", "expected_docs": [112], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- HANDBOOK_GRADING_FDA (4) ---
    {"id": "B17", "query": "If my final score is 74 in a core computing course, did I fail and does SAMCIS require a higher retention mark?", "expected_intent": "HANDBOOK_GRADING_FDA", "expected_docs": [114], "register": "EN", "type": "in_domain"},
    {"id": "B18", "query": "Naka-INC po ako dahil na-ospital ako noong finals, gaano katagal bago ito maging No Credit?", "expected_intent": "HANDBOOK_GRADING_FDA", "expected_docs": [116], "register": "TL-EN", "type": "in_domain"},
    {"id": "B19", "query": "Naimbag a bigat! Agadal ak idiay SAMCIS—mano a porsiento ti absent sakbay ma-FDA?", "expected_intent": "HANDBOOK_GRADING_FDA", "expected_docs": [115], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B20", "query": "Gawis ay agew! Ad-ado unexcused absences ko, automatic drop kadi no sobra 20 percent?", "expected_intent": "HANDBOOK_GRADING_FDA", "expected_docs": [115], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- EXAM_PERMIT_INTEGRITY (4) ---
    {"id": "B21", "query": "What happens if a proctor catches someone checking notes on a smartphone during finals?", "expected_intent": "EXAM_PERMIT_INTEGRITY", "expected_docs": [118, 117], "register": "EN", "type": "in_domain"},
    {"id": "B22", "query": "Naiwan ko po sa dorm yung exam permit at RFID ko, papapasukin pa ba ako ng proctor sa midterm?", "expected_intent": "EXAM_PERMIT_INTEGRITY", "expected_docs": [117], "register": "TL-EN", "type": "in_domain"},
    {"id": "B23", "query": "Gawis ay agsapa! Inayan ti plagiarism ken contract cheating, ania parusa ti Disciplinary Board?", "expected_intent": "EXAM_PERMIT_INTEGRITY", "expected_docs": [118, 119], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B24", "query": "Mapteng shapa! Paano yung tongtong due process at disciplinary sanctions sa OSAS?", "expected_intent": "EXAM_PERMIT_INTEGRITY", "expected_docs": [119, 118], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- CAMPUS_DECORUM_DRESSCODE (4) ---
    {"id": "B25", "query": "Is vaping allowed behind the campus buildings or are all SLU campuses strictly smoke-free?", "expected_intent": "CAMPUS_DECORUM_DRESSCODE", "expected_docs": [122], "register": "EN", "type": "in_domain"},
    {"id": "B26", "query": "Pwede po ba pumasok nang naka-tsinelas slippers o sando kapag Friday Wash Day?", "expected_intent": "CAMPUS_DECORUM_DRESSCODE", "expected_docs": [120], "register": "TL-EN", "type": "in_domain"},
    {"id": "B27", "query": "Naimbag a bigat! Maiparit kadi ti agipabulod ti RFID card no sumrek iti Gate 1?", "expected_intent": "CAMPUS_DECORUM_DRESSCODE", "expected_docs": [121], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B28", "query": "Gawis ay masdem! Lunes agingga Huwebes kadi ti uniform bado isnan SLU?", "expected_intent": "CAMPUS_DECORUM_DRESSCODE", "expected_docs": [120], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- CAMPUS_HEALTH_SAFETY (4) ---
    {"id": "B29", "query": "I am feeling ill with a high fever—can the Bonifacio campus clinic see me and verify my doctor's excuse letter?", "expected_intent": "CAMPUS_HEALTH_SAFETY", "expected_docs": [124], "register": "EN", "type": "in_domain"},
    {"id": "B30", "query": "Sobrang ambigat na ng stress ko sa deadlines, paano po magpa-schedule ng online counseling sa CCW?", "expected_intent": "CAMPUS_HEALTH_SAFETY", "expected_docs": [126], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B31", "query": "Naimbag a bigat! No adda gingined earthquake idiay Baguio, sadino evacuation area—SLU Main Oval kadi?", "expected_intent": "CAMPUS_HEALTH_SAFETY", "expected_docs": [125], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B32", "query": "May parusa po ba kapag may nag-post ng cyberbullying, libel, at private info under RA 10173 sa Freedom Wall?", "expected_intent": "CAMPUS_HEALTH_SAFETY", "expected_docs": [123], "register": "TL-EN", "type": "in_domain"},

    # --- TUITION_FINANCE (4) ---
    {"id": "B33", "query": "As a Senior High School Valedictorian, how do I avail of the SLU Entrance Scholarship tuition discount?", "expected_intent": "TUITION_FINANCE", "expected_docs": [129], "register": "EN", "type": "in_domain"},
    {"id": "B34", "query": "Nagbayad na po ako ng dp sa partner bank via mobile banking, ipapasa pa ba accounting copy sa Finance Office?", "expected_intent": "TUITION_FINANCE", "expected_docs": [127], "register": "TL-EN", "type": "in_domain"},
    {"id": "B35", "query": "Naimbag nga aldaw! Agbayad ak kuma ti installment balance, kasano tuition adjustment no nag-drop ak?", "expected_intent": "TUITION_FINANCE", "expected_docs": [128, 127], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B36", "query": "Gawis ay agsapa! Adda kadi tulong kasla CHED TES wenno DOST scholarship idiay SLU?", "expected_intent": "TUITION_FINANCE", "expected_docs": [129], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- CAMPUS_FACILITIES_LAB (4) ---
    {"id": "B37", "query": "How long can a graduate student keep borrowed books from the Msgr. Charles Vath Library?", "expected_intent": "CAMPUS_FACILITIES_LAB", "expected_docs": [130], "register": "EN", "type": "in_domain"},
    {"id": "B38", "query": "Locked out po yung SLU institutional email at campus Wi-Fi ko, sino po sa IT support ang kokontakin?", "expected_intent": "CAMPUS_FACILITIES_LAB", "expected_docs": [132], "register": "TL-EN", "type": "in_domain"},
    {"id": "B39", "query": "Man-obla kami isnan MLS laboratory, kanino i-report ang kulang na pipette reagents at sirang microscope?", "expected_intent": "CAMPUS_FACILITIES_LAB", "expected_docs": [131], "register": "CAR-TL-EN", "type": "in_domain"},
    {"id": "B40", "query": "Mapteng shapa! Pwede kadi mag-borrow ti 3 books for 3 days idiyay UNL library?", "expected_intent": "CAMPUS_FACILITIES_LAB", "expected_docs": [130], "register": "CAR-TL-EN", "type": "in_domain"},

    # --- OUT-OF-DOMAIN / GREETING / ADVERSARIAL TRAPS (8) ---
    {"id": "O01", "query": "random gibberish xyzzy qwerty plugh", "expected_intent": "OUT_OF_DOMAIN", "expected_docs": [], "register": "EN", "type": "ood"},
    {"id": "O02", "query": "What is the best recipe for Baguio strawberry sinigang?", "expected_intent": "OUT_OF_DOMAIN", "expected_docs": [], "register": "EN", "type": "ood"},
    {"id": "O03", "query": "Who won the NBA basketball championship last night?", "expected_intent": "OUT_OF_DOMAIN", "expected_docs": [], "register": "EN", "type": "ood"},
    {"id": "O04", "query": "Totoo ba pag sinabi ng crush ko na study first muna haha?", "expected_intent": "OUT_OF_DOMAIN", "expected_docs": [], "register": "TL-EN", "type": "ood"},
    {"id": "O05", "query": "hello good morning", "expected_intent": "GREETING", "expected_docs": [], "register": "EN", "type": "greeting"},
    {"id": "O06", "query": "Naimbag a bigat!", "expected_intent": "GREETING", "expected_docs": [], "register": "CAR-TL-EN", "type": "greeting"},
    {"id": "O07", "query": "What is the punishment for plagiarism?", "expected_intent": "EXAM_PERMIT_INTEGRITY", "expected_docs": [118], "register": "EN", "type": "car_trap_en"},
    {"id": "O08", "query": "Who sits on the disciplinary board?", "expected_intent": "EXAM_PERMIT_INTEGRITY", "expected_docs": [119, 118], "register": "EN", "type": "car_trap_en"},
]


def build_all():
    os.makedirs(EXPANDED_DIR, exist_ok=True)

    # 1. Write slu_official_policies_v2.json
    pol_path = os.path.join(EXPANDED_DIR, "slu_official_policies_v2.json")
    with open(pol_path, "w", encoding="utf-8") as f:
        json.dump(OFFICIAL_POLICIES_V2, f, indent=2, ensure_ascii=False)

    # 2. Write slu_car_domain_lexicon_v2.csv
    lex_path = os.path.join(EXPANDED_DIR, "slu_car_domain_lexicon_v2.csv")
    seen_ids = set()
    with open(lex_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Lexicon_ID",
            "Lemma_Entry",
            "Language_ISO",
            "POS_Tag",
            "Morphological_Root",
            "Affix_or_Type",
            "Institutional_or_English_Gloss",
            "Filipino_Gloss",
            "Domain_Intent_Mapping",
            "Native_Aliases",
            "Semantic_Aliases",
        ])
        for row in EXPANDED_LEXICON_ROWS:
            assert row[0] not in seen_ids, f"Duplicate Lexicon_ID: {row[0]}"
            seen_ids.add(row[0])
            writer.writerow(row)

    # 3. Build 250-doc balanced expanded corpus (25 per intent across 10 intents)
    corpus_rows = []
    doc_counter = 1
    intent_order = list(CURATED_INQUIRIES_BY_INTENT.keys())

    # First insert the 32 official policies
    policies_by_intent = {intent: [] for intent in intent_order}
    for p in OFFICIAL_POLICIES_V2:
        policies_by_intent[p["intent_label"]].append(p)

    for intent in intent_order:
        intent_docs = []
        for p in policies_by_intent[intent]:
            intent_docs.append({
                "Doc_ID": doc_counter,
                "Source_Type": "OFFICIAL_SLU_POLICY",
                "Source_File": p["source_file"],
                "Section_Reference": p["section_ref"],
                "Intent_Category": intent,
                "Sentiment_Urgency": "AUTHORITATIVE_POLICY",
                "Code_Switching": "EN",
                "Cleaned_Text": clean_text(p["raw_text"], preserve_car_hyphens=True),
            })
            doc_counter += 1

        for src_type, sec_ref, sent, cs, raw in CURATED_INQUIRIES_BY_INTENT[intent]:
            intent_docs.append({
                "Doc_ID": doc_counter,
                "Source_Type": src_type,
                "Source_File": "slu_expanded_multilingual_corpus.csv",
                "Section_Reference": sec_ref,
                "Intent_Category": intent,
                "Sentiment_Urgency": sent,
                "Code_Switching": cs,
                "Cleaned_Text": clean_text(raw, preserve_car_hyphens=True),
            })
            doc_counter += 1

        assert len(intent_docs) == 25, f"Intent {intent} has {len(intent_docs)} docs, expected 25"
        corpus_rows.extend(intent_docs)

    corp_path = os.path.join(EXPANDED_DIR, "annotated_corpus_expanded.csv")
    with open(corp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Doc_ID",
                "Source_Type",
                "Source_File",
                "Section_Reference",
                "Intent_Category",
                "Sentiment_Urgency",
                "Code_Switching",
                "Cleaned_Text",
            ],
        )
        writer.writeheader()
        writer.writerows(corpus_rows)

    # 4. Write heldout_benchmark.json and assert ZERO exact-text leakage
    corpus_texts = {r["Cleaned_Text"] for r in corpus_rows}
    for b in HELDOUT_BENCHMARK:
        cleaned_b = clean_text(b["query"], preserve_car_hyphens=True)
        assert cleaned_b not in corpus_texts, f"Train/test leakage detected for {b['id']}: {b['query']}"

    bench_path = os.path.join(EXPANDED_DIR, "heldout_benchmark.json")
    with open(bench_path, "w", encoding="utf-8") as f:
        json.dump(HELDOUT_BENCHMARK, f, indent=2, ensure_ascii=False)

    # Print verified summary
    lang_counts = Counter(r[2] for r in EXPANDED_LEXICON_ROWS)
    cs_counts = Counter(r["Code_Switching"] for r in corpus_rows)
    src_counts = Counter(r["Source_Type"] for r in corpus_rows)
    print(f"[OK] Policies: {len(OFFICIAL_POLICIES_V2)} across {len(policies_by_intent)} intents")
    print(f"[OK] Lexicon:  {len(EXPANDED_LEXICON_ROWS)} entries | langs={dict(lang_counts)}")
    print(f"[OK] Corpus:   {len(corpus_rows)} docs (25/intent) | cs={dict(cs_counts)} | src={dict(src_counts)}")
    print(f"[OK] Held-out: {len(HELDOUT_BENCHMARK)} unseen queries (0 leakage)")


if __name__ == "__main__":
    build_all()
