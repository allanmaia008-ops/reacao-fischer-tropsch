"""Extract publisher Table 1 and run a reproducible exploratory LTFT benchmark."""
import csv
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from plataforma_ltft.literature_kinetics import CATALYST, fit, predict

URL = 'https://link.springer.com/article/10.1186/2228-5547-4-1/tables/1'
DOI = '10.1186/2228-5547-4-1'


def extract(page):
    table = re.search(r'<table\b.*?</table>', page, re.S).group()
    rows = []
    for tr in re.findall(r'<tr\b.*?</tr>', table, re.S):
        cells = [html.unescape(re.sub('<[^>]+>', '', cell)).strip() for cell in re.findall(r'<td\b[^>]*>(.*?)</td>', tr, re.S)]
        if len(cells) != 7 or not cells[0].isdigit():
            continue
        number, temp, h2, co, flow, conversion, rate = cells
        residual = float(rate) - float(flow) * float(conversion) / 100
        rows.append(dict(row_id=number, catalyst_id=CATALYST, temperature_c=temp,
                         p_h2_bar=h2, p_co_bar=co, feed_co_mmol_gcat_min=flow,
                         conversion_co_pct=conversion, rate_mmol_gcat_min=rate,
                         rate_consistency_residual=residual,
                         consistency_check='pass' if abs(residual) <= .0002 else 'review',
                         ltft_eligible=180 <= float(temp) <= 260,
                         source_doi=DOI, source_table='1', source_url=URL,
                         measurement_uncertainty='not_reported', evidence_type='published_experiment'))
    if len(rows) != 22:
        raise ValueError(f'Expected 22 source records, got {len(rows)}')
    return rows


def main():
    out = ROOT / 'outputs/ft024_literature'
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'table1.html'
    if '--refresh' in sys.argv or not source.exists():
        response = requests.get(URL, timeout=45)
        response.raise_for_status()
        extract(response.text)  # Never replace a valid cache with a challenge/error page.
        source.write_text(response.text, encoding='utf-8')
    rows = extract(source.read_text(encoding='utf-8'))
    destination = ROOT / 'data/evidence/ltft_mansouri_2013_kinetics.csv'
    with destination.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    eligible = [r for r in rows if r['ltft_eligible'] and r['consistency_check'] == 'pass']
    # Fixed split by temperature, before fitting; never called external validation.
    test = [r for r in eligible if float(r['temperature_c']) in (220, 240)]
    train = [r for r in eligible if r not in test]
    model = fit(train)
    predictions = predict(model, test)
    errors = [p['median_rate'] - float(r['rate_mmol_gcat_min']) for r,p in zip(test,predictions)]
    report = {'source_url': URL, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'csv_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
              'source_rows': len(rows), 'ltft_rows': len(eligible),
              'train_ids': [r['row_id'] for r in train], 'test_ids': [r['row_id'] for r in test],
              'validation_type': 'same_study_temperature_holdout', 'model': model,
              'mae_mmol_gcat_min': sum(abs(e) for e in errors)/len(errors),
              'rmse_mmol_gcat_min': (sum(e*e for e in errors)/len(errors))**.5,
              'predictions': [dict(row_id=r['row_id'], observed=float(r['rate_mmol_gcat_min']), **p) for r,p in zip(test,predictions)],
              'excluded_consistency_ids': [r['row_id'] for r in rows if r['consistency_check'] != 'pass'],
              'ft024_status': 'exploratory_model_external_validation_pending',
              'ft027_status': 'laboratory_execution_pending', 'recommendation_blocked': True,
              'limitations': ['One study and one catalyst only; no industrial-pressure transfer',
                             'Two coupled pressures; individual pressure orders are not identifiable',
                             'Intervals assume independent normal homoscedastic log residuals; not measurement uncertainty',
                             'No independent validation dataset or project laboratory pilot']}
    (out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('source_rows','ltft_rows','mae_mmol_gcat_min','rmse_mmol_gcat_min','excluded_consistency_ids')}, indent=2))


if __name__ == '__main__':
    main()
