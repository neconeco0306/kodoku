import unittest

from kodoku import Candidate, EvolutionConfig, evolve


class CoreSmokeTests(unittest.TestCase):
    def test_seeded_run_is_replayable_in_text_and_scores(self):
        seeds=[Candidate(text="alpha beta gamma"),Candidate(text="delta epsilon zeta")]

        def score(candidate):
            return float(len(set(candidate.text.split())))

        config=EvolutionConfig(generations=4,population_size=6,survivors=2,seed=7)
        first=evolve(seeds,evaluator=score,config=config)
        second=evolve(
            [Candidate(text="alpha beta gamma"),Candidate(text="delta epsilon zeta")],
            evaluator=score,
            config=config,
        )

        self.assertEqual(
            [(x.text,x.score) for x in first.hall_of_fame],
            [(x.text,x.score) for x in second.hall_of_fame],
        )

    def test_hall_of_fame_does_not_repeat_same_survivor_across_generations(self):
        seed=Candidate(text="stable candidate",id="stable-id")
        result=evolve(
            [seed],
            evaluator=lambda candidate: 1.0,
            config=EvolutionConfig(
                generations=5,
                population_size=1,
                survivors=1,
                hall_of_fame_size=10,
                seed=11,
            ),
        )

        self.assertEqual([x.id for x in result.hall_of_fame],["stable-id"])

    def test_invalid_config_fails_closed(self):
        with self.assertRaises(ValueError):
            EvolutionConfig(generations=0).validate()

    def test_empty_seed_set_is_rejected(self):
        with self.assertRaises(ValueError):
            evolve([],evaluator=lambda candidate: 0.0)


if __name__=="__main__":
    unittest.main()
