# Trace Report: {{project_name}}

> Generated {{date}} by `/trace` skill  
> **Inputs:**
> - Architecture: `{{architecture_path}}`
> - Architecture Review Report: `{{review_path}}`
> - Project Output: `{{output_path}}`

---

## 1. Decision Path

```mermaid
{{decision_flow_diagram}}
```

### Decision Summary

| # | Decision | Category | Source | Chose | Over |
|:--|:---------|:---------|:-------|:------|:-----|
{{decision_rows}}

_Total decisions traced: {{decision_count}}_

---

## 2. Assumption Challenges

> **Risk scale:** 🔴 High = confidently wrong output, no warning | 🟡 Medium = degraded quality | 🔵 Low = cosmetic

| # | Decision Point | Assumption Made | Challenge Question | Risk |
|:--|:---------------|:----------------|:-------------------|:-----|
{{assumption_rows}}

### Action Items

{{high_risk_action_items}}

---

## 3. Landmines

> Ranked by severity × detectability difficulty. LANDMINE-1 is the most dangerous.

{{landmine_blocks}}

### Pre-Demo Checklist

{{pre_demo_checklist}}

---

## 4. Logic Drift Detection

{{#if drift_detected}}
### ⚠️ Drift Detected

| Planned (plan.md) | Actual (Implementation) | Drift Type | Variance |
|:------------------|:------------------------|:-----------|:---------|
{{drift_rows}}

**Recommendation:** Update `plan.md` to reflect actual implementation, or refactor to match the plan.
{{else}}
### ✅ No Drift Detected

Implementation aligns with `plan.md`.
{{/if}}

---

## 5. Cross-Skill Interactions

{{#if multi_skill}}
```mermaid
{{sequence_diagram}}
```

### Handoff Points

| From | To | Data Format | Validated? |
|:-----|:---|:------------|:----------:|
{{handoff_rows}}
{{else}}
_Single-skill trace — no cross-skill interactions detected._
{{/if}}

---

_End of Trace Report_
