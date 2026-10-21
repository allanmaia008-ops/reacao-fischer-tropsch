"""Run one queued simulation job from the local SQLite pilot."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from plataforma_ltft.database import Database
from plataforma_ltft.observability import configure_logging, metrics_snapshot
from plataforma_ltft.worker import run_queued_once


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("artifacts/worker"))
    parser.add_argument("--worker-id", required=True)
    args = parser.parse_args()
    configure_logging()
    database = Database(args.database)
    database.migrate()
    result = run_queued_once(database, args.output, worker_id=args.worker_id)
    print(json.dumps({"job":result,"health":metrics_snapshot(database)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
