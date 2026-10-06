from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    text: str

    def validate(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id is required")
        if not self.text.strip():
            raise ValueError("claim text is required")


@dataclass(frozen=True, slots=True)
class Falsifier:
    claim_id: str
    condition: str
    measurement: str

    def validate(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("falsifier claim_id is required")
        if not self.condition.strip():
            raise ValueError("falsifier condition is required")
        if not self.measurement.strip():
            raise ValueError("falsifier measurement is required")


@dataclass(frozen=True, slots=True)
class EvidenceRequest:
    claim_id: str
    query: str
    required_evidence_roles: tuple[str, ...]

    def validate(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("evidence request claim_id is required")
        if not self.query.strip():
            raise ValueError("evidence request query is required")
        if not self.required_evidence_roles:
            raise ValueError("at least one required_evidence_role is required")
        if any(not role.strip() for role in self.required_evidence_roles):
            raise ValueError("required_evidence_roles cannot contain blanks")


@dataclass(frozen=True, slots=True)
class FinalistHandoff:
    candidate_id: str
    run_fingerprint: str
    domain: str
    summary: str
    claims: tuple[Claim, ...]
    falsifiers: tuple[Falsifier, ...]
    evidence_requests: tuple[EvidenceRequest, ...]
    status: str = "EVIDENCE_PENDING"

    def validate(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id is required")
        if not self.run_fingerprint.strip():
            raise ValueError("run_fingerprint is required")
        if not self.domain.strip():
            raise ValueError("domain is required")
        if not self.summary.strip():
            raise ValueError("summary is required")
        if self.status != "EVIDENCE_PENDING":
            raise ValueError(
                "KODOKU handoffs must remain EVIDENCE_PENDING; "
                "validation belongs downstream"
            )
        if not self.claims:
            raise ValueError("at least one claim is required")

        for claim in self.claims:
            claim.validate()
        for falsifier in self.falsifiers:
            falsifier.validate()
        for request in self.evidence_requests:
            request.validate()

        claim_ids = [claim.claim_id for claim in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("claim_id values must be unique")

        known = set(claim_ids)
        falsified = {item.claim_id for item in self.falsifiers}
        requested = {item.claim_id for item in self.evidence_requests}

        unknown_falsifiers = falsified - known
        unknown_requests = requested - known
        if unknown_falsifiers:
            raise ValueError("falsifiers reference unknown claim_id values")
        if unknown_requests:
            raise ValueError("evidence requests reference unknown claim_id values")

        missing_falsifiers = known - falsified
        missing_requests = known - requested
        if missing_falsifiers:
            raise ValueError("every claim requires at least one falsifier")
        if missing_requests:
            raise ValueError("every claim requires at least one evidence request")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


def build_finalist_handoff(
    *,
    candidate_id: str,
    run_fingerprint: str,
    domain: str,
    summary: str,
    claims: Iterable[Claim],
    falsifiers: Iterable[Falsifier],
    evidence_requests: Iterable[EvidenceRequest],
) -> FinalistHandoff:
    handoff = FinalistHandoff(
        candidate_id=candidate_id,
        run_fingerprint=run_fingerprint,
        domain=domain,
        summary=summary,
        claims=tuple(claims),
        falsifiers=tuple(falsifiers),
        evidence_requests=tuple(evidence_requests),
    )
    handoff.validate()
    return handoff
