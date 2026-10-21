from pathlib import Path
import tempfile
import unittest

from plataforma_ltft.database import Database


class DatabaseTests(unittest.TestCase):
    def test_migrations_are_versioned_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "platform.sqlite3")
            self.assertEqual(database.migrate(), ("001_core.sql", "002_auth.sql", "003_worker_jobs.sql", "004_run_results_and_audit_chain.sql"))
            self.assertEqual(database.migrate(), ())
            self.assertEqual(database.applied_migrations(), ("001_core.sql", "002_auth.sql", "003_worker_jobs.sql", "004_run_results_and_audit_chain.sql"))

    def test_runs_and_audit_events_round_trip_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "platform.sqlite3")
            database.migrate()
            database.create_project("p-1", "Fischer-Tropsch")
            database.create_run(
                "r-1", "p-1", {"temperature_c": 220, "recommendation_blocked": True},
                case_id="case-1", status="blocked",
            )
            self.assertEqual(
                database.get_run("r-1")["payload"],
                {"recommendation_blocked": True, "temperature_c": 220},
            )
            self.assertEqual(database.get_run("r-1")["status"], "blocked")
            self.assertEqual(database.record_event("run.note", {"run_id": "r-1"}, project_id="p-1"), 3)
            self.assertTrue(database.verify_audit_chain()["valid"])

    def test_job_idempotency_leases_retry_and_cancel(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "platform.sqlite3")
            database.migrate()
            database.create_project("p", "Project")
            job_id = database.enqueue_run("r1", "p", {"desired_product":"C5-C11"}, idempotency_key="same", max_attempts=2)
            self.assertEqual(database.enqueue_run("ignored-run", "p", {}, idempotency_key="same"), job_id)
            claimed = database.claim_job("worker-1")
            self.assertEqual(claimed["job_id"], job_id)
            self.assertEqual(database.finish_job(job_id, "worker-1", success=False, error="ValueError"), "queued")
            with database.connection() as connection:
                connection.execute("UPDATE worker_jobs SET available_at='2000-01-01T00:00:00Z' WHERE job_id=?", (job_id,))
            claimed = database.claim_job("worker-2")
            self.assertEqual(claimed["attempt"], 2)
            self.assertEqual(database.finish_job(job_id, "worker-2", success=False, error="ValueError"), "failed")
            self.assertTrue(database.verify_audit_chain()["valid"])
            job2 = database.enqueue_run("r2", "p", {}, idempotency_key="cancel-me")
            self.assertTrue(database.cancel_job(job2))
            self.assertFalse(database.cancel_job(job2))

    def test_audit_hash_chain_detects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "platform.sqlite3")
            database.migrate()
            database.record_event("case.updated", {"case_id":"c1"})
            self.assertTrue(database.verify_audit_chain()["valid"])
            with database.connection() as connection:
                connection.execute("UPDATE audit_events SET payload_json='{}' WHERE event_id=1")
            self.assertFalse(database.verify_audit_chain()["valid"])

    def test_backup_restore_integrity_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = Database(root / "platform.sqlite3")
            database.migrate()
            database.create_project("p-1", "Project")
            database.create_run("r-1", "p-1", {"value": 3})
            backup = database.backup_to(root / "backups" / "snapshot.sqlite3")
            restored = Database.restore_backup(backup, root / "restored.sqlite3")
            self.assertEqual(restored.get_run("r-1")["payload"], {"value": 3})
            with self.assertRaises(FileExistsError):
                database.backup_to(backup)
            with self.assertRaises(FileExistsError):
                Database.restore_backup(backup, root / "restored.sqlite3")

    def test_status_and_required_fields_are_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "platform.sqlite3")
            database.migrate()
            with self.assertRaises(ValueError):
                database.create_run("r-1", "p-1", {}, status="done")
            with self.assertRaises(ValueError):
                database.create_project(" ", " ")


if __name__ == "__main__":
    unittest.main()
