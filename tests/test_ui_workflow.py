import unittest

from plataforma_ltft.ui_workflow import (
    STEP_CATALYST,
    STEP_PRODUCT,
    STEP_REGIME,
    WORKFLOW_STEPS,
    catalyst_input_errors,
    invalidate_from,
    mark_step_complete,
    pending_steps,
    product_input_error,
    regime_input_errors,
    workflow_progress,
)


class UIWorkflowTests(unittest.TestCase):
    def test_progress_uses_only_known_unique_steps(self):
        completed = [STEP_PRODUCT, STEP_PRODUCT, "desconhecida"]
        self.assertEqual(workflow_progress(completed), 1 / len(WORKFLOW_STEPS))

    def test_completion_and_pending_steps_follow_official_order(self):
        completed = mark_step_complete([], STEP_REGIME)
        completed = mark_step_complete(completed, STEP_PRODUCT)
        self.assertEqual(completed, [STEP_PRODUCT, STEP_REGIME])
        self.assertEqual(pending_steps(completed)[0], STEP_CATALYST)

    def test_change_invalidates_the_step_and_dependents(self):
        self.assertEqual(
            invalidate_from(WORKFLOW_STEPS, STEP_CATALYST),
            [STEP_PRODUCT, STEP_REGIME],
        )

    def test_unknown_step_is_rejected(self):
        with self.assertRaises(ValueError):
            mark_step_complete([], "etapa inexistente")

    def test_product_validation_is_immediate_and_bounded(self):
        self.assertIsNone(product_input_error(""))
        self.assertIsNone(product_input_error("c16"))
        self.assertIn("C seguido", product_input_error("diesel"))
        self.assertIn("C1 e C60", product_input_error("C61"))

    def test_transition_and_catalyst_report_specific_missing_fields(self):
        self.assertEqual(len(regime_input_errors("transicao", "")), 1)
        self.assertFalse(regime_input_errors("LTFT", ""))
        errors = catalyst_input_errors("", "Co0", "")
        self.assertEqual(errors, ("Preencha composição.", "Preencha suporte."))


if __name__ == "__main__":
    unittest.main()
