from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def test_frozen_baseline():
    s=json.load(open(ROOT/'historical/frozen_summary.json'))
    assert s['n_primitive_readouts']==13
    assert s['baseline']['candidate_axes']==4
    assert s['baseline']['promoted_axes']==2
def test_controls():
    d=pd.read_csv(ROOT/'historical/defense_overview.csv').set_index('experiment')
    assert int(d.loc['label_shuffle','n_promoted_axes'])==0
    assert int(d.loc['knockdown_volatility_family','n_promoted_axes'])==0
def test_seed_stability():
    d=pd.read_csv(ROOT/'historical/multi_seed_stability_aggregate.csv').iloc[0]
    assert int(d.n_seeds)==24
    assert float(d.top_axis_promoted_rate)==1.0
