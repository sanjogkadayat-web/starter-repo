# copilot-agent-skills

A collection of reusable GitHub Copilot agent skills and slash commands for code exploration, architecture review, and skill authoring.

Drop the `.github/` folder into any repository to activate all skills and commands in Copilot agent mode.

---

## Skills

Skills live in `.github/skills/` and are invoked by typing `/skill-name` in Copilot Chat (agent mode).

### `/scout`
Explore and analyze a Python codebase — scan repo structure, build dependency graphs, detect architecture hotspots, and generate Mermaid diagrams.

**When to use:** When you want to map or document a Python project's architecture.  
**Output:** `ARCHITECTURE.md` with system diagrams, module summaries, and hotspot annotations.  
**Tools included:** `scan_repo.py`, `build_dependency_graph.py`, `detect_hotspots.py`, `analyze_python_file.py`

### `/trace`
Audit the full decision path from spec → implementation → output. Reveals implicit assumptions and lists project-specific landmines.

**When to use:** After `/scout` and `/review` have been run; when you want to understand *why* something was built a certain way and *what could break*.  
**Output:** `reports/trace_YYYYMMDD_HHMMSS.md` with a decision flow diagram, assumption challenges, ranked landmines, and drift detection.  
**Requires:** `ARCHITECTURE.md` (from `/scout`) and an Architecture Review Report (from `/review`).

### `/add-skill`
Create a new SKILL.md, turn an existing workflow into a reusable skill, or refine how a skill should trigger and what it should produce.

**When to use:** When you want to package a repeatable workflow as a Copilot skill.

### `/skill-finder`
Search the [awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) catalog and return a ranked match report for a workflow or capability you describe.

**When to use:** Before building a new skill — check whether one already exists.

---

## Slash Commands

Commands live in `.github/prompts/` and are invoked with `/command-name` in Copilot Chat.

| Command | Purpose |
|---|---|
| `/review` | Architectural review agent — cross-checks `ARCHITECTURE.md` against specs, plans, and design principles. Saves report to `reports/arch_review_YYYYMMDD_HHMMSS.md`. |
| `/conclude` | Saves the current implementation plan status to memory for future reference. |
| `/followup` | Generates follow-up code or completions based on the current spec context. |
| `/handoff` | Produces a structured markdown handoff prompt summarising the current implementation state. |

---

## Recommended Workflow

```
/scout   →   /review   →   /trace
```

1. **`/scout`** — Map the codebase. Generates `ARCHITECTURE.md`.
2. **`/review`** — Cross-check architecture against specs and design principles. Generates `reports/arch_review_*.md`.
3. **`/trace`** — Audit the full decision path against the outputs of both. Generates `reports/trace_*.md`.

---

## Installation

```bash
# Copy into your repo
cp -r .github /path/to/your-repo/

# Or add as a git subtree
git subtree add --prefix .github https://github.com/<org>/copilot-agent-skills main --squash
```

All skills and commands activate automatically in Copilot Chat agent mode — no additional configuration required.

---

## Requirements

- GitHub Copilot with **agent mode** enabled
- VS Code with the GitHub Copilot extension
- Python 3.9+ (for `/scout` and `/trace` render scripts)
