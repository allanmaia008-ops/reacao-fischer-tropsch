import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_campaign_is_complete_but_not_falsely_executed():
    path = ROOT / "data" / "planned" / "ft024_external_campaign_100_runs.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 100
    assert len({(r["temperature_c"], r["h2_co_ratio"]) for r in rows}) == 50
    assert {r["independent_catalyst_batch"] for r in rows} == {"EXT-A", "EXT-B"}
    assert sorted(int(r["randomization_order"]) for r in rows) == list(range(1, 101))
    assert all(r["observed_rate_mmol_gcat_min"] == "" for r in rows)
    assert all(r["execution_confirmed"] == "False" for r in rows)
    assert all(r["validation_eligible"] == "False" for r in rows)


def test_manifest_preserves_scientific_gate():
    manifest = json.loads((ROOT / "data" / "planned" / "ft024_external_campaign_manifest.json").read_text(encoding="utf-8"))
    assert manifest["planned_runs"] == 100
    assert manifest["observed_measurements"] == 0
    assert manifest["external_validation_complete"] is False
    assert manifest["recommendation_blocked"] is True
