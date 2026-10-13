import unittest

from plataforma_ltft.thermodynamics import ThermodynamicContract, thermodynamic_readiness, validate_thermodynamic_contract


def contract(status="draft", datasets=(), metrics=None):
    return ThermodynamicContract(
        package_id="candidate-test", package_version="1", provider="test provider",
        equation_of_state="declared EOS", mixing_rule="declared mixing rule",
        component_mapping={"H2": "hydrogen", "CO": "carbon monoxide", "H2O": "water"},
        pseudocomponent_method="declared method", vle_method="declared method",
        phase_coverage=("syngas", "water", "light_hydrocarbons", "liquid_hydrocarbons", "waxes"),
        temperature_c=(180.0, 260.0), pressure_bar=(1.0, 50.0),
        source_ids=("source",), validation_dataset_ids=datasets,
        validation_metrics={} if metrics is None else metrics, validation_status=status,
    )


class ThermodynamicsTests(unittest.TestCase):
    def test_complete_draft_is_registered_but_blocked(self):
        item = contract()
        self.assertEqual(validate_thermodynamic_contract(item), ())
        self.assertFalse(thermodynamic_readiness(item)["valid_for_process_model"])

    def test_validated_package_requires_data_and_metrics(self):
        errors = validate_thermodynamic_contract(contract(status="validated"))
        self.assertTrue(any("validation_dataset_ids" in error for error in errors))
        self.assertTrue(any("métricas" in error for error in errors))

    def test_validated_package_passes_contract_gate(self):
        state = thermodynamic_readiness(contract(status="validated", datasets=("vle-data",), metrics={"aape_vle_pct": 3.2}))
        self.assertTrue(state["valid_for_process_model"])

    def test_all_phase_groups_are_required(self):
        item = contract()
        incomplete = ThermodynamicContract(**{**item.__dict__, "phase_coverage": ("syngas", "water")})
        self.assertTrue(any("Cobertura" in error for error in validate_thermodynamic_contract(incomplete)))

    def test_non_finite_domain_and_metrics_are_rejected(self):
        item = contract(status="validated", datasets=("data",), metrics={"aape_pct": float("nan")})
        invalid = ThermodynamicContract(**{**item.__dict__, "temperature_c": (180.0, float("inf"))})
        errors = validate_thermodynamic_contract(invalid)
        self.assertTrue(any("temperature_c" in error for error in errors))
        self.assertTrue(any("métricas" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
