"""Parse a VASP OUTCAR into an auditable, schema-checked JSON result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jsonschema import Draft202012Validator
from plataforma_ltft.dft_parser import parse_vasp_outcar_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outcar", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force-threshold", type=float)
    parser.add_argument("--expected-atom-count", type=int)
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    result = parse_vasp_outcar_file(
        args.outcar,
        force_threshold_ev_angstrom=args.force_threshold,
        expected_atom_count=args.expected_atom_count,
        synthetic=args.synthetic,
    )
    schema = json.loads((ROOT / "schemas/ft-dft-parsed-result-v1.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(result))
    if errors:
        for error in errors:
            print(f"schema error: {error.message}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{result['status']}: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
