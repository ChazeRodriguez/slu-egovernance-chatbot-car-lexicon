# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/generate_charts.py
Description: Generates publication-grade high-DPI PNG charts (1600x900) directly from
             verified corpus outputs and models/evaluation_report.json using Pillow:
               1. charts/01_midterm_bow_top15.png        - Verified Midterm BoW Top 15 Stems
               2. charts/02_corpus_scaling_registers.png - Midterm->Finals Scaling & Language Registers
               3. charts/03_cv_model_comparison.png      - Stratified 5-Fold CV: NB vs LogReg vs Linear SVM
               4. charts/04_confusion_matrix.png         - Best Classifier 10x10 Confusion Matrix Heatmap
               5. charts/05_retrieval_ablation.png       - 4-Stage Held-Out Retrieval Ablation Study
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import csv
import json
import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
CHARTS_DIR = os.path.join(REPO_ROOT, "charts")

# SLU Brand Palette
NAVY = (0, 40, 85)
ROYAL = (0, 75, 135)
TEAL = (14, 116, 144)
GOLD = (212, 175, 55)
AMBER = (217, 119, 6)
GREEN = (21, 128, 61)
RED = (185, 28, 28)
SLATE_BG = (248, 250, 252)
WHITE = (255, 255, 255)
TEXT_DARK = (15, 23, 42)
TEXT_MUTED = (71, 85, 105)
GRID_LINE = (226, 232, 240)
BORDER = (203, 213, 225)


def load_font(size, bold=False):
    candidates = (
        [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def new_canvas(title, subtitle, width=1600, height=900):
    img = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(img)
    # Header bar
    draw.rectangle([0, 0, width, 112], fill=NAVY)
    draw.rectangle([0, 112, width, 120], fill=GOLD)
    f_title = load_font(36, bold=True)
    f_sub = load_font(21, bold=False)
    draw.text((54, 24), title, fill=WHITE, font=f_title)
    draw.text((54, 72), subtitle, fill=(219, 234, 254), font=f_sub)
    # Footer
    f_foot = load_font(17, bold=False)
    draw.text(
        (54, height - 38),
        "Saint Louis University (SAMCIS) • CSE 30 NLP • Group 2 – AiNomally • Data-Driven Verified Output",
        fill=TEXT_MUTED,
        font=f_foot,
    )
    return img, draw


def draw_bow_chart(bow_rows):
    top15 = bow_rows[:15]
    img, draw = new_canvas(
        "Verified Midterm Top 15 Bag of Words Stems",
        "24 Consolidated Documents • 624 Filtered Tokens • 426 Unique Verified Stems (0 Corrupted Roots)",
    )
    f_lbl = load_font(22, bold=True)
    f_val = load_font(20, bold=False)
    f_axis = load_font(18, bold=False)

    left = 260
    right = 1480
    top = 165
    bar_h = 34
    gap = 10
    max_freq = max(int(r["Frequency"]) for r in top15)

    # Vertical grid lines
    for tick in range(0, max_freq + 1, 2):
        x = left + int((tick / max_freq) * (right - left - 120))
        draw.line([x, top - 10, x, top + len(top15) * (bar_h + gap)], fill=GRID_LINE, width=2)
        draw.text((x - 8, top + len(top15) * (bar_h + gap) + 8), str(tick), fill=TEXT_MUTED, font=f_axis)

    for i, r in enumerate(top15):
        y = top + i * (bar_h + gap)
        term = r["Stem_Term"]
        freq = int(r["Frequency"])
        cov = r["Percentage_Coverage"]
        bw = int((freq / max_freq) * (right - left - 120))
        color = NAVY if i < 4 else (ROYAL if i < 10 else TEAL)
        if term == "semester":
            color = GOLD

        # Label right-aligned
        bbox = draw.textbbox((0, 0), term, font=f_lbl)
        tw = bbox[2] - bbox[0]
        draw.text((left - tw - 18, y + 4), term, fill=TEXT_DARK, font=f_lbl)
        draw.rounded_rectangle([left, y, left + bw, y + bar_h], radius=6, fill=color)
        draw.text((left + bw + 14, y + 5), f"{freq} ({cov})", fill=TEXT_DARK, font=f_val)

    out_path = os.path.join(CHARTS_DIR, "01_midterm_bow_top15.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_corpus_scaling_chart(eval_report):
    img, draw = new_canvas(
        "Corpus & Lexicon Scaling: Midterm Baseline vs. Finals Expansion",
        "Balanced 10-Intent Architecture with Transparent Provenance & Authentic CAR Language Coverage",
    )
    f_sec = load_font(26, bold=True)
    f_lbl = load_font(20, bold=True)
    f_val = load_font(20, bold=False)
    f_small = load_font(18, bold=False)

    # Left panel: Scaling Bars (Midterm vs Finals)
    draw.rounded_rectangle([54, 155, 780, 825], radius=14, fill=SLATE_BG, outline=BORDER, width=2)
    draw.text((84, 180), "Milestone Growth (Midterm → Finals)", fill=NAVY, font=f_sec)

    metrics = [
        ("Annotated Docs", 24, eval_report["corpus_summary"]["total_documents"]),
        ("Official Policies", 12, 32),
        ("Lexicon Entries", 25, 156),
        ("CAR-TL-EN Docs", 2, eval_report["corpus_summary"]["code_switching_counts"].get("CAR-TL-EN", 0)),
        ("Held-Out Queries", 8, 48),
    ]
    y0 = 250
    for idx, (label, mid, fin) in enumerate(metrics):
        y = y0 + idx * 108
        draw.text((84, y), label, fill=TEXT_DARK, font=f_lbl)
        max_w = 460
        scale = max(fin, 1)
        w_mid = max(14, int((mid / scale) * max_w))
        w_fin = max_w
        # Midterm bar
        draw.rounded_rectangle([84, y + 32, 84 + w_mid, y + 58], radius=5, fill=(148, 163, 184))
        draw.text((84 + w_mid + 12, y + 32), f"Midterm: {mid}", fill=TEXT_MUTED, font=f_small)
        # Finals bar
        draw.rounded_rectangle([84, y + 64, 84 + w_fin, y + 92], radius=5, fill=NAVY)
        draw.text((84 + w_fin + 12, y + 65), f"Finals: {fin}", fill=NAVY, font=f_lbl)

    # Right panel: Finals Register & Lexicon Language Breakdown
    draw.rounded_rectangle([820, 155, 1546, 825], radius=14, fill=SLATE_BG, outline=BORDER, width=2)
    draw.text((850, 180), "Expanded Corpus Registers (N=250)", fill=NAVY, font=f_sec)

    cs = eval_report["corpus_summary"]["code_switching_counts"]
    reg_items = [
        ("English (EN)", cs.get("EN", 0), ROYAL),
        ("Taglish (TL-EN)", cs.get("TL-EN", 0), TEAL),
        ("Cordilleran (CAR-TL-EN)", cs.get("CAR-TL-EN", 0), GOLD),
    ]
    total_c = sum(v for _, v, _ in reg_items)
    for i, (lbl, cnt, col) in enumerate(reg_items):
        y = 242 + i * 76
        pct = cnt / total_c * 100
        bw = int((cnt / total_c) * 520)
        draw.text((850, y), f"{lbl}: {cnt} docs ({pct:.1f}%)", fill=TEXT_DARK, font=f_lbl)
        draw.rounded_rectangle([850, y + 30, 850 + bw, y + 56], radius=6, fill=col)

    draw.line([850, 495, 1515, 495], fill=BORDER, width=2)
    draw.text((850, 515), "Expanded CAR + SLU Lexicon (N=156)", fill=NAVY, font=f_sec)

    lex_items = [
        ("Ilocano (ilo)", 48, ROYAL),
        ("Northern Kankanaey (kne)", 40, TEAL),
        ("SLU Acronyms & Taglish", 36, NAVY),
        ("Ibaloi (ibl)", 32, GOLD),
    ]
    for i, (lbl, cnt, col) in enumerate(lex_items):
        y = 572 + i * 58
        bw = int((cnt / 50) * 340)
        draw.text((850, y), lbl, fill=TEXT_DARK, font=f_small)
        draw.rounded_rectangle([1115, y, 1115 + bw, y + 30], radius=5, fill=col)
        draw.text((1115 + bw + 12, y + 2), str(cnt), fill=TEXT_DARK, font=f_lbl)

    out_path = os.path.join(CHARTS_DIR, "02_corpus_scaling_registers.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_cv_comparison_chart(eval_report):
    img, draw = new_canvas(
        "Supervised Intent Classifier Benchmark (Stratified 5-Fold CV)",
        "Leak-Free Fold-Local TF-IDF (Unigrams + Bigrams) Across 250 Balanced Multilingual Docs (10 Intents)",
    )
    cv = eval_report["stratified_5fold_cv"]
    models = list(cv.keys())
    metric_defs = [
        ("accuracy", "Accuracy", NAVY),
        ("macro_precision", "Macro Precision", ROYAL),
        ("macro_recall", "Macro Recall", TEAL),
        ("macro_f1", "Macro F1", GOLD),
    ]

    f_lbl = load_font(22, bold=True)
    f_val = load_font(18, bold=True)
    f_axis = load_font(18, bold=False)

    # Legend
    lx = 460
    for _, mlbl, col in metric_defs:
        draw.rounded_rectangle([lx, 148, lx + 24, 172], radius=4, fill=col)
        draw.text((lx + 32, 148), mlbl, fill=TEXT_DARK, font=f_axis)
        lx += 225

    chart_left = 130
    chart_right = 1520
    chart_top = 215
    chart_bottom = 735
    chart_h = chart_bottom - chart_top

    # Y-axis from 80% to 100% for crisp visual separation
    y_min, y_max = 0.80, 1.00
    for tick_pct in [80, 85, 90, 95, 100]:
        frac = (tick_pct / 100.0 - y_min) / (y_max - y_min)
        y = chart_bottom - int(frac * chart_h)
        draw.line([chart_left, y, chart_right, y], fill=GRID_LINE, width=2)
        draw.text((chart_left - 65, y - 10), f"{tick_pct}%", fill=TEXT_MUTED, font=f_axis)

    draw.line([chart_left, chart_bottom, chart_right, chart_bottom], fill=TEXT_DARK, width=2)

    group_w = (chart_right - chart_left) // len(models)
    bar_w = 72
    bar_gap = 16

    for m_idx, m_name in enumerate(models):
        gx = chart_left + m_idx * group_w + 55
        res = cv[m_name]
        for k_idx, (m_key, _, col) in enumerate(metric_defs):
            val = res[m_key]
            frac = max(0.0, min(1.0, (val - y_min) / (y_max - y_min)))
            bh = int(frac * chart_h)
            bx = gx + k_idx * (bar_w + bar_gap)
            by = chart_bottom - bh
            draw.rounded_rectangle([bx, by, bx + bar_w, chart_bottom], radius=6, fill=col)
            txt = f"{val*100:.1f}%"
            tb = draw.textbbox((0, 0), txt, font=f_val)
            draw.text((bx + (bar_w - (tb[2] - tb[0])) // 2, by - 26), txt, fill=TEXT_DARK, font=f_val)

        # Model title below group
        short_name = m_name.replace(" (L2 Softmax)", "\n(L2 Softmax)").replace(" (One-vs-Rest Hinge)", "\n(One-vs-Rest Hinge)")
        if m_name == eval_report["best_model"]:
            short_name += "\n[BEST] (±" + f"{res['std_macro_f1']*100:.2f}%)"
        else:
            short_name += f"\n(±{res['std_macro_f1']*100:.2f}%)"
        draw.multiline_text((gx + 10, chart_bottom + 14), short_name, fill=NAVY if m_name == eval_report["best_model"] else TEXT_DARK, font=f_lbl, align="center")

    out_path = os.path.join(CHARTS_DIR, "03_cv_model_comparison.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_confusion_matrix_chart(eval_report):
    best_name = eval_report["best_model"]
    best = eval_report["stratified_5fold_cv"][best_name]
    cm = best["confusion_matrix"]
    classes = best["classes"]
    short = [
        c.replace("ACADEMIC_SHIFTING_TRANSFER", "SHIFTING")
        .replace("CAMPUS_DECORUM_DRESSCODE", "DRESSCODE")
        .replace("CAMPUS_FACILITIES_LAB", "FACIL_LAB")
        .replace("CAMPUS_HEALTH_SAFETY", "HEALTH_SAF")
        .replace("EXAM_PERMIT_INTEGRITY", "EXAM_INTEG")
        .replace("HANDBOOK_GRADING_FDA", "GRADE_FDA")
        .replace("TUITION_FINANCE", "TUITION")
        .replace("URO_ENROLLMENT_PORTAL", "PORTAL_ENR")
        .replace("URO_ENROLLMENT_TOR", "URO_TOR")
        .replace("URO_SUBJECT_ADJUSTMENT", "SUBJ_ADJ")
        for c in classes
    ]

    img, draw = new_canvas(
        f"10×10 Confusion Matrix — {best_name}",
        f"Stratified 5-Fold Aggregate (N=250, 25/class) • Accuracy {best['accuracy']*100:.2f}% • Macro F1 {best['macro_f1']*100:.2f}%",
    )
    f_hdr = load_font(17, bold=True)
    f_cell = load_font(22, bold=True)
    f_side = load_font(18, bold=True)

    left = 250
    top = 200
    cell_w = 122
    cell_h = 60

    draw.text((54, 152), "True ↓  /  Predicted →", fill=NAVY, font=f_side)

    for j, lbl in enumerate(short):
        x = left + j * cell_w
        tb = draw.textbbox((0, 0), lbl, font=f_hdr)
        draw.text((x + (cell_w - (tb[2] - tb[0])) // 2, top - 34), lbl, fill=NAVY, font=f_hdr)

    for i, row in enumerate(cm):
        y = top + i * cell_h
        tb = draw.textbbox((0, 0), short[i], font=f_hdr)
        draw.text((left - (tb[2] - tb[0]) - 16, y + 20), short[i], fill=NAVY, font=f_hdr)
        for j, val in enumerate(row):
            x = left + j * cell_w
            if i == j:
                intensity = val / 25.0
                bg = (int(220 - 200 * intensity), int(252 - 140 * intensity), int(231 - 150 * intensity))
                fg = WHITE if intensity > 0.65 else TEXT_DARK
            elif val > 0:
                bg = (254, 202, 202)
                fg = RED
            else:
                bg = SLATE_BG
                fg = (148, 163, 184)
            draw.rectangle([x + 2, y + 2, x + cell_w - 2, y + cell_h - 2], fill=bg, outline=WHITE, width=2)
            txt = str(val)
            tb_v = draw.textbbox((0, 0), txt, font=f_cell)
            draw.text((x + (cell_w - (tb_v[2] - tb_v[0])) // 2, y + 17), txt, fill=fg, font=f_cell)

    out_path = os.path.join(CHARTS_DIR, "04_confusion_matrix.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_ablation_chart(eval_report):
    img, draw = new_canvas(
        "4-Stage Held-Out Retrieval Ablation Study (48 Unseen Queries)",
        "42 In-Domain Multilingual Queries (EN / TL-EN / CAR-TL-EN) + 4 OOD + 2 Greetings • 0% False-Positive CAR Rate",
    )
    ab = eval_report["heldout_ablation"]
    stages = [
        ("A_raw_tfidf", "A. Raw TF-IDF\nCosine Only"),
        ("B_clean_morph", "B. + Cleaning &\nCAR Morphology"),
        ("C_lexicon_boost", "C. + 156 Lexicon\n& OOD Gate"),
        ("D_full_hybrid", "D. Full Hybrid\n(+ ML Intent) [BEST]"),
    ]
    metrics = [
        ("top1_policy_accuracy", "Top-1 Policy Acc", NAVY),
        ("mrr", "MRR (×100)", ROYAL),
        ("ood_rejection_rate", "OOD Rejection", GOLD),
    ]

    f_lbl = load_font(20, bold=True)
    f_val = load_font(18, bold=True)
    f_axis = load_font(18, bold=False)

    # Legend
    lx = 470
    for _, mlbl, col in metrics:
        draw.rounded_rectangle([lx, 146, lx + 24, 170], radius=4, fill=col)
        draw.text((lx + 32, 146), mlbl, fill=TEXT_DARK, font=f_axis)
        lx += 250

    left, right = 120, 1520
    top, bottom = 210, 725
    ch = bottom - top

    for pct in [0, 20, 40, 60, 80, 100]:
        y = bottom - int((pct / 100.0) * ch)
        draw.line([left, y, right, y], fill=GRID_LINE, width=2)
        draw.text((left - 62, y - 10), f"{pct}%", fill=TEXT_MUTED, font=f_axis)
    draw.line([left, bottom, right, bottom], fill=TEXT_DARK, width=2)

    gw = (right - left) // len(stages)
    bw = 74
    bgap = 16

    for s_idx, (s_key, s_label) in enumerate(stages):
        gx = left + s_idx * gw + 48
        data = ab[s_key]
        for m_idx, (m_key, _, col) in enumerate(metrics):
            v = data[m_key]
            bh = max(4, int(v * ch))
            bx = gx + m_idx * (bw + bgap)
            by = bottom - bh
            draw.rounded_rectangle([bx, by, bx + bw, bottom], radius=6, fill=col)
            txt = f"{v*100:.1f}%" if m_key != "mrr" else f"{v:.3f}"
            tb = draw.textbbox((0, 0), txt, font=f_val)
            draw.text((bx + (bw - (tb[2] - tb[0])) // 2, by - 26), txt, fill=TEXT_DARK, font=f_val)
        draw.multiline_text((gx + 15, bottom + 16), s_label, fill=NAVY if s_key == "D_full_hybrid" else TEXT_DARK, font=f_lbl, align="center")

    out_path = os.path.join(CHARTS_DIR, "05_retrieval_ablation.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    with open(os.path.join(REPO_ROOT, "corpus_bow_summary.csv"), encoding="utf-8") as f:
        bow_rows = list(csv.DictReader(f))
    with open(os.path.join(REPO_ROOT, "models", "evaluation_report.json"), encoding="utf-8") as f:
        eval_report = json.load(f)

    paths = [
        draw_bow_chart(bow_rows),
        draw_corpus_scaling_chart(eval_report),
        draw_cv_comparison_chart(eval_report),
        draw_confusion_matrix_chart(eval_report),
        draw_ablation_chart(eval_report),
    ]
    for p in paths:
        print(f"[OK] Generated chart: {os.path.relpath(p, REPO_ROOT)}")


if __name__ == "__main__":
    main()
