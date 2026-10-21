"""Small local SQLite persistence provider and migration/backup tools (FT-041).

This module is a local-development pilot. It does not claim PostgreSQL or
production deployment readiness.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
from hashlib import sha256
import json
import uuid
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping

MIGRATION_DIRECTORY = Path(__file__).resolve().parents[2] / "migrations"
RUN_STATUSES = {"created", "validated", "queued", "running", "succeeded", "failed", "blocked", "cancelled"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class DatabaseError(RuntimeError):
    """Raised when persistence invariants are not met."""


class Database:
    """SQLite development database with versioned migrations and safe backups."""

    def __init__(self, path: str | Path, *, migration_directory: str | Path | None = None):
        self.path = Path(path)
        self.migration_directory = Path(migration_directory or MIGRATION_DIRECTORY)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Commit on success and always close the handle (including on Windows)."""
        handle = self.connect()
        try:
            yield handle
            handle.commit()
        except Exception:
            handle.rollback()
            raise
        finally:
            handle.close()

    def migrate(self) -> tuple[str, ...]:
        self.migration_directory.mkdir(parents=True, exist_ok=True)
        applied_now: list[str] = []
        with self.connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(migration_id TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
            )
            applied = {
                row["migration_id"]
                for row in connection.execute("SELECT migration_id FROM schema_migrations")
            }
            for migration in sorted(self.migration_directory.glob("[0-9][0-9][0-9]_*.sql")):
                migration_id = migration.name
                if migration_id in applied:
                    continue
                sql = migration.read_text(encoding="utf-8")
                escaped_id = migration_id.replace("'", "''")
                escaped_time = _utc_now().replace("'", "''")
                script = (
                    "BEGIN IMMEDIATE;\n"
                    + sql
                    + f"\nINSERT INTO schema_migrations(migration_id, applied_at) "
                    f"VALUES ('{escaped_id}', '{escaped_time}');\nCOMMIT;"
                )
                try:
                    connection.executescript(script)
                except sqlite3.Error:
                    if connection.in_transaction:
                        connection.rollback()
                    raise
                applied_now.append(migration_id)
            self._initialize_audit_chain(connection)
        return tuple(applied_now)

    @staticmethod
    def _event_hash(previous: str, event: Mapping[str, Any]) -> str:
        canonical = json.dumps(dict(event), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256((previous + canonical).encode("utf-8")).hexdigest()

    @classmethod
    def _initialize_audit_chain(cls, connection: sqlite3.Connection) -> None:
        # One-time chain anchoring for events written before migration 004.
        rows = connection.execute("SELECT * FROM audit_events ORDER BY event_id").fetchall()
        if not rows or all(row["event_hash"] for row in rows):
            return
        previous = "0" * 64
        for row in rows:
            event = {key: row[key] for key in ("event_id", "project_id", "actor_id", "event_type", "payload_json", "created_at")}
            digest = cls._event_hash(previous, event)
            connection.execute("UPDATE audit_events SET previous_hash=?,event_hash=? WHERE event_id=?", (previous, digest, row["event_id"]))
            previous = digest

    @classmethod
    def _append_event(cls, connection: sqlite3.Connection, project_id: str | None, actor_id: str | None,
                      event_type: str, payload: Mapping[str, Any], created_at: str) -> int:
        latest = connection.execute("SELECT event_hash FROM audit_events ORDER BY event_id DESC LIMIT 1").fetchone()
        previous = latest[0] if latest and latest[0] else "0" * 64
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        cursor = connection.execute(
            "INSERT INTO audit_events(project_id,actor_id,event_type,payload_json,created_at,previous_hash,event_hash) VALUES (?,?,?,?,?,?,?)",
            (project_id,actor_id,event_type,serialized,created_at,previous,"pending"),
        )
        event_id = int(cursor.lastrowid)
        event = {"event_id":event_id,"project_id":project_id,"actor_id":actor_id,"event_type":event_type,"payload_json":serialized,"created_at":created_at}
        digest = cls._event_hash(previous, event)
        connection.execute("UPDATE audit_events SET event_hash=? WHERE event_id=?", (digest,event_id))
        return event_id

    def verify_audit_chain(self) -> dict[str, Any]:
        with self.connection() as connection:
            rows = connection.execute("SELECT * FROM audit_events ORDER BY event_id").fetchall()
        previous = "0" * 64
        for row in rows:
            event = {key: row[key] for key in ("event_id", "project_id", "actor_id", "event_type", "payload_json", "created_at")}
            expected = self._event_hash(previous,event)
            if row["previous_hash"] != previous or row["event_hash"] != expected:
                return {"valid":False,"checked_events":row["event_id"]-1,"invalid_event_id":row["event_id"]}
            previous = expected
        return {"valid":True,"checked_events":len(rows),"head_hash":previous if rows else None}

    def applied_migrations(self) -> tuple[str, ...]:
        if not self.path.exists():
            return ()
        with self.connection() as connection:
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone()
            if table is None:
                return ()
            return tuple(
                row["migration_id"]
                for row in connection.execute(
                    "SELECT migration_id FROM schema_migrations ORDER BY migration_id"
                )
            )

    def create_project(self, project_id: str, name: str, *, created_at: str | None = None) -> None:
        if not project_id.strip() or not name.strip():
            raise ValueError("project_id and name must not be empty")
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO projects(project_id, name, created_at) VALUES (?, ?, ?)",
                (project_id.strip(), name.strip(), created_at or _utc_now()),
            )
            self._append_event(connection, project_id.strip(), None, "project.created", {"project_id":project_id.strip()}, created_at or _utc_now())

    def create_run(
        self,
        run_id: str,
        project_id: str,
        payload: Mapping[str, Any],
        *,
        case_id: str | None = None,
        status: str = "created",
        created_at: str | None = None,
    ) -> None:
        if status not in RUN_STATUSES:
            raise ValueError(f"unsupported run status: {status}")
        if not run_id.strip() or not project_id.strip():
            raise ValueError("run_id and project_id must not be empty")
        payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO runs(run_id, project_id, case_id, status, payload_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id.strip(), project_id.strip(), case_id, status, payload_json, created_at or _utc_now()),
            )
            self._append_event(connection, project_id.strip(), None, "run.created", {"run_id":run_id.strip(),"case_id":case_id,"status":status}, created_at or _utc_now())

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            return None
        return {
            "run_id": row["run_id"],
            "project_id": row["project_id"],
            "case_id": row["case_id"],
            "status": row["status"],
            "payload": json.loads(row["payload_json"]),
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "created_at": row["created_at"],
        }

    def enqueue_run(
        self, run_id: str, project_id: str, payload: Mapping[str, Any], *,
        idempotency_key: str, max_attempts: int = 3, case_id: str | None = None,
    ) -> str:
        """Persist a run and queue job exactly once per idempotency key."""
        if not idempotency_key.strip() or max_attempts < 1:
            raise ValueError("idempotency key and positive max_attempts are required")
        existing = None
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT job_id FROM worker_jobs WHERE idempotency_key=?", (idempotency_key.strip(),)
            ).fetchone()
            if existing:
                return str(existing["job_id"])
            now = _utc_now()
            connection.execute(
                "INSERT INTO runs(run_id, project_id, case_id, status, payload_json, created_at) "
                "VALUES (?, ?, ?, 'queued', ?, ?)",
                (run_id, project_id, case_id, json.dumps(payload, ensure_ascii=False, sort_keys=True), now),
            )
            job_id = str(uuid.uuid4())
            connection.execute(
                "INSERT INTO worker_jobs(job_id,run_id,idempotency_key,status,max_attempts,available_at,created_at,updated_at) "
                "VALUES (?, ?, ?, 'queued', ?, ?, ?, ?)",
                (job_id, run_id, idempotency_key.strip(), max_attempts, now, now, now),
            )
            self._append_event(connection, project_id, None, "run.queued", {"run_id":run_id,"job_id":job_id,"idempotency_key":idempotency_key.strip()}, now)
            return job_id

    def claim_job(self, worker_id: str, *, lease_seconds: int = 300) -> dict[str, Any] | None:
        """Atomically claim the oldest available job; expired leases are recoverable."""
        if not worker_id.strip() or lease_seconds < 1:
            raise ValueError("worker_id and positive lease_seconds are required")
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat(timespec="seconds").replace("+00:00", "Z")
        lease = (now_dt + timedelta(seconds=lease_seconds)).isoformat(timespec="seconds").replace("+00:00", "Z")
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM worker_jobs WHERE (status='queued' AND available_at<=?) "
                "OR (status='running' AND lease_expires_at<=?) ORDER BY created_at LIMIT 1", (now, now)
            ).fetchone()
            if row is None:
                return None
            attempts = int(row["attempts"]) + 1
            if attempts > int(row["max_attempts"]):
                connection.execute("UPDATE worker_jobs SET status='failed', updated_at=?, lease_owner=NULL, lease_expires_at=NULL WHERE job_id=?", (now, row["job_id"]))
                connection.execute("UPDATE runs SET status='failed' WHERE run_id=?", (row["run_id"],))
                run = connection.execute("SELECT project_id FROM runs WHERE run_id=?", (row["run_id"],)).fetchone()
                self._append_event(connection, run["project_id"], worker_id, "run.lease_expired_final", {"run_id":row["run_id"],"job_id":row["job_id"],"attempts":row["attempts"]}, now)
                return None
            connection.execute(
                "UPDATE worker_jobs SET status='running', attempts=?, lease_owner=?, lease_expires_at=?, updated_at=? WHERE job_id=?",
                (attempts, worker_id, lease, now, row["job_id"]),
            )
            connection.execute("UPDATE runs SET status='running' WHERE run_id=?", (row["run_id"],))
            run = connection.execute("SELECT * FROM runs WHERE run_id=?", (row["run_id"],)).fetchone()
            self._append_event(connection, run["project_id"], worker_id, "run.started", {"run_id":row["run_id"],"job_id":row["job_id"],"attempt":attempts}, now)
            return {"job_id":row["job_id"],"run_id":row["run_id"],"payload":json.loads(run["payload_json"]),"attempt":attempts,"max_attempts":row["max_attempts"],"worker_id":worker_id}

    def finish_job(self, job_id: str, worker_id: str, *, success: bool, error: str | None = None) -> str:
        now = _utc_now()
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM worker_jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None or row["status"] != "running" or row["lease_owner"] != worker_id:
                raise DatabaseError("job is not leased to this worker")
            retry = not success and int(row["attempts"]) < int(row["max_attempts"])
            status = "succeeded" if success else "queued" if retry else "failed"
            delay = min(300, 2 ** max(0, int(row["attempts"]) - 1)) if retry else 0
            available_at = (datetime.now(timezone.utc) + timedelta(seconds=delay)).isoformat(timespec="seconds").replace("+00:00", "Z")
            connection.execute(
                "UPDATE worker_jobs SET status=?,available_at=?,lease_owner=NULL,lease_expires_at=NULL,last_error=?,updated_at=? WHERE job_id=?",
                (status, available_at, None if success else (error or "worker_failed")[:1000], now, job_id),
            )
            run_status = "succeeded" if success else "queued" if retry else "failed"
            connection.execute("UPDATE runs SET status=? WHERE run_id=?", (run_status, row["run_id"]))
            project_id = connection.execute("SELECT project_id FROM runs WHERE run_id=?", (row["run_id"],)).fetchone()[0]
            self._append_event(connection, project_id, worker_id, "run.succeeded" if success else "run.retry_scheduled" if retry else "run.failed", {"run_id":row["run_id"],"job_id":job_id,"error":None if success else (error or "worker_failed")[:1000]}, now)
            return status

    def cancel_job(self, job_id: str) -> bool:
        now = _utc_now()
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT run_id,status FROM worker_jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None or row["status"] not in {"queued", "running"}:
                return False
            connection.execute("UPDATE worker_jobs SET status='cancelled',lease_owner=NULL,lease_expires_at=NULL,updated_at=? WHERE job_id=?", (now, job_id))
            connection.execute("UPDATE runs SET status='cancelled' WHERE run_id=?", (row["run_id"],))
            project_id = connection.execute("SELECT project_id FROM runs WHERE run_id=?", (row["run_id"],)).fetchone()[0]
            self._append_event(connection, project_id, None, "run.cancelled", {"run_id":row["run_id"],"job_id":job_id}, now)
            return True

    def operational_snapshot(self) -> dict[str, Any]:
        """Return low-cardinality counts for readiness/metrics; no user payloads."""
        if not self.path.exists():
            return {"database": "missing", "runs": {}, "jobs": {}, "audit_events": 0}
        with self.connection() as connection:
            migrations = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
            runs = {row[0]:row[1] for row in connection.execute("SELECT status,COUNT(*) FROM runs GROUP BY status")}
            jobs = {row[0]:row[1] for row in connection.execute("SELECT status,COUNT(*) FROM worker_jobs GROUP BY status")} if "worker_jobs" in {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")} else {}
            events = connection.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        return {"database":"ok" if integrity == "ok" else "error", "migrations_applied":migrations, "runs":runs, "jobs":jobs, "audit_events":events, "audit_chain":self.verify_audit_chain()}

    def record_event(
        self,
        event_type: str,
        payload: Mapping[str, Any],
        *,
        project_id: str | None = None,
        actor_id: str | None = None,
    ) -> int:
        if not event_type.strip():
            raise ValueError("event_type must not be empty")
        with self.connection() as connection:
            return self._append_event(connection, project_id, actor_id, event_type.strip(), payload, _utc_now())

    def save_run_result(self, run_id: str, result: Mapping[str, Any]) -> None:
        with self.connection() as connection:
            cursor = connection.execute("UPDATE runs SET result_json=? WHERE run_id=?", (json.dumps(result,ensure_ascii=False,sort_keys=True),run_id))
            if cursor.rowcount != 1:
                raise DatabaseError("run not found")
            project_id = connection.execute("SELECT project_id FROM runs WHERE run_id=?", (run_id,)).fetchone()[0]
            encoded = json.dumps(result,sort_keys=True,ensure_ascii=False).encode("utf-8")
            self._append_event(connection, project_id, None, "run.result_saved", {"run_id":run_id,"result_sha256":sha256(encoded).hexdigest()}, _utc_now())

    def backup_to(self, destination: str | Path) -> Path:
        """Create an atomic-consistent SQLite snapshot; never overwrite a backup."""
        target = Path(destination)
        if target.resolve() == self.path.resolve():
            raise ValueError("backup destination must differ from database path")
        if target.exists():
            raise FileExistsError(target)
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target_connection = sqlite3.connect(target)
        try:
            source_connection = sqlite3.connect(self.path)
            try:
                source_connection.backup(target_connection)
            finally:
                source_connection.close()
            result = target_connection.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                target_connection.close()
                target.unlink(missing_ok=True)
                raise DatabaseError(f"backup integrity check failed: {result}")
        except Exception:
            target_connection.close()
            target.unlink(missing_ok=True)
            raise
        target_connection.close()
        return target

    @classmethod
    def restore_backup(
        cls,
        backup_path: str | Path,
        destination: str | Path,
        *,
        migration_directory: str | Path | None = None,
    ) -> "Database":
        """Restore to a new path after integrity/schema checks; never overwrite."""
        source_path = Path(backup_path)
        target = Path(destination)
        if source_path.resolve() == target.resolve():
            raise ValueError("restore destination must differ from backup path")
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        if target.exists():
            raise FileExistsError(target)
        source_connection = sqlite3.connect(source_path)
        try:
            integrity = source_connection.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise DatabaseError(f"backup integrity check failed: {integrity}")
            has_migrations = source_connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone()
            if has_migrations is None:
                raise DatabaseError("backup has no schema migration history")
            migrations = tuple(
                row[0]
                for row in source_connection.execute(
                    "SELECT migration_id FROM schema_migrations ORDER BY migration_id"
                )
            )
            expected = tuple(path.name for path in sorted(Path(migration_directory or MIGRATION_DIRECTORY).glob("[0-9][0-9][0-9]_*.sql")))
            if migrations != expected:
                raise DatabaseError("backup schema version does not match the current migration set")
            target.parent.mkdir(parents=True, exist_ok=True)
            target_connection = sqlite3.connect(target)
            try:
                source_connection.backup(target_connection)
            except Exception:
                target_connection.close()
                target.unlink(missing_ok=True)
                raise
            target_connection.close()
        finally:
            source_connection.close()
        restored = cls(target, migration_directory=migration_directory)
        if restored.applied_migrations() != expected:
            target.unlink(missing_ok=True)
            raise DatabaseError("restored database failed schema verification")
        return restored
