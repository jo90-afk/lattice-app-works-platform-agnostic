from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from state_engine import LatticeError  # noqa: E402
from write_ownership import (  # noqa: E402
    repository_artifact_owned,
    role_write_domains,
    roles_conflict,
    validate_artifact_ownership,
)


class WriteOwnershipTest(unittest.TestCase):
    def test_canonical_agency_domains_are_parsed(self) -> None:
        domains = role_write_domains(ROOT)
        self.assertIn("projects/{project_id}/platform/**", domains["application"])
        self.assertIn("projects/{project_id}/ops/**", domains["release"])
        self.assertIn("projects/{project_id}/contracts/**", domains["architecture"])

    def test_application_owns_only_its_project_application_paths(self) -> None:
        self.assertTrue(
            repository_artifact_owned(
                ROOT, "project-001", "application", "projects/project-001/platform/app.py"
            )
        )
        self.assertTrue(
            repository_artifact_owned(
                ROOT,
                "project-001",
                "application",
                "projects/project-001/tests/application-unit/test_app.py",
            )
        )
        self.assertFalse(
            repository_artifact_owned(
                ROOT, "project-001", "application", "projects/project-001/services/app.py"
            )
        )
        self.assertFalse(
            repository_artifact_owned(
                ROOT, "project-001", "application", "projects/project-002/platform/app.py"
            )
        )

    def test_typed_external_project_refs_use_project_relative_role_domains(self) -> None:
        valid = "project-artifact://project-001/platform/app.py"
        wrong_role = "project-artifact://project-001/services/server.py"
        wrong_project = "project-artifact://project-002/platform/app.py"

        self.assertTrue(repository_artifact_owned(ROOT, "project-001", "application", valid))
        self.assertFalse(
            repository_artifact_owned(ROOT, "project-001", "application", wrong_role)
        )
        self.assertFalse(
            repository_artifact_owned(ROOT, "project-001", "application", wrong_project)
        )
        validate_artifact_ownership(ROOT, "project-001", "application", [valid])

        with self.assertRaisesRegex(LatticeError, "does not own external project artifact path"):
            validate_artifact_ownership(ROOT, "project-001", "application", [wrong_role])
        with self.assertRaisesRegex(LatticeError, "outside project"):
            validate_artifact_ownership(ROOT, "project-001", "application", [wrong_project])

    def test_logical_external_refs_do_not_claim_repository_ownership(self) -> None:
        self.assertTrue(
            repository_artifact_owned(
                ROOT, "project-001", "application", "artifact://build-output"
            )
        )
        validate_artifact_ownership(
            ROOT, "project-001", "application", ["artifact://build-output"]
        )

    def test_path_traversal_and_cross_domain_submission_are_rejected(self) -> None:
        with self.assertRaises(LatticeError):
            validate_artifact_ownership(
                ROOT,
                "project-001",
                "application",
                ["projects/project-001/platform/../services/server.py"],
            )
        with self.assertRaises(LatticeError):
            validate_artifact_ownership(
                ROOT,
                "project-001",
                "application",
                ["project-artifact://project-001/platform/../services/server.py"],
            )
        with self.assertRaisesRegex(LatticeError, "does not own artifact path"):
            validate_artifact_ownership(
                ROOT,
                "project-001",
                "application",
                ["projects/project-001/services/server.py"],
            )

    def test_canonical_specialist_domains_are_disjoint(self) -> None:
        self.assertTrue(roles_conflict(ROOT, "project-001", "application", "application"))
        self.assertFalse(roles_conflict(ROOT, "project-001", "application", "services"))
        self.assertFalse(roles_conflict(ROOT, "project-001", "architecture", "application"))
        self.assertFalse(roles_conflict(ROOT, "project-001", "quality", "security"))


if __name__ == "__main__":
    unittest.main()
