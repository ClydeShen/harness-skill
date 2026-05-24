# Context

## Glossary

### Runtime
An AI agent framework that executes the harness-engineering skill. Current targets: Claude Code, Codex, Kiro, Gemini. Distinct from **stack** (Node/Python/Go), which is orthogonal — a project can be Node on Kiro or Python on Claude Code.

Detection signals:
- Claude Code / Codex: `.claude/` directory present
- Kiro: `.kiro/` directory present
- Gemini: `.gemini/` directory present
- Ambiguous: none of the above — consume a Phase 2 question slot

### Full support (runtime)
A runtime has full support when all three are true: (1) Phase 1 detects it via file-system signal, (2) the skill produces paste-ready runtime-specific snippets, (3) at least one eval covers the scenario. Currently: Claude Code, Codex, Kiro.

### Best-effort support (runtime)
A runtime is best-effort when it can be detected but output adapts Claude Code snippets with a note to customise. Currently: Gemini. Claude Desktop is out of scope — it has no code-editing harness to detect.

### Harness-concept mapping
When a gsd-2 command directly satisfies an existing harness gap, the gap is conditionally closed rather than listed as missing. Current mappings:
- `/gsd doctor` → closes the `init.sh` (health check) gap
- `/gsd verdict` → implements the Judge audit pattern
- `/gsd status` → satisfies session-state tracking

This applies only when gsd-2 is detected as installed in the current session (Phase 1 step 10).

### Stack
The language/framework of the user's project (Node/TS, Python, Go). Orthogonal to runtime. Determines which stack-specific reference file loads in Phase 3 (`node-snippets.md`, `python-snippets.md`).

### Compound Engineering
Source: https://ai.sulat.com/compound-engineering-with-ai-the-definitive-guide-05530cf717dd

A systematic discipline where each unit of engineering work makes subsequent units easier, not harder. Like compound interest, improvements accumulate exponentially over time rather than linearly.

The per-task cycle has four phases:
- **Plan (40%)** — Thinking that prevents rework: requirements, codebase patterns, research, design, plan validation
- **Work (10%)** — AI agent executes; deliberately short because planning resolves hard questions
- **Review (40%)** — Correctness, security, performance, pattern adherence, test quality, edge cases
- **Compound (10%)** — Capture learnings in CLAUDE.md updates, solution documents, and implementation notes

The Compound phase is what distinguishes this from vibe coding: every solved problem becomes permanent institutional knowledge.

Maturity stages (0–5): 0=manual, 1=chat+copy-paste, 2=agentic+line-review, 3=plan-first+PR-review (inflection), 4=idea-to-PR single machine, 5=parallel cloud orchestration.

Distinct from **harness engineering**, which is the infrastructure that enables compound engineering to run reliably across sessions.

### Harness Engineering
The infrastructure layer that allows AI agents to run long-running tasks reliably: hooks, CI, instruction files, session state, context handover. Distinct from **compound engineering**, which is the per-task methodology that runs on top of the harness.

### Session
A single continuous Claude Code conversation. Sessions are bounded by context window limits. A **context handover** is the structured transition between sessions, preserving continuity.

### Context Handover
The structured process executed near the end of a session to preserve state across sessions. Produces: updated memory (MEMORY.md or memobank), an updated handoff document, updated GitHub issue status, and an implementation notes artifact. Distinct from the built-in `/compact` command, which compresses conversation history without preserving structured state.

Trigger: context window token usage reaches ≥80% of total capacity. Claude receives this natively via `<system_warning>Token usage: X/Y; Z remaining</system_warning>` after each tool call — no external hook required for detection. The remaining 10-20% is the reserved buffer for executing the handover procedure itself.

**Handoff document:** A single unified file at `.claude/handoff.md` in the project root. Overwritten in place on every handover — no timestamped copies. Added to `.gitignore` by `setup-harness-skills`. This is the primary continuity artifact for the next agent session; `session-start` reads it directly. The "Last updated" timestamp inside the file records when it was last written.

**GitHub issue comments:** For multi-session issues (effort > 1 context window), `context-handover` also appends a progress comment to the active GitHub issue. Comments accumulate into a visible progress log for humans. The issue comment is the durable remote record; `.claude/handoff.md` is the primary local record. `session-start` uses `.claude/handoff.md` by default and fetches the last GitHub comment only when the local file is absent, the task has severely deviated, or the user explicitly requests a sync.

Session continuation is manual: the human starts a new session via `/compact` or `/new`. Automation (Desktop tasks, `/loop`) is out of scope — the handoff document quality is the primary continuity mechanism, not automated chaining.

Distinct from subscription quota monitoring (5-hour/7-day billing windows), which is a separate concern unrelated to context handover.

### Context Cleanliness
The design principle that each context window should contain only conversation content relevant to the active main task. Off-task discussions, completed subtask artifacts, and tangential tool results degrade context quality. Degraded contexts increase the risk of the agent losing focus, contradicting prior decisions, or hallucinating state.

Two mechanisms enforce context cleanliness:
1. **Subagent isolation**: any task that deviates from the session's main task spawns a subagent (separate context window) rather than being handled inline.
2. **Context handover**: at session end, the context is compacted and the next session starts clean with only the structured handoff artifacts loaded.

Context cleanliness is the primary reason for context handover — not just resource management, but quality preservation.

### Implementation Notes
A running artifact (markdown file) maintained during an Execution phase session when the agent makes decisions not covered by the spec. Captures: decisions not in the spec, things changed from the original plan, tradeoffs accepted, and anything the next session or human reviewer should know. Not created for every issue — only when the agent deviated from the spec.

Path: `docs/implementation-notes/YYYY-MM-DD-issue-NNN.md` (version controlled, permanent institutional knowledge). The agent links the file path in a closing GitHub issue comment. Distinct from CLAUDE.md (project-level institutional knowledge that applies universally) and the handoff document (session state for the next agent session).

### Project Phase
One of four project-level phases: Design, Product, Execution, Testing. The default order is Design → Product → Execution → Testing, but phases can be **skipped** or **reversed** based on existing artifacts:

- **Skip (A)**: `session-start` evaluates what artifacts already exist. If a spec exists, skip Design. If issues already exist in GitHub, skip Product. Entry condition is artifact presence, not human declaration.
- **Reverse (B)**: Agent detects a specific artifact absence and sets `session.json.current_phase` back to the appropriate earlier phase, commenting on the Design Phase Tracking Issue to explain. Revert is triggered **only by observable artifact absence** — never by the agent's subjective quality judgment about artifacts. Concrete triggers: (1) revert to Design when no `.md` file exists in `docs/superpowers/specs/`; (2) revert to Design when `current_phase == "product"` but no `phase:design` issue is closed or labelled `design-approved`; (3) revert to Product when `current_phase == "execution"` but `gh issue list --label "phase:execution,status:ready-for-agent"` returns 0 issues. If the spec file exists but is thin in quality, the agent proceeds and notes the quality concern in the issue comment — not revert. Human observes on GitHub.
- **Parallel phases**: Out of scope (YAGNI).

Distinct from the per-task **compound engineering cycle** (Plan/Work/Review/Compound), which repeats within each project phase. A project phase may span multiple sessions; a compound cycle maps to one task.

Each phase reasons its own context window allocation independently. The compound engineering 40/10/40/10 ratios are illustrative principles, not fixed constraints. All allocations reserve a minimum 10% buffer before context handover. Example reasoning differences by phase: Design allocates more to user dialogue and review (documents accumulate and must be reconciled); Execution allocates more to implementation and less to dialogue.

Phase transitions are criteria-based and agent-declared (not human-initiated). The agent self-validates against exit criteria defined during the Design phase, then posts a GitHub transition summary for human visibility. Humans may veto; they do not initiate.

**Invariant:** All phase exit criteria must be defined during the Design phase, before any other phase begins. A Design phase that does not produce exit criteria for all subsequent phases is not complete.

**Human gate:** Human approval is required to exit the Design phase only. All other phase transitions (Product → Execution, Execution → Testing, Testing → done) are agent-declared and autonomous. Human observes via GitHub; may veto but does not initiate.

### Phase Exit Criteria
Machine-verifiable conditions that determine when a phase is complete. Defined during Design phase for all phases. The agent validates these at phase end and posts a transition summary (GitHub comment or issue) before advancing.

Per-phase oracles:
- **Design**: Design Phase Tracking Issue has `design-approved` label or is closed by human.
- **Product**: All breakdown issues have `status:ready-for-agent` + `phase:execution`.
- **Execution**: All `phase:execution` issues are closed via merged PRs. PR merge is the oracle — agent must go through PR flow; direct push to main is prohibited via GitHub branch protection rules (require PR + require CI pass, configured by `setup-harness-skills`). Issue close happens automatically via `Closes #NNN` in PR body. If branch protection configuration fails (insufficient token permissions), it is recorded as an unresolved gap and listed in the setup report — other configuration steps continue unaffected.
- **Testing**: All `phase:testing` issues are `status:done` and no `p1` open bugs remain.

Exit criteria must be:
- **Observable**: verifiable by reading an artifact, not by trusting the agent's self-report
- **Specific**: no fuzzy language ("working well" is not a criterion; "all evals pass with no FAIL" is)
- **Complete**: if all criteria are met, the phase is unambiguously done

### Human Interaction Trigger
The condition under which an autonomous agent session pauses to ask the human a question. In this system: only when information required to proceed is absent from all available artifacts (task anchor, MEMORY.md, handoff document, CLAUDE.md, CONTEXT.md, docs/agents/). If the agent can make a reasonable inference, it should proceed and document the inference in the implementation notes, not stop to ask.

### Task (Session Task)
The single unit of work that scopes a session's context window. One session = one task. The task boundary is defined by the **task anchor** — the artifact that identifies what "relevant" means for that context.

Task anchor by phase:
- **Design phase**: the Design Phase Tracking Issue (a single GitHub issue created at project start, before any design work begins). All Design phase sessions comment on this issue. The active design document path is noted in the handoff document.
- **Product phase**: one PRD document or one epic breakdown session; tracked via GitHub issue or milestone.
- **Execution phase**: one GitHub issue number (agent brief format per mattpocock/skills pattern).
- **Testing phase**: one test plan document or one batch of related issues being tested together.

Any work outside the task anchor's scope must be deferred: create a new issue/document and either spawn a subagent or queue it for the next session. Never handled inline.

### GitHub Label Schema
The four label categories used across all issues in the system:

| Category | Values |
|---|---|
| `status:` | `triage` / `needs-prd` / `ready-for-agent` / `in-progress` / `done` |
| `phase:` | `design` / `product` / `execution` / `testing` |
| `type:` | `feature` / `bug` / `chore` / `task` |
| `priority:` | `p1` / `p2` / `p3` |

`phase:` is **categorical** (what kind of issue this is), not temporal (what phase the project is currently in). A `phase:execution` issue and a `phase:testing` issue can coexist on the board. The current project phase is canonical in `session.json`; the agent processes only issues matching `phase:<current-phase>` + `status:ready-for-agent`.

### GitHub Milestone
GitHub's native issue-grouping container. Used in this system as a release or phase container — not an issue type. Created by `setup-harness-skills` at project start (e.g., `Design`, `MVP`, `v1.0`). Issues are assigned to milestones during the Product phase breakdown. Milestones are visible on the GitHub Project board and give humans a progress view per release. Distinct from `type:` labels, which describe the nature of an individual issue.

### User Story
The unit of work produced by the Product phase. Written in BA (Business Analyst) format and assigned to `phase:execution` issues. A user story describes **what** the system should do from the user's perspective — never **how** to implement it. Technical decisions belong to the Execution phase agent.

**Format:**
```
As a [role], I want [capability], so that [benefit].
```

**Acceptance Criteria (AC):** Written in Given/When/Then (BDD) style or as a verifiable checklist. Must include at least:
- 1 happy path (normal successful flow)
- 1 sad path (error or edge case)

**Definition of Ready (DoR):** Criteria that must be true before an Execution agent can start:
- Story has a clear role, capability, and benefit
- All AC are written and unambiguous
- Dependencies on other issues are identified
- Effort estimate (context windows) is set

**Definition of Done (DoD):** Criteria that must be true for the issue to close:
- All AC pass (verified by the agent or CI)
- PR merged to main
- No regressions in related tests
- Implementation notes written if agent deviated from spec

**Effort estimate:** Set during Product phase. Unit = context windows. `1` = estimated to complete within one context window. Maximum: `8`. Stories estimated at >8 context windows must be split into smaller issues before creation — above this threshold the scope is too large to track and hand over reliably. Used to populate the `Effort (windows)` GitHub Project field.

**INVEST criteria applied:** Stories must be Independent (can be worked in any order within a phase), Negotiable (scope can be adjusted), Valuable (delivers user-facing benefit), Estimable (effort is knowable), Small (fits within 1–2 context windows), Testable (AC are verifiable).

### harness.json
The static project configuration file, written by `setup-harness-skills` to `.claude/harness.json` in the user's project. **Version-controlled (committed)** — shared team config analogous to `package.json`. Separates static config (what the project is) from dynamic session state (what is happening right now — see `session.json`). Contains: GitHub owner, repo, default branch, Project v2 board ID, docs_agents_dir, specs_dir, and issue_tracker type. All skills read this file with null-safety. Updated only when the user re-runs `setup-harness-skills` to change a setting.

### handoff.md
The unified context handover document at `.claude/handoff.md` in the user's project. A single file overwritten in place on every `context-handover` invocation — no timestamped copies. **Gitignored** (agent working file — per-agent ephemeral state). Contains: last-updated timestamp, phase, session summary, next step, artifact references (paths/URLs only, never inlined content), and suggested skills. Read by `session-start` as the primary local continuity artifact. Distinct from the GitHub issue comment (durable remote record for humans) and from `session.json` (machine-readable state).

### session.json
The dynamic session state file at `.claude/session.json` in the user's project. **Gitignored** (agent working file — changes every session). Tracks: current phase, active task (GitHub issue number, title, effort estimate, project board item ID), last handover timestamp, and next session hint. Written by `session-start` (initialize) and `context-handover` (update). Read by `session-start`, `context-handover`, and `harness-engineering`. Distinct from `harness.json` (version-controlled team config) and `handoff.md` (human-readable continuity document).

### Design Phase Tracking Issue
A single GitHub issue created at project start (before any design work begins). Labelled `phase:design`. Serves as the task anchor for all Design phase sessions. The agent comments on this issue at each session end (progress, decisions made, next design document). Human approval is signalled by applying a label (e.g. `design-approved`) or by the human closing the issue. All subsequent phase tracking may use separate issues or milestones.
