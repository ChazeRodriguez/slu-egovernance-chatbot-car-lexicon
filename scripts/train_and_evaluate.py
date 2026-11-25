# -*- coding: utf-8 -*-
"""
CSE 30: CS Special Topics (Natural Language Processing)
Saint Louis University - Department of Computer Science
Script: scripts/train_and_evaluate.py
Description: Zero-dependency pure-Python supervised NLP intent classification & retrieval
             evaluation suite:
               - Multinomial Naive Bayes (Lidstone smoothed TF-IDF)
               - L2-Regularized Multinomial Logistic Regression (Softmax)
               - One-vs-Rest Linear SVM (L2-Regularized Hinge Loss)
             Evaluated via leak-free Stratified 5-Fold Cross-Validation (TF-IDF vocab/IDF
             fitted strictly within each training fold), plus a 4-stage Retrieval Ablation
             Study across 48 strictly held-out unseen multilingual, OOD, and adversarial queries.
Author: Group 2 - AiNomally (Angcaway, Delin, Hernandez, Rodriguez, Sibayan)
"""

import csv
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPT_DIR)

from car_morphology import QUERY_STOPWORDS, bilingual_stemmer
from data_cleaning import clean_text
import slu_chatbot_engine as eng


def extract_features(text):
    cleaned = clean_text(text, preserve_car_hyphens=True)
    raw_tokens = eng.tokenize(cleaned)
    filtered = [
        t for t in raw_tokens
        if t not in QUERY_STOPWORDS and len(t) > 1 and (not t.isdigit() or t in eng.POLICY_NUMERIC_TOKENS or (50 <= int(t) <= 99))
    ]
    stems = [bilingual_stemmer(t) for t in filtered]
    bigrams = eng.generate_ngrams(stems, n=2)
    return stems + bigrams


class SparseTfidfVectorizer:
    """Fits TF-IDF vocabulary strictly on training documents and outputs L2-normalized sparse dicts."""

    def __init__(self, min_df=1):
        self.min_df = min_df
        self.vocab = {}
        self.idf = []

    def fit(self, feature_lists):
        n_docs = len(feature_lists)
        df = Counter()
        for feats in feature_lists:
            for f in set(feats):
                df[f] += 1
        kept = sorted([f for f, c in df.items() if c >= self.min_df])
        self.vocab = {f: i for i, f in enumerate(kept)}
        self.idf = [math.log((1.0 + n_docs) / (1.0 + df[f])) + 1.0 for f in kept]
        return self

    def transform_one(self, feats):
        tf = Counter(feats)
        vec = {}
        norm_sq = 0.0
        for f, count in tf.items():
            idx = self.vocab.get(f)
            if idx is not None:
                w = (1.0 + math.log(count)) * self.idf[idx]
                vec[idx] = w
                norm_sq += w * w
        if norm_sq > 0.0:
            inv_norm = 1.0 / math.sqrt(norm_sq)
            for idx in vec:
                vec[idx] *= inv_norm
        return vec

    def transform(self, feature_lists):
        return [self.transform_one(feats) for feats in feature_lists]


class MultinomialNBClassifier:
    """Lidstone-smoothed Multinomial Naive Bayes over TF-IDF sparse vectors."""

    def __init__(self, alpha=0.35):
        self.alpha = alpha
        self.classes = []
        self.log_priors = []
        self.log_probs = []

    def fit(self, X, y, n_features):
        self.classes = sorted(set(y))
        c_to_i = {c: i for i, c in enumerate(self.classes)}
        n_classes = len(self.classes)
        doc_counts = [0] * n_classes
        feat_sums = [[0.0] * n_features for _ in range(n_classes)]
        class_totals = [0.0] * n_classes

        for vec, label in zip(X, y):
            ci = c_to_i[label]
            doc_counts[ci] += 1
            for f_idx, val in vec.items():
                feat_sums[ci][f_idx] += val
                class_totals[ci] += val

        total_docs = float(len(y))
        self.log_priors = [math.log(c / total_docs) for c in doc_counts]
        self.log_probs = []
        for ci in range(n_classes):
            denom = class_totals[ci] + self.alpha * n_features
            self.log_probs.append([math.log((feat_sums[ci][fi] + self.alpha) / denom) for fi in range(n_features)])
        return self

    def predict_one(self, vec):
        best_c = None
        best_score = -1e18
        for ci, cls in enumerate(self.classes):
            s = self.log_priors[ci]
            lp = self.log_probs[ci]
            for f_idx, val in vec.items():
                s += val * lp[f_idx]
            if s > best_score:
                best_score = s
                best_c = cls
        return best_c

    def predict(self, X):
        return [self.predict_one(v) for v in X]

    def export_dict(self, vectorizer):
        return {
            "model_type": "multinomial_nb",
            "classes": self.classes,
            "vocab": vectorizer.vocab,
            "idf": [round(x, 6) for x in vectorizer.idf],
            "log_priors": [round(x, 6) for x in self.log_priors],
            "log_probs": [[round(x, 6) for x in row] for row in self.log_probs],
        }


class MultinomialLogisticRegression:
    """L2-regularized Multinomial Softmax Logistic Regression trained with deterministic SGD."""

    def __init__(self, lr=1.2, l2=1e-4, epochs=55, seed=42):
        self.lr = lr
        self.l2 = l2
        self.epochs = epochs
        self.seed = seed
        self.classes = []
        self.weights = []
        self.biases = []

    def fit(self, X, y, n_features):
        self.classes = sorted(set(y))
        c_to_i = {c: i for i, c in enumerate(self.classes)}
        n_classes = len(self.classes)
        self.weights = [[0.0] * n_features for _ in range(n_classes)]
        self.biases = [0.0] * n_classes

        rng = random.Random(self.seed)
        indices = list(range(len(X)))

        for epoch in range(self.epochs):
            rng.shuffle(indices)
            step = self.lr / (1.0 + 0.04 * epoch)
            decay = 1.0 - step * self.l2
            for idx in indices:
                vec = X[idx]
                true_ci = c_to_i[y[idx]]
                logits = []
                for ci in range(n_classes):
                    s = self.biases[ci]
                    cw = self.weights[ci]
                    for f_idx, val in vec.items():
                        s += cw[f_idx] * val
                    logits.append(s)
                max_l = max(logits)
                exps = [math.exp(l - max_l) for l in logits]
                denom = sum(exps)
                probs = [e / denom for e in exps]

                for ci in range(n_classes):
                    err = probs[ci] - (1.0 if ci == true_ci else 0.0)
                    self.biases[ci] -= step * err
                    cw = self.weights[ci]
                    for f_idx, val in vec.items():
                        cw[f_idx] = cw[f_idx] * decay - step * err * val
        return self

    def predict_one(self, vec):
        best_c = None
        best_score = -1e18
        for ci, cls in enumerate(self.classes):
            s = self.biases[ci]
            cw = self.weights[ci]
            for f_idx, val in vec.items():
                s += cw[f_idx] * val
            if s > best_score:
                best_score = s
                best_c = cls
        return best_c

    def predict(self, X):
        return [self.predict_one(v) for v in X]

    def export_dict(self, vectorizer):
        return {
            "model_type": "logistic_regression",
            "classes": self.classes,
            "vocab": vectorizer.vocab,
            "idf": [round(x, 6) for x in vectorizer.idf],
            "weights": [[round(x, 6) for x in row] for row in self.weights],
            "biases": [round(x, 6) for x in self.biases],
        }


class OneVsRestLinearSVM:
    """One-vs-Rest L2-regularized Linear SVM (hinge loss subgradient descent)."""

    def __init__(self, lr=0.85, l2=8e-4, epochs=55, seed=42):
        self.lr = lr
        self.l2 = l2
        self.epochs = epochs
        self.seed = seed
        self.classes = []
        self.weights = []
        self.biases = []

    def fit(self, X, y, n_features):
        self.classes = sorted(set(y))
        n_classes = len(self.classes)
        self.weights = [[0.0] * n_features for _ in range(n_classes)]
        self.biases = [0.0] * n_classes

        rng = random.Random(self.seed)
        indices = list(range(len(X)))

        for epoch in range(self.epochs):
            rng.shuffle(indices)
            step = self.lr / (1.0 + 0.05 * epoch)
            decay = 1.0 - step * self.l2
            for idx in indices:
                vec = X[idx]
                true_label = y[idx]
                for ci, cls in enumerate(self.classes):
                    target = 1.0 if true_label == cls else -1.0
                    cw = self.weights[ci]
                    score = self.biases[ci]
                    for f_idx, val in vec.items():
                        score += cw[f_idx] * val
                    if target * score < 1.0:
                        self.biases[ci] += step * target
                        for f_idx, val in vec.items():
                            cw[f_idx] = cw[f_idx] * decay + step * target * val
                    else:
                        for f_idx in vec:
                            cw[f_idx] *= decay
        return self

    def predict_one(self, vec):
        best_c = None
        best_score = -1e18
        for ci, cls in enumerate(self.classes):
            s = self.biases[ci]
            cw = self.weights[ci]
            for f_idx, val in vec.items():
                s += cw[f_idx] * val
            if s > best_score:
                best_score = s
                best_c = cls
        return best_c

    def predict(self, X):
        return [self.predict_one(v) for v in X]

    def export_dict(self, vectorizer):
        return {
            "model_type": "linear_svm",
            "classes": self.classes,
            "vocab": vectorizer.vocab,
            "idf": [round(x, 6) for x in vectorizer.idf],
            "weights": [[round(x, 6) for x in row] for row in self.weights],
            "biases": [round(x, 6) for x in self.biases],
        }


def make_stratified_folds(labels, k=5, seed=42):
    rng = random.Random(seed)
    by_class = defaultdict(list)
    for idx, lab in enumerate(labels):
        by_class[lab].append(idx)
    folds = [[] for _ in range(k)]
    for lab in sorted(by_class.keys()):
        idxs = list(by_class[lab])
        rng.shuffle(idxs)
        for pos, idx in enumerate(idxs):
            folds[pos % k].append(idx)
    return folds


def compute_classification_metrics(y_true, y_pred, classes):
    c_to_i = {c: i for i, c in enumerate(classes)}
    k = len(classes)
    cm = [[0] * k for _ in range(k)]
    for yt, yp in zip(y_true, y_pred):
        cm[c_to_i[yt]][c_to_i[yp]] += 1

    per_class = {}
    precisions, recalls, f1s, supports = [], [], [], []
    correct = 0
    for i, c in enumerate(classes):
        tp = cm[i][i]
        correct += tp
        fp = sum(cm[r][i] for r in range(k) if r != i)
        fn = sum(cm[i][col] for col in range(k) if col != i)
        sup = sum(cm[i])
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        per_class[c] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
            "support": sup,
        }
        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)
        supports.append(sup)

    total = len(y_true)
    acc = correct / total if total > 0 else 0.0
    macro_p = sum(precisions) / k
    macro_r = sum(recalls) / k
    macro_f1 = sum(f1s) / k
    weighted_f1 = sum(f * s for f, s in zip(f1s, supports)) / total if total > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm,
        "classes": classes,
    }


def evaluate_stratified_cv(docs, labels, k=5, seed=42):
    feature_lists = [extract_features(text) for text in docs]
    classes = sorted(set(labels))
    folds = make_stratified_folds(labels, k=k, seed=seed)

    model_builders = {
        "Multinomial Naive Bayes": lambda: MultinomialNBClassifier(alpha=0.35),
        "Logistic Regression (L2 Softmax)": lambda: MultinomialLogisticRegression(lr=1.2, l2=1e-4, epochs=55, seed=seed),
        "Linear SVM (One-vs-Rest Hinge)": lambda: OneVsRestLinearSVM(lr=0.85, l2=8e-4, epochs=55, seed=seed),
    }

    results = {}
    for model_name, builder in model_builders.items():
        all_true = []
        all_pred = []
        fold_accs = []
        fold_f1s = []

        for val_fold_idx in range(k):
            val_indices = set(folds[val_fold_idx])
            train_feats = [feature_lists[i] for i in range(len(docs)) if i not in val_indices]
            train_y = [labels[i] for i in range(len(docs)) if i not in val_indices]
            val_feats = [feature_lists[i] for i in folds[val_fold_idx]]
            val_y = [labels[i] for i in folds[val_fold_idx]]

            # Fit TF-IDF vectorizer strictly inside training fold (zero data leakage)
            vec = SparseTfidfVectorizer(min_df=1).fit(train_feats)
            X_train = vec.transform(train_feats)
            X_val = vec.transform(val_feats)

            clf = builder().fit(X_train, train_y, len(vec.vocab))
            preds = clf.predict(X_val)

            fold_m = compute_classification_metrics(val_y, preds, classes)
            fold_accs.append(fold_m["accuracy"])
            fold_f1s.append(fold_m["macro_f1"])
            all_true.extend(val_y)
            all_pred.extend(preds)

        agg = compute_classification_metrics(all_true, all_pred, classes)
        agg["fold_accuracies"] = fold_accs
        agg["fold_macro_f1s"] = fold_f1s
        agg["std_macro_f1"] = round(
            math.sqrt(sum((x - (sum(fold_f1s) / k)) ** 2 for x in fold_f1s) / k), 4
        )
        results[model_name] = agg

    return results, model_builders, feature_lists


def run_ablation_study(benchmark):
    variants = [
        ("A_raw_tfidf", "Raw TF-IDF Cosine Only", dict(use_cleaning_morph=False, use_lexicon_boost=False, use_ml_intent=False, enable_ood_gate=False)),
        ("B_clean_morph", "+ Acronym-Safe Cleaning & CAR Morphology", dict(use_cleaning_morph=True, use_lexicon_boost=False, use_ml_intent=False, enable_ood_gate=False)),
        ("C_lexicon_boost", "+ 176-Entry CAR/SLU Lexicon Intent Boost", dict(use_cleaning_morph=True, use_lexicon_boost=True, use_ml_intent=False, enable_ood_gate=True, min_confidence=0.14)),
        ("D_full_hybrid", "Full Hybrid (+ Trained ML Intent + OOD Gate)", dict(use_cleaning_morph=True, use_lexicon_boost=True, use_ml_intent=True, enable_ood_gate=True, min_confidence=0.14)),
    ]

    ablation_out = {}
    for key, label, cfg in variants:
        bot = eng.SLUChatbotEngine(dataset="expanded", **cfg)
        in_domain_items = [b for b in benchmark if b["type"] in ("in_domain", "car_trap_en")]
        ood_items = [b for b in benchmark if b["type"] == "ood"]
        greet_items = [b for b in benchmark if b["type"] == "greeting"]
        trap_items = [b for b in benchmark if b["type"] == "car_trap_en"]

        top1 = 0
        top3 = 0
        rr_sum = 0.0
        intent_hits = 0
        by_reg = defaultdict(lambda: {"n": 0, "top1": 0, "top3": 0, "rr": 0.0})
        misses = []

        for item in in_domain_items:
            res = bot.answer_query(item["query"], top_k=3)
            returned = [d["doc_id"] for d in res["top_documents"]]
            exp = set(item["expected_docs"])
            hits = [r for r, did in enumerate(returned, 1) if did in exp]
            reg = item["register"]
            by_reg[reg]["n"] += 1

            if res["predicted_intent"] == item["expected_intent"]:
                intent_hits += 1
            if hits:
                top3 += 1
                by_reg[reg]["top3"] += 1
                rr_sum += 1.0 / hits[0]
                by_reg[reg]["rr"] += 1.0 / hits[0]
                if hits[0] == 1:
                    top1 += 1
                    by_reg[reg]["top1"] += 1
                else:
                    misses.append({"id": item["id"], "returned": returned, "expected": item["expected_docs"]})
            else:
                misses.append({"id": item["id"], "returned": returned, "expected": item["expected_docs"]})

        ood_rejected = sum(1 for item in ood_items if bot.answer_query(item["query"])["is_fallback"])
        greet_ok = sum(1 for item in greet_items if bot.answer_query(item["query"])["predicted_intent"] == "GREETING")
        fp_car = sum(
            1 for item in trap_items
            if bot.answer_query(item["query"])["code_switching"] == "CAR-TL-EN"
        )

        n_in = len(in_domain_items)
        reg_summary = {}
        for reg, st in by_reg.items():
            reg_summary[reg] = {
                "queries": st["n"],
                "top1_accuracy": round(st["top1"] / st["n"], 4),
                "top3_recall": round(st["top3"] / st["n"], 4),
                "mrr": round(st["rr"] / st["n"], 4),
            }

        ablation_out[key] = {
            "label": label,
            "in_domain_queries": n_in,
            "top1_policy_accuracy": round(top1 / n_in, 4),
            "top3_policy_recall": round(top3 / n_in, 4),
            "mrr": round(rr_sum / n_in, 4),
            "intent_accuracy": round(intent_hits / n_in, 4),
            "ood_rejection_rate": round(ood_rejected / len(ood_items), 4),
            "greeting_accuracy": round(greet_ok / len(greet_items), 4),
            "false_positive_car_rate": round(fp_car / len(trap_items), 4),
            "by_register": reg_summary,
            "top1_misses": misses,
        }
    return ablation_out


def main():
    corp_path = os.path.join(REPO_ROOT, "data", "expanded", "annotated_corpus_expanded.csv")
    bench_path = os.path.join(REPO_ROOT, "data", "expanded", "heldout_benchmark.json")
    models_dir = os.path.join(REPO_ROOT, "models")
    os.makedirs(models_dir, exist_ok=True)

    with open(corp_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    docs = [r["Cleaned_Text"] for r in rows]
    labels = [r["Intent_Category"] for r in rows]

    with open(bench_path, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    print(f"[*] Running Stratified 5-Fold Cross-Validation on {len(docs)} balanced documents ({len(set(labels))} intents)...")
    cv_results, builders, feature_lists = evaluate_stratified_cv(docs, labels, k=5, seed=42)

    for name, metrics in cv_results.items():
        print(
            f"  - {name:34s} | Acc={metrics['accuracy']*100:5.2f}% | "
            f"MacroP={metrics['macro_precision']*100:5.2f}% | "
            f"MacroR={metrics['macro_recall']*100:5.2f}% | "
            f"MacroF1={metrics['macro_f1']*100:5.2f}% (±{metrics['std_macro_f1']*100:.2f}%)"
        )

    # Select best model by Macro F1 (tie-break by Accuracy) and fit on full 250-doc corpus
    best_model_name = max(
        cv_results.keys(),
        key=lambda m: (cv_results[m]["macro_f1"], cv_results[m]["accuracy"]),
    )
    full_vec = SparseTfidfVectorizer(min_df=1).fit(feature_lists)
    X_full = full_vec.transform(feature_lists)
    best_clf = builders[best_model_name]().fit(X_full, labels, len(full_vec.vocab))

    model_payload = best_clf.export_dict(full_vec)
    model_payload["best_model_name"] = best_model_name
    model_payload["cv_macro_f1"] = cv_results[best_model_name]["macro_f1"]
    model_payload["cv_accuracy"] = cv_results[best_model_name]["accuracy"]
    model_payload["training_docs"] = len(docs)

    model_path = os.path.join(models_dir, "intent_classifier.json")
    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(model_payload, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved best supervised model ({best_model_name}) -> {model_path} (vocab={len(full_vec.vocab)})")

    print(f"\n[*] Running 4-Stage Retrieval Ablation Study on {len(benchmark)} strictly held-out queries...")
    ablation = run_ablation_study(benchmark)
    for key, res in ablation.items():
        print(
            f"  - {res['label']:45s} | Top-1={res['top1_policy_accuracy']*100:5.1f}% | "
            f"Top-3={res['top3_policy_recall']*100:5.1f}% | MRR={res['mrr']:.4f} | "
            f"OOD={res['ood_rejection_rate']*100:5.1f}% | FP-CAR={res['false_positive_car_rate']*100:4.1f}%"
        )

    # Corpus summary stats for charts & paper
    all_expanded_feats = [t for r in rows for t in eng.tokenize(r["Cleaned_Text"]) if t not in QUERY_STOPWORDS and len(t) > 1 and not t.isdigit()]
    expanded_stems = [bilingual_stemmer(t) for t in all_expanded_feats]
    expanded_bow = Counter(expanded_stems)
    n_intents = len(set(labels))

    report = {
        "corpus_summary": {
            "total_documents": len(rows),
            "intent_classes": n_intents,
            "docs_per_intent": len(rows) // n_intents if n_intents else 0,
            "total_filtered_tokens": len(all_expanded_feats),
            "unique_stems": len(expanded_bow),
            "code_switching_counts": dict(Counter(r["Code_Switching"] for r in rows)),
            "source_type_counts": dict(Counter(r["Source_Type"] for r in rows)),
            "intent_counts": dict(Counter(labels)),
            "top20_expanded_stems": [
                {"term": term, "frequency": freq, "coverage_pct": round(freq / len(expanded_stems) * 100, 2)}
                for term, freq in expanded_bow.most_common(20)
            ],
        },
        "best_model": best_model_name,
        "stratified_5fold_cv": cv_results,
        "heldout_ablation": ablation,
    }

    report_path = os.path.join(models_dir, "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved full evaluation report -> {report_path}")


if __name__ == "__main__":
    main()
