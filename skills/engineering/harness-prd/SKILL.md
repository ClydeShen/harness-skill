---
name: harness-prd
description: Turn the current conversation context into a GSD-compatible PRD with WHAT/HOW constraints, optionally writing to .planning/phases/01-discuss/CONTEXT.md. Use when user wants to create a PRD from the current context.
---

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-harness-skills` if not.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.

2. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

3. Write the PRD using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage. For discuss-phase output, use the GSD CONTEXT.md format in the section below instead of the prd-template.

## GSD-compatible output

Write the PRD to `.planning/phases/01-discuss/01-CONTEXT.md` using GSD's 6-section CONTEXT.md format:

| GSD section | Content |
|---|---|
| `<domain>` | Phase boundary — what the discuss phase delivers (from user's stated scope) |
| `<decisions>` | Implementation decisions — WHAT the system must respect (maps to Technical Constraints) |
| `<canonical_refs>` | ADRs, spec sections, external docs cited during discussion |
| `<code_context>` | Brownfield: existing patterns, reusable assets, integration points |
| `<specifics>` | Specific user requirements ("I want it like X") |
| `<deferred>` | Ideas that came up but belong in other phases |

After writing: "CONTEXT.md written to `.planning/phases/01-discuss/01-CONTEXT.md`. Run `/harness-issues` to plan this phase."

**WHAT/HOW invariant:** `<decisions>` contains only system-level constraints — external integrations, compliance, performance SLAs, system boundaries. No file paths, class names, schemas, or user requirements. User requirements ("I want X") belong in `<specifics>`, not `<decisions>`.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Technical Constraints

<!-- WHAT the system must respect — NOT how to build it.
     The Execution agent reads these as non-negotiables and makes its own implementation decisions. -->

- [External integration constraints: e.g. "Must integrate with OAuth provider at /auth/callback"]
- [Compliance/regulatory constraints: e.g. "Session data must not be persisted to disk (GDPR)"]
- [Performance SLAs: e.g. "API response must be <200ms at p99"]
- [Existing system boundaries: e.g. "Must use the existing PostgreSQL instance — no new datastores"]

**NOT allowed here:** module names, class names, file paths, schema decisions, technology choices, or architectural patterns. Those belong to the Execution agent's own technical plan.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>

**Spike recommendation:** If the solution approach is uncertain — whether the output is a PRD or a GSD CONTEXT.md — append after writing:

> *Solution uncertainty detected — recommend creating a `type:spike` issue (1–2 context windows / ~150K–400K tokens, AFK, throwaway) to validate the approach before breaking down into implementation stories. Spike output is a decision (proceed / pivot / split), not shippable code.*
