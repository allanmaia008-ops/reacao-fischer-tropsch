import unittest

from plataforma_ltft.kinetics import KineticContract, kinetic_readiness, validate_kinetic_contract


def complete_contract(status="validated", validation_ids=("dataset-001",)):
    return KineticContract(
        model_id="example-contract-test", model_version="1.0",
        rate_expression="symbolic expression registered by the model owner",
        variables={"temperature": "K", "partial_pressure_H2": "bar", "partial_pressure_CO": "bar"},
        parameters={"k_ref": 1.0}, parameter_units={"k_ref": "mol_CO g_cat^-1 s^-1"},
        applicability_domain={"ft_regime": "LTFT", "temperature_c": [200, 240], "pressure_bar": [10, 30], "catalyst_family": "Co"},
        source_ids=("source-001",), uncertainty_method="declared test method",
        validation_dataset_ids=validation_ids, calibration_status=status,
    )


class KineticContractTests(unittest.TestCase):
    def test_complete_validated_contract_is_ready(self):
        contract = complete_contract()
        self.assertEqual(validate_kinetic_contract(contract), ())
        self.assertTrue(kinetic_readiness(contract)["valid_for_rate_calculation"])

    def test_draft_contract_remains_blocked(self):
        readiness = kinetic_readiness(complete_contract(status="draft", validation_ids=()))
        self.assertTrue(readiness["contract_valid"])
        self.assertFalse(readiness["valid_for_rate_calculation"])

    def test_units_sources_domain_and_validation_are_enforced(self):
        contract = complete_contract(status="validated", validation_ids=())
        errors = validate_kinetic_contract(contract)
        self.assertTrue(any("validation_dataset_ids" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
