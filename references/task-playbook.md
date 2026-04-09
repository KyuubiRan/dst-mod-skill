# Task Playbook

Use this file as a compact decision tree.

## Before Coding

1. Check whether `modinfo.lua` and `modmain.lua` exist.
2. If `modinfo.lua` exists, classify the mod as all-clients gameplay, client-only, or server-only from its flags before reading runtime-specific APIs.
3. Identify the smallest official file that already matches the feature shape.
4. Inspect the exact hook or helper definition in official code.
5. Check whether the behavior is server-only, client-only, or replicated.
6. Keep the implementation smaller than the official source you inspected.

## Common Task Routes

### Patch An Existing Prefab

1. Read `scripts/prefabs/<prefab>.lua`.
2. Read the component files that drive the target behavior.
3. Reach for `AddPrefabPostInit` unless the change clearly belongs elsewhere.
4. Add only the missing behavior instead of replacing the prefab wholesale.

### Add Player-Wide Behavior

1. Read `scripts/prefabs/player_common.lua` and any components involved.
2. Reach for `AddPlayerPostInit` or a component hook.
3. Guard master-sim and client logic explicitly.

### Add Or Extend A Component

1. Read the official component with the closest lifecycle and networking shape.
2. Reach for `AddComponentPostInit` for small extensions.
3. If the component has a replica, inspect replica and classified patterns before writing net code.
4. Register replica support with `AddReplicableComponent` when needed.

### Patch UI

1. Read the concrete class under `scripts/widgets/` or `scripts/screens/`.
2. Read `references/input-patterns.md` if the patch listens to keyboard, mouse, or mapped controls.
3. Reach for `AddClassPostConstruct`.
4. Patch the constructor or add listeners narrowly instead of replacing the whole widget.

### Add Recipes, Actions, Or Stategraph Changes

1. Read the relevant registration function in `scripts/modutil.lua`.
2. Read the target stategraph under `scripts/stategraphs/`.
3. Reuse an existing official action flow whenever possible.
4. Prefer `AddRecipe2` over deprecated recipe APIs.

### Add A New Prefab Or Item

1. Pick the closest official prefab.
2. Read that prefab and any helper calls in `scripts/standardcomponents.lua`.
3. Reuse helper constructors for burnable, freezable, physics, hauntable, floatable, and similar setup.
4. Register the prefab in `PrefabFiles` and keep assets relative to the mod root.

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
