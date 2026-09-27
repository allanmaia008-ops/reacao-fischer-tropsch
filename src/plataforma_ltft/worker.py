"""Worker local determinístico para uma configuração LTFT em JSON."""
import argparse
import json
from pathlib import Path

from .domain import LTFTCase
from .screening import run_screening
from .product_targets import plan_product_target


def execute(config_path: Path, output_dir: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    unknown = set(config) - {"case", "alpha", "desired_product"}
    if unknown:
        raise ValueError(f"Campos desconhecidos na configuração: {sorted(unknown)}")
    if "desired_product" in config and "case" not in config:
        result = {
            "schema_version": "1.0.0",
            "status": "orientacao_por_produto",
            "target_plan": plan_product_target(config["desired_product"]),
            "warning": "Orientação qualitativa e matemática ASF; não é recomendação experimental final.",
        }
    else:
        case = LTFTCase(**config["case"])
        result = run_screening(case, config["alpha"])
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "resultado_ltft.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Worker da Plataforma LTFT")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(execute(args.config, args.output))


if __name__ == "__main__":
    main()
