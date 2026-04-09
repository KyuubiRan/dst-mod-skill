# Task Playbook

Use this file as a compact decision tree.

## Before Coding

1. Check whether `modinfo.lua` and `modmain.lua` exist.
2. If `modinfo.lua` exists, classify the mod as all-clients gameplay, client-only, or server-only from its flags before reading runtime-specific APIs.
3. Identify the smallest official file that already matches the feature shape.
4. Inspect the exact hook or helper definition in official code.
5. Check whether the behavior is server-only, client-only, or replicated.
6. Keep the implementation smaller than the official source you inspected.

## When Debugging A Broken Feature

1. Read `references/diagnostic-patterns.md` first.
2. Classify the symptom before touching code:
   - missing registration
   - wrong runtime context
   - missing client replication
   - wrong UI/action wiring
3. Inspect the smallest official file that matches the failing subsystem.

## Common Task Routes

### Patch Worldgen Or Presets

1. Read `references/worldgen-patterns.md` first.
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

1. Read `scripts/prefabs/player_common.lua` and any components involved.
2. Reach for `AddPlayerPostInit` or a component hook.
3. Guard master-sim and client logic explicitly.

### Add Or Extend A Component

1. Read `references/creation-patterns.md` for the base loading path first.
2. Read the official component with the closest lifecycle and networking shape.
3. Reach for `AddComponentPostInit` for small extensions.
4. If the component has a replica, inspect replica and classified patterns before writing net code.
5. Register replica support with `AddReplicableComponent` when needed.

### Patch UI

1. Read `references/ui-patterns.md` first.
2. Read the concrete class under `scripts/widgets/` or `scripts/screens/`.
3. Read `references/input-patterns.md` if the patch listens to keyboard, mouse, or mapped controls.
4. Reach for `AddClassPostConstruct`.
5. Patch the constructor or add listeners narrowly instead of replacing the whole widget.

### Add Recipes, Actions, Or Stategraph Changes

1. Read `references/action-patterns.md` first.
2. Read the relevant registration function in `scripts/modutil.lua`.
3. Read the target stategraph under `scripts/stategraphs/`.
4. Reuse an existing official action flow whenever possible.
5. Prefer `AddRecipe2` over deprecated recipe APIs.

### Add Recipes Or Placers

1. Read `references/recipe-patterns.md` first.
2. Use `AddRecipe2` unless the task explicitly needs legacy behavior.
3. Use `MakePlacer` for placeable structures or deployables.
4. Keep recipe names, placer names, and prefab names aligned.

### Add Or Patch Brain AI

1. Read `references/brain-patterns.md` first.
2. Read the closest official prefab and note which brain file it requires.
3. Read the matching file under `scripts/brains/`.
4. If the change is small, prefer `AddBrainPostInit`.
5. If the AI shape is mod-owned, create a dedicated brain file under `scripts/brains/`.

### Add Strings Or Localization

1. Read `references/string-patterns.md` first.
2. Decide whether the text belongs in runtime `STRINGS` or in localized `modinfo.lua` metadata.
3. Keep prefab and action keys aligned with uppercase `STRINGS` entries.

### Add Assets Or Icons

1. Read `references/asset-patterns.md` first.
2. Decide whether the asset belongs in a prefab-local `assets` table or top-level mod `Assets`.
3. Keep atlas and texture paths explicit when a recipe or UI element depends on them.

### Add RPC, Replica, Or Netvars

1. Read `references/networking-patterns.md` first.
2. Decide whether the need is RPC intent, replicated state, or both.
3. Read `scripts/networkclientrpc.lua` for RPC routing.
4. Read `scripts/entityreplica.lua` and a similar official prefab or component before adding replica or classified logic.
5. Keep client reads on replica or netvars, not server-only components.

### Add A New Prefab Or Item

1. Read `references/creation-patterns.md` for the loader path from `modmain.lua` to `prefabs/*.lua`.
2. Pick the closest official prefab.
3. Read that prefab and any helper calls in `scripts/standardcomponents.lua`.
4. Reuse helper constructors for burnable, freezable, physics, hauntable, floatable, and similar setup.
5. Register the prefab in `PrefabFiles` and keep assets relative to the mod root.

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
