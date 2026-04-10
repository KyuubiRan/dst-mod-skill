#!/usr/bin/env python3
"""
Lightweight integrity checks for the DST mod development skill.
"""

from __future__ import annotations

import argparse
import fnmatch
import py_compile
import re
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_FILES = [
    REPO_ROOT / "SKILL.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "README_zh.md",
]
SCRIPT_FILES = sorted((REPO_ROOT / "scripts").glob("*.py"))
REFERENCE_FILES = sorted((REPO_ROOT / "references").glob("*.md"))
COMPONENT_REFERENCE_FILES = sorted((REPO_ROOT / "references" / "components").glob("*.md"))
OFFICIAL_REFERENCE_DOCS = [
    REPO_ROOT / "references" / "official-files.md",
    REPO_ROOT / "references" / "official-examples.md",
]
CRITICAL_PATHS = [
    REPO_ROOT / "SKILL.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "README_zh.md",
    REPO_ROOT / "scripts" / "dst_zip_tool.py",
    REPO_ROOT / "scripts" / "init_dst_mod.py",
    REPO_ROOT / "scripts" / "bundle_release.py",
    REPO_ROOT / "scripts" / "tex_atlas_tool.py",
    REPO_ROOT / "scripts" / "resize_png.py",
    REPO_ROOT / "references" / "task-playbook.md",
    REPO_ROOT / "references" / "official-files.md",
    REPO_ROOT / "references" / "component-patterns.md",
    REPO_ROOT / "references" / "feature-recipes.md",
    REPO_ROOT / "references" / "texture-patterns.md",
]

PATH_PATTERN = re.compile(r"(references/[A-Za-z0-9_./-]+\.md|scripts/[A-Za-z0-9_./-]+\.py)")
OFFICIAL_SCRIPT_PATTERN = re.compile(r"`(scripts/[^`]+)`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lightweight integrity checks for this skill.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat soft warnings such as low doc counts as failures.",
    )
    return parser.parse_args()


def to_repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def check_exists(errors: list[str]) -> None:
    for path in CRITICAL_PATHS:
        if not path.exists():
            errors.append(f"missing critical path: {to_repo_relative(path)}")


def check_markdown_references(errors: list[str]) -> None:
    markdown_files = DOC_FILES + REFERENCE_FILES + COMPONENT_REFERENCE_FILES
    for doc in markdown_files:
        text = doc.read_text(encoding="utf-8")
        for match in PATH_PATTERN.findall(text):
            target = REPO_ROOT / Path(match)
            if not target.exists():
                errors.append(
                    f"broken reference in {to_repo_relative(doc)}: {match}"
                )


def check_py_compile(errors: list[str]) -> None:
    for script in SCRIPT_FILES:
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"py_compile failed for {to_repo_relative(script)}: {exc.msg}")


def normalize_official_script_ref(ref: str) -> str:
    return ref.strip()


def validate_official_script_ref(
    ref: str,
    entry_names: set[str],
    all_entries: list[str],
) -> bool:
    if "*" in ref:
        return any(fnmatch.fnmatch(name, ref) for name in all_entries)
    if ref.endswith("/"):
        return any(name.startswith(ref) for name in all_entries)
    return ref in entry_names


def check_official_script_references(errors: list[str], warnings: list[str]) -> None:
    try:
        from dst_zip_tool import resolve_zip_path
    except Exception as exc:  # pragma: no cover - defensive import fallback
        warnings.append(f"skipped official script reference validation: {exc}")
        return

    try:
        zip_path = resolve_zip_path(None)
    except Exception as exc:
        warnings.append(f"skipped official script reference validation: {exc}")
        return

    with zipfile.ZipFile(zip_path) as zf:
        all_entries = sorted(
            info.filename for info in zf.infolist() if not info.is_dir()
        )
        entry_names = set(all_entries)

    for doc in OFFICIAL_REFERENCE_DOCS:
        text = doc.read_text(encoding="utf-8")
        refs = {
            normalize_official_script_ref(ref)
            for ref in OFFICIAL_SCRIPT_PATTERN.findall(text)
        }
        for ref in sorted(refs):
            if ref.endswith(".py"):
                continue
            if not validate_official_script_ref(ref, entry_names, all_entries):
                errors.append(
                    f"broken official script reference in {to_repo_relative(doc)}: {ref}"
                )


def check_counts(warnings: list[str]) -> None:
    if len(REFERENCE_FILES) < 20:
        warnings.append(f"reference doc count looks low: {len(REFERENCE_FILES)}")
    if len(COMPONENT_REFERENCE_FILES) < 4:
        warnings.append(
            f"component detail doc count looks low: {len(COMPONENT_REFERENCE_FILES)}"
        )
    if len(SCRIPT_FILES) < 5:
        warnings.append(f"helper script count looks low: {len(SCRIPT_FILES)}")


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    check_exists(errors)
    check_markdown_references(errors)
    check_py_compile(errors)
    check_official_script_references(errors, warnings)
    check_counts(warnings)

    print(f"repo: {REPO_ROOT}")
    print(f"references: {len(REFERENCE_FILES)}")
    print(f"component_references: {len(COMPONENT_REFERENCE_FILES)}")
    print(f"scripts: {len(SCRIPT_FILES)}")

    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.strict and warnings:
        return 1

    print("check_skill: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
