import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install_windows_mcp as installer
import update_mcp_pins as pins


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
            run.return_value.stderr = b"magpie: no server called windows-mcp"
            self.assertEqual(installer.register(check_only=False), 0)
            command = run.call_args_list[-2].args[0]
            self.assertEqual(command[:5], ["magpie.com", "library", "mcp", "add", installer.NAME])
            self.assertIn("--local", command)
            self.assertIn("agents=codex", command)
            self.assertEqual(command[-len(installer.ARGS):], installer.ARGS)
            self.assertEqual(
                run.call_args.args[0],
                ["magpie.com", "library", "mcp", "router", installer.NAME, "direct"],
            )

            run.reset_mock()
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({
                "local": True, "transport": "stdio", "command": "uvx", "agents": ["codex"],
                "args": installer.ARGS, "hub": "direct",
            })
            self.assertEqual(installer.register(check_only=True), 0)
            run.assert_called_once()

    def test_existing_magpie_pin_is_warmed_before_upgrade(self):
        old = {
            "name": installer.NAME, "transport": "stdio", "command": "uvx.exe",
            "local": True, "agents": ["codex", "dsh"], "hub": "direct",
            "args": ["--system-certs", "windows-mcp==0.0.1", "serve", "--transport", "stdio"],
        }
        with (
            patch.object(sys, "platform", "win32"),
            patch.object(installer.shutil, "which", side_effect=lambda name: name),
            patch.object(installer.subprocess, "run") as run,
            patch.object(installer, "upgrade_magpie") as upgrade,
        ):
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps(old)
            self.assertEqual(installer.register(check_only=True), 1)
            upgrade.assert_not_called()
            run.reset_mock()
            run.side_effect = [
                run.return_value,
                subprocess.CalledProcessError(1, "uvx"),
            ]
            with self.assertRaises(subprocess.CalledProcessError):
                installer.register(check_only=False)
            upgrade.assert_not_called()
            run.side_effect = None
            self.assertEqual(installer.register(check_only=False), 0)
            self.assertEqual(run.call_args.args[0], ["uvx.exe", *installer.ARGS, "--help"])
            upgrade.assert_called_once_with("magpie.com", old, installer.ARGS)

    def test_magpie_upgrade_preserves_library_and_rolls_back_on_sync_failure(self):
        current = {
            "name": installer.NAME, "command": "uvx", "transport": "stdio",
            "args": ["--system-certs", "windows-mcp==0.0.1", "serve", "--transport", "stdio"],
            "local": True, "agents": ["codex", "dsh", "zcode"], "hub": "direct",
            "env": {"ANONYMIZED_TELEMETRY": "false"}, "startupTimeout": 90,
        }
        library = {"mcp": [current, {"name": "unrelated"}], "skills": [{"name": "keep"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "library.json"
            path.write_text(json.dumps(library), encoding="utf-8")
            with (
                patch.object(installer.subprocess, "check_output", return_value=f"files: {path.parent}\n".encode()),
                patch.object(installer.subprocess, "run") as run,
            ):
                run.side_effect = [subprocess.CalledProcessError(1, "magpie"), None]
                with self.assertRaises(subprocess.CalledProcessError):
                    installer.upgrade_magpie("magpie", current, installer.ARGS)
                self.assertEqual(json.loads(path.read_bytes()), library)
                run.side_effect = None
                installer.upgrade_magpie("magpie", current, installer.ARGS)
                updated = json.loads(path.read_bytes())
                self.assertEqual(updated["mcp"][0]["args"], installer.ARGS)
                updated["mcp"][0]["args"] = current["args"]
                self.assertEqual(updated, library)


class WindowsMcpPinTests(unittest.TestCase):
    def test_pin_follows_newer_stable_pypi_release_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pin.txt"
            path.write_text("0.8.9\n", encoding="ascii")
            with patch.object(pins, "WINDOWS_MCP_PIN", path), patch.object(pins, "registry_json") as registry:
                for version, yanked, updated in (
                    ("0.8.8", False, False),
                    ("0.9.0rc1", False, False),
                    ("0.9.0", True, False),
                    ("0.9.0", False, True),
                ):
                    with self.subTest(version=version, yanked=yanked):
                        registry.return_value = {
                            "info": {"name": "windows-mcp", "version": version},
                            "urls": [{"filename": "windows_mcp.whl", "yanked": yanked}],
                        }
                        self.assertEqual(pins.refresh_windows_mcp(), updated)
                        self.assertEqual(path.read_text(encoding="ascii").strip(), "0.9.0" if updated else "0.8.9")


if __name__ == "__main__":
    unittest.main()
