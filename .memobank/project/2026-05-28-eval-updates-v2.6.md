---
name: eval-updates-v2.6
description: Updated eval provider endpoint to 127.0.0.1:8081 and created yaml eval files for 4 renamed skills after v2.6.0 dedup refactor
metadata:
  type: project
---

After v2.6.0 renamed triage→harness-triage, to-prd→harness-prd, to-issues→harness-issues, write-a-skill→write-harness-skill, the corresponding promptfoo eval yaml files were missing.

**Why:** The rename commit (865cd1c) updated skill dirs and evals.json files but did not create new `evals/promptfoo/*.yaml` configs. The runner discovers by yaml glob — no yaml = skill not tested.

**How to apply:** If adding/renaming skills in the future, always create a matching `evals/promptfoo/<skill-name>.yaml` before committing. Run `python evals/run_evals.py --skill <name>` to verify.

Changes made:
- `evals/promptfoo/provider.py` + `grader.py`: API_BASE updated from `localhost:8080` to `127.0.0.1:8081` (Qwen2.5-Coder-32B served via llamacpp)
- Created: `harness-triage.yaml` (5 evals), `harness-prd.yaml` (5 evals), `harness-issues.yaml` (5 evals), `write-harness-skill.yaml` (4 evals)
- `run_evals.py` comment updated to reflect new port

Model in use: Qwen2.5-Coder-32B-Instruct at http://127.0.0.1:8081
