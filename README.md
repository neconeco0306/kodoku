# KODOKU

KODOKU is an experimental evolutionary search framework for ideas.

Instead of asking one model for one answer, KODOKU keeps a population of candidates, evaluates them, preserves strong lineages, mutates survivors, injects outside "bloodlines", and records a Hall of Fame across generations.

The public version is intentionally small and model-agnostic. It contains no private prompts, personal memory, credentials, customer data, or internal business state.

## Core loop

```
generate -> evaluate -> select -> mutate -> repeat
                     \-> hall of fame
```

A run is built around five concepts:

- **Candidate** — one idea or solution.
- **Evaluator** — returns a numeric fitness score and optional notes.
- **Selector** — decides which candidates survive.
- **Mutator** — produces descendants from survivors.
- **Hall of Fame** — preserves top candidates across generations.

## Why this exists

Single-shot generation often overfits to the first framing of a problem. KODOKU treats generation as a search process instead:

1. Keep multiple competing hypotheses.
2. Preserve diversity instead of averaging everything together.
3. Track ancestry so useful traits can survive across generations.
4. Introduce outside candidates periodically to reduce local convergence.
5. Separate "a candidate won once" from "this pattern is reproducibly strong."

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/neconeco0306/kodoku.git
cd kodoku
python -m pip install -e .
kodoku-demo
```

The demo evolves short product ideas with a deterministic toy evaluator. Replace the evaluator and mutator with your own LLM, market-data, simulation, or human-review adapters.

## Minimal example

```python
from kodoku import Candidate, EvolutionConfig, evolve

seeds = [
    Candidate(text="AI inbox triage for small teams"),
    Candidate(text="Local-first research notebook"),
]

def score(candidate: Candidate) -> float:
    # Replace this with your own evaluator.
    return float(len(set(candidate.text.lower().split())))

result = evolve(
    seeds,
    evaluator=score,
    config=EvolutionConfig(generations=8, population_size=8, survivors=3),
)

for item in result.hall_of_fame[:5]:
    print(item.score, item.text)
```

## Design principles

- **Evidence over vibes** — a single high score is only one observation.
- **Diversity over averaging** — preserve distinct lineages when possible.
- **Reproducibility** — seeded runs should be replayable. Set `deterministic_ids=True` when lineage IDs must also be stable across replays.
- **Inspectable state** — generation history and ancestry stay visible.
- **Replaceable modules** — generation, evaluation, mutation, and selection are swappable.
- **Safe public surface** — secrets and private state do not belong in the repository.

## Roadmap

- Pluggable LLM adapters
- Multi-objective fitness
- Novelty / diversity pressure
- External bloodline injection
- Boundary-search experiments
- Cross-seed evaluation
- Run persistence and replay
- Visualization of lineage trees
- Benchmark harness

## Status

Early experimental release. The API will change.

## License

MIT
