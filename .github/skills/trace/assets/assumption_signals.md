# Assumption Signals

Patterns in architecture docs, review reports, and project outputs that
indicate an implicit assumption — a decision was made without explicit
justification or specification.

Use these signals during Step 4 (Challenge Assumptions) to systematically
scan the input artifacts for hidden assumptions.

---

## Language Signals

These phrases in documentation or code comments often hide assumptions:

| Signal Pattern | What It Usually Assumes |
|---|---|
| "should be", "will be", "is expected to" | Input conforms to a specific format or state |
| "always", "never", "guaranteed" | No edge cases exist for this condition |
| "by default", "unless specified" | A default behaviour is acceptable for all users |
| "assumes", "assuming", "given that" | Explicit assumption — verify it's validated |
| "for now", "currently", "temporary" | Technical debt that may persist longer than intended |
| "standard", "typical", "normal" | Domain norms apply without verification |
| "should work", "usually works" | Untested path treated as reliable |

## Structural Signals

These patterns in architecture or code structure imply assumptions:

| Signal | Implied Assumption |
|---|---|
| Single input format supported | All users will provide input in this exact format |
| No error handling at boundaries | Upstream data is always clean and well-formed |
| Hardcoded thresholds or limits | One size fits all; no need for configurability |
| No validation before handoff | The producing skill's output is always correct |
| Linear pipeline (no branches) | No conditional logic is needed; all inputs follow the same path |
| Missing fallback logic | The primary path always succeeds |
| Fixed output schema | Downstream consumers all expect the same format |

## Decision Signals

These patterns in decision-making indicate unjustified choices:

| Signal | What to Challenge |
|---|---|
| Technology chosen without comparison | Why this library/tool over alternatives? |
| Architecture mirrors a tutorial/example | Is the example's context applicable here? |
| "We chose X" with no "because" | What criteria drove the selection? |
| Single implementation for multiple use cases | Does one approach genuinely fit all cases? |
| Feature omitted without explanation | Was this a deliberate scope decision or an oversight? |

## How to Use These Signals

1. Read through each input artifact line by line
2. Flag any line matching a signal pattern
3. For each flag, formulate a specific challenge question
4. Assess risk level based on: What happens if this assumption is wrong?
5. Record in the Assumption Challenges table of the Trace Report
