#!/usr/bin/env python3
"""Build a dependency graph from import statements across a Python repository.

Usage:
    python tools/build_dependency_graph.py [--path DIR]

Returns JSON with directed edges ``{"from": <file>, "to": <module>}``.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
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


def _discover_python_files(root: str) -> list[str]:
    """Return sorted list of ``*.py`` file paths relative to *root*."""
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            if fname.endswith(".py"):
                full = os.path.join(dirpath, fname)
                found.append(os.path.relpath(full, root))
    found.sort()
    return found


def _extract_imports_from_file(filepath: str) -> list[str]:
    """Parse *filepath* and return module names from all import statements."""
    try:
        with open(filepath, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=filepath)
    except (OSError, SyntaxError):
        return []

    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules


def _module_to_relpath(module: str, known_files: set[str]) -> str | None:
    """Attempt to map a dotted module name to a known relative file path.

    Returns the relative path if found, otherwise ``None``.
    """
    candidates = [
        module.replace(".", os.sep) + ".py",
        os.path.join(module.replace(".", os.sep), "__init__.py"),
    ]
    for candidate in candidates:
        if candidate in known_files:
            return candidate
    return None


def build_graph(root: str = ".") -> dict[str, Any]:
    """Build dependency graph for all Python files under *root*."""
    root = os.path.abspath(root)
    files = _discover_python_files(root)
    known_set = set(files)

    edges: list[dict[str, str]] = []
    external_deps: set[str] = set()

    for relpath in files:
        abspath = os.path.join(root, relpath)
        imported_modules = _extract_imports_from_file(abspath)
        for mod in imported_modules:
            target = _module_to_relpath(mod, known_set)
            if target:
                edges.append({"from": relpath, "to": target})
            else:
                edges.append({"from": relpath, "to": mod})
                external_deps.add(mod)

    unique_edges = list({(e["from"], e["to"]): e for e in edges}.values())
    unique_edges.sort(key=lambda e: (e["from"], e["to"]))

    return {
        "root": root,
        "total_files": len(files),
        "total_edges": len(unique_edges),
        "edges": unique_edges,
        "external_dependencies": sorted(external_deps),
    }


def main(argv: list[str] | None = None) -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(description="Build Python dependency graph")
    parser.add_argument(
        "--path",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    args = parser.parse_args(argv)
    result = build_graph(root=args.path)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
