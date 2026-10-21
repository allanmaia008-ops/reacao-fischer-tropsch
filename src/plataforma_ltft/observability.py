"""Small local JSON logging and health snapshots (FT-046).

This is process-local observability, not a remote metrics backend or alerting
service. Do not put scientific payloads, credentials, or session tokens in logs.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import logging
import os
import threading
from typing import Any

_counts: Counter[str] = Counter()
_lock = threading.Lock()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": getattr(record, "event", record.getMessage()),
        }
        for name in ("run_id", "job_id", "worker_id", "status", "duration_ms", "error_code"):
            value = getattr(record, name, None)
            if value is not None:
                payload[name] = value
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def configure_logging(level: str | None = None) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel((level or os.getenv("FT_LOG_LEVEL", "INFO")).upper())


def emit(event: str, *, level: int = logging.INFO, **fields: Any) -> None:
    with _lock:
        _counts[event] += 1
    logging.getLogger("plataforma_ltft").log(level, event, extra={"event": event, **fields})


def metrics_snapshot(database: Any | None = None) -> dict[str, Any]:
    with _lock:
        process_counts = dict(_counts)
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "process_events": process_counts,
        "database": database.operational_snapshot() if database is not None else {"status": "not_configured"},
    }
