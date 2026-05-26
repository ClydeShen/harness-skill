#!/usr/bin/env bash
set -e

echo "→ Installing Node dependencies..."
npm ci

echo "→ Validating promptfoo config..."
npm run eval:validate

echo "→ Checking Python syntax..."
python -m py_compile evals/run_evals.py evals/promptfoo/provider.py evals/promptfoo/grader.py evals/promptfoo/scaffold_helper.py

echo "✓ Environment ready. Run 'python evals/run_evals.py --skill <name>' to test a skill."
