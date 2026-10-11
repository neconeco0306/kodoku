import unittest
from datetime import date, timedelta
from experiments.protocol_strata.protocol_health import assess

SOURCE_IDS = ("mcp", "a2a", "agent-skills")
START = date(2026, 10, 9)


def at(day, source, status="ok"):
    record = {"source": source, "status": status, "observed_at": day.isoformat() + "T03:17:00Z"}
    if status == "ok":
        record["sha"] = "a" * 40
    return record


def make_days(number):
    return [at(START + timedelta(days=i), s) for i in range(number) for s in SOURCE_IDS]


class ProtocolHealthTests(unittest.TestCase):
    def test_not_started(self):
        self.assertEqual(assess([], as_of=START)["status"], "NOT_STARTED")

    def test_initial_three_days_are_not_a_month(self):
        r = assess(make_days(3), as_of=START + timedelta(days=2))
        self.assertEqual((r["status"], r["complete_days"], r["days_elapsed"]), ("INCOMPLETE", 3, 3))

    def test_missing_dates_not_counted_as_unchanged(self):
        r = assess(make_days(3), as_of=START + timedelta(days=9))
        self.assertEqual((r["complete_days"], r["missing_days_elapsed"]), (3, 7))

    def test_thirty_day_threshold_is_exact(self):
        r = assess(make_days(25), as_of=START + timedelta(days=29))
        self.assertEqual((r["status"], r["complete_days"], r["missing_days_elapsed"]), ("PASS", 25, 5))
        self.assertEqual(assess(make_days(24), as_of=START + timedelta(days=29))["status"], "FAIL")

    def test_partial_error_does_not_count_as_all_three_success(self):
        rows = [at(START, "mcp"), at(START, "a2a", "error"), at(START, "agent-skills")]
        r = assess(rows, as_of=START)
        self.assertEqual((r["complete_days"], r["error_days_elapsed"]), (0, 1))
        rows.append(at(START, "a2a"))
        self.assertEqual(assess(rows, as_of=START)["complete_days"], 1)

    def test_rejects_wrong_clock_source_status_and_missing_sha(self):
        invalid = [
            {"source": "mcp", "status": "ok", "observed_at": "2026-10-09T03:00:00+09:00", "sha": "a"*40},
            {"source": "typo", "status": "ok", "observed_at": "2026-10-09T03:00:00Z", "sha": "a"*40},
            {"source": "mcp", "status": "ok", "observed_at": "2026-10-09T03:00:00Z"},
            {"source": "mcp", "status": "claim", "observed_at": "2026-10-09T03:00:00Z"},
            {"source": "mcp", "status": "ok", "observed_at": "2026-10-09Z", "sha": "a"*40},
            {"source": "mcp", "status": "ok", "observed_at": "2026-10-09T03:00:00Z", "sha": "not-a-commit"},
        ]
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ValueError):
                assess([item], as_of=START)

    def test_future_observations_do_not_increase_elapsed_days(self):
        r = assess(make_days(30), as_of=START + timedelta(days=2))
        self.assertEqual((r["days_elapsed"], r["complete_days"]), (3, 3))

    def test_as_of_before_first_observation_fails(self):
        with self.assertRaises(ValueError):
            assess(make_days(1), as_of=START - timedelta(days=1))


if __name__ == "__main__":
    unittest.main()
