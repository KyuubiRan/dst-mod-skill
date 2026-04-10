# Entrypoint Patterns

Use this file when the task is mainly about choosing or splitting root mod entry files:

- `modinfo.lua`
- `modmain.lua`
- `modworldgenmain.lua`
- `modservercreationmain.lua`

If the task is mainly about compatibility flags or `configuration_options`, also read `references/modinfo-patterns.md`.
If the task is mainly about `modmain.lua` as the runtime registration hub, also read `references/modmain-patterns.md`.
If the task is mainly about rooms, tasks, presets, or start locations, also read `references/worldgen-patterns.md`.

## Root Entry Files Are About Phase, Not Mod Type

Do not confuse these two decisions:

- mod shape
  - client-only, server-only, or all-clients gameplay
- root entry file
  - metadata, gameplay runtime, generation-time logic, or host setup frontend

Practical consequence:

- a server-only mod can still need `modservercreationmain.lua`
- an all-clients gameplay mod can still need `modworldgenmain.lua`
- a client-only mod can still use `modmain.lua` for local UI or input bootstrap

## Official Load Order

Observed in `scripts/mods.lua`:

- preset and server-creation frontend flow prepares:
  - `modservercreationmain.lua`
  - then `modworldgenmain.lua`
- enabled gameplay mod loading later prepares:
  - `modworldgenmain.lua`
  - then `modmain.lua`

Practical consequence:

- `modservercreationmain.lua` is not the place for ordinary gameplay runtime logic
- `modworldgenmain.lua` is not only a UI helper; it is the real worldgen-side entry file
- `modmain.lua` is the normal gameplay runtime entry file

## Quick Matrix

### `modinfo.lua`

Use for:

- metadata
- compatibility flags
- dependencies
- config definitions and config-only localization

Do not use for:

- runtime string tables
- gameplay hooks
- prefab registration
- standard Lua-library-heavy helpers

Read next:

- `references/modinfo-patterns.md`

### `modmain.lua`

Use for:

- `PrefabFiles`
- top-level `Assets`
- `modimport(...)`
- gameplay hooks and post-inits
- actions, recipes, RPC, replica registration
- shared runtime bootstrap
- character registration

Do not use for:

- generation-only world data
- host setup frontend-only preset logic

Read next:

- `references/modmain-patterns.md`
- `references/creation-patterns.md`

### `modworldgenmain.lua`

Use for:

- rooms
- tasks
- task sets
- levels
- start locations
- generation-time world mutation

Do not use for:

- normal prefab hooks
- HUD or local input logic
- assuming `TheWorld` already exists like runtime gameplay code

Read next:

- `references/worldgen-patterns.md`

### `modservercreationmain.lua`

Use for:

- host-facing world setup routing
- preset-facing customization data
- frontend server-creation setup that must exist before the world does

Do not use for:

- actual generated content definitions when the data belongs to worldgen
- ordinary gameplay runtime hooks

Read next:

- `references/worldgen-patterns.md`

## Quick Routing By User Intent

- "Add a weapon, creature, structure, UI patch, input hook, action, RPC, replica, or ordinary gameplay feature"
  - start in `modmain.lua`
- "Add a room, task, level, task set, or start location"
  - start in `modworldgenmain.lua`
- "Change what the host sees in the world setup or preset screen"
  - start in `modservercreationmain.lua`
- "Change metadata, dependencies, compatibility flags, or config options"
  - start in `modinfo.lua`

## Common Two-File Cases

Some features are not single-file at the root level.

High-frequency examples:

- host-visible customization option
  - `modservercreationmain.lua` for host-facing setup
  - `modworldgenmain.lua` for generation-side data
- custom start location
  - `modworldgenmain.lua` for the start location itself
  - sometimes `modservercreationmain.lua` when setup-screen presentation also changes
- playable character mod
  - `modmain.lua` for character registration and runtime bootstrap
  - `modinfo.lua` for compatibility and config

## Common Mistakes

- putting generation-time code into `modmain.lua`
  - it often does nothing at worldgen time
- only changing `modservercreationmain.lua` and expecting real generated content to change
  - the frontend screen and the worldgen data layer are related, but not identical
- treating `modworldgenmain.lua` like a normal runtime file
  - many `TheWorld`, `ThePlayer`, HUD, or runtime-component assumptions do not belong there
- treating `modmain.lua` like the only entry file that matters
  - presets, start locations, and world customization often cross into other root files

## Minimal Rule

- use `modinfo.lua` for metadata and config
- use `modmain.lua` for gameplay runtime
- use `modworldgenmain.lua` for world generation data
- use `modservercreationmain.lua` for host setup and preset-facing frontend work
