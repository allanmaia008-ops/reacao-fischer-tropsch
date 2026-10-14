"""Migra um caso FT atual para o template experimental v2 sem inventar campos."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.domain import LTFTCase, migrate_case_v1_to_v2
from plataforma_ltft.experimental_protocol import migrate_case_to_experimental_protocol_v2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--protocol-id", required=True)
    parser.add_argument("--source-id", required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    case_payload = payload.get("case", payload)
    if case_payload.get("schema_version") == "1.0.0":
        case_payload = migrate_case_v1_to_v2(case_payload)
    protocol = migrate_case_to_experimental_protocol_v2(
        LTFTCase(**case_payload), args.protocol_id, (args.source_id,)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(asdict(protocol), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
