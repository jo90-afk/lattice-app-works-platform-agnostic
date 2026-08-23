from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from hooks import dispatch_hooks  # noqa: E402
from state_engine import LatticeError  # noqa: E402


class HookDispatchTest(unittest.TestCase):
    def test_hooks_run_in_declaration_order_with_event_on_stdin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "runtime").mkdir()
            sink = root / "sink.txt"
            hook = root / "hook.py"
            hook.write_text(
                "import json, pathlib, sys\n"
                "label, target = sys.argv[1], pathlib.Path(sys.argv[2])\n"
                "event = json.loads(sys.stdin.read())\n"
                "with target.open('a', encoding='utf-8') as stream:\n"
                "    stream.write(label + ':' + event['event_type'] + '\\n')\n",
                encoding="utf-8",
            )
            (root / "runtime" / "hooks.json").write_text(
                json.dumps({
                    "action_claimed": [
                        [sys.executable, str(hook), "first", str(sink)],
                        [sys.executable, str(hook), "second", str(sink)],
                    ]
                }),
                encoding="utf-8",
            )
            results = dispatch_hooks(root, "action_claimed", {"event_type": "action_claimed"})
            self.assertEqual([row["returncode"] for row in results], [0, 0])
            self.assertEqual(sink.read_text(encoding="utf-8"), "first:action_claimed\nsecond:action_claimed\n")

    def test_hook_failure_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "runtime").mkdir()
            (root / "runtime" / "hooks.json").write_text(
                json.dumps({"policy_checked": [[sys.executable, "-c", "import sys; sys.exit(7)"]]}),
                encoding="utf-8",
            )
            with self.assertRaises(LatticeError):
                dispatch_hooks(root, "policy_checked", {"event_type": "policy_checked"})


if __name__ == "__main__":
    unittest.main()
