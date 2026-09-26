from random import Random

from kodoku import Candidate, EvolutionConfig, evolve


def evaluator(candidate: Candidate) -> float:
    words = candidate.text.lower().split()
    return len(set(words)) + (2.0 if "measurable" in words else 0.0)


def mutator(candidate: Candidate, rng: Random) -> Candidate:
    suffixes = [
        "with measurable outcomes",
        "with human fallback",
        "with reproducible evaluation",
    ]
    return Candidate(
        text=f"{candidate.text} {rng.choice(suffixes)}",
        parent_id=candidate.id,
        generation=candidate.generation + 1,
    )


result = evolve(
    [
        Candidate(text="AI workflow assistant"),
        Candidate(text="Research agent"),
    ],
    evaluator=evaluator,
    mutator=mutator,
    config=EvolutionConfig(
        generations=6,
        population_size=8,
        survivors=3,
        seed=7,
    ),
)

for candidate in result.hall_of_fame[:5]:
    print(candidate.score, candidate.text)
