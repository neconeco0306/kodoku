from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import blake2s
from random import Random
from typing import Callable, Iterable
from uuid import uuid4


Evaluator = Callable[["Candidate"], float]
Mutator = Callable[["Candidate", Random], "Candidate"]


@dataclass(slots=True)
class Candidate:
    text: str
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    parent_id: str | None = None
    generation: int = 0
    score: float | None = None
    notes: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class EvolutionConfig:
    generations: int = 10
    population_size: int = 12
    survivors: int = 4
    hall_of_fame_size: int = 20
    seed: int = 42
    deterministic_ids: bool = False

    def validate(self) -> None:
        if self.generations < 1:
            raise ValueError("generations must be >= 1")
        if self.population_size < 1:
            raise ValueError("population_size must be >= 1")
        if not 1 <= self.survivors <= self.population_size:
            raise ValueError("survivors must be between 1 and population_size")
        if self.hall_of_fame_size < 1:
            raise ValueError("hall_of_fame_size must be >= 1")


@dataclass(slots=True)
class EvolutionResult:
    final_population: list[Candidate]
    hall_of_fame: list[Candidate]
    history: list[list[Candidate]]


def _stable_candidate_id(*parts: object) -> str:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    return blake2s(payload, digest_size=10).hexdigest()


def _with_deterministic_id(
    candidate: Candidate,
    *,
    run_seed: int,
    stage: str,
    generation: int,
    ordinal: int,
    parent_id: str | None,
) -> Candidate:
    candidate_id = _stable_candidate_id(
        run_seed,
        stage,
        generation,
        ordinal,
        parent_id or "",
        candidate.text,
    )
    return replace(
        candidate,
        id=candidate_id,
        parent_id=parent_id,
        generation=generation,
        score=None,
    )


def _default_mutator(candidate: Candidate, rng: Random) -> Candidate:
    tokens = candidate.text.split()
    if not tokens:
        text = candidate.text
    else:
        operation = rng.choice(("swap", "duplicate", "trim"))
        mutated = list(tokens)

        if operation == "swap" and len(mutated) >= 2:
            i, j = rng.sample(range(len(mutated)), 2)
            mutated[i], mutated[j] = mutated[j], mutated[i]
        elif operation == "duplicate":
            mutated.insert(rng.randrange(len(mutated) + 1), rng.choice(mutated))
        elif operation == "trim" and len(mutated) > 2:
            mutated.pop(rng.randrange(len(mutated)))

        text = " ".join(mutated)

    return Candidate(
        text=text,
        parent_id=candidate.id,
        generation=candidate.generation + 1,
    )


def _evaluate(
    population: Iterable[Candidate],
    evaluator: Evaluator,
) -> list[Candidate]:
    evaluated: list[Candidate] = []

    for candidate in population:
        score = float(evaluator(candidate))
        evaluated.append(replace(candidate, score=score))

    return evaluated


def _rank(population: Iterable[Candidate]) -> list[Candidate]:
    return sorted(
        population,
        key=lambda candidate: (
            float("-inf") if candidate.score is None else candidate.score
        ),
        reverse=True,
    )


def _dedupe(candidates: Iterable[Candidate]) -> list[Candidate]:
    seen: set[tuple[str, str | None, int]] = set()
    output: list[Candidate] = []

    for candidate in candidates:
        key = (candidate.text, candidate.parent_id, candidate.generation)
        if key in seen:
            continue
        seen.add(key)
        output.append(candidate)

    return output


def evolve(
    seeds: Iterable[Candidate],
    *,
    evaluator: Evaluator,
    config: EvolutionConfig | None = None,
    mutator: Mutator | None = None,
) -> EvolutionResult:
    cfg = config or EvolutionConfig()
    cfg.validate()

    mutation = mutator or _default_mutator
    rng = Random(cfg.seed)

    initial = list(seeds)
    if not initial:
        raise ValueError("at least one seed candidate is required")

    if cfg.deterministic_ids:
        initial = [
            _with_deterministic_id(
                candidate,
                run_seed=cfg.seed,
                stage="seed",
                generation=0,
                ordinal=index,
                parent_id=candidate.parent_id,
            )
            for index, candidate in enumerate(initial)
        ]

    population = initial[: cfg.population_size]

    while len(population) < cfg.population_size:
        parent = rng.choice(initial)
        child = mutation(parent, rng)
        if cfg.deterministic_ids:
            child = _with_deterministic_id(
                child,
                run_seed=cfg.seed,
                stage="bootstrap",
                generation=0,
                ordinal=len(population),
                parent_id=parent.id,
            )
        population.append(child)

    history: list[list[Candidate]] = []
    hall: list[Candidate] = []

    for generation in range(cfg.generations):
        normalized = [
            replace(candidate, generation=generation)
            for candidate in population
        ]
        ranked = _rank(_evaluate(normalized, evaluator))
        history.append(ranked)

        hall = _rank(_dedupe([*hall, *ranked]))[: cfg.hall_of_fame_size]
        survivors = ranked[: cfg.survivors]

        next_population = list(survivors)
        while len(next_population) < cfg.population_size:
            parent = rng.choice(survivors)
            child = mutation(parent, rng)
            child.generation = generation + 1
            if cfg.deterministic_ids:
                child = _with_deterministic_id(
                    child,
                    run_seed=cfg.seed,
                    stage="generation",
                    generation=generation + 1,
                    ordinal=len(next_population),
                    parent_id=parent.id,
                )
            next_population.append(child)

        population = next_population

    final_population = history[-1]
    return EvolutionResult(
        final_population=final_population,
        hall_of_fame=hall,
        history=history,
    )
