import unittest
from plataforma_ltft.literature_kinetics import CATALYST, fit, predict
from plataforma_ltft.experimental_planning import validate_pilot_record


class LiteratureKineticsTests(unittest.TestCase):
    def rows(self):
        import math
        return [dict(catalyst_id=CATALYST, temperature_c=t, p_h2_bar=h, p_co_bar=c,
                     rate_mmol_gcat_min=math.exp(-3 + 2*(1000*(1/493.15-1/(t+273.15))) + (h == .4)*.1))
                for t in (200,220,240,260) for h,c in ((.333,.333),(.4,.267))]

    def test_recovers_known_synthetic_law_without_claiming_validation(self):
        rows = self.rows(); model = fit(rows)
        self.assertAlmostEqual(model['beta'][1], 2)
        self.assertFalse(model['external_validation'])
        self.assertTrue(model['recommendation_blocked'])
        self.assertAlmostEqual(predict(model, rows)[0]['median_rate'], rows[0]['rate_mmol_gcat_min'])

    def test_rejects_transfer_and_nonidentifiability(self):
        rows = self.rows(); model = fit(rows)
        for override in ({'temperature_c':270}, {'p_h2_bar':10}, {'catalyst_id':'other'}):
            with self.assertRaises(ValueError): predict(model, [dict(rows[0], **override)])
        with self.assertRaises(ValueError): fit(rows[:1]*4)

    def test_literature_never_becomes_project_pilot(self):
        record = dict(pilot_id='test', protocol_id='test', execution_date='2020-01-01',
                      raw_data_uri='source.csv', analytical_method='GC', execution_confirmed=True,
                      raw_data_sha256='a'*64, raw_data_verified=True, reviewer='test',
                      comparison_report_uri='report.json', evidence_type='published_experiment')
        self.assertFalse(validate_pilot_record(record)['record_is_evidence'])
        record['evidence_type'] = 'project_experiment'
        self.assertTrue(validate_pilot_record(record)['record_is_evidence'])
        record['execution_date'] = '2999-01-01'
        self.assertFalse(validate_pilot_record(record)['record_is_evidence'])
