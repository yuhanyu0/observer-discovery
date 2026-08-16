# Reproducibility status

## Frozen historical evidence

The files under `historical/` are the public scientific evidence layer for v0.4. They preserve the baseline axes, primitive readout scores, stride sweep, reviewer-defense controls, measurement-noise sweep, threshold sensitivity, and multi-seed stability summaries.

The historical v0.5 version manifest records `run_observer_discovery_v0.py` (19,182 bytes), `scripts/run_stability_sensitivity.py` (20,847 bytes), `tests/test_smoke.py` (4,002 bytes), and `requirements.txt` (50 bytes), and the v0.5 QA report records `pytest -q: 3 passed`. However, the exact historical source files are not currently recoverable as standalone canonical Library assets.

## Public executable reconstruction

`experiments/observer_discovery_reconstruction.py` is newly assembled from the documented method and frozen result schema. It is **not byte-identical historical source** and must not be cited as if it generated the frozen v0.4 numbers.

The reconstruction is tested for structural behavior:

- 13 primitive readouts;
- correlation-based clustering and PCA candidate axes;
- strong baseline separability;
- label-shuffle degradation;
- readout-family knockdown degradation;
- coarse-stride and high-noise degradation.

This distinction is deliberate: executable method availability is useful, but provenance should not be manufactured.
