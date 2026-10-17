"""Frozen HTFT temperature-transfer benchmark and external-holdout evaluation."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path

MODEL_ID = "htft-catalyst-persistence-baseline"
MODEL_VERSION = "1.0.0"
TARGETS = (
    "co_conversion_pct",
    "ch4_carbon_pct",
    "c2_c4_olefins_carbon_pct",
    "olefin_paraffin_ratio",
)


def load_dataset(path: Path) -> list[dict[str, object]]:
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result: list[dict[str, object]] = []
    for row in rows:
        item: dict[str, object] = dict(row)
        for field in ("temperature_c", "pressure_bar", "h2_co_ratio", "ghsv_l_gcat_h", *TARGETS):
            item[field] = float(row[field])
        result.append(item)
    return result


def freeze_persistence_model(rows: list[dict[str, object]]) -> dict[str, object]:
    calibration = [row for row in rows if row["split"] == "calibration"]
    if not calibration:
        raise ValueError("calibration rows required")
    values = {
        str(row["catalyst"]): {target: float(row[target]) for target in TARGETS}
        for row in calibration
    }
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":"))
    return {
        "model_id": MODEL_ID,
        "version": MODEL_VERSION,
        "frozen": True,
        "model_class": "same-catalyst persistence baseline",
        "calibration_temperature_c": sorted({float(row["temperature_c"]) for row in calibration}),
        "predictions_by_catalyst": values,
        "parameters_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "declared_domain": "same four catalysts, fixed-bed, 20 bar, H2/CO=1, 4.2 L gcat-1 h-1; temperature transfer 300 to 320 C",
        "scientific_limitation": "baseline assumes no temperature response and is evaluated as a falsifiable benchmark, not a production predictor",
    }


def _bootstrap_mae_ci(residuals: list[float], seed: int = 34034, iterations: int = 10000) -> list[float]:
    rng = random.Random(seed)
    n = len(residuals)
    values = sorted(sum(abs(residuals[rng.randrange(n)]) for _ in range(n)) / n for _ in range(iterations))
    return [values[int(0.025 * iterations)], values[int(0.975 * iterations) - 1]]


def evaluate_external_holdout(rows: list[dict[str, object]], model: dict[str, object]) -> dict[str, object]:
    holdout = [row for row in rows if row["split"] == "external_holdout"]
    predictions = model["predictions_by_catalyst"]
    details: list[dict[str, object]] = []
    metrics: dict[str, object] = {}
    for target in TARGETS:
        residuals = []
        for row in holdout:
            predicted = float(predictions[str(row["catalyst"])][target])
            observed = float(row[target])
            residual = predicted - observed
            residuals.append(residual)
            details.append({"row_id": row["row_id"], "catalyst": row["catalyst"], "target": target,
                            "observed": observed, "predicted": predicted, "residual_predicted_minus_observed": residual})
        mse = sum(value * value for value in residuals) / len(residuals)
        metrics[target] = {
            "n": len(residuals),
            "mae": sum(abs(value) for value in residuals) / len(residuals),
            "mse": mse,
            "rmse": math.sqrt(mse),
            "bias": sum(residuals) / len(residuals),
            "mae_bootstrap_95_ci": _bootstrap_mae_ci(residuals),
        }
    criteria = {
        "co_conversion_mae_at_most_10_pct_points": metrics["co_conversion_pct"]["mae"] <= 10,
        "ch4_mae_at_most_5_pct_points": metrics["ch4_carbon_pct"]["mae"] <= 5,
        "c2_c4_olefins_mae_at_most_5_pct_points": metrics["c2_c4_olefins_carbon_pct"]["mae"] <= 5,
        "olefin_paraffin_ratio_mae_at_most_0_15": metrics["olefin_paraffin_ratio"]["mae"] <= 0.15,
    }
    return {
        "schema_version": "1.0.0",
        "model_id": model["model_id"],
        "model_version": model["version"],
        "external_holdout_rows": len(holdout),
        "uncertainty_method": "deterministic nonparametric bootstrap of catalyst-level absolute residuals, 10000 resamples, fixed seed 34034",
        "metrics": metrics,
        "residuals": details,
        "criteria": criteria,
        "quantitative_validation_passed": all(criteria.values()),
        "recommendation_blocked": True,
    }
