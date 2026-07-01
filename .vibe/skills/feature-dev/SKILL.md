---
name: feature-dev
description: >
  Guided feature development workflow. Invoke with /feature-dev followed by a
  description of the feature you want to build. Runs 7 structured phases:
  Discovery, Codebase Exploration, Clarifying Questions, Architecture Design,
  Implementation, Quality Review, and Summary. Delegates exploration, design,
  and review work to specialised subagents.
license: MIT
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - search_replace
  - grep
  - bash
  - task
  - ask_user_question
  - todo
---

# Feature Development Workflow

A structured 7-phase workflow for building features systematically. Rather than
jumping straight into code, this skill guides you through understanding the
existing codebase, clarifying requirements, designing architecture thoughtfully,
and conducting quality reviews before and after implementation.

## How to invoke

```
/feature-dev Add rate limiting to the API
/feature-dev Implement on-device speech recognition using MLX
```

Or simply `/feature-dev` to start the guided workflow with no initial description.

---

## Phase 1 — Discovery

**Goal:** Understand what the user wants to build.

- Read the user's feature description carefully.
- Identify the core problem being solved and the key constraints.
- If the description is vague or incomplete, ask 1–2 focused questions using
  `ask_user_question` before proceeding. Keep it tight — don't interview.
- Summarise what you understand the feature to be in 2–3 sentences and confirm
  with the user before moving on.

**Output:** A clear, agreed feature statement.

---

## Phase 2 — Codebase Exploration

**Goal:** Understand the existing code that's relevant to this feature.

Delegate exploration to the `code-explorer` subagent using the `task` tool.
Give it specific directions:

1. **Similar features:** Find existing code that does something analogous.
2. **Architectural patterns:** Identify the conventions used — layering,
   dependency injection, module structure, naming, error handling.
3. **Integration points:** Locate the files and interfaces the new feature will
   need to touch or extend.

Run 2–3 exploration tasks in parallel if possible (e.g. one for similar
features, one for architecture patterns, one for integration points).

**Present findings to the user as a concise summary:**

- Key files and their roles
- Patterns the codebase follows
- Where the new feature will plug in

---

## Phase 3 — Clarifying Questions

**Goal:** Resolve ambiguity before designing anything.

Based on what you learned in Phase 2, ask the user targeted questions about:

- Edge cases and error handling expectations
- Performance or scale requirements
- Integration preferences (which existing abstractions to reuse)
- Testing expectations
- Any constraints not mentioned in the original description

Use `ask_user_question` with multiple-choice options where appropriate. Keep
to 3–5 questions maximum. Concrete questions produce better implementations
than open-ended ones.

**Output:** Documented answers that will guide Phase 4.

---

## Phase 4 — Architecture Design

**Goal:** Propose implementation approaches with clear trade-offs.

Delegate to the `code-architect` subagent using the `task` tool. Provide it
with:

- The feature statement from Phase 1
- The codebase findings from Phase 2
- The clarified requirements from Phase 3

The architect should propose **2–3 implementation approaches**, each with:

- A short name and one-sentence summary
- The key files to create or modify
- Trade-offs: what this approach optimises for and what it sacrifices
- A recommendation with rationale

**Present the options to the user** and let them choose. If they ask for your
recommendation, give one with clear reasoning. Do not proceed until the user
has selected an approach.

**Output:** A chosen implementation approach with a file-level plan.

---

## Phase 5 — Implementation

**Goal:** Build the feature following the chosen approach.

- Work through the implementation plan file by file.
- Follow the codebase conventions identified in Phase 2.
- Use `todo` to track progress through the implementation steps.
- After each significant file change, briefly state what was done and why.
- If you encounter an unexpected decision point, pause and ask the user
  using `ask_user_question` rather than guessing.
- Run any relevant tests or linting as you go using `bash`.

**Output:** Working implementation with all planned files created or modified.

---

## Phase 6 — Quality Review

**Goal:** Catch issues before they reach production.

Delegate to the `code-reviewer` subagent using the `task` tool. Provide it
with a list of all files that were created or modified in Phase 5.

The reviewer should check for:

1. **Bugs and logic errors** — off-by-ones, null handling, race conditions
2. **Security issues** — injection, auth bypass, data exposure
3. **Convention violations** — naming, structure, patterns that diverge from
   the existing codebase
4. **Missing error handling** — unhappy paths, network failures, edge cases
5. **Test coverage** — are the important paths tested?

**Findings should be scored by priority** (high / medium / low).

Present findings to the user. Fix high-priority issues. Discuss medium-priority
items and fix if the user agrees.

**Output:** A clean, reviewed implementation.

---

## Phase 7 — Summary

**Goal:** Give the user a clear picture of what was built.

Produce a summary that includes:

- **What was built:** 2–3 sentence description
- **Key decisions:** The approach chosen and why
- **Files modified:** List with one-line descriptions
- **Files created:** List with one-line descriptions
- **Suggested next steps:** Tests to add, documentation to update, follow-on
  features, deployment considerations

Keep it concise. The user can dig into details if they need to.

---

## Guidelines

- **Don't skip phases.** The structure exists to catch problems early. Even for
  small features, at least do a quick pass through each phase.
- **Pause for input.** Phases 1, 3, 4, and 6 should all wait for user
  confirmation before proceeding.
- **Stay in scope.** Don't refactor adjacent code, add unrequested features, or
  touch files outside the plan unless the user asks.
- **Use subagents.** Phases 2, 4, and 6 should delegate to the specialised
  subagents rather than doing everything in the main agent context.
- **Track progress.** Use the `todo` tool to maintain a visible checklist of
  the implementation plan.
