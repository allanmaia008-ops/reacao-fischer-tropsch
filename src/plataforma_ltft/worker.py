"""Worker local determinístico para uma configuração LTFT em JSON."""
import argparse
import json
import logging
from pathlib import Path
from time import perf_counter
from hashlib import sha256

from .domain import CASE_SCHEMA_VERSION, LTFTCase, migrate_case_v1_to_v2
from .screening import run_screening
from .product_targets import plan_product_target
from .database import Database
from .observability import emit


def execute_config(config: dict, output_dir: Path) -> Path:
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


def execute(config_path: Path, output_dir: Path) -> Path:
    return execute_config(json.loads(config_path.read_text(encoding="utf-8")), output_dir)


def run_queued_once(database: Database, output_root: Path, *, worker_id: str, lease_seconds: int = 300) -> dict | None:
    """Claim one persisted job, execute once, store result, and schedule bounded retry on error."""
    job = database.claim_job(worker_id, lease_seconds=lease_seconds)
    if job is None:
        return None
    start = perf_counter()
    emit("worker.job_started", job_id=job["job_id"], run_id=job["run_id"], worker_id=worker_id)
    try:
        run_dir = output_root / sha256(job["run_id"].encode("utf-8")).hexdigest()[:20]
        output_path = execute_config(job["payload"], run_dir)
        result = json.loads(output_path.read_text(encoding="utf-8"))
        database.save_run_result(job["run_id"], result)
        status = database.finish_job(job["job_id"], worker_id, success=True)
        emit("worker.job_finished", job_id=job["job_id"], run_id=job["run_id"], worker_id=worker_id,
             status=status, duration_ms=round((perf_counter()-start)*1000))
        return {"job_id":job["job_id"],"run_id":job["run_id"],"status":status,"result":result,"artifact":str(output_path)}
    except Exception as exc:
        status = database.finish_job(job["job_id"], worker_id, success=False, error=type(exc).__name__)
        emit("worker.job_failed", level=logging.ERROR, job_id=job["job_id"], run_id=job["run_id"],
             worker_id=worker_id, status=status, error_code=type(exc).__name__,
             duration_ms=round((perf_counter()-start)*1000))
        return {"job_id":job["job_id"],"run_id":job["run_id"],"status":status,"error_code":type(exc).__name__}


def main() -> None:
    parser = argparse.ArgumentParser(description="Worker da Reação Fischer–Tropsch")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(execute(args.config, args.output))


if __name__ == "__main__":
    main()
