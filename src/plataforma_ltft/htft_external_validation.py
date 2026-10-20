"""Publication-grouped validation for the diverse HTFT evidence corpus."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np


TARGETS = {
    "co_conversion_pct": 10.0,
    "co2_selectivity_pct": 5.0,
    "ch4_hc_carbon_pct": 5.0,
    "c2_c4_olefins_hc_carbon_pct": 5.0,
}

V41_FIELDS = ("temperature_c", "pressure_bar", "h2_co_ratio", "ghsv_ml_gcat_h", "tos_h")
V41_MIN_PUBLICATIONS = 2
V41_MIN_ROWS = 6


def _independent_source_id(row: dict[str, str]) -> str:
    """Treat linked publications/campaigns as one source when lineage is known."""
    return row.get("source_group_id", "").strip() or row["source_doi"]


def load_rows(path: Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _number(row: dict[str, str], key: str, default: float) -> float:
    value = row.get(key, "").strip()
    return float(value) if value else default


def _features(row: dict[str, str], families: list[str]) -> list[float]:
    family = row["family"]
    continuous = [
        (_number(row, "temperature_c", 320.0) - 320.0) / 40.0,
        (_number(row, "pressure_bar", 10.0) - 10.0) / 10.0,
        (_number(row, "h2_co_ratio", 1.5) - 1.5),
        math.log(max(_number(row, "ghsv_ml_gcat_h", 10000.0), 1.0) / 10000.0),
        math.log(max(_number(row, "tos_h", 24.0), 0.1) / 24.0),
    ]
    return continuous + [1.0 if family == item else 0.0 for item in families]


def _ridge(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, ridge: float = 10.0) -> np.ndarray:
    mean = train_x.mean(axis=0)
    scale = train_x.std(axis=0)
    scale[scale == 0] = 1.0
    design = np.column_stack([np.ones(len(train_x)), (train_x - mean) / scale])
    test = np.column_stack([np.ones(len(test_x)), (test_x - mean) / scale])
    penalty = np.eye(design.shape[1]) * ridge
    penalty[0, 0] = 0.0
    coefficients = np.linalg.pinv(design.T @ design + penalty) @ design.T @ train_y
    return np.clip(test @ coefficients, 0.0, 100.0)


def _publication_balanced_ridge(
    train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray,
    publications: list[str], ridge: float = 10.0,
) -> np.ndarray:
    """Give each training publication equal total weight, not each table row.

    Normalization and weights are learned anew within each training fold;
    the held-out publication contributes neither responses nor statistics.
    """
    if len(publications) != len(train_y):
        raise ValueError("one publication identifier required per training row")
    counts = {source: publications.count(source) for source in set(publications)}
    weights = np.array([len(publications) / (len(counts) * counts[source])
                        for source in publications], dtype=float)
    mean = np.average(train_x, axis=0, weights=weights)
    scale = np.sqrt(np.average((train_x - mean) ** 2, axis=0, weights=weights))
    scale[scale == 0] = 1.0
    design = np.column_stack([np.ones(len(train_x)), (train_x - mean) / scale])
    test = np.column_stack([np.ones(len(test_x)), (test_x - mean) / scale])
    penalty = np.eye(design.shape[1]) * ridge
    penalty[0, 0] = 0.0
    coefficients = np.linalg.pinv(design.T @ (weights[:, None] * design) + penalty) @ (
        design.T @ (weights * train_y)
    )
    return np.clip(test @ coefficients, 0.0, 100.0)


def evaluate_leave_one_publication_out(
    rows: list[dict[str, str]], *, publication_balanced: bool = False,
) -> dict[str, object]:
    """Hold out every row from one DOI and report honest external errors."""
    families = sorted({row["family"] for row in rows})
    publications = sorted({row["source_doi"] for row in rows})
    residuals: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for publication in publications:
        for target in TARGETS:
            train = [row for row in rows if row["source_doi"] != publication and row.get(target, "").strip()]
            test = [row for row in rows if row["source_doi"] == publication and row.get(target, "").strip()]
            if not test or len(train) < 5:
                skipped.append({"publication": publication, "target": target,
                                "reason": "no_test_rows" if not test else "insufficient_training_rows"})
                continue
            train_x = np.array([_features(row, families) for row in train], dtype=float)
            test_x = np.array([_features(row, families) for row in test], dtype=float)
            train_y = np.array([float(row[target]) for row in train])
            predictions = (
                _publication_balanced_ridge(train_x, train_y, test_x,
                                            [row["source_doi"] for row in train])
                if publication_balanced else _ridge(train_x, train_y, test_x)
            )
            for row, prediction in zip(test, predictions):
                observed = float(row[target])
                residuals.append({"held_out_publication": publication, "row_id": row["row_id"],
                                  "family": row["family"], "target": target, "observed": observed,
                                  "predicted": float(prediction),
                                  "residual_predicted_minus_observed": float(prediction - observed)})
    metrics: dict[str, object] = {}
    for target, criterion in TARGETS.items():
        target_rows = [row for row in residuals if row["target"] == target]
        values = [float(row["residual_predicted_minus_observed"]) for row in target_rows]
        if not values:
            metrics[target] = {"n": 0, "criterion_mae": criterion, "passed": False}
            continue
        mse = sum(value * value for value in values) / len(values)
        mae = sum(abs(value) for value in values) / len(values)
        metrics[target] = {"n": len(values), "mae": mae, "mse": mse, "rmse": math.sqrt(mse),
                           "bias": sum(values) / len(values), "criterion_mae": criterion,
                           "passed": mae <= criterion}
    return {
        "schema_version": "1.0.0",
        "model_id": "htft-publication-balanced-ridge-candidate" if publication_balanced else "htft-diverse-family-ridge-baseline",
        "model_version": "4.3.0-research-candidate" if publication_balanced else "4.0.0-research-baseline",
        "evaluation_design": "leave-one-publication-out",
        "publication_count": len(publications),
        "catalyst_family_count": len(families),
        "row_count": len(rows),
        "metrics": metrics,
        "all_targets_passed": all(item["passed"] for item in metrics.values()),
        "skipped_combinations": skipped,
        "residuals": residuals,
        "recommendation_blocked": True,
    }


def predict_v41_guarded(
    training_rows: list[dict[str, str]], query: dict[str, str], target: str
) -> dict[str, object]:
    """Return a local research estimate only inside a replicated evidence domain.

    A categorical family observed only in one article cannot establish a
    transferable relationship. Missing operating coordinates are never imputed.
    """
    if target not in TARGETS:
        raise ValueError(f"Unsupported target: {target}")
    family = query.get("family", "").strip()
    if not family:
        return {"estimate_available": False, "reason": "missing_family", "recommendation_blocked": True}
    candidates = [row for row in training_rows if row.get("family") == family and row.get(target, "").strip()]
    publications = {_independent_source_id(row) for row in candidates}
    if len(publications) < V41_MIN_PUBLICATIONS:
        return {"estimate_available": False, "reason": "insufficient_independent_publications",
                "family": family, "observed_publications": len(publications),
                "required_publications": V41_MIN_PUBLICATIONS, "recommendation_blocked": True}
    if any(not query.get(field, "").strip() for field in V41_FIELDS):
        return {"estimate_available": False, "reason": "missing_operating_coordinate",
                "required_coordinates": list(V41_FIELDS), "recommendation_blocked": True}
    complete = [row for row in candidates if all(row.get(field, "").strip() for field in V41_FIELDS)]
    signature_sources: dict[tuple[str, ...], set[str]] = {}
    for row in complete:
        signature = (row["catalyst"], *(row[field] for field in V41_FIELDS), row[target])
        signature_sources.setdefault(signature, set()).add(_independent_source_id(row))
    if len(complete) < V41_MIN_ROWS or len({_independent_source_id(row) for row in complete}) < V41_MIN_PUBLICATIONS:
        return {"estimate_available": False, "reason": "insufficient_complete_observations",
                "family": family, "complete_rows": len(complete), "recommendation_blocked": True}
    independent = [row for row in complete if len(signature_sources[
        (row["catalyst"], *(row[field] for field in V41_FIELDS), row[target])]) == 1]
    if len({_independent_source_id(row) for row in independent}) < V41_MIN_PUBLICATIONS or len(independent) < V41_MIN_ROWS:
        return {"estimate_available": False, "reason": "repeated_observations_across_sources",
                "family": family, "independent_rows": len(independent),
                "recommendation_blocked": True}
    complete = independent
    scales = (40.0, 10.0, 1.0, 10000.0, 100.0)
    point = np.array([float(query[field]) for field in V41_FIELDS])
    matrix = np.array([[float(row[field]) for field in V41_FIELDS] for row in complete])
    if np.any(point < matrix.min(axis=0)) or np.any(point > matrix.max(axis=0)):
        return {"estimate_available": False, "reason": "outside_observed_operating_envelope",
                "family": family, "recommendation_blocked": True}
    distances = np.linalg.norm((matrix - point) / np.array(scales), axis=1)
    nearest = np.argsort(distances)[: min(8, len(complete))]
    if float(distances[nearest[0]]) > 0.75:
        return {"estimate_available": False, "reason": "no_local_operating_support",
                "family": family, "recommendation_blocked": True}
    local_publications = {_independent_source_id(complete[index]) for index in nearest}
    if len(local_publications) < V41_MIN_PUBLICATIONS:
        return {"estimate_available": False, "reason": "no_independent_local_support",
                "family": family, "recommendation_blocked": True}
    weights = 1.0 / np.maximum(distances[nearest], 0.05)
    values = np.array([float(complete[index][target]) for index in nearest])
    estimate = float(np.average(values, weights=weights))
    spread = float(np.sqrt(np.average((values - estimate) ** 2, weights=weights)))
    return {"estimate_available": True, "model_version": "4.1.0-research-gated",
            "family": family, "target": target, "estimate": estimate,
            "local_observed_spread": spread, "support_rows": len(nearest),
            "support_publications": len(local_publications),
            "recommendation_blocked": True}


def evaluate_v41_grouped(rows: list[dict[str, str]]) -> dict[str, object]:
    """Measure coverage and error without treating abstentions as successes."""
    publications = sorted({_independent_source_id(row) for row in rows})
    residuals: list[dict[str, object]] = []
    abstentions: list[dict[str, object]] = []
    eligible = 0
    for publication in publications:
        train = [row for row in rows if _independent_source_id(row) != publication]
        test = [row for row in rows if _independent_source_id(row) == publication]
        for row in test:
            for target in TARGETS:
                if not row.get(target, "").strip():
                    continue
                eligible += 1
                result = predict_v41_guarded(train, row, target)
                if not result["estimate_available"]:
                    abstentions.append({"held_out_publication": publication, "row_id": row["row_id"],
                                        "target": target, "reason": result["reason"]})
                    continue
                observed = float(row[target])
                residuals.append({"held_out_publication": publication, "row_id": row["row_id"],
                                  "target": target, "observed": observed,
                                  "predicted": result["estimate"],
                                  "residual_predicted_minus_observed": result["estimate"] - observed})
    metrics: dict[str, object] = {}
    for target, criterion in TARGETS.items():
        values = [float(row["residual_predicted_minus_observed"])
                  for row in residuals if row["target"] == target]
        metrics[target] = {"n": len(values), "mae": sum(map(abs, values)) / len(values) if values else None,
                           "criterion_mae": criterion,
                           "passed": bool(values) and sum(map(abs, values)) / len(values) <= criterion}
    return {"schema_version": "1.0.0", "model_version": "4.1.0-research-gated",
            "evaluation_design": "leave-one-publication-out-with-abstention",
            "eligible_target_rows": eligible, "predicted_target_rows": len(residuals),
            "coverage": len(residuals) / eligible if eligible else 0.0,
            "metrics": metrics, "all_targets_passed": all(item["passed"] for item in metrics.values()),
            "abstention_reasons": {reason: sum(item["reason"] == reason for item in abstentions)
                                    for reason in sorted({item["reason"] for item in abstentions})},
            "abstentions": abstentions, "residuals": residuals, "recommendation_blocked": True}
