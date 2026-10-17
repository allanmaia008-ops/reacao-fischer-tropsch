import copy
import json
from pathlib import Path
import tempfile
import unittest

from plataforma_ltft.dft_engine import (
    EngineInputError,
    build_vasp_input,
    validate_engine_input_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


class DFTVaspAdapterTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def inputs(self):
        structure = self.load("dft_structure_synthetic_v1.json")
        surface = self.load("dft_surface_synthetic_v1.json")
        surface["electronic_method"].update(
            {"engine": "vasp", "functional": "PBE", "dispersion": "D3(BJ)", "pseudopotential_family": "PAW_PBE"}
        )
        return structure, surface

    def test_builds_versioned_deterministic_vasp_bundle(self):
        structure, surface = self.inputs()
        first = build_vasp_input(structure, surface, input_set_id="ft038-synthetic-001")
        second = build_vasp_input(structure, surface, input_set_id="ft038-synthetic-001")
        self.assertEqual(first.files, second.files)
        self.assertEqual(first.manifest, second.manifest)
        self.assertEqual(set(first.files), {"INCAR", "KPOINTS", "POSCAR"})
        self.assertIn("ENCUT = 400", first.files["INCAR"])
        self.assertIn("GGA = Pe", first.files["INCAR"])
        self.assertIn("IVDW = 12", first.files["INCAR"])
        self.assertEqual(validate_engine_input_manifest(first.manifest), ())
        self.assertTrue(first.manifest["recommendation_blocked"])

    def test_refuses_unassigned_or_wrong_engine(self):
        structure, surface = self.inputs()
        surface["electronic_method"]["engine"] = "unassigned"
        with self.assertRaisesRegex(EngineInputError, "unsupported engine"):
            build_vasp_input(structure, surface, input_set_id="bad")

    def test_does_not_generate_or_hide_missing_potcar(self):
        structure, surface = self.inputs()
        bundle = build_vasp_input(structure, surface, input_set_id="ft038-synthetic-001")
        self.assertNotIn("POTCAR", bundle.files)
        self.assertEqual(bundle.manifest["required_external_files"][0]["status"], "missing")

    def test_writes_without_overwriting_existing_bundle(self):
        structure, surface = self.inputs()
        bundle = build_vasp_input(structure, surface, input_set_id="ft038-synthetic-001")
        with tempfile.TemporaryDirectory() as folder:
            paths = bundle.write(Path(folder))
            self.assertEqual({path.name for path in paths}, {"INCAR", "KPOINTS", "POSCAR", "manifest.json"})
            with self.assertRaises(FileExistsError):
                bundle.write(Path(folder))

    def test_contract_change_changes_source_fingerprint(self):
        structure, surface = self.inputs()
        first = build_vasp_input(structure, surface, input_set_id="ft038-synthetic-001")
        changed = copy.deepcopy(surface)
        changed["electronic_method"]["cutoff_ev"] = 450
        second = build_vasp_input(structure, changed, input_set_id="ft038-synthetic-001")
        self.assertNotEqual(
            first.manifest["source"]["contract_fingerprint_sha256"],
            second.manifest["source"]["contract_fingerprint_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
