"""Valida os JSON Schemas e seus exemplos versionados para uso na CI."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

EXAMPLE_CASES = (
    ("ltft-case-v1.schema.json", "caso_co.json", "case", True),
    ("ltft-case-v1.schema.json", "caso_experimental_completo.json", "case", True),
    ("ft-case-v2.schema.json", "caso_htft_v2.json", "case", True),
    ("ft-case-v2.schema.json", "caso_transicao_v2.json", "case", True),
    ("ft-catalyst-v1.schema.json", "catalisador_co_v1.json", None, True),
    ("ft-catalyst-v1.schema.json", "catalisador_fe_v1.json", None, True),
    ("ft-catalyst-v1.schema.json", "catalisador_co_fe_exploratorio_v1.json", None, True),
    ("ft-elemental-balance-v1.schema.json", "balanco_elementar_demonstracao.json", None, True),
    ("ft-asf-measurement-v1.schema.json", "comparacao_asf_medicao_sintetica.json", None, True),
    ("ft-advanced-asf-v1.schema.json", "asf_avancada_dual_sintetica.json", None, True),
    ("ft-experimental-protocol-v2.schema.json", "protocolo_experimental_v2_template.json", None, True),
    ("ft-experimental-protocol-v2.schema.json", "protocolo_experimental_v2_sintetico_completo.json", None, True),
    ("ft-transport-diagnostics-v1.schema.json", "diagnostico_transporte_sintetico.json", None, True),
    ("ft-export-manifest-v1.schema.json", "manifesto_exportacao_sintetico.json", None, True),
    ("htft-case-v1.schema.json", "htft_light_olefins_v1.json", None, True),
    ("htft-case-v1.schema.json", "htft_invalid_cobalt_v1.json", None, False),
    ("ft-htft-balance-v1.schema.json", "htft_balance_closed_v1.json", None, True),
)


@dataclass(frozen=True)
class SchemaValidationReport:
    schema_count: int
    example_count: int
    issues: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: JSON ilegível: {exc}") from exc


def validate_repository(root: Path = ROOT) -> SchemaValidationReport:
    schemas_dir = root / "schemas"
    examples_dir = root / "examples"
    schema_paths = sorted(schemas_dir.glob("*.schema.json"))
    issues: list[str] = []
    schemas: dict[str, dict[str, Any]] = {}
    schema_ids: dict[str, str] = {}

    for path in schema_paths:
        try:
            schema = _load_json(path)
            Draft202012Validator.check_schema(schema)
            schema_id = schema.get("$id")
            if not isinstance(schema_id, str) or not schema_id:
                issues.append(f"{path.name}: $id obrigatório.")
            elif schema_id in schema_ids:
                issues.append(f"{path.name}: $id duplicado com {schema_ids[schema_id]}.")
            else:
                schema_ids[schema_id] = path.name
            schemas[path.name] = schema
        except Exception as exc:  # jsonschema detalha a falha estrutural
            issues.append(f"{path.name}: {exc}")

    for schema_name, example_name, member, should_be_valid in EXAMPLE_CASES:
        schema = schemas.get(schema_name)
        if schema is None:
            issues.append(f"{example_name}: schema ausente: {schema_name}.")
            continue
        try:
            document = _load_json(examples_dir / example_name)
            instance = document[member] if member else document
            errors = sorted(
                Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
                key=lambda error: list(error.absolute_path),
            )
            if should_be_valid and errors:
                details = "; ".join(error.message for error in errors[:3])
                issues.append(f"{example_name}: deveria ser válido: {details}")
            if not should_be_valid and not errors:
                issues.append(f"{example_name}: exemplo estruturalmente negativo deixou de falhar.")
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(f"{example_name}: {exc}")

    return SchemaValidationReport(len(schema_paths), len(EXAMPLE_CASES), tuple(issues))


def main() -> int:
    report = validate_repository()
    if report.valid:
        print(f"OK: {report.schema_count} schemas e {report.example_count} exemplos verificados.")
        return 0
    print("Falha na validação de schemas:")
    for issue in report.issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
