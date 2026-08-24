from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from provider_setup import resolve_model, runtime_model_status, save_model_preferences, save_provider


class ProviderSetupTest(unittest.TestCase):
    def test_credentials_stay_out_of_status_and_roles_can_use_different_models(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"LATTICE_CONFIG_DIR": temporary}, clear=False):
            save_provider("openai", "openai-secret-value")
            save_provider("anthropic", "anthropic-secret-value")
            save_model_preferences(
                "openai",
                "gpt-architecture-default",
                {
                    "experience": {"provider": "anthropic", "model": "claude-interface"},
                    "architecture": {"provider": "openai", "model": "gpt-architecture"},
                },
            )
            status = runtime_model_status()
            encoded = json.dumps(status)
            self.assertTrue(status["configured"])
            self.assertNotIn("openai-secret-value", encoded)
            self.assertNotIn("anthropic-secret-value", encoded)
            self.assertEqual(resolve_model("experience"), {"provider": "anthropic", "model": "claude-interface"})
            self.assertEqual(resolve_model("architecture"), {"provider": "openai", "model": "gpt-architecture"})
            self.assertEqual(resolve_model("services"), {"provider": "openai", "model": "gpt-architecture-default"})

    def test_unconfigured_provider_cannot_be_assigned(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"LATTICE_CONFIG_DIR": temporary}, clear=False):
            save_provider("openai", "secret")
            with self.assertRaisesRegex(ValueError, "unconfigured provider"):
                save_model_preferences("openai", "gpt", {"experience": {"provider": "anthropic", "model": "claude"}})


if __name__ == "__main__":
    unittest.main()
