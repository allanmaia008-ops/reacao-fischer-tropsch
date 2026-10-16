"""Build the source-faithful, long-form FT-024 experimental measurement database."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANSOURI = ROOT / "data/evidence/ltft_mansouri_2013_kinetics.csv"
OUTPUT = ROOT / "data/evidence/ft024_cobalt_cerium_measurements.csv"
MANIFEST = ROOT / "data/evidence/ft024_cobalt_cerium_measurements.manifest.json"

RSC_DOI = "10.1039/C7RA05490D"
RSC_SOURCE = "https://www.rsc.org/suppdata/c7/ra/c7ra05490d/c7ra05490d1.pdf"
RSC_COLUMNS = ("conversion_co_pct", "conversion_h2_pct", "selectivity_ch4_pct", "selectivity_c2h6_pct",
               "selectivity_c2h4_pct", "selectivity_c3h8_pct", "selectivity_c3h6_pct",
               "selectivity_c4h8_pct", "selectivity_c4h10_pct", "selectivity_c5plus_pct", "selectivity_co2_pct")
RSC_DATA = {
"1:1:1": [[270,78,89.2,62.4,4.24,0,6.9,20.11,0,5.7,0,0],[300,26.4,44.3,30.1,4.75,.06,6.75,17.1,5.17,4.29,0,1.21],[330,34.3,58.5,47.6,8.34,1.67,6.54,17.6,3.54,2.9,5.19,2.33],[350,39,66.4,51.9,10.6,4.76,6.48,15.4,2.83,2.62,1.3,2.64],[380,43,71,54.8,11.2,5.99,5.39,14.1,1.14,1.74,1.2,2.86],[400,49.5,75.5,56.5,11.4,5.02,3.5,10.7,.69,1.45,.99,4.62]],
"1:0.5:1": [[270,76,81,60.1,5.3,0,0,21.39,3.98,0,9.23,0],[300,29,49.81,54.1,7.11,.62,0,19.57,5.63,0,3.62,1.2],[330,35,59.2,62.2,7.53,1.03,0,20.1,5.15,0,2.29,1.6],[350,39.2,63.8,62.8,8.48,1.34,1.48,15.5,4.68,.51,2,1.81],[380,47.9,72.6,63.2,8.87,7.16,1,14.76,1.47,.2,1.2,2.1],[400,69.7,87.1,70.4,9.49,6.86,.68,5.13,.05,0,1.05,5.6]],
"1:0.25:1": [[270,81,87.1,72.4,0,0,0,0,0,0,0,0],[300,33.4,50.2,50.6,5.62,.64,0,15.24,0,0,0,.03],[330,35.7,54.8,58.5,7.8,1.07,0,15.14,2.96,0,.021,1.35],[350,42.6,63.7,59.2,9.67,7.36,3.9,15.3,2.68,0,.08,1.52],[380,45,68.3,60.3,10.5,7.1,2.2,12.42,1.23,0,.97,2.23],[400,50.2,74.9,61.5,11.37,8.43,1.13,11.48,.06,0,1.69,3.87]],
"1:1:0.5": [[270,78.9,87.1,73,9.27,0,0,0,0,0,7.63,0],[300,26.4,38.9,44.8,10.68,0,13.04,13,3.52,0,8.8,0],[330,30.6,46.1,47.6,11,.04,6.06,19.57,4.52,3.23,5.6,1.98],[350,41.6,56.7,49.8,12.79,4.64,5.5,11.98,1.9,2.17,2.29,3.2],[380,47.3,62.8,56.7,12.95,2.98,4.93,8.17,1.25,.51,1.61,6.72],[400,60.2,73.5,68.9,13.12,1.76,2.99,1.85,.74,0,.89,9.1]],
"1:1:0.25": [[270,72.7,74.7,46.3,10.13,0,19.79,9.29,0,8.97,5.16,0],[300,41.63,49.2,40.8,12.54,6.6,4.54,19.97,7.21,2.74,4.89,.47],[330,49.3,54.8,47.3,12.76,4.28,4.7,15.79,4.05,2.78,4.2,3.74],[350,54,65.1,50.1,13.2,4.49,4.95,13.43,2.23,1.12,3.62,6.69],[380,58.2,69.6,57.7,13.86,1.61,4.52,8.92,1.02,.78,2.19,8.3],[400,66.3,72.9,65.41,14.13,1.35,4.65,4.45,.709,0,.02,9.1]]}

FIELDS = ("measurement_id","run_id","dataset_id","catalyst_id","catalyst_composition","support","preparation_method","temperature_c","pressure_bar","h2_co_ratio","ghsv_h_inv","response_name","response_value","response_unit","measurement_uncertainty","source_doi","source_locator","source_url","evidence_type","compatibility_class","external_validation_eligible","exclusion_reason")


def build_rows():
    rows=[]
    with MANSOURI.open(encoding="utf-8-sig", newline="") as stream:
        for source in csv.DictReader(stream):
            run=f"mansouri2013-{int(source['row_id']):03d}"
            for response, unit in (("conversion_co_pct","pct"),("rate_co_consumption","mmol_CO_gcat_min")):
                value=source["conversion_co_pct"] if response=="conversion_co_pct" else source["rate_mmol_gcat_min"]
                rows.append(dict(measurement_id=f"{run}-{response}",run_id=run,dataset_id="mansouri2013_table1",catalyst_id=source["catalyst_id"],catalyst_composition="80%Co/20%Ce/15wt%SiO2",support="SiO2",preparation_method="co-precipitation",temperature_c=source["temperature_c"],pressure_bar=1,h2_co_ratio=round(float(source["p_h2_bar"])/float(source["p_co_bar"]),6),ghsv_h_inv="2700-5200",response_name=response,response_value=value,response_unit=unit,measurement_uncertainty="not_reported",source_doi=source["source_doi"],source_locator="Table 1",source_url=source["source_url"],evidence_type="published_experiment",compatibility_class="strict_same_catalyst_same_study",external_validation_eligible=False,exclusion_reason="same_study_as_model_calibration"))
    for ratio, experiments in RSC_DATA.items():
        for index, values in enumerate(experiments,1):
            temperature, *responses=values; run=f"lari2017-{ratio.replace(':','_')}-{temperature}"
            for response, value in zip(RSC_COLUMNS,responses):
                rows.append(dict(measurement_id=f"{run}-{response}",run_id=run,dataset_id="lari2017_esi_tables_s4_s8",catalyst_id=f"Lari2017_FeCoCe_{ratio}",catalyst_composition=f"Fe:Co:Ce={ratio}",support="unsupported",preparation_method="solvothermal",temperature_c=temperature,pressure_bar=2,h2_co_ratio=1,ghsv_h_inv=3600,response_name=response,response_value=value,response_unit="pct",measurement_uncertainty="not_reported",source_doi=RSC_DOI,source_locator=f"ESI Table S{4+list(RSC_DATA).index(ratio)}",source_url=RSC_SOURCE,evidence_type="published_experiment",compatibility_class="contextual_cobalt_cerium_family",external_validation_eligible=False,exclusion_reason="Fe_present_support_and_composition_mismatch"))
    return rows


def main():
    rows=build_rows(); OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with OUTPUT.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
    unique_runs=len({row["run_id"] for row in rows})
    manifest={"schema_version":"1.0.0","measurement_rows":len(rows),"unique_experimental_runs":unique_runs,"strict_model_catalyst_runs":22,"contextual_family_runs":30,"externally_validating_runs":0,"minimum_100_measurements_met":len(rows)>=100,"sha256":hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),"recommendation_blocked":True,"note":"Measurement rows are not independent experiments; model validation remains pending."}
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(manifest,indent=2,ensure_ascii=False))


if __name__=="__main__": main()
