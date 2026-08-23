from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AgentSkillPackagingTest(unittest.TestCase):
    def test_lattice_execution_skill_uses_open_skill_shape(self) -> None:
        path = ROOT / ".agents" / "skills" / "lattice-execution" / "SKILL.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(frontmatter)
        body = frontmatter.group("body")
        self.assertIn("name: lattice-execution", body)
        self.assertRegex(body, r"(?m)^description: .+")
        self.assertIn("python3 scripts/lattice.py expertise", text)
        self.assertIn("scripts/host_adapter.py", text)
        self.assertIn("does not grant authority", text)
        self.assertNotIn("state/current.json` directly", text)

    def test_github_adapter_points_to_canonical_kernel_and_shared_skill(self) -> None:
        path = ROOT / "adapters" / "github" / "README.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("root `AGENTS.md`", text)
        self.assertIn(".agents/skills/lattice-execution/SKILL.md", text)
        self.assertIn("scripts/host_adapter.py", text)
        self.assertIn("does not by itself satisfy", text)
        self.assertNotIn("copy the Agency Kernel", text)

    def test_adapter_index_registers_github_without_host_specific_policy(self) -> None:
        text = (ROOT / "adapters" / "README.md").read_text(encoding="utf-8")
        self.assertIn("`github/`", text)
        self.assertIn("Reusable execution technique lives under `.agents/skills/`", text)
        self.assertIn("must not copy the Agency Kernel", text)


if __name__ == "__main__":
    unittest.main()
