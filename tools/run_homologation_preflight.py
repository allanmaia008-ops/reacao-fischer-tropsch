"""Run reproducible technical smoke checks; does not certify scientific readiness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from plataforma_ltft.homologation import build_preflight_report


def run(command: list[str]) -> dict[str, object]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    return {"command":command,"returncode":result.returncode,"passed":result.returncode == 0,
            "stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON report path; refuses to overwrite")
    args = parser.parse_args()
    checks = [
        run([sys.executable,"-m","unittest","tests.test_database","tests.test_auth","tests.test_worker","tests.test_worker_queue","tests.test_observability","tests.test_homologation"]),
        run([sys.executable,"tools/validate_schemas.py"]),
    ]
    report = build_preflight_report(checks)
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open("x",encoding="utf-8") as stream:
            stream.write(rendered)
    print(rendered)
    if not all(c["passed"] for c in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
