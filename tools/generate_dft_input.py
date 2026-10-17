"""Generate an auditable FT-038 VASP input bundle from versioned contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from plataforma_ltft.dft_engine import build_vasp_input


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("structure", type=Path, help="FT-035 structure-contract JSON")
    parser.add_argument("surface", type=Path, help="FT-036 surface-protocol JSON")
    parser.add_argument("destination", type=Path, help="new output directory")
    parser.add_argument("--input-set-id", required=True)
    args = parser.parse_args()

    structure = json.loads(args.structure.read_text(encoding="utf-8"))
    surface = json.loads(args.surface.read_text(encoding="utf-8"))
    paths = build_vasp_input(
        structure, surface, input_set_id=args.input_set_id
    ).write(args.destination)
    print(json.dumps({"status": "generated", "files": [str(path) for path in paths]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
