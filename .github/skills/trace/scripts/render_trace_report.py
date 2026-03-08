#!/usr/bin/env python3
"""Render a Trace Report markdown document from agent-produced structured JSON.

Usage:
    python render_trace_report.py <trace_json> [--output <md_path>]

The agent performs all semantic reasoning (Steps 1–7 in SKILL.md) and writes
its findings to a structured JSON file. This script deterministically renders
that JSON into the final Trace Report using assets/trace_report_template.md.

JSON input schema:
{
  "project_name": "string",
  "architecture_path": "string",
  "review_path": "string",
  "output_path": "string",
  "decisions": [
    {
      "id": "D1",
      "description": "string",
      "category": "TECHNOLOGY|ARCHITECTURE|DATA|SCOPE|PROCESS|OUTPUT",
      "source": "spec|plan|architecture|ad-hoc",
      "chosen": "string",
      "alternatives": ["string"],
      "is_drift": false
    }
  ],
  "assumptions": [
    {
      "decision_id": "D1",
      "assumption": "string",
      "challenge_question": "string",
      "risk_level": "high|medium|low"
    }
  ],
  "landmines": [
    {
      "rank": 1,
      "name": "string",
      "trigger_condition": "string",
      "impact": "string",
      "mitigation": "string",
      "risk_level": "high|medium|low"
    }
  ],
  "drift": {
    "detected": false,
    "items": [
      {
        "planned": "string",
        "actual": "string",
        "drift_type": "intentional|accidental|improvement",
        "variance": "string"
      }
    ]
  },
  "cross_skill": {
    "multi_skill": false,
    "sequence_diagram": "string",
    "handoffs": [
      {
        "from": "string",
        "to": "string",
        "data_format": "string",
        "validated": true
      }
    ]
  }
}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_template() -> str:
    path = skill_root() / "assets" / "trace_report_template.md"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Risk formatting
# ---------------------------------------------------------------------------

RISK_EMOJI = {
    "high": "🔴 High",
    "medium": "🟡 Medium",
    "low": "🔵 Low",
}

def fmt_risk(level: str) -> str:
    return RISK_EMOJI.get(level.lower(), level)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_decision_flow(decisions: list[dict[str, Any]], project_name: str) -> str:
    """Build a Mermaid graph TD decision flow diagram."""
    lines = [
        "graph TD",
        '    SPEC["spec.md"]',
        '    PLAN["plan.md"]',
        '    IMPL["Implementation"]',
        f'    OUTPUT["Project Output"]',
        "",
        "    SPEC --> PLAN",
        "    PLAN --> IMPL",
        "    IMPL --> OUTPUT",
        "",
    ]

    for d in decisions:
        node_id = d["id"]
        label = d["description"][:45]
        source = d.get("source", "ad-hoc")
        is_drift = d.get("is_drift", False)

        if source == "spec":
            lines.append(f'    SPEC -->|"D{node_id[1:]}"| {node_id}["{label}"]')
        elif source == "plan":
            lines.append(f'    PLAN -->|"D{node_id[1:]}"| {node_id}["{label}"]')
        else:
            lines.append(f'    IMPL --> {node_id}["{label}"]')

        lines.append(f'    {node_id} --> OUTPUT')

        if is_drift:
            lines.append(f"    style {node_id} fill:#ff6,stroke:#f00")

        lines.append("")

    return "\n".join(lines)


def render_decision_table(decisions: list[dict[str, Any]]) -> str:
    rows = [
        "| # | Decision | Category | Source | Chose | Over |",
        "|:--|:---------|:---------|:-------|:------|:-----|",
    ]
    for i, d in enumerate(decisions, 1):
        alts = ", ".join(d.get("alternatives", [])) or "—"
        rows.append(
            f"| {i} | {d['description']} | {d.get('category', '—')} "
            f"| {d.get('source', '—')} | {d.get('chosen', '—')} | {alts} |"
        )
    return "\n".join(rows)


def render_assumption_table(assumptions: list[dict[str, Any]]) -> str:
    rows = [
        "| # | Decision Point | Assumption Made | Challenge Question | Risk |",
        "|:--|:---------------|:----------------|:-------------------|:-----|",
    ]
    for i, a in enumerate(assumptions, 1):
        rows.append(
            f"| {i} | {a.get('decision_id', '—')} | {a['assumption']} "
            f"| {a['challenge_question']} | {fmt_risk(a['risk_level'])} |"
        )
    return "\n".join(rows)


def render_high_risk_actions(assumptions: list[dict[str, Any]]) -> str:
    items = [
        f"- [ ] **HIGH PRIORITY:** `{a['decision_id']}` — {a['challenge_question']}"
        for a in assumptions
        if a.get("risk_level", "").lower() == "high"
    ]
    return "\n".join(items) if items else "_No High-risk assumptions identified._"


def render_landmines(landmines: list[dict[str, Any]]) -> str:
    blocks = []
    for lm in landmines:
        block = "\n".join([
            f"### LANDMINE-{lm['rank']}: {lm['name']}",
            "",
            f"**Trigger:** {lm['trigger_condition']}  ",
            f"**Impact:** {lm['impact']}  ",
            f"**Mitigation:** {lm['mitigation']}  ",
            f"**Risk:** {fmt_risk(lm['risk_level'])}  ",
        ])
        blocks.append(block)
    return "\n\n".join(blocks) if blocks else "_No landmines identified._"


def render_pre_demo_checklist(landmines: list[dict[str, Any]]) -> str:
    items = [
        f"- [ ] **{lm['name']}:** {lm['mitigation']}"
        for lm in landmines
        if lm.get("risk_level", "").lower() == "high"
    ]
    return "\n".join(items) if items else "_No High-risk landmines requiring pre-demo verification._"


def render_drift(drift: dict[str, Any]) -> str:
    if not drift.get("detected", False):
        return "### ✅ No Drift Detected\n\nImplementation aligns with `plan.md`."

    rows = [
        "### ⚠️ Drift Detected",
        "",
        "| Planned (plan.md) | Actual (Implementation) | Drift Type | Variance |",
        "|:------------------|:------------------------|:-----------|:---------|",
    ]
    for item in drift.get("items", []):
        rows.append(
            f"| {item['planned']} | {item['actual']} "
            f"| {item.get('drift_type', '—')} | {item.get('variance', '—')} |"
        )
    rows.append("")
    rows.append(
        "**Recommendation:** Update `plan.md` to reflect actual implementation, "
        "or refactor to match the plan."
    )
    return "\n".join(rows)


def render_cross_skill(cross_skill: dict[str, Any]) -> str:
    if not cross_skill.get("multi_skill", False):
        return "_Single-skill trace — no cross-skill interactions detected._"

    parts = []
    seq = cross_skill.get("sequence_diagram", "").strip()
    if seq:
        parts.append(f"```mermaid\n{seq}\n```")

    handoffs = cross_skill.get("handoffs", [])
    if handoffs:
        rows = [
            "### Handoff Points",
            "",
            "| From | To | Data Format | Validated? |",
            "|:-----|:---|:------------|:----------:|",
        ]
        for h in handoffs:
            validated = "✓" if h.get("validated") else "✗"
            rows.append(
                f"| {h['from']} | {h['to']} | {h['data_format']} | {validated} |"
            )
        parts.append("\n".join(rows))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render_report(data: dict[str, Any]) -> str:
    decisions = data.get("decisions", [])
    assumptions = data.get("assumptions", [])
    landmines = data.get("landmines", [])
    drift = data.get("drift", {"detected": False, "items": []})
    cross_skill = data.get("cross_skill", {"multi_skill": False})

    project_name = data.get("project_name", "Unknown Project")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""# Trace Report: {project_name}

> Generated {date_str} by `/trace` skill
> **Inputs:**
> - Architecture: `{data.get("architecture_path", "ARCHITECTURE.md")}`
> - Architecture Review Report: `{data.get("review_path", "—")}`
> - Project Output: `{data.get("output_path", "—")}`

---

## 1. Decision Path

```mermaid
{render_decision_flow(decisions, project_name)}
```

### Decision Summary

{render_decision_table(decisions)}

_Total decisions traced: {len(decisions)}_

---

## 2. Assumption Challenges

> **Risk scale:** 🔴 High = confidently wrong output, no warning | 🟡 Medium = degraded quality | 🔵 Low = cosmetic

{render_assumption_table(assumptions)}

### Action Items

{render_high_risk_actions(assumptions)}

---

## 3. Landmines

> Ranked by severity × detectability difficulty. LANDMINE-1 is the most dangerous.

{render_landmines(landmines)}

### Pre-Demo Checklist

{render_pre_demo_checklist(landmines)}

---

## 4. Logic Drift Detection

{render_drift(drift)}

---

## 5. Cross-Skill Interactions

{render_cross_skill(cross_skill)}

---

_End of Trace Report_
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a Trace Report from agent-produced structured JSON."
    )
    parser.add_argument("trace_json", help="Path to the structured JSON file from the agent")
    parser.add_argument("--output", "-o", help="Output markdown path (default: stdout)")
    args = parser.parse_args()

    json_path = Path(args.trace_json)
    if not json_path.exists():
        print(f"ERROR: {json_path} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {json_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    report = render_report(data)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Trace Report written to {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
