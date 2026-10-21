"""Build a JSON and Markdown DFT audit report from declared inputs and parser output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jsonschema import Draft202012Validator
from plataforma_ltft.dft_reporting import build_dft_report, write_dft_report


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parsed_result", type=Path)
    parser.add_argument("structure_contract", type=Path)
    parser.add_argument("surface_protocol", type=Path)
    parser.add_argument("input_manifest", type=Path)
    parser.add_argument("--report-id", required=True)
    parser.add_argument("--source-citation", required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()
    targets = (args.output_prefix.with_suffix(".json"), args.output_prefix.with_suffix(".md"))
    if any(path.exists() for path in targets):
        parser.error("refusing to overwrite existing report files")
    report = build_dft_report(
        load_json(args.parsed_result),
        report_id=args.report_id,
        structure_contract=load_json(args.structure_contract),
        surface_protocol=load_json(args.surface_protocol),
        input_manifest=load_json(args.input_manifest),
        source_citation=args.source_citation,
    )
    schema = load_json(ROOT / "schemas/ft-dft-report-v1.schema.json")
    errors = list(Draft202012Validator(schema).iter_errors(report))
    if errors:
        for error in errors:
            print(f"schema error: {error.message}", file=sys.stderr)
        return 2
    written = write_dft_report(report, args.output_prefix)
    print("\n".join(str(path) for path in written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
