from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .core import Candidate


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def fingerprint_seed_material(seeds: Iterable[Candidate]) -> str:
    payload = [
        {
            "text": candidate.text,
            "parent_id": candidate.parent_id,
            "notes": dict(sorted(candidate.notes.items())),
        }
        for candidate in seeds
    ]
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class RunManifest:
    schema_version: str
    code_revision: str
    runner_path: str
    config_json: str
    seed: int
    seed_material_sha256: str
    evaluator_id: str
    mutator_id: str

    def validate(self) -> None:
        for name, value in (
            ("schema_version", self.schema_version),
            ("code_revision", self.code_revision),
            ("runner_path", self.runner_path),
            ("seed_material_sha256", self.seed_material_sha256),
            ("evaluator_id", self.evaluator_id),
            ("mutator_id", self.mutator_id),
        ):
            if not str(value).strip():
                raise ValueError(f"{name} is required")

        try:
            parsed = json.loads(self.config_json)
        except json.JSONDecodeError as exc:
            raise ValueError("config_json must be valid JSON") from exc

        if _canonical_json(parsed) != self.config_json:
            raise ValueError("config_json must use canonical JSON encoding")

    @property
    def run_fingerprint(self) -> str:
        self.validate()
        payload = {
            "schema_version": self.schema_version,
            "code_revision": self.code_revision,
            "runner_path": self.runner_path,
            "config_json": self.config_json,
            "seed": self.seed,
            "seed_material_sha256": self.seed_material_sha256,
            "evaluator_id": self.evaluator_id,
            "mutator_id": self.mutator_id,
        }
        return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_run_manifest(
    *,
    code_revision: str,
    runner_path: str,
    config: Mapping[str, Any],
    seed: int,
    seeds: Iterable[Candidate],
    evaluator_id: str,
    mutator_id: str,
    schema_version: str = "1",
) -> RunManifest:
    seed_list = list(seeds)
    manifest = RunManifest(
        schema_version=schema_version,
        code_revision=code_revision,
        runner_path=runner_path,
        config_json=_canonical_json(dict(config)),
        seed=seed,
        seed_material_sha256=fingerprint_seed_material(seed_list),
        evaluator_id=evaluator_id,
        mutator_id=mutator_id,
    )
    manifest.validate()
    return manifest
