#!/usr/bin/env python3
"""Structural lint for skills/{research,planning}/SKILL.md.

Run: python scripts/lint-skills.py

Exits 0 if every check passes; exits 1 with one diagnostic per failure on stderr.

Checks (added by Plan 04 of the research-planning-as-a-product feature):

- Required top-level H2 sections exist in each SKILL.md
- planning SKILL.md contains the load-bearing critic prompt version marker
- planning SKILL.md contains the location.section convention table
- planning SKILL.md contains the Plan 03 refs debug commands (cascade Gap 16)
- No bare task IDs in CLI examples (must use <plan-name>/<task-basename>)
- planning SKILL.md is at most 800 lines (the inline critic prompt cap from
  decision d06; if breached, factor the critic prompt to skills/planning/critic-v1.md)

This script intentionally uses only the stdlib so the fork doesn't need a
Python environment beyond a base CPython 3.10+.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_SKILL = REPO_ROOT / "skills" / "research" / "SKILL.md"
PLANNING_SKILL = REPO_ROOT / "skills" / "planning" / "SKILL.md"

PLANNING_LINE_CAP = 800

REQUIRED_RESEARCH_H2 = [
    "## How This Skill Works",
    "## Step 1: Understand the Research Question",
    "## Step 2: Gather Codebase Context",
    "## Step 3: Deep-Dive with Primitive Tools",
    "## Step 4: Produce Research Artifacts",
    "## Step 5: Finalize",
    "## Using `driver-rp`",
    "## Anti-Patterns",
]

REQUIRED_PLANNING_H2 = [
    "## How This Skill Works",
    "## Step 1: Ingest Research",
    "## Step 2: Clarify Scope",
    "## Step 3: Gather Broad Codebase Context",
    "## Step 4: Detail with Primitive Driver MCP Tools",
    "## Step 5: Write the Plan",
    "## Step 6: Self-Review",
    "## Step 7: Finalize",
    "## Using `driver-rp`",
    "## Dry-Run Loop",
    "## Critic Prompt",
    "## Stopping Criteria",
    "## Anti-Patterns",
]

CRITIC_VERSION_MARKER = "<!-- critic_prompt_version: v1 -->"

LOCATION_SECTION_CANARY = "frontmatter.depends_on"

REFS_DEBUG_COMMANDS = [
    "refs extract",
    "refs verify",
    "refs cache clear",
]

# Bare task IDs in `driver-rp task get / complete` examples must include the
# `<plan-name>/` prefix. This regex matches the bad form: a basename starting
# with `t<digits>-` that is NOT followed by a slash, meaning no plan prefix
# preceded it. We anchor on `driver-rp (task get|complete)` to scope the check
# to CLI examples specifically.
BARE_TASK_ID_RE = re.compile(r"driver-rp (?:task get|complete) t\d+-[^/\s]")


def _read_text(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _top_level_h2_in(lines: list[str]) -> set[str]:
    """Return literal H2 headings that appear OUTSIDE fenced code blocks.

    Code-fence-aware so embedded plan templates inside ``` fences don't get
    counted as real sections (the planning SKILL.md template includes its
    own ## headings as illustration).
    """
    found: set[str] = set()
    in_fence = False
    for raw in lines:
        stripped = raw.rstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("## ") and not stripped.startswith("### "):
            found.add(stripped)
    return found


def _check_required_h2(label: str, path: Path, required: list[str]) -> list[str]:
    if not path.exists():
        return [f"[{label}] missing file: {path}"]
    found = _top_level_h2_in(_read_text(path))
    return [
        f"[{label}] missing required H2 section: {section}"
        for section in required
        if section not in found
    ]


def _check_critic_version_marker(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    count = text.count(CRITIC_VERSION_MARKER)
    if count == 0:
        return [f"[planning] missing critic prompt version marker: {CRITIC_VERSION_MARKER}"]
    if count > 1:
        return [
            f"[planning] critic prompt version marker appears {count} times "
            f"(expected exactly 1): {CRITIC_VERSION_MARKER}"
        ]
    return []


def _check_location_section_table(path: Path) -> list[str]:
    if not path.exists():
        return []
    if LOCATION_SECTION_CANARY not in path.read_text(encoding="utf-8"):
        return [
            f"[planning] missing location.section convention table "
            f"(expected canary string '{LOCATION_SECTION_CANARY}' in critic prompt section)"
        ]
    return []


def _check_refs_debug_commands(path: Path) -> list[str]:
    """Cascade Gap 16: planning SKILL.md must reference Plan 03 refs subgroup."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return [
        f"[planning] missing Plan 03 refs debug command reference: '{cmd}' "
        f"(cascade Gap 16 — see plans/00-overview.md)"
        for cmd in REFS_DEBUG_COMMANDS
        if cmd not in text
    ]


def _check_bare_task_ids(label: str, path: Path) -> list[str]:
    if not path.exists():
        return []
    diagnostics: list[str] = []
    for lineno, raw in enumerate(_read_text(path), start=1):
        if BARE_TASK_ID_RE.search(raw):
            diagnostics.append(
                f"[{label}] bare task ID at line {lineno}: {raw.strip()} "
                f"(must use <plan-name>/<task-basename> form)"
            )
    return diagnostics


def _check_planning_line_cap(path: Path) -> list[str]:
    if not path.exists():
        return []
    line_count = len(_read_text(path))
    if line_count > PLANNING_LINE_CAP:
        return [
            f"[planning] file is {line_count} lines, exceeds cap of {PLANNING_LINE_CAP} "
            f"(decision d06: factor the critic prompt to skills/planning/critic-v1.md)"
        ]
    return []


def main() -> int:
    diagnostics: list[str] = []

    diagnostics += _check_required_h2("research", RESEARCH_SKILL, REQUIRED_RESEARCH_H2)
    diagnostics += _check_required_h2("planning", PLANNING_SKILL, REQUIRED_PLANNING_H2)

    diagnostics += _check_critic_version_marker(PLANNING_SKILL)
    diagnostics += _check_location_section_table(PLANNING_SKILL)
    diagnostics += _check_refs_debug_commands(PLANNING_SKILL)

    diagnostics += _check_bare_task_ids("research", RESEARCH_SKILL)
    diagnostics += _check_bare_task_ids("planning", PLANNING_SKILL)

    diagnostics += _check_planning_line_cap(PLANNING_SKILL)

    if diagnostics:
        for d in diagnostics:
            print(d, file=sys.stderr)
        print(f"\nlint-skills: {len(diagnostics)} failure(s)", file=sys.stderr)
        return 1

    print("lint-skills: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
