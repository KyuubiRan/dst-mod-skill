#!/usr/bin/env python3
"""
Create a minimal DST mod scaffold with modinfo.lua and modmain.lua.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a minimal DST mod scaffold.")
    parser.add_argument("output_dir", type=Path, help="Target mod directory.")
    parser.add_argument("--display-name", required=True, help="Display name for modinfo.lua.")
    parser.add_argument("--description", required=True, help="Description for modinfo.lua.")
    parser.add_argument("--author", default="", help="Author name.")
    parser.add_argument("--version", default="0.1.0", help="Version string.")
    parser.add_argument(
        "--mod-type",
        choices=("all-clients", "client-only", "server-only"),
        default="all-clients",
        help="Choose the intended execution/install model.",
    )
    parser.add_argument(
        "--with-config",
        action="store_true",
        help="Include a starter configuration_options block.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite modinfo.lua or modmain.lua if they already exist.",
    )
    return parser.parse_args()


def lua_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def mod_flags(mod_type: str) -> tuple[bool, bool]:
    if mod_type == "client-only":
        return True, False
    if mod_type == "server-only":
        return False, False
    return False, True


def build_modinfo(args: argparse.Namespace) -> str:
    client_only_mod, all_clients_require_mod = mod_flags(args.mod_type)
    config_block = ""
    if args.with_config:
        config_block = """
local function MakeConfigSectionHeader(label)
    return {
        name = "",
        label = label,
        options = {
            {
                description = "",
                data = false,
            },
        },
        default = false,
    }
end

configuration_options = {
    MakeConfigSectionHeader("General"),
    {
        name = "example_toggle",
        label = "Example Toggle",
        hover = "Replace this with a real option.",
        options = {
            { description = "Off", data = false },
            { description = "On", data = true },
        },
        default = false,
    },
}
"""
    return f"""name = {lua_string(args.display_name)}
description = {lua_string(args.description)}
author = {lua_string(args.author)}
version = {lua_string(args.version)}

api_version = 10
dst_compatible = true
client_only_mod = {"true" if client_only_mod else "false"}
all_clients_require_mod = {"true" if all_clients_require_mod else "false"}

{config_block}"""


def build_modmain(mod_type: str) -> str:
    header = """local GLOBAL = GLOBAL
GLOBAL.setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})

PrefabFiles = {
}

Assets = {
}
"""
    if mod_type == "client-only":
        body = """
if TheNet:IsDedicated() then
    return
end

-- Client-only logic goes here.
"""
    elif mod_type == "server-only":
        body = """
if not TheWorld.ismastersim then
    return
end

-- Server-only logic goes here.
"""
    else:
        body = """
-- Shared setup goes here.

if not TheWorld.ismastersim then
    return
end

-- Server-authoritative logic goes here.
"""
    return (header + body).strip() + "\n"


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists. Use --force to overwrite it.")
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_file(args.output_dir / "modinfo.lua", build_modinfo(args), args.force)
    write_file(args.output_dir / "modmain.lua", build_modmain(args.mod_type), args.force)
    print(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
