# Task Playbook

Use this file as a compact decision tree.

## Before Coding

1. Check whether `modinfo.lua` and `modmain.lua` exist.
2. If `modinfo.lua` exists, read `references/modinfo-patterns.md` when metadata, dependencies, or config layout may matter.
3. If `modinfo.lua` exists, classify the mod as all-clients gameplay, client-only, or server-only from its flags before reading runtime APIs.
4. Identify the smallest official file that already matches the feature shape.
5. Inspect the exact hook or helper definition in official code.
6. Check whether the behavior is server-only, client-only, or replicated.
7. Keep the implementation smaller than the official source you inspected.

## Edit `modinfo.lua`

1. Read `references/modinfo-patterns.md`.
2. Classify the mod from `client_only_mod` and `all_clients_require_mod`.
3. Keep metadata localization inside `modinfo.lua`, not in runtime `STRINGS`.
4. Keep config helpers tiny and avoid Lua standard-library assumptions.
5. If config needs grouping, use `MakeConfigSectionHeader(...)`.

## Debug A Broken Feature

1. Read `references/diagnostic-patterns.md`.
2. Classify the symptom before touching code:
   - missing registration
   - wrong runtime context
   - missing client replication
   - wrong UI or action wiring
3. Inspect the smallest official file that matches the failing subsystem.

## Common Task Routes

### Patch Worldgen Or Presets

1. Read `references/worldgen-patterns.md`.
2. Decide whether the task belongs in `modworldgenmain.lua` or `modservercreationmain.lua`.
3. Read the smallest official worldgen or server-creation file that matches the feature shape.
4. Keep worldgen-time logic separate from normal gameplay bootstrap.

### Patch An Existing Prefab

1. Read `scripts/prefabs/<prefab>.lua`.
2. Read the component files that drive the target behavior.
3. Reach for `AddPrefabPostInit` unless the change clearly belongs elsewhere.
4. Add only the missing behavior instead of replacing the prefab wholesale.

If the only viable patch point is a closed-over helper function, read `references/debug-techniques.md` before copying a large outer function.

### Add Player-Wide Behavior

1. Read `scripts/prefabs/player_common.lua` and any involved components.
2. Reach for `AddPlayerPostInit` or a component hook.
3. Guard master-sim and client logic explicitly.

### Patch Survival, Combat, Equipment, Or Container Behavior

1. Read `references/component-patterns.md`.
2. Open the exact official component file under `scripts/components/`.
3. Read the closest official prefab that uses the same component pattern.
4. If tags, actions, animation, input, or SG flow matter, read the matching narrow reference page too.
5. Prefer a small component post-init or prefab-local setup change over rewriting the system.

### Add Or Extend A Component

1. Read `references/creation-patterns.md` for the base loading path.
2. Read `references/component-patterns.md` if the task targets a common official component.
3. Read the official component with the closest lifecycle and networking shape.
4. Reach for `AddComponentPostInit` for small extensions.
5. If the component has a replica, inspect replica and classified patterns before writing net code.
6. Register replica support with `AddReplicableComponent` when needed.

### Patch UI

1. Read `references/ui-patterns.md`.
2. Read the concrete class under `scripts/widgets/` or `scripts/screens/`.
3. Read `references/input-patterns.md` if the patch listens to keyboard, mouse, or mapped controls.
4. Reach for `AddClassPostConstruct`.
5. Patch narrowly instead of replacing the whole widget.

### Add Recipes, Actions, Or Stategraph Changes

1. Read `references/action-patterns.md`.
2. Read `references/stategraph-patterns.md` when the task touches performer states, events, prediction, or SG timing.
3. Read the relevant registration function in `scripts/modutil.lua`.
4. Read the target stategraph under `scripts/stategraphs/`.
5. Reuse an existing official action flow whenever possible.
6. Prefer `AddRecipe2` over deprecated recipe APIs.

### Patch Common World Systems

1. Read `references/world-system-patterns.md`.
2. Open the exact official component files under `scripts/components/`.
3. Check `scripts/standardcomponents.lua` for an existing helper before hand-rolling setup.
4. Read the closest official prefab that combines the same systems.
5. If player interaction or placement is involved, also inspect action or recipe routing.

### Add Recipes Or Placers

1. Read `references/recipe-patterns.md`.
2. Use `AddRecipe2` unless the task explicitly needs legacy behavior.
3. Use `MakePlacer` for placeable structures or deployables.
4. Keep recipe names, placer names, and prefab names aligned.

### Add Or Patch Brain AI

1. Read `references/brain-patterns.md`.
2. Read the closest official prefab and note which brain file it requires.
3. Read the matching file under `scripts/brains/`.
4. If the change is small, prefer `AddBrainPostInit`.
5. If the AI shape is mod-owned, create a dedicated brain file under `scripts/brains/`.

### Add Strings Or Localization

1. Read `references/string-patterns.md`.
2. Decide whether the text belongs in runtime `STRINGS` or localized `modinfo.lua` metadata.
3. If the task is really about runtime i18n architecture, read `references/runtime-i18n-patterns.md`.
4. Keep prefab and action keys aligned with uppercase `STRINGS` entries.

### Add Assets Or Icons

1. Read `references/asset-patterns.md`.
2. Decide whether the asset belongs in a prefab-local `assets` table or top-level mod `Assets`.
3. Keep atlas and texture paths explicit when a recipe or UI element depends on them.

### Pack, Unpack, Or Resize Textures

1. Read `references/texture-patterns.md`.
2. Decide whether the task is official-atlas unpacking, local TEX/XML unpacking, atlas packing, or PNG resizing.
3. Use `scripts/tex_atlas_tool.py` for atlas pack or unpack tasks.
4. Use `scripts/resize_png.py` when the task is mainly about fitting icon dimensions.
5. If the task also changes asset declarations, read `references/asset-patterns.md`.

### Add Or Patch Animation State

1. Read `references/animstate-patterns.md`.
2. Identify whether the task is about startup animation, SG-driven flow, symbol override, layer toggling, or progress-driven UI animation.
3. Read the closest official prefab, SG, widget, or screen that already uses the same pattern.
4. Verify bank, build, animation, symbol, and layer names before changing code.
5. Keep animation patches narrow.

### Add Lighting, FX, Or Sound

1. Read `references/effects-patterns.md`.
2. Decide whether the task is a lit gameplay prefab, a local-only helper, a network proxy, a particle effect, or SG-timed sound.
3. Read the closest official prefab that already matches that shape.
4. If interaction or timing also changes, inspect `references/tag-patterns.md` or `references/stategraph-patterns.md`.
5. If the task needs new textures, shaders, or sound assets, inspect `references/asset-patterns.md`.

### Add RPC, Replica, Or Netvars

1. Read `references/networking-patterns.md`.
2. Read `references/networking-templates.md` for the smallest implementation shape that fits.
3. Decide whether the need is RPC intent, replicated state, or both.
4. Read `scripts/networkclientrpc.lua` for RPC routing.
5. Read `scripts/entityreplica.lua` and a similar official prefab or component before adding replica or classified logic.
6. Keep client reads on replica or netvars, not server-only components.

### Add A New Prefab Or Item

1. Read `references/creation-patterns.md` for the loader path from `modmain.lua` to `prefabs/*.lua`.
2. Read `references/feature-recipes.md` if the request is phrased as a whole feature such as a weapon, container, creature, structure, or playable character.
3. Read `references/animstate-patterns.md` if the prefab has custom `AnimState` behavior beyond a basic idle clip.
4. Pick the closest official prefab.
5. Read that prefab and any helper calls in `scripts/standardcomponents.lua`.
6. Reuse helper constructors for burnable, freezable, physics, hauntable, floatable, and similar setup.
7. Register the prefab in `PrefabFiles` and keep assets relative to the mod root.

If the mod owns a family of near-identical prefab variants, prefer a shared factory pattern over repeated constructors. Use `scripts/prefabs/staff.lua` as the official shape reference.

### Adjust Numbers Or Balance

1. Start in `scripts/tuning.lua`.
2. Read `scripts/constants.lua` if symbolic identifiers are involved.
3. Avoid scanning unrelated prefab code until a value's usage site is unclear.

## Validation Checklist

- Check that the target file is the right entry point.
- Check that `PrefabFiles` and `Assets` cover any new prefab or asset.
- Check that server and client code are not mixed accidentally.
- Check that RPC namespace and name pairs match on both sides.
- Check that replica-only reads do not call server-only components.
- Check that the final implementation still matches the official pattern you inspected.
