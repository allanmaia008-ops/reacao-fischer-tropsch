import unittest

from plataforma_ltft.kinetics import KineticContract
from plataforma_ltft.reactor import ReactorContract, inlet_balance, reactor_readiness, validate_reactor_contract


def reactor():
    return ReactorContract(
        reactor_id="ltft-fixed-bed-test", reactor_type="fixed_bed_pfr",
        feed_molar_flow_mol_s={"H2": 2.0, "CO": 1.0, "N2": 0.1},
        temperature_c=220.0, pressure_bar=20.0,
        catalyst_mass_g=10.0, whsv_h_1=1.0,
        geometry={"diameter_m": 0.02, "length_m": 1.0},
    )


def validated_kinetic():
    return KineticContract(
        model_id="test", model_version="1", rate_expression="registered expression",
        variables={"temperature": "K", "partial_pressure_H2": "bar", "partial_pressure_CO": "bar"},
        parameters={"k": 1.0}, parameter_units={"k": "mol g_cat^-1 s^-1"},
        applicability_domain={"ft_regime": "LTFT", "temperature_c": [200, 240], "pressure_bar": [10, 30], "catalyst_family": "Co"},
        source_ids=("source",), uncertainty_method="test", validation_dataset_ids=("data",), calibration_status="validated",
    )


class ReactorTests(unittest.TestCase):
    def test_contract_and_inlet_inventory(self):
        contract = reactor()
        self.assertEqual(validate_reactor_contract(contract), ())
        balance = inlet_balance(contract)
        self.assertAlmostEqual(balance["total_molar_flow_mol_s"], 3.1)
        self.assertIsNone(balance["outlet_molar_flow_mol_s"])

    def test_simulation_stays_blocked_without_kinetics_thermo_and_models(self):
        state = reactor_readiness(reactor(), None, thermo_ready=False)
        self.assertFalse(state["valid_for_simulation"])
        self.assertIsNone(state["CO_conversion_pct"])
        self.assertTrue(any("cinético" in reason for reason in state["blocking_reasons"]))

    def test_validated_kinetic_alone_is_not_enough(self):
        state = reactor_readiness(reactor(), validated_kinetic(), thermo_ready=True)
        self.assertFalse(state["valid_for_simulation"])
        self.assertTrue(any("energy_model" in reason for reason in state["blocking_reasons"]))

    def test_space_velocity_and_geometry_must_be_positive(self):
        item = reactor()
        invalid = ReactorContract(**{**item.__dict__, "whsv_h_1": 0.0, "geometry": {"diameter_m": -0.02}})
        errors = validate_reactor_contract(invalid)
        self.assertTrue(any("whsv_h_1" in error for error in errors))
        self.assertTrue(any("geometria" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
