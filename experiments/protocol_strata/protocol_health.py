"""Read-only 30-day availability measure for PROTOCOL STRATA observations.

A successful observation is NOT a meaningful upstream protocol change, and
availability alone is NOT evidence of product-market fit.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path

SOURCES = frozenset({"mcp", "a2a", "agent-skills"})
WINDOW_DAYS = 30
REQUIRED_GOOD_DAYS = 25


def _utc_date(value: str) -> date:
    if not isinstance(value, str) or "T" not in value or not value.endswith("Z"):
        raise ValueError("observed_at must be a UTC ISO-8601 timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid observed_at") from exc
    if parsed.tzinfo != timezone.utc:
        raise ValueError("observed_at must be UTC")
    return parsed.date()


def assess(rows: list[dict], *, as_of: date) -> dict:
    """Assess the fixed first 30 UTC days; never count missing as unchanged.

    A successful retry on a UTC date can recover from an earlier recorded
    failure. Unknown/malformed records make the assessment fail closed.
    """
    observed: dict[date, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("observation must be an object")
        source = row.get("source")
        status = row.get("status")
        if source not in SOURCES or status not in {"ok", "error"}:
            raise ValueError("unknown source/status in observation")
        day = _utc_date(row.get("observed_at"))
        if status == "ok":
            sha = row.get("sha")
            if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
                raise ValueError("successful observation has invalid revision")
        observed[day][source].add(status)
    if not observed:
        return {
            "status": "NOT_STARTED", "days_elapsed": 0, "window_days": WINDOW_DAYS,
            "complete_days": 0, "missing_days_elapsed": 0, "error_days_elapsed": 0,
            "window_start": None, "window_end": None,
            "note": "No observations. Cannot infer protocol stability.",
        }

    start = min(observed)
    end = start + timedelta(days=WINDOW_DAYS - 1)
    if as_of < start:
        raise ValueError("as_of precedes first recorded observation")
    elapsed = min(WINDOW_DAYS, (as_of - start).days + 1)
    complete = missing = errors = 0
    for day_index in range(elapsed):
        statuses = observed[start + timedelta(days=day_index)]
        if all("ok" in statuses.get(source, ()) for source in SOURCES):
            complete += 1
        elif any("error" in statuses.get(source, ()) for source in SOURCES):
            errors += 1
        else:
            missing += 1
    # An error on a day that is later successfully retried does not cause
    # that day's availability to fail, but remains in the raw audit records.
    status = "INCOMPLETE" if elapsed < WINDOW_DAYS else (
        "PASS" if complete >= REQUIRED_GOOD_DAYS else "FAIL"
    )
    return {
        "status": status, "window_start": start.isoformat(),
        "window_end": end.isoformat(), "days_elapsed": elapsed,
        "window_days": WINDOW_DAYS, "complete_days": complete,
        "missing_days_elapsed": missing, "error_days_elapsed": errors,
        "required_complete_days": REQUIRED_GOOD_DAYS,
        "note": "Availability only; independent downstream use and business value are unverified.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=Path, default=Path(__file__).parent / "data/observations.jsonl")
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    args = parser.parse_args()
    try:
        rows = [json.loads(line) for line in args.observations.read_text("utf-8").splitlines() if line.strip()]
        report = assess(rows, as_of=args.as_of)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"protocol-health NOT_VERIFIED: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
