"""Source-nested research comparison. Never enables experimental recommendations.

Only NumPy is required. GP hyperparameters are fixed; model selection is nested.
The hybrid is an empirical inverse-temperature trend plus a GP residual, NOT
an identified kinetic law or a reactor mass/energy balance.
"""
from __future__ import annotations

import math
import numpy as np

MODELS = ('ridge', 'gaussian_process', 'hybrid_trend_gp')
PROFILES = {
    'operating_core': ('temperature_c', 'pressure_bar', 'h2_co_ratio'),
    'space_time': ('temperature_c', 'pressure_bar', 'h2_co_ratio', 'ghsv_ml_gcat_h', 'tos_h'),
}


def numeric(row, key):
    try:
        value = float(row.get(key, ''))
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) else None


def eligible(row, target, fields):
    y = numeric(row, target)
    if y is None or not 0 <= y <= 100:
        return False
    for key in fields:
        v = numeric(row, key)
        if v is None or (key == 'tos_h' and v < 0) or (key != 'tos_h' and v <= 0):
            return False
    return True


def source(row):
    return row.get('source_group_id') or row['source_doi']


def design(rows, fields, families):
    result = []
    for row in rows:
        values = []
        for field in fields:
            v = float(row[field])
            if field == 'temperature_c':
                v = 1000 / (v + 273.15)
            elif field == 'tos_h':
                v = math.log1p(v)
            elif field in ('ghsv_ml_gcat_h', 'pressure_bar', 'h2_co_ratio'):
                v = math.log(v)
            values.append(v)
        result.append(values + [float(row['family'] == f) for f in families])
    return np.asarray(result, dtype=float)


def predict(train, test, target, fields, model, *, observation_weights=None):
    if model not in MODELS or not train or not test:
        raise ValueError('Unknown model or empty train/test')
    if not all(eligible(r, target, fields) for r in train):
        raise ValueError('Invalid training values')
    families = sorted({r['family'] for r in train})
    x, z = design(train, fields, families), design(test, fields, families)
    groups = [source(r) for r in train]
    weights = np.array([len(train)/(len(set(groups))*groups.count(g)) for g in groups])
    if observation_weights is not None:
        weights *= np.asarray(observation_weights, dtype=float)
        weights *= len(weights) / weights.sum()
    mean = np.average(x, axis=0, weights=weights)
    scale = np.sqrt(np.average((x-mean)**2, axis=0, weights=weights))
    scale[scale < 1e-10] = 1
    x, z = (x-mean)/scale, (z-mean)/scale
    y = np.array([float(r[target]) for r in train])
    a, b = np.c_[np.ones(len(x)), x], np.c_[np.ones(len(z)), z]
    penalty = np.eye(a.shape[1])*10
    penalty[0, 0] = 0
    beta = np.linalg.solve(a.T@(weights[:, None]*a)+penalty, a.T@(weights*y))
    trend, trend_test = a@beta, b@beta
    if model == 'ridge':
        return np.clip(trend_test, 0, 100)
    if model == 'gaussian_process':
        trend = np.full(len(x), np.average(y, weights=weights))
        trend_test = np.full(len(z), trend[0])
    # Fixed unit-amplitude RBF; publication balancing enters observation noise.
    def kernel(p, q):
        return np.exp(-np.sum((p[:, None]-q[None, :])**2, axis=2)/(2*2.0**2))
    k = kernel(x, x)+np.diag(0.25/weights+1e-8)
    return np.clip(trend_test+kernel(z, x)@np.linalg.solve(k, y-trend), 0, 100)


def metrics(records):
    if not records:
        return {'n': 0, 'mae': None, 'mse': None, 'rmse': None, 'bias': None}
    e = np.array([r['predicted']-r['observed'] for r in records])
    groups = sorted({r['source'] for r in records})
    source_mae = [np.mean([abs(r['predicted']-r['observed']) for r in records if r['source']==g]) for g in groups]
    rng = np.random.default_rng(17028)
    bootstrap = np.mean(rng.choice(source_mae, (1000,len(groups)), replace=True),axis=1)
    return {'n': len(e), 'sources': len(groups), 'mae': float(np.mean(abs(e))),
            'source_balanced_mae': float(np.mean(source_mae)), 'mse': float(np.mean(e**2)),
            'rmse': float(np.sqrt(np.mean(e**2))), 'bias': float(np.mean(e)),
            'source_mae_bootstrap_95_descriptive': np.quantile(bootstrap,[.025,.975]).tolist()}


def compare(rows, target, fields, scope='transfer_diagnostic', *, models=MODELS, predictor=predict):
    """Outer source held out; winner chosen solely on inner source folds.

    In family scope, unseen families abstain rather than falling back globally.
    Interval width uses the inner OOF error quantile: heuristic, not conformal.
    """
    rows = [r for r in rows if eligible(r,target,fields)]
    if len({r['row_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate observation IDs')
    groups = sorted({source(r) for r in rows})
    records, folds = [], []
    for holdout in groups:
        outer_train = [r for r in rows if source(r)!=holdout]
        test_all = [r for r in rows if source(r)==holdout]
        for family in (sorted({r['family'] for r in test_all}) if scope=='family' else [None]):
            train = [r for r in outer_train if family is None or r['family']==family]
            test = [r for r in test_all if family is None or r['family']==family]
            training_groups = sorted({source(r) for r in train})
            if len(training_groups)<3:
                folds.append({'held_out':holdout,'family':family,'status':'insufficient_training_sources', 'test_rows':len(test)})
                continue
            inner = {m:[] for m in models}
            for validation in training_groups:
                tr = [r for r in train if source(r)!=validation]
                va = [r for r in train if source(r)==validation]
                for m in models:
                    for r,p in zip(va,predictor(tr,va,target,fields,m)):
                        inner[m].append({'source':validation,'observed':float(r[target]),'predicted':float(p)})
            scores = {m:metrics(inner[m])['source_balanced_mae'] for m in models}
            chosen = min(models,key=lambda m:scores[m])
            errors = [abs(r['predicted']-r['observed']) for r in inner[chosen]]
            # Empirical inner OOF absolute-error quantile, no coverage guarantee.
            width = float(np.quantile(errors,.95,method='higher'))
            folds.append({'held_out':holdout,'family':family,'training_sources':training_groups,
                          'selected':chosen,'inner_source_balanced_mae':scores,'status':'evaluated'})
            for m in models:
                for r,p in zip(test,predictor(train,test,target,fields,m)):
                    unseen = r['family'] not in {v['family'] for v in train}
                    outside = any(float(r[f])<min(float(v[f]) for v in train) or float(r[f])>max(float(v[f]) for v in train) for f in fields)
                    rec={'model':m,'row_id':r['row_id'],'source':holdout,'family':r['family'],
                         'observed':float(r[target]),'predicted':float(p),'residual':float(p)-float(r[target]),
                         'unseen_family':unseen,'outside_training_ranges':outside}
                    records.append(rec)
                    if m==chosen:
                        records.append(dict(rec,model='nested_selected',lower=max(0,float(p)-width),upper=min(100,float(p)+width),interval_kind='inner_oof_heuristic_not_calibrated'))
    result={m:metrics([r for r in records if r['model']==m]) for m in (*models,'nested_selected')}
    selected=[r for r in records if r['model']=='nested_selected']
    return {'eligible_rows':len(rows),'sources':len(groups),'scope':scope,
            'coverage':len(selected)/len(rows) if rows else 0,
            'interval_coverage_observed':sum(r['lower']<=r['observed']<=r['upper'] for r in selected)/len(selected) if selected else None,
            'metrics':result,'folds':folds,'residuals':records,
            'model_promoted':False,'recommendation_blocked':True,
            'independent_prospective_confirmation_pending':True}
