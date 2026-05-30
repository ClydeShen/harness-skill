#!/usr/bin/env python3
"""Run promptfoo evals for all skills or a specific one.

Usage:
  python evals/run_evals.py                          # all skills (text + artifact tiers)
  python evals/run_evals.py --skill harness-audit
  python evals/run_evals.py --skill triage --filter "#2"
  python evals/run_evals.py --tier text              # text-contract evals only
  python evals/run_evals.py --tier artifact          # artifact evals only
  python evals/run_evals.py --tier external          # fake-GitHub evals only

Each skill has a dedicated config in evals/promptfoo/<skill-name>.yaml.
Both the response provider and the LLM judge connect to a llamacpp server
configured via EVAL_API_BASE (see .env.local / .env.example).

The --filter flag is forwarded to promptfoo's --filter-pattern to run
only tests whose description matches the given regex (e.g. "#2").

Tier metadata is read from a comment in each yaml: "# tier: text|artifact|external".
Files without a tier comment are treated as text tier (backwards compatible).
Default (no --tier) runs text + artifact.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PROMPTFOO_DIR = Path(__file__).parent / "promptfoo"

_TIER_RE = re.compile(r"^#\s*tier:\s*(\w+)", re.MULTILINE)
_DEFAULT_TIERS = {"text", "artifact"}


def _read_tier(config: Path) -> str:
    """Return the tier declared in a yaml config comment, defaulting to 'text'."""
    try:
        header = config.read_text(encoding="utf-8")[:512]
        m = _TIER_RE.search(header)
        return m.group(1) if m else "text"
    except OSError:
        return "text"

# Load .env.local from repo root if present
_env_local = REPO_ROOT / ".env.local"
if _env_local.exists():
    for line in _env_local.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())
PROMPTFOO_EXE = shutil.which("promptfoo") or shutil.which("promptfoo.cmd") or "promptfoo"


def discover_configs(skill: str | None, tier: str | None) -> list[Path]:
    """Return sorted list of per-skill YAML configs, filtered by tier if given."""
    allowed_tiers = {tier} if tier else _DEFAULT_TIERS
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
    return [p for p in all_configs if _read_tier(p) in allowed_tiers]


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
    parser.add_argument("--tier", metavar="TIER", choices=["text", "artifact", "external"],
                        help="Run only evals of this tier (default: text + artifact)")
    args = parser.parse_args()

    configs = discover_configs(args.skill, args.tier)
    print(f"Running {len(configs)} skill config(s)…", flush=True)

    exit_codes = [run_config(c, args.filter) for c in configs]
    failed = sum(1 for code in exit_codes if code != 0)
    if failed:
        print(f"\n{failed}/{len(exit_codes)} skill run(s) exited with errors.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
