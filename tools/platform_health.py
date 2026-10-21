"""Print local platform health and low-cardinality counters as JSON."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from plataforma_ltft.database import Database
from plataforma_ltft.observability import metrics_snapshot


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database",type=Path)
    args=parser.parse_args()
    database=Database(args.database) if args.database else None
    print(json.dumps(metrics_snapshot(database),ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
