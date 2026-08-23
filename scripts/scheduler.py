#!/usr/bin/env python3
"""Queue-free bounded scheduler for the Lattice active frontier."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from concurrency import claim_for_host_atomic
from state_engine import LatticeError, StateStore, utc_now
from store_factory import open_state_store

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Worker:
    actor: str
    role: str
    host: str
    workspace_id: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Worker":
        missing = [name for name in ("actor", "role", "host") if not value.get(name)]
        if missing:
            raise LatticeError("Scheduler worker is missing: " + ", ".join(missing))
        return cls(
            actor=str(value["actor"]),
            role=str(value["role"]),
            host=str(value["host"]),
            workspace_id=str(value["workspace_id"]) if value.get("workspace_id") else None,
        )


def parse_registry(registry_path: Path) -> tuple[list[str], int]:
    """Read portfolio order and specialist capacity from the human registry."""
    text = registry_path.read_text(encoding="utf-8")
    capacity_match = re.search(r"\*\*Concurrency limit:\*\*\s*(\d+)\s+specialist", text, re.I)
    capacity = int(capacity_match.group(1)) if capacity_match else 3
    if capacity < 1:
        raise LatticeError("Portfolio concurrency limit must be at least 1")

    project_ids: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "Project ID" or cells[0].startswith("<"):
            continue
        project_ids.append(cells[0])
    return project_ids, capacity


def portfolio_order(store: StateStore, registry_path: Path) -> tuple[list[str], int]:
    registered, capacity = parse_registry(registry_path)
    active = [
        str(row["id"])
        for row in store.conn.execute(
            "SELECT id FROM projects WHERE status = 'active' ORDER BY created_at, id"
        ).fetchall()
    ]
    active_set = set(active)
    ordered = [project_id for project_id in registered if project_id in active_set]
    seen = set(ordered)
    ordered.extend(project_id for project_id in active if project_id not in seen)
    return ordered, capacity


def active_specialist_leases(store: StateStore) -> int:
    return int(
        store.conn.execute(
            "SELECT COUNT(*) FROM leases WHERE expires_at > ? AND role <> 'principal'",
            (utc_now(),),
        ).fetchone()[0]
    )


def _available_workers(store: StateStore, workers: Iterable[Worker]) -> list[Worker]:
    now = utc_now()
    result: list[Worker] = []
    for worker in workers:
        if worker.role == "principal":
            continue
        store._validate_role(worker.role)
        already_active = store.conn.execute(
            "SELECT 1 FROM leases WHERE leased_by = ? AND expires_at > ? LIMIT 1",
            (worker.actor, now),
        ).fetchone()
        if already_active is None:
            result.append(worker)
    return result


def _project_slots(store: StateStore, project_id: str) -> int:
    now = utc_now()
    project = store._require_project(project_id)
    active = int(
        store.conn.execute(
            "SELECT COUNT(*) FROM leases WHERE project_id = ? AND expires_at > ?",
            (project_id, now),
        ).fetchone()[0]
    )
    return max(0, int(project["max_wip"]) - active)


def _active_project_roles(store: StateStore, project_id: str) -> set[str]:
    return {
        str(row["role"])
        for row in store.conn.execute(
            "SELECT DISTINCT role FROM leases WHERE project_id = ? AND expires_at > ?",
            (project_id, utc_now()),
        ).fetchall()
    }


def candidate_plan(
    store: StateStore,
    workers: Iterable[Worker],
    *,
    registry_path: Path | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Return the next compatible assignments without persisting a queue."""
    registry = registry_path or (store.root / "portfolio" / "registry.md")
    projects, portfolio_capacity = portfolio_order(store, registry)
    active = active_specialist_leases(store)
    capacity = max(0, portfolio_capacity - active)
    if limit is not None:
        capacity = min(capacity, max(0, limit))

    available = _available_workers(store, workers)
    assignments: list[dict[str, Any]] = []
    used_workers: set[str] = set()
    project_slots = {project_id: _project_slots(store, project_id) for project_id in projects}
    project_planned = {project_id: 0 for project_id in projects}
    unavailable_roles = {project_id: _active_project_roles(store, project_id) for project_id in projects}

    # Portfolio order is the primary sort. Frontier score already captures
    # readiness/risk/priority inside a project. Repeated passes give each project
    # one opportunity before a higher-ranked project consumes another slot.
    project_actions = {
        project_id: store.frontier(project_id, None, 1000)
        for project_id in projects
    }
    while len(assignments) < capacity:
        made_assignment = False
        for project_id in projects:
            if len(assignments) >= capacity:
                break
            if project_planned[project_id] >= project_slots[project_id]:
                continue
            actions = project_actions[project_id]
            action = next(
                (
                    item for item in actions
                    if item["role"] != "principal"
                    and item["role"] not in unavailable_roles[project_id]
                    and not any(existing["action"]["action_key"] == item["action_key"] for existing in assignments)
                    and any(
                        worker.actor not in used_workers and worker.role == item["role"]
                        for worker in available
                    )
                ),
                None,
            )
            if action is None:
                continue
            worker = next(
                worker for worker in available
                if worker.actor not in used_workers and worker.role == action["role"]
            )
            assignments.append(
                {
                    "project_id": project_id,
                    "worker": {
                        "actor": worker.actor,
                        "role": worker.role,
                        "host": worker.host,
                        "workspace_id": worker.workspace_id,
                    },
                    "action": {
                        key: action[key]
                        for key in (
                            "action_key", "kind", "project_id", "target_id", "role", "title", "score", "state_revision"
                        )
                    },
                }
            )
            used_workers.add(worker.actor)
            project_planned[project_id] += 1
            unavailable_roles[project_id].add(action["role"])
            made_assignment = True
        if not made_assignment:
            break

    return {
        "format": "lattice-schedule-plan",
        "version": 1,
        "portfolio_capacity": portfolio_capacity,
        "active_specialist_leases": active,
        "available_slots": capacity,
        "project_order": projects,
        "project_slots": project_slots,
        "assignments": assignments,
        "unassigned_workers": [worker.actor for worker in available if worker.actor not in used_workers],
    }


def dispatch(
    store: StateStore,
    workers: Iterable[Worker],
    *,
    registry_path: Path | None = None,
    limit: int | None = None,
    ttl_minutes: int | None = None,
) -> dict[str, Any]:
    """Claim the current bounded plan; only successful claims become durable."""
    plan = candidate_plan(store, workers, registry_path=registry_path, limit=limit)
    claims: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for assignment in plan["assignments"]:
        worker = assignment["worker"]
        action = assignment["action"]
        try:
            claim = claim_for_host_atomic(
                store,
                project_id=assignment["project_id"],
                role=worker["role"],
                actor=worker["actor"],
                host=worker["host"],
                workspace_id=worker.get("workspace_id"),
                action_key=action["action_key"],
                ttl_minutes=ttl_minutes,
            )
        except LatticeError as error:
            rejected.append(
                {
                    "project_id": assignment["project_id"],
                    "action_key": action["action_key"],
                    "actor": worker["actor"],
                    "reason": str(error),
                }
            )
            continue
        claims.append(claim)
    return {
        "format": "lattice-schedule-dispatch",
        "version": 1,
        "plan": plan,
        "claims": claims,
        "rejected": rejected,
    }


def _load_workers(path: str | None) -> list[Worker]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    value = json.loads(raw)
    if not isinstance(value, list):
        raise LatticeError("Scheduler worker input must be a JSON array")
    return [Worker.from_dict(item) for item in value]


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive or dispatch bounded portfolio work without creating a queue.")
    parser.add_argument("command", choices=("plan", "dispatch"))
    parser.add_argument("--workers", help="JSON worker file; stdin is used when omitted")
    parser.add_argument("--registry", default=str(ROOT / "portfolio" / "registry.md"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--ttl", type=int)
    args = parser.parse_args()
    try:
        workers = _load_workers(args.workers)
        with open_state_store(ROOT) as store:
            if args.command == "plan":
                result = candidate_plan(store, workers, registry_path=Path(args.registry), limit=args.limit)
            else:
                result = dispatch(
                    store,
                    workers,
                    registry_path=Path(args.registry),
                    limit=args.limit,
                    ttl_minutes=args.ttl,
                )
    except (OSError, json.JSONDecodeError, LatticeError, KeyError, ValueError, TypeError) as error:
        print("Lattice scheduler rejected the request: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
