#!/usr/bin/env python3
"""Dependency-free command line entry point for Lattice App Works."""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

from control_plane import claim_for_host, read_model, recover_expired_leases
from expertise import resolve_expertise
from state_engine import LatticeError, StateStore


ROOT = Path(__file__).resolve().parents[1]


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def run_script(name: str, args: list[str]) -> int:
    return subprocess.call([sys.executable, str(ROOT / "scripts" / name), *args], cwd=ROOT)


def add_project(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True)


def add_lease(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--lease", required=True)
    parser.add_argument("--role", required=True)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Operate Lattice's active-frontier runtime.")
    commands = result.add_subparsers(dest="command", required=True)

    commands.add_parser("validate")
    commands.add_parser("status")

    inspect = commands.add_parser("inspect")
    inspect.add_argument("--project")
    inspect.add_argument("--frontier-limit", type=int, default=5)

    recover = commands.add_parser("recover")
    recover.add_argument("--project")

    expertise = commands.add_parser("expertise")
    add_project(expertise)
    expertise.add_argument("--role", required=True)
    expertise.add_argument("--platform", action="append")

    initialize = commands.add_parser("initialize")
    initialize.add_argument("--principal-alias", required=True)
    initialize.add_argument("--project-id", required=True)
    initialize.add_argument("--project-name", required=True)

    export = commands.add_parser("export-chatgpt-work")
    add_project(export)
    export.add_argument("--role")
    export.add_argument("--limit", type=int, default=3)
    export.add_argument("--output")
    export.add_argument("--overwrite", action="store_true")

    project_add = commands.add_parser("project-add")
    add_project(project_add)
    project_add.add_argument("--name", required=True)
    project_add.add_argument("--status", choices=("active", "paused", "closed"), default="active")
    project_add.add_argument("--max-wip", type=int)
    project_add.add_argument("--role", default="director")

    project_create = commands.add_parser("project-create")
    project_create.add_argument("--project-id", required=True)
    project_create.add_argument("--project-name", required=True)

    project_status = commands.add_parser("project-status")
    add_project(project_status)
    project_status.add_argument("--status", required=True, choices=("active", "paused", "closed"))
    project_status.add_argument("--role", default="director")

    objective = commands.add_parser("objective-add")
    add_project(objective)
    objective.add_argument("--id")
    objective.add_argument("--title", required=True)
    objective.add_argument("--description", default="")
    objective.add_argument("--owner-role", default="product")
    objective.add_argument("--priority", type=int, default=50)
    objective.add_argument("--role", default="director")

    milestone = commands.add_parser("milestone-add")
    add_project(milestone)
    milestone.add_argument("--objective", required=True)
    milestone.add_argument("--id")
    milestone.add_argument("--title", required=True)
    milestone.add_argument("--ordinal", required=True, type=int)
    milestone.add_argument("--activate", action="store_true")
    milestone.add_argument("--role", default="director")

    record = commands.add_parser("record-put")
    add_project(record)
    record.add_argument("--id")
    record.add_argument("--key", required=True)
    record.add_argument("--kind", required=True, choices=("requirement", "constraint", "decision", "artifact", "risk", "contract"))
    record.add_argument("--title", required=True)
    record.add_argument("--body", default="")
    record.add_argument("--owner-role", required=True)
    record.add_argument("--role", required=True)
    record.add_argument("--source-ref")
    record.add_argument("--status", choices=("current", "invalidated", "superseded"), default="current")
    record.add_argument("--reason", default="state updated")

    truth_add = commands.add_parser("truth-add")
    add_project(truth_add)
    truth_add.add_argument("--id")
    truth_add.add_argument("--key", required=True)
    truth_add.add_argument("--statement", required=True)
    truth_add.add_argument("--epistemic-status", required=True, choices=("observed", "accepted", "contested", "false", "superseded", "unknown"))
    truth_add.add_argument("--attention", required=True, choices=("frontier", "background", "archived"))
    truth_add.add_argument("--confidence", type=float)
    truth_add.add_argument("--source-ref")
    truth_add.add_argument("--material", action="store_true")
    truth_add.add_argument("--role", required=True)

    truth_revise = commands.add_parser("truth-revise")
    truth_revise.add_argument("--truth", required=True)
    truth_revise.add_argument("--statement")
    truth_revise.add_argument("--epistemic-status", choices=("observed", "accepted", "contested", "false", "superseded", "unknown"))
    truth_revise.add_argument("--confidence", type=float)
    truth_revise.add_argument("--source-ref")
    truth_revise.add_argument("--material", action="store_true", default=None)
    truth_revise.add_argument("--reason", required=True)
    truth_revise.add_argument("--role", required=True)

    truth_move = commands.add_parser("truth-move")
    truth_move.add_argument("--truth", required=True)
    truth_move.add_argument("--attention", required=True, choices=("frontier", "background", "archived"))
    truth_move.add_argument("--reason", required=True)
    truth_move.add_argument("--role", required=True)

    truth_link = commands.add_parser("truth-link")
    truth_link.add_argument("--from-truth", required=True)
    truth_link.add_argument("--to-truth", required=True)
    truth_link.add_argument("--relation", required=True, choices=("supports", "contradicts", "refines", "depends_on", "supersedes"))
    truth_link.add_argument("--role", required=True)

    truth_list = commands.add_parser("truth-list")
    add_project(truth_list)
    truth_list.add_argument("--attention", choices=("frontier", "background", "archived"))
    truth_list.add_argument("--epistemic-status", choices=("observed", "accepted", "contested", "false", "superseded", "unknown"))

    condition = commands.add_parser("condition-add")
    add_project(condition)
    condition.add_argument("--objective", required=True)
    condition.add_argument("--milestone", required=True)
    condition.add_argument("--id")
    condition.add_argument("--key", required=True)
    condition.add_argument("--title", required=True)
    condition.add_argument("--description", required=True)
    condition.add_argument("--owner-role", required=True)
    condition.add_argument("--verifier-role", required=True)
    condition.add_argument("--priority", type=int, default=50)
    condition.add_argument("--severity", choices=("critical", "major", "minor", "note"), default="major")
    condition.add_argument("--attempt-budget", type=int)
    condition.add_argument("--input", action="append", default=[])
    condition.add_argument("--truth", action="append", default=[])
    condition.add_argument("--depends-on", action="append", default=[])
    condition.add_argument("--reviewer", action="append", default=[])
    condition.add_argument("--role", required=True)

    frontier = commands.add_parser("frontier")
    add_project(frontier)
    frontier.add_argument("--role")
    frontier.add_argument("--limit", type=int, default=3)

    readiness = commands.add_parser("readiness")
    add_project(readiness)
    readiness.add_argument("--milestone")

    claim = commands.add_parser("claim")
    add_project(claim)
    claim.add_argument("--role", required=True)
    claim.add_argument("--actor", required=True)
    claim.add_argument("--host", default="local")
    claim.add_argument("--workspace")
    claim.add_argument("--action-key")
    claim.add_argument("--ttl", type=int)

    release = commands.add_parser("release")
    add_lease(release)

    submit = commands.add_parser("submit")
    add_lease(submit)
    submit.add_argument("--summary", required=True)
    submit.add_argument("--artifact", action="append", default=[])
    submit.add_argument("--evidence-ref")

    fail = commands.add_parser("fail")
    add_lease(fail)
    fail.add_argument("--summary", required=True)

    review = commands.add_parser("review")
    add_lease(review)
    review.add_argument("--verdict", required=True, choices=("SATISFIED", "NOT_SATISFIED", "CONCUR", "BLOCK"))
    review.add_argument("--summary", required=True)
    review.add_argument("--evidence-ref")

    advance = commands.add_parser("advance")
    add_lease(advance)
    advance.add_argument("--summary", required=True)

    commitment = commands.add_parser("commitment-add")
    add_project(commitment)
    commitment.add_argument("--id")
    commitment.add_argument("--title", required=True)
    commitment.add_argument("--detail", default="")
    commitment.add_argument("--owner-role", required=True)
    commitment.add_argument("--priority", type=int, default=50)
    commitment.add_argument("--due-at")
    commitment.add_argument("--blocking", action="store_true")
    commitment.add_argument("--role", required=True)

    fulfill = commands.add_parser("commitment-fulfill")
    add_lease(fulfill)
    fulfill.add_argument("--summary", required=True)

    exception = commands.add_parser("exception-raise")
    add_project(exception)
    exception.add_argument("--dedupe-key", required=True)
    exception.add_argument("--title", required=True)
    exception.add_argument("--detail", default="")
    exception.add_argument("--severity", choices=("critical", "major", "minor", "note"), default="major")
    exception.add_argument("--owner-role", default="director")
    exception.add_argument("--principal-only", action="store_true")
    exception.add_argument("--target-type")
    exception.add_argument("--target-id")
    exception.add_argument("--role", required=True)

    resolve = commands.add_parser("exception-resolve")
    add_lease(resolve)
    resolve.add_argument("--resolution", required=True)

    state_export = commands.add_parser("state-export")
    state_export.add_argument("--output")

    state_import = commands.add_parser("state-import")
    state_import.add_argument("--file", required=True)
    state_import.add_argument("--expected-revision", type=int)

    delta = commands.add_parser("apply-delta")
    delta.add_argument("--file", required=True)

    return result


def main() -> int:
    args = parser().parse_args()
    if args.command == "validate":
        return run_script("validate_lattice.py", [])
    if args.command == "initialize":
        return run_script(
            "initialize_seed.py",
            [
                "--principal-alias", args.principal_alias,
                "--project-id", args.project_id,
                "--project-name", args.project_name,
            ],
        )
    if args.command == "export-chatgpt-work":
        command = ["--project", args.project, "--limit", str(args.limit)]
        if args.role:
            command.extend(["--role", args.role])
        if args.output:
            command.extend(["--output", args.output])
        if args.overwrite:
            command.append("--overwrite")
        return run_script("export_chatgpt_work.py", command)
    if args.command == "project-create":
        return run_script(
            "create_project.py",
            ["--project-id", args.project_id, "--project-name", args.project_name],
        )
    if args.command == "expertise":
        try:
            emit(resolve_expertise(args.role, args.project, args.platform))
        except (ValueError, KeyError) as error:
            print("Lattice rejected the operation: " + str(error), file=sys.stderr)
            return 2
        return 0

    try:
        with StateStore(ROOT) as store:
            if args.command == "status":
                emit(store.status())
            elif args.command == "inspect":
                emit(read_model(store, args.project, args.frontier_limit))
            elif args.command == "recover":
                emit(recover_expired_leases(store, args.project))
            elif args.command == "project-add":
                emit(store.ensure_project(args.project, args.name, args.status, args.max_wip, args.role))
            elif args.command == "project-status":
                emit(store.set_project_status(args.project, args.status, args.role))
            elif args.command == "objective-add":
                emit(store.add_objective(args.project, args.title, args.description, args.owner_role, args.priority, args.id, args.role))
            elif args.command == "milestone-add":
                emit(store.add_milestone(args.project, args.objective, args.title, args.ordinal, args.activate, args.id, args.role))
            elif args.command == "record-put":
                emit(store.put_record(args.project, args.key, args.kind, args.title, args.body, args.owner_role, args.role, args.source_ref, args.status, args.reason, args.id))
            elif args.command == "truth-add":
                emit(store.add_truth(args.project, args.key, args.statement, args.epistemic_status, args.attention, args.role, args.confidence, args.source_ref, args.material, args.id))
            elif args.command == "truth-revise":
                emit(store.revise_truth(args.truth, args.role, args.reason, args.statement, args.epistemic_status, args.confidence, args.source_ref, args.material))
            elif args.command == "truth-move":
                emit(store.move_truth(args.truth, args.attention, args.role, args.reason))
            elif args.command == "truth-link":
                store.link_truths(args.from_truth, args.to_truth, args.relation, args.role)
                emit({"linked": True})
            elif args.command == "truth-list":
                emit(store.truth_ledger(args.project, args.attention, args.epistemic_status))
            elif args.command == "condition-add":
                emit(store.add_condition(args.project, args.objective, args.milestone, args.key, args.title, args.description, args.owner_role, args.verifier_role, args.role, args.priority, args.severity, args.attempt_budget, args.input, args.truth, args.depends_on, args.reviewer, args.id))
            elif args.command == "frontier":
                emit(store.frontier(args.project, args.role, args.limit))
            elif args.command == "readiness":
                emit(store.readiness(args.project, args.milestone))
            elif args.command == "claim":
                emit(claim_for_host(
                    store,
                    project_id=args.project,
                    role=args.role,
                    actor=args.actor,
                    host=args.host,
                    workspace_id=args.workspace,
                    action_key=args.action_key,
                    ttl_minutes=args.ttl,
                ))
            elif args.command == "release":
                store.release_lease(args.lease, args.role)
                emit({"released": args.lease})
            elif args.command == "submit":
                emit(store.submit(args.lease, args.role, args.summary, args.artifact, args.evidence_ref))
            elif args.command == "fail":
                emit(store.fail_action(args.lease, args.role, args.summary))
            elif args.command == "review":
                emit(store.review(args.lease, args.role, args.verdict, args.summary, args.evidence_ref))
            elif args.command == "advance":
                emit(store.advance_milestone(args.lease, args.role, args.summary))
            elif args.command == "commitment-add":
                emit(store.add_commitment(args.project, args.title, args.detail, args.owner_role, args.role, args.priority, args.due_at, args.blocking, args.id))
            elif args.command == "commitment-fulfill":
                emit(store.fulfill_commitment(args.lease, args.role, args.summary))
            elif args.command == "exception-raise":
                emit(store.raise_exception(args.project, args.dedupe_key, args.title, args.detail, args.severity, args.owner_role, args.role, args.principal_only, args.target_type, args.target_id))
            elif args.command == "exception-resolve":
                emit(store.resolve_exception(args.lease, args.role, args.resolution))
            elif args.command == "state-export":
                emit(store.export_snapshot(Path(args.output).resolve() if args.output else None))
            elif args.command == "state-import":
                store.import_snapshot(Path(args.file).resolve(), args.expected_revision)
                emit(store.status())
            elif args.command == "apply-delta":
                emit(store.apply_delta(json.loads(Path(args.file).read_text(encoding="utf-8"))))
            else:
                raise LatticeError("Unsupported command: " + args.command)
    except (LatticeError, sqlite3.Error, ValueError, KeyError) as error:
        print("Lattice rejected the operation: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
