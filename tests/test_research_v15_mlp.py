import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_research_v14_probabilistic_multitask import TARGETS_ORDER  # noqa: E402
from run_research_v15_mlp import compare_mlp, fit_predict_mlp  # noqa: E402
from plataforma_ltft.target_research import PROFILES  # noqa: E402


def synthetic_rows():
    rows = []
    for group in range(5):
        for replicate in range(2):
            rows.append({
                "row_id": f"g{group}-{replicate}", "source_doi": f"doi-{group}",
                "family": "Fe" if group % 2 else "Co", "temperature_c": 290 + group * 8 + replicate * 2,
                "pressure_bar": 10 + group, "h2_co_ratio": 1.2 + group * 0.1,
                "ghsv_ml_gcat_h": 5000 + group * 500, "tos_h": 24 + replicate * 12,
                "co_conversion_pct": 20 + group * 4 + replicate,
                "co2_selectivity_pct": 5 + group + replicate * 0.5,
                "ch4_hc_carbon_pct": 10 + group * 1.5 + replicate,
                "c2_c4_olefins_hc_carbon_pct": 20 + group * 2 + replicate,
            })
    return rows


def test_mlp_predictions_are_bounded_and_multi_output():
    rows = synthetic_rows()
    train = [row for row in rows if row["source_doi"] != "doi-4"]
    test = [row for row in rows if row["source_doi"] == "doi-4"]
    prediction, metadata = fit_predict_mlp(
        train, test, PROFILES["operating_core"], TARGETS_ORDER,
    )
    assert set(prediction) == set(TARGETS_ORDER)
    assert all(np.all((values >= 0) & (values <= 100)) for values in prediction.values())
    assert metadata["inner_source_groups"] == 4


def test_mlp_comparison_keeps_source_groups_out_of_training():
    report = compare_mlp(synthetic_rows(), "operating_core")
    assert report["eligible_rows"] == 10
    assert report["sources"] == 5
    for fold in report["folds"]:
        if fold["status"] == "evaluated":
            assert fold["held_out"] not in fold["training_sources"]
            assert len(fold["model_details"]["inner_source_grouped_mae"]) == 4
    assert all(metrics["n"] == 10 for metrics in report["metrics_by_target"].values())
