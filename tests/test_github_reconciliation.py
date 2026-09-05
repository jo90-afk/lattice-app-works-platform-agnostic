from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lattice
from github_reconciliation import check_github_state, reconcile_github_state
from state_engine import LatticeError, StateStore, json_text

REPO = "example/product"
API = "https://api.github.com/repos/" + REPO
WEB = "https://github.com/" + REPO
NOW = datetime(2026, 9, 4, 20, tzinfo=timezone.utc)
A, B, C = "a" * 40, "b" * 40, "c" * 40


def tracking(kind="pull_request", identifier=7, status="active"):
    return {"format": "lattice-github-tracking", "version": 1, "repository": REPO,
            "declarations": [{"kind": kind, "id": identifier, "status": status,
                              "source_ref": "projects/product/PROJECT.md"}]}


def pull_capture(state="closed", merged=True):
    return {"url": API + "/pulls/7", "status": 200, "data": {
        "url": API + "/pulls/7", "html_url": WEB + "/pull/7", "number": 7,
        "base": {"sha": A, "ref": "main", "repo": {"full_name": REPO}},
        "head": {"sha": B, "ref": "feature", "repo": {"full_name": "contributor/fork"}},
        "state": state, "merged": merged, "merge_commit_sha": C if merged else None,
        "updated_at": "2026-09-04T18:00:00Z", "merged_at": "2026-09-04T17:00:00Z" if merged else None}}


def release_capture(draft=False):
    return {"url": API + "/releases/tags/v0.1.0-rc.4", "status": 200, "data": {
        "id": 9, "tag_name": "v0.1.0-rc.4", "url": API + "/releases/9",
        "html_url": WEB + "/releases/tag/v0.1.0-rc.4", "draft": draft, "prerelease": True,
        "target_commitish": "main", "published_at": None if draft else "2026-09-04T17:00:00Z"}}


def comparison(ahead=0, behind=3):
    status = "diverged" if ahead and behind else "ahead" if ahead else "behind" if behind else "identical"
    return {"url": API + "/compare/" + A + "..." + B, "status": 200,
            "data": {"base_commit": {"sha": A}, "ahead_by": ahead, "behind_by": behind,
                     "status": status, "html_url": WEB + "/compare/" + A + "..." + B}}


def observations(*captures, captured_at="2026-09-04T19:00:00Z"):
    return {"format": "lattice-github-observations", "version": 1, "repository": REPO,
            "captured_at": captured_at, "responses": list(captures or [pull_capture()])}


class GitHubCheckTest(unittest.TestCase):
    def check(self, declared=None, captured=None):
        return check_github_state(declared or tracking(), captured or observations(), now=NOW)

    def test_merged_active_pr_is_unresolved_without_acceptance(self):
        report = self.check()
        self.assertEqual(report["unresolved"], ["pull_request:7"])
        self.assertEqual(report["items"][0]["observed"], "merged")
        self.assertEqual(report["items"][0]["finding"], "declared_state_drift")
        self.assertFalse(report["acceptance_changed"])
        self.assertFalse(report["publication_authorized"])

    def test_published_release_contradicts_pending_declaration(self):
        report = self.check(tracking("release", "v0.1.0-rc.4", "pending"), observations(release_capture()))
        self.assertEqual(report["items"][0]["observed"], "published")
        self.assertEqual(report["unresolved"], ["release:v0.1.0-rc.4"])
        self.assertFalse(report["publication_authorized"])
        self.assertTrue(report["items"][0]["facts"]["prerelease"])

    def test_draft_release_remains_pending(self):
        report = self.check(tracking("release", "v0.1.0-rc.4", "pending"), observations(release_capture(True)))
        self.assertEqual(report["unresolved"], [])

    def test_closed_unmerged_pr_does_not_become_merged(self):
        report = self.check(captured=observations(pull_capture("closed", False)))
        self.assertEqual(report["items"][0]["observed"], "closed")

    def test_zero_ahead_open_pr_is_only_a_supersession_candidate(self):
        report = self.check(captured=observations(pull_capture("open", False), comparison()))
        self.assertEqual(report["items"][0]["observed"], "active")
        self.assertEqual(report["items"][0]["finding"], "supersession_candidate")
        self.assertEqual(report["items"][0]["attention"], "frontier")

    def test_integration_branch_can_supersede_an_old_stacked_pr(self):
        declared = tracking()
        declared["integration_branch"] = "main"
        branch = {"url": API + "/branches/main", "status": 200, "data": {
            "name": "main", "commit": {"sha": C, "url": API + "/commits/" + C}}}
        compare = json.loads(json.dumps(comparison()).replace(A, C))
        report = self.check(declared, observations(pull_capture("open", False), branch, compare))
        self.assertEqual(report["items"][0]["finding"], "supersession_candidate")
        self.assertEqual(report["items"][0]["facts"]["comparison_base_sha"], C)
        self.assertEqual(report["items"][0]["facts"]["base_sha"], A)
        with self.assertRaisesRegex(LatticeError, "Missing GitHub evidence"):
            self.check(declared, observations(pull_capture("open", False), compare))
        branch["data"]["commit"]["url"] = "https://api.github.com/repos/example/other/commits/" + C
        with self.assertRaises(LatticeError):
            self.check(declared, observations(pull_capture("open", False), branch, compare))

    def test_superseded_declaration_has_history_and_requires_a_reason(self):
        declared = tracking(status="superseded")
        with self.assertRaisesRegex(LatticeError, "supersession reason"):
            self.check(declared)
        declared["declarations"][0]["reason"] = "The current main implementation incorporates this work."
        report = self.check(declared, observations(pull_capture("open", False), comparison()))
        self.assertEqual(report["unresolved"], [])
        self.assertEqual(report["items"][0]["attention"], "historical")
        self.assertEqual(report["items"][0]["observed"], "active")

    def test_cross_repository_and_inconsistent_identity_fail_closed(self):
        mutations = [
            lambda e: e.update(repository="example/other"),
            lambda e: e["responses"][0].update(url="https://api.github.com/repos/example/other/pulls/7"),
            lambda e: e["responses"][0]["data"]["base"]["repo"].update(full_name="example/other"),
            lambda e: e["responses"][0]["data"].update(html_url=WEB + "/pull/8"),
            lambda e: e["responses"][0]["data"].update(url=API + "/pulls/8"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                capture = observations()
                mutate(capture)
                with self.assertRaises(LatticeError):
                    self.check(captured=capture)

    def test_freshness_timezone_and_source_chronology_fail_closed(self):
        for timestamp in ["2026-09-02T00:00:00Z", "2026-09-05T00:00:00Z", "2026-09-04T19:00:00", "yesterday", "2026-09-04T16:00:00Z"]:
            with self.subTest(timestamp=timestamp), self.assertRaises(LatticeError):
                self.check(captured=observations(captured_at=timestamp))

    def test_malformed_missing_denied_and_extra_evidence_fail_closed(self):
        mutations = [
            lambda e: e.update(responses=[]),
            lambda e: e.update(acceptance=True),
            lambda e: e.update(version=True),
            lambda e: e["responses"][0].update(status=403),
            lambda e: e["responses"][0].update(status=404),
            lambda e: e["responses"][0]["data"].update(merged="true"),
            lambda e: e["responses"][0]["data"].update(state=[]),
            lambda e: e["responses"][0]["data"].update(merged_at=None),
            lambda e: e["responses"][0]["data"]["head"].update(sha="main"),
            lambda e: e["responses"].append(copy.deepcopy(e["responses"][0])),
            lambda e: e["responses"].append(release_capture()),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                capture = observations()
                mutate(capture)
                with self.assertRaises(LatticeError):
                    self.check(captured=capture)

    def test_comparison_binds_the_observed_base_and_head(self):
        for mutate in [lambda c: c["data"]["base_commit"].update(sha=C),
                       lambda c: c["data"].update(html_url=WEB + "/compare/main...feature"),
                       lambda c: c["data"].update(ahead_by=-1),
                       lambda c: c["data"].update(ahead_by=True),
                       lambda c: c["data"].update(status="ahead")]:
            capture = comparison()
            mutate(capture)
            with self.subTest(mutation=mutate), self.assertRaises(LatticeError):
                self.check(captured=observations(pull_capture("open", False), capture))

    def test_inconsistent_release_evidence_cannot_claim_publication(self):
        for change in [{"published_at": None}, {"draft": "false"}, {"prerelease": 1},
                       {"url": "https://api.github.com/repos/example/other/releases/9"},
                       {"tag_name": "v0.1.0-rc.3"}]:
            capture = release_capture()
            capture["data"].update(change)
            with self.subTest(change=change), self.assertRaises(LatticeError):
                self.check(tracking("release", "v0.1.0-rc.4", "pending"), observations(capture))

    def test_duplicate_and_unauthorized_declarations_fail_closed(self):
        for mutate in [lambda d: d["declarations"].append(copy.deepcopy(d["declarations"][0])),
                       lambda d: d["declarations"][0].update(status="accepted"),
                       lambda d: d["declarations"][0].update(status=[]),
                       lambda d: d["declarations"][0].update(acceptance=True)]:
            declared = tracking()
            mutate(declared)
            with self.subTest(mutation=mutate), self.assertRaises(LatticeError):
                self.check(declared)

    def test_check_cli_has_exit_codes_and_does_not_open_a_state_store(self):
        with tempfile.TemporaryDirectory() as folder:
            d, e = Path(folder) / "declarations.json", Path(folder) / "observations.json"
            e.write_text(json.dumps(observations()), encoding="utf-8")
            for declared, expected in [(tracking(), 1), (tracking(status="merged"), 0)]:
                d.write_text(json.dumps(declared), encoding="utf-8")
                args = ["lattice", "github-check", "--declarations", str(d), "--observations", str(e)]
                with patch.object(sys, "argv", args), patch.object(lattice, "StateStore", side_effect=AssertionError("must not open state")), patch("github_reconciliation.datetime") as clock, contextlib.redirect_stdout(io.StringIO()):
                    clock.now.return_value = NOW
                    clock.fromisoformat.side_effect = datetime.fromisoformat
                    self.assertEqual(lattice.main(), expected)


class GitHubReconcileTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        folder = Path(self.temp.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.store.ensure_project("product", "Example product")
        self.store.add_objective("product", "Deliver", "A bounded increment", "product", objective_id="objective")
        self.store.add_milestone("product", "objective", "Ready", 1, True, milestone_id="milestone")
        self.declared = tracking()
        self.record()

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def record(self):
        return self.store.put_record("product", "github.tracking", "contract", "GitHub transport declarations",
                                     json_text(self.declared), "director", "director")

    def reconcile(self, envelope=None, revision=None, role="director", project="product"):
        return reconcile_github_state(self.store, project_id=project, envelope=envelope or observations(),
                                     expected_revision=self.store.project_revision(project) if revision is None else revision,
                                     role=role, now=NOW)

    def test_uses_truth_history_without_accepting_milestone_or_publication(self):
        result = self.reconcile()
        self.assertEqual(result["truth"]["epistemic_status"], "contested")
        self.assertEqual(result["truth"]["attention_state"], "frontier")
        self.assertEqual(self.store.conn.execute("SELECT status FROM milestones WHERE id = 'milestone'").fetchone()[0], "active")
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0], 0)
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0], 0)
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM commitments").fetchone()[0], 0)
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM exceptions").fetchone()[0], 0)

    def test_exact_retry_is_idempotent_with_old_revision(self):
        original_revision = self.store.project_revision("product")
        first = self.reconcile(revision=original_revision)
        revision = self.store.revision
        replay = self.reconcile(revision=original_revision)
        self.assertTrue(replay["replayed"])
        self.assertEqual(first["truth"]["id"], replay["truth"]["id"])
        self.assertEqual(revision, self.store.revision)
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM truth_versions").fetchone()[0], 1)

    def test_stale_revision_and_malformed_observation_leave_snapshot_unchanged(self):
        self.reconcile()
        previous = self.store.snapshot_path.read_bytes()
        fresh = observations(captured_at="2026-09-04T19:30:00Z")
        with self.assertRaisesRegex(LatticeError, "expected project revision"):
            self.reconcile(fresh, revision=0)
        bad = copy.deepcopy(fresh)
        bad["responses"][0]["data"]["base"]["repo"]["full_name"] = "example/other"
        with self.assertRaises(LatticeError):
            self.reconcile(bad)
        self.assertEqual(previous, self.store.snapshot_path.read_bytes())

    def test_director_updates_declaration_then_fresh_observation_retires_drift(self):
        first = self.reconcile()
        self.declared["declarations"][0]["status"] = "merged"
        self.record()
        second = self.reconcile(observations(captured_at="2026-09-04T19:30:00Z"))
        self.assertEqual(second["report"]["unresolved"], [])
        self.assertEqual(second["truth"]["attention_state"], "background")
        self.assertEqual(second["truth"]["epistemic_status"], "observed")
        self.assertEqual(second["truth"]["id"], first["truth"]["id"])
        self.assertEqual(second["truth"]["version"], 2)
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM truth_versions").fetchone()[0], 2)
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM record_versions").fetchone()[0], 2)
        self.assertEqual(self.store.conn.execute("SELECT to_attention FROM truth_transitions").fetchone()[0], "background")

    def test_unresolved_earlier_item_is_not_dropped_when_another_is_settled(self):
        self.declared["declarations"].append(tracking("release", "v0.1.0-rc.4", "published")["declarations"][0])
        self.record()
        result = self.reconcile(observations(pull_capture(), release_capture()))
        self.assertEqual(result["report"]["unresolved"], ["pull_request:7"])
        self.assertEqual(result["truth"]["attention_state"], "frontier")

    def test_milestone_acceptance_cannot_background_unresolved_drift(self):
        truth = self.reconcile()["truth"]
        self.store.add_condition("product", "objective", "milestone", "other", "Verified", "Unrelated work verified",
                                 "application", "quality", "director", truth_ids=[truth["id"]])
        lease = self.store.claim("product", "application", "builder")
        self.store.submit(lease["lease_id"], "application", "Built", ["artifact://product/result"])
        reviewer = self.store.claim("product", "quality", "reviewer")
        self.store.review(reviewer["lease_id"], "quality", "SATISFIED", "Verified")
        assurance = self.store.claim("product", "assurance", "assurance")
        self.store.advance_milestone(assurance["lease_id"], "assurance", "Unrelated milestone complete")
        self.assertEqual(self.store.conn.execute("SELECT attention_state FROM truths WHERE id = ?", (truth["id"],)).fetchone()[0], "frontier")

    def test_linked_condition_remains_frontier_and_is_invalidated(self):
        first = self.reconcile()
        self.store.add_condition("product", "objective", "milestone", "condition", "Verified", "Behavior verified",
                                 "application", "quality", "director", truth_ids=[first["truth"]["id"]], condition_id="condition")
        lease = self.store.claim("product", "application", "builder")
        self.store.submit(lease["lease_id"], "application", "Built", ["artifact://product/result"])
        reviewer = self.store.claim("product", "quality", "reviewer")
        self.store.review(reviewer["lease_id"], "quality", "SATISFIED", "Verified")
        self.declared["declarations"][0]["status"] = "merged"
        self.record()
        result = self.reconcile(observations(captured_at="2026-09-04T19:30:00Z"))
        self.assertEqual(result["truth"]["attention_state"], "frontier")
        self.assertEqual(self.store.conn.execute("SELECT status FROM conditions WHERE id = 'condition'").fetchone()[0], "unknown")
        self.assertFalse(self.store.readiness("product")["ready"])

    def test_cross_project_observations_cannot_borrow_binding_or_truth(self):
        self.reconcile()
        self.store.ensure_project("other", "Other")
        with self.assertRaisesRegex(LatticeError, "github.tracking"):
            self.reconcile(project="other")
        other = tracking()
        other["repository"] = "example/other"
        self.store.put_record("other", "github.tracking", "contract", "Other GitHub", json_text(other), "director", "director")
        with self.assertRaisesRegex(LatticeError, "Cross-repository"):
            self.reconcile(project="other")
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM truths WHERE project_id = 'other'").fetchone()[0], 0)

    def test_rebinding_a_repository_cannot_rewrite_existing_external_truth(self):
        self.reconcile()
        self.declared["repository"] = "example/other"
        self.record()
        capture = json.loads(json.dumps(observations(captured_at="2026-09-04T19:30:00Z")).replace(REPO, "example/other"))
        with self.assertRaisesRegex(LatticeError, "binding cannot be reassigned"):
            self.reconcile(capture)

    def test_role_and_manual_truth_status_are_not_overridden(self):
        for role in ["application", "quality", "assurance", "principal", "unknown"]:
            with self.subTest(role=role), self.assertRaisesRegex(LatticeError, "Only the Director"):
                self.reconcile(role=role)
        truth = self.reconcile()["truth"]
        self.store.revise_truth(truth["id"], "product", "Questioned source", epistemic_status="contested")
        with self.assertRaisesRegex(LatticeError, "manual status"):
            self.reconcile(observations(captured_at="2026-09-04T19:30:00Z"))

    def test_older_capture_or_github_update_cannot_replace_newer_truth(self):
        self.reconcile()
        with self.assertRaisesRegex(LatticeError, "must be newer"):
            self.reconcile(observations(captured_at="2026-09-04T18:30:00Z"))
        capture = observations(captured_at="2026-09-04T19:30:00Z")
        capture["responses"][0]["data"]["updated_at"] = "2026-09-04T17:30:00Z"
        with self.assertRaisesRegex(LatticeError, "older GitHub update"):
            self.reconcile(capture)


if __name__ == "__main__":
    unittest.main()
