"""Random Forest research candidates; source-grouped tuning, never OOB validation."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from .target_research import design, source

GRID = {
    f'rf_d{depth}_leaf{leaf}': dict(n_estimators=100, max_depth=depth,
        min_samples_leaf=leaf, max_features=.7, bootstrap=True,
        random_state=17028, n_jobs=1)
    for depth in (2,4) for leaf in (3,5)
}


def predict(train,test,target,fields,model,*,observation_weights=None):
    families=sorted({r['family'] for r in train})
    x,z=design(train,fields,families),design(test,fields,families)
    groups=[source(r) for r in train]
    weights=np.array([len(train)/(len(set(groups))*groups.count(g)) for g in groups])
    if observation_weights is not None:
        weights *= np.asarray(observation_weights, dtype=float)
        weights *= len(weights) / weights.sum()
    estimator=RandomForestRegressor(**GRID[model])
    estimator.fit(x,np.array([float(r[target]) for r in train]),sample_weight=weights)
    return np.clip(estimator.predict(z),0,100)
