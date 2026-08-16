# Methods snapshot

The historical Observer Discovery design starts with trajectories from two controlled kernels and a bank of 13 primitive readouts. Readouts are standardized and clustered using correlation structure. Each cluster is compressed to one candidate axis by the first principal component. Candidate axes are scored using standardized effect size, AUROC, and bootstrap uncertainty.

The frozen promotion rule is:

```text
effect_size > 0.8 and bootstrap_low > 0
```

The main scientific object is not a numeric cluster label. Cluster numbering is arbitrary; stability is assessed through readout membership/signature.

Reliability checks include label shuffle, pre-specified readout-family knockdown, stride coarsening, post-generation measurement noise, promotion-threshold sensitivity, and a 24-seed signature-stability study.

The public reconstruction retains the same conceptual steps but fixes `maxclust=4` as a release fixture so that it is not misrepresented as an independent reproduction of how the historical code selected the number of clusters. Frozen historical tables remain authoritative for quantitative claims.
