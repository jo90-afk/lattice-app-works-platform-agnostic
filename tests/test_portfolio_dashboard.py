from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from portfolio_dashboard import render_portfolio_html  # noqa: E402


class PortfolioDashboardTest(unittest.TestCase):
    def test_inactive_projects_do_not_render_on_active_portfolio(self) -> None:
        def project(pid: str, name: str, status: str) -> dict:
            return {
                "project": {"id": pid, "name": name, "status": status},
                "objective": None,
                "milestone": None,
                "frontier": [],
                "active_leases": [],
                "pending_verification": [],
                "open_exceptions": [],
                "temporal_health": {"blocked_conditions": []},
                "readiness": {"ready": False, "conditions": []},
                "evidence_chain": [],
                "frontier_truths": [],
                "consequence_graph": {"counts": {}},
            }

        model = {
            "portfolio": {"active_projects": 1, "in_flight": 0, "pending_verification": 0},
            "principal_inbox": {"count": 0, "items": []},
            "recent_accepted_changes": [],
            "projects": [
                project("active-001", "Active Project", "active"),
                project("inactive-001", "Inactive Seed Project", "inactive"),
            ],
        }
        page = render_portfolio_html(model)
        self.assertIn("Active Project", page)
        self.assertNotIn("Inactive Seed Project", page)
        self.assertIn("Projects</strong> <b>1/1", page)


if __name__ == "__main__":
    unittest.main()
