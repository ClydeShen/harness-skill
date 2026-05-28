#!/usr/bin/env python3
"""Run promptfoo evals for all skills or a specific one.

Usage:
  python evals/run_evals.py                          # all skills
  python evals/run_evals.py --skill harness-audit
  python evals/run_evals.py --skill triage --filter "#2"

Each skill has a dedicated config in evals/promptfoo/<skill-name>.yaml.
Both the response provider and the LLM judge connect to a llamacpp server
running at 127.0.0.1:8081 (see evals/promptfoo/provider.py and grader.py).

The --filter flag is forwarded to promptfoo's --filter-pattern to run
only tests whose description matches the given regex (e.g. "#2").
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROMPTFOO_DIR = Path(__file__).parent / "promptfoo"
PROMPTFOO_EXE = shutil.which("promptfoo") or shutil.which("promptfoo.cmd") or "promptfoo"


def discover_configs(skill: str | None) -> list[Path]:
    """Return sorted list of per-skill YAML configs."""
    all_configs = sorted(
        p for p in PROMPTFOO_DIR.glob("*.yaml")
        if not p.stem.startswith("output")
    )
    if skill:
        matches = [p for p in all_configs if p.stem == skill]
        if not matches:
            available = [p.stem for p in all_configs]
            print(f"ERROR: no config found for skill '{skill}'", file=sys.stderr)
            print(f"Available: {available}", file=sys.stderr)
            sys.exit(1)
        return matches
    return all_configs


def run_config(config: Path, filter_desc: str | None) -> int:
    cmd = [PROMPTFOO_EXE, "eval", "--config", str(config), "--no-cache"]
    if filter_desc:
        cmd += ["--filter-pattern", filter_desc]
    print(f"\n{'#' * 70}", flush=True)
    print(f"# Skill: {config.stem}", flush=True)
    print(f"# Config: {config.relative_to(PROMPTFOO_DIR.parent)}", flush=True)
    print(f"{'#' * 70}", flush=True)
    result = subprocess.run(cmd, cwd=PROMPTFOO_DIR)
    return result.returncode


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Run promptfoo evals via llamacpp")
    parser.add_argument("--skill", metavar="NAME",
                        help="Run evals for one skill only (e.g. harness-audit)")
    parser.add_argument("--filter", metavar="DESC",
                        help="Filter tests by description substring (e.g. '#2')")
    args = parser.parse_args()

    configs = discover_configs(args.skill)
    print(f"Running {len(configs)} skill config(s)…", flush=True)

    exit_codes = [run_config(c, args.filter) for c in configs]
    failed = sum(1 for code in exit_codes if code != 0)
    if failed:
        print(f"\n{failed}/{len(exit_codes)} skill run(s) exited with errors.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
