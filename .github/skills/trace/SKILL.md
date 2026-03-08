---
name: trace
description: >-
  Use this skill when the user wants to trace the decision path from specification
  to final output, reveal implicit assumptions, or surface project-specific landmines.
  Trigger when the user asks to trace decisions, explain why something was built a
  certain way, audit the path from spec to output, find hidden risks before a demo,
  generate a pre-flight checklist, or debug unexpected output by tracing it back to
  the decision that caused it. Also use when the user asks to visualize the decision
  flow, challenge assumptions in an implementation, or identify what could break.
  Requires ARCHITECTURE.md (from /scout), an Architecture Review Report
  (from /review), and the actual project output.
---

# Trace — Decision Path Investigator

Trace reads three artifacts — the architecture map (from `/scout`), the
architecture review report (from `/review`), and the actual project output —
and produces a Trace Report that reveals the decision path from spec to
output, challenges implicit assumptions, and lists project-specific landmines.

The goal is not to summarize what was built. The goal is to answer three
questions:

1. **How did we get here?** — The decision path from spec → plan → implementation → output
2. **What did we assume?** — Implicit choices that were never explicitly specified
3. **What could break?** — Landmines triggered by this implementation

## Scripts and Assets

| Path | Purpose |
|---|---|
| [scripts/render_trace_report.py](./scripts/render_trace_report.py) | Deterministic renderer: takes agent-produced structured JSON → final Trace Report markdown |
| [assets/trace_report_template.md](./assets/trace_report_template.md) | Markdown template shape for the final Trace Report |
| [assets/common_landmines.json](./assets/common_landmines.json) | Library of common landmine archetypes with triggers, impacts, and mitigations |
| [assets/assumption_signals.md](./assets/assumption_signals.md) | Patterns that flag lines where a decision implies an unvalidated assumption |

---

## Inputs To Identify First

When the skill triggers, locate these three required inputs:

1. **ARCHITECTURE.md** (from `/scout`)
   - File index, module descriptions, architecture diagram (Mermaid)
   - Default location: `ARCHITECTURE.md` in project root
   - If missing: tell the user to run `/scout` first

2. **Architecture Review Report** (from `/review`)
   - Design principle violations, spec coverage gaps, plan alignment issues,
     internal architecture consistency issues, and suggested fixes
   - Each finding has a severity: Critical, High, Medium, or Low
   - Look for files matching `reports/arch_review_*.md` in the project
   - If missing: tell the user to run `/review` first, or proceed with a
     partial trace (note the gap in the report)

3. **Project Output**
   - The actual artifact(s) produced by the skill or pipeline being traced
   - Ask the user which output to trace if not obvious
   - Examples: `marketing-kit.json`, `shorts_report.md`, `cleaned-dataset.csv`

Also check for:
- **spec.md** and **plan.md** — if a speckit workflow was used, these provide
  the requirements and implementation plan to trace decisions against
- Look in `.specify/specs/` for feature specs

If any input is missing, state which input is absent and what impact that has
on the trace (e.g., "Without the Architecture Review Report, drift detection
will be limited to comparing the output against ARCHITECTURE.md only").

---

## Core Workflow

### Step 1 — Ingest all inputs

Read the three required inputs in full. Also read `spec.md` and `plan.md` if
they exist. Note the key structures:

From **ARCHITECTURE.md**:
- Repository structure (planned vs actual)
- System architecture diagram
- Module descriptions and responsibilities
- Technology choices

From **Architecture Review Report**:
- Design Principle Violations (with severity and recommendations)
- Spec Coverage Gaps (required capabilities vs architecture status)
- Plan Alignment Issues (planned components vs architecture)
- Internal Architecture Issues (self-consistency checks)
- Suggested Fixes (concrete edits for architecture, specs, and plans)

From **Project Output**:
- Format and structure of the actual output
- Content coverage (what was produced vs what was specified)
- Any metadata, timestamps, or provenance markers

### Step 2 — Extract decisions

Identify every point where the implementation chose one path over alternatives.
Categorise each decision:

| Category | What it captures |
|---|---|
| **TECHNOLOGY** | Language, framework, library, or tool choice |
| **ARCHITECTURE** | Module boundaries, data flow paths, API design |
| **DATA** | Input format assumptions, transformation choices, output schema |
| **SCOPE** | What was included/excluded vs what was specified |
| **PROCESS** | Workflow order, automation choices, manual vs scripted steps |
| **OUTPUT** | Format, structure, depth, and presentation of the result |

For each decision, record:
- **What was chosen** and **what alternatives existed**
- **Where it originated**: spec, plan, architecture, or was it ad-hoc?
- **What assumption it implies** (if the choice was not explicitly justified)

### Step 3 — Map the decision path

Generate a **Mermaid `graph TD`** diagram showing the flow:

```
Spec → Plan → Implementation → Output
```

With decision points branching off the main flow. Rules:
- Use `graph TD` for the primary decision flow
- Use `subgraph` blocks for clearly separable phases
- Label each decision node with a short ID (e.g., `D1`, `D2`)
- Show the chosen path as a solid arrow, alternatives as dashed
- Highlight **Logic Drifts** where execution deviated from `plan.md`
  using a distinct style (e.g., `style D3 fill:#ff6,stroke:#f00`)
- Keep node labels ≤ 45 characters
- All Mermaid syntax must be wrapped in proper fenced code blocks

If the project's **own runtime workflow** involves multiple skills or agents
interacting (excluding utility skills `/scout`, `/review`, `/trace`), also
generate a **`sequenceDiagram`** showing the handoff points between them.

### Step 4 — Challenge assumptions

For every decision that implies an assumption not explicitly stated in the
spec or plan, generate a challenge entry:

| Field | Description |
|---|---|
| **Decision Point** | Which decision this assumption belongs to |
| **Assumption Made** | What was implicitly assumed |
| **Challenge Question** | An actionable question that tests the assumption |
| **Risk Level** | 🔴 High / 🟡 Medium / 🔵 Low |

Risk scale:
- **🔴 High** — If this assumption is wrong, the output is confidently wrong
  with no warning
- **🟡 Medium** — If wrong, output quality degrades but is still usable
- **🔵 Low** — If wrong, only cosmetic or minor impact

Challenge questions must be **actionable**, not rhetorical. Good: "What if the
transcript lacks speaker labels — does segmentation still work?" Bad: "Is
this really the best approach?"

Read [assets/assumption_signals.md](./assets/assumption_signals.md) for
patterns that commonly indicate hidden assumptions.

### Step 5 — Identify landmines

A **landmine** is a specific input, condition, or scenario that the
implementation is not designed to handle but that a user might naturally
encounter.

Start from the common landmine library in
[assets/common_landmines.json](./assets/common_landmines.json). For each
archetype, check whether it applies to this project by looking for detection
signals in the architecture and output.

Then add **project-specific landmines** based on:
- Decisions that have no fallback path
- Assumptions rated 🔴 High that have no mitigation
- Cross-skill handoff points where format mismatches could occur
- Performance cliffs (e.g., input exceeds token limits, API rate limits)
- Critical or High severity findings from the Architecture Review Report
  that remain unresolved

For each landmine, record:
- **Name** — short descriptive label
- **Trigger Condition** — what specific input or state detonates it
- **Impact** — what breaks and how visibly
- **Mitigation** — concrete safeguard to add
- **Risk Level** — 🔴 High / 🟡 Medium / 🔵 Low

Aim for 5–10 landmines. Rank by (severity × detectability difficulty).

### Step 6 — Detect logic drift

Compare the implementation and output against `plan.md` (if it exists).
Also use the **Plan Alignment Issues** section from the Architecture Review
Report — it already flags components that are planned but missing from the
architecture, or present in the architecture but unplanned.

- For each planned step, check if the implementation matches
- Flag any **drift** — where the actual implementation differs from the plan
- Classify each drift:
  - **Intentional** — plan was updated or superseded (document why)
  - **Accidental** — implementation diverged without updating the plan
  - **Improvement** — implementation improved on the plan

If no `plan.md` exists, compare the output against the spec and architecture
to identify any gaps between intent and result.

### Step 7 — Check cross-skill interactions

> **Scope rule:** Utility/diagnostic skills — `/scout`, `/review`, and `/trace`
> itself — are **always excluded** from this analysis. They are tooling applied
> to the project from the outside, not part of the project's own skill chain.
> Only map skills that the project **itself** invokes as part of its runtime
> workflow.

If the project's own workflow involves multiple skills (e.g., a content
pipeline that calls `/podcast-shorts-analyzer` followed by a downstream
publishing skill), map those handoff points:

- What data format does each skill produce?
- Does the next skill validate what it receives?
- Are there format assumptions at handoff boundaries?

Generate a `sequenceDiagram` for multi-skill flows.

If the project is a single self-contained skill with no cross-skill
dependencies (in its own runtime workflow), note:
"Single-skill trace — no cross-skill interactions detected."

### Step 8 — Produce the Trace Report

Write your findings from Steps 2–7 to a structured JSON file, then render
it using [scripts/render_trace_report.py](./scripts/render_trace_report.py).

The JSON must follow the schema documented at the top of `render_trace_report.py`
(decisions, assumptions, landmines, drift, cross_skill).

```bash
python .github/skills/trace/scripts/render_trace_report.py \
    /tmp/trace_data.json \
    --output reports/trace_$(date +%Y%m%d_%H%M%S).md
```

Inspect the rendered output and refine any Mermaid diagrams or table rows
that need editorial polish before saving the final report.

The report must contain all five sections:
1. Decision Path (Mermaid diagram + decision summary table)
2. Assumption Challenges (table + action items for 🔴 High risks)
3. Landmines (ranked list + pre-demo checklist for 🔴 High risks)
4. Logic Drift Detection (drift table or "No Drift Detected")
5. Cross-Skill Interactions (sequence diagram or "Single-skill trace")

---

## Output Location

Save the Trace Report to:
`reports/trace_YYYYMMDD_HHMMSS.md`

Create the `reports/` directory if it does not exist. Use the same
convention as `/review` (which saves to `reports/arch_review_YYYYMMDD_HHMMSS.md`)
so all diagnostic reports are co-located.

If the user specifies a different location, use that instead.

---

## Constraints

- Use `graph TD` for decision flow diagrams
- Use `sequenceDiagram` for multi-agent/multi-skill interactions
- Risk levels: 🔴 High, 🟡 Medium, 🔵 Low
- All Mermaid syntax must be wrapped in fenced code blocks with the `mermaid` language tag
- Challenge questions must be actionable (not rhetorical)
- Highlight Logic Drifts visually in the Mermaid diagram
- Keep the report factual — anchor every claim to a specific line, section,
  or decision in the input artifacts
- Do not re-run or execute project code during a trace

---

## What This Skill Does Not Do

- Does **not** execute project code or scripts
- Does **not** fix the issues it finds — it produces a diagnostic report
- Does **not** replace `/review` — `/review` cross-checks architecture
  documentation against specs, plans, and design principles;
  `/trace` audits the full decision path from spec → output
- Does **not** generate new features or refactor code

---

## Completion Check

A trace is complete when:

1. All three inputs (ARCHITECTURE.md, Architecture Review Report, Project
   Output) have been read and referenced (or their absence is documented)
2. The Mermaid decision flow covers all major decision points
3. Every 🔴 High-risk assumption has a challenge question and action item
4. At least 5 landmines are listed with trigger conditions and mitigations
5. Logic drift detection has been performed (or noted as not applicable)
6. The output follows the shape in `assets/trace_report_template.md`
7. `render_trace_report.py` was run to produce the final markdown
8. The report is saved to `reports/trace_YYYYMMDD_HHMMSS.md` (or user-specified location)
