import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plataforma_ltft.domain import LTFTCase, migrate_case_v1_to_v2
from plataforma_ltft.experimental_protocol import (
    ExperimentalProtocolV2,
    migrate_case_to_experimental_protocol_v2,
    validate_experimental_protocol_v2,
)

ROOT = Path(__file__).resolve().parents[1]


def base_case() -> LTFTCase:
    legacy = json.loads((ROOT / "examples" / "caso_experimental_completo.json").read_text(encoding="utf-8"))["case"]
    return LTFTCase(**migrate_case_v1_to_v2(legacy))


class ExperimentalProtocolTests(unittest.TestCase):
    def test_migration_preserves_case_and_does_not_invent_new_fields(self):
        case = base_case()
        protocol = migrate_case_to_experimental_protocol_v2(case, "protocol-1", ("synthetic-source",))
        self.assertEqual(protocol.base_case["temperature_c"], case.temperature_c)
        self.assertTrue(all(value is None for value in protocol.reactor_configuration.values()))
        self.assertTrue(all(value is None for value in protocol.activation_protocol.values()))
        self.assertTrue(all(value is None for value in protocol.analytics.values()))
        validation = validate_experimental_protocol_v2(protocol)
        self.assertTrue(validation.structurally_valid)
        self.assertFalse(validation.ready_for_transport_assessment)
        self.assertIn("reactor_configuration.internal_diameter_mm", validation.missing_fields)

    def test_complete_synthetic_protocol_passes_readiness_gate(self):
        case = base_case()
        reactor = {
            "internal_diameter_mm": 9.1, "heated_length_mm": 300,
            "bed_porosity_fraction": 0.4, "catalyst_particle_diameter_um": 150,
            "catalyst_mass_g": 0.5, "inert_diluent": "SiC",
            "dilution_ratio_mass": 5, "diluent_particle_diameter_um": 180,
        }
        activation = {
            "gas_composition_mol_fraction": {"H2": 1.0}, "total_flow_mol_s": 0.001,
            "temperature_c": 350, "heating_rate_c_min": 1, "hold_time_h": 10,
            "pressure_bar": 1,
        }
        analytics = {
            "online_detectors": ["FID", "TCD"],
            "species_ranges": {"FID": "C1-C30", "TCD": "H2,CO,CO2,N2"},
            "calibration_protocol": "synthetic protocol for software test",
            "detection_limits": {"CO2_pct": 0.01},
            "quantification_limits": {"CO2_pct": 0.03},
            "heavy_fraction_method": "synthetic GC-MS method for software test",
            "heavy_fraction_recovery_pct": 95,
        }
        populated = {
            **{f"reactor_configuration.{key}": "synthetic-source" for key in reactor},
            **{f"activation_protocol.{key}": "synthetic-source" for key in activation},
            **{f"analytics.{key}": "synthetic-source" for key in analytics},
        }
        protocol = ExperimentalProtocolV2(
            protocol_id="synthetic-complete", base_case=case.__dict__,
            reactor_configuration=reactor, activation_protocol=activation,
            analytics=analytics, source_ids=("synthetic-source",), field_sources=populated,
        )
        validation = validate_experimental_protocol_v2(protocol)
        self.assertTrue(validation.structurally_valid, validation.errors)
        self.assertTrue(validation.ready_for_transport_assessment)
        self.assertTrue(validation.ready_for_experimental_execution_review)

    def test_missing_field_source_is_rejected(self):
        protocol = migrate_case_to_experimental_protocol_v2(base_case(), "protocol-2", ("source",))
        reactor = dict(protocol.reactor_configuration)
        reactor["internal_diameter_mm"] = 9.1
        changed = ExperimentalProtocolV2(**{**protocol.__dict__, "reactor_configuration": reactor})
        result = validate_experimental_protocol_v2(changed)
        self.assertFalse(result.structurally_valid)
        self.assertTrue(any("field_sources" in error for error in result.errors))

    def test_executed_status_requires_confirmation(self):
        protocol = migrate_case_to_experimental_protocol_v2(base_case(), "protocol-3", ("source",))
        changed = ExperimentalProtocolV2(**{**protocol.__dict__, "status": "executed"})
        self.assertTrue(any("execution_confirmed" in error for error in validate_experimental_protocol_v2(changed).errors))
