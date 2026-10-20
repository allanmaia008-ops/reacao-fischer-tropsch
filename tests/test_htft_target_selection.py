import json
from pathlib import Path

from plataforma_ltft.htft_target_selection import best_model_by_target
from plataforma_ltft.htft_target_selection import compare_versions_v6_v14


ROOT = Path(__file__).resolve().parents[1]


def synthetic_v14_report():
    targets = ("co_conversion_pct", "co2_selectivity_pct", "ch4_hc_carbon_pct",
               "c2_c4_olefins_hc_carbon_pct")
    return {"recommendation_blocked": True, "model_promoted": False, "models": {
        profile: {
            "v6_nested_reference": {"metrics_by_target": {
                target: {"mae": 2.0, "n": 10, "sources": 5} for target in targets}},
            "gp_matern": {"metrics_by_target": {
                target: {"mae": 1.0, "n": 10, "sources": 5} for target in targets}},
        } for profile in ("operating_core", "space_time")}}


def test_v14_selects_minimum_mae_per_target_and_profile_without_promotion():
    report = synthetic_v14_report()
    selected = best_model_by_target(report)

    assert len(selected) == 8
    assert report["recommendation_blocked"] is True
    assert report["model_promoted"] is False
    assert all(row["deployment_allowed"] is False for row in selected)
    got = {(row["profile"], row["target"]): row["model_id"] for row in selected}
    assert got[("operating_core", "co_conversion_pct")] == "gp_matern"
    assert got[("space_time", "co_conversion_pct")] == "gp_matern"
    assert {row["sources"] for row in selected} == {5}


def test_selector_handles_missing_and_nonfinite_metrics():
    report = {"models": {"test": {
        "a": {"metrics_by_target": {"x": {"mae": 2.0, "n": 4, "sources": ["s"]},
                                       "y": {"mae": float("nan")}}},
        "b": {"metrics_by_target": {"x": {"mae": 1.0, "n": 4, "sources": ["s"]}}},
    }}}
    assert best_model_by_target(report)[0]["model_id"] == "b"
    assert len(best_model_by_target(report)) == 1


def test_version_selector_is_rendered_on_htft_page():
    from streamlit.testing.v1 import AppTest
    from plataforma_ltft.ui_workflow import STEP_REGIME

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    next(button for button in app.button if button.label == "Começar planejamento").click().run()
    app.radio[0].set_value(STEP_REGIME).run()
    next(field for field in app.selectbox if field.label == "Regime").set_value("HTFT").run()
    assert not app.exception
    assert any("Melhor modelo retrospectivo por alvo" in item.value for item in app.markdown)
    assert any("Nenhum candidato foi promovido" in item.value for item in app.warning)


def test_version_comparison_uses_compatible_common_cohorts():
    profiles = ("operating_core", "space_time")
    targets = ("co_conversion_pct", "co2_selectivity_pct", "ch4_hc_carbon_pct",
               "c2_c4_olefins_hc_carbon_pct")
    metric = lambda mae: {"mae": mae, "n": 12, "sources": 4}
    v12 = {"profiles": {profile: {target: {
        "v7_gradient_boosting": {"metrics": {"nested_selected": metric(5.0)}},
        "v8_random_forest": {"metrics": {"nested_selected": metric(4.0)}},
    } for target in targets} for profile in profiles}}
    v13 = {"profiles": {profile: {target: {
        "v8_random_forest": {"metrics": {"robust__rf": metric(3.0)}}
    } for target in targets} for profile in profiles}}
    v14 = {"models": {profile: {
        "v6_nested_reference": {"metrics_by_target": {target: metric(2.0) for target in targets}},
        "multitask_lasso": {"metrics_by_target": {target: metric(1.0) for target in targets}},
    } for profile in profiles}}
    selected = compare_versions_v6_v14(v12, v13, v14)
    assert len(selected) == 8
    assert {(row["profile"], row["target"]) for row in selected} == {
        (profile, target)
        for profile in ("operating_core", "space_time")
        for target in ("co_conversion_pct", "co2_selectivity_pct", "ch4_hc_carbon_pct",
                       "c2_c4_olefins_hc_carbon_pct")
    }
    assert all(row["deployment_allowed"] is False for row in selected)
    assert all(row["version"] == "v14" and row["model_id"] == "multitask_lasso" for row in selected)


def test_public_summary_contains_aggregates_only_and_keeps_gate():
    path = ROOT / "data/htft/validation/htft_public_model_summary_v1.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    assert len(summary["best_v6_v14_by_profile_and_target"]) == 8
    assert len(summary["mlp_v15_pilot"]) == 8
    assert summary["model_promoted"] is False
    assert summary["recommendation_blocked"] is True
    serialized = json.dumps(summary)
    assert '"residuals"' not in serialized
    assert '"observed"' not in serialized
    assert '"predicted"' not in serialized
