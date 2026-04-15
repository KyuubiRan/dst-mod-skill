#!/usr/bin/env python3
"""
Invoke official Don't Starve Mod Tools to compile Spriter SCML assets or
already-exported animation zip intermediates.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_MOD_TOOLS_ROOTS = [
    Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools\mod_tools"
    ),
    Path(
        r"D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools\mod_tools"
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile DST SCML assets through the official Mod Tools."
    )
    parser.add_argument(
        "--mod-tools-root",
        type=Path,
        default=None,
        help="Path to the Mod Tools mod_tools directory.",
    )
    parser.add_argument(
        "--scml-exe",
        type=Path,
        default=None,
        help="Path to scml.exe. Defaults to DST_SCML_EXE or the local Mod Tools install.",
    )
    parser.add_argument(
        "--python-exe",
        type=Path,
        default=None,
        help=(
            "Path to the Mod Tools Python 2.7 executable. Defaults to "
            "DST_MOD_TOOLS_PYTHON or the local Mod Tools install."
        ),
    )
    parser.add_argument(
        "--buildanimation-script",
        type=Path,
        default=None,
        help=(
            "Path to buildanimation.py. Defaults to DST_BUILDANIMATION_PY or the "
            "local Mod Tools install."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved command without executing it.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build",
        help="Compile one .scml file through official scml.exe.",
    )
    build_parser.add_argument("source", type=Path, help="Path to the .scml file.")
    build_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory that will receive anim/<name>.zip. Defaults to the source "
            "folder's parent/data."
        ),
    )

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile one exported animation .zip through buildanimation.py.",
    )
    compile_parser.add_argument(
        "source",
        type=Path,
        help="Path to the intermediate animation .zip that contains build.xml and animation.xml.",
    )
    compile_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory that will receive anim/<name>.zip. Defaults to the zip "
            "folder's parent/data."
        ),
    )
    compile_parser.add_argument("--scale", type=float, default=1.0)
    compile_parser.add_argument("--platform", default="opengl")
    compile_parser.add_argument("--textureformat", default="bc3")
    compile_parser.add_argument("--hardalphatextureformat", default="bc1")
    compile_parser.add_argument("--force", action="store_true")
    compile_parser.add_argument("--square", action="store_true")
    compile_parser.add_argument("--skipantialias", action="store_true")
    compile_parser.add_argument("--ignoreexceptions", action="store_true")
    return parser.parse_args()


def resolve_existing_path(candidate: Path | None, env_name: str) -> Path | None:
    if candidate is not None:
        candidate = candidate.expanduser()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"{candidate} does not exist.")

    env_value = os.environ.get(env_name)
    if env_value:
        path = Path(env_value).expanduser()
        if path.exists():
            return path
        raise FileNotFoundError(f"{path} does not exist. Fix {env_name}.")
    return None


def resolve_mod_tools_root(candidate: Path | None) -> Path:
    resolved = resolve_existing_path(candidate, "DST_MOD_TOOLS_ROOT")
    if resolved is not None:
        return resolved
    for path in DEFAULT_MOD_TOOLS_ROOTS:
        if path.is_dir():
            return path
    tried = "\n".join(f"- {path}" for path in DEFAULT_MOD_TOOLS_ROOTS)
    raise FileNotFoundError(
        "Could not locate Don't Starve Mod Tools. Pass --mod-tools-root or set "
        f"DST_MOD_TOOLS_ROOT.\nTried:\n{tried}"
    )


def resolve_scml_exe(candidate: Path | None, mod_tools_root: Path) -> Path:
    resolved = resolve_existing_path(candidate, "DST_SCML_EXE")
    if resolved is not None:
        return resolved
    path = mod_tools_root / "scml.exe"
    if path.is_file():
        return path
    raise FileNotFoundError(f"scml.exe not found under {mod_tools_root}")


def resolve_python_exe(candidate: Path | None, mod_tools_root: Path) -> Path:
    resolved = resolve_existing_path(candidate, "DST_MOD_TOOLS_PYTHON")
    if resolved is not None:
        return resolved
    path = mod_tools_root / "buildtools" / "windows" / "python27" / "python.exe"
    if path.is_file():
        return path
    raise FileNotFoundError(f"Mod Tools python.exe not found under {mod_tools_root}")


def resolve_buildanimation_script(candidate: Path | None, mod_tools_root: Path) -> Path:
    resolved = resolve_existing_path(candidate, "DST_BUILDANIMATION_PY")
    if resolved is not None:
        return resolved
    path = mod_tools_root / "tools" / "scripts" / "buildanimation.py"
    if path.is_file():
        return path
    raise FileNotFoundError(f"buildanimation.py not found under {mod_tools_root}")


def default_output_dir(source: Path) -> Path:
    return source.parent.parent / "data"


def normalize_output_dir(source: Path, output_dir: Path | None) -> Path:
    output = (output_dir or default_output_dir(source)).expanduser()
    if output.suffix.lower() == ".zip":
        raise ValueError(
            f"{output} looks like a zip file path. The output must be a directory."
        )
    return output.resolve()


def run_command(command: list[str], cwd: Path, dry_run: bool) -> int:
    rendered = subprocess.list2cmdline(command)
    print(f"cwd: {cwd}")
    print(f"cmd: {rendered}")
    if dry_run:
        return 0
    return subprocess.call(command, cwd=str(cwd))


def ensure_source_suffix(path: Path, suffix: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Input file not found: {resolved}")
    if resolved.suffix.lower() != suffix:
        raise ValueError(f"Expected a {suffix} file, got {resolved.name}")
    return resolved


def build_from_scml(args: argparse.Namespace, mod_tools_root: Path) -> int:
    scml_exe = resolve_scml_exe(args.scml_exe, mod_tools_root)
    source = ensure_source_suffix(args.source, ".scml")
    output_dir = normalize_output_dir(source, args.output_dir)
    command = [str(scml_exe), str(source), str(output_dir)]
    exit_code = run_command(command, source.parent, args.dry_run)
    if exit_code != 0 or args.dry_run:
        return exit_code

    intermediate_zip = source.with_suffix(".zip")
    final_zip = output_dir / "anim" / f"{source.stem}.zip"
    print(f"intermediate_zip: {intermediate_zip}")
    print(f"final_zip: {final_zip}")
    if not intermediate_zip.is_file():
        raise FileNotFoundError(
            f"scml.exe finished but did not produce the intermediate zip: {intermediate_zip}"
        )
    if not final_zip.is_file():
        raise FileNotFoundError(
            f"scml.exe finished but did not produce the final anim zip: {final_zip}"
        )
    return 0


def compile_from_zip(args: argparse.Namespace, mod_tools_root: Path) -> int:
    python_exe = resolve_python_exe(args.python_exe, mod_tools_root)
    buildanimation_script = resolve_buildanimation_script(
        args.buildanimation_script, mod_tools_root
    )
    source = ensure_source_suffix(args.source, ".zip")
    output_dir = normalize_output_dir(source, args.output_dir)

    command = [
        str(python_exe),
        str(buildanimation_script),
        str(source),
        f"--outputdir={output_dir}",
        f"--scale={args.scale}",
        f"--platform={args.platform}",
        f"--textureformat={args.textureformat}",
        f"--hardalphatextureformat={args.hardalphatextureformat}",
    ]
    if args.force:
        command.append("--force")
    if args.square:
        command.append("--square")
    if args.skipantialias:
        command.append("--skipantialias")
    if args.ignoreexceptions:
        command.append("--ignoreexceptions")

    exit_code = run_command(command, source.parent, args.dry_run)
    if exit_code != 0 or args.dry_run:
        return exit_code

    final_zip = output_dir / "anim" / source.name
    print(f"final_zip: {final_zip}")
    if not final_zip.is_file():
        raise FileNotFoundError(
            "buildanimation.py finished but did not produce the final anim zip: "
            f"{final_zip}"
        )
    return 0


def main() -> int:
    args = parse_args()
    try:
        mod_tools_root = resolve_mod_tools_root(args.mod_tools_root)
        if args.command == "build":
            return build_from_scml(args, mod_tools_root)
        if args.command == "compile":
            return compile_from_zip(args, mod_tools_root)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
