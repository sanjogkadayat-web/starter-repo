# Scout — Codebase Exploration Skill

A Cursor Agent Skill that enables an AI agent to explore, analyze, and document
Python codebases.

## Quick Start

1. Place this skill in `.cursor/skills/scout/` (already done if you cloned this repo).
2. In Cursor, the agent will auto-discover the skill when you ask it to
   "explore this codebase", "analyze the architecture", or "generate an
   ARCHITECTURE.md".

## What It Does

| Tool | Purpose | Output |
|------|---------|--------|
| `scan_repo.py` | Discover Python files, preview first N lines | `{ files: [{ path, type, preview }] }` |
| `analyze_python_file.py` | AST analysis of one file | `{ classes, functions, imports, calls }` |
| `build_dependency_graph.py` | Import-based dependency edges | `{ edges: [{ from, to }] }` |
| `detect_hotspots.py` | Complexity metrics and flag hotspots | `{ hotspots: [{ file, loc, fan_in, fan_out, reasons }] }` |

## Agent Workflow

The agent follows this sequence automatically:

1. **Scan** — `scan_repo.py` to discover files
2. **Summarize** — AI generates one-line summaries per file
3. **Dependency graph** — `build_dependency_graph.py` to map imports
4. **Architecture diagram** — AI generates Mermaid `graph TD`
5. **Hotspots** — `detect_hotspots.py` to flag complex modules
6. **User selection** — agent asks which file to deep-analyze
7. **AST analysis** — `analyze_python_file.py` on selected file
8. **Class & call diagrams** — AI generates Mermaid diagrams
9. **ARCHITECTURE.md** — AI compiles everything into a document

## Running Tools Directly

All tools are standalone Python scripts with no external dependencies
(stdlib only).

```bash
# Scan the repo
python .cursor/skills/scout/tools/scan_repo.py --path src/

# Analyze a single file
python .cursor/skills/scout/tools/analyze_python_file.py src/main.py

# Build dependency graph
python .cursor/skills/scout/tools/build_dependency_graph.py --path src/

# Detect hotspots (custom thresholds)
python .cursor/skills/scout/tools/detect_hotspots.py --path src/ \
    --loc-threshold 300 --fan-in-threshold 3
```

## Directory Structure

```
.cursor/skills/scout/
├── SKILL.md                          # Skill definition (agent reads this)
├── architecture-template.md          # Template for generated docs
├── README.md                         # This file
└── tools/
    ├── __init__.py
    ├── scan_repo.py                  # Repo scanner
    ├── analyze_python_file.py        # AST analyzer
    ├── build_dependency_graph.py     # Dependency graph builder
    └── detect_hotspots.py            # Hotspot detector
```

## Example Usage in Cursor

Open Cursor and type any of these prompts:

- "Scout this repo and show me the architecture"
- "Use the scout skill to explore the codebase"
- "Analyze the architecture and generate ARCHITECTURE.md"
- "What are the hotspots in this project?"
- "Show me the dependency graph for src/"

The agent will read `SKILL.md`, run the tools, and produce summaries,
Mermaid diagrams, and documentation.

## Dependencies

**None** — all tools use Python standard library only (`ast`, `os`, `json`,
`subprocess`, `argparse`).

## Output Format

All tools return structured JSON to stdout. The agent interprets the JSON
and generates:

- File summary tables
- Mermaid architecture diagrams (`graph TD`)
- Mermaid class diagrams (`classDiagram`)
- Mermaid call graphs (`flowchart TD`)
- A complete `ARCHITECTURE.md` document
