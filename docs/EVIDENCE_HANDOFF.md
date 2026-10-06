# KODOKU -> evidence handoff

A KODOKU finalist is a search result, not a verified discovery.

Before a finalist can leave search, create a `FinalistHandoff` that binds the candidate to its reproducible run fingerprint and decomposes the idea into explicit claims.

Every claim must include:

- at least one falsifier: what observation would count against the claim,
- at least one evidence request: what should be retrieved and what evidence roles are acceptable.

KODOKU is only allowed to emit `EVIDENCE_PENDING`.

It must not emit `VALIDATED`, `PROVEN`, or an equivalent truth state. External retrieval can be handled by POLYMATH LAB 1; criticism/replication and downstream safety/evidence gates remain separate.

Intended flow:

`KODOKU finalist -> EVIDENCE_PENDING -> POLYMATH source intake -> independent critique / validation -> NILO-CHECKS or domain gate -> SECOND/Nilo execution`
