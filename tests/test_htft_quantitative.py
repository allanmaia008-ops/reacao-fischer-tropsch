from pathlib import Path
import unittest

from plataforma_ltft.htft_quantitative import evaluate_external_holdout, freeze_persistence_model, load_dataset

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/htft/htft_ahmed_2021_temperature_holdout.csv"


class HTFTQuantitativeTests(unittest.TestCase):
    def test_frozen_model_and_external_holdout_are_separate(self):
        rows = load_dataset(DATA)
        model = freeze_persistence_model(rows)
        self.assertTrue(model["frozen"])
        self.assertEqual(model["calibration_temperature_c"], [300.0])
        self.assertEqual(sum(row["split"] == "external_holdout" for row in rows), 4)

    def test_metrics_residuals_uncertainty_and_failed_criterion_are_explicit(self):
        report = evaluate_external_holdout(load_dataset(DATA), freeze_persistence_model(load_dataset(DATA)))
        self.assertEqual(report["external_holdout_rows"], 4)
        self.assertEqual(len(report["residuals"]), 16)
        self.assertAlmostEqual(report["metrics"]["co_conversion_pct"]["mae"], 28.0)
        self.assertAlmostEqual(report["metrics"]["c2_c4_olefins_carbon_pct"]["rmse"], 6.9101374805)
        self.assertFalse(report["quantitative_validation_passed"])
        self.assertTrue(report["recommendation_blocked"])


if __name__ == "__main__":
    unittest.main()
