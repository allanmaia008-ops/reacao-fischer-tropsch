import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class StreamlitAppTests(unittest.TestCase):
    def test_initial_page_has_no_exception_or_error(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.title[0].value, "Reação Fischer–Tropsch")

    def test_htft_selection_resets_regime_specific_defaults(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        app.selectbox[1].set_value("HTFT").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox[2].value, "Fe")
        self.assertEqual(app.number_input[0].value, 320.0)
        self.assertTrue(any("HTFT está em preparação" in item.value for item in app.warning))


if __name__ == "__main__":
    unittest.main()
