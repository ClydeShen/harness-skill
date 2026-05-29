# Q&A — Practitioner Questions

Questions from people who are seriously studying harness and compound engineering.

---

## Memory System

<details>
<summary><strong>Do I have to use a specific memory system?</strong></summary>

No. The framework detects whichever is present: agentmemory, mem0, MEMORY.md, or falls back to writing key decisions into `.continue-here.json`. Pick one and use it consistently — switching mid-project splits your history.

</details>

<details>
<summary><strong>What does "memory as a black box" mean in practice?</strong></summary>

`context-handover` triggers the memory system's update and moves on — it does not validate the write. If the system fails silently, the fallback is `decisions_made` in `.continue-here.json`.

</details>

---

## Session Lifecycle

<details>
<summary><strong>Why isn't <code>/session-start</code> auto-triggered by a hook?</strong></summary>

Hooks fire unconditionally — including on 30-second throwaway sessions where a briefing is noise. The hook handles the lightweight part (writing `status: "in_progress"` and a timestamp); the skill handles interpretation and outputs a briefing only when there is prior state to read.

If you want near-automatic behaviour, add `/session-start` as a mandatory first step in your `CLAUDE.md`.

</details>

<details>
<summary><strong>What is the difference between <code>.continue-here.json</code> and <code>state.json</code>?</strong></summary>

`state.json` is machine-readable routing — phase, active task, status. `.continue-here.json` is the detailed handoff doc — completed work, remaining work, decisions, next concrete action. The split lets the hook cheaply update routing state without touching the full handoff context.

</details>

<details>
<summary><strong>What happens if context fills without running <code>/context-handover</code>?</strong></summary>

`/session-start` detects the interrupted session via a stale `last_active` timestamp and outputs a Recovery briefing using `git log`. You lose the structured handoff arrays, but git history plus GitHub comments are usually enough to reconstruct position.

</details>

---

## Phase System and GitHub

<details>
<summary><strong>Can I use this without GSD Redux's phase system?</strong></summary>

Yes. `position.phase` is just a routing label — the framework does not enforce any specific phase structure. The audit and guide skills are phase-agnostic entirely.

</details>

<details>
<summary><strong>Can I use this without GitHub?</strong></summary>

Yes. GitHub integration is conditional — comment posting and label updates are skipped when no remote or `docs/agents/` config is detected. The core (`.harness/` state, Stop hook, memory) has no GitHub dependency.

</details>

<details>
<summary><strong>Why GitHub Issues specifically and not Linear or Jira?</strong></summary>

GitHub Issues is the only tracker available to every repository by default — no credentials, no external account. It is a constraint to minimise setup friction, not an architectural preference. The framework still works with other trackers; you lose automatic comment posting and label updates.

</details>

<details>
<summary><strong>Why use a GitHub Project board?</strong></summary>

Long-running agent tasks need multiple sources of truth that can cross-validate each other. For this framework, the SOTs are:

- **git history** — commit messages and file diffs
- **GitHub Project board** — automated task tracking per issue

A harness system is only as reliable as its ability to recover from interruption. Cross-validating position across git and a task board is what makes recovery deterministic rather than reconstructive.

</details>

<details>
<summary><strong>I already have a task board. Do I need a separate GitHub Project?</strong></summary>

They serve different purposes and should not replace each other.

**Your existing board** is human-operated: updates are informal, estimates are in story points or days, and it is not structured for machine consumption.

**The GitHub Project board in this framework** is AI- and CI-operated:
- Updates are automated — the agent posts progress comments and moves cards without human input.
- Estimates are in **context windows**, not time. Claude's context window is 200K tokens on standard paid plans, 500K for Opus 4.x / Sonnet 4.6, and up to 1M in Claude Code. This is the unit that matters for agent planning, not hours.
- In a multi-person team, each developer's Claude Code instance can read the same board to coordinate autonomously without a human synchronisation step.

The human board tells humans what is happening. The GitHub Project board is a machine-readable SOT that the agent uses to orient itself across sessions.

</details>

---

## Hooks and Verification

<details>
<summary><strong>Why is the Stop hook always gap #1?</strong></summary>

Every other gap is an additive improvement. The Stop hook is a regression blocker — without it, the agent can exit after planning or partial implementation and declare success. All other improvements are undermined if the session boundary itself is unprotected.

</details>

<details>
<summary><strong>What does the Stop hook do at runtime?</strong></summary>

It fires a shell command before the agent exits. The typical pattern forces a verification prompt against the completion criteria. The framework supplies paste-ready snippets via `/harness-audit` but does not prescribe the specific command.

</details>

<details>
<summary><strong>What is a PostToolUse hook?</strong></summary>

It fires after every file write or edit — typically running lint or a quick build check. Regressions caught immediately at the point of change are cheaper to fix than regressions found at the end of a session.

</details>

---

## Anti-Patterns

<details>
<summary><strong>How do I know if my agent is hitting one of the named anti-patterns?</strong></summary>

| Pattern | Signal |
|---|---|
| **Fuzzy Done** | Task closed with "looks good" — no explicit verification in git log |
| **Proxy Signal** | Tests pass → declared done, no behavioural check |
| **Confidence Exit** | Agent reports progress mid-task and calls the rest "straightforward" |
| **Planning=Done** | PLAN.md written, issue closed, no implementation commit |

`/harness-guide` classifies sessions against these by name.

</details>

<details>
<summary><strong>Are these anti-patterns empirical or theoretical?</strong></summary>

Derived from Anthropic's [*Effective Harnesses for Long-Running Agents*](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025). The names are this framework's labels; the underlying observations are Anthropic's. Full list in [`skills/engineering/harness-guide/references/anti-patterns.md`](./skills/engineering/harness-guide/references/anti-patterns.md).

</details>

---

## Evals

<details>
<summary><strong>How are the skills evaluated?</strong></summary>

Each skill has a `promptfoo` config under `evals/promptfoo/`. The runner scaffolds a minimal project directory, sends prompts to a local llamacpp server, and judges responses via a separate LLM judge call to the same server. No hosted eval service — offline-first and reproducible.

</details>

<details>
<summary><strong>Can I run evals against a different model?</strong></summary>

Change `MODEL` and `API_BASE` in `evals/promptfoo/provider.py` and `grader.py`. Both are plain Python with no provider abstraction.

</details>
