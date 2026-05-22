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
