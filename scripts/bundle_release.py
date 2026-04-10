#!/usr/bin/env python3
"""
Bundle a DST mod into a release directory with exclusion rules and incremental sync.
"""

from __future__ import annotations

import argparse
import os
import shutil
import time
from fnmatch import fnmatch
from pathlib import Path


DEFAULT_EXCLUDES = (
    "*.py",
    "*.md",
    "*.png",
    ".gitignore",
    "exported/**",
)
EXCLUDED_DIR_NAMES = {"__pycache__", "exported", "tmp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bundle a DST mod into a release directory with exclusion rules."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=".",
        help="Source mod directory. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory. Defaults to ../<source_name>_release.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Extra exclusion glob. Can be passed multiple times.",
    )
    parser.add_argument(
        "--include-png",
        action="store_true",
        help="Do not exclude PNG files.",
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Do not delete files in the release directory that no longer exist in the source.",
    )
    return parser.parse_args()


def to_rel_posix(path: Path) -> str:
    return path.as_posix().lstrip("./")


def build_output_path(source: Path, output: str | None) -> Path:
    if output:
        return Path(output).expanduser().resolve()
    return (source.parent / f"{source.name}_release").resolve()


def build_excludes(args: argparse.Namespace) -> tuple[str, ...]:
    excludes = list(DEFAULT_EXCLUDES)
    if args.include_png:
        excludes = [pattern for pattern in excludes if pattern != "*.png"]
    excludes.extend(args.exclude)
    return tuple(excludes)


def is_hidden_relpath(rel_path: Path) -> bool:
    return any(part.startswith(".") for part in rel_path.parts)


def matches_exclude(rel_path: Path, patterns: tuple[str, ...]) -> bool:
    rel_posix = to_rel_posix(rel_path)
    name = rel_path.name

    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if fnmatch(rel_posix, normalized) or fnmatch(name, normalized):
            return True
        if normalized.endswith("/**"):
            root = normalized[:-3]
            if rel_posix == root or rel_posix.startswith(root + "/"):
                return True
    return False


def should_skip(rel_path: Path, patterns: tuple[str, ...]) -> bool:
    return (
        is_hidden_relpath(rel_path)
        or any(part in EXCLUDED_DIR_NAMES for part in rel_path.parts)
        or matches_exclude(rel_path, patterns)
    )


def files_are_synced(src: Path, dst: Path) -> bool:
    if not dst.is_file():
        return False
    src_stat = src.stat()
    dst_stat = dst.stat()
    return (
        src_stat.st_size == dst_stat.st_size
        and src_stat.st_mtime_ns == dst_stat.st_mtime_ns
    )


def copy_changed_file(src: Path, dst: Path) -> bool:
    if files_are_synced(src, dst):
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def sync_files(source: Path, output: Path, excludes: tuple[str, ...]) -> tuple[set[str], set[str], int]:
    expected_dirs = {""}
    expected_files: set[str] = set()
    copied_count = 0

    for root, dirs, files in os.walk(source):
        root_path = Path(root)
        rel_root = root_path.relative_to(source)

        pruned_dirs: list[str] = []
        for dirname in dirs:
            rel_dir = rel_root / dirname
            if should_skip(rel_dir, excludes):
                continue
            pruned_dirs.append(dirname)
            expected_dirs.add(to_rel_posix(rel_dir))
        dirs[:] = pruned_dirs

        for filename in files:
            rel_file = rel_root / filename
            if should_skip(rel_file, excludes):
                continue

            expected_files.add(to_rel_posix(rel_file))

            src_file = source / rel_file
            dst_file = output / rel_file
            if copy_changed_file(src_file, dst_file):
                copied_count += 1
                print(f"Copied: {rel_file.as_posix()}")

    return expected_dirs, expected_files, copied_count


def delete_stale_entries(output: Path, expected_dirs: set[str], expected_files: set[str]) -> tuple[int, int]:
    deleted_files = 0
    deleted_dirs = 0

    if not output.exists():
        return deleted_files, deleted_dirs

    for root, dirs, files in os.walk(output, topdown=False):
        root_path = Path(root)
        rel_root = root_path.relative_to(output)

        for filename in files:
            rel_file = rel_root / filename
            rel_posix = to_rel_posix(rel_file)
            if rel_posix not in expected_files:
                (output / rel_file).unlink()
                deleted_files += 1
                print(f"Deleted file: {rel_file.as_posix()}")

        for dirname in dirs:
            rel_dir = rel_root / dirname
            rel_posix = to_rel_posix(rel_dir)
            dir_path = output / rel_dir
            if rel_posix not in expected_dirs:
                shutil.rmtree(dir_path)
                deleted_dirs += 1
                print(f"Deleted dir: {rel_dir.as_posix()}")
            elif not any(dir_path.iterdir()):
                dir_path.rmdir()
                deleted_dirs += 1
                print(f"Deleted empty dir: {rel_dir.as_posix()}")

    return deleted_files, deleted_dirs


def main() -> int:
    args = parse_args()
    start_time = time.time()

    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source directory does not exist: {source}")

    output = build_output_path(source, args.output)
    excludes = build_excludes(args)

    if output == source:
        raise SystemExit("Output directory must be different from the source directory.")

    output.mkdir(parents=True, exist_ok=True)

    expected_dirs, expected_files, copied_count = sync_files(source, output, excludes)

    deleted_files = 0
    deleted_dirs = 0
    if not args.no_delete:
        deleted_files, deleted_dirs = delete_stale_entries(output, expected_dirs, expected_files)

    duration = time.time() - start_time
    print(
        "Bundle release done. "
        f"copied={copied_count} deleted_files={deleted_files} deleted_dirs={deleted_dirs} "
        f"output={output} time={duration:.2f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
