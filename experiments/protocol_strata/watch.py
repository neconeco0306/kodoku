"""Observe revisions to official public AI agent specifications (stdlib only)."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
SOURCES = (
    ("mcp", "modelcontextprotocol/modelcontextprotocol", "schema"),
    ("a2a", "a2aproject/A2A", "specification"),
    ("agent-skills", "agentskills/agentskills", "docs/specification.mdx"),
)

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def fetch_commit(repo, path):
    url = "https://api.github.com/repos/" + repo + "/commits?" + urlencode({"path": path, "per_page": 1})
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nilo-protocol-strata/0.1"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urlopen(Request(url, headers=headers), timeout=15) as response:
        raw = response.read(262145)
    if len(raw) > 262144:
        raise ValueError("Oversized API response")
    response = json.loads(raw)
    if not isinstance(response, list) or not response:
        raise ValueError("Missing upstream path")
    item = response[0]
    sha = item["sha"]
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Unexpected revision fingerprint")
    return {"sha": sha, "source_date": item["commit"]["committer"]["date"],
            "source_url": "https://github.com/" + repo + "/commit/" + sha}

def read_json(path, default):
    return json.loads(path.read_text("utf-8")) if path.exists() else default

def read_rows(path):
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line] if path.exists() else []

def write(path, content):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(content, "utf-8")
    temp.replace(path)

def collect(root=HERE, fetcher=fetch_commit, at=None):
    at = at or now()
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    state_file, readings_file, changes_file = (data / n for n in ("state.json", "observations.jsonl", "changes.jsonl"))
    state = read_json(state_file, {"version": 1, "sources": {}})
    readings = read_rows(readings_file)
    changes = read_rows(changes_file)
    counts = {"baseline": 0, "changed": 0, "unchanged": 0, "errors": 0}
    for sid, repo, path in SOURCES:
        record = {"source": sid, "repository": repo, "path": path, "observed_at": at}
        try:
            found = fetcher(repo, path)
            record.update(found)
            record["status"] = "ok"
            prev = state["sources"].get(sid)
            if not prev:
                counts["baseline"] += 1
                state["sources"][sid] = {**found, "first_seen": at, "last_seen": at, "transitions": 0}
            elif prev["sha"] != found["sha"]:
                counts["changed"] += 1
                changes.append({**record, "previous_sha": prev["sha"]})
                state["sources"][sid] = {**found, "first_seen": prev["first_seen"],
                                          "last_seen": at, "transitions": prev["transitions"] + 1}
            else:
                counts["unchanged"] += 1
                prev["last_seen"] = at
        except (OSError, KeyError, TypeError, ValueError) as exc:
            counts["errors"] += 1
            record.update(status="error", error_type=type(exc).__name__)
        # Same-day repeated identical observations are not duplicated, including retries.
        fingerprint = lambda r: (r["observed_at"][:10], r["source"], r["status"], r.get("sha"), r.get("error_type"))
        if not any(fingerprint(r) == fingerprint(record) for r in readings):
            readings.append(record)
    write(state_file, json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write(readings_file, "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in readings))
    write(changes_file, "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in changes))
    report = ["# PROTOCOL STRATA", "", "Source revisions, not semantic changes. First observations are baselines, not transitions.",
              "Observation timestamps are not upstream commit dates. Fetch failures are not proof of stability.", "",
              "| Protocol | Last source revision | Source commit date (UTC) | Observed transitions |",
              "|---|---|---|---:|"]
    for sid, repo, path in SOURCES:
        s = state["sources"].get(sid)
        report.append(f"| {sid} | [{s['sha'][:12]}]({s['source_url']}) | {s['source_date']} | {s['transitions']} |" if s else f"| {sid} | NOT_OBSERVED | — | — |")
    report += ["", "Last attempted observation (UTC): " + at, "",
               "Only the latest GitHub commit touching the watched path is checked each day.",
               "Intermediate changes can be missed. Upstream rename, API downtime, and history rewrites need investigation.", ""]
    write(root / "STATUS.md", "\n".join(report))
    return counts

if __name__ == "__main__":
    outcome = collect()
    print(json.dumps(outcome))
    if outcome["errors"]:
        raise SystemExit(1)
