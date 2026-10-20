"""Exploratory per-target ranking for the HTFT v14 benchmark.

This module selects the lowest retrospective MAE on the *same* source-held-out
cohort. It is a comparison display only: it does not produce predictions and
does not relax the scientific/deployment gate in the source report.
"""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import Any


TARGET_LABELS = {
    "co_conversion_pct": "Conversão de CO",
    "co2_selectivity_pct": "Seletividade de CO₂",
    "ch4_hc_carbon_pct": "Seletividade de CH₄",
    "c2_c4_olefins_hc_carbon_pct": "Olefinas C₂–C₄",
}

MODEL_LABELS = {
    "v6_nested_reference": "v6 · Ridge/GP híbrido aninhado",
    "gp_matern": "GP Matérn",
    "multitask_lasso": "Lasso multitarefa",
    "random_forest_reference": "Random Forest",
    "extra_trees_reference": "Extra Trees",
    "v7_gradient_boosting": "Gradient Boosting",
    "v8_random_forest": "Random Forest (v8)",
    "v9_svr_rbf": "SVR RBF",
    "v10_additive_splines": "Splines aditivos",
    "v11_pls_pcr": "PLS/PCR",
}

PROFILE_LABELS = {
    "operating_core": "Condições operacionais",
    "space_time": "Condições + GHSV/TOS",
}


def best_model_by_target(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return lowest-MAE candidate per target/profile, preserving the gate."""
    models = report.get("models")
    if not isinstance(models, Mapping):
        raise ValueError("Relatório v14 sem seção 'models'.")

    blocked = bool(report.get("recommendation_blocked", True))
    promoted = bool(report.get("model_promoted", False))
    rows: list[dict[str, Any]] = []
    for profile, profile_data in models.items():
        if not isinstance(profile_data, Mapping):
            continue
        by_target: dict[str, list[tuple[float, str, Mapping[str, Any]]]] = {}
        for model_id, model_data in profile_data.items():
            metrics = model_data.get("metrics_by_target", {})
            if not isinstance(metrics, Mapping):
                continue
            for target, metric in metrics.items():
                try:
                    mae = float(metric["mae"])
                except (KeyError, TypeError, ValueError):
                    continue
                if isfinite(mae):
                    by_target.setdefault(str(target), []).append((mae, str(model_id), metric))

        for target, candidates in by_target.items():
            mae, model_id, metric = min(candidates, key=lambda item: (item[0], item[1]))
            rows.append({
                "profile": str(profile),
                "profile_label": PROFILE_LABELS.get(str(profile), str(profile)),
                "target": target,
                "target_label": TARGET_LABELS.get(target, target),
                "model_id": model_id,
                "model_label": MODEL_LABELS.get(model_id, model_id),
                "mae": mae,
                "n": metric.get("n"),
                "sources": (
                    metric.get("sources")
                    if isinstance(metric.get("sources"), int)
                    else len(metric.get("sources", []))
                    if isinstance(metric.get("sources"), list)
                    else None
                ),
                "status": "exploratory_only",
                "deployment_allowed": promoted and not blocked,
            })
    return rows


def compare_versions_v6_v14(
    report_v12: Mapping[str, Any],
    report_v13_robust: Mapping[str, Any],
    report_v14: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Collect comparable v6-v14 candidates from the common source cohorts.

    v12 contains nested-selected winners for v6-v11; v13 adds robust-fit
    variants; v14 adds GP, multitask, RF and ExtraTrees on the same cohorts.
    The v13 compositional report is intentionally excluded because it uses a
    different response basis and a 22-row/3-source cohort.
    """
    candidates: list[dict[str, Any]] = []

    for profile, targets in report_v12.get("profiles", {}).items():
        for target, versions in targets.items():
            for version_id, result in versions.items():
                # v14 is the current rerun of the v6 baseline on these cohorts.
                if version_id.startswith("v6_"):
                    continue
                metric = result.get("metrics", {}).get("nested_selected")
                if metric and isinstance(metric.get("mae"), (int, float)):
                    candidates.append(_candidate(profile, target, version_id, metric, "v12 nested"))

    for profile, targets in report_v13_robust.get("profiles", {}).items():
        for target, versions in targets.items():
            for version_id, result in versions.items():
                for estimator_id, metric in result.get("metrics", {}).items():
                    if not estimator_id.startswith("robust__"):
                        continue
                    if isinstance(metric.get("mae"), (int, float)):
                        candidates.append(_candidate(
                            profile, target, "v13_robust_" + estimator_id.removeprefix("robust__"),
                            metric, "v13 robust sensitivity",
                        ))

    for profile, model_data in report_v14.get("models", {}).items():
        for model_id, result in model_data.items():
            for target, metric in result.get("metrics_by_target", {}).items():
                if isinstance(metric.get("mae"), (int, float)):
                    source_version = "v6" if model_id.startswith("v6_") else "v14"
                    candidates.append(_candidate(profile, target, model_id, metric,
                                                 "v14 common cohort", source_version))

    best: dict[tuple[str, str], dict[str, Any]] = {}
    for item in candidates:
        key = (item["profile"], item["target"])
        current = best.get(key)
        if current is None or (item["mae"], item["model_id"]) < (current["mae"], current["model_id"]):
            best[key] = item
    return list(best.values())


def _candidate(profile: str, target: str, model_id: str, metric: Mapping[str, Any],
               benchmark: str, version_override: str | None = None) -> dict[str, Any]:
    version = model_id.split("_", 1)[0]
    if model_id.startswith("v13_robust_"):
        estimator = model_id.removeprefix("v13_robust_")
        model_label = "v13 robust · " + MODEL_LABELS.get(estimator, estimator.replace("_", " "))
        version = "v13"
    else:
        model_label = MODEL_LABELS.get(model_id, model_id.replace("_", " "))
    if version_override is not None:
        version = version_override
    source_count = metric.get("sources")
    return {
        "profile": profile,
        "profile_label": PROFILE_LABELS.get(profile, profile),
        "target": target,
        "target_label": TARGET_LABELS.get(target, target),
        "version": version,
        "model_id": model_id,
        "model_label": model_label,
        "mae": float(metric["mae"]),
        "n": metric.get("n"),
        "sources": source_count if isinstance(source_count, int) else None,
        "benchmark": benchmark,
        "status": "exploratory_only",
        "deployment_allowed": False,
    }
