# Reproducible run manifest

A KODOKU result is not reproducible merely because its prose summary names a generation count.

For any run that may influence downstream decisions, retain a `RunManifest` fingerprint containing:

- committed code revision
- exact runner path
- canonical configuration
- RNG seed
- fingerprint of seed candidate material
- evaluator identity
- mutator identity

If any of these change, the run fingerprint changes.

The manifest proves **run identity**, not correctness. It does not prove that the evaluator was good, the evidence was true, or the winner generalizes. Those questions belong to robustness and evidence validation.

A result without enough information to reconstruct this manifest should be downgraded to historical observation rather than silently treated as reproducible evidence.
