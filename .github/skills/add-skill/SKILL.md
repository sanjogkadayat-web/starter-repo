---
name: add-skill
description: Use this skill when the user wants to create a new SKILL.md, turn an existing workflow into a reusable skill, or refine how a skill should trigger and what it should produce. This skill helps extract the workflow from conversation history, clarify trigger conditions and outputs, draft the SKILL.md frontmatter and body, and iterate on ambiguous parts until the skill is ready to use.
---

# Create Skill

Create a reusable GitHub Copilot skill for this workspace by first understanding the workflow, then drafting a SKILL.md that explains when the skill should trigger and how it should operate.

At a high level, the process is:

- Figure out what the skill should help with
- Identify when the skill should trigger
- Clarify the expected outputs and success criteria
- Draft the SKILL.md
- Identify ambiguous or weak parts
- Revise until the user is satisfied

Be flexible about how much process the user wants. Some users want a quick draft. Others want a more complete workflow with examples, checks, and follow-up prompts.

## Creating a Skill

### Capture Intent

Start by understanding the user's intent. If the conversation already contains a repeated workflow or methodology, extract it before asking new questions.

Pull out these details when available:

- What outcome the skill should produce
- The sequence of steps the workflow follows
- Inputs the workflow expects
- Outputs the workflow should create
- Decision points and branching logic
- Corrections or quality bars the user has already expressed

Confirm the intended scope:

1. What should this skill enable Copilot to do?
2. When should this skill trigger?
3. What output should it produce?
4. Is this a workspace skill or a personal skill?
5. Does the user want a quick checklist or a full multi-step workflow?

If the user already answered some of these in the conversation, do not ask them again unless something is still ambiguous.

### Interview and Research

Before drafting the skill, close the biggest gaps.

Ask about:

- Edge cases
- Input and output formats
- Required tools or dependencies
- Examples of good requests that should trigger the skill
- Examples of nearby requests that should not trigger the skill
- Completion criteria

When useful, inspect the workspace for related instructions, prompts, agents, or existing skills so the new skill matches the local customization style.

### Write the SKILL.md

Draft the skill using these parts:

- `name`: a short, stable identifier
- `description`: what the skill does and when it should trigger; put trigger guidance here, not buried in the body
- body instructions: the actual workflow Copilot should follow after the skill triggers

For workspace-scoped skills, save the file at `.github/skills/<skill-name>/SKILL.md`.

The description is the main trigger surface. Make it explicit enough that the skill will be selected for the right tasks, including cases where the user does not name the skill directly.

### Skill Writing Guide

#### Anatomy of a Skill

```text
.github/
└── skills/
	└── skill-name/
		└── SKILL.md
```

Add bundled references or helper files only when they materially improve repeatability or keep the main skill concise.

#### Progressive Disclosure

Use the skill body for the core workflow. If the skill grows large or supports multiple variants, split detailed references into separate files and tell Copilot when to read them.

Keep the SKILL.md focused on:

- trigger intent
- the main workflow
- decision points
- output expectations
- quality checks

#### Writing Patterns

Prefer imperative instructions.

Explain why important steps matter instead of relying on rigid rules with no reasoning.

When a fixed output structure matters, state it clearly.

When examples help, include short examples that show the expected behavior.

### Writing Style

Write for reuse, not just for the current example. Generalize from the conversation without overfitting to specific filenames or one-off details.

Prefer practical guidance such as:

- what to inspect first
- what to clarify before writing
- how to branch when information is missing
- how to decide whether the draft is complete

### Draft and Iterate

After drafting the skill:

1. Save the first draft.
2. Review it for ambiguity, missing trigger guidance, and missing completion checks.
3. Surface the weakest parts to the user.
4. Revise the skill based on the user's answers.

When surfacing weaknesses, focus on the most consequential gaps, such as:

- unclear trigger boundaries
- missing output format guidance
- vague success criteria
- missing edge-case handling

### Completion Check

Before considering the skill ready, verify that it:

- states when to trigger
- defines the intended outcome
- gives a concrete workflow to follow
- includes any necessary branching logic
- tells Copilot how to recognize a complete result

## Response Pattern

When using this skill, follow this interaction pattern:

1. Extract any reusable workflow already present in the conversation.
2. Ask only the minimum clarifying questions needed to close critical gaps.
3. Draft the SKILL.md and save it.
4. Point out the most ambiguous or weak parts.
5. Refine the skill with the user's feedback.
6. Summarize what the skill produces.
7. Suggest a few realistic prompts the user can try.
8. Propose related customizations that would complement the skill.

## Example Prompts

- Turn my code review workflow into a reusable skill.
- Create a skill that drafts podcast episode summaries from transcript files.
- Make a workspace skill for our spec to plan to tasks workflow.
- Help me write a SKILL.md that triggers when I ask for architecture exploration.