import unittest

from plataforma_ltft.ui_workflow import (
    STEP_CATALYST,
    STEP_PRODUCT,
    STEP_REGIME,
    WORKFLOW_STEPS,
    invalidate_from,
    mark_step_complete,
    pending_steps,
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


if __name__ == "__main__":
    unittest.main()
