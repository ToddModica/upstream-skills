"""Offline release checks for the files produced by sync_sources.py."""
import ast
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PLUGINS = Path(__file__).resolve().parents[1] / "plugins"
SKILL = PLUGINS / "research-toolkit/skills/nature-academic-search"


class MarketplaceCompatibility(unittest.TestCase):
    def test_academic_launch_and_scopus_defaults(self):
        snippet = json.loads((SKILL / "config/mcp-snippet.json").read_text(encoding="utf-8"))
        args = snippet["mcpServers"]["academic-search"]["args"]
        self.assertEqual(args[args.index("--with-requirements") + 1], "requirements.txt")
        server = SKILL / "mcp-server"
        self.assertIn("defusedxml", (server / "requirements.txt").read_text(encoding="utf-8"))
        for source in ("sources/arxiv.py", "sources/pubmed.py"):
            tree = ast.parse((server / source).read_text(encoding="utf-8"))
            wrappers = {alias.asname for n in ast.walk(tree) if isinstance(n, ast.Import)
                        for alias in n.names if alias.name == "defusedxml.ElementTree"}
            for attr in (n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == "Element"):
                if isinstance(attr.value, ast.Name):
                    self.assertNotIn(attr.value.id, wrappers, f"{source}: use the stdlib Element type")
        for module, name in [("academic_search_server.py", "search_scopus"), ("sources/scopus.py", "search")]:
            tree = ast.parse((server / module).read_text(encoding="utf-8"))
            fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
            defaults = dict(zip([a.arg for a in fn.args.args][-len(fn.args.defaults):], fn.args.defaults))
            self.assertIs(ast.literal_eval(defaults["subscriber"]), False)

    def test_zcode_hooks(self):
        for name, events in [("ponytail", {"SessionStart", "UserPromptSubmit"}),
                             ("no-negative-echo", {"SessionStart"})]:
            root = PLUGINS / name
            manifest = json.loads((root / ".zcode-plugin/plugin.json").read_text(encoding="utf-8"))
            codex = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], codex["version"])
            self.assertFalse((root / "hooks/hooks.json").exists(), "ZCode auto-loads this file too")
            self.assertEqual(set(manifest["hooks"]), events)
            with tempfile.TemporaryDirectory() as data:
                env = dict(os.environ, ZCODE_PLUGIN_ROOT=str(root), ZCODE_PLUGIN_DATA=data,
                           PONYTAIL_DEFAULT_MODE="full", PONYTAIL_MAP="0")
                for event in events:
                    hook, = manifest["hooks"][event][0]["hooks"]
                    argv = [hook["command"], *[a.replace("${ZCODE_PLUGIN_ROOT}", str(root)) for a in hook["args"]]]
                    cases = [("hello", "PONYTAIL MODE ACTIVE" if name == "ponytail" else "NO_NEGATIVE_ECHO:ACTIVE")]
                    if event == "UserPromptSubmit":
                        cases = [("hello", None), ("/ponytail lite", "PONYTAIL MODE CHANGED")]
                    for prompt, marker in cases:
                        output = subprocess.check_output(argv, input=json.dumps({"source": "startup", "prompt": prompt}),
                                                         cwd=data, env=env, encoding="utf-8", timeout=10)
                        result = json.loads(output)
                        if marker is None:
                            self.assertEqual(result, {})
                        else:
                            context = result["hookSpecificOutput"]
                            self.assertEqual(context["hookEventName"], event)
                            self.assertIn(marker, context["additionalContext"])


if __name__ == "__main__":
    unittest.main()
