# Official File Map

Use the local DST install as the source of truth.

## Local Paths

- Game root: `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Script bundle: `data\databundles\scripts.zip`
- Version file: `version.txt`
- Official mod note: `mods\MAKING_MODS.txt`

## Confirmed Mod Entry Points

The official loader code confirms these root-level entry files:

- `modinfo.lua`
- `modmain.lua`
- `modworldgenmain.lua`
- `modservercreationmain.lua`

Use `modinfo.lua` for metadata and configuration options.
Use `modmain.lua` for the normal gameplay-side mod bootstrap.
Use the worldgen or server-creation entry files only when the task is specific to those phases.

## High-Value Official Files

- `scripts/modutil.lua`
  - Mod environment helpers and most registration APIs.
  - Start here for hooks such as prefab, component, stategraph, recipe, RPC, and widget patching.
- `scripts/mods.lua`
  - Loader flow for `modmain.lua`, `modworldgenmain.lua`, `PrefabFiles`, and `Assets`.
  - Useful when behavior depends on load order or asset registration.
- `scripts/modindex.lua`
  - `modinfo.lua` parsing, API-version checks, compatibility flags, and configuration option handling.
  - Useful for validating metadata assumptions.
- `scripts/entityscript.lua`
  - Core instance methods for tags, components, tasks, events, buffered actions, children, SG, and brain assignment.
  - Read when a prefab method or lifecycle detail is unclear.
- `scripts/standardcomponents.lua`
  - Reusable helper constructors such as burnable, freezable, physics, hauntable, floatable, and other common setup helpers.
  - Read before writing low-level setup by hand.
- `scripts/componentutil.lua`
  - Shared component-side helper functions and utility logic used across the game.
  - Read when behavior seems to rely on utility wrappers rather than a single component method.
- `scripts/prefabutil.lua`
  - Smaller prefab-side helpers.
  - Read when the relevant pattern is prefab-centric but not in `standardcomponents.lua`.
- `scripts/mainfunctions.lua`
  - Prefab loading and asset resolution details.
  - Useful when asset paths or prefab registration behave unexpectedly.
- `scripts/input.lua`
  - Local input handler registration for keyboard, mouse, movement, text, and mapped controls.
  - Read this when a mod needs hotkeys, mouse hooks, or local input interception.
- `scripts/constants.lua`
  - Core constants, enums, and identifiers used throughout the codebase.
- `scripts/tuning.lua`
  - Tuning values and balance constants.
  - Read here first for balance changes.

## Pattern Directories

- `scripts/prefabs/`
  - Official prefab implementations. Read this first when adding or modifying gameplay objects.
- `scripts/components/`
  - Official component logic. Read this first when behavior is component-driven.
- `scripts/stategraphs/`
  - State transitions, action handling, and animation logic.
- `scripts/brains/`
  - AI decision logic.
- `scripts/widgets/`
  - Widget classes used by UI patches.
- `scripts/screens/`
  - Screen-level UI flow.

## Practical Reading Order

1. Read `scripts/modutil.lua` for the hook family you plan to use.
2. Read `scripts/mods.lua` and `scripts/mainfunctions.lua` when the task is about how `modmain.lua`, `PrefabFiles`, or assets are loaded.
3. Read the concrete official file that already does something similar.
4. Read `scripts/entityscript.lua` or `scripts/standardcomponents.lua` if the concrete file calls deeper helpers.
5. Read `scripts/tuning.lua` or `scripts/constants.lua` only when the task is mostly data or constants.
