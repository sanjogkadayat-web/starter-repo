#!/usr/bin/env python3
"""Analyze a single Python file using the ``ast`` module.

Usage:
    python tools/analyze_python_file.py <filepath>

Extracts classes, functions, imports, and intra-file call relationships.
Returns structured JSON.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from typing import Any


class _CallVisitor(ast.NodeVisitor):
    """Collect function-call edges within each function/method body."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []
        self._current_func: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        prev = self._current_func
        self._current_func = node.name
        self.generic_visit(node)
        self._current_func = prev

    visit_AsyncFunctionDef = visit_FunctionDef  # treat async defs identically

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        callee = self._resolve_call_name(node.func)
        if callee and self._current_func:
            self.calls.append({"caller": self._current_func, "callee": callee})
        self.generic_visit(node)

    @staticmethod
    def _resolve_call_name(node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = [node.attr]
            current: ast.expr = node.value
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        return None


def _extract_imports(tree: ast.Module) -> list[dict[str, Any]]:
    """Return a list of import records from *tree*."""
    imports: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"module": alias.name, "alias": alias.asname, "kind": "import"})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(
                    {
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "kind": "from",
                    }
                )
    return imports


def _extract_classes(tree: ast.Module) -> list[dict[str, Any]]:
    """Return class definitions with their methods."""
    classes: list[dict[str, Any]] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                n.name
                for n in ast.iter_child_nodes(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(ast.dump(base))
            classes.append(
                {
                    "name": node.name,
                    "bases": bases,
                    "methods": methods,
                    "lineno": node.lineno,
                }
            )
    return classes


def _extract_functions(tree: ast.Module) -> list[dict[str, Any]]:
    """Return top-level function definitions."""
    funcs: list[dict[str, Any]] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            funcs.append(
                {
                    "name": node.name,
                    "args": args,
                    "lineno": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                }
            )
    return funcs


def analyze(filepath: str) -> dict[str, Any]:
    """Parse *filepath* and return structured analysis."""
    with open(filepath, encoding="utf-8") as fh:
        source = fh.read()

    tree = ast.parse(source, filename=filepath)

    visitor = _CallVisitor()
    visitor.visit(tree)

    return {
        "file": filepath,
        "classes": _extract_classes(tree),
        "functions": _extract_functions(tree),
        "imports": _extract_imports(tree),
        "calls": visitor.calls,
    }


def main(argv: list[str] | None = None) -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(description="Analyze a Python file via AST")
    parser.add_argument("filepath", help="Path to the Python file")
    args = parser.parse_args(argv)

    try:
        result = analyze(args.filepath)
    except (OSError, SyntaxError) as exc:
        json.dump({"error": str(exc)}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
