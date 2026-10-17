"""Generate the frozen HTFT model and external-holdout evaluation artifacts."""
import json
from pathlib import Path

from plataforma_ltft.htft_quantitative import evaluate_external_holdout, freeze_persistence_model, load_dataset

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/htft/htft_ahmed_2021_temperature_holdout.csv"
OUTPUT = ROOT / "data/htft/validation"


def main() -> int:
    rows = load_dataset(DATA)
    model = freeze_persistence_model(rows)
    report = evaluate_external_holdout(rows, model)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "htft_model_frozen_v1.json").write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUTPUT / "htft_external_validation_v1.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"model": model["model_id"], "passed": report["quantitative_validation_passed"], "output": str(OUTPUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
