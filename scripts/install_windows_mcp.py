#!/usr/bin/env python3
"""Register the Windows desktop MCP for Codex on this computer."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


NAME = "windows-mcp"
VERSION = Path(__file__).with_name("windows_mcp_version.txt").read_text(encoding="ascii").strip()
ARGS = ["--system-certs", f"{NAME}=={VERSION}", "serve", "--transport", "stdio"]
TELEMETRY = "ANONYMIZED_TELEMETRY=false"


def version_from_args(args):
    if not isinstance(args, list) or len(args) != len(ARGS) or args[:1] + args[2:] != ARGS[:1] + ARGS[2:]:
        return None
    match = re.fullmatch(r"windows-mcp==(\d+\.\d+\.\d+)", args[1]) if isinstance(args[1], str) else None
    return match[1] if match else None


def replace_library_args(path, expected, args):
    original = path.read_bytes()
    contents = json.loads(original)
    entries = [entry for entry in contents.get("mcp", []) if entry.get("name") == NAME]
    if entries != [expected]:
        raise ValueError("The Magpie Windows MCP entry changed while preparing the update; retry sync")
    entry = entries[0]
    entry["args"] = args
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        pending = Path(stream.name)
        json.dump(contents, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    try:
        if path.read_bytes() != original:
            raise ValueError("Magpie Library changed during the update; retry sync")
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)
    return entry


def upgrade_magpie(magpie, current, args):
    location = subprocess.check_output([magpie, "data"], timeout=15).decode("utf-8")
    folder = next((Path(line[7:].strip()) for line in location.splitlines() if line.startswith("files: ")), None)
    if folder is None or not folder.is_absolute():
        raise ValueError("Could not locate the Magpie Library from 'magpie data'")
    path = (folder / "library.json").resolve(strict=True)
    updated = replace_library_args(path, current, args)
    sync = [magpie, "library", "sync"]
    try:
        result = subprocess.run(sync, capture_output=True, check=True, timeout=60)
        problems = tuple(f"! {agent} mcp" for agent in current.get("agents", []))
        if any(line.startswith(problems) for line in result.stdout.decode("utf-8", errors="replace").splitlines()):
            raise ValueError("Magpie could not synchronize an assigned agent's MCP configuration")
    except (OSError, ValueError, subprocess.SubprocessError):
        replace_library_args(path, updated, current["args"])
        subprocess.run(sync, check=True, timeout=60)
        raise


def register(check_only):
    if sys.platform != "win32":
        print("Windows MCP is available on Windows only.")
        return 0

    if not re.fullmatch(r"\d+\.\d+\.\d+", VERSION):
        raise ValueError("Invalid Windows MCP version pin")
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
    result = subprocess.run(lookup, capture_output=True, timeout=15)
    current = json.loads(result.stdout) if result.returncode == 0 else None
    if current is None:
        expected = "no server called" if magpie else "no mcp server named"
        if expected not in result.stderr.decode("utf-8", errors="replace").lower():
            raise ValueError(f"Could not read Windows MCP registration from {owner}")
    installed = None
    if current is not None:
        if magpie:
            installed = version_from_args(current.get("args"))
            ready = (
                current.get("local") is True
                and current.get("transport") == "stdio"
                and Path(current.get("command", "")).name.lower() in {"uvx", "uvx.exe"}
                and installed is not None
            )
        else:
            ready = current.get("enabled", True) and current.get("transport", {}).get("args") == ARGS
        if not ready:
            print(f"Windows MCP has a different registration in {owner}.", file=sys.stderr)
            return 1
    elif check_only:
        print(f"Windows MCP is missing from {owner}.", file=sys.stderr)
        return 1

    if installed is not None and installed != VERSION:
        if tuple(map(int, installed.split("."))) >= tuple(map(int, VERSION.split("."))):
            print(f"Windows MCP {installed} already meets the Marketplace pin {VERSION}.")
            return 0
        if check_only:
            print(f"Windows MCP {installed} needs an update to {VERSION}.", file=sys.stderr)
            return 1

    if not check_only:
        # Warm the new version before changing any agent's configuration.
        launcher = current["command"] if magpie and current is not None else uvx
        subprocess.run([launcher, *ARGS, "--help"], stdout=subprocess.DEVNULL, check=True, timeout=120)
        if current is None:
            subprocess.run(install, check=True, timeout=90)
            if magpie:
                subprocess.run([*library, "router", NAME, "direct"], check=True, timeout=25)
        elif installed is not None and installed != VERSION:
            upgrade_magpie(magpie, current, ARGS)
            print(f"Windows MCP updated from {installed} to {VERSION} in Magpie Library.")
            return 0
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
