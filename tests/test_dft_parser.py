import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from plataforma_ltft.dft_parser import parse_vasp_outcar

ROOT = Path(__file__).resolve().parents[1]


def complete_outcar():
    return """vasp.6.4.2
NIONS =      1 ions
aborting loop because EDIFF is reached
free energy TOTEN = -10.000000 eV
POSITION (Angst) TOTAL-FORCE (eV/Angst)
-----------------------------------------------------------------------------------
0.000 0.000 0.000 0.020 0.000 0.000
-----------------------------------------------------------------------------------
aborting loop because EDIFF is reached
free energy TOTEN = -10.123456 eV
POSITION (Angst) TOTAL-FORCE (eV/Angst)
-----------------------------------------------------------------------------------
0.000 0.000 0.000 0.010 0.000 0.000
-----------------------------------------------------------------------------------
reached required accuracy - stopping structural energy minimisation
General timing and accounting informations for this job:
"""


class DFTOutputParserTests(unittest.TestCase):
    def test_parses_energy_forces_and_convergence_with_source_hash(self):
        result = parse_vasp_outcar(
            complete_outcar(),
            source_name="nested/OUTCAR",
            force_threshold_ev_angstrom=0.03,
        )
        self.assertEqual(result["status"], "succeeded")
        self.assertAlmostEqual(result["total_energy_ev"], -10.123456)
        self.assertEqual(result["ionic_steps_with_forces"], 2)
        self.assertAlmostEqual(result["final_max_force_ev_angstrom"], 0.01)
        self.assertEqual(result["final_force_count"], 1)
        self.assertEqual(result["reported_nions"], 1)
        self.assertEqual(result["expected_atom_count"], 1)
        self.assertTrue(result["force_count_matches_expected"])
        self.assertTrue(result["electronic_converged"])
        self.assertTrue(result["ionic_converged"])
        self.assertEqual(result["source"]["name"], "OUTCAR")
        self.assertTrue(result["recommendation_blocked"])

    def test_file_presence_or_normal_termination_alone_is_not_success(self):
        result = parse_vasp_outcar(
            "free energy TOTEN = -1.0 eV\n"
            "General timing and accounting informations for this job:\n"
        )
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["electronic_converged"])
        self.assertIsNone(result["ionic_converged"])

    def test_explicit_error_and_force_failure_are_reported(self):
        failed = parse_vasp_outcar("VERY BAD NEWS! internal error in subroutine\n")
        self.assertEqual(failed["status"], "failed")
        self.assertTrue(failed["error_messages"])
        unconverged = parse_vasp_outcar(
            complete_outcar().replace("reached required accuracy - stopping structural energy minimisation", ""),
            force_threshold_ev_angstrom=0.005,
        )
        self.assertEqual(unconverged["status"], "unconverged")
        self.assertFalse(unconverged["ionic_converged"])

    def test_ionic_stop_marker_does_not_override_force_threshold(self):
        text = complete_outcar().replace("0.010 0.000 0.000", "0.080 0.000 0.000")
        result = parse_vasp_outcar(text, force_threshold_ev_angstrom=0.03)
        self.assertTrue(result["ionic_stop_marker_present"])
        self.assertFalse(result["ionic_converged"])
        self.assertEqual(result["status"], "unconverged")

    def test_ionic_status_is_unknown_without_declared_force_threshold(self):
        result = parse_vasp_outcar(complete_outcar())
        self.assertTrue(result["ionic_stop_marker_present"])
        self.assertIsNone(result["ionic_converged"])
        self.assertEqual(result["status"], "incomplete")

    def test_synthetic_state_is_preserved_and_empty_input_rejected(self):
        synthetic = parse_vasp_outcar(complete_outcar(), synthetic=True)
        self.assertEqual(synthetic["status"], "synthetic_test")
        with self.assertRaises(ValueError):
            parse_vasp_outcar("  ")

    def test_expected_force_count_prevents_partial_structure_from_appearing_valid(self):
        result = parse_vasp_outcar(
            complete_outcar(),
            force_threshold_ev_angstrom=0.03,
            expected_atom_count=2,
        )
        self.assertEqual(result["status"], "incomplete")
        self.assertFalse(result["force_count_matches_expected"])

    def test_parsed_result_schema_accepts_conservative_parser_output(self):
        schema = json.loads((ROOT / "schemas" / "ft-dft-parsed-result-v1.schema.json").read_text(encoding="utf-8"))
        result = parse_vasp_outcar(complete_outcar(), force_threshold_ev_angstrom=0.03)
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(result)), [])


if __name__ == "__main__":
    unittest.main()
