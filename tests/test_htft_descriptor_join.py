import csv
import tempfile
from pathlib import Path

from plataforma_ltft.htft_descriptor_join import join_source_descriptors


def _write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_descriptors_join_only_to_matching_study_catalyst_and_doi():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        descriptor = temp / "descriptors.csv"
        source = temp / "source.csv"
        _write_csv(descriptor, [{"dataset_id": "study-a", "catalyst": "3Fe", "source": "10.1234/ABC",
                                 "fe_wt_pct": "2", "k2o_wt_pct": "", "na_wt_pct": "0.03",
                                 "s_wt_pct": "0.005", "particle_size_nm": "3"}])
        _write_csv(source, [{"dataset_id": "study-a", "row_id": "row-1", "catalyst": "3Fe",
                             "source_doi": "https://doi.org/10.1234/abc", "temperature_c": "340"},
                            {"dataset_id": "study-a", "row_id": "row-2", "catalyst": "3Fe",
                             "source_doi": "10.1234/abc", "temperature_c": "350"}])
        result = join_source_descriptors(descriptor, [source])
    audit = result["audit"]
    assert audit["descriptor_records"] == 1
    assert audit["descriptor_records_matched"] == 1
    assert audit["descriptor_records_unmatched"] == 0
    assert audit["source_rows_with_descriptors"] == 2
    assert audit["row_join_coverage"] == 1
    assert all(row["descriptor_join_status"] == "exact_dataset_catalyst_doi" for row in result["rows"])


def test_no_cross_study_or_doi_fuzzy_match_is_created():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        descriptor = temp / "descriptors.csv"
        source = temp / "source.csv"
        _write_csv(descriptor, [{"dataset_id": "study-a", "catalyst": "3Fe", "source": "10.1234/abc",
                                 "fe_wt_pct": "2"}])
        _write_csv(source, [{"dataset_id": "study-b", "row_id": "row-1", "catalyst": "3Fe",
                             "source_doi": "10.1234/abc"}])
        result = join_source_descriptors(descriptor, [source])
    assert result["audit"]["source_rows_with_descriptors"] == 0
    assert all(row["descriptor_join_status"] == "unmatched" for row in result["rows"])
