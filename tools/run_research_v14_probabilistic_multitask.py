"""Small-data GP uncertainty and joint multi-output HTFT research comparison.

All preprocessing/model fitting is nested inside grouped source holdouts. This
is research-only: no candidate is promoted and no experiment recommendation
is enabled by this report.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.impute import SimpleImputer
from sklearn.linear_model import MultiTaskLasso
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from assess_htft_falkenhagen_2018 import load_new_rows
from plataforma_ltft.htft_external_validation import TARGETS, load_rows
from plataforma_ltft.target_research import PROFILES, compare as compare_v6, eligible, numeric, source
from plataforma_ltft.forest_research import predict as predict_rf

INPUTS = [
    ROOT / "data/htft/htft_external_diverse_catalysts_v1.csv",
    ROOT / "data/htft/htft_femn_new_primary_tables_2026.csv",
    ROOT / "data/htft/htft_falkenhagen_2018_primary_tables.json",
]
REPORT = ROOT / "data/htft/validation/target_research_v14_probabilistic_multitask.json"
TARGETS_ORDER = tuple(TARGETS)
MULTITASK_CONVERGENCE_WARNINGS = 0


def rows_all():
    rows = load_rows(INPUTS[0]) + load_rows(INPUTS[1]) + load_new_rows()
    return [r for r in rows if numeric(r, "temperature_c") is not None
            and 280 <= float(r["temperature_c"]) <= 350]


def features(rows, fields, families=None):
    """Operational-only features shared with v13; never fill missing outcomes."""
    families = sorted({r["family"] for r in rows}) if families is None else families
    x = []
    for row in rows:
        values = []
        for field in fields:
            v = numeric(row, field)
            if v is None:
                values.append(np.nan)
            elif field == "temperature_c":
                values.append(1000.0 / (v + 273.15))
            elif field == "tos_h":
                values.append(math.log1p(v))
            elif field in ("ghsv_ml_gcat_h", "pressure_bar", "h2_co_ratio"):
                values.append(math.log(v))
            else:
                values.append(v)
        values.extend(float(row["family"] == family) for family in families)
        x.append(values)
    return np.asarray(x, dtype=float), families


def source_balanced_weights(rows):
    groups = [source(r) for r in rows]
    count = len(set(groups))
    return np.asarray([len(rows) / (count * groups.count(g)) for g in groups])


def fit_predict(train_rows, test_rows, fields, model_name, outputs):
    global MULTITASK_CONVERGENCE_WARNINGS
    x_train, families = features(train_rows, fields)
    x_test, _ = features(test_rows, fields, families)
    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    xt = scaler.fit_transform(imputer.fit_transform(x_train))
    xv = scaler.transform(imputer.transform(x_test))
    weights = source_balanced_weights(train_rows)
    y = np.asarray([[numeric(r, target) for target in outputs] for r in train_rows], dtype=float)
    predictions = {target: np.full((len(test_rows),), np.nan) for target in outputs}

    if model_name == "multitask_lasso":
        # Shared row-wise feature selection across all endpoints. Weighted
        # centering plus sqrt(weights) gives the source-balanced objective.
        inner_sources = sorted({source(r) for r in train_rows})
        candidates = (0.001, 0.01, 0.1, 1.0)
        scores = []
        for alpha in candidates:
            errs = []
            for held in inner_sources:
                inner_train = [r for r in train_rows if source(r) != held]
                inner_test = [r for r in train_rows if source(r) == held]
                if len({source(r) for r in inner_train}) < 2 or len(inner_train) < 5 or not inner_test:
                    continue
                raw_a, families_a = features(inner_train, fields)
                raw_b, _ = features(inner_test, fields, families_a)
                imp = SimpleImputer(strategy="median", add_indicator=True)
                scl = StandardScaler()
                xa = scl.fit_transform(imp.fit_transform(raw_a))
                xb = scl.transform(imp.transform(raw_b))
                ya = np.asarray([[numeric(r, target) for target in outputs] for r in inner_train], dtype=float)
                yb = np.asarray([[numeric(r, target) for target in outputs] for r in inner_test], dtype=float)
                wa = source_balanced_weights(inner_train)
                xm = np.average(xa, axis=0, weights=wa)
                ym = np.average(ya, axis=0, weights=wa)
                ys = np.sqrt(np.average((ya - ym) ** 2, axis=0, weights=wa))
                ys[ys < 1e-8] = 1.0
                root_w = np.sqrt(wa / np.mean(wa))[:, None]
                model = MultiTaskLasso(alpha=alpha, fit_intercept=False, max_iter=200000, tol=1e-4)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always", ConvergenceWarning)
                    model.fit((xa - xm) * root_w, ((ya - ym) / ys) * root_w)
                MULTITASK_CONVERGENCE_WARNINGS += sum(issubclass(w.category, ConvergenceWarning) for w in caught)
                estimate = ((xb - xm) @ model.coef_.T) * ys + ym
                errs.extend(np.abs(estimate - yb).ravel().tolist())
            scores.append(float(np.mean(errs)) if errs else math.inf)
        best_alpha = candidates[int(np.argmin(scores))]
        xm = np.average(xt, axis=0, weights=weights)
        ym = np.average(y, axis=0, weights=weights)
        ys = np.sqrt(np.average((y - ym) ** 2, axis=0, weights=weights))
        ys[ys < 1e-8] = 1.0
        root_w = np.sqrt(weights / np.mean(weights))[:, None]
        model = MultiTaskLasso(alpha=best_alpha, fit_intercept=False, max_iter=200000, tol=1e-4)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            model.fit((xt - xm) * root_w, ((y - ym) / ys) * root_w)
        MULTITASK_CONVERGENCE_WARNINGS += sum(issubclass(w.category, ConvergenceWarning) for w in caught)
        estimate = ((xv - xm) @ model.coef_.T) * ys + ym
        for j, target in enumerate(outputs):
            predictions[target] = np.clip(estimate[:, j], 0, 100)
        return predictions, {"alpha": best_alpha, "inner_mae_by_alpha": dict(zip(map(str, candidates), scores))}

    for target in outputs:
        j = TARGETS_ORDER.index(target)
        valid = np.flatnonzero(np.isfinite(y[:, j]))
        if len(valid) < 4:
            continue
        if model_name == "gp_matern":
            kernel = ConstantKernel(1.0, constant_value_bounds="fixed") * Matern(length_scale=1.0, length_scale_bounds="fixed", nu=1.5) + WhiteKernel(noise_level=0.1, noise_level_bounds="fixed")
            y_mean = float(np.average(y[valid, j], weights=weights[valid]))
            y_scale = float(np.sqrt(np.average((y[valid, j] - y_mean) ** 2, weights=weights[valid]))) or 1.0
            model = GaussianProcessRegressor(kernel=kernel, alpha=0.05 / weights[valid], normalize_y=False, optimizer=None, random_state=1400 + j)
            model.fit(xt[valid], (y[valid, j] - y_mean) / y_scale)
            mean, std = model.predict(xv, return_std=True)
            predictions[target] = np.clip(mean * y_scale + y_mean, 0, 100)
            predictions[target + "__std"] = std * y_scale
        elif model_name == "random_forest_reference":
            model = RandomForestRegressor(n_estimators=300, min_samples_leaf=2, max_features=0.8, random_state=1400 + j)
            model.fit(xt[valid], y[valid, j], sample_weight=weights[valid])
            predictions[target] = np.clip(model.predict(xv), 0, 100)
        elif model_name == "extra_trees_reference":
            model = ExtraTreesRegressor(n_estimators=300, min_samples_leaf=2, max_features=0.8, random_state=1400 + j)
            model.fit(xt[valid], y[valid, j], sample_weight=weights[valid])
            predictions[target] = np.clip(model.predict(xv), 0, 100)
    return predictions, {}


def score_records(records):
    if not records:
        return {"n": 0, "sources": 0, "mae": None, "mse": None, "rmse": None, "bias": None}
    error = np.asarray([r["predicted"] - r["observed"] for r in records])
    groups = sorted({r["source"] for r in records})
    source_mae = [np.mean([abs(r["predicted"] - r["observed"]) for r in records if r["source"] == g]) for g in groups]
    rng = np.random.default_rng(14021)
    boot = rng.choice(source_mae, (5000, len(groups)), replace=True).mean(axis=1)
    return {"n": len(error), "sources": len(groups), "mae": float(np.mean(np.abs(error))),
            "source_balanced_mae": float(np.mean(source_mae)), "mse": float(np.mean(error**2)),
            "rmse": float(np.sqrt(np.mean(error**2))), "bias": float(np.mean(error)),
            "descriptive_source_bootstrap_95": np.quantile(boot, [0.025, 0.975]).tolist()}


def compare(rows, profile, outputs, model_name):
    fields = PROFILES[profile]
    folds, records = [], []
    sources = sorted({source(r) for r in rows})
    # A common all-target cohort allows fair model comparisons and joint tasks.
    cohort = [r for r in rows if all(eligible(r, target, fields) for target in outputs)]
    groups = sorted({source(r) for r in cohort})
    v6_nested_predictions = {}
    if model_name == "v6_nested_reference":
        for target in outputs:
            base_result = compare_v6(cohort, target, fields)
            v6_nested_predictions[target] = {r["row_id"]: r["predicted"]
                for r in base_result["residuals"] if r["model"] == "nested_selected"}
    for held in groups:
        train = [r for r in cohort if source(r) != held]
        test = [r for r in cohort if source(r) == held]
        if len({source(r) for r in train}) < 3:
            folds.append({"held_out": held, "status": "insufficient_training_sources", "rows": len(test)})
            continue
        calibration_scores = {target: [] for target in outputs}
        calibration_group_scores = {target: {} for target in outputs}
        if model_name == "gp_matern":
            inner_sources = sorted({source(r) for r in train})
            for cal_source in inner_sources:
                inner_train = [r for r in train if source(r) != cal_source]
                inner_test = [r for r in train if source(r) == cal_source]
                if len({source(r) for r in inner_train}) < 3:
                    continue
                inner_pred, _ = fit_predict(inner_train, inner_test, fields, model_name, outputs)
                for row_i, row in enumerate(inner_test):
                    for target in outputs:
                        sd = inner_pred[target + "__std"][row_i]
                        if np.isfinite(sd) and sd > 0:
                            score = abs(inner_pred[target][row_i] - numeric(row, target)) / sd
                            calibration_scores[target].append(float(score))
                            calibration_group_scores[target].setdefault(cal_source, []).append(float(score))
        if model_name == "v6_nested_reference":
            pred, meta = {target: np.full(len(test), np.nan) for target in outputs}, {"selection": "existing nested v6 ridge/GP/hybrid on identical outer source cohort"}
            for target in outputs:
                for i, row in enumerate(test):
                    if row["row_id"] in v6_nested_predictions[target]:
                        pred[target][i] = v6_nested_predictions[target][row["row_id"]]
        else:
            pred, meta = fit_predict(train, test, fields, model_name, outputs)
        fold_info = {"held_out": held, "training_sources": sorted({source(r) for r in train}),
                     "status": "evaluated", "train_rows": len(train), "test_rows": len(test), "model_details": meta}
        if model_name == "gp_matern":
            for target in outputs:
                group_quantiles = [float(np.quantile(scores, 0.9, method="higher"))
                                   for scores in calibration_group_scores[target].values() if scores]
                q = float(np.quantile(group_quantiles, 0.9, method="higher")) if group_quantiles else None
                fold_info.setdefault("inner_source_calibration", {})[target] = {
                    "source_groups": len(group_quantiles), "quantile": q,
                    "nominal_level": 0.90, "descriptive_not_guaranteed": True,
                }
                if q is not None:
                    pred[target + "__lower"] = np.clip(pred[target] - q * pred[target + "__std"], 0, 100)
                    pred[target + "__upper"] = np.clip(pred[target] + q * pred[target + "__std"], 0, 100)
        folds.append(fold_info)
        for row_i, row in enumerate(test):
            for target in outputs:
                value = pred[target][row_i]
                if np.isfinite(value):
                    records.append({"row_id": row["row_id"], "source": held, "family": row["family"],
                                    "target": target, "observed": numeric(row, target), "predicted": float(value),
                                    "residual": float(value) - numeric(row, target)})
                    std_key = target + "__std"
                    if std_key in pred and np.isfinite(pred[std_key][row_i]):
                        records[-1]["gp_std"] = float(pred[std_key][row_i])
                    if target + "__lower" in pred:
                        records[-1]["interval_lower"] = float(pred[target + "__lower"][row_i])
                        records[-1]["interval_upper"] = float(pred[target + "__upper"][row_i])
    metrics_by_target = {}
    for target in outputs:
        target_records = [r for r in records if r["target"] == target]
        metrics_by_target[target] = score_records(target_records)
        intervals = [r for r in target_records if "interval_lower" in r]
        if intervals:
            metrics_by_target[target]["inner_source_calibrated_90_interval"] = {
                "observed_coverage": float(np.mean([r["interval_lower"] <= r["observed"] <= r["interval_upper"] for r in intervals])),
                "mean_width_pp": float(np.mean([r["interval_upper"] - r["interval_lower"] for r in intervals])),
                "n": len(intervals), "calibration": "nested leave-one-source-out inner folds; descriptive; few-source limitation",
            }
    return {"eligible_rows": len(cohort), "sources": len(groups), "folds": folds, "residuals": records,
            "metrics_by_target": metrics_by_target}


def uncertainty_audit(gp_records):
    result = {}
    for target in TARGETS_ORDER:
        rows = [r for r in gp_records if r["target"] == target and "gp_std" in r]
        if not rows:
            result[target] = {"n": 0, "status": "not_available"}
            continue
        error = np.asarray([abs(r["residual"]) for r in rows])
        std = np.asarray([r["gp_std"] for r in rows])
        # Standardize error only as a diagnostic; interval coverage is separately empirical.
        result[target] = {
            "n": len(rows), "mean_gp_std": float(std.mean()),
            "spearman_proxy_correlation_abs_error_std": float(np.corrcoef(np.argsort(np.argsort(error)), np.argsort(np.argsort(std)))[0, 1]),
            "coverage_1_96std_descriptive": float(np.mean(error <= 1.96 * std)),
            "calibrated_interval": False,
        }
    return result


def descriptor_audit(rows):
    desc_path = ROOT / "data/htft/htft_catalyst_descriptors_v1.csv"
    desc = load_rows(desc_path)
    lookup = {(r.get("dataset_id", ""), r.get("catalyst", "")): r for r in desc}
    fields = [k for k in desc[0] if k not in ("descriptor_id", "dataset_id", "catalyst", "family", "source")]
    attached = [r for r in rows if (r.get("dataset_id", ""), r.get("catalyst", "")) in lookup]
    descriptor_dois = {r.get("source", "").strip().lower() for r in desc}
    model_dois = {r.get("source_doi", "").strip().lower() for r in rows}
    per_field = {field: sum(bool(lookup[(r.get("dataset_id", ""), r.get("catalyst", ""))].get(field, "")) for r in attached)
                 for field in fields}
    family_sources = {}
    catalyst_sources = {}
    for row in rows:
        family_sources.setdefault(row.get("family", ""), set()).add(source(row))
        catalyst_sources.setdefault(row.get("catalyst", ""), set()).add(source(row))
    reused_families = {name: sorted(groups) for name, groups in family_sources.items() if name and len(groups) > 1}
    reused_catalysts = {name: sorted(groups) for name, groups in catalyst_sources.items() if name and len(groups) > 1}
    structure_files = [str(p.relative_to(ROOT)) for p in (ROOT / "data/htft").rglob("*")
                       if p.is_file() and p.suffix.lower() in {".cif", ".vasp", ".poscar", ".xyz"}]
    return {"model_rows": len(rows), "descriptor_records": len(desc), "rows_joined_exact_dataset_catalyst": len(attached),
            "join_coverage": len(attached) / len(rows) if rows else 0.0, "descriptor_fields": per_field,
            "descriptor_source_dois": sorted(descriptor_dois), "model_source_dois": sorted(model_dois),
            "source_doi_overlap": sorted(descriptor_dois & model_dois),
            "families_repeated_across_sources": reused_families,
            "exact_catalyst_names_repeated_across_sources": reused_catalysts,
            "crystal_or_atomic_structure_files_available": structure_files,
            "status": "descriptor_table_does_not_join_current_model_corpus; no structural inputs for GNN"}


def main():
    input_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
    rows = rows_all()
    descriptor = descriptor_audit(rows)
    report = {"version": "14.0-probabilistic-and-multitask-research", "input_sha256": input_hashes,
              "design": "common complete-case cohort; outer leave-one-independent-source-out; source-balanced fit and score; all preprocessing inside each fold",
              "model_promoted": False, "recommendation_blocked": True,
              "models": {}, "descriptor_audit": descriptor,
              "hierarchical_model": {"status": "deferred_not_identifiable", "reason": "too few independent sources and sparse repeated catalyst identities across sources; source random effects cannot establish transport to unseen publications"}}
    for profile in PROFILES:
        report["models"][profile] = {}
        for model in ("v6_nested_reference", "gp_matern", "multitask_lasso", "random_forest_reference", "extra_trees_reference"):
            # GP uncertainty is generated only in GP branch; rest follow identical cohort.
            result = compare(rows, profile, TARGETS_ORDER, model)
            report["models"][profile][model] = result
            print(profile, model, result["eligible_rows"], result["sources"],
                  {k: round(v["mae"], 3) if v["mae"] is not None else None for k, v in result["metrics_by_target"].items()}, flush=True)
        # Paired source-level MAE deltas versus nested v6; descriptive only.
        ref = report["models"][profile]["v6_nested_reference"]
        for model, result in report["models"][profile].items():
            if model == "v6_nested_reference":
                continue
            result["paired_delta_vs_v6"] = {}
            for target in TARGETS_ORDER:
                a = {r["row_id"]: r for r in ref["residuals"] if r["target"] == target}
                b = {r["row_id"]: r for r in result["residuals"] if r["target"] == target}
                common = sorted(set(a) & set(b))
                if not common:
                    continue
                groups = sorted({a[k]["source"] for k in common})
                deltas = [np.mean([abs(b[k]["residual"]) - abs(a[k]["residual"])
                                   for k in common if a[k]["source"] == g]) for g in groups]
                rng = np.random.default_rng(14022)
                boot = rng.choice(deltas, (5000, len(deltas)), replace=True).mean(axis=1)
                result["paired_delta_vs_v6"][target] = {
                    "paired_rows": len(common), "sources": len(groups),
                    "delta_source_balanced_mae": float(np.mean(deltas)),
                    "descriptive_source_bootstrap_95": np.quantile(boot, [0.025, 0.975]).tolist(),
                }
    report["gp_uncertainty_diagnostic"] = {
        profile: uncertainty_audit(report["models"][profile]["gp_matern"]["residuals"])
        for profile in PROFILES
    }
    report["multitask_solver_diagnostics"] = {
        "convergence_warnings": MULTITASK_CONVERGENCE_WARNINGS,
        "status": "not_reliable_for_promotion" if MULTITASK_CONVERGENCE_WARNINGS else "converged_in_recorded_fits",
        "note": "Convergence warnings are counted, not hidden; output values remain candidate-only.",
    }
    out = REPORT
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("saved", out)


if __name__ == "__main__":
    main()
