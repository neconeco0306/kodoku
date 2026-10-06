from __future__ import annotations

from dataclasses import dataclass
from random import Random
from statistics import mean

from kodoku import Candidate, EvolutionConfig, evolve


POPULATION = 64
SURVIVORS = 12
N_BITS_RUGGED = 40
N_BITS_SMOOTH = 128


def mutate_bits(candidate: Candidate, rng: Random) -> Candidate:
    bits = list(candidate.text)
    roll = rng.random()
    flips = 1 if roll < 0.7 else 2 if roll < 0.9 else rng.choice((3, 4))
    for index in rng.sample(range(len(bits)), flips):
        bits[index] = "1" if bits[index] == "0" else "0"
    return Candidate(
        text="".join(bits),
        parent_id=candidate.id,
        generation=candidate.generation + 1,
    )


def random_seeds(seed: int, n_bits: int, count: int = 8) -> list[Candidate]:
    rng = Random(seed)
    return [
        Candidate(text="".join(str(rng.randrange(2)) for _ in range(n_bits)))
        for _ in range(count)
    ]


def rugged_evaluator(seed: int):
    rng = Random(seed)
    target = [rng.randrange(2) for _ in range(N_BITS_RUGGED)]
    pairs = []
    for _ in range(N_BITS_RUGGED * 2):
        i, j = rng.sample(range(N_BITS_RUGGED), 2)
        pairs.append((i, j, rng.randrange(4), rng.uniform(0.1, 0.8)))

    def score(candidate: Candidate) -> float:
        bits = [int(value) for value in candidate.text]
        total = 0.0
        for start in range(0, N_BITS_RUGGED, 5):
            stop = min(start + 5, N_BITS_RUGGED)
            matches = sum(bits[i] == target[i] for i in range(start, stop))
            size = stop - start
            total += size * 1.5 if matches == size else (size - 1 - matches) * 0.7
        for i, j, preferred, weight in pairs:
            if ((bits[i] << 1) | bits[j]) == preferred:
                total += weight
        return total

    return score


def smooth_evaluator(seed: int):
    rng = Random(seed)
    target = [rng.randrange(2) for _ in range(N_BITS_SMOOTH)]

    def score(candidate: Candidate) -> float:
        bits = [int(value) for value in candidate.text]
        matches = sum(a == b for a, b in zip(bits, target))
        prefix = 0
        for a, b in zip(bits, target):
            if a != b:
                break
            prefix += 1
        return matches + 0.5 * prefix

    return score


@dataclass(frozen=True)
class Strategy:
    name: str
    segments: tuple[tuple[int, int], ...]


STRATEGIES = (
    Strategy("1000x1", ((1000, 1),)),
    Strategy("500x2", ((500, 2),)),
    Strategy("200x5", ((200, 5),)),
    Strategy("100x10", ((100, 10),)),
    Strategy("50x20", ((50, 20),)),
    Strategy("hybrid_500x1_plus_50x10", ((500, 1), (50, 10))),
)


def run_segment(
    evaluator,
    *,
    generations: int,
    landscape_seed: int,
    run_index: int,
    n_bits: int,
) -> float:
    seed = landscape_seed * 100_003 + run_index * 7_919 + generations
    result = evolve(
        random_seeds(seed, n_bits),
        evaluator=evaluator,
        config=EvolutionConfig(
            generations=generations,
            population_size=POPULATION,
            survivors=SURVIVORS,
            hall_of_fame_size=20,
            seed=seed,
        ),
        mutator=mutate_bits,
    )
    return float(result.hall_of_fame[0].score)


def run_strategy(strategy: Strategy, evaluator, *, landscape_seed: int, n_bits: int) -> float:
    best = float("-inf")
    run_index = 0
    for generations, repeats in strategy.segments:
        for _ in range(repeats):
            best = max(
                best,
                run_segment(
                    evaluator,
                    generations=generations,
                    landscape_seed=landscape_seed,
                    run_index=run_index,
                    n_bits=n_bits,
                ),
            )
            run_index += 1
    return best


def benchmark(label: str, evaluator_factory, n_bits: int, landscapes: range) -> None:
    scores = {strategy.name: [] for strategy in STRATEGIES}
    for landscape_seed in landscapes:
        evaluator = evaluator_factory(landscape_seed)
        for strategy in STRATEGIES:
            scores[strategy.name].append(
                run_strategy(
                    strategy,
                    evaluator,
                    landscape_seed=landscape_seed,
                    n_bits=n_bits,
                )
            )

    print(label)
    for strategy in STRATEGIES:
        values = scores[strategy.name]
        print(f"{strategy.name:28s} mean={mean(values):.3f} worst={min(values):.3f}")
    print()


def main() -> None:
    benchmark("rugged", rugged_evaluator, N_BITS_RUGGED, range(1, 21))
    benchmark("smooth", smooth_evaluator, N_BITS_SMOOTH, range(1, 11))


if __name__ == "__main__":
    main()
