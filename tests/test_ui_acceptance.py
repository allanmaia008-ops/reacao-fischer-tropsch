import unittest

from plataforma_ltft.ui_design import GLOBAL_CSS


class UiAcceptanceTests(unittest.TestCase):
    def test_focus_mobile_and_reduced_motion_rules_exist(self):
        self.assertIn(":focus-visible", GLOBAL_CSS)
        self.assertIn("@media (max-width: 700px)", GLOBAL_CSS)
        self.assertIn("prefers-reduced-motion: reduce", GLOBAL_CSS)

    def test_maturity_categories_have_distinct_textual_classes(self):
        for css_class in (
            "ft-mathematical", "ft-heuristic", "ft-literature",
            "ft-experimental", "ft-calibrated", "ft-blocked",
        ):
            self.assertIn(css_class, GLOBAL_CSS)


if __name__ == "__main__":
    unittest.main()
