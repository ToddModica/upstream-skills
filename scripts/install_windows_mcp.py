#!/usr/bin/env python3
"""Register the Windows desktop MCP for Codex on this computer."""

import argparse
import json
import shutil
import subprocess
import sys


NAME = "windows-mcp"
VERSION = "0.9.0"
ARGS = ["--system-certs", f"{NAME}=={VERSION}", "serve", "--transport", "stdio"]
TELEMETRY = "ANONYMIZED_TELEMETRY=false"


def register(check_only):
    if sys.platform != "win32":
        print("Windows MCP is available on Windows only.")
        return 0

    uvx = shutil.which("uvx")
    codex = shutil.which("codex")
    if not uvx or not codex:
        print("Windows MCP requires uvx and Codex CLI on PATH.", file=sys.stderr)
        return 1

    magpie = shutil.which("magpie.com") or shutil.which("magpie")
    if magpie:
        library = [magpie, "library", "mcp"]
        lookup = [*library, "show", NAME]
        install = [
            *library, "add", NAME, "agents=codex", "--local", f"env={TELEMETRY}",
            "timeout=90", "--", uvx, *ARGS,
        ]
    else:
        lookup = [codex, "mcp", "get", NAME, "--json"]
        install = [codex, "mcp", "add", NAME, "--env", TELEMETRY, "--", uvx, *ARGS]
    owner = "Magpie Library" if magpie else "Codex"
    result = subprocess.run(lookup, capture_output=True, timeout=30)
    current = json.loads(result.stdout) if result.returncode == 0 else None
    if current is not None:
        if magpie:
            ready = (
                current.get("local") is True
                and "codex" in current.get("agents", [])
                and not current.get("disabled", False)
                and current.get("args") == ARGS
            )
        else:
            ready = current.get("enabled", True) and current.get("transport", {}).get("args") == ARGS
        if not ready:
            print(f"Windows MCP has a different registration in {owner}.", file=sys.stderr)
            return 1
    elif check_only:
        print(f"Windows MCP is missing from {owner}.", file=sys.stderr)
        return 1

    if not check_only:
        # Populate uv's cache before the first client handshake.
        subprocess.run([uvx, *ARGS, "--help"], stdout=subprocess.DEVNULL, check=True, timeout=180)
        if result.returncode:
            subprocess.run(install, check=True, timeout=90)
    if magpie and (current is None or current.get("hub") != "direct"):
        if check_only:
            print("Windows MCP is not configured for local launch by Codex.", file=sys.stderr)
            return 1
        subprocess.run([*library, "router", NAME, "direct"], check=True, timeout=25)
    print(f"Windows MCP {VERSION} registered in {owner}.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="inspect registration without installing")
    try:
        return register(parser.parse_args().check_only)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Windows MCP setup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
