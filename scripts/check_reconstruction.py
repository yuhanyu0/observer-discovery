from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'outputs_reconstruction/reconstruction_summary.csv'
if not p.exists(): raise SystemExit('Run reconstruction first')
df=pd.read_csv(p).set_index('condition')
base=df.loc['baseline']
assert int(base.n_candidate_axes)==4
assert float(base.top_effect_size)>1.0
assert float(df.loc['label_shuffle'].top_effect_size)<float(base.top_effect_size)*0.5
assert int(df.loc['label_shuffle'].n_promoted_axes)==0
assert float(df.loc['knockdown_volatility_family'].top_effect_size)<float(base.top_effect_size)*0.75
assert float(df.loc['stride_16'].top_effect_size)<float(base.top_effect_size)*0.6
assert float(df.loc['measurement_noise_2.0'].top_effect_size)<float(base.top_effect_size)*0.8
print('PASS curated reconstruction structural qualification')
