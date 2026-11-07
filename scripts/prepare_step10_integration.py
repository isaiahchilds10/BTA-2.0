"""BTA 2.0 Step 10: safely integrate Step 9 schedules into the actual app.

This script is intentionally NOT a replacement for streamlit_app.py.
It derives a proposed candidate from the actual existing source, validates
known navigation structure, and only writes the real entrypoint with --apply
on a development branch. stdlib only; no external calls.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
from pathlib import Path
import shutil
import sys

NAV = ("Home", "NBA", "NFL", "College Football", "My Slip")
CALLS = {
    "Home": "render_home_schedules(days=7, tz=\"America/New_York\")",
    "NBA": "render_sport_schedule(Sport.NBA, days=14, tz=\"America/New_York\")",
    "NFL": "render_sport_schedule(Sport.NFL, days=14, tz=\"America/New_York\")",
    "College Football": "render_sport_schedule(Sport.COLLEGE_FOOTBALL, days=14, tz=\"America/New_York\")",
}
IMPORTS = (
    "from domain.contracts import Sport\n"
    "from ui.schedule_sections import render_home_schedules, render_sport_schedule\n"
)
CANDIDATE = "streamlit_app_step10_candidate.py"

class UnsafeIntegration(ValueError):
    """The actual app differs from known safe starter structure."""


def _is_eq_page(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Compare) or len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
        return None
    lhs, rhs = node.left, node.comparators[0]
    if isinstance(lhs, ast.Name) and lhs.id == "page" and isinstance(rhs, ast.Constant) and isinstance(rhs.value, str):
        return rhs.value
    if isinstance(rhs, ast.Name) and rhs.id == "page" and isinstance(lhs, ast.Constant) and isinstance(lhs.value, str):
        return lhs.value
    return None


def _uses_selected_nav(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "sections" for t in node.targets):
            try:
                if tuple(ast.literal_eval(node.value)) != NAV:
                    continue
            except (ValueError, TypeError, MemoryError):
                continue
            return True
    return False


def _find_route(tree: ast.Module) -> tuple[dict[str, ast.If], list[ast.stmt]]:
    roots = [n for n in tree.body if isinstance(n, ast.If) and _is_eq_page(n.test) == "Home"]
    if len(roots) != 1:
        raise UnsafeIntegration("Expected exactly one top-level 'if page == Home' navigation block; source not modified.")
    branches: dict[str, ast.If] = {}
    node = roots[0]
    while True:
        name = _is_eq_page(node.test)
        if name not in NAV or name in branches:
            raise UnsafeIntegration("Unexpected or duplicated navigation branch; source not modified.")
        branches[name] = node
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            node = node.orelse[0]
            continue
        return branches, node.orelse


def _has_terminator(statements: list[ast.stmt]) -> bool:
    return any(isinstance(n, (ast.Return, ast.Raise, ast.Break, ast.Continue)) for s in statements for n in ast.walk(s))


def integrate(source: str) -> str:
    """Return modified source without touching disk; fail closed if unexpected."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise UnsafeIntegration("The existing app does not parse as Python; source not modified.") from exc
    if "render_home_schedules" in source or "render_sport_schedule" in source:
        raise UnsafeIntegration("It looks like schedules are already wired in; refusing duplicate integration.")
    if not _uses_selected_nav(tree):
        raise UnsafeIntegration("Expected the original five-section navigation list; source not modified.")
    if "import streamlit as st" not in source:
        raise UnsafeIntegration("Could not locate expected Streamlit import; source not modified.")
    branches, fallback = _find_route(tree)
    if "Home" not in branches or "My Slip" not in branches:
        raise UnsafeIntegration("Expected explicit Home and My Slip branches; source not modified.")
    if _has_terminator(branches["Home"].body):
        raise UnsafeIntegration("Home branch contains control-flow exit; unsafe to append.")
    missing = [name for name in ("NBA", "NFL", "College Football") if name not in branches]
    if missing and (not fallback or _has_terminator(fallback)):
        raise UnsafeIntegration("Missing sport branches have no safe catch-all else block; source not modified.")
    insertions: dict[int, list[str]] = {}
    # Insertion is after each already-closed branch body, while preserving any
    # existing headings, CSS, and custom My Slip code exactly as authored.
    for name in ("Home", "NBA", "NFL", "College Football"):
        if name in branches:
            body = branches[name].body
            if not body or _has_terminator(body):
                raise UnsafeIntegration(f"{name} branch cannot be safely extended.")
            indent = " " * body[0].col_offset
            insertions.setdefault(body[-1].end_lineno, []).append(f"{indent}{CALLS[name]}\n")
    if missing:
        indent = " " * fallback[0].col_offset
        # Only the sport names absent from explicit branching get a handler.
        for i, name in enumerate(missing):
            prefix = "if" if i == 0 else "elif"
            insertions.setdefault(fallback[-1].end_lineno, []).append(
                f"{indent}{prefix} page == {name!r}:\n{indent}    {CALLS[name]}\n"
            )
    lines = source.splitlines(keepends=True)
    for lineno in sorted(insertions, reverse=True):
        if lineno < 1 or lineno > len(lines):
            raise UnsafeIntegration("Line boundaries could not be verified.")
        lines[lineno:lineno] = insertions[lineno]
    proposal = "".join(lines)
    # Respect future-annotations, if present, and never force imports above it.
    import_line = next((i for i, x in enumerate(proposal.splitlines(keepends=True))
                        if x.strip() == "import streamlit as st"), None)
    if import_line is None:
        raise UnsafeIntegration("Cannot place imports safely.")
    new_lines = proposal.splitlines(keepends=True)
    new_lines.insert(import_line + 1, IMPORTS)
    proposal = "".join(new_lines)
    try:
        compile(proposal, CANDIDATE, "exec")
    except SyntaxError as exc:
        raise UnsafeIntegration("Generated candidate does not compile; source unchanged.") from exc
    # Detect that navigation labels and My Slip branch were retained.
    parsed = ast.parse(proposal)
    if not _uses_selected_nav(parsed) or "My Slip" not in _find_route(parsed)[0]:
        raise UnsafeIntegration("Navigation preservation verification failed.")
    for name, call in CALLS.items():
        if proposal.count(call) != 1:
            raise UnsafeIntegration(f"Integration count check failed for {name}.")
    return proposal


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--prepare", action="store_true", help="Generate test-only candidate (default).")
    group.add_argument("--apply", action="store_true", help="Apply reviewed candidate after successful preview.")
    args = parser.parse_args(argv)
    root = Path.cwd()
    app = root / "streamlit_app.py"
    candidate = root / CANDIDATE
    if not app.is_file() or not (root / "ui" / "schedule_sections.py").is_file():
        print("STOP: Run from repository root with streamlit_app.py and Step 9 ui/ present.", file=sys.stderr)
        return 2
    if not (root / ".git").exists():
        print("STOP: Expected a Git repository; no changes made.", file=sys.stderr)
        return 2
    original = app.read_text(encoding="utf-8")
    try:
        output = integrate(original)
    except UnsafeIntegration as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        print("Do not force this update. Share the non-secret streamlit_app.py code for a tailored patch.", file=sys.stderr)
        return 2
    if not args.apply:
        candidate.write_text(output, encoding="utf-8")
        print(f"Wrote SAFE PREVIEW ONLY: {CANDIDATE}")
        print("Next: python -m streamlit run streamlit_app_step10_candidate.py --server.address 0.0.0.0")
        print("After preview works, run the same script with --apply to update the original on your BRANCH.")
        return 0
    if not candidate.is_file() or candidate.read_text(encoding="utf-8") != output:
        print("STOP: Candidate missing or differs from current original. Run --prepare and preview again.", file=sys.stderr)
        return 2
    # Keep backup in Git metadata so it isn't accidentally committed/deployed.
    back = root / ".git" / "bta_step10_backup" / "streamlit_app.py"
    back.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(app, back)
    app.write_text(output, encoding="utf-8")
    print(f"Updated {app.name} on your current branch. Backup: {back}")
    print("Review `git diff -- streamlit_app.py`, run all tests, open Codespaces preview, then create PR.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
