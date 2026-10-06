from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Iterable, Literal


PromotionDecision = Literal["PROMOTE", "HOLD"]


@dataclass(frozen=True, slots=True)
class EvaluationObservation:
    candidate_id: str
    evaluator_id: str
    independence_group: str
    seed: int
    normalized_score: float
    adversarial: bool = False

    def validate(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id is required")
        if not self.evaluator_id.strip():
            raise ValueError("evaluator_id is required")
        if not self.independence_group.strip():
            raise ValueError("independence_group is required")
        if not 0.0 <= self.normalized_score <= 1.0:
            raise ValueError("normalized_score must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class RobustnessPolicy:
    min_observations: int = 6
    min_independence_groups: int = 3
    min_seeds: int = 3
    min_adversarial_observations: int = 1
    min_median_score: float = 0.65
    min_floor_score: float = 0.35
    max_score_spread: float = 0.45

    def validate(self) -> None:
        if self.min_observations < 1:
            raise ValueError("min_observations must be >= 1")
        if self.min_independence_groups < 1:
            raise ValueError("min_independence_groups must be >= 1")
        if self.min_seeds < 1:
            raise ValueError("min_seeds must be >= 1")
        if self.min_adversarial_observations < 0:
            raise ValueError("min_adversarial_observations must be >= 0")
        for name, value in (
            ("min_median_score", self.min_median_score),
            ("min_floor_score", self.min_floor_score),
            ("max_score_spread", self.max_score_spread),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class RobustnessReport:
    candidate_id: str
    decision: PromotionDecision
    reasons: tuple[str, ...]
    observation_count: int
    independence_group_count: int
    seed_count: int
    adversarial_count: int
    median_score: float | None
    floor_score: float | None
    score_spread: float | None


def assess_candidate(
    observations: Iterable[EvaluationObservation],
    *,
    policy: RobustnessPolicy | None = None,
) -> RobustnessReport:
    cfg = policy or RobustnessPolicy()
    cfg.validate()

    items = list(observations)
    if not items:
        return RobustnessReport(
            candidate_id="",
            decision="HOLD",
            reasons=("no observations",),
            observation_count=0,
            independence_group_count=0,
            seed_count=0,
            adversarial_count=0,
            median_score=None,
            floor_score=None,
            score_spread=None,
        )

    for item in items:
        item.validate()

    candidate_ids = {item.candidate_id for item in items}
    if len(candidate_ids) != 1:
        raise ValueError("all observations must refer to the same candidate_id")

    candidate_id = items[0].candidate_id
    groups = {item.independence_group for item in items}
    seeds = {item.seed for item in items}
    adversarial_count = sum(item.adversarial for item in items)
    scores = [item.normalized_score for item in items]
    med = float(median(scores))
    floor = min(scores)
    spread = max(scores) - min(scores)

    reasons: list[str] = []

    if len(items) < cfg.min_observations:
        reasons.append(
            f"observations {len(items)} < required {cfg.min_observations}"
        )
    if len(groups) < cfg.min_independence_groups:
        reasons.append(
            f"independence groups {len(groups)} < required {cfg.min_independence_groups}"
        )
    if len(seeds) < cfg.min_seeds:
        reasons.append(f"seeds {len(seeds)} < required {cfg.min_seeds}")
    if len(normalization_ids) != 1:\n        reasons.append(\n            f\"normalization schemes {len(normalization_ids)} != required 1\"\n        )\n    if adversarial_count < cfg.min_adversarial_observations:
        reasons.append(
            f"adversarial observations {adversarial_count} < required "
            f"{cfg.min_adversarial_observations}"
        )
    if med < cfg.min_median_score:
        reasons.append(
            f"median score {med:.3f} < required {cfg.min_median_score:.3f}"
        )
    if floor < cfg.min_floor_score:
        reasons.append(
            f"floor score {floor:.3f} < required {cfg.min_floor_score:.3f}"
        )
    if spread > cfg.max_score_spread:
        reasons.append(
            f"score spread {spread:.3f} > allowed {cfg.max_score_spread:.3f}"
        )

    return RobustnessReport(
        candidate_id=candidate_id,
        decision="HOLD" if reasons else "PROMOTE",
        reasons=tuple(reasons),
        observation_count=len(items),
        independence_group_count=len(groups),
        seed_count=len(seeds),
        adversarial_count=adversarial_count,
        median_score=med,
        floor_score=floor,
        score_spread=spread,
    )
