#!/usr/bin/env python3
"""Detect architectural hotspots (high-complexity modules) in a Python repo.

Usage:
    python tools/detect_hotspots.py [--path DIR] [--loc-threshold N]
        [--func-threshold N] [--import-threshold N]
        [--fan-in-threshold N] [--fan-out-threshold N]

Computes per-file metrics and flags files that exceed thresholds.
Returns structured JSON.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from collections import Counter
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

DEFAULT_THRESHOLDS = {
    "loc": 500,
    "functions": 20,
    "imports": 15,
    "fan_in": 5,
    "fan_out": 8,
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


def _count_lines(filepath: str) -> int:
    """Return the number of lines in *filepath*."""
    try:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def _parse_file(filepath: str) -> ast.Module | None:
    """Parse *filepath*, returning ``None`` on failure."""
    try:
        with open(filepath, encoding="utf-8") as fh:
            return ast.parse(fh.read(), filename=filepath)
    except (OSError, SyntaxError):
        return None


def _count_functions(tree: ast.Module) -> int:
    """Count top-level and nested function/method definitions."""
    return sum(
        1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def _count_classes(tree: ast.Module) -> int:
    """Count class definitions."""
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))


def _extract_imported_modules(tree: ast.Module) -> list[str]:
    """Return list of module names imported by *tree*."""
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
    """Map dotted module name to a known relative file path."""
    candidates = [
        module.replace(".", os.sep) + ".py",
        os.path.join(module.replace(".", os.sep), "__init__.py"),
    ]
    for c in candidates:
        if c in known_files:
            return c
    return None


def _compute_fan_metrics(
    root: str,
    files: list[str],
    known_set: set[str],
) -> tuple[Counter[str], dict[str, int]]:
    """Return (fan_in counter, fan_out dict) for all files."""
    fan_in: Counter[str] = Counter()
    fan_out: dict[str, int] = {}

    for relpath in files:
        tree = _parse_file(os.path.join(root, relpath))
        if tree is None:
            fan_out[relpath] = 0
            continue
        imported = _extract_imported_modules(tree)
        out_count = 0
        for mod in imported:
            target = _module_to_relpath(mod, known_set)
            if target and target != relpath:
                fan_in[target] += 1
                out_count += 1
        fan_out[relpath] = out_count

    return fan_in, fan_out


def detect_hotspots(
    root: str = ".",
    thresholds: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Analyze *root* for architectural hotspots and return metrics."""
    root = os.path.abspath(root)
    thresh = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    files = _discover_python_files(root)
    known_set = set(files)
    fan_in, fan_out = _compute_fan_metrics(root, files, known_set)

    all_metrics: list[dict[str, Any]] = []
    hotspots: list[dict[str, Any]] = []

    for relpath in files:
        abspath = os.path.join(root, relpath)
        loc = _count_lines(abspath)
        tree = _parse_file(abspath)
        n_funcs = _count_functions(tree) if tree else 0
        n_classes = _count_classes(tree) if tree else 0
        imports = _extract_imported_modules(tree) if tree else []
        n_imports = len(imports)
        fi = fan_in.get(relpath, 0)
        fo = fan_out.get(relpath, 0)

        reasons: list[str] = []
        if loc > thresh["loc"]:
            reasons.append(f"high LOC ({loc})")
        if n_funcs > thresh["functions"]:
            reasons.append(f"many functions ({n_funcs})")
        if n_imports > thresh["imports"]:
            reasons.append(f"many imports ({n_imports})")
        if fi > thresh["fan_in"]:
            reasons.append(f"high fan-in ({fi})")
        if fo > thresh["fan_out"]:
            reasons.append(f"high fan-out ({fo})")

        entry: dict[str, Any] = {
            "file": relpath,
            "loc": loc,
            "classes": n_classes,
            "functions": n_funcs,
            "imports": n_imports,
            "fan_in": fi,
            "fan_out": fo,
        }
        all_metrics.append(entry)

        if reasons:
            hotspots.append({**entry, "reasons": reasons})

    hotspots.sort(key=lambda h: len(h["reasons"]), reverse=True)

    return {
        "root": root,
        "total_files": len(files),
        "thresholds": thresh,
        "hotspots": hotspots,
        "all_metrics": all_metrics,
    }


def main(argv: list[str] | None = None) -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(description="Detect architectural hotspots")
    parser.add_argument("--path", default=".", help="Root directory (default: .)")
    parser.add_argument("--loc-threshold", type=int, default=DEFAULT_THRESHOLDS["loc"])
    parser.add_argument("--func-threshold", type=int, default=DEFAULT_THRESHOLDS["functions"])
    parser.add_argument("--import-threshold", type=int, default=DEFAULT_THRESHOLDS["imports"])
    parser.add_argument("--fan-in-threshold", type=int, default=DEFAULT_THRESHOLDS["fan_in"])
    parser.add_argument("--fan-out-threshold", type=int, default=DEFAULT_THRESHOLDS["fan_out"])
    args = parser.parse_args(argv)

    thresholds = {
        "loc": args.loc_threshold,
        "functions": args.func_threshold,
        "imports": args.import_threshold,
        "fan_in": args.fan_in_threshold,
        "fan_out": args.fan_out_threshold,
    }

    result = detect_hotspots(root=args.path, thresholds=thresholds)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
