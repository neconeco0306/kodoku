from __future__ import annotations

from collections import Counter

from .core import Candidate, EvolutionConfig, evolve


def _score(candidate: Candidate) -> float:
    words = [
        token.strip(".,:;!?()[]{}").lower()
        for token in candidate.text.split()
        if token.strip(".,:;!?()[]{}")
    ]
    if not words:
        return 0.0

    unique = len(set(words))
    repetition_penalty = sum(
        count - 1 for count in Counter(words).values() if count > 1
    )
    specificity_bonus = sum(
        1 for word in words if len(word) >= 7
    ) * 0.25

    return unique + specificity_bonus - repetition_penalty * 0.5


def main() -> None:
    seeds = [
        Candidate(text="AI inbox triage for small teams"),
        Candidate(text="Local first research notebook with replayable experiments"),
        Candidate(text="Agent evaluation harness with deterministic fallbacks"),
    ]

    result = evolve(
        seeds,
        evaluator=_score,
        config=EvolutionConfig(
            generations=8,
            population_size=10,
            survivors=3,
            hall_of_fame_size=10,
            seed=42,
        ),
    )

    print("KODOKU demo")
    print("=" * 48)

    for index, candidate in enumerate(result.hall_of_fame[:5], start=1):
        print(f"{index:>2}. score={candidate.score:.2f}")
        print(f"    {candidate.text}")
        print(f"    id={candidate.id} parent={candidate.parent_id}")


if __name__ == "__main__":
    main()
