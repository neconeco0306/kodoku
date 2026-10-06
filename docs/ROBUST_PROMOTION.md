# Robust promotion gate

KODOKU search winners are not validated discoveries.

Before a candidate is promoted downstream, the robustness gate requires repeated evaluation across distinct **independence groups**, seeds, and at least one adversarial check.

An independence group is the underlying source of judgment, not the prompt name. Two prompts sent to the same model should normally share one group. This prevents prompt variants from pretending to be independent confirmation.\n\nScores are compared only when every observation declares the same `normalization_id`. The normalization must make scores comparable across evaluators (for example, rank percentile against the same finalist pool). Raw self-reported confidence from different evaluators is not a valid shared scale.

The default thresholds in `RobustnessPolicy` are initial hyperparameters, not scientific constants. They are deliberately fail-closed: disagreement produces `HOLD`, never forced promotion.

This gate also does not treat web retrieval as truth. External source collection should follow the POLYMATH boundary:

`discovery -> candidate evidence -> independent verification -> promotion decision`

The intended downstream flow is:

`KODOKU search winner -> robustness gate -> POLYMATH evidence collection / critique -> NILO-CHECKS or domain-specific validation -> SECOND/Nilo execution`
