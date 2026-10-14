"""Calcula um relatório C/H/O a partir do contrato JSON versionado."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.elemental_balance import ElementalBalanceContract, calculate_elemental_balance


def main() -> int:
    parser = argparse.ArgumentParser(description="Balanço elementar Fischer–Tropsch")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    report = calculate_elemental_balance(ElementalBalanceContract(**payload))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
