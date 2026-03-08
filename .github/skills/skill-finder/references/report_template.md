# Skill Finder — Report Template

Use this template shape when generating the similarity report. Adapt section sizes based on the number of matches.

---

## Example Report

```markdown
# Skill Finder Report

## Requirements Summary
- **Goal:** [user's goal in one sentence]
- **Domain:** [domain/technology area]
- **Platform:** [target agent platform, or "any"]
- **Constraints:** [must-haves and deal-breakers, or "none"]

---

## Top Matches

### 1. [Skill Name] — Score: X.X / 10
- **Category:** [section from catalog]
- **Description:** [from catalog]
- **Source:** [link to repo or skill]
- **Scores:**
  | Dimension | Score |
  |-----------|-------|
  | Goal alignment | X/10 |
  | Domain match | X/10 |
  | Platform compatibility | X/10 |
  | Constraint satisfaction | X/10 |
- **Rationale:** [2–3 sentences explaining why this skill matches and any caveats]

### 2. [Skill Name] — Score: X.X / 10
[same structure]

---

## Partial Matches (3.0–4.9)

| Skill | Category | Score | One-line reason |
|-------|----------|-------|-----------------|
| [name] | [cat] | X.X | [why it partially fits] |

---

## Relevant Skill Collections

If any Skill Collection (aggregator repo) is relevant, list it here:

| Collection | Link | Why relevant |
|------------|------|--------------|
| [name] | [url] | [reason] |

---

## Gaps

[What the user's requirements need that no existing skill fully covers]

---

## Recommended Next Steps

1. **Install [top skill]:** [command or instructions]
2. **Explore [collection]:** [link] — may contain unlisted sub-skills
3. **Create a custom skill:** Use `/create-skill` to build [specific gap]
```
