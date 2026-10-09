# PROTOCOL STRATA / Independent Node 001

This is an independent, low-cost, long-horizon observation experiment. The collector tracks **official public AI protocol revisions**, rather than making AI products or buying speculative domain names.

Sources: MCP schema in modelcontextprotocol/modelcontextprotocol; A2A specification in a2aproject/A2A; Agent Skills specification in agentskills/agentskills. Exact watched paths are in watch.py.

## Operation

Run from the KODOKU repository root:

    python3 -m unittest discover -s experiments/protocol_strata/tests -v
    python3 experiments/protocol_strata/watch.py

The standalone GitHub Actions workflow runs at 03:17 UTC daily (12:17 JST), and can be manually dispatched. It needs no new domain, hardware, user API key, or paid platform.

Records:
- data/observations.jsonl: UTC-dated samples, including errors.
- data/changes.jsonl: first observed transitions between commit fingerprints (not the initial baseline).
- data/state.json: latest successful observation per protocol.
- STATUS.md: current report.

## Critical limitations

- A latest-commit SHA transition is not proof of a semantic or breaking specification change.
- The upstream commit timestamp is not the time the observer first saw that change.
- Only the latest commit touching each specified source path is sampled. Changes and reversions between daily checks can be missed.
- Upstream Git history can be rewritten, and watched paths can move.
- Source/API errors do not update prior known-good fingerprints.
- The observer records public source metadata, not full copyrighted document bodies or private user data.
- GitHub is a single infrastructure dependency. Scheduled jobs can be delayed or disabled due to repository inactivity, so missing dates must not be interpreted as unchanged history.
- Public data alone does not provide exclusive ownership or guaranteed economic value.

## 30-day continuation gate

Keep it only if at least 25 days have successful checks, no path failures went unnoticed, source revision signals are interpretable, and there is independent use for the resulting history. Do not buy servers or domains for this without evidence.
