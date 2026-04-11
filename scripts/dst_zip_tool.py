#!/usr/bin/env python3
"""
Inspect official Don't Starve Together files inside scripts.zip without extracting
the full archive.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
import zipfile
from pathlib import Path

from dst_zip_cache import ZipContextCache


DEFAULT_ZIP_PATHS = [
    Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip"
    ),
    Path(
        r"D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip"
    ),
    Path.home()
    / ".local"
    / "share"
    / "Steam"
    / "steamapps"
    / "common"
    / "Don't Starve Together"
    / "data"
    / "databundles"
    / "scripts.zip",
    Path.home()
    / "Library"
    / "Application Support"
    / "Steam"
    / "steamapps"
    / "common"
    / "Don't Starve Together"
    / "data"
    / "databundles"
    / "scripts.zip",
]
TEXT_SUFFIXES = {".lua", ".txt", ".json", ".xml", ".po"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect DST official files from scripts.zip."
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=None,
        help="Path to scripts.zip. Defaults to DST_SCRIPTS_ZIP or the local DST install path.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List files in the archive.")
    list_parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Case-insensitive substring filter for entry paths.",
    )
    list_parser.add_argument(
        "--limit", type=int, default=200, help="Maximum number of entries to print."
    )

    grep_parser = subparsers.add_parser("grep", help="Search text entries.")
    grep_parser.add_argument("pattern", help="Regex pattern to search for.")
    grep_parser.add_argument(
        "--path-glob",
        default="*",
        help='Glob for entry paths, for example "scripts/prefabs/*.lua".',
    )
    grep_parser.add_argument(
        "--ignore-case", action="store_true", help="Search case-insensitively."
    )
    grep_parser.add_argument(
        "--max-results",
        type=int,
        default=200,
        help="Maximum number of matching lines to print.",
    )

    show_parser = subparsers.add_parser("show", help="Print a file with line numbers.")
    show_parser.add_argument("entry", help="Archive entry path, for example scripts/modutil.lua.")
    show_parser.add_argument("--start", type=int, default=1, help="Starting line number.")
    show_parser.add_argument("--end", type=int, default=200, help="Ending line number.")

    extract_parser = subparsers.add_parser(
        "extract", help="Extract a single archive entry to a file."
    )
    extract_parser.add_argument("entry", help="Archive entry path to extract.")
    extract_parser.add_argument(
        "--output", type=Path, required=True, help="Output file path."
    )

    stats_parser = subparsers.add_parser("stats", help="Print basic archive stats.")
    stats_parser.add_argument(
        "--top", type=int, default=20, help="Maximum number of top-level groups to print."
    )

    return parser.parse_args()


def resolve_zip_path(candidate: Path | None) -> Path:
    env_value = os.environ.get("DST_SCRIPTS_ZIP")
    if candidate is not None:
        path = candidate.expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(
            f"scripts.zip not found at {path}. Pass a valid --zip-path."
        )

    if env_value:
        path = Path(env_value).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(
            f"scripts.zip not found at {path}. Fix DST_SCRIPTS_ZIP or pass --zip-path."
        )

    for path in DEFAULT_ZIP_PATHS:
        expanded = path.expanduser()
        if expanded.is_file():
            return expanded

    tried = "\n".join(f"- {path.expanduser()}" for path in DEFAULT_ZIP_PATHS)
    raise FileNotFoundError(
        "scripts.zip not found in common locations. Pass --zip-path or set "
        f"DST_SCRIPTS_ZIP.\nTried:\n{tried}"
    )


def is_text_entry(name: str) -> bool:
    return Path(name).suffix.lower() in TEXT_SUFFIXES


def iter_entries(zf: zipfile.ZipFile):
    for info in zf.infolist():
        if info.is_dir():
            continue
        yield info


def get_entry_names(zip_path: Path, cache: ZipContextCache) -> list[str]:
    cached = cache.load_entry_names()
    if cached is not None:
        return cached
    with zipfile.ZipFile(zip_path) as zf:
        entries = [info.filename for info in iter_entries(zf)]
    cache.store_entry_names(entries)
    return entries


def read_text(zip_path: Path, cache: ZipContextCache, entry_name: str) -> list[str]:
    cached = cache.load_text_lines(entry_name)
    if cached is not None:
        return cached
    with zipfile.ZipFile(zip_path) as zf:
        try:
            raw = zf.read(entry_name)
        except KeyError as exc:
            raise FileNotFoundError(f"Archive entry not found: {entry_name}") from exc
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if is_text_entry(entry_name):
        cache.store_text_lines(entry_name, lines)
    return lines


def command_list(zip_path: Path, cache: ZipContextCache, query: str, limit: int) -> int:
    query_lower = query.lower()
    count = 0
    for entry_name in get_entry_names(zip_path, cache):
        if query_lower and query_lower not in entry_name.lower():
            continue
        print(entry_name)
        count += 1
        if count >= limit:
            break
    return 0


def command_grep(
    zip_path: Path,
    cache: ZipContextCache,
    pattern: str,
    path_glob: str,
    ignore_case: bool,
    max_results: int,
) -> int:
    flags = re.IGNORECASE if ignore_case else 0
    regex = re.compile(pattern, flags)
    results = 0
    for entry_name in get_entry_names(zip_path, cache):
        if not is_text_entry(entry_name):
            continue
        if not fnmatch.fnmatch(entry_name, path_glob):
            continue
        try:
            lines = read_text(zip_path, cache, entry_name)
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            if regex.search(line):
                print(f"{entry_name}:{number}: {line}")
                results += 1
                if results >= max_results:
                    return 0
    return 0


def command_show(
    zip_path: Path,
    cache: ZipContextCache,
    entry: str,
    start: int,
    end: int,
) -> int:
    if start < 1 or end < start:
        raise ValueError("--start must be >= 1 and --end must be >= --start.")
    lines = read_text(zip_path, cache, entry)
    for number in range(start, min(end, len(lines)) + 1):
        print(f"{number:4}: {lines[number - 1]}")
    return 0


def command_extract(zf: zipfile.ZipFile, entry: str, output: Path) -> int:
    try:
        data = zf.read(entry)
    except KeyError as exc:
        raise FileNotFoundError(f"Archive entry not found: {entry}") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    print(output)
    return 0


def command_stats(zip_path: Path, cache: ZipContextCache, top: int) -> int:
    groups: dict[str, int] = {}
    total = 0
    for entry_name in get_entry_names(zip_path, cache):
        total += 1
        parts = entry_name.split("/", 2)
        group = "/".join(parts[:2]) if len(parts) >= 2 else entry_name
        groups[group] = groups.get(group, 0) + 1
    print(f"entries: {total}")
    for name, count in sorted(groups.items(), key=lambda item: (-item[1], item[0]))[:top]:
        print(f"{count:5}  {name}")
    return 0


def main() -> int:
    args = parse_args()
    zip_path = resolve_zip_path(args.zip_path)
    cache = ZipContextCache(zip_path)
    try:
        if args.command == "list":
            return command_list(zip_path, cache, args.query, args.limit)
        if args.command == "grep":
            return command_grep(
                zip_path,
                cache,
                args.pattern,
                args.path_glob,
                args.ignore_case,
                args.max_results,
            )
        if args.command == "show":
            return command_show(zip_path, cache, args.entry, args.start, args.end)
        if args.command == "extract":
            with zipfile.ZipFile(zip_path) as zf:
                return command_extract(zf, args.entry, args.output)
        if args.command == "stats":
            return command_stats(zip_path, cache, args.top)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
