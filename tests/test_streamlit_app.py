import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from plataforma_ltft.ui_workflow import (
    STEP_CATALYST, STEP_CONDITIONS, STEP_EVIDENCE, STEP_REGIME, STEP_RESULTS, WORKFLOW_STEPS,
)

ROOT = Path(__file__).resolve().parents[1]


class StreamlitAppTests(unittest.TestCase):
    def test_initial_page_has_no_exception_or_error(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.title[0].value, "Projeto Fischer–Tropsch")
        self.assertTrue(any("Planejamento científico orientado" in item.value for item in app.subheader))
        self.assertTrue(any("Protótipo funcional" in item.value for item in app.success))
        self.assertTrue(any("Em preparação" in item.value for item in app.warning))
        self.assertTrue(any("Bloqueadas" in item.value for item in app.markdown))

    def test_home_primary_action_opens_product_step(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        next(button for button in app.button if button.label == "Começar planejamento").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.session_state["show_home"])
        self.assertTrue(any(item.value == "Produto desejado" for item in app.subheader))

    def test_invalid_exact_product_is_reported_before_confirmation(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        next(button for button in app.button if button.label == "Começar planejamento").click().run()
        next(field for field in app.text_input if field.label == "Hidrocarboneto individual, opcional").set_value("C61").run()
        self.assertTrue(any("C1 e C60" in item.value for item in app.error))
        confirm = next(button for button in app.button if button.label == "Confirmar produto")
        self.assertTrue(confirm.disabled)

    def test_transition_requires_justification_immediately(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        next(button for button in app.button if button.label == "Começar planejamento").click().run()
        app.radio[0].set_value(STEP_REGIME).run()
        app.selectbox[0].set_value("transicao").run()
        self.assertTrue(any("justificativa científica" in item.value for item in app.error))
        confirm = next(button for button in app.button if button.label == "Confirmar regime")
        self.assertTrue(confirm.disabled)

    def test_htft_selection_resets_regime_specific_defaults(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        next(button for button in app.button if button.label == "Começar planejamento").click().run()
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
        next(button for button in app.button if button.label == "Começar planejamento").click().run()
        next(button for button in app.button if button.label == "Confirmar produto").click().run()
        app.radio[0].set_value(STEP_REGIME).run()
        next(button for button in app.button if button.label == "Confirmar regime").click().run()
        app.radio[0].set_value(STEP_CATALYST).run()
        next(button for button in app.button if button.label == "Confirmar catalisador").click().run()
        app.radio[0].set_value(STEP_CONDITIONS).run()
        calculate = next(button for button in app.button if button.label == "Validar e calcular distribuição ASF")
        self.assertFalse(calculate.disabled)
        calculate.click().run()
        self.assertFalse(app.exception)
        self.assertIsNotNone(app.session_state["screening_result"])
        app.radio[0].set_value(STEP_RESULTS).run()
        self.assertTrue(any("Distribuição ASF condicional calculada" in item.value for item in app.success))
        self.assertTrue(any("Curva ASF por número de carbono" in item.value for item in app.markdown))
        self.assertTrue(any("cauda analítica C61+" in item.value for item in app.caption))
        self.assertTrue(any("Recomendação bloqueada" in item.value for item in app.error))
        self.assertTrue(any("Maturidade dos resultados" in item.value for item in app.markdown))
        next(field for field in app.checkbox if field.label == "Ativar comparação matemática").set_value(True).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Sensibilidade matemática" in item.value for item in app.warning))

    def test_evidence_step_exposes_all_maturity_categories(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        next(button for button in app.button if button.label == "Começar planejamento").click().run()
        app.radio[0].set_value(STEP_EVIDENCE).run()
        rendered = " ".join(item.value for item in app.markdown)
        for category in ("matemático", "heurístico", "literatura", "experimental", "calibrado", "bloqueado"):
            self.assertIn(category, rendered)


if __name__ == "__main__":
    unittest.main()
