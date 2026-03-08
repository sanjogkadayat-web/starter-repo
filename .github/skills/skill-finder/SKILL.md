---
name: skill-finder
description: "Use this skill when the user wants to find, discover, or search for agent skills that match a specific need, workflow, or use case. Trigger when the user asks to search for skills, find a skill for a task, browse available agent skills, compare skills to requirements, recommend skills for a project, or query the awesome-agent-skills catalog. Also use when the user describes a workflow and wants to know if an existing agent skill already covers it."
argument-hint: "Describe the workflow, task, or capability you need a skill for"
---

# Skill Finder

Search the [awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) catalog and return a ranked similarity report matching available skills to the user's requirements.

## When To Use This Skill

Use this skill when the user wants to:

- find agent skills that match a described workflow or task
- search the awesome-agent-skills catalog for a specific capability
- compare their requirements against known community and official skills
- discover skills they didn't know existed for their use case
- get a recommendation report before building a custom skill

Do not use this skill for:

- creating or authoring a new SKILL.md (use the `create-skill` skill instead)
- installing or configuring an already-identified skill
- general questions about what agent skills are (just answer directly)

## Procedure

### Step 1 — Collect Requirements

Ask the user (or extract from context) what they need. Capture:

- **Goal:** What outcome are they trying to achieve?
- **Domain:** What domain or technology area? (e.g., testing, data analysis, DevOps, security, writing)
- **Platform:** Which agent platform? (e.g., GitHub Copilot, Claude Code, Codex, any)
- **Constraints:** Any must-haves or deal-breakers? (e.g., "must work offline", "needs MCP", "Python only")

If the user's message already contains enough detail, skip the interview and proceed.

### Step 2 — Fetch the Catalog

Fetch the latest skill catalog from the awesome-agent-skills repo:

```
URL: https://raw.githubusercontent.com/heilcheng/awesome-agent-skills/main/README.md
```

Use the `fetch_webpage` tool to retrieve the raw README.md content. This is the single source of truth for available skills.

### Step 3 — Parse the Skill List

From the fetched README, extract every skill entry. Skills are organized in tables under these sections:

- **Official Claude Skills (Document Processing)** — docx, xlsx, pptx, pdf
- **Official OpenAI Codex Skills** — repo/user/admin/system scoped
- **Official HuggingFace Skills** — dataset, evaluation, training, publishing
- **Community Skills** — organized by sub-category:
  - Skill Collections (aggregator repos)
  - Document Processing
  - Development & Code Tools
  - Data & Analysis
  - Integration & Automation
  - Collaboration & Project Management
  - Security & Systems
  - Advanced & Research

For each skill, capture:
- **Name** (with link if available)
- **Description** (the short summary from the table)
- **Category** (the section/sub-section it belongs to)
- **Source** (repo link if available)

### Step 4 — Score Similarity

For each skill, assess how well it matches the user's requirements across these dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Goal alignment** | 40% | Does the skill's purpose directly address what the user wants to accomplish? |
| **Domain match** | 25% | Is the skill in the same domain or technology area? |
| **Platform compatibility** | 15% | Does the skill work on the user's target platform (or is it universal)? |
| **Constraint satisfaction** | 20% | Does it meet the user's stated must-haves and avoid deal-breakers? |

Assign each dimension a score from 0–10, then compute a weighted total (0–10 scale).

### Step 5 — Generate the Report

Produce a markdown report following the template in [report_template.md](./references/report_template.md).

**Key rules:**

- Rank skills by total similarity score, descending.
- Include **all skills scoring 5.0 or higher** in the "Top Matches" section.
- Include skills scoring **3.0–4.9** in a "Partial Matches" section (brief table, no deep analysis).
- Omit skills scoring below 3.0 entirely.
- If no skills score 5.0+, say so explicitly and suggest the user create a custom skill.
- For each top match, include a 2–3 sentence rationale explaining the score.
- If a Skill Collection (aggregator repo) is relevant, flag it separately — it may contain sub-skills not individually listed.

### Step 6 — Recommend Next Steps

After the report, suggest concrete next steps:

1. **Install:** For the top 1–2 matches, provide the install command or link.
2. **Combine:** If no single skill covers everything, suggest combining 2–3 skills.
3. **Create:** If the gap is significant, suggest using the `create-skill` skill to build a custom one.

## Notes

- The catalog evolves. Always fetch fresh data — do not rely on cached or memorized skill lists.
- Skill Collections (e.g., `anthropics/skills`, `agentskill.sh`) are meta-entries containing many sub-skills. Flag them for deeper exploration if relevant.
- Some skills link to external repos. Include the link so the user can inspect the SKILL.md directly.
