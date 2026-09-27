"""Gera o relatório JSON de auditoria dos CSVs LTFT."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.domain import LTFTCase
from plataforma_ltft.evidence_validation import write_audit_report


parser = argparse.ArgumentParser(description="Audita a evidência CSV da Reação Fischer–Tropsch")
parser.add_argument("--evidence", type=Path, default=ROOT / "data" / "evidence")
parser.add_argument("--case", type=Path)
parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "evidence_audit.json")
args = parser.parse_args()
case = None
if args.case:
    payload = json.loads(args.case.read_text(encoding="utf-8"))
    case = LTFTCase(**payload["case"])
print(write_audit_report(args.evidence, args.output, case))
