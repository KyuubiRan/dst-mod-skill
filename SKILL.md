---
name: dst-mod-development
description: Build, inspect, and debug Don't Starve Together mods using the official local DST installation and `data/databundles/scripts.zip`. Use when Codex needs to implement or explain DST mod code, inspect `modinfo.lua` or `modmain.lua`, trace hook APIs such as `AddPrefabPostInit` or `AddComponentPostInit`, look up prefab/component/stategraph behavior, inspect `TUNING` or constants, or verify asset, recipe, RPC, and replica patterns. Prefer official game files as the source of truth and avoid learning behavior from third-party mods unless the user explicitly asks for that comparison.
---

# DST Mod Development

## Overview

Use the local DST install as the primary reference.
Inspect official scripts before writing mod code and tie conclusions to concrete files inside `scripts.zip`.

## Use Official Sources First

- Common Windows game root: `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Common Windows script bundle: `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip`
- Common Linux game root: `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- Common Linux script bundle: `~/.local/share/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Common macOS game root: `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`
- Common macOS script bundle: `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Prefer a user-provided game path when the path is not already known.
- If the user refuses to provide it, say that accuracy may be lower without reading the local official scripts.
- Treat official game files as authoritative. Do not learn default behavior from third-party mods unless the user explicitly asks for comparison.

## Follow This Workflow

1. Classify the request.
2. Confirm the local game path if it is not already known.
3. Check whether `modinfo.lua` and `modmain.lua` exist in the target mod folder.
4. If `modinfo.lua` exists, read it early and classify the mod as all-clients gameplay, client-only, or server-only before choosing hooks or reading runtime globals.
5. If `modinfo.lua` is missing, ask whether the user wants a new mod skeleton.
6. Inspect the smallest official source that answers the question.
7. Reuse official patterns instead of guessing signatures.
8. Implement the change with the narrowest safe hook.
9. Re-check server/client boundaries, replica usage, RPC direction, and file placement.

## Classify Existing Mods Early

When a target mod already exists, do not only check whether `modinfo.lua` is present.
Read the compatibility flags early and infer the mod shape before making implementation choices.

Use this quick rule:

- `client_only_mod = true` and `all_clients_require_mod = false`
  - Treat it as client-only.
- `client_only_mod = false` and `all_clients_require_mod = true`
  - Treat it as all-clients gameplay.
- `client_only_mod = false` and `all_clients_require_mod = false`
  - Treat it as server-only unless the rest of the mod clearly contradicts that.

If the flags and the code shape disagree, call out the mismatch explicitly before editing.

## Use The Helper Script

Prefer the helper scripts over manually extracting or rewriting boilerplate.

Useful commands:

List matching files:
```bash
python scripts/dst_zip_tool.py list modutil
```

Search for a symbol or string:
```bash
python scripts/dst_zip_tool.py grep AddPrefabPostInit --path-glob "scripts/*.lua"
```

Read a section with line numbers:
```bash
python scripts/dst_zip_tool.py show scripts/entityscript.lua --start 600 --end 700
```

Extract one official file when a local copy is genuinely useful:
```bash
python scripts/dst_zip_tool.py extract scripts/modutil.lua --output tmp/modutil.lua
```

Scaffold a new mod:
```bash
python scripts/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

## Read These References As Needed

- Read `references/official-files.md` for file paths, entry points, and what each official file family is good for.
- Read `references/mod-api-map.md` for the highest-value mod APIs and where they live.
- Read `references/creation-patterns.md` when the task is about how prefabs, components, or helper modules are created and loaded.
- Read `references/component-patterns.md` when the task is mainly about high-frequency official components such as `inspectable`, `inventoryitem`, `stackable`, `finiteuses`, `inventory`, `container`, `edible`, `cookable`, `fuel`, `tool`, `pickable`, `workable`, `timer`, `talker`, `health`, `hunger`, `sanity`, `combat`, `equippable`, `armor`, or `weapon`.
- Read `references/tag-patterns.md` when the task depends on prefab tags, action filters, `FindEntities(...)` queries, AI targeting, or helper-entity interaction rules such as `NOCLICK`, `FX`, or `structure`.
- Read `references/template-patterns.md` when the task needs a practical starter skeleton for common mod code.
- Read `references/brain-patterns.md` when the task creates or patches NPC AI behavior.
- Read `references/worldgen-patterns.md` when the task touches `modworldgenmain.lua`, `modservercreationmain.lua`, presets, or generation-time logic.
- Read `references/ui-patterns.md` when the task creates or patches widgets, screens, HUD, or local UI flows.
- Read `references/action-patterns.md` when the task adds custom actions or stategraph action routing.
- Read `references/string-patterns.md` when the task adds names, inspect text, UI text, speech, or localized metadata.
- Read `references/asset-patterns.md` when the task adds anim zips, atlases, inventory icons, or minimap assets.
- Read `references/animstate-patterns.md` when the task touches `inst.AnimState`, animation playback flow, symbol overrides, or animation-driven UI state.
- Read `references/recipe-patterns.md` when the task adds recipes, crafting filters, or placers.
- Read `references/runtime-globals.md` first, then the specific runtime page you actually need.
- Read `references/runtime-authority.md` for `TheWorld`, `TheNet`, and authority boundaries.
- Read `references/runtime-local-ui.md` for `ThePlayer`, HUD, and local UI globals.
- Read `references/input-patterns.md` for `TheInput`, keyboard, mouse, and control handlers.
- Read `references/networking-patterns.md` when the task needs RPC, replica, classified entities, or netvars.
- Read `references/entity-query-patterns.md` for `TheSim:FindEntities(...)`.
- Read `references/execution-contexts.md` before deciding whether code should be all-clients, client-only, or server-only.
- Read `references/signatures.md` first, then the narrow signature page you need.
- Read `references/hook-signatures.md`, `references/entityscript-signatures.md`, `references/helper-signatures.md`, or `references/runtime-signatures.md` for exact signatures.
- Read `references/debug-techniques.md` when a task needs narrow closure patching or deeper Lua-side debugging.
- Read `references/pitfalls.md` first, then the narrow pitfalls page you need.
- Read `references/diagnostic-patterns.md` when the task is mostly symptom-based debugging or feature triage.
- Read `references/context-pitfalls.md`, `references/networking-pitfalls.md`, or `references/performance-pitfalls.md` for common mistakes.
- Read `references/mod-bootstrap.md` when the task looks like a new mod scaffold.
- Read `references/task-playbook.md` for a compact decision tree and validation checklist.

## Avoid These Mistakes

- Do not guess DST signatures or execution context.
- Do not use `ThePlayer` or HUD globals without guarding local-client availability.
- Do not copy large official files when a post-init, helper, or smaller override is enough.
