---
name: promptfoo-windows-grader-timeout
description: promptfoo LLM-rubric assertions spawn stuck Python grader.py workers on Windows, causing "Worker failed to become ready within timeout" errors and 15+ zombie processes
metadata:
  type: feedback
---

promptfoo grader.py workers (used for `llm-rubric` assertions) time out on Windows during process startup. The provider.py runs fine and generates model output, but the grader subprocess never becomes ready.

**Why:** Windows subprocess startup latency exceeds promptfoo's worker initialization timeout. Each of 25 test cases spawns its own Python worker; all fail, accumulating zombie processes (~33 MB each).

**How to apply:** When evals fail with "Worker failed to become ready within timeout", do not retry blindly. Kill all stuck processes via PowerShell: `Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force`. Treat the eval infrastructure as broken for grading purposes; verify skill correctness by reading the `output-<skill>.json` response field directly instead.
