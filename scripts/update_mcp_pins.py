#!/usr/bin/env python3
"""Refresh the pinned npm package version used by the bundled MCP servers."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = (
    {
        "file": ROOT / "plugins/playwright-mcp/.mcp.json",
        "server": "playwright",
        "package": "@playwright/mcp",
    },
)
REGISTRY = "https://registry.npmjs.org/{package}/latest"
TIMEOUT_SECONDS = 30


def parse_version(value: str) -> tuple[int, int, int] | None:
    base = value.split("+", 1)[0]
    if "-" in base:
        return None
    parts = base.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0]), int(parts[1]), int(parts[2])


def latest_version(package: str) -> str | None:
    request = urllib.request.Request(
        REGISTRY.format(package=package.replace("/", "%2F")),
        headers={"Accept": "application/json", "User-Agent": "upstream-skills-pin-refresh"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"WARNING: could not read the latest version of {package}: {error}", file=sys.stderr)
        return None
    version = payload.get("version")
    return str(version) if version else None


def refresh(pin: dict[str, object]) -> bool:
    path = Path(str(pin["file"]))
    package = str(pin["package"])
    server_name = str(pin["server"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    args = payload.get("mcpServers", {}).get(server_name, {}).get("args", [])
    prefix = f"{package}@"
    current = next((str(arg)[len(prefix):] for arg in args if str(arg).startswith(prefix)), None)
    if current is None:
        print(f"WARNING: {path.relative_to(ROOT)} does not pin {package}", file=sys.stderr)
        return False
    latest = latest_version(package)
    if latest is None or latest == current:
        print(f"{package}: {current} is current")
        return False
    current_version, latest_version_tuple = parse_version(current), parse_version(latest)
    if current_version and latest_version_tuple and latest_version_tuple <= current_version:
        print(f"{package}: {current} is current")
        return False
    payload["mcpServers"][server_name]["args"] = [
        f"{prefix}{latest}" if str(arg).startswith(prefix) else arg for arg in args
    ]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{package}: {current} -> {latest}")
    return True


def main() -> int:
    for pin in PINS:
        refresh(pin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
