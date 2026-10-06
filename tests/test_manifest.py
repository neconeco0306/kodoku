import unittest

from kodoku import Candidate
from kodoku.manifest import build_run_manifest, fingerprint_seed_material


class RunManifestTests(unittest.TestCase):
    def test_same_run_inputs_produce_same_fingerprint(self):
        kwargs=dict(
            code_revision="abc123",
            runner_path="experiments/example/run.py",
            config={"population_size":64,"generations":100},
            seed=7,
            evaluator_id="eval-v1",
            mutator_id="mut-v2",
        )
        first=build_run_manifest(
            seeds=[Candidate(text="alpha"),Candidate(text="beta")],
            **kwargs,
        )
        second=build_run_manifest(
            seeds=[Candidate(text="alpha"),Candidate(text="beta")],
            **kwargs,
        )
        self.assertEqual(first.run_fingerprint,second.run_fingerprint)

    def test_evaluator_change_changes_run_fingerprint(self):
        base=dict(
            code_revision="abc123",
            runner_path="runner.py",
            config={"generations":10},
            seed=1,
            seeds=[Candidate(text="alpha")],
            mutator_id="mut-v1",
        )
        first=build_run_manifest(evaluator_id="eval-a",**base)
        second=build_run_manifest(evaluator_id="eval-b",**base)
        self.assertNotEqual(first.run_fingerprint,second.run_fingerprint)

    def test_seed_material_tracks_notes(self):
        first=fingerprint_seed_material([
            Candidate(text="same",notes={"source":"a"}),
        ])
        second=fingerprint_seed_material([
            Candidate(text="same",notes={"source":"b"}),
        ])
        self.assertNotEqual(first,second)

    def test_non_commit_revision_fails_closed(self):
        with self.assertRaises(ValueError):
            build_run_manifest(
                code_revision="latest",
                runner_path="runner.py",
                config={"generations":10},
                seed=1,
                seeds=[Candidate(text="alpha")],
                evaluator_id="eval-v1",
                mutator_id="mut-v1",
            )

    def test_parent_traversal_runner_path_fails_closed(self):
        with self.assertRaises(ValueError):
            build_run_manifest(
                code_revision="abcdef1",
                runner_path="../runner.py",
                config={"generations":10},
                seed=1,
                seeds=[Candidate(text="alpha")],
                evaluator_id="eval-v1",
                mutator_id="mut-v1",
            )

    def test_missing_code_revision_fails_closed(self):
        with self.assertRaises(ValueError):
            build_run_manifest(
                code_revision="",
                runner_path="runner.py",
                config={"generations":10},
                seed=1,
                seeds=[Candidate(text="alpha")],
                evaluator_id="eval-v1",
                mutator_id="mut-v1",
            )


if __name__=="__main__":
    unittest.main()
