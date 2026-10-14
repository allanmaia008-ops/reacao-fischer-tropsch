"""Exportação reproduzível e relatório científico para resultados FT."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any, Mapping, Sequence

EXPORT_CONTRACT_VERSION = "1.0.0"
SCIENTIFIC_REPORT_VERSION = "1.0.0"


def _canonical_json_bytes(data: Any) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _require_result(result: Mapping[str, Any]) -> None:
    required = {
        "schema_version", "status", "case", "alpha", "ft_regime", "product_bands",
        "target_fraction", "readiness", "recommendation_blocked",
        "recommendation_blocking_reason", "warning",
    }
    missing = sorted(required - set(result))
    if missing:
        raise ValueError("Resultado incompleto para exportação: " + ", ".join(missing) + ".")
    if result.get("recommendation_blocked") is not True:
        raise ValueError("A exportação científica exige recommendation_blocked=true nesta versão.")


def _csv_bytes(fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def build_export_artifacts(result: Mapping[str, Any]) -> dict[str, bytes]:
    """Gera artefatos determinísticos; mesmos dados produzem os mesmos bytes."""
    _require_result(result)
    result_payload = {
        "export_contract_version": EXPORT_CONTRACT_VERSION,
        "result": result,
    }
    result_json = _canonical_json_bytes(result_payload)
    result_sha = _sha256(_canonical_json_bytes(result))
    bands = result["product_bands"]
    summary_rows = [{
        "export_contract_version": EXPORT_CONTRACT_VERSION,
        "result_schema_version": result["schema_version"],
        "result_sha256": result_sha,
        "status": result["status"],
        "ft_regime": result["ft_regime"],
        "desired_product": result["case"]["desired_product"],
        "alpha": result["alpha"],
        "target_fraction": result["target_fraction"],
        "recommendation_blocked": str(result["recommendation_blocked"]).lower(),
    }]
    summary_csv = _csv_bytes(tuple(summary_rows[0]), summary_rows)
    band_rows = [
        {
            "export_contract_version": EXPORT_CONTRACT_VERSION,
            "result_sha256": result_sha,
            "product_band": band,
            "carbon_fraction": fraction,
        }
        for band, fraction in bands.items()
    ]
    bands_csv = _csv_bytes(tuple(band_rows[0]), band_rows)
    artifacts = {
        "resultado_ft_v1.json": result_json,
        "resumo_ft_v1.csv": summary_csv,
        "faixas_asf_v1.csv": bands_csv,
    }
    manifest = {
        "export_contract_version": EXPORT_CONTRACT_VERSION,
        "result_schema_version": result["schema_version"],
        "result_sha256": result_sha,
        "deterministic_export": True,
        "files": [
            {"name": name, "media_type": "application/json" if name.endswith(".json") else "text/csv", "sha256": _sha256(content), "bytes": len(content)}
            for name, content in artifacts.items()
        ],
    }
    artifacts["manifesto_exportacao_v1.json"] = _canonical_json_bytes(manifest)
    return artifacts


def generate_scientific_report(result: Mapping[str, Any], source_ids: Sequence[str] = ()) -> str:
    """Gera relatório Markdown auditável sem promover o resultado a evidência."""
    _require_result(result)
    canonical_result = _canonical_json_bytes(result)
    fingerprint = _sha256(canonical_result)
    case = result["case"]
    readiness = result["readiness"]
    sources = "\n".join(f"- `{source}`" for source in source_ids) if source_ids else "- Nenhuma fonte experimental aprovada anexada a este resultado."
    bands = "\n".join(f"- {name}: {100 * value:.4f}%" for name, value in result["product_bands"].items())
    missing_experimental = ", ".join(readiness.get("missing_experimental_fields", ())) or "nenhum"
    missing_rate = ", ".join(readiness.get("missing_rate_fields", ())) or "nenhum"
    return f"""# Relatório científico Fischer–Tropsch

**Versão do relatório:** {SCIENTIFIC_REPORT_VERSION}  
**Versão do resultado:** {result['schema_version']}  
**Identificador SHA-256 do resultado:** `{fingerprint}`

## Objetivo e escopo

Documentar uma triagem ASF condicionada às entradas declaradas. Este relatório não constitui recomendação experimental, validação cinética ou confirmação de desempenho do catalisador.

## Premissas declaradas

- Regime FT: {result['ft_regime']}
- Produto-alvo: {case['desired_product']}
- Temperatura: {case['temperature_c']} °C
- Pressão absoluta: {case['pressure_bar']} bar
- Razão molar H2/CO: {case['h2_co_molar_ratio']}
- Catalisador declarado: {case['active_family']} / {case['support']}
- Probabilidade de crescimento α: {result['alpha']} ({result.get('alpha_origin', 'origem não declarada')})
- Base de produto: {result.get('product_basis', 'não declarada')}

## Resultados matemáticos

- Fração de carbono no alvo: {100 * result['target_fraction']:.4f}%
{bands}
- Conversão de CO: {result.get('CO_conversion_pct') if result.get('CO_conversion_pct') is not None else 'não calculada'}
- Produtividade física: {result.get('physical_productivity') if result.get('physical_productivity') is not None else 'não calculada'}

## Evidências e rastreabilidade

{sources}

O resultado é uma saída matemática condicionada a α. Ausência de fonte experimental não foi convertida em evidência, zero ou confirmação.

## Prontidão e dados ausentes

- Triagem ASF: {'disponível' if readiness.get('valid_for_screening') else 'bloqueada'}
- Plano experimental: {'disponível' if readiness.get('valid_for_experimental_plan') else 'bloqueado'}
- Cálculo de taxa: {'disponível' if readiness.get('valid_for_rate_calculation') else 'bloqueado'}
- Campos experimentais ausentes: {missing_experimental}
- Campos cinéticos ausentes: {missing_rate}

## Limitações e bloqueios

- Recomendação bloqueada: **sim**
- Motivo: {result['recommendation_blocking_reason']}
- Advertência do modelo: {result['warning']}
- As faixas ASF não representam automaticamente pureza, separação ou rendimento comercial.
- Temperatura e pressão não determinam conversão ou α sem modelo calibrado e evidência adequada.
- A revisão humana permanece obrigatória antes de uso experimental.
"""
