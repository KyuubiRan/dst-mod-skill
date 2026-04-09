---
name: dst-mod-development
description: Build, inspect, and debug Don't Starve Together mods using the official local DST installation and `data/databundles/scripts.zip`. Use when Codex needs to implement or explain DST mod code, inspect `modinfo.lua` or `modmain.lua`, trace hook APIs such as `AddPrefabPostInit` or `AddComponentPostInit`, look up prefab/component/stategraph behavior, inspect `TUNING` or constants, or verify asset, recipe, RPC, and replica patterns. Prefer official game files as the source of truth and avoid learning behavior from third-party mods unless the user explicitly asks for that comparison.
---

# DST Mod Development

## Overview

Use the local DST install as the primary reference.
Inspect official scripts before writing mod code and tie conclusions to concrete files inside `scripts.zip`.

## Use Official Sources First

- Default game root: `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Default script bundle: `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip`
- Prefer a user-provided game path when the path is not already known.
- If the user refuses to provide it, say that accuracy may be lower without reading the local official scripts.
- Treat official game files as authoritative. Do not learn default behavior from third-party mods unless the user explicitly asks for comparison.

## Follow This Workflow

1. Classify the request.
2. Confirm the local game path if it is not already known.
3. If `modinfo.lua` or `modmain.lua` is missing, ask whether the user wants a new mod skeleton.
4. Inspect the smallest official source that answers the question.
5. Reuse official patterns instead of guessing signatures.
6. Implement the change with the narrowest safe hook.
7. Re-check server/client boundaries, replica usage, RPC direction, and file placement.

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
- Read `references/runtime-globals.md` first, then the specific runtime page you actually need.
- Read `references/runtime-authority.md` for `TheWorld`, `TheNet`, and authority boundaries.
- Read `references/runtime-local-ui.md` for `ThePlayer`, HUD, and local UI globals.
- Read `references/entity-query-patterns.md` for `TheSim:FindEntities(...)`.
- Read `references/execution-contexts.md` before deciding whether code should be all-clients, client-only, or server-only.
- Read `references/signatures.md` first, then the narrow signature page you need.
- Read `references/hook-signatures.md`, `references/entityscript-signatures.md`, `references/helper-signatures.md`, or `references/runtime-signatures.md` for exact signatures.
- Read `references/pitfalls.md` first, then the narrow pitfalls page you need.
- Read `references/context-pitfalls.md`, `references/networking-pitfalls.md`, or `references/performance-pitfalls.md` for common mistakes.
- Read `references/mod-bootstrap.md` when the task looks like a new mod scaffold.
- Read `references/task-playbook.md` for a compact decision tree and validation checklist.

## Avoid These Mistakes

- Do not guess DST signatures or execution context.
- Do not use `ThePlayer` or HUD globals without guarding local-client availability.
- Do not copy large official files when a post-init, helper, or smaller override is enough.
