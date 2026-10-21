import unittest

from plataforma_ltft.homologation import build_preflight_report, REQUIRED_GATES


class HomologationTests(unittest.TestCase):
    def test_technical_checks_do_not_auto_approve_homologation(self):
        report=build_preflight_report([{"name":"tests","passed":True}])
        self.assertEqual(report["technical_preflight"],"passed")
        self.assertEqual(report["homologation"],"pending_gates")
        self.assertFalse(report["production_ready"])
        self.assertEqual(set(report["required_gates"]),set(REQUIRED_GATES))

    def test_failed_check_blocks_technical_preflight(self):
        report=build_preflight_report([{"name":"tests","passed":False}],gates={k:True for k in REQUIRED_GATES})
        self.assertEqual(report["technical_preflight"],"failed")
        self.assertEqual(report["homologation"],"pending_gates")


if __name__=="__main__": unittest.main()
