# DST Mod Development Skill

[中文说明](./README_zh.md)

This repository is a local skill for Don't Starve Together mod development.
It is intended for Codex-style agent workflows around DST modding.

Its core workflow is:

- inspect official `scripts.zip`
- confirm runtime context and authority boundaries
- implement with the narrowest safe hook or patch

## Scope

This skill is designed to help with:

- inspecting `modinfo.lua` and `modmain.lua`
- classifying a mod as `all-clients`, `client-only`, or `server-only`
- tracing hooks such as `AddPrefabPostInit` and `AddComponentPostInit`
- understanding prefabs, components, stategraphs, brains, widgets, and screens
- mapping user intent to common component bundles and prefab tags
- working with recipes, placers, assets, RPC, replica, classified entities, and netvars
- organizing repeated prefab families with shared factory patterns
- symptom-driven debugging and Lua debug techniques

## Principles

- official local DST files are the source of truth
- prefer `data/databundles/scripts.zip`
- avoid copying large official functions when a smaller hook is available
- separate server, client, and local UI concerns before coding
- for existing mods, read `modinfo.lua` first and classify the mod before implementation

## Repository Layout

```text
.
├─ SKILL.md
├─ agents/
├─ references/
└─ scripts/
```

- `SKILL.md`
  - main skill instructions and workflow
- `agents/`
  - agent metadata
- `references/`
  - topic-focused reference docs
- `scripts/`
  - helper scripts
  - `dst_zip_tool.py`: inspect official `scripts.zip`
  - `init_dst_mod.py`: scaffold a basic mod skeleton

## Requirements

- local Don't Starve Together installation
- common Windows game path:
  - `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- common Windows script bundle path:
  - `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip`
- common Linux game path:
  - `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- common Linux script bundle path:
  - `~/.local/share/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- common macOS game path:
  - `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`
- common macOS script bundle path:
  - `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Python 3

If your local install path differs, provide it explicitly when using the skill.

## Common Commands

List matching files:

```bash
python scripts/dst_zip_tool.py list modutil
```

Search for a symbol:

```bash
python scripts/dst_zip_tool.py grep AddPrefabPostInit --path-glob "scripts/*.lua"
```

Read a source range:

```bash
python scripts/dst_zip_tool.py show scripts/entityscript.lua --start 600 --end 700
```

Extract one official file:

```bash
python scripts/dst_zip_tool.py extract scripts/modutil.lua --output tmp/modutil.lua
```

Scaffold a new mod:

```bash
python scripts/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

## Recommended Reading

High-value docs under `references/` include:

- `official-files.md`
  - official file map and where to read first
- `modinfo-patterns.md`
  - `modinfo.lua` metadata, dependencies, configuration layout, and its constrained execution environment
- `component-patterns.md`
  - common official components, intent-to-component bundles, and negative constraints such as infinite durability
- `tag-patterns.md`
  - high-frequency prefab tags and the difference between prefab-added and component-managed tags
- `world-system-patterns.md`
  - common world-system combinations such as `fueled`, `burnable`, `freezable`, `lootdropper`, `trader`, `hauntable`, and `deployable`
- `networking-templates.md`
  - small implementation templates for netvars, replica, classified entities, and RPC
- `stategraph-patterns.md`
  - SG object shape, `wilson` versus `wilson_client`, prediction clues, and SG hook routing
- `effects-patterns.md`
  - official light, FX prefab, particle, and sound patterns
- `task-playbook.md`
  - compact task routing and validation order
- `creation-patterns.md`
  - prefab, component, replica, and shared factory structure
- `animstate-patterns.md`
  - `inst.AnimState` patterns, symbol overrides, layer versus symbol, and animation progress control
- `template-patterns.md`
  - minimal templates plus a shared `table + factory + unpack` prefab-family template
- `diagnostic-patterns.md`
  - symptom-driven debugging checklists
- `debug-techniques.md`
  - Lua `debug` techniques such as narrow upvalue patching

## Recommended Agent Flow

When this skill is used in an agent workflow, the recommended flow is:

1. confirm the local DST path
2. read the target mod's `modinfo.lua`
3. classify the mod type
4. inspect the smallest relevant official source
5. only then implement changes
