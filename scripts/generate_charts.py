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

# SLU + Canva EAG-QJ6Vos4 Graph-Paper Palette
NAVY = (0, 40, 85)
ROYAL = (0, 75, 135)
TEAL = (14, 116, 144)
GOLD = (212, 175, 55)
AMBER = (217, 119, 6)
GREEN = (21, 128, 61)
RED = (185, 28, 28)
SLATE_BG = (248, 250, 252)
CREAM_PAPER = (250, 248, 243)
PAPER_GRID = (212, 230, 241)
CANVA_INK = (13, 10, 26)
CANVA_VIOLET = (109, 40, 217)
CANVA_PINK = (219, 39, 119)
CANVA_CORAL = (235, 106, 72)
WHITE = (255, 255, 255)
TEXT_DARK = (15, 23, 42)
TEXT_MUTED = (71, 85, 105)
GRID_LINE = (226, 232, 240)
BORDER = (203, 213, 225)


def new_graph_paper_canvas(width, height, step=40):
    """Creates a Canva EAG-QJ6Vos4 warm cream graph-paper canvas."""
    img = Image.new("RGB", (width, height), CREAM_PAPER)
    draw = ImageDraw.Draw(img)
    for x in range(0, width, step):
        draw.line([x, 0, x, height], fill=PAPER_GRID, width=2)
    for y in range(0, height, step):
        draw.line([0, y, width, y], fill=PAPER_GRID, width=2)
    return img, draw


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


def draw_corpus_scaling_chart(eval_report, counts):
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

    total_docs = eval_report["corpus_summary"]["total_documents"]
    metrics = [
        ("Annotated Docs", 24, total_docs),
        ("Official Policies", 12, counts["policies"]),
        ("Lexicon Entries", 25, counts["lex_total"]),
        ("CAR-TL-EN Docs", 2, eval_report["corpus_summary"]["code_switching_counts"].get("CAR-TL-EN", 0)),
        ("Held-Out Queries", 8, counts["benchmark"]),
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
    draw.text((850, 180), f"Expanded Corpus Registers (N={total_docs})", fill=NAVY, font=f_sec)

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
    draw.text((850, 515), f"Expanded CAR + SLU Lexicon (N={counts['lex_total']})", fill=NAVY, font=f_sec)

    lex_items = [
        ("Ilocano (ilo)", counts["lex_ilo"], ROYAL),
        ("SLU Acronyms & Taglish", counts["lex_slu"], NAVY),
        ("Northern Kankanaey (kne)", counts["lex_kne"], TEAL),
        ("Ibaloi (ibl)", counts["lex_ibl"], GOLD),
    ]
    max_lex = max(v for _, v, _ in lex_items)
    for i, (lbl, cnt, col) in enumerate(lex_items):
        y = 572 + i * 58
        bw = int((cnt / max_lex) * 340)
        draw.text((850, y), lbl, fill=TEXT_DARK, font=f_small)
        draw.rounded_rectangle([1115, y, 1115 + bw, y + 30], radius=5, fill=col)
        draw.text((1115 + bw + 12, y + 2), str(cnt), fill=TEXT_DARK, font=f_lbl)

    out_path = os.path.join(CHARTS_DIR, "02_corpus_scaling_registers.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_cv_comparison_chart(eval_report):
    total_docs = eval_report["corpus_summary"]["total_documents"]
    img, draw = new_canvas(
        "Supervised Intent Classifier Benchmark (Stratified 5-Fold CV)",
        f"Leak-Free Fold-Local Sublinear TF-IDF (1+log tf) Across {total_docs} Balanced Docs (10 Intents)",
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

    total_docs = eval_report["corpus_summary"]["total_documents"]
    per_cls = eval_report["corpus_summary"]["docs_per_intent"]
    img, draw = new_canvas(
        f"10×10 Confusion Matrix — {best_name}",
        f"Stratified 5-Fold Aggregate (N={total_docs}, {per_cls}/class) • Accuracy {best['accuracy']*100:.2f}% • Macro F1 {best['macro_f1']*100:.2f}%",
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
                intensity = min(1.0, val / float(max(per_cls, 1)))
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


def draw_ablation_chart(eval_report, counts):
    ab = eval_report["heldout_ablation"]
    in_dom = ab["D_full_hybrid"]["in_domain_queries"]
    img, draw = new_canvas(
        f"4-Stage Held-Out Retrieval Ablation Study ({counts['benchmark']} Unseen Queries)",
        f"{in_dom} In-Domain Multilingual Queries (EN / TL-EN / CAR-TL-EN) + 4 OOD + 2 Greetings • 0% False-Positive CAR Rate",
    )
    stages = [
        ("A_raw_tfidf", "A. Raw TF-IDF\nCosine Only"),
        ("B_clean_morph", "B. + Cleaning &\nCAR Morphology"),
        ("C_lexicon_boost", f"C. + {counts['lex_total']} Lexicon\n& OOD Gate"),
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


# ==============================================================================
# LARGE-PRINT CLASSROOM TV CHARTS (ZERO HEADER CHROME, 2X GIANT TYPOGRAPHY)
# Designed specifically for legibility from the back of a large classroom on a
# standard-sized TV (6-10 meters viewing distance).
# ==============================================================================

def draw_tv_bow_top10(bow_rows):
    top10 = bow_rows[:10]
    W, H = 1600, 740
    img, draw = new_graph_paper_canvas(W, H, step=40)

    f_lbl = load_font(36, bold=True)
    f_val = load_font(32, bold=True)
    f_axis = load_font(26, bold=True)

    left = 320
    right = 1330
    top = 24
    bar_h = 52
    gap = 14
    max_freq = max(int(r["Frequency"]) for r in top10)

    for tick in [0, 5, 10, 15, 20]:
        if tick > max_freq + 2:
            continue
        x = left + int((tick / max_freq) * (right - left))
        draw.line([x, top, x, top + len(top10) * (bar_h + gap)], fill=(186, 214, 232), width=3)
        draw.text((x - 14, top + len(top10) * (bar_h + gap) + 8), str(tick), fill=CANVA_INK, font=f_axis)

    for i, r in enumerate(top10):
        y = top + i * (bar_h + gap)
        term = r["Stem_Term"]
        freq = int(r["Frequency"])
        cov = r["Percentage_Coverage"]
        bw = int((freq / max_freq) * (right - left))
        color = CANVA_CORAL if term == "semester" else (CANVA_INK if i < 3 else (CANVA_VIOLET if i < 7 else TEAL))

        tb = draw.textbbox((0, 0), term, font=f_lbl)
        draw.text((left - (tb[2] - tb[0]) - 22, y + 6), term, fill=CANVA_INK, font=f_lbl)
        draw.rounded_rectangle([left, y, left + bw, y + bar_h], radius=10, fill=color)
        draw.text((left + bw + 20, y + 8), f"{freq}  ({cov})", fill=CANVA_CORAL if term == "semester" else CANVA_INK, font=f_val)

    out_path = os.path.join(CHARTS_DIR, "tv_01_bow_top10.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_tv_corpus_scaling(eval_report, counts):
    W, H = 1600, 740
    img, draw = new_graph_paper_canvas(W, H, step=40)

    f_sec = load_font(36, bold=True)
    f_lbl = load_font(30, bold=True)
    f_val = load_font(30, bold=True)
    f_sub = load_font(26, bold=True)

    total_docs = eval_report["corpus_summary"]["total_documents"]
    car_docs = eval_report["corpus_summary"]["code_switching_counts"].get("CAR-TL-EN", 0)

    # Left panel: Midterm vs Finals Growth
    draw.rounded_rectangle([16, 16, 860, H - 16], radius=18, fill=WHITE, outline=CANVA_INK, width=4)
    draw.text((48, 36), "Midterm → Finals Growth", fill=CANVA_INK, font=f_sec)

    metrics = [
        ("Corpus Docs", 24, total_docs, f"{total_docs/24:.1f}×"),
        ("Official Policies", 12, counts["policies"], f"{counts['policies']/12:.1f}×"),
        ("CAR Lexicon", 25, counts["lex_total"], f"{counts['lex_total']/25:.1f}×"),
        ("CAR-TL-EN Docs", 2, car_docs, f"{car_docs//2}×"),
        ("Unseen Queries", 8, counts["benchmark"], f"{counts['benchmark']/8:.1f}×"),
    ]
    y0 = 104
    max_bar = 470
    for idx, (label, mid, fin, mult) in enumerate(metrics):
        y = y0 + idx * 122
        draw.text((48, y), f"{label}", fill=CANVA_INK, font=f_lbl)
        draw.text((695, y), mult, fill=CANVA_PINK, font=f_lbl)
        w_mid = max(24, int((mid / max(fin, 1)) * max_bar))
        draw.rounded_rectangle([48, y + 40, 48 + w_mid, y + 70], radius=6, fill=(148, 163, 184))
        draw.text((48 + w_mid + 16, y + 38), f"Mid: {mid}", fill=TEXT_MUTED, font=f_sub)
        draw.rounded_rectangle([48, y + 76, 48 + max_bar, y + 110], radius=8, fill=CANVA_VIOLET)
        draw.text((48 + max_bar + 16, y + 75), f"Fin: {fin}", fill=CANVA_INK, font=f_val)

    # Right panel: Finals Registers (top) + CAR Lexicon (bottom)
    draw.rounded_rectangle([888, 16, W - 16, H - 16], radius=18, fill=WHITE, outline=CANVA_INK, width=4)
    draw.text((920, 36), f"{total_docs} Docs by Register", fill=CANVA_INK, font=f_sec)

    cs = eval_report["corpus_summary"]["code_switching_counts"]
    reg_items = [
        ("English (EN)", cs.get("EN", 0), CANVA_INK),
        ("Taglish (TL-EN)", cs.get("TL-EN", 0), CANVA_VIOLET),
        ("Cordilleran (CAR)", cs.get("CAR-TL-EN", 0), CANVA_CORAL),
    ]
    total_c = sum(v for _, v, _ in reg_items)
    max_reg = max(v for _, v, _ in reg_items)
    for i, (lbl, cnt, col) in enumerate(reg_items):
        y = 100 + i * 86
        pct = cnt / total_c * 100
        bw = int((cnt / max_reg) * 580)
        draw.text((920, y), f"{lbl}: {cnt} ({pct:.0f}%)", fill=CANVA_INK, font=f_sub)
        draw.rounded_rectangle([920, y + 36, 920 + bw, y + 68], radius=8, fill=col)

    draw.line([920, 376, W - 48, 376], fill=BORDER, width=3)
    draw.text((920, 396), f"{counts['lex_total']} Lexicon Entries", fill=CANVA_INK, font=f_sec)

    lex_items = [
        ("Ilocano (ilo)", counts["lex_ilo"], CANVA_VIOLET),
        ("SLU & Taglish", counts["lex_slu"], CANVA_INK),
        ("Kankanaey (kne)", counts["lex_kne"], TEAL),
        ("Ibaloi (ibl)", counts["lex_ibl"], CANVA_CORAL),
    ]
    max_lex = max(v for _, v, _ in lex_items)
    for i, (lbl, cnt, col) in enumerate(lex_items):
        y = 458 + i * 64
        bw = int((cnt / max_lex) * 280)
        draw.text((920, y + 4), lbl, fill=CANVA_INK, font=f_sub)
        draw.rounded_rectangle([1200, y, 1200 + bw, y + 42], radius=8, fill=col)
        draw.text((1200 + bw + 16, y + 4), str(cnt), fill=CANVA_INK, font=f_val)

    out_path = os.path.join(CHARTS_DIR, "tv_02_corpus_scaling.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_tv_cv_comparison(eval_report):
    W, H = 1600, 620
    img, draw = new_graph_paper_canvas(W, H, step=40)

    cv = eval_report["stratified_5fold_cv"]
    best_name = eval_report["best_model"]
    models = [
        ("Linear SVM (One-vs-Rest Hinge)", "Linear SVM\n(OvR Hinge)"),
        ("Multinomial Naive Bayes", "Multinomial NB\n(Laplace)"),
        ("Logistic Regression (L2 Softmax)", "Logistic Reg.\n(L2 Softmax)"),
    ]
    models.sort(key=lambda m: (m[0] != best_name, -cv[m[0]]["macro_f1"]))
    metric_defs = [
        ("accuracy", "Accuracy", CANVA_INK),
        ("macro_f1", "Macro F1", CANVA_CORAL),
    ]

    f_lbl = load_font(34, bold=True)
    f_val = load_font(34, bold=True)
    f_axis = load_font(28, bold=True)

    lx = 520
    for _, mlbl, col in metric_defs:
        draw.rounded_rectangle([lx, 18, lx + 36, 54], radius=6, fill=col)
        draw.text((lx + 48, 18), mlbl, fill=CANVA_INK, font=f_lbl)
        lx += 320

    chart_left = 150
    chart_right = 1550
    chart_top = 90
    chart_bottom = 485
    chart_h = chart_bottom - chart_top

    y_min, y_max = 0.88, 0.98
    for tick_pct in [88, 90, 92, 94, 96, 98]:
        frac = (tick_pct / 100.0 - y_min) / (y_max - y_min)
        y = chart_bottom - int(frac * chart_h)
        draw.line([chart_left, y, chart_right, y], fill=(186, 214, 232), width=3)
        draw.text((chart_left - 96, y - 16), f"{tick_pct}%", fill=CANVA_INK, font=f_axis)

    draw.line([chart_left, chart_bottom, chart_right, chart_bottom], fill=CANVA_INK, width=4)

    group_w = (chart_right - chart_left) // len(models)
    bar_w = 148
    bar_gap = 28

    for m_idx, (m_key, m_disp) in enumerate(models):
        gx = chart_left + m_idx * group_w + 74
        res = cv[m_key]
        for k_idx, (mk, _, col) in enumerate(metric_defs):
            val = res[mk]
            frac = max(0.0, min(1.0, (val - y_min) / (y_max - y_min)))
            bh = int(frac * chart_h)
            bx = gx + k_idx * (bar_w + bar_gap)
            by = chart_bottom - bh
            draw.rounded_rectangle([bx, by, bx + bar_w, chart_bottom], radius=10, fill=col)
            txt = f"{val*100:.2f}%"
            tb = draw.textbbox((0, 0), txt, font=f_val)
            draw.text((bx + (bar_w - (tb[2] - tb[0])) // 2, by - 44), txt, fill=CANVA_INK, font=f_val)

        center_x = gx + (2 * bar_w + bar_gap) // 2
        lines = (m_disp + ("\n[BEST]" if m_key == best_name else "")).split("\n")[:2]
        if m_key == best_name:
            lines = [m_disp.split("\n")[0], "[BEST MODEL]"]
        for li, ln in enumerate(lines):
            tb = draw.textbbox((0, 0), ln, font=f_lbl)
            col_t = CANVA_PINK if (m_key == best_name and li == 1) else CANVA_INK
            draw.text((center_x - (tb[2] - tb[0]) // 2, chart_bottom + 18 + li * 42), ln, fill=col_t, font=f_lbl)

    out_path = os.path.join(CHARTS_DIR, "tv_03_cv_comparison.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_tv_confusion_matrix(eval_report):
    best_name = eval_report["best_model"]
    best = eval_report["stratified_5fold_cv"][best_name]
    cm = best["confusion_matrix"]
    classes = best["classes"]
    per_cls = float(max(eval_report["corpus_summary"]["docs_per_intent"], 1))
    short = [
        c.replace("ACADEMIC_SHIFTING_TRANSFER", "SHIFT")
        .replace("CAMPUS_DECORUM_DRESSCODE", "DRESS")
        .replace("CAMPUS_FACILITIES_LAB", "LABS")
        .replace("CAMPUS_HEALTH_SAFETY", "HEALTH")
        .replace("EXAM_PERMIT_INTEGRITY", "EXAM")
        .replace("HANDBOOK_GRADING_FDA", "GRADE")
        .replace("TUITION_FINANCE", "FINANCE")
        .replace("URO_ENROLLMENT_PORTAL", "PORTAL")
        .replace("URO_ENROLLMENT_TOR", "TOR")
        .replace("URO_SUBJECT_ADJUSTMENT", "ADJUST")
        for c in classes
    ]

    W, H = 1600, 740
    img, draw = new_graph_paper_canvas(W, H, step=40)

    f_hdr = load_font(26, bold=True)
    f_cell = load_font(34, bold=True)
    f_zero = load_font(26, bold=False)

    left = 200
    top = 62
    cell_w = 136
    cell_h = 66

    draw.text((16, 16), "True ↓ / Pred →", fill=CANVA_INK, font=load_font(24, bold=True))

    for j, lbl in enumerate(short):
        x = left + j * cell_w
        tb = draw.textbbox((0, 0), lbl, font=f_hdr)
        draw.text((x + (cell_w - (tb[2] - tb[0])) // 2, 16), lbl, fill=CANVA_INK, font=f_hdr)

    for i, row in enumerate(cm):
        y = top + i * cell_h
        tb = draw.textbbox((0, 0), short[i], font=f_hdr)
        draw.text((left - (tb[2] - tb[0]) - 18, y + 18), short[i], fill=CANVA_INK, font=f_hdr)
        for j, val in enumerate(row):
            x = left + j * cell_w
            if i == j:
                intensity = min(1.0, val / per_cls)
                bg = (int(210 - 190 * intensity), int(248 - 135 * intensity), int(225 - 145 * intensity))
                fg = WHITE if intensity > 0.65 else TEXT_DARK
                txt = str(val)
                font_use = f_cell
            elif val > 0:
                bg = (254, 202, 202)
                fg = RED
                txt = str(val)
                font_use = f_cell
            else:
                bg = WHITE
                fg = (168, 178, 192)
                txt = "·"
                font_use = f_zero
            draw.rectangle([x + 3, y + 3, x + cell_w - 3, y + cell_h - 3], fill=bg, outline=PAPER_GRID, width=2)
            tb_v = draw.textbbox((0, 0), txt, font=font_use)
            draw.text((x + (cell_w - (tb_v[2] - tb_v[0])) // 2, y + (cell_h - (tb_v[3] - tb_v[1])) // 2 - 4), txt, fill=fg, font=font_use)

    out_path = os.path.join(CHARTS_DIR, "tv_04_confusion_matrix.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def draw_tv_ablation(eval_report):
    W, H = 1600, 720
    img, draw = new_graph_paper_canvas(W, H, step=40)

    ab = eval_report["heldout_ablation"]
    stages = [
        ("A_raw_tfidf", "A. Raw\nTF-IDF"),
        ("B_clean_morph", "B. + Clean &\nCAR Morph"),
        ("C_lexicon_boost", "C. + Lexicon\n& OOD Gate"),
        ("D_full_hybrid", "D. Full Hybrid\n(+ ML) [BEST]"),
    ]
    metrics = [
        ("top1_policy_accuracy", "Top-1 Policy Acc", CANVA_VIOLET),
        ("ood_rejection_rate", "OOD Rejection", CANVA_CORAL),
    ]

    f_lbl = load_font(30, bold=True)
    f_val = load_font(30, bold=True)
    f_mrr = load_font(24, bold=True)
    f_axis = load_font(26, bold=True)

    lx = 430
    for _, mlbl, col in metrics:
        draw.rounded_rectangle([lx, 18, lx + 34, 52], radius=6, fill=col)
        draw.text((lx + 46, 18), mlbl, fill=CANVA_INK, font=f_lbl)
        lx += 380

    left, right = 135, 1560
    top, bottom = 100, 565
    ch = bottom - top

    for pct in [0, 25, 50, 75, 100]:
        y = bottom - int((pct / 100.0) * ch)
        draw.line([left, y, right, y], fill=(186, 214, 232), width=3)
        draw.text((left - 92, y - 14), f"{pct}%", fill=CANVA_INK, font=f_axis)
    draw.line([left, bottom, right, bottom], fill=CANVA_INK, width=4)

    gw = (right - left) // len(stages)
    bw = 112
    bgap = 22

    for s_idx, (s_key, s_label) in enumerate(stages):
        gx = left + s_idx * gw + 54
        data = ab[s_key]
        for m_idx, (m_key, _, col) in enumerate(metrics):
            v = data[m_key]
            bh = max(8, int(v * ch))
            bx = gx + m_idx * (bw + bgap)
            by = bottom - bh
            draw.rounded_rectangle([bx, by, bx + bw, bottom], radius=8, fill=col)
            txt = f"{v*100:.1f}%" if v > 0 else "0%"
            tb = draw.textbbox((0, 0), txt, font=f_val)
            draw.text((bx + (bw - (tb[2] - tb[0])) // 2, by - 40), txt, fill=CANVA_INK, font=f_val)

        cx = gx + (2 * bw + bgap) // 2
        lines = s_label.split("\n")
        for li, ln in enumerate(lines):
            tb = draw.textbbox((0, 0), ln, font=f_lbl)
            draw.text((cx - (tb[2] - tb[0]) // 2, bottom + 14 + li * 38), ln, fill=CANVA_PINK if s_key == "D_full_hybrid" else CANVA_INK, font=f_lbl)
        mrr_txt = f"MRR {data['mrr']:.3f}"
        tb_m = draw.textbbox((0, 0), mrr_txt, font=f_mrr)
        draw.text((cx - (tb_m[2] - tb_m[0]) // 2, bottom + 94), mrr_txt, fill=CANVA_VIOLET, font=f_mrr)

    out_path = os.path.join(CHARTS_DIR, "tv_05_ablation.png")
    img.save(out_path, dpi=(300, 300))
    return out_path


def load_live_counts():
    with open(os.path.join(REPO_ROOT, "data", "expanded", "slu_official_policies_v2.json"), encoding="utf-8") as f:
        pols = json.load(f)
    with open(os.path.join(REPO_ROOT, "data", "expanded", "slu_car_domain_lexicon_v2.csv"), encoding="utf-8-sig") as f:
        lex = list(csv.DictReader(f))
    with open(os.path.join(REPO_ROOT, "data", "expanded", "heldout_benchmark.json"), encoding="utf-8") as f:
        bench = json.load(f)
    return {
        "policies": len(pols),
        "lex_total": len(lex),
        "lex_ilo": sum(1 for r in lex if r["Language_ISO"] == "ilo"),
        "lex_kne": sum(1 for r in lex if r["Language_ISO"] == "kne"),
        "lex_ibl": sum(1 for r in lex if r["Language_ISO"] == "ibl"),
        "lex_slu": sum(1 for r in lex if r["Language_ISO"] not in ("ilo", "kne", "ibl")),
        "benchmark": len(bench),
    }


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    with open(os.path.join(REPO_ROOT, "corpus_bow_summary.csv"), encoding="utf-8") as f:
        bow_rows = list(csv.DictReader(f))
    with open(os.path.join(REPO_ROOT, "models", "evaluation_report.json"), encoding="utf-8") as f:
        eval_report = json.load(f)
    counts = load_live_counts()

    paths = [
        draw_bow_chart(bow_rows),
        draw_corpus_scaling_chart(eval_report, counts),
        draw_cv_comparison_chart(eval_report),
        draw_confusion_matrix_chart(eval_report),
        draw_ablation_chart(eval_report, counts),
        draw_tv_bow_top10(bow_rows),
        draw_tv_corpus_scaling(eval_report, counts),
        draw_tv_cv_comparison(eval_report),
        draw_tv_confusion_matrix(eval_report),
        draw_tv_ablation(eval_report),
    ]
    for p in paths:
        print(f"[OK] Generated chart: {os.path.relpath(p, REPO_ROOT)}")


if __name__ == "__main__":
    main()
