"""Exporta um resultado FT existente como JSON/CSV e manifesto versionado."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.reporting import build_export_artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, content in build_export_artifacts(result).items():
        args.output.joinpath(name).write_bytes(content)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
