---
name: dst-mod-development
description: Build, inspect, and debug Don't Starve Together mods using the official local DST installation and `data/databundles/scripts.zip`. Use when Codex needs to implement or explain DST mod code, inspect `modinfo.lua` or `modmain.lua`, trace hook APIs such as `AddPrefabPostInit` or `AddComponentPostInit`, look up prefab/component/stategraph behavior, inspect `TUNING` or constants, or verify asset, skin, wardrobe, recipe, RPC, and replica patterns. Prefer official game files as the source of truth and avoid learning behavior from third-party mods unless the user explicitly asks for that comparison.
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
- If the current workspace path is already inside a DST install tree, infer the game root from the current path before asking the user or scanning anything.
- Example: if the workspace is `...\Don't Starve Together\mods\Huohuo`, infer the game root as `...\Don't Starve Together`.
- Treat a workspace under `...\Don't Starve Together\mods\...` as strong evidence that the parent `...\Don't Starve Together` directory is the local game root.
- Prefer a user-provided game path when the path is not already known.
- If the user refuses to provide it, say that accuracy may be lower without reading the local official scripts.
- When the game path is known, also check whether `Don't Starve Mod Tools` exists under the same Steam `common` directory before deciding how to handle texture packing tasks.
- If Mod Tools is not found in the usual Steam location, ask whether it is installed elsewhere.
- If the user does not have Mod Tools installed, recommend installing Steam App ID `245850` before relying on atlas packing workflows.
- On Windows, the install prompt can be launched with `start steam://install/245850`.
- When passing game paths into shell commands, quote or escape them correctly. Paths such as `Don't Starve Together` contain an apostrophe and can fail on the first command if the shell string is built carelessly.
- Treat official game files as authoritative. Do not learn default behavior from third-party mods unless the user explicitly asks for comparison.

## Follow This Workflow

1. Classify the request.
2. Confirm the local game path if it is not already known.
   - First check whether the current workspace path already sits inside a DST install tree and infer the root from that.
   - Do not recursively scan unrelated directories when the workspace path already gives a clear answer.
   - Once the game path is known, check for a sibling `Don't Starve Mod Tools` install under the same Steam `common` directory.
   - If Mod Tools is missing there, ask whether it exists in another location before falling back to non-official texture packing.
3. Check whether `modinfo.lua` and the relevant root entry files such as `modmain.lua`, `modworldgenmain.lua`, or `modservercreationmain.lua` exist in the target mod folder.
4. If `modinfo.lua` exists, read it early and classify the mod as all-clients gameplay, client-only, or server-only before choosing hooks or reading runtime globals.
5. If `modinfo.lua` is missing, ask whether the user wants a new mod skeleton.
6. Inspect the smallest official source that answers the question.
7. Reuse official patterns instead of guessing signatures.
8. Implement the change with the narrowest safe hook.
9. Re-check server/client boundaries, replica usage, RPC direction, and file placement.
10. When the user reports an error, crash, red text, or "it broke", inspect the relevant DST log before guessing.

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

`dst_zip_tool.py` keeps a short-lived local cache for archive entry lists and recently-read text files.
The cache is keyed by zip path plus file size and `mtime`, so a game update invalidates it automatically.
Treat it like a short context cache, not a persistent extraction mirror.

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

Bundle a release directory with exclusion and incremental sync:
```bash
python scripts/bundle_release.py . --output ..\MyMod_release
```

Unpack an official icon atlas:
```bash
python scripts/tex_atlas_tool.py unpack inventoryimages1
```

Pack multiple PNGs into one atlas:
```bash
python scripts/tex_atlas_tool.py pack path/to/png_dir my_atlas
```

If Mod Tools is missing and texture packing accuracy matters, install it from Steam:
```bash
start steam://install/245850
```

Resize one icon:
```bash
python scripts/resize_png.py path/to/icon.png 64x64
```

Run a lightweight skill integrity check:
```bash
python scripts/check_skill.py
```

## Read Logs Early When Debugging

- Windows client log: `~/Documents/Klei/DoNotStarveTogether/client_log.txt`
- Windows backup logs: `~/Documents/Klei/DoNotStarveTogether/backup/`
- macOS client log: `~/Documents/Klei/DoNotStarveTogether/client_log.txt`
- macOS backup logs: `~/Documents/Klei/DoNotStarveTogether/backup/`
- Linux client log: `~/.klei/DoNotStarveTogether/client_log.txt`
- Linux backup logs: `~/.klei/DoNotStarveTogether/backup/`
- For listen-host or shard runtime problems, also inspect `master_server_log.txt` and `caves_server_log.txt`.
- Search for `LUA ERROR stack traceback:` first when the user reports a Lua exception.
- If the user already restarted the game, say that the active log may have been refreshed and ask whether `backup/` should be inspected instead.
- Do not confuse warning noise such as missing default textures or shutdown-time unload messages with a real Lua stack trace.
- After reading the stack, distinguish between two intents:
  - explanation only
  - active mod debugging
- If the user is actively debugging, confirm whether the failing stack belongs to the current target mod before proposing edits.
- After you explain the error, ask whether the user wants help fixing it.
- Do not modify the user's code unless the user clearly confirms that they want a fix, patch, or implementation change.

## Read These References As Needed

- Read `references/official-files.md` for file paths, entry points, and what each official file family is good for.
- Read `references/official-examples.md` when you already know the subsystem but need the closest concrete official prefab, widget, SG, map, or networking example to open first.
- Read `references/patterns.md` when you need a grouped map of the subsystem detail pages under `references/patterns/`.
- Read `references/mod-api-map.md` for the highest-value mod APIs and where they live.
- Read `references/patterns/modinfo-patterns.md` when the task edits `modinfo.lua`, compatibility flags, dependencies, or `configuration_options`.
- Read `references/patterns/entrypoint-patterns.md` when the task is mainly about choosing between `modinfo.lua`, `modmain.lua`, `modworldgenmain.lua`, and `modservercreationmain.lua`.
- Read `references/patterns/modmain-patterns.md` when the task is mainly about `modmain.lua` as the gameplay entry hub, including `PrefabFiles`, top-level `Assets`, `modimport(...)`, `AddModCharacter(...)`, or shared startup glue.
- Read `references/patterns/creation-patterns.md` when the task is about how prefabs, components, or helper modules are created and loaded.
- Read `references/feature-recipes.md` when the user describes a whole feature such as a weapon, container, creature, structure, or playable character and you need the likely file set before drilling into subsystems.
- Read `references/patterns/character-patterns.md` when the task is specifically a playable character mod, especially when it uses `prefabs/player_common.lua`, `MakePlayerCharacter(...)`, character strings, portraits, or an optional skill tree.
- Read `references/patterns/player-patterns.md` when the task patches players as a class, uses `AddPlayerPostInit(...)`, or depends on player lifecycle events such as `playerentered` or `playeractivated`.
- Read `references/patterns/player-network-patterns.md` when the task is specifically about player-owned replicated state, `player_classified`, owner-only HUD or controller data, or deciding between player netvars, replica, and classified patterns.
- Read `references/patterns/skin-patterns.md` when the task is specifically about official skin data, wardrobe or loadout skin selection, `PREFAB_SKINS`, or `CreatePrefabSkin(...)`.
- Read `references/component-patterns.md` when the task is mainly about high-frequency official components such as `inspectable`, `inventoryitem`, `stackable`, `finiteuses`, `inventory`, `container`, `edible`, `cookable`, `fuel`, `tool`, `pickable`, `workable`, `timer`, `talker`, `health`, `hunger`, `sanity`, `combat`, `equippable`, `armor`, or `weapon`. Use it as the routing page, then open the matching detail file under `references/components/`.
- Read `references/patterns/standard-helper-patterns.md` when the task is mainly about `Make*` helper constructors from `scripts/standardcomponents.lua`, especially physics, floatable, snow-covered, or haunt helper selection.
- Read `references/patterns/tag-patterns.md` when the task depends on prefab tags, action filters, `FindEntities(...)` queries, AI targeting, or helper-entity interaction rules such as `NOCLICK`, `FX`, or `structure`.
- Read `references/templates/template-patterns.md` when the task needs a practical starter skeleton for common mod code.
- Read `references/patterns/brain-patterns.md` when the task creates or patches NPC AI behavior.
- Read `references/patterns/worldgen-patterns.md` when the task touches `modworldgenmain.lua`, `modservercreationmain.lua`, presets, or generation-time logic.
- Read `references/patterns/ui-patterns.md` when the task creates or patches widgets, screens, HUD, or local UI flows.
- Read `references/patterns/ui-patch-patterns.md` when the hard part is choosing between `widgets/controls`, `screens/playerhud`, transient widgets, popup screens, `widgets/screen`, or `frontend`.
- Read `references/patterns/action-patterns.md` when the task adds custom actions or stategraph action routing.
- Read `references/patterns/stategraph-patterns.md` when the task adds or patches states, SG events, player action performer states, prediction flow, or `wilson` versus `wilson_client` behavior.
- Read `references/patterns/world-system-patterns.md` when the task combines common world systems such as `fueled`, `burnable`, `freezable`, `lootdropper`, `trader`, `hauntable`, or `deployable`.
- Read `references/patterns/string-patterns.md` when the task adds names, inspect text, UI text, speech, or localized metadata.
- Read `references/patterns/runtime-i18n-patterns.md` when the task designs or refactors runtime localization, locale loaders, character speech inheritance, or `.po` versus Lua-table i18n strategy.
- Read `references/patterns/persistence-patterns.md` when the task needs `OnSave(...)`, `OnLoad(...)`, `OnPreLoad(...)`, `OnLoadPostPass(...)`, `LongUpdate(...)`, nested save records, or save-migration logic.
- Read `references/templates/persistence-templates.md` when the task already knows it needs save/load code and now wants the smallest correct shape.
- Read `references/patterns/persistent-string-patterns.md` when the task needs `TheSim:SetPersistentString(...)`, `TheSim:GetPersistentString(...)`, local profile-like cache files, or cross-save local mod settings.
- Read `references/patterns/protected-call-patterns.md` when the task needs `pcall(...)`, `xpcall(...)`, safe `json.decode(...)`, safe `json.encode(...)`, or optional `require(...)` around fragile serialization or deserialization boundaries.
- When the task stores local mod config through `TheSim:SetPersistentString(...)` or related persistent-string APIs, default to serializing a Lua table with `json.encode(...)` and loading it with guarded `json.decode(...)`.
- Read `references/patterns/asset-patterns.md` when the task adds anim zips, atlases, inventory icons, or minimap assets.
- Read `references/patterns/texture-patterns.md` when the task packs or unpacks atlas `tex+xml`, inspects official icon atlases from `images.zip`, or resizes PNG files for DST texture fitting.
- Read `references/patterns/animstate-patterns.md` when the task touches `inst.AnimState`, animation playback flow, symbol overrides, or animation-driven UI state.
- Read `references/patterns/effects-patterns.md` when the task adds lighting, a visual FX prefab, particle FX, or sound playback.
- Read `references/patterns/recipe-patterns.md` when the task adds recipes, crafting filters, or placers.
- Read `references/patterns/runtime-globals.md` first, then the specific runtime page you actually need.
- Read `references/patterns/runtime-authority.md` for `TheWorld`, `TheNet`, and authority boundaries.
- Read `references/patterns/runtime-local-ui.md` for `ThePlayer`, HUD, and local UI globals.
- Read `references/patterns/input-patterns.md` for `TheInput`, keyboard, mouse, and control handlers.
- Read `references/patterns/networking-patterns.md` when the task needs RPC, replica, classified entities, or netvars.
- Read `references/templates/networking-templates.md` when the task needs implementation-ready netvar, replica, classified, or RPC templates.
- Read `references/patterns/shard-patterns.md` when the task is specifically about Master/Caves runtime boundaries, shard-aware world ids, player or item migration, cluster-wide shard state, or shard mod RPC.
- Read `references/patterns/hook-selection-patterns.md` when the task is mainly about choosing between `AddPrefabPostInit(...)`, `AddPrefabPostInitAny(...)`, `AddPlayerPostInit(...)`, `AddComponentPostInit(...)`, `AddClassPostConstruct(...)`, and related patch hooks.
- Read `references/patterns/entity-query-patterns.md` for `TheSim:FindEntities(...)`.
- Read `references/patterns/execution-contexts.md` before deciding whether code should be all-clients, client-only, or server-only.
- Read `references/signatures.md` first, then the narrow signature page you need.
- Read `references/signatures/hook-signatures.md`, `references/signatures/entityscript-signatures.md`, `references/signatures/helper-signatures.md`, or `references/signatures/runtime-signatures.md` for exact signatures.
- Read `references/patterns/debug-techniques.md` when a task needs narrow closure patching or deeper Lua-side debugging.
- Read `references/pitfalls.md` first, then the narrow pitfalls page you need.
- Read `references/patterns/diagnostic-patterns.md` when the task is mostly symptom-based debugging or feature triage.
- Read `references/pitfalls/context-pitfalls.md`, `references/pitfalls/networking-pitfalls.md`, `references/pitfalls/performance-pitfalls.md`, `references/pitfalls/persistence-pitfalls.md`, `references/pitfalls/shard-pitfalls.md`, or `references/pitfalls/ui-pitfalls.md` for common mistakes.
- Read `references/mod-bootstrap.md` when the task looks like a new mod scaffold.
- Read `references/task-playbook.md` for a compact decision tree and validation checklist.

## Avoid These Mistakes

- Do not guess DST signatures or execution context.
- Do not use `ThePlayer` or HUD globals without guarding local-client availability.
- Do not copy large official files when a post-init, helper, or smaller override is enough.
- Do not treat `modmain.lua` like a prefab constructor; keep it focused on registration, routing, and startup glue.
- Do not modify the user's animation asset files by default, especially `.scml`.
- In animation-related work, default to inspection, explanation, routing, validation, or compile-flow guidance unless the user explicitly asks for an animation asset edit.
- If an animation asset edit appears necessary, stop first, tell the user which files would be changed, and get consent before editing them.
