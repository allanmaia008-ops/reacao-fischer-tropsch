"""Build a public-safe HTFT model summary without row-level measurements."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.htft_target_selection import compare_versions_v6_v14  # noqa: E402

VALIDATION = ROOT / "data/htft/validation"
OUTPUT = VALIDATION / "htft_public_model_summary_v1.json"


def _load(filename: str):
    return json.loads((VALIDATION / filename).read_text(encoding="utf-8"))


def build_summary() -> dict:
    v12 = _load("target_research_v12.json")
    v13 = _load("target_research_v13_robust_all_versions.json")
    v14 = _load("target_research_v14_probabilistic_multitask.json")
    v15 = _load("target_research_v15_mlp_pilot.json")
    v31 = _load("htft_multiaxis_v31_domain_validation.json")
    v41 = _load("htft_external_lopo_v41_guarded.json")
    selected = compare_versions_v6_v14(v12, v13, v14)
    best = [{key: row[key] for key in ("profile", "profile_label", "target", "target_label",
                                      "version", "model_id", "model_label", "mae", "n", "sources",
                                      "deployment_allowed")}
            for row in selected]
    mlp = []
    for profile, result in v15["profiles"].items():
        for target, metrics in result["metrics_by_target"].items():
            prior = next(item for item in selected
                         if item["profile"] == profile and item["target"] == target)
            mlp.append({
                "profile": profile, "profile_label": prior["profile_label"],
                "target": target, "target_label": prior["target_label"],
                "mae": metrics["mae"], "reference_version": prior["version"],
                "reference_model": prior["model_label"], "reference_mae": prior["mae"],
                "delta_mae_vs_v6_v14_best": metrics["mae"] - prior["mae"],
                "n": metrics["n"], "sources": metrics["sources"],
                "promoted": False,
            })
    return {
        "schema_version": "1.0.0",
        "benchmark_scope": "HTFT source-grouped retrospective comparison; same complete-case cohorts",
        "best_v6_v14_by_profile_and_target": best,
        "mlp_v15_pilot": mlp,
        "mlp_convergence_warnings": v15.get("convergence_warnings", 0),
        "v31_thermal_interpolation_passed_within_domain": bool(v31.get("within_domain_validation_passed")),
        "v41_transfer_coverage": v41.get("coverage"),
        "v41_predicted_target_rows": v41.get("predicted_target_rows"),
        "v41_eligible_target_rows": v41.get("eligible_target_rows"),
        "model_promoted": False,
        "recommendation_blocked": True,
        "limitations": [
            "Best-by-target is selected retrospectively on the same benchmark and is optimistic.",
            "No model is promoted for operational prediction or experimental recommendations.",
            "The v13 compositional model is excluded because it uses a different target basis and cohort.",
            "The MLP is a pilot only; nested fits include convergence warnings and it does not win consistently.",
            "This public summary excludes row-level observed values, predictions, and residuals.",
        ],
        "source_reports": [
            "target_research_v12.json", "target_research_v13_robust_all_versions.json",
            "target_research_v14_probabilistic_multitask.json", "target_research_v15_mlp_pilot.json",
            "htft_multiaxis_v31_domain_validation.json", "htft_external_lopo_v41_guarded.json",
        ],
    }


def main() -> None:
    summary = build_summary()
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "best_models": len(summary["best_v6_v14_by_profile_and_target"]),
                      "mlp_rows": len(summary["mlp_v15_pilot"]),
                      "model_promoted": summary["model_promoted"],
                      "recommendation_blocked": summary["recommendation_blocked"]}, indent=2))


if __name__ == "__main__":
    main()
