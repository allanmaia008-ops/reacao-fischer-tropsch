import unittest

from plataforma_ltft.units import (
    CANONICAL_UNITS,
    FIELD_QUANTITIES,
    UNIT_CATALOG_VERSION,
    UnitError,
    canonicalize,
    canonicalize_field,
    convert,
    normalize_unit,
    unit_catalog,
)


class UnitCatalogTests(unittest.TestCase):
    def test_catalog_is_versioned_and_covers_contract_fields(self):
        self.assertEqual(UNIT_CATALOG_VERSION, "1.0.0")
        self.assertEqual(CANONICAL_UNITS["pressure_absolute"], "bar")
        self.assertEqual(FIELD_QUANTITIES["feed_flow_mol_s"], "molar_flow")
        self.assertGreaterEqual(len(unit_catalog()), 30)

    def test_temperature_conversions_include_affine_offsets(self):
        self.assertAlmostEqual(convert(298.15, "K", "degC"), 25.0, places=10)
        self.assertAlmostEqual(convert(77.0, "degF", "degC"), 25.0, places=10)
        self.assertAlmostEqual(convert(25.0, "degC", "K"), 298.15, places=10)

    def test_absolute_pressure_conversions(self):
        self.assertAlmostEqual(convert(2.0, "MPa", "bar"), 20.0)
        self.assertAlmostEqual(convert(1.0, "atm", "kPa"), 101.325)
        self.assertEqual(normalize_unit("bara"), "bar")

    def test_time_and_inverse_time_are_distinct(self):
        self.assertAlmostEqual(convert(90.0, "min", "h"), 1.5)
        self.assertAlmostEqual(convert(1.0, "s^-1", "h^-1"), 3600.0)
        with self.assertRaises(UnitError):
            convert(1.0, "h", "h^-1")

    def test_molar_flow_mass_and_volume_conversions(self):
        self.assertAlmostEqual(convert(3.6, "kmol/h", "mol/s"), 1.0)
        self.assertAlmostEqual(convert(2.5, "kg", "g"), 2500.0)
        self.assertAlmostEqual(convert(1.2, "L", "mL"), 1200.0)

    def test_fraction_conversions_do_not_mix_mass_and_molar_basis(self):
        self.assertAlmostEqual(convert(0.2, "fraction", "wt_pct"), 20.0)
        self.assertAlmostEqual(convert(25.0, "mol_pct", "mol_fraction"), 0.25)
        with self.assertRaises(UnitError):
            convert(20.0, "wt_pct", "mol_fraction")

    def test_canonical_measurement_preserves_original_observation(self):
        result = canonicalize(2.0, "MPa", "pressure_absolute")
        self.assertEqual(result.canonical_value, 20.0)
        self.assertEqual(result.canonical_unit, "bar")
        self.assertEqual(result.original_value, 2.0)
        self.assertEqual(result.original_unit, "MPa")
        self.assertEqual(result.catalog_version, UNIT_CATALOG_VERSION)

    def test_contract_field_selects_expected_dimension(self):
        result = canonicalize_field("bed_volume_ml", 0.001, "L")
        self.assertEqual(result.canonical_value, 1.0)
        self.assertEqual(result.canonical_unit, "mL")
        with self.assertRaises(UnitError):
            canonicalize_field("bed_volume_ml", 1.0, "g")

    def test_invalid_values_units_and_fields_are_rejected(self):
        for invalid in (True, float("nan"), float("inf")):
            with self.assertRaises(UnitError):
                convert(invalid, "bar", "kPa")
        with self.assertRaises(UnitError):
            normalize_unit("barg")
        with self.assertRaises(UnitError):
            canonicalize_field("unknown_field", 1.0, "bar")


if __name__ == "__main__":
    unittest.main()

