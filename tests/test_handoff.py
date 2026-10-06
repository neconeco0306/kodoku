import unittest

from kodoku.handoff import (
    Claim,
    EvidenceRequest,
    Falsifier,
    FinalistHandoff,
    build_finalist_handoff,
)


def valid_handoff():
    return build_finalist_handoff(
        candidate_id="candidate-1",
        run_fingerprint="run-fingerprint",
        domain="agent reliability",
        summary="Stop high-impact actions when state evidence disagrees.",
        claims=[
            Claim("c1","State-diff checks reduce silent high-impact failures."),
        ],
        falsifiers=[
            Falsifier(
                "c1",
                "failure rate does not improve against a no-check baseline",
                "controlled failure-rate delta",
            ),
        ],
        evidence_requests=[
            EvidenceRequest(
                "c1",
                "agent state diff high impact action failure evaluation",
                ("primary_research","executable_artifact","benchmark_observation"),
            ),
        ],
    )


class HandoffTests(unittest.TestCase):
    def test_valid_handoff_remains_evidence_pending(self):
        handoff=valid_handoff()
        self.assertEqual(handoff.status,"EVIDENCE_PENDING")
        self.assertEqual(handoff.to_dict()["claims"][0]["claim_id"],"c1")

    def test_kodoku_cannot_self_validate(self):
        handoff=valid_handoff()
        with self.assertRaises(ValueError):
            FinalistHandoff(
                candidate_id=handoff.candidate_id,
                run_fingerprint=handoff.run_fingerprint,
                domain=handoff.domain,
                summary=handoff.summary,
                claims=handoff.claims,
                falsifiers=handoff.falsifiers,
                evidence_requests=handoff.evidence_requests,
                status="VALIDATED",
            ).validate()

    def test_every_claim_requires_falsifier(self):
        with self.assertRaises(ValueError):
            build_finalist_handoff(
                candidate_id="candidate-1",
                run_fingerprint="run",
                domain="test",
                summary="summary",
                claims=[Claim("c1","claim")],
                falsifiers=[],
                evidence_requests=[
                    EvidenceRequest("c1","query",("primary_research",)),
                ],
            )

    def test_every_claim_requires_evidence_request(self):
        with self.assertRaises(ValueError):
            build_finalist_handoff(
                candidate_id="candidate-1",
                run_fingerprint="run",
                domain="test",
                summary="summary",
                claims=[Claim("c1","claim")],
                falsifiers=[Falsifier("c1","condition","measurement")],
                evidence_requests=[],
            )


if __name__=="__main__":
    unittest.main()
