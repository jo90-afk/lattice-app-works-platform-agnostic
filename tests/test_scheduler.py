from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from scheduler import Worker, candidate_plan, dispatch  # noqa: E402
from state_engine import StateStore  # noqa: E402


class SchedulerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.registry = folder / "registry.md"

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def add_project(self, project_id: str, *, max_wip: int = 3) -> tuple[str, str]:
        self.store.ensure_project(project_id, project_id.title(), max_wip=max_wip)
        objective = self.store.add_objective(
            project_id,
            "Deliver " + project_id,
            "Scheduler fixture",
            "product",
            objective_id=f"objective-{project_id}",
        )
        milestone = self.store.add_milestone(
            project_id,
            objective["id"],
            "Ready",
            1,
            True,
            milestone_id=f"milestone-{project_id}",
        )
        return objective["id"], milestone["id"]

    def add_condition(
        self,
        project_id: str,
        objective_id: str,
        milestone_id: str,
        key: str,
        owner_role: str,
        priority: int = 50,
    ) -> None:
        verifier = "quality" if owner_role != "quality" else "assurance"
        self.store.add_condition(
            project_id,
            objective_id,
            milestone_id,
            key,
            key,
            "Scheduler fixture condition",
            owner_role,
            verifier,
            "director",
            priority=priority,
            condition_id=f"condition-{project_id}-{key}",
        )

    def write_registry(self, project_ids: list[str], capacity: int = 3) -> None:
        rows = "\n".join(
            f"| {project_id} | {project_id.title()} | {index + 1} | Active | projects/{project_id}/ |"
            for index, project_id in enumerate(project_ids)
        )
        self.registry.write_text(
            "# Portfolio Registry\n\n"
            f"**Concurrency limit:** {capacity} specialist threads.\n\n"
            "| Project ID | Project | Priority | State | Capsule |\n"
            "| --- | --- | --- | --- | --- |\n"
            + rows
            + "\n",
            encoding="utf-8",
        )

    def test_plan_honors_portfolio_order_and_round_robins_projects(self) -> None:
        a_obj, a_ms = self.add_project("project-a")
        b_obj, b_ms = self.add_project("project-b")
        self.add_condition("project-a", a_obj, a_ms, "services", "services", priority=90)
        self.add_condition("project-b", b_obj, b_ms, "application", "application", priority=20)
        self.write_registry(["project-b", "project-a"], capacity=2)

        plan = candidate_plan(
            self.store,
            [
                Worker("app-1", "application", "ci", "app-ws"),
                Worker("svc-1", "services", "ci", "svc-ws"),
            ],
            registry_path=self.registry,
        )

        self.assertEqual(plan["project_order"], ["project-b", "project-a"])
        self.assertEqual(
            [item["project_id"] for item in plan["assignments"]],
            ["project-b", "project-a"],
        )
        self.assertEqual(len(plan["assignments"]), 2)

    def test_plan_projects_role_wip_before_claiming(self) -> None:
        objective, milestone = self.add_project("project-a", max_wip=3)
        self.add_condition("project-a", objective, milestone, "app-one", "application", priority=90)
        self.add_condition("project-a", objective, milestone, "app-two", "application", priority=80)
        self.add_condition("project-a", objective, milestone, "services", "services", priority=70)
        self.write_registry(["project-a"], capacity=3)

        plan = candidate_plan(
            self.store,
            [
                Worker("app-1", "application", "ci"),
                Worker("app-2", "application", "ci"),
                Worker("svc-1", "services", "ci"),
            ],
            registry_path=self.registry,
        )
        roles = [item["action"]["role"] for item in plan["assignments"]]
        self.assertEqual(roles.count("application"), 1)
        self.assertEqual(roles.count("services"), 1)
        self.assertEqual(len(plan["assignments"]), 2)

    def test_existing_leases_reduce_portfolio_and_project_capacity(self) -> None:
        objective, milestone = self.add_project("project-a", max_wip=2)
        self.add_condition("project-a", objective, milestone, "application", "application", priority=90)
        self.add_condition("project-a", objective, milestone, "services", "services", priority=80)
        self.write_registry(["project-a"], capacity=2)
        self.store.claim("project-a", "application", "existing-app")

        plan = candidate_plan(
            self.store,
            [Worker("svc-1", "services", "ci")],
            registry_path=self.registry,
        )
        self.assertEqual(plan["active_specialist_leases"], 1)
        self.assertEqual(plan["available_slots"], 1)
        self.assertEqual(plan["project_slots"]["project-a"], 1)
        self.assertEqual(plan["assignments"][0]["action"]["role"], "services")

    def test_blocked_first_project_does_not_stop_unrelated_project(self) -> None:
        a_obj, a_ms = self.add_project("project-a")
        self.add_condition("project-a", a_obj, a_ms, "application", "application")
        self.add_project("project-b")
        self.store.set_project_status("project-b", "paused", "director")
        self.write_registry(["project-b", "project-a"], capacity=1)

        plan = candidate_plan(
            self.store,
            [Worker("app-1", "application", "ci")],
            registry_path=self.registry,
        )
        self.assertEqual(plan["project_order"], ["project-a"])
        self.assertEqual(plan["assignments"][0]["project_id"], "project-a")

    def test_dispatch_persists_only_successful_leases_not_a_queue(self) -> None:
        objective, milestone = self.add_project("project-a")
        self.add_condition("project-a", objective, milestone, "application", "application")
        self.write_registry(["project-a"], capacity=1)
        before_revision = self.store.revision

        plan = candidate_plan(
            self.store,
            [Worker("app-1", "application", "ci", "worktree-a")],
            registry_path=self.registry,
        )
        self.assertEqual(self.store.revision, before_revision)
        self.assertEqual(
            int(self.store.conn.execute("SELECT COUNT(*) FROM leases").fetchone()[0]),
            0,
        )

        result = dispatch(
            self.store,
            [Worker("app-1", "application", "ci", "worktree-a")],
            registry_path=self.registry,
        )
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(result["rejected"], [])
        self.assertEqual(
            int(self.store.conn.execute("SELECT COUNT(*) FROM leases").fetchone()[0]),
            1,
        )
        tables = {
            row[0]
            for row in self.store.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        self.assertNotIn("schedule", tables)
        self.assertNotIn("queue", tables)
        self.assertNotIn("work_orders", tables)

    def test_principal_actions_are_never_auto_scheduled(self) -> None:
        objective, milestone = self.add_project("project-a")
        self.add_condition("project-a", objective, milestone, "application", "application")
        self.store.raise_exception(
            "project-a",
            "principal-decision",
            "Principal decision",
            "Human boundary",
            "major",
            "director",
            "director",
            principal_only=True,
        )
        self.write_registry(["project-a"], capacity=2)

        plan = candidate_plan(
            self.store,
            [
                Worker("principal-1", "principal", "human"),
                Worker("app-1", "application", "ci"),
            ],
            registry_path=self.registry,
        )
        self.assertEqual(len(plan["assignments"]), 1)
        self.assertEqual(plan["assignments"][0]["action"]["role"], "application")
        self.assertNotIn("principal-1", [item["worker"]["actor"] for item in plan["assignments"]])


if __name__ == "__main__":
    unittest.main()
