import unittest

from kodoku import (
    EvaluationObservation,
    RobustnessPolicy,
    assess_candidate,
)


def obs(
    evaluator_id,
    group,
    seed,
    score,
    *,
    adversarial=False,
    candidate_id="candidate-a",
):
    return EvaluationObservation(
        candidate_id=candidate_id,
        evaluator_id=evaluator_id,
        independence_group=group,
        seed=seed,
        normalized_score=score,
        adversarial=adversarial,
    )


class RobustnessGateTests(unittest.TestCase):
    def test_repeated_same_model_does_not_fake_independence(self):
        report=assess_candidate([
            obs(f"prompt-{i}","same-model",i,0.9,adversarial=(i==0))
            for i in range(6)
        ])
        self.assertEqual(report.decision,"HOLD")
        self.assertEqual(report.independence_group_count,1)

    def test_promotes_only_when_diverse_checks_agree(self):
        report=assess_candidate([
            obs("a1","model-a",1,0.78),
            obs("a2","model-a",2,0.74),
            obs("b1","model-b",1,0.81),
            obs("b2","model-b",3,0.70),
            obs("c1","human-or-external",2,0.76),
            obs("c2","human-or-external",3,0.69,adversarial=True),
        ])
        self.assertEqual(report.decision,"PROMOTE")
        self.assertEqual(report.independence_group_count,3)
        self.assertEqual(report.seed_count,3)

    def test_large_disagreement_holds_candidate(self):
        report=assess_candidate([
            obs("a","model-a",1,0.95),
            obs("a2","model-a",2,0.92),
            obs("b","model-b",1,0.91),
            obs("b2","model-b",3,0.88),
            obs("c","external",2,0.30,adversarial=True),
            obs("c2","external",3,0.25),
        ])
        self.assertEqual(report.decision,"HOLD")
        self.assertGreater(report.score_spread,RobustnessPolicy().max_score_spread)

    def test_mixed_candidate_ids_fail_closed(self):
        with self.assertRaises(ValueError):
            assess_candidate([
                obs("a","model-a",1,0.8,candidate_id="x"),
                obs("b","model-b",2,0.8,candidate_id="y"),
            ])


if __name__=="__main__":
    unittest.main()
