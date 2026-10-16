"""Restricted empirical benchmark; never asserts external validation or lab execution."""
import math
import numpy as np
from scipy.stats import t as student_t

CATALYST = "Mansouri2013_CoCe_SiO2"
FEATURES = ("intercept", "1000*(1/493.15-1/T_K)", "feed_0.400H2_0.267CO_bar")


def design(rows):
    result = []
    for row in rows:
        temp, h2, co = (float(row[k]) for k in ("temperature_c", "p_h2_bar", "p_co_bar"))
        if row["catalyst_id"] != CATALYST or not 200 <= temp <= 260:
            raise ValueError("Outside catalyst/temperature domain")
        if (h2, co) not in ((0.333, 0.333), (0.4, 0.267)):
            raise ValueError("Only the two measured feed compositions are supported")
        result.append([1., 1000 * (1 / 493.15 - 1 / (temp + 273.15)), float(h2 == 0.4)])
    return np.asarray(result)


def fit(rows):
    if len(rows) <= 3:
        raise ValueError("Insufficient observations")
    x = design(rows)
    rates = np.array([float(r["rate_mmol_gcat_min"]) for r in rows])
    if not np.all(np.isfinite(rates)) or np.any(rates <= 0):
        raise ValueError("Rates must be positive and finite")
    if np.linalg.matrix_rank(x) != 3:
        raise ValueError("Unidentifiable model")
    beta = np.linalg.lstsq(x, np.log(rates), rcond=None)[0]
    variance = float(np.sum((np.log(rates) - x @ beta) ** 2) / (len(rows) - 3))
    return {"beta": beta.tolist(), "covariance": (variance * np.linalg.inv(x.T @ x)).tolist(),
            "residual_log_variance": variance, "degrees_freedom": len(rows) - 3,
            "temperature_range_c": [min(float(r['temperature_c']) for r in rows), max(float(r['temperature_c']) for r in rows)],
            "features": FEATURES, "response_unit": "mmol_CO/(g_cat*min)",
            "calibration_status": "exploratory", "external_validation": False,
            "recommendation_blocked": True}


def predict(model, rows):
    x = design(rows)
    if any(not model['temperature_range_c'][0] <= float(r['temperature_c']) <= model['temperature_range_c'][1] for r in rows):
        raise ValueError("Temperature extrapolation")
    center = x @ np.asarray(model['beta'])
    variance = np.einsum('ij,jk,ik->i', x, np.asarray(model['covariance']), x)
    width = student_t.ppf(.975, model['degrees_freedom']) * np.sqrt(variance + model['residual_log_variance'])
    return [{"median_rate": float(math.exp(c)), "prediction_lower_95": float(math.exp(c-w)),
             "prediction_upper_95": float(math.exp(c+w))} for c,w in zip(center,width)]


def assess_external_dataset(model, rows):
    """Checks scientific compatibility before any numeric validation is attempted."""
    reasons = []
    catalysts = sorted({str(r.get("catalyst_id", "")) for r in rows})
    if catalysts != [CATALYST]:
        reasons.append("catalyst_mismatch")
    for row in rows:
        temp = float(row["temperature_c"])
        if not model["temperature_range_c"][0] <= temp <= model["temperature_range_c"][1]:
            reasons.append("temperature_outside_calibration_domain")
        if (float(row["p_h2_bar"]), float(row["p_co_bar"])) not in ((.333, .333), (.4, .267)):
            reasons.append("feed_composition_outside_calibration_domain")
    reasons = list(dict.fromkeys(reasons))
    return {"compatible": not reasons, "reasons": reasons,
            "validation_performed": False, "recommendation_blocked": bool(reasons)}
