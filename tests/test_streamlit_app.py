import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from plataforma_ltft.ui_workflow import (
    STEP_CATALYST, STEP_CONDITIONS, STEP_REGIME, STEP_RESULTS, WORKFLOW_STEPS,
)

ROOT = Path(__file__).resolve().parents[1]


class StreamlitAppTests(unittest.TestCase):
    def test_initial_page_has_no_exception_or_error(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.title[0].value, "Projeto Fischer–Tropsch")

    def test_htft_selection_resets_regime_specific_defaults(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        app.radio[0].set_value(STEP_REGIME).run()
        app.selectbox[0].set_value("HTFT").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("HTFT está em preparação" in item.value for item in app.warning))
        app.radio[0].set_value(STEP_CATALYST).run()
        self.assertEqual(app.selectbox[0].value, "Fe")
        app.radio[0].set_value(STEP_CONDITIONS).run()
        self.assertEqual(app.number_input[0].value, 320.0)

    def test_sidebar_exposes_the_six_guided_steps(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertEqual(tuple(app.radio[0].options), WORKFLOW_STEPS)
        self.assertTrue(any("progresso indica preenchimento" in item.value for item in app.caption))

    def test_guided_ltft_flow_persists_and_reaches_results(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        app.button[0].click().run()
        app.radio[0].set_value(STEP_REGIME).run()
        app.button[0].click().run()
        app.radio[0].set_value(STEP_CATALYST).run()
        app.button[0].click().run()
        app.radio[0].set_value(STEP_CONDITIONS).run()
        self.assertFalse(app.button[0].disabled)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertIsNotNone(app.session_state["screening_result"])
        app.radio[0].set_value(STEP_RESULTS).run()
        self.assertTrue(any("Distribuição ASF condicional calculada" in item.value for item in app.success))


if __name__ == "__main__":
    unittest.main()
