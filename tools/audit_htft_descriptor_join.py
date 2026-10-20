"""Generate an auditable, source-scoped HTFT catalyst-descriptor join."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plataforma_ltft.htft_descriptor_join import join_source_descriptors  # noqa: E402


def main() -> None:
    data = ROOT / "data" / "htft"
    result = join_source_descriptors(
        data / "htft_catalyst_descriptors_v1.csv",
        [data / "htft_liu_fuel_2021_temperature_series.csv",
         data / "htft_xie_2016_temporal_holdout.csv"],
    )
    output_dir = data / "validation"
    (output_dir / "htft_descriptor_source_join_audit_v1.json").write_text(
        json.dumps(result["audit"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = result["rows"]
    fieldnames = list(dict.fromkeys(field for row in rows for field in row))
    with (data / "htft_descriptors_joined_source_rows_v1.csv").open(
        "w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(result["audit"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
