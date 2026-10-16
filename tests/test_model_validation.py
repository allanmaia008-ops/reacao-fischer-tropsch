import unittest
from plataforma_ltft.model_validation import validation_metrics, assess_validation


class ModelValidationTests(unittest.TestCase):
    def test_metrics_definitions(self):
        result=validation_metrics([1,2,3],[1,3,2])
        self.assertAlmostEqual(result["mae"],2/3)
        self.assertAlmostEqual(result["mse"],2/3)
        self.assertAlmostEqual(result["bias"],0)

    def test_all_scientific_gates_are_required(self):
        metrics={"n":100,"nmae_mean":.1,"nrmse_mean":.12,"bias":0,"mean_observed":1}
        diagnostics={"pi95_coverage":.95,"std_residual_outlier_fraction":0,"max_abs_spearman_residual_driver":.1,"heteroscedasticity_p_value":.2,"cluster_bootstrap_ci_reported":True,"measurement_uncertainty_propagated":True,"independent_dataset":False,"catalyst_and_domain_compatible":True}
        result=assess_validation(metrics,diagnostics)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["independent_dataset"])

if __name__=="__main__": unittest.main()
