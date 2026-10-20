"""Audit a newly transcribed HTFT paper before any model promotion."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.htft_external_validation import (  # noqa: E402
    TARGETS, V41_FIELDS, evaluate_leave_one_publication_out, evaluate_v41_grouped,
    load_rows,
)

BASE = ROOT / "data/htft/htft_external_diverse_catalysts_v1.csv"
ND = ROOT / "data/htft/htft_femn_new_primary_tables_2026.csv"
SOURCE = ROOT / "data/htft/htft_falkenhagen_2018_primary_tables.json"
OUT = ROOT / "data/htft/validation/htft_falkenhagen_2018_impact.json"


def load_new_rows(path: Path = SOURCE) -> list[dict[str, str]]:
    source = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for original in source["rows"]:
        row = dict(original)
        if not all(row.get(field, "").strip() for field in V41_FIELDS):
            raise ValueError(f"incomplete coordinates: {row['row_id']}")
        parts = [float(row[f"c{n}_olefins_hc_carbon_pct"]) for n in (2, 3, 4)]
        row["c2_c4_olefins_hc_carbon_pct"] = str(round(sum(parts), 1))
        for target in TARGETS:
            if not 0 <= float(row[target]) <= 100:
                raise ValueError(f"invalid {target}: {row['row_id']}")
        row["source_doi"] = source["source_doi"]
        row["source_group_id"] = source["source_group_id"]
        row["source_table"] = source["source_tables"]
        rows.append(row)
    if len(rows) != 9 or len({row["row_id"] for row in rows}) != len(rows):
        raise ValueError("expected nine unique primary-table rows")
    return rows


def metrics_for(residuals: list[dict[str, object]]) -> dict[str, object]:
    return {
        target: {
            "n": len(errors := [abs(float(row["residual_predicted_minus_observed"]))
                                 for row in residuals if row["target"] == target]),
            "mae": sum(errors) / len(errors) if errors else None,
            "criterion_mae": limit,
            "passed": bool(errors) and sum(errors) / len(errors) <= limit,
        }
        for target, limit in TARGETS.items()
    }


def assess() -> dict[str, object]:
    old = load_rows(BASE) + load_rows(ND)
    old = [row for row in old if all(row.get(field, "").strip() for field in V41_FIELDS)]
    new = load_new_rows()
    if {row["row_id"] for row in old} & {row["row_id"] for row in new}:
        raise ValueError("duplicate row ID across source files")
    old_dois = {row["source_doi"] for row in old}
    baseline = evaluate_leave_one_publication_out(old)
    expanded = evaluate_leave_one_publication_out(old + new)
    old_holdouts = [row for row in expanded["residuals"]
                    if row["held_out_publication"] in old_dois]
    new_holdout = [row for row in expanded["residuals"]
                   if row["held_out_publication"] not in old_dois]
    guarded = evaluate_v41_grouped(old + new)
    families_by_source = {}
    for row in old + new:
        families_by_source.setdefault(row["family"], set()).add(
            row.get("source_group_id", "").strip() or row["source_doi"]
        )
    return {
        "schema_version": "1.0.0",
        "design": "retrospective complete-case leave-one-publication-out; no hyperparameter tuning",
        "old_complete_rows": len(old), "new_complete_rows": len(new),
        "source_doi": new[0]["source_doi"],
        "old_holdout_metrics_before": metrics_for(baseline["residuals"]),
        "old_holdout_metrics_after": metrics_for(old_holdouts),
        "new_publication_holdout_metrics": metrics_for(new_holdout),
        "repeated_families_across_source_groups": sorted(
            family for family, groups in families_by_source.items() if len(groups) >= 2
        ),
        "guarded_eligible_target_rows": guarded["eligible_target_rows"],
        "guarded_predicted_target_rows": guarded["predicted_target_rows"],
        "guarded_coverage": guarded["coverage"],
        "model_promoted": False,
        "recommendation_blocked": True,
    }


def main() -> None:
    result = assess()
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
