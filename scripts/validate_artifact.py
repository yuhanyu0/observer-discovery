from pathlib import Path
import json, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def req(c,m):
    if not c: raise SystemExit('FAIL: '+m)
for rel in ['README.md','CLAIM_BOUNDARY.md','REPRODUCIBILITY.md','METHODS.md','OGD_BRIDGE.md','SOURCE_DOCUMENTS.json','historical/frozen_summary.json','historical/observer_axes.csv','historical/defense_overview.csv','historical/stride_sweep_summary.csv','historical/multi_seed_stability_aggregate.csv','experiments/observer_discovery_reconstruction.py']:
    req((ROOT/rel).exists(),'missing '+rel)
s=json.load(open(ROOT/'historical/frozen_summary.json'))
req(s['n_primitive_readouts']==13,'readout count')
req(s['baseline']['candidate_axes']==4,'candidate axes')
req(s['baseline']['promoted_axes']==2,'promoted axes')
req(abs(s['baseline']['top_effect_size']-4.098978939189904)<1e-6,'top effect drift')
req(abs(s['baseline']['top_auroc']-0.999825)<1e-9,'top AUROC drift')
req(s['controls']['label_shuffle']['promoted_axes']==0,'label shuffle')
req(s['controls']['knockdown_volatility_family']['promoted_axes']==0,'knockdown')
req(s['controls']['measurement_noise_endpoint']['promoted_axes']==0,'noise endpoint')
req(s['stride']['stride_16_effect']<0.25 and s['stride']['stride_16_promoted_axes']==0,'stride endpoint')
req(s['measurement_noise']['noise_2_effect']<0.7 and s['measurement_noise']['noise_2_promoted_axes']==0,'noise endpoint effect')
req(s['multi_seed']['n_seeds']==24 and s['multi_seed']['promotion_rate']==1.0,'multi-seed')
req(s['multi_seed']['mean_signature_jaccard']>0.98,'signature stability')
req(all(v is False for v in s['claim_flags'].values()),'overclaim flag')
src=json.load(open(ROOT/'SOURCE_DOCUMENTS.json'))
req('not_recovered' in src['historical_runner_status'],'runner provenance')
readme=(ROOT/'README.md').read_text()
for x in ['curated reconstruction','not a byte-identical','13 primitive readouts','4 candidate axes','2','does **not** claim to discover real observers']:
    req(x.lower() in readme.lower(),'README boundary '+x)
print('PASS Observer Discovery public artifact validation')
