import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install_windows_mcp as installer


class WindowsMcpInstallTests(unittest.TestCase):
    def test_non_windows_skips_runtime_and_registration(self):
        for platform in ("darwin", "linux"):
            with (
                self.subTest(platform=platform),
                patch.object(sys, "platform", platform),
                patch.object(installer.shutil, "which") as which,
                patch.object(installer.subprocess, "run") as run,
            ):
                self.assertEqual(installer.register(check_only=False), 0)
                which.assert_not_called()
                run.assert_not_called()

    def test_magpie_registration_is_local_and_check_only(self):
        with (
            patch.object(sys, "platform", "win32"),
            patch.object(installer.shutil, "which", side_effect=lambda name: name),
            patch.object(installer.subprocess, "run") as run,
        ):
            run.return_value.returncode = 1
            self.assertEqual(installer.register(check_only=False), 0)
            command = run.call_args.args[0]
            self.assertEqual(command[:5], ["magpie.com", "library", "mcp", "add", installer.NAME])
            self.assertIn("--local", command)
            self.assertIn("agents=codex", command)
            self.assertEqual(command[-len(installer.ARGS):], installer.ARGS)

            run.reset_mock()
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({
                "local": True, "agents": ["codex"], "args": installer.ARGS,
            })
            self.assertEqual(installer.register(check_only=True), 0)
            run.assert_called_once()
