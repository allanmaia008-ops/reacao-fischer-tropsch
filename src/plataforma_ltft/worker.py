"""Worker local determinístico para uma configuração LTFT em JSON."""
import argparse
import json
from pathlib import Path

from .domain import CASE_SCHEMA_VERSION, LTFTCase, migrate_case_v1_to_v2
from .screening import run_screening
from .product_targets import plan_product_target


def execute(config_path: Path, output_dir: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    unknown = set(config) - {"case", "alpha", "desired_product"}
    if unknown:
        raise ValueError(f"Campos desconhecidos na configuração: {sorted(unknown)}")
    if "desired_product" in config and "case" not in config:
        result = {
            "schema_version": CASE_SCHEMA_VERSION,
            "status": "orientacao_por_produto",
            "ft_regime": "nao_definido",
            "regime_envelope_version": "1.0.0",
            "recommendation_blocked": True,
            "recommendation_blocking_reason": "Regime, catalisador e condições ainda não foram definidos.",
            "target_plan": plan_product_target(config["desired_product"]),
            "warning": "Orientação qualitativa e matemática ASF; não é recomendação experimental final.",
        }
    else:
        case_data = config["case"]
        if case_data.get("schema_version") == "1.0.0":
            case_data = migrate_case_v1_to_v2(case_data)
        case = LTFTCase(**case_data)
        result = run_screening(case, config["alpha"])
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "resultado_ft.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Worker da Reação Fischer–Tropsch")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(execute(args.config, args.output))


if __name__ == "__main__":
    main()
