import json
import tempfile
import unittest
from pathlib import Path
from experiments.protocol_strata import watch

A = "a" * 40
B = "b" * 40

def fake(sha):
    return lambda repo, path: {
        "sha": sha,
        "source_date": "2026-10-01T00:00:00Z",
        "source_url": "https://github.com/" + repo + "/commit/" + sha,
    }

class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
    def tearDown(self):
        self.dir.cleanup()
    def rows(self, path):
        return [json.loads(x) for x in (self.root / "data" / path).read_text().splitlines() if x]
    def test_baseline_not_change(self):
        result = watch.collect(self.root, fake(A), "2026-10-10T01:00:00Z")
        self.assertEqual(result["baseline"], 3)
        self.assertEqual(self.rows("changes.jsonl"), [])
    def test_same_day_dedup_and_transition(self):
        watch.collect(self.root, fake(A), "2026-10-10T01:00:00Z")
        watch.collect(self.root, fake(A), "2026-10-10T02:00:00Z")
        self.assertEqual(len(self.rows("observations.jsonl")), 3)
        result = watch.collect(self.root, fake(B), "2026-10-10T03:00:00Z")
        self.assertEqual(result["changed"], 3)
        self.assertEqual(len(self.rows("changes.jsonl")), 3)
        self.assertEqual(len(self.rows("observations.jsonl")), 6)
        watch.collect(self.root, fake(B), "2026-10-10T04:00:00Z")
        self.assertEqual(len(self.rows("changes.jsonl")), 3)
        self.assertEqual(len(self.rows("observations.jsonl")), 6)
    def test_failed_source_preserves_last_known_sha(self):
        watch.collect(self.root, fake(A), "2026-10-10T01:00:00Z")
        def fail(repo, path):
            raise OSError("secret-value-that-must-not-be-recorded")
        result = watch.collect(self.root, fail, "2026-10-11T01:00:00Z")
        self.assertEqual(result["errors"], 3)
        state = json.loads((self.root / "data" / "state.json").read_text())
        self.assertTrue(all(x["sha"] == A for x in state["sources"].values()))
        self.assertNotIn("secret-value", (self.root / "data" / "observations.jsonl").read_text())
    def test_partial_failure_then_recovery(self):
        watch.collect(self.root, fake(A), "2026-10-10T01:00:00Z")
        def fail_one(repo, path):
            if repo == "a2aproject/A2A":
                raise ValueError("offline")
            return fake(B)(repo, path)
        result = watch.collect(self.root, fail_one, "2026-10-11T01:00:00Z")
        self.assertEqual((result["changed"], result["errors"]), (2, 1))
        result = watch.collect(self.root, fake(B), "2026-10-12T01:00:00Z")
        self.assertEqual(result["changed"], 1)

if __name__ == "__main__":
    unittest.main()
