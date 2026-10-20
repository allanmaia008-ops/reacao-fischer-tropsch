"""Provenance-safe join of HTFT catalyst descriptors to their own source rows."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


DESCRIPTOR_FIELDS = (
    "fe_wt_pct", "k2o_wt_pct", "na_wt_pct", "s_wt_pct", "particle_size_nm",
    "al2o3_to_znal2o4_molar_ratio", "support_alumina_only", "promoted",
)


def _key(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").strip().lower())


def _doi(value: str | None) -> str:
    return (value or "").strip().lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def join_source_descriptors(
    descriptor_path: str | Path,
    source_paths: list[str | Path],
) -> dict[str, Any]:
    """Join only exact dataset/catalyst/DOI identities; never infer aliases.

    Returns augmented source rows and an audit. Rows from other studies remain
    unmatched and receive no imputed catalyst descriptors.
    """
    descriptor_rows = _read_csv(Path(descriptor_path))
    source_rows = [row for path in source_paths for row in _read_csv(Path(path))]

    index: dict[tuple[str, str, str], dict[str, str]] = {}
    duplicate_keys: list[tuple[str, str, str]] = []
    for descriptor in descriptor_rows:
        key = (_key(descriptor.get("dataset_id")), _key(descriptor.get("catalyst")),
               _doi(descriptor.get("source")))
        if key in index:
            duplicate_keys.append(key)
        else:
            index[key] = descriptor

    augmented: list[dict[str, Any]] = []
    matched_descriptor_keys: set[tuple[str, str, str]] = set()
    matched_rows = 0
    for source in source_rows:
        key = (_key(source.get("dataset_id")), _key(source.get("catalyst")),
               _doi(source.get("source_doi")))
        descriptor = index.get(key)
        item: dict[str, Any] = dict(source)
        for field in DESCRIPTOR_FIELDS:
            item[field] = descriptor.get(field, "") if descriptor else ""
        item["descriptor_join_status"] = "exact_dataset_catalyst_doi" if descriptor else "unmatched"
        augmented.append(item)
        if descriptor:
            matched_rows += 1
            matched_descriptor_keys.add(key)

    matched_descriptors = len(matched_descriptor_keys)
    return {
        "rows": augmented,
        "audit": {
            "join_keys": ["dataset_id", "catalyst", "source_doi"],
            "descriptor_records": len(descriptor_rows),
            "descriptor_records_matched": matched_descriptors,
            "descriptor_records_unmatched": len(index) - matched_descriptors,
            "source_rows": len(source_rows),
            "source_rows_with_descriptors": matched_rows,
            "row_join_coverage": matched_rows / len(source_rows) if source_rows else 0.0,
            "duplicate_descriptor_keys": [list(key) for key in duplicate_keys],
            "status": "exact_source_scoped_join" if matched_rows else "no_exact_join",
            "scope_warning": "Joined only to the Liu/Xie source tables supplied; this does not imply coverage in the v14 multicatalyst cohort.",
        },
    }
