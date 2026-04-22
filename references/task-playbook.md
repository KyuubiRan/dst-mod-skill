# Task Playbook

Use this file as a compact decision tree.

## Before Coding

1. Check whether `modinfo.lua` and the relevant root entry files such as `modmain.lua`, `modworldgenmain.lua`, or `modservercreationmain.lua` exist.
2. If `modinfo.lua` exists, read `references/patterns/modinfo-patterns.md` when metadata, dependencies, or config layout may matter.
3. If the task is mainly about which root file should own the feature, read `references/patterns/entrypoint-patterns.md`.
4. If the task is mainly about bootstrap wiring, `PrefabFiles`, top-level assets, `modimport(...)`, or character registration, read `references/patterns/modmain-patterns.md`.
5. If `modinfo.lua` exists, classify the mod as all-clients gameplay, client-only, or server-only from its flags before reading runtime APIs.
6. If the task is runtime-side, read `references/patterns/runtime-globals.md` and decide whether it is authority logic, local UI, local input, or entity-query logic.
7. Identify the smallest official file that already matches the feature shape.
8. If you still need a concrete official starter, read `references/official-examples.md`.
9. Inspect the exact hook or helper definition in official code.
10. If the real question is patch-hook choice, read `references/patterns/hook-selection-patterns.md`.
11. Check whether the behavior is server-only, client-only, or replicated.
12. Keep the implementation smaller than the official source you inspected.

## Edit `modinfo.lua`

1. Read `references/patterns/modinfo-patterns.md`.
2. Classify the mod from `client_only_mod` and `all_clients_require_mod`.
3. Keep metadata localization inside `modinfo.lua`, not in runtime `STRINGS`.
4. Keep config helpers tiny and avoid Lua standard-library assumptions.
5. If config needs grouping, use `MakeConfigSectionHeader(...)`.

## Scaffold A New Mod

1. Read `references/mod-bootstrap.md`.
2. Classify the mod as all-clients gameplay, client-only, or server-only.
3. Generate only `modinfo.lua` and `modmain.lua` first unless worldgen or host setup files are clearly required.
4. If the user wants deterministic output, use `scripts/init_dst_mod.py`.
5. Read `references/patterns/entrypoint-patterns.md` if the first real feature might belong in worldgen or host setup instead of ordinary runtime.
6. Read `references/patterns/modmain-patterns.md` before turning the fresh `modmain.lua` into a registration hub.
7. After the scaffold exists, route the first real feature through `references/templates/template-patterns.md` or the narrower subsystem page.

## Debug A Broken Feature

1. Read `references/patterns/diagnostic-patterns.md`.
2. If the user reports an explicit error or crash, inspect the relevant log before touching code.
3. Search for `LUA ERROR stack traceback:` first.
4. If the failing stack contains `../mods/workshop-<id>/...`, treat it as a Steam Workshop mod and map `<id>` directly to `steamapps/workshop/content/322330/<id>` before guessing.
5. Inspect the real Workshop source before probing `common/Don't Starve Together/mods/workshop-<id>`.
6. If the expected Workshop directory is missing, ask the user for the installed path of the crash-related mod before proposing a file-level fix.
7. If the current log is clean but the game has already been restarted, inspect `backup/`.
8. Determine whether the user is only asking for the cause or is actively debugging the mod.
9. If this is active debugging, confirm whether the failing stack belongs to the current target mod.
10. Explain the error first and ask whether the user wants help fixing it.
11. Do not modify code unless the user clearly confirms that they want a fix.
12. Classify the symptom before touching code:
   - missing registration
   - wrong runtime context
   - missing client replication
   - wrong UI or action wiring
13. Use official console checks first when the symptom is "does this thing even exist right now?"
14. Inspect the smallest official file that matches the failing subsystem.

### Decide Runtime Context

1. Read `references/patterns/runtime-globals.md`.
2. If the code mutates real gameplay state, read `references/patterns/runtime-authority.md`.
3. If the code touches HUD, screens, or local player state, read `references/patterns/runtime-local-ui.md`.
4. If the code listens for local controls, read `references/patterns/input-patterns.md`.
5. If the code scans nearby entities, read `references/patterns/entity-query-patterns.md`.

## Common Task Routes

### Patch Worldgen Or Presets

1. Read `references/patterns/worldgen-patterns.md`.
2. Decide whether the task belongs in `modworldgenmain.lua` or `modservercreationmain.lua`.
3. If the task is rooms or tasks, read `scripts/map/rooms.lua`, `scripts/map/tasks.lua`, or `scripts/map/tasksets.lua`.
4. If the task is host customization, preset ids, or start-location selection, read `scripts/map/customize.lua`, `scripts/map/levels.lua`, and `scripts/map/startlocations.lua`.
5. If the task is server-creation screen behavior, read `scripts/widgets/redux/worldsettings/worldsettingstab.lua` or the matching screen/widget file.
6. Keep worldgen-time logic separate from normal gameplay bootstrap.

### Add Or Remove World Customization Options

1. Read `references/patterns/worldgen-patterns.md`.
2. Read `scripts/map/customize.lua` first.
3. Decide whether the option belongs to `LEVELCATEGORY.SETTINGS` or `LEVELCATEGORY.WORLDGEN`.
4. Use `AddCustomizeGroup(...)`, `AddCustomizeItem(...)`, `RemoveCustomizeGroup(...)`, or `RemoveCustomizeItem(...)` from `modutil.lua`.
5. If the option is really a new start type, also inspect `scripts/map/startlocations.lua`.
6. If the task mentions presets, verify whether settings and worldgen sides both need changes.

### Patch An Existing Prefab

1. Read `scripts/prefabs/<prefab>.lua`.
2. Read the component files that drive the target behavior.
3. Read `references/patterns/hook-selection-patterns.md` if the hook choice is not obvious.
4. Reach for `AddPrefabPostInit` unless the change clearly belongs elsewhere.
5. Add only the missing behavior instead of replacing the prefab wholesale.

If the only viable patch point is a closed-over helper function, read `references/patterns/debug-techniques.md` before copying a large outer function.

### Add Player-Wide Behavior

1. Read `references/patterns/player-patterns.md`.
2. Read `scripts/prefabs/player_common.lua` and any involved components.
3. If the task needs owner-only player replication, HUD sync, or `player_classified`, read `references/patterns/player-network-patterns.md`.
4. Reach for `AddPlayerPostInit` or a component hook.
5. Guard master-sim and client logic explicitly.

### Use Standard Helper Constructors

1. Read `references/patterns/standard-helper-patterns.md`.
2. Read `references/signatures/helper-signatures.md` for exact argument order.
3. Read `scripts/standardcomponents.lua`.
4. Read the closest official prefab that already uses the same helper family.
5. Verify whether the helper belongs before `SetPristine()` or only on the master path.
6. Do not assume every helper name is equally complete; verify current helper behavior in source.

### Patch Survival, Combat, Equipment, Or Container Behavior

1. Read `references/component-patterns.md`.
2. Open the exact official component file under `scripts/components/`.
3. Read the closest official prefab that uses the same component pattern.
4. If tags, actions, animation, input, or SG flow matter, read the matching narrow reference page too.
5. Prefer a small component post-init or prefab-local setup change over rewriting the system.

### Add Or Extend A Component

1. Read `references/patterns/creation-patterns.md` for the base loading path.
2. Read `references/component-patterns.md` if the task targets a common official component.
3. Read the official component with the closest lifecycle and networking shape.
4. Read `references/patterns/hook-selection-patterns.md` if the task is really about patch-hook choice.
5. Reach for `AddComponentPostInit` for small extensions.
6. If the component has a replica, inspect replica and classified patterns before writing net code.
7. Register replica support with `AddReplicableComponent` when needed.

### Persist State Across Save Or Load

1. Read `references/patterns/persistence-patterns.md`.
2. If the task needs a ready shape, read `references/templates/persistence-templates.md`.
3. Decide whether the data is plain scalar state, cross-entity references, nested owned entities, or offline time catch-up.
4. Read `scripts/entityscript.lua` for lifecycle order before inventing a custom flow.
5. Use `OnLoadPostPass(...)` for cross-entity repair and `LongUpdate(dt)` for offline progression.
6. Keep saved data minimal and canonical.

### Persist Local Settings Or Cross-Save Profile Data

1. Read `references/patterns/persistent-string-patterns.md`.
2. Decide whether the data is truly local process data, not one world save or one entity.
3. If the user actually wants host-visible mod config, stop and route back to `references/patterns/modinfo-patterns.md`.
4. If malformed or old payloads are plausible, read `references/patterns/protected-call-patterns.md`.
5. Serialize the table to string first, usually with `json.encode(...)`.
6. Load through the callback of `TheSim:GetPersistentString(...)`; do not treat it as a synchronous return.
7. Prefix the file key with a stable mod namespace.

### Guard Serialization, Deserialization, Or Optional `require(...)`

1. Read `references/patterns/protected-call-patterns.md`.
2. Keep the protected boundary narrow: decode, encode, or one optional `require(...)`.
3. Prefer `pcall(...)` by default.
4. Reach for `xpcall(...)` only when a custom error handler materially improves the failure path.
5. Validate the decoded result after the protected call; `ok == true` is not enough.

### Patch UI

1. Read `references/patterns/ui-patterns.md`.
2. If the hard part is ownership or lifecycle routing, read `references/patterns/ui-patch-patterns.md`.
3. Read the concrete class under `scripts/widgets/` or `scripts/screens/`.
4. Read `references/patterns/input-patterns.md` if the patch listens to keyboard, mouse, or mapped controls.
5. If the UI should request real gameplay changes, route the authoritative side through networking or action flow instead of mutating gameplay directly from the widget.
6. Read `references/patterns/hook-selection-patterns.md`.
7. Reach for `AddClassPostConstruct` unless the UI is fully mod-owned and should be a new widget or screen.
8. Patch narrowly and define teardown for any handlers, listeners, or tasks.

### Understand Or Refactor `modmain.lua`

1. Read `references/patterns/modmain-patterns.md`.
2. Read `scripts/mods.lua` when load order, `modimport(...)`, `PrefabFiles`, or top-level `Assets` behavior is unclear.
3. Read `scripts/modutil.lua` when the task depends on registration helpers exposed to `modmain.lua`.
4. Decide which code is true bootstrap glue and which code should move into prefabs, components, widgets, brains, SG files, or helper modules.
5. If the file is large, split registration work into `scripts/modmain/*.lua` and keep the root `modmain.lua` small and ordered.

### Add Recipes, Actions, Or Stategraph Changes

1. Read `references/patterns/action-patterns.md`.
2. Read `references/patterns/stategraph-patterns.md` when the task touches performer states, events, prediction, or SG timing.
3. Read the relevant registration function in `scripts/modutil.lua`.
4. Read the target stategraph under `scripts/stategraphs/`.
5. Reuse an existing official action flow whenever possible.
6. Prefer `AddRecipe2` over deprecated recipe APIs.

If the request is actually a local screen or HUD interaction, stop and reroute to `references/patterns/ui-patterns.md`.

### Patch Common World Systems

1. Read `references/patterns/world-system-patterns.md`.
2. Open the exact official component files under `scripts/components/`.
3. Check `scripts/standardcomponents.lua` for an existing helper before hand-rolling setup.
4. Read the closest official prefab that combines the same systems.
5. If player interaction or placement is involved, also inspect action or recipe routing.

### Add Recipes Or Placers

1. Read `references/patterns/recipe-patterns.md`.
2. Use `AddRecipe2` unless the task explicitly needs legacy behavior.
3. Use `MakePlacer` for placeable structures or deployables.
4. Keep recipe names, placer names, and prefab names aligned.

### Add Or Patch Brain AI

1. Read `references/patterns/brain-patterns.md`.
2. Read the closest official prefab and note which brain file it requires.
3. Read the matching file under `scripts/brains/`.
4. Read the matching SG too, because AI choice and performer execution are separate layers.
5. If the change is small, prefer `AddBrainPostInit`.
6. If the AI shape is mod-owned, create a dedicated brain file under `scripts/brains/`.

### Add Strings Or Localization

1. Read `references/patterns/string-patterns.md`.
2. Decide whether the text belongs in runtime `STRINGS` or localized `modinfo.lua` metadata.
3. If the task is really about runtime i18n architecture, read `references/patterns/runtime-i18n-patterns.md`.
4. Keep prefab and action keys aligned with uppercase `STRINGS` entries.
5. If art or icon issues are mixed in, inspect `references/patterns/asset-patterns.md` separately instead of treating it as a string bug.

### Add Assets Or Icons

1. Read `references/patterns/asset-patterns.md`.
2. Decide whether the asset belongs in a prefab-local `assets` table or top-level mod `Assets`.
3. Keep atlas and texture paths explicit when a recipe or UI element depends on them.

### Pack, Unpack, Or Resize Textures

1. Read `references/patterns/texture-patterns.md`.
2. Decide whether the task is official-atlas unpacking, local TEX/XML unpacking, atlas packing, or PNG resizing.
3. Use `scripts/tex_atlas_tool.py` for atlas pack or unpack tasks.
4. Use `scripts/resize_png.py` when the task is mainly about fitting icon dimensions.
5. If the task also changes asset declarations, read `references/patterns/asset-patterns.md`.

### Add Or Patch Animation State

1. Read `references/patterns/animstate-patterns.md`.
2. Identify whether the task is about startup animation, SG-driven flow, symbol override, layer toggling, or progress-driven UI animation.
3. Read the closest official prefab, SG, widget, or screen that already uses the same pattern.
4. Verify bank, build, animation, symbol, and layer names before changing code.
5. Keep animation patches narrow.

### Add Lighting, FX, Or Sound

1. Read `references/patterns/effects-patterns.md`.
2. Decide whether the task is a lit gameplay prefab, a local-only helper, a network proxy, a particle effect, or SG-timed sound.
3. Read the closest official prefab that already matches that shape.
4. If interaction or timing also changes, inspect `references/patterns/tag-patterns.md` or `references/patterns/stategraph-patterns.md`.
5. If the task needs new textures, shaders, or sound assets, inspect `references/patterns/asset-patterns.md`.

### Add RPC, Replica, Or Netvars

1. Read `references/patterns/networking-patterns.md`.
2. Read `references/templates/networking-templates.md` for the smallest implementation shape that fits.
3. If the task is player-owned or owner-only, also read `references/patterns/player-network-patterns.md`.
4. Decide whether the need is RPC intent, replicated state, or both.
5. Read `scripts/networkclientrpc.lua` for RPC routing.
6. Read `scripts/entityreplica.lua` and a similar official prefab or component before adding replica or classified logic.
7. Keep client reads on replica or netvars, not server-only components.

### Add Shard-Aware Runtime Behavior

1. Read `references/patterns/shard-patterns.md`.
2. Decide whether the feature is current-shard only, master-shard only, or truly cross-shard.
3. If the task also saves shard-aware positions or migration state, read `references/patterns/persistence-patterns.md`.
4. Use existing migration, `worldmigrator`, or shard aggregation patterns before inventing a new protocol.
5. Reach for shard mod RPC only when ordinary client/server RPC and saved world state are not enough.

### Choose A Patch Hook

1. Read `references/patterns/hook-selection-patterns.md`.
2. If the target is one prefab, prefer `AddPrefabPostInit(...)`.
3. If the target is all players, prefer `AddPlayerPostInit(...)`.
4. If the target is a component family, prefer `AddComponentPostInit(...)`.
5. If the target is a widget or screen class, prefer `AddClassPostConstruct(...)`.
6. Use `AddPrefabPostInitAny(...)` only when a narrower hook cannot express the target set.

If the request is actually a built-in world interaction with prediction, inspect action and SG flow before defaulting to custom RPC.

### Add A New Prefab Or Item

1. Read `references/patterns/modmain-patterns.md` for the registration side of `modmain.lua`.
2. Read `references/patterns/creation-patterns.md` for the loader path from `modmain.lua` to `prefabs/*.lua`.
3. Read `references/feature-recipes.md` if the request is phrased as a whole feature such as a weapon, container, creature, structure, or playable character.
4. Read `references/patterns/animstate-patterns.md` if the prefab has custom `AnimState` behavior beyond a basic idle clip.
5. Pick the closest official prefab.
6. Read that prefab and any helper calls in `scripts/standardcomponents.lua`.
7. Reuse helper constructors for burnable, freezable, physics, hauntable, floatable, and similar setup.
8. Register the prefab in `PrefabFiles` and keep assets relative to the mod root.

If the mod owns a family of near-identical prefab variants, prefer a shared factory pattern over repeated constructors. Use `scripts/prefabs/staff.lua` as the official shape reference.

If the prefab is a creature or NPC, also route through brain and SG placement early instead of treating it as a plain item prefab.

### Add Or Refactor A Playable Character

1. Read `references/patterns/character-patterns.md`.
2. Read `references/patterns/modmain-patterns.md` for character registration and shared assets.
3. Read `scripts/prefabs/player_common.lua` before writing the character prefab from scratch.
4. Read the closest official character prefab such as `scripts/prefabs/wilson.lua` or `scripts/prefabs/wormwood.lua`.
5. Keep character identity tags and client-visible animation setup in `common_postinit`.
6. Keep stat tuning, server-only components, and authoritative listeners in `master_postinit`.
7. If the character needs progression, read `scripts/prefabs/skilltree_defs.lua` and the closest `scripts/prefabs/skilltree_<character>.lua`.
8. Only add a skill tree when the design actually needs unlockable progression or skill-gated recipes.
9. If portraits, avatar icons, or self-inspect art are wrong, inspect `scripts/screens/lobbyscreen.lua`, `scripts/screens/redux/serverslotscreen.lua`, and `scripts/widgets/inventorybar.lua` before changing unrelated gameplay code.
10. If wardrobe or loadout preview forms are wrong, inspect `scripts/widgets/redux/loadoutselect.lua`, `scripts/widgets/skinspuppet.lua`, and whether `AddModCharacter(..., modes)` uses `type` names that match the character's base skin mapping.

### Add Or Patch Official Skin Data

1. Read `references/patterns/skin-patterns.md`.
2. Decide whether the task really needs the official skin system or only preview modes or runtime build swaps.
3. Inspect `scripts/prefabskin.lua`, `scripts/prefabskins.lua`, and `scripts/prefabs/skinprefabs.lua`.
4. Inspect `scripts/widgets/redux/loadoutselect.lua` and `scripts/screens/redux/defaultskinselection.lua` before promising wardrobe behavior.
5. Do not assume mod characters get the vanilla base-skin selector.
6. Do not assume ownership exists unless the task also patches the inventory-facing selection flow.

### Adjust Numbers Or Balance

1. Start in `scripts/tuning.lua`.
2. Read `scripts/constants.lua` if symbolic identifiers are involved.
3. Avoid scanning unrelated prefab code until a value's usage site is unclear.

## Validation Checklist

- Check that the chosen root entry file matches the execution phase.
- Check that the target file is the right entry point.
- Check that `PrefabFiles` and `Assets` cover any new prefab or asset.
- Check that server and client code are not mixed accidentally.
- Check that the chosen hook is the narrowest one that matches the target.
- Check that save/load logic uses the right phase: `OnLoad`, `OnLoadPostPass`, or `LongUpdate`.
- Check whether the data should be world-save lifecycle or `TheSim` persistent-string storage.
- Check that fragile decode, encode, or optional `require(...)` boundaries use `pcall(...)` or `xpcall(...)` appropriately.
- Check that shard-aware logic distinguishes current shard, master shard, and cross-shard behavior.
- Check that local UI patches target the right layer: `controls`, `playerhud`, transient widget, popup screen, or `frontend`.
- Check that UI handlers, listeners, and tasks are cleaned up on close or destroy.
- Check that RPC namespace and name pairs match on both sides.
- Check that replica-only reads do not call server-only components.
- Check that engine globals such as `GLOBAL`, `TheSim`, `TheNet`, `TheShard`, `TheInput`, `TheFrontEnd`, `TheWorld`, and `ThePlayer` were not overwritten or rebound.
- Check that shared registries such as `TUNING`, `STRINGS`, `ACTIONS`, and mod RPC registries were extended narrowly instead of being replaced wholesale.
- Check that the final implementation still matches the official pattern you inspected.
- Run `python scripts/check_skill.py` after documentation or helper-script refactors.
