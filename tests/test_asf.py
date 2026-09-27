import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plataforma_ltft.asf import product_bands, tail_fraction


class ASFTests(unittest.TestCase):
    def test_exclusive_bands_close(self):
        bands = product_bands(0.85)
        self.assertAlmostEqual(sum(bands[k] for k in ("CH4", "C2-C4", "C5-C11", "C12-C20", "C21+")), 1.0)

    def test_c5plus_is_tail(self):
        self.assertAlmostEqual(product_bands(0.8)["C5+"], tail_fraction(0.8, 5))

