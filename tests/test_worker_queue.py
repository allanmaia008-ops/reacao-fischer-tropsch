import json
from pathlib import Path
import tempfile
import unittest

from plataforma_ltft.database import Database
from plataforma_ltft.worker import run_queued_once

ROOT=Path(__file__).resolve().parents[1]


class QueueWorkerTests(unittest.TestCase):
    def test_claim_execute_persist_result_and_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            db=Database(root/"db.sqlite3"); db.migrate(); db.create_project("p","Project")
            payload=json.loads((ROOT/"examples/caso_co.json").read_text(encoding="utf-8"))
            job=db.enqueue_run("run-1","p",payload,idempotency_key="key-1")
            done=run_queued_once(db,root/"outputs",worker_id="worker-A")
            self.assertEqual(done["job_id"],job)
            record=db.get_run("run-1")
            self.assertEqual(record["status"],"succeeded")
            self.assertEqual(record["result"]["status"],"distribuicao_asf_condicional")
            self.assertTrue(db.verify_audit_chain()["valid"])

    def test_invalid_payload_is_failed_without_leaking_exception_text(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            db=Database(root/"db.sqlite3"); db.migrate(); db.create_project("p","Project")
            job=db.enqueue_run("run-1","p",{"password":"not logged","bad":True},idempotency_key="key-1",max_attempts=1)
            result=run_queued_once(db,root/"outputs",worker_id="worker-A")
            self.assertEqual(result["status"],"failed")
            self.assertEqual(result["error_code"],"ValueError")
            self.assertTrue(db.verify_audit_chain()["valid"])


if __name__=="__main__": unittest.main()
