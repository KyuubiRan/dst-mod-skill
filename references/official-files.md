# Official File Map

Use the local DST install as the source of truth.

## Local Paths

- Common Windows game root: `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Common Windows script bundle: `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip`
- Common Linux game root: `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- Common Linux script bundle: `~/.local/share/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Common macOS game root: `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`
- Common macOS script bundle: `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Version file: `version.txt`
- Official mod note: `mods\MAKING_MODS.txt`

Use the real local install path when it is already known.
Do not assume the common Windows path is correct on every machine.

## Infer The Game Root From The Workspace First

If the current workspace is already somewhere under the DST install tree, infer the game root directly from that path before asking the user or scanning the disk.

Example:

- workspace: `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\mods\Huohuo`
- inferred game root: `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`

Practical rule:

- if the workspace path contains `Don't Starve Together\mods\...`, treat the ancestor `Don't Starve Together` directory as the likely game root
- from that root, derive the script bundle as `data\databundles\scripts.zip`
- do not recursively scan unrelated directories when the workspace path already points into the install tree

## Check For Mod Tools Beside The Game Install

When the game root is known, also probe the sibling Steam `common` directory for `Don't Starve Mod Tools`.

Common Windows path:

- `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools`
- `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools`

High-value files for atlas workflows:

- `mod_tools\compiler_scripts\image_build.py`
- `mod_tools\tools\bin\TextureConverter.exe`
- `mod_tools\buildtools\windows\Python27\Lib\site-packages\klei\atlas.py`
- `mod_tools\buildtools\windows\Python27\Lib\site-packages\klei\textureconverter.py`

Practical rule:

- if the user needs PNG to `tex+xml` packing, prefer the local Mod Tools path over ad hoc encoders
- if Mod Tools is not installed in the usual Steam location, ask whether it exists elsewhere
- if it is not installed at all, recommend Steam App ID `245850`
- on Windows, `start steam://install/245850` opens the Steam install prompt

## Short-Lived Zip Cache

The helper script `scripts/dst_zip_tool.py` may use a short-lived local cache for `scripts.zip` entry names and recently-read text entries.

Practical rule:

- the cache is keyed by absolute zip path plus file size and `mtime_ns`
- if the game updates and `scripts.zip` changes, the cache namespace changes automatically
- the cache is intentionally short-lived and should be treated like request context, not a long-term extracted copy

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
- `scripts/prefabutil.lua`
  - Helper constructors such as `MakePlacer(...)`.
  - Read this when a mod adds placeable structures or deployable preview logic.
- `scripts/modindex.lua`
  - `modinfo.lua` parsing, API-version checks, compatibility flags, and configuration option handling.
  - Useful for validating metadata assumptions.
- `scripts/networkclientrpc.lua`
  - Mod RPC registration tables, send helpers, and namespace/id routing.
  - Read this when a task needs custom RPC flow.
- `scripts/brain.lua`
  - Base brain lifecycle and behavior-tree ownership.
  - Read this when a mod adds or patches NPC brains.
- `scripts/entityscript.lua`
  - Core instance methods for tags, components, tasks, events, buffered actions, children, SG, and brain assignment.
  - Read when a prefab method or lifecycle detail is unclear.
- `scripts/entityreplica.lua`
  - Replica-component setup and `AddReplicableComponent` behavior.
  - Read this when a custom component needs client-readable replica state.
- `scripts/standardcomponents.lua`
  - Reusable helper constructors such as burnable, freezable, physics, hauntable, floatable, and other common setup helpers.
  - Read before writing low-level setup by hand.
- `scripts/componentactions.lua`
  - Official action collector definitions and action-type routing such as `SCENE`, `USEITEM`, and `POINT`.
  - Read this before inventing custom action collection logic.
- `scripts/stategraph.lua`
  - Core SG object model: `State`, `ActionHandler`, `EventHandler`, `TimeEvent`, and timeline behavior.
  - Read this when SG object shape or prediction-side fields are unclear.
- `scripts/stategraphs/commonstates.lua`
  - Reusable helper constructors for locomotion, combat, sleep, frozen, hit, and death state families.
  - Read this before hand-writing a whole common state family.
- `scripts/componentutil.lua`
  - Shared component-side helper functions and utility logic used across the game.
  - Read when behavior seems to rely on utility wrappers rather than a single component method.
- `scripts/components/`
  - High-frequency official component implementations such as `health.lua`, `hunger.lua`, `sanity.lua`, `combat.lua`, `equippable.lua`, `armor.lua`, `weapon.lua`, and `container.lua`.
  - Read these first when the task is stat, combat, equipment, or storage centered.
- `scripts/prefabs/`
  - Also the main place to verify prefab-authored tags such as `structure`, `backpack`, `NOCLICK`, `FX`, or `hostile`.
- `scripts/mainfunctions.lua`
  - Prefab loading and asset resolution details.
  - Useful when asset paths or prefab registration behave unexpectedly.
- `scripts/input.lua`
  - Local input handler registration for keyboard, mouse, movement, text, and mapped controls.
  - Read this when a mod needs hotkeys, mouse hooks, or local input interception.
- `scripts/frontend.lua`
  - Frontend screen stack and frontend sound access such as `PushScreen(...)`, `PopScreen(...)`, and `GetSound()`.
  - Read this when a task depends on local screen flow rather than gameplay authority.
- `scripts/map/rooms.lua`
  - Core room registration and duplicate-name behavior.
  - Read this when the task adds or patches room definitions.
- `scripts/map/tasks.lua`
  - Core task registration and duplicate-name behavior.
  - Read this when the task adds or patches task definitions.
- `scripts/map/tasksets.lua`
  - Task-set definitions used by world presets.
  - Read this when the task modifies preset composition or task-set routing.
- `scripts/map/startlocations.lua`
  - Start-location definitions and world-entry routing.
  - Read this when the task changes spawn starts or custom start locations.
- `scripts/map/customize.lua`
  - World customization option definitions, categories, and mod-added customization groups or items.
  - Read this when the task adds or removes host-visible world settings or worldgen options.
- `scripts/map/levels.lua`
  - Preset lists, preset lookup by `LEVELCATEGORY`, and settings/worldgen preset composition.
  - Read this when the task depends on preset ids, preset descriptions, or combined preset behavior.
- `scripts/constants.lua`
  - Core constants, enums, and identifiers used throughout the codebase.
- `scripts/tuning.lua`
  - Tuning values and balance constants.
  - Read here first for balance changes.
- `scripts/strings.lua`
  - Core `STRINGS` tree and naming patterns.
  - Read this when a mod adds or routes runtime text.
- `scripts/consolecommands.lua`
  - High-value debug console helpers such as `c_spawn`, `c_find`, `c_findtag`, and `c_dumpworldstate`.
  - Read this when the task needs practical in-game verification or debugging shortcuts.
- `scripts/recipe.lua`
  - Recipe object behavior behind `AddRecipe2`.
  - Read this when recipe config behavior is unclear.

## Pattern Directories

- `scripts/prefabs/`
  - Official prefab implementations. Read this first when adding or modifying gameplay objects.
- `scripts/components/`
  - Official component logic. Read this first when behavior is component-driven.
- `scripts/stategraphs/`
  - State transitions, action handling, and animation logic.
- `scripts/prefabs/*fx*.lua`
  - High-value references for one-shot FX, sound proxies, light helpers, and presentation-only prefabs.
- `scripts/prefabs/lighterfire_common.lua`
  - Practical light-helper and netvar-driven portable light pattern.
- `scripts/prefabs/torchfire_barber.lua`
  - Practical `AddVFXEffect()` particle-system reference.
- `scripts/brains/`
  - AI decision logic.
- `scripts/map/levels/*.lua`
  - Concrete level definitions for forest, caves, events, and special modes.
- `scripts/map/customize.lua`
  - Category and option wiring for world settings and worldgen customization screens.
- `scripts/map/rooms/**`
  - Concrete room definitions grouped by biome or content family.
- `scripts/map/tasks/*.lua`
  - Concrete task definitions grouped by world family.
- `scripts/widgets/`
  - Widget classes used by UI patches.
- `scripts/screens/`
  - Screen-level UI flow.

## `AnimState` Reality Check

`AnimState` is engine-side.
You will not find a normal Lua implementation such as `animstate.lua` inside `scripts.zip`.

For animation work, inspect script-level usage instead:

- `scripts/prefabs/`
  - prefab startup animation, symbol swaps, build overrides
- `scripts/stategraphs/`
  - actor-driven animation flow and transition sequencing
- `scripts/widgets/`
  - progress bars and UI `SetPercent(...)` usage
- `scripts/screens/`
  - screen-local animation state updates

## Practical Reading Order

1. Read `scripts/modutil.lua` for the hook family you plan to use.
2. Read `scripts/mods.lua` and `scripts/mainfunctions.lua` when the task is about how `modmain.lua`, `PrefabFiles`, or assets are loaded.
3. Read `scripts/componentactions.lua` when the task adds custom action collection or input-to-action behavior.
4. Read `scripts/stategraph.lua` and `scripts/stategraphs/commonstates.lua` when the task adds or patches SG flow.
5. Read `scripts/networkclientrpc.lua` and `scripts/entityreplica.lua` when the task needs RPC or replica/netvar flow.
6. Read `scripts/brain.lua` and the matching file under `scripts/brains/` when the task adds NPC AI.
7. Read `scripts/prefabutil.lua` and `scripts/recipe.lua` when the task adds placers or recipes.
8. Read `scripts/strings.lua` when the task is mostly text or localization wiring.
9. Read the concrete official file that already does something similar.
10. Read `scripts/entityscript.lua` or `scripts/standardcomponents.lua` if the concrete file calls deeper helpers.
11. Read `scripts/tuning.lua` or `scripts/constants.lua` only when the task is mostly data or constants.
