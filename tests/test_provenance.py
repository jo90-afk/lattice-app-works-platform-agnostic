from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from lifecycle import review_action, submit_action  # noqa: E402
from provenance import claim_provenance, completion_provenance  # noqa: E402
from state_engine import StateStore  # noqa: E402


class ProvenanceTest(unittest.TestCase):
    def test_submission_telemetry_keeps_host_workspace_and_artifact_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with StateStore(ROOT, folder / "state.db", folder / "current.json") as store:
                store.ensure_project("project-001", "Provenance Project")
                store.add_objective(
                    "project-001", "Trace output", "Associate output with execution identity.",
                    "product", objective_id="objective-001",
                )
                store.add_milestone(
                    "project-001", "objective-001", "Output verified", 1, True,
                    milestone_id="milestone-001",
                )
                store.add_condition(
                    "project-001", "objective-001", "milestone-001", "output.traced",
                    "Output is traced", "Submit traceable output.",
                    "application", "quality", "director", condition_id="condition-001",
                )
                claimed = claim_for_host_atomic(
                    store,
                    project_id="project-001",
                    role="application",
                    actor="builder-7",
                    host="codex",
                    workspace_id="worktree-42",
                )
                submitted = submit_action(
                    store,
                    claimed["lease_id"],
                    "application",
                    "Built",
                    ["artifact://bundle/123"],
                    "evidence://build/123",
                )
                payload = submitted["lifecycle"]["payload"]
                self.assertEqual(payload["actor"], "builder-7")
                self.assertEqual(payload["host"], "codex")
                self.assertEqual(payload["workspace_id"], "worktree-42")
                self.assertEqual(payload["artifact_refs"], ["artifact://bundle/123"])
                self.assertEqual(payload["evidence_ref"], "evidence://build/123")

                claim = claim_provenance(store, claimed["lease_id"])
                self.assertEqual(claim["workspace_id"], "worktree-42")
                completion = completion_provenance(store, claimed["lease_id"])
                self.assertEqual(completion["completion_event"], "action_submitted")
                self.assertEqual(
                    completion["completion_payload"]["artifact_refs"],
                    ["artifact://bundle/123"],
                )

    def test_verification_evidence_retains_verifier_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with StateStore(ROOT, folder / "state.db", folder / "current.json") as store:
                store.ensure_project("project-001", "Verification Provenance")
                store.add_objective(
                    "project-001", "Trace verification", "Keep verifier execution identity.",
                    "product", objective_id="objective-001",
                )
                store.add_milestone(
                    "project-001", "objective-001", "Verified", 1, True,
                    milestone_id="milestone-001",
                )
                store.add_condition(
                    "project-001", "objective-001", "milestone-001", "verify.traced",
                    "Verification traced", "Verify independently.",
                    "application", "quality", "director", condition_id="condition-001",
                )
                author = claim_for_host_atomic(
                    store, project_id="project-001", role="application",
                    actor="builder", host="local", workspace_id="author-ws",
                )
                submit_action(store, author["lease_id"], "application", "Built", [])
                verifier = claim_for_host_atomic(
                    store, project_id="project-001", role="quality",
                    actor="verifier", host="github", workspace_id="review-ws",
                )
                reviewed = review_action(
                    store, verifier["lease_id"], "quality", "SATISFIED", "Verified",
                    "evidence://review/1",
                )
                payload = reviewed["lifecycle"]["payload"]
                self.assertEqual(payload["host"], "github")
                self.assertEqual(payload["workspace_id"], "review-ws")
                self.assertEqual(payload["evidence_ref"], "evidence://review/1")


if __name__ == "__main__":
    unittest.main()
