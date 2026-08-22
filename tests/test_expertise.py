from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from expertise import load_catalog, resolve_expertise  # noqa: E402
from export_chatgpt_work import expertise_paths  # noqa: E402


class ExpertiseResolverTest(unittest.TestCase):
    def test_every_agent_role_has_one_selective_core_module(self) -> None:
        catalog = load_catalog()
        for role, core in catalog["role_modules"].items():
            result = resolve_expertise(role, "example-001")
            self.assertIn("expertise/README.md", result["paths"])
            self.assertIn(core, result["paths"])
            if role != "application":
                self.assertEqual(len(result["paths"]), 2)

    def test_aliases_resolve_without_duplicate_or_unrelated_packs(self) -> None:
        result = resolve_expertise(
            "application",
            "example-001",
            ["ios", "apple", "pwa", "winui", "gnome", "terminal", "android"],
        )
        expected = {
            "expertise/platforms/android.md",
            "expertise/platforms/apple.md",
            "expertise/platforms/cli.md",
            "expertise/platforms/linux.md",
            "expertise/platforms/web.md",
            "expertise/platforms/windows.md",
        }
        self.assertEqual(set(result["resolved_platform_packs"]), expected)
        self.assertEqual(len(result["resolved_platform_packs"]), len(expected))
        self.assertEqual(result["unresolved_platforms"], [])

    def test_unknown_platform_is_reported_without_loading_the_library(self) -> None:
        result = resolve_expertise(
            "application", "example-001", ["spatial-console-x", "web"]
        )
        self.assertEqual(result["unresolved_platforms"], ["spatial-console-x"])
        self.assertIn("expertise/platforms/web.md", result["paths"])
        loaded_platforms = [
            path for path in result["paths"] if path.startswith("expertise/platforms/")
        ]
        self.assertEqual(loaded_platforms, ["expertise/platforms/web.md"])

    def test_declared_targets_and_cross_platform_strategy_drive_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            local = Path(folder)
            shutil.copytree(ROOT / "expertise", local / "expertise")
            project = local / "projects" / "sample-001" / "project"
            project.mkdir(parents=True)
            (project / "capabilities.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "application_platforms": [
                            "android", "ios", "web", "windows", "linux", "cli"
                        ],
                        "cross_platform_strategy": "flutter",
                    }
                ),
                encoding="utf-8",
            )
            result = resolve_expertise("application", "sample-001", root=local)
        self.assertEqual(len(result["resolved_platform_packs"]), 7)
        self.assertIn("expertise/platforms/cross-platform.md", result["paths"])

    def test_host_export_uses_seed_capabilities_without_platform_flood(self) -> None:
        paths = expertise_paths("example-001", [{"role": "application"}])
        self.assertIn("expertise/roles/application.md", paths)
        self.assertFalse(any(path.startswith("expertise/platforms/") for path in paths))


if __name__ == "__main__":
    unittest.main()
