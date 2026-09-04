#!/usr/bin/env python3
"""Observe GitHub transport state without granting acceptance or publication authority.

The connector supplies frozen GET responses. A Director-owned contract selects the
repository and tracked objects; reports are derived, and accepted observations use
the existing truth ledger. No GitHub mutation or markdown inference occurs here.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

from state_backend import backend_for_store
from state_engine import LatticeError, StateStore, json_text

TRACKING_KEY = "github.tracking"
TRUTH_KEY = "github.observed-state"
OBSERVATION_REASON = "Reconciled fresh GitHub observations; acceptance unchanged"
MAX_CAPTURE_AGE = timedelta(hours=24)


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LatticeError(name + " must be an object")
    return value


def _fields(value: dict[str, Any], required: set[str], optional: set[str], name: str) -> None:
    if required - value.keys() or value.keys() - required - optional:
        raise LatticeError(name + " has missing or unsupported fields")


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LatticeError(name + " must be a nonempty string")
    return value


def _integer(value: Any, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise LatticeError(name + " must be an integer >= " + str(minimum))
    return value


def _sha(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise LatticeError("A full lowercase Git SHA is required")
    return value


def _time(value: Any, name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(_text(value, name).replace("Z", "+00:00"))
    except ValueError as error:
        raise LatticeError(name + " must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise LatticeError(name + " must include a timezone")
    return parsed.astimezone(timezone.utc)


def _repository(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise LatticeError("repository must be owner/name")
    return value


def validate_tracking(value: Any) -> dict[str, Any]:
    tracking = _object(value, "tracking")
    _fields(tracking, {"format", "version", "repository", "declarations"}, {"integration_branch"}, "tracking")
    if tracking["format"] != "lattice-github-tracking" or type(tracking["version"]) is not int or tracking["version"] != 1:
        raise LatticeError("Unsupported GitHub tracking contract")
    _repository(tracking["repository"])
    if "integration_branch" in tracking:
        _text(tracking["integration_branch"], "integration_branch")
    declarations = tracking["declarations"]
    if not isinstance(declarations, list) or not 1 <= len(declarations) <= 100:
        raise LatticeError("declarations must contain 1 to 100 scoped objects")
    keys: set[str] = set()
    for declaration in declarations:
        item = _object(declaration, "declaration")
        _fields(item, {"kind", "id", "status", "source_ref"}, {"reason"}, "declaration")
        _text(item["source_ref"], "declaration source_ref")
        _text(item["kind"], "declaration kind")
        _text(item["status"], "declared status")
        if item["kind"] == "pull_request":
            _integer(item["id"], "pull request id", 1)
            statuses = {"active", "merged", "closed", "superseded"}
        elif item["kind"] == "release":
            _text(item["id"], "release tag")
            statuses = {"pending", "published", "superseded"}
        else:
            raise LatticeError("Unsupported declaration kind")
        if item["status"] not in statuses:
            raise LatticeError("Unsupported declared status")
        if item["status"] == "superseded":
            _text(item.get("reason"), "supersession reason")
        key = item["kind"] + ":" + str(item["id"])
        if key in keys:
            raise LatticeError("Duplicate declaration: " + key)
        keys.add(key)
    return tracking


def _response(capture: dict[str, Any], url: str) -> dict[str, Any]:
    if capture.get("url") != url:
        raise LatticeError("Observation URL is not the declared repository/object: " + url)
    if capture.get("status") != 200 or type(capture.get("status")) is not int:
        raise LatticeError("Observation requires a successful 200 GET response")
    return _object(capture.get("data"), "GET response data")


def check_github_state(tracking: Any, envelope: Any, *, now: datetime | None = None) -> dict[str, Any]:
    """Return a deterministic report. Missing, stale or mis-scoped evidence fails closed."""
    tracking = validate_tracking(tracking)
    envelope = _object(envelope, "observations")
    _fields(envelope, {"format", "version", "repository", "captured_at", "responses"}, set(), "observations")
    if envelope["format"] != "lattice-github-observations" or type(envelope["version"]) is not int or envelope["version"] != 1:
        raise LatticeError("Unsupported GitHub observation envelope")
    repository = tracking["repository"]
    if envelope["repository"] != repository:
        raise LatticeError("Cross-repository observation rejected")
    captured = _time(envelope["captured_at"], "captured_at")
    now = now or datetime.now(timezone.utc)
    if captured > now + timedelta(minutes=5) or now - captured > MAX_CAPTURE_AGE:
        raise LatticeError("Observation capture is stale or in the future; fetch fresh GitHub evidence")
    responses = envelope["responses"]
    if not isinstance(responses, list) or not 1 <= len(responses) <= 200:
        raise LatticeError("responses must contain 1 to 200 GET captures")
    captures: dict[str, dict[str, Any]] = {}
    prefix = "https://api.github.com/repos/" + repository
    for raw in responses:
        capture = _object(raw, "response capture")
        _fields(capture, {"url", "status", "data"}, set(), "response capture")
        url = _text(capture["url"], "response URL")
        if not url.startswith(prefix + "/") or url in captures:
            raise LatticeError("Cross-repository or duplicate response URL")
        captures[url] = capture
    used: set[str] = set()

    def fetch(url: str) -> dict[str, Any]:
        if url not in captures:
            raise LatticeError("Missing GitHub evidence: " + url)
        used.add(url)
        return _response(captures[url], url)

    items = []
    integration_sha = None
    if "integration_branch" in tracking:
        branch = tracking["integration_branch"]
        data = fetch(prefix + "/branches/" + quote(branch, safe=""))
        if data.get("name") != branch:
            raise LatticeError("Integration branch does not match the tracking contract")
        commit = _object(data.get("commit"), "integration branch commit")
        integration_sha = _sha(commit.get("sha"))
        if commit.get("url") != prefix + "/commits/" + integration_sha:
            raise LatticeError("Integration branch commit is outside the declared repository")
    for declaration in tracking["declarations"]:
        kind, identifier = declaration["kind"], declaration["id"]
        declared = declaration["status"]
        finding = None
        if kind == "pull_request":
            url = prefix + "/pulls/" + str(identifier)
            data = fetch(url)
            if data.get("number") != identifier or type(data.get("number")) is not int:
                raise LatticeError("Pull request number does not match declaration")
            if data.get("url") != url or data.get("html_url") != "https://github.com/" + repository + "/pull/" + str(identifier):
                raise LatticeError("Pull request identity does not match source")
            base = _object(data.get("base"), "PR base")
            head = _object(data.get("head"), "PR head")
            if _object(base.get("repo"), "PR base repository").get("full_name") != repository:
                raise LatticeError("PR base repository does not match declaration")
            base_sha, head_sha = _sha(base.get("sha")), _sha(head.get("sha"))
            _text(base.get("ref"), "PR base ref")
            _text(head.get("ref"), "PR head ref")
            state, merged = _text(data.get("state"), "PR state"), data.get("merged")
            if state not in {"open", "closed"} or type(merged) is not bool:
                raise LatticeError("Pull request requires state and a boolean merged flag")
            updated = _time(data.get("updated_at"), "PR updated_at")
            if updated > captured:
                raise LatticeError("PR changed after the claimed capture time")
            if merged:
                merged_at = _time(data.get("merged_at"), "PR merged_at")
                if state != "closed" or merged_at > updated:
                    raise LatticeError("Inconsistent merged pull request evidence")
                _sha(data.get("merge_commit_sha"))
            elif data.get("merged_at") is not None:
                raise LatticeError("Unmerged pull request has a merge timestamp")
            observed = "merged" if merged else ("active" if state == "open" else "closed")
            facts = {"base_sha": base_sha, "head_sha": head_sha, "updated_at": data["updated_at"],
                     "merged_at": data.get("merged_at"), "merge_commit_sha": data.get("merge_commit_sha") if merged else None}
            comparison_base = integration_sha or base_sha
            compare_url = prefix + "/compare/" + comparison_base + "..." + head_sha
            if compare_url in captures:
                compare = fetch(compare_url)
                if _object(compare.get("base_commit"), "compare base").get("sha") != comparison_base:
                    raise LatticeError("Comparison base SHA does not match the observed pull request")
                ahead = _integer(compare.get("ahead_by"), "ahead_by")
                behind = _integer(compare.get("behind_by"), "behind_by")
                expected_status = "diverged" if ahead and behind else "ahead" if ahead else "behind" if behind else "identical"
                if compare.get("status") != expected_status:
                    raise LatticeError("Inconsistent comparison counts/status")
                if compare.get("html_url") != "https://github.com/" + repository + "/compare/" + comparison_base + "..." + head_sha:
                    raise LatticeError("Comparison identity does not bind both frozen SHAs")
                facts["ahead_by"], facts["behind_by"] = ahead, behind
                facts["comparison_base_sha"] = comparison_base
                facts["comparison_base_ref"] = tracking.get("integration_branch", base["ref"])
                if observed == "active" and ahead == 0 and declared == "active":
                    finding = "supersession_candidate"
            if declared != "superseded" and observed != declared:
                finding = "declared_state_drift"
        else:
            url = prefix + "/releases/tags/" + quote(identifier, safe="")
            data = fetch(url)
            if data.get("tag_name") != identifier or data.get("html_url") != "https://github.com/" + repository + "/releases/tag/" + quote(identifier, safe=""):
                raise LatticeError("Release identity does not match declaration")
            release_id = _integer(data.get("id"), "release id", 1)
            if data.get("url") != prefix + "/releases/" + str(release_id):
                raise LatticeError("Release API identity is outside the declared repository")
            draft, prerelease = data.get("draft"), data.get("prerelease")
            if type(draft) is not bool or type(prerelease) is not bool:
                raise LatticeError("Release requires boolean draft and prerelease flags")
            published = data.get("published_at")
            if not draft and published is None:
                raise LatticeError("Published release requires published_at")
            if published is not None and _time(published, "published_at") > captured:
                raise LatticeError("Release publication is later than observation capture")
            observed = "pending" if draft else "published"
            facts = {"release_id": release_id, "published_at": published, "prerelease": prerelease,
                     "target_commitish": _text(data.get("target_commitish"), "target_commitish")}
            if declared != "superseded" and observed != declared:
                finding = "declared_state_drift"
        items.append({"key": kind + ":" + str(identifier), "kind": kind, "id": identifier,
                      "declared": declared, "observed": observed, "source_ref": data["html_url"],
                      "declaration_source": declaration["source_ref"], "facts": facts, "finding": finding,
                      "attention": "frontier" if finding else "historical" if declared == "superseded" else "background",
                      "reason": declaration.get("reason")})
    if used != captures.keys():
        raise LatticeError("Unrequested or incorrectly scoped response captures")
    items.sort(key=lambda item: item["key"])
    findings = [item["key"] for item in items if item["finding"]]
    return {"format": "lattice-github-state-report", "version": 1, "repository": repository,
            "captured_at": envelope["captured_at"], "items": items, "unresolved": findings,
            "authority": "external_observation_only", "acceptance_changed": False, "publication_authorized": False}


def reconcile_github_state(store: StateStore, *, project_id: str, envelope: Any,
                           expected_revision: int, role: str, now: datetime | None = None) -> dict[str, Any]:
    """Record one project observation under a revision lock, never external acceptance.

    A single existing add/revise truth transition commits all semantic changes. A
    retry of the identical accepted capture is a no-op, including after another
    project write; a changed capture must use the current project revision.
    """
    if role != "director":
        raise LatticeError("Only the Director may reconcile GitHub project observations")
    _integer(expected_revision, "expected_revision")
    backend = backend_for_store(store)
    try:
        backend.begin_project_write(project_id)
        store._require_project(project_id)
        record = store.conn.execute("SELECT * FROM records WHERE project_id = ? AND key = ?", (project_id, TRACKING_KEY)).fetchone()
        if record is None or record["owner_role"] != "director" or record["kind"] != "contract" or record["status"] != "current":
            raise LatticeError("A current Director-owned github.tracking contract is required")
        tracking = validate_tracking(json.loads(record["body"]))
        report = check_github_state(tracking, envelope, now=now)
        payload = {"tracking_record_id": record["id"], "tracking_version": record["version"],
                   "observation_sha256": hashlib.sha256(json_text(envelope).encode()).hexdigest(), "report": report}
        statement = json_text(payload)
        current = store.conn.execute("SELECT * FROM truths WHERE project_id = ? AND key = ?", (project_id, TRUTH_KEY)).fetchone()
        if current and current["created_by"] != "director":
            raise LatticeError("GitHub observation truth is not owned by this adapter's Director role")
        if current:
            previous = json.loads(current["statement"])
            expected_status = "contested" if previous["report"]["unresolved"] else "observed"
            version = store.conn.execute("SELECT changed_by, change_reason FROM truth_versions WHERE truth_id = ? AND version = ?",
                                         (current["id"], current["version"])).fetchone()
            if current["epistemic_status"] != expected_status or version["changed_by"] != role or version["change_reason"] not in {"truth recorded", OBSERVATION_REASON}:
                raise LatticeError("GitHub observation truth has an unresolved manual status; resolve it explicitly")
        if current and current["statement"] == statement:
            backend.rollback()
            return {"replayed": True, "truth": dict(current), "report": report, "project_revision": store.project_revision(project_id)}
        revision = store.project_revision(project_id)
        if revision != expected_revision:
            raise LatticeError(f"GitHub observation is stale: expected project revision {expected_revision}, current {revision}")
        if current:
            previous_report = previous["report"]
            if previous_report["repository"] != tracking["repository"]:
                raise LatticeError("Repository binding cannot be reassigned by reconciliation")
            if _time(report["captured_at"], "captured_at") <= _time(previous_report["captured_at"], "previous captured_at"):
                raise LatticeError("Observation capture must be newer than the current GitHub truth")
            previous_items = {item["key"]: item for item in previous_report["items"]}
            for item in report["items"]:
                old = previous_items.get(item["key"])
                if old and item["kind"] == "pull_request" and _time(item["facts"]["updated_at"], "updated_at") < _time(old["facts"]["updated_at"], "previous updated_at"):
                    raise LatticeError("Pull request evidence regressed to an older GitHub update")
        attention = "frontier" if report["unresolved"] else "background"
        if current and store.conn.execute(
            "SELECT 1 FROM condition_truths ct JOIN conditions c ON c.id = ct.condition_id "
            "JOIN milestones m ON m.id = c.milestone_id WHERE ct.truth_id = ? "
            "AND m.status IN ('active', 'planned') LIMIT 1", (current["id"],)
        ).fetchone():
            attention = "frontier"
        source_ref = "https://github.com/" + tracking["repository"]
        epistemic = "contested" if report["unresolved"] else "observed"
        if current:
            truth = store.revise_truth(current["id"], role, OBSERVATION_REASON,
                                       statement=statement, epistemic_status=epistemic, source_ref=source_ref, material=True, attention_state=attention)
        else:
            truth = store.add_truth(project_id, TRUTH_KEY, statement, epistemic, attention, role,
                                    source_ref=source_ref, material=True)
        return {"replayed": False, "truth": truth, "report": report, "project_revision": store.project_revision(project_id)}
    except Exception:
        backend.rollback()
        raise
