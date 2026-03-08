#!/usr/bin/env python3
"""Scan a repository to discover Python files and generate structured previews.

Usage:
    python tools/scan_repo.py [--path DIR] [--max-preview-lines N] [--json]

Returns JSON with file paths, types, and first-N-line previews.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "node_modules",
    ".tox",
    "dist",
    "build",
    "egg-info",
}


def discover_python_files(root: str) -> list[str]:
    """Walk *root* and return sorted list of ``*.py`` file paths (relative to *root*).

    Skips directories listed in ``IGNORE_DIRS``.
    """
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                full = os.path.join(dirpath, fname)
                found.append(os.path.relpath(full, root))
    found.sort()
    return found


def file_type(filepath: str) -> str:
    """Return a human-readable file-type string via ``file(1)``."""
    try:
        result = subprocess.run(
            ["file", "--brief", filepath],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def head_lines(filepath: str, n: int = 50) -> str:
    """Return the first *n* lines of *filepath*."""
    lines: list[str] = []
    try:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= n:
                    break
                lines.append(line.rstrip("\n"))
    except OSError:
        return ""
    return "\n".join(lines)


def scan(root: str = ".", max_preview: int = 50) -> dict[str, Any]:
    """Scan *root* for Python files and return structured metadata."""
    root = os.path.abspath(root)
    files = discover_python_files(root)
    records: list[dict[str, str]] = []
    for relpath in files:
        abspath = os.path.join(root, relpath)
        records.append(
            {
                "path": relpath,
                "type": file_type(abspath),
                "preview": head_lines(abspath, max_preview),
            }
        )
    return {"root": root, "total_files": len(records), "files": records}


def main(argv: list[str] | None = None) -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(description="Scan repo for Python files")
    parser.add_argument(
        "--path",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--max-preview-lines",
        type=int,
        default=50,
        help="Number of preview lines per file (default: 50)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Output as JSON (default: true)",
    )
    args = parser.parse_args(argv)
    result = scan(root=args.path, max_preview=args.max_preview_lines)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
