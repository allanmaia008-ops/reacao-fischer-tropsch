"""Build the prospective FT-024 external-validation campaign.

The output contains planned runs and blank observation fields.  It must never be
treated as experimental evidence until an independent laboratory executes and
signs the protocol.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "planned" / "ft024_external_campaign_100_runs.csv"
MANIFEST = ROOT / "data" / "planned" / "ft024_external_campaign_manifest.json"
SEED = 24024


def build_rows() -> list[dict[str, object]]:
    temperatures = [200 + 2.5 * index for index in range(25)]
    feeds = [(1.0, 0.333, 0.333), (1.5, 0.400, 0.267)]
    rows: list[dict[str, object]] = []
    for batch in ("EXT-A", "EXT-B"):
        for temperature in temperatures:
            for ratio, p_h2, p_co in feeds:
                rows.append({
                    "campaign_id": "FT024-EXT-001",
                    "planned_run_id": f"FT024-EXT-{len(rows)+1:03d}",
                    "independent_catalyst_batch": batch,
                    "randomization_order": 0,
                    "catalyst_id": "Mansouri2013_CoCe_SiO2",
                    "catalyst_nominal_composition": "80%Co/20%Ce/15wt%SiO2",
                    "preparation_method": "coprecipitation; independent reproduction required",
                    "temperature_c": temperature,
                    "pressure_bar": 1.0,
                    "h2_co_ratio": ratio,
                    "p_h2_bar": p_h2,
                    "p_co_bar": p_co,
                    "ghsv_h_1": 3950,
                    "catalyst_mass_g": 1.0,
                    "steady_state_h": 12,
                    "observed_co_conversion_pct": "",
                    "observed_rate_mmol_gcat_min": "",
                    "measurement_standard_uncertainty": "",
                    "raw_data_uri": "",
                    "raw_data_sha256": "",
                    "operator_id": "",
                    "execution_date": "",
                    "independent_reviewer": "",
                    "execution_confirmed": False,
                    "validation_eligible": False,
                    "exclusion_reason": "not_executed",
                })
    rng = random.Random(SEED)
    order = list(range(1, len(rows) + 1))
    rng.shuffle(order)
    for row, randomized in zip(rows, order):
        row["randomization_order"] = randomized
    return sorted(rows, key=lambda row: int(row["randomization_order"]))


def main() -> None:
    rows = build_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    manifest = {
        "campaign_id": "FT024-EXT-001",
        "status": "planned_not_executed",
        "planned_runs": len(rows),
        "unique_conditions": 50,
        "independent_catalyst_batches": 2,
        "randomization_seed": SEED,
        "source_model_doi": "10.1186/2228-5547-4-1",
        "observed_measurements": 0,
        "external_validation_complete": False,
        "recommendation_blocked": True,
        "sha256": digest,
        "required_release_conditions": [
            "independent laboratory executes the campaign",
            "raw chromatograms and calibration records are retained",
            "transport and thermal criteria pass",
            "at least 20 compatible unique conditions remain after exclusions",
            "pre-registered MAE, MSE, residual and uncertainty criteria pass",
            "independent reviewer signs the validation report",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
