"""Pre-registered validation metrics and residual/uncertainty criteria for FT-024."""
from __future__ import annotations

import math
from collections.abc import Sequence

VALIDATION_CRITERIA_VERSION = "1.0.0"


def validation_metrics(observed: Sequence[float], predicted: Sequence[float]) -> dict[str, float]:
    if len(observed) != len(predicted) or len(observed) < 3:
        raise ValueError("observed and predicted must have equal length >= 3")
    obs = [float(value) for value in observed]
    pred = [float(value) for value in predicted]
    if any(not math.isfinite(value) for value in obs + pred):
        raise ValueError("values must be finite")
    residuals = [prediction - measurement for measurement, prediction in zip(obs, pred)]
    mse = sum(value * value for value in residuals) / len(residuals)
    mean_observed = sum(obs) / len(obs)
    return {
        "n": len(obs), "mae": sum(abs(value) for value in residuals) / len(residuals),
        "mse": mse, "rmse": math.sqrt(mse), "bias": sum(residuals) / len(residuals),
        "mean_observed": mean_observed,
        "nmae_mean": (sum(abs(value) for value in residuals) / len(residuals)) / abs(mean_observed),
        "nrmse_mean": math.sqrt(mse) / abs(mean_observed),
    }


def assess_validation(metrics: dict[str, float], diagnostics: dict[str, object]) -> dict[str, object]:
    """Apply project acceptance criteria; these thresholds are governance choices."""
    checks = {
        "external_unique_runs_at_least_20": metrics["n"] >= 20,
        "nmae_at_most_15_pct": metrics["nmae_mean"] <= 0.15,
        "nrmse_at_most_20_pct": metrics["nrmse_mean"] <= 0.20,
        "absolute_bias_at_most_5_pct_mean": abs(metrics["bias"]) <= 0.05 * abs(metrics["mean_observed"]),
        "prediction_interval_95_coverage_90_to_99_pct": 0.90 <= float(diagnostics.get("pi95_coverage", -1)) <= 0.99,
        "standardized_residual_outlier_fraction_at_most_1_pct": float(diagnostics.get("std_residual_outlier_fraction", 1)) <= 0.01,
        "no_material_residual_trend": abs(float(diagnostics.get("max_abs_spearman_residual_driver", 1))) < 0.30,
        "heteroscedasticity_not_detected": float(diagnostics.get("heteroscedasticity_p_value", 0)) >= 0.05,
        "cluster_bootstrap_ci_reported": diagnostics.get("cluster_bootstrap_ci_reported") is True,
        "measurement_uncertainty_propagated": diagnostics.get("measurement_uncertainty_propagated") is True,
        "independent_dataset": diagnostics.get("independent_dataset") is True,
        "catalyst_and_domain_compatible": diagnostics.get("catalyst_and_domain_compatible") is True,
    }
    return {"criteria_version": VALIDATION_CRITERIA_VERSION, "checks": checks,
            "passed": all(checks.values()), "recommendation_blocked": not all(checks.values())}
