"""Nested source-held-out pilot of a small tabular multi-output MLP.

Research only; does not alter the runtime estimator or recommendation gate.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from plataforma_ltft.htft_external_validation import TARGETS  # noqa: E402
from plataforma_ltft.target_research import PROFILES, eligible, numeric, source  # noqa: E402
from run_research_v14_probabilistic_multitask import (  # noqa: E402
    features, rows_all, score_records, source_balanced_weights,
)


TARGETS_ORDER = tuple(TARGETS)
PARAMETER_GRID = (((3,), 0.1), ((3,), 1.0), ((5,), 0.1), ((5,), 1.0))
CONVERGENCE_WARNINGS = 0
REPORT = ROOT / "data/htft/validation/target_research_v15_mlp_pilot.json"


def _preprocess(train_rows, test_rows, fields):
    x_train, families = features(train_rows, fields)
    x_test, _ = features(test_rows, fields, families)
    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(imputer.fit_transform(x_train))
    x_test_scaled = scaler.transform(imputer.transform(x_test))
    return x_train_scaled, x_test_scaled


def _fit_mlp(train_rows, test_rows, fields, outputs, hidden, alpha, seed=1500):
    global CONVERGENCE_WARNINGS
    x_train, x_test = _preprocess(train_rows, test_rows, fields)
    y_train = np.asarray([[numeric(row, target) for target in outputs] for row in train_rows], dtype=float)
    weights = source_balanced_weights(train_rows)
    y_mean = np.average(y_train, axis=0, weights=weights)
    y_scale = np.sqrt(np.average((y_train - y_mean) ** 2, axis=0, weights=weights))
    y_scale[y_scale < 1e-8] = 1.0
    model = MLPRegressor(
        hidden_layer_sizes=hidden, activation="tanh", solver="lbfgs",
        alpha=alpha, max_iter=800, random_state=seed,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(x_train, (y_train - y_mean) / y_scale, sample_weight=weights)
    CONVERGENCE_WARNINGS += sum(issubclass(item.category, ConvergenceWarning) for item in caught)
    estimate = model.predict(x_test) * y_scale + y_mean
    return np.clip(estimate, 0.0, 100.0), {
        "hidden_layer_sizes": list(hidden), "alpha_l2": alpha,
        "iterations": int(model.n_iter_), "converged": model.n_iter_ < model.max_iter,
    }


def fit_predict_mlp(train_rows, test_rows, fields, outputs=TARGETS_ORDER):
    """Inner source-grouped tune + fit on outer training groups only."""
    inner_groups = sorted({source(row) for row in train_rows})
    scores = []
    for hidden, alpha in PARAMETER_GRID:
        source_maes = []
        for held in inner_groups:
            fit_rows = [row for row in train_rows if source(row) != held]
            validation_rows = [row for row in train_rows if source(row) == held]
            if len({source(row) for row in fit_rows}) < 3 or len(fit_rows) < 6 or not validation_rows:
                continue
            predictions, _ = _fit_mlp(fit_rows, validation_rows, fields, outputs,
                                      hidden, alpha, seed=1500)
            errors = [abs(predictions[i, j] - numeric(row, target))
                      for i, row in enumerate(validation_rows)
                      for j, target in enumerate(outputs)]
            source_maes.append(float(np.mean(errors)))
        scores.append(float(np.mean(source_maes)) if source_maes else float("inf"))
    selected_index = min(range(len(scores)), key=lambda index: (scores[index], PARAMETER_GRID[index][0], PARAMETER_GRID[index][1]))
    hidden, alpha = PARAMETER_GRID[selected_index]
    estimate, fit_meta = _fit_mlp(train_rows, test_rows, fields, outputs, hidden, alpha, seed=1500)
    predictions = {target: estimate[:, index] for index, target in enumerate(outputs)}
    return predictions, {**fit_meta, "inner_source_grouped_mae": scores,
                         "inner_source_groups": len(inner_groups)}


def compare_mlp(rows, profile, outputs=TARGETS_ORDER):
    fields = PROFILES[profile]
    cohort = [row for row in rows if all(eligible(row, target, fields) for target in outputs)]
    groups = sorted({source(row) for row in cohort})
    folds, residuals = [], []
    for held in groups:
        train_rows = [row for row in cohort if source(row) != held]
        test_rows = [row for row in cohort if source(row) == held]
        if len({source(row) for row in train_rows}) < 3:
            folds.append({"held_out": held, "status": "insufficient_training_sources"})
            continue
        prediction, metadata = fit_predict_mlp(train_rows, test_rows, fields, outputs)
        folds.append({"held_out": held, "training_sources": sorted({source(row) for row in train_rows}),
                      "status": "evaluated", "train_rows": len(train_rows),
                      "test_rows": len(test_rows), "model_details": metadata})
        for index, row in enumerate(test_rows):
            for target in outputs:
                predicted = float(prediction[target][index])
                observed = numeric(row, target)
                residuals.append({"row_id": row["row_id"], "source": held,
                                  "target": target, "observed": observed,
                                  "predicted": predicted, "residual": predicted - observed})
    metrics = {
        target: score_records([row for row in residuals if row["target"] == target])
        for target in outputs
    }
    return {"eligible_rows": len(cohort), "sources": len(groups), "folds": folds,
            "residuals": residuals, "metrics_by_target": metrics}


def main():
    rows = rows_all()
    profiles = {profile: compare_mlp(rows, profile) for profile in PROFILES}
    report = {
        "version": "15.0-small-tabular-mlp-pilot",
        "design": "common complete-case cohort; nested outer/inner leave-one-independent-source-out; source-balanced fit; all transforms fit inside folds",
        "architecture": "small multi-output MLP; tanh; hidden layer 3 or 5 units; L2 alpha 0.1 or 1.0; LBFGS; no random row early-stopping split",
        "profiles": profiles,
        "model_promoted": False,
        "recommendation_blocked": True,
        "convergence_warnings": CONVERGENCE_WARNINGS,
        "interpretation": "pilot only; few independent source groups; no operational deployment",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"version": report["version"],
                      "model_promoted": report["model_promoted"],
                      "recommendation_blocked": report["recommendation_blocked"],
                      "convergence_warnings": CONVERGENCE_WARNINGS,
                      "profiles": {profile: {"eligible_rows": item["eligible_rows"],
                                             "sources": item["sources"],
                                             "mae": {target: metric["mae"] for target, metric in item["metrics_by_target"].items()}}
                                  for profile, item in profiles.items()}}, indent=2))


if __name__ == "__main__":
    main()
