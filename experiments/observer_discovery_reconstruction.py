#!/usr/bin/env python3
"""Curated executable reconstruction of the Observer Discovery method.

This is NOT the recovered historical v0.4 source. The archived v0.5 manifest
verifies that the historical runner existed, but that exact file is not
currently available as a standalone canonical Library asset.

This release implementation makes the method executable while historical
frozen tables remain the scientific source of truth.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

READOUTS=[
    'mean','std','variance','skew_proxy','kurtosis_proxy','autocorr_lag1','autocorr_lag5',
    'rolling_vol_mean','rolling_vol_std','high_frequency_energy','low_frequency_energy',
    'turning_rate','max_drawdown_proxy'
]
VOL_FAMILY={
    'std','variance','kurtosis_proxy','autocorr_lag1','autocorr_lag5','rolling_vol_mean',
    'rolling_vol_std','high_frequency_energy','turning_rate','max_drawdown_proxy'
}

def _acf(x,lag):
    if len(x)<=lag or np.std(x)<1e-12: return 0.0
    return float(np.corrcoef(x[:-lag],x[lag:])[0,1])

def _skew(x):
    s=np.std(x)
    return 0.0 if s<1e-12 else float(np.mean(((x-np.mean(x))/s)**3))

def _kurt(x):
    s=np.std(x)
    return 0.0 if s<1e-12 else float(np.mean(((x-np.mean(x))/s)**4)-3.0)

def _rolling_std(x,w=16):
    if len(x)<w: return np.array([np.std(x)])
    return np.array([np.std(x[i-w+1:i+1]) for i in range(w-1,len(x))])

def _readouts(x):
    x=np.asarray(x,float)
    dx=np.diff(x)
    r=_rolling_std(x,16)
    spec=np.abs(np.fft.rfft(x-x.mean()))**2
    if len(spec)>4:
        cut=max(2,len(spec)//4)
        low=float(spec[1:cut].mean())
        high=float(spec[cut:].mean())
    else: low=high=0.0
    turns=float(np.mean(np.sign(dx[1:])!=np.sign(dx[:-1]))) if len(dx)>1 else 0.0
    cumulative=np.cumsum(x-x.mean())
    peak=np.maximum.accumulate(cumulative)
    draw=float(np.max(peak-cumulative)) if len(cumulative) else 0.0
    return {
        'mean':float(x.mean()), 'std':float(x.std()), 'variance':float(x.var()),
        'skew_proxy':_skew(x), 'kurtosis_proxy':_kurt(x),
        'autocorr_lag1':_acf(x,1), 'autocorr_lag5':_acf(x,5),
        'rolling_vol_mean':float(r.mean()), 'rolling_vol_std':float(r.std()),
        'high_frequency_energy':high, 'low_frequency_energy':low,
        'turning_rate':turns, 'max_drawdown_proxy':draw,
    }

def generate(n_per_kernel=200,T=256,seed=42,measurement_noise=0.0,stride=1):
    rng=np.random.default_rng(seed)
    rows=[]; labels=[]
    for label in [0,1]:
        for _ in range(n_per_kernel):
            e=rng.normal(size=T)
            x=np.zeros(T)
            if label==0:
                for t in range(1,T): x[t]=0.50*x[t-1]+0.88*e[t]
            else:
                burst=np.ones(T)
                for start in rng.choice(np.arange(18,T-18), size=5, replace=False):
                    burst[start:start+8] += rng.uniform(1.6,2.8)
                hf=np.sin(np.pi*np.arange(T))*rng.normal(0.0,0.42,size=T)
                for t in range(1,T): x[t]=0.45*x[t-1]+0.72*burst[t]*e[t]+0.42*hf[t]
                x=x/(0.75+0.25*np.std(x))
            if measurement_noise>0:
                x=x+rng.normal(scale=measurement_noise,size=T)
            if stride>1:
                m=(len(x)//stride)*stride
                x=x[:m].reshape(-1,stride).mean(axis=1)
            rows.append(_readouts(x)); labels.append(label)
    return pd.DataFrame(rows)[READOUTS], np.asarray(labels,int)

def effect_size(z,y):
    a=z[y==0]; b=z[y==1]
    va=np.var(a,ddof=1); vb=np.var(b,ddof=1)
    pooled=np.sqrt(((len(a)-1)*va+(len(b)-1)*vb)/max(len(a)+len(b)-2,1))
    return 0.0 if pooled<1e-12 else float(abs(a.mean()-b.mean())/pooled)

def bootstrap_low(z,y,n_boot=80,seed=123):
    rng=np.random.default_rng(seed); vals=[]
    a=z[y==0]; b=z[y==1]
    for _ in range(n_boot):
        aa=rng.choice(a,size=len(a),replace=True); bb=rng.choice(b,size=len(b),replace=True)
        yy=np.r_[np.zeros(len(aa),int),np.ones(len(bb),int)]
        vals.append(effect_size(np.r_[aa,bb],yy))
    return float(np.quantile(vals,0.025))

def discover(X,y,n_clusters=4,n_boot=80,seed=42):
    scaler=StandardScaler(); Z=scaler.fit_transform(X)
    corr=pd.DataFrame(Z).corr().fillna(0.0).to_numpy()
    np.fill_diagonal(corr,1.0)
    dist=np.clip(1-np.abs(corr),0,1)
    np.fill_diagonal(dist,0)
    link=linkage(squareform(dist,checks=False),method='average')
    groups=fcluster(link,t=n_clusters,criterion='maxclust')
    out=[]
    for gid in sorted(set(groups)):
        cols=[c for c,g in zip(X.columns,groups) if g==gid]
        block=Z[:,[list(X.columns).index(c) for c in cols]]
        if float(np.var(block, axis=0).sum()) < 1e-12:
            axis=np.zeros(len(block),dtype=float)
        else:
            axis=PCA(n_components=1).fit_transform(block).ravel()
        if axis[y==1].mean()<axis[y==0].mean(): axis=-axis
        eff=effect_size(axis,y); auc=float(roc_auc_score(y,axis)); auc=max(auc,1-auc)
        lo=bootstrap_low(axis,y,n_boot=n_boot,seed=seed+gid)
        out.append({'axis_id':f'axis_{gid-1}','cluster_id':int(gid-1),'n_readouts':len(cols),
                    'top_readouts':'|'.join(cols),'effect_size':eff,'auroc':auc,
                    'bootstrap_low':lo,'promoted':bool(eff>0.8 and lo>0)})
    return pd.DataFrame(out).sort_values('effect_size',ascending=False).reset_index(drop=True)

def run_condition(name,seed=42,stride=1,measurement_noise=0.0,label_shuffle=False,knockdown=False):
    X,y=generate(seed=seed,stride=stride,measurement_noise=measurement_noise)
    if knockdown: X=X[[c for c in X.columns if c not in VOL_FAMILY]]
    if label_shuffle:
        rng=np.random.default_rng(seed+999); y=rng.permutation(y)
    k=min(4,X.shape[1])
    axes=discover(X,y,n_clusters=k,n_boot=60,seed=seed)
    top=axes.iloc[0]
    return {'condition':name,'top_effect_size':float(top.effect_size),'top_auroc':float(top.auroc),
            'n_candidate_axes':int(len(axes)),'n_promoted_axes':int(axes.promoted.sum()),
            'top_readouts':str(top.top_readouts)}, axes

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',default='outputs_reconstruction'); ap.add_argument('--seed',type=int,default=42)
    args=ap.parse_args(); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    rows=[]
    base,axes=run_condition('baseline',seed=args.seed); rows.append(base); axes.to_csv(out/'observer_axes_reconstruction.csv',index=False)
    for s in [2,4,8,16]: rows.append(run_condition(f'stride_{s}',seed=args.seed,stride=s)[0])
    rows.append(run_condition('label_shuffle',seed=args.seed,label_shuffle=True)[0])
    rows.append(run_condition('knockdown_volatility_family',seed=args.seed,knockdown=True)[0])
    for noise in [0.5,1.0,2.0]: rows.append(run_condition(f'measurement_noise_{noise}',seed=args.seed,measurement_noise=noise)[0])
    frame=pd.DataFrame(rows); frame.to_csv(out/'reconstruction_summary.csv',index=False)
    print(frame.to_string(index=False))
    print(json.dumps({'readouts':13,'historical_source_recovered':False,'release_runner':'curated_reconstruction'},indent=2))
if __name__=='__main__': main()
