import io
import json
import logging
import unittest

from plataforma_ltft.observability import JsonFormatter, emit, metrics_snapshot


class ObservabilityTests(unittest.TestCase):
    def test_json_log_uses_safe_context_fields_only(self):
        record=logging.LogRecord("test",logging.INFO,"",0,"worker",(),None)
        record.event="job.done"; record.run_id="r1"; record.password="secret"
        parsed=json.loads(JsonFormatter().format(record))
        self.assertEqual(parsed["event"],"job.done")
        self.assertEqual(parsed["run_id"],"r1")
        self.assertNotIn("password",parsed)

    def test_metrics_snapshot_has_process_counts_and_no_payloads(self):
        emit("test.counter",run_id="safe-run-id")
        snapshot=metrics_snapshot()
        self.assertGreaterEqual(snapshot["process_events"]["test.counter"],1)
        self.assertEqual(snapshot["database"]["status"],"not_configured")


if __name__=="__main__": unittest.main()
