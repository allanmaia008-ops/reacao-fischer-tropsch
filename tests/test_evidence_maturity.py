import unittest

from plataforma_ltft.evidence_maturity import maturity_catalog, result_maturity_rows


class EvidenceMaturityTests(unittest.TestCase):
    def test_catalog_has_all_governed_categories(self):
        self.assertEqual(
            {row["category"] for row in maturity_catalog()},
            {"matemático", "heurístico", "literatura", "experimental", "calibrado", "bloqueado"},
        )

    def test_result_rows_follow_explicit_result_state(self):
        rows = result_maturity_rows({
            "alpha_origin": "informado_pelo_usuario",
            "recommendation_blocked": True,
            "recommendation_blocking_reason": "Faltam dados.",
        })
        self.assertEqual([row["category"] for row in rows], ["matemático", "heurístico", "bloqueado"])
        self.assertEqual(rows[-1]["limitation"], "Faltam dados.")


if __name__ == "__main__":
    unittest.main()
