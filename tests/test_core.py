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

    def test_deterministic_ids_replay_full_lineage(self):
        def score(candidate):
            return float(len(set(candidate.text.split())))

        config=EvolutionConfig(
            generations=4,
            population_size=6,
            survivors=2,
            seed=7,
            deterministic_ids=True,
        )
        first=evolve(
            [Candidate(text="alpha beta gamma"),Candidate(text="delta epsilon zeta")],
            evaluator=score,
            config=config,
        )
        second=evolve(
            [Candidate(text="alpha beta gamma"),Candidate(text="delta epsilon zeta")],
            evaluator=score,
            config=config,
        )

        def snapshot(result):
            return [
                [(x.id,x.parent_id,x.text,x.score) for x in generation]
                for generation in result.history
            ]

        self.assertEqual(snapshot(first),snapshot(second))

    def test_deterministic_ids_include_candidate_notes(self):
        def score(candidate):
            return 1.0

        config=EvolutionConfig(
            generations=1,
            population_size=2,
            survivors=1,
            seed=3,
            deterministic_ids=True,
        )
        result=evolve(
            [
                Candidate(text="same text",notes={"source":"a"}),
                Candidate(text="same text",notes={"source":"b"}),
            ],
            evaluator=score,
            config=config,
        )

        ids=[candidate.id for candidate in result.final_population]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(len(candidate_id)==20 for candidate_id in ids))

    def test_deterministic_ids_change_with_run_seed(self):
        def score(candidate):
            return 1.0

        first=evolve(
            [Candidate(text="same seed")],
            evaluator=score,
            config=EvolutionConfig(
                generations=1,
                population_size=1,
                survivors=1,
                seed=1,
                deterministic_ids=True,
            ),
        )
        second=evolve(
            [Candidate(text="same seed")],
            evaluator=score,
            config=EvolutionConfig(
                generations=1,
                population_size=1,
                survivors=1,
                seed=2,
                deterministic_ids=True,
            ),
        )

        self.assertNotEqual(first.final_population[0].id,second.final_population[0].id)

    def test_invalid_config_fails_closed(self):
        with self.assertRaises(ValueError):
            EvolutionConfig(generations=0).validate()

    def test_empty_seed_set_is_rejected(self):
        with self.assertRaises(ValueError):
            evolve([],evaluator=lambda candidate: 0.0)


if __name__=="__main__":
    unittest.main()
