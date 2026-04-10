# Worldgen Patterns

Use this file when the task touches world presets, level generation, tasks, set pieces, or server-creation customization.

## The Four Common Mod Entry Files

Official mod loading recognizes these root-level entry files:

- `modinfo.lua`
- `modmain.lua`
- `modworldgenmain.lua`
- `modservercreationmain.lua`

Pick the entry file by execution context, not by feature name.

## Official Load Behavior

Observed in `scripts/mods.lua`:

- frontend server-creation flow initializes `modservercreationmain.lua`, then `modworldgenmain.lua`
- gameplay worldgen initialization also runs `modworldgenmain.lua`
- normal gameplay runtime still uses `modmain.lua`

Relevant official lines:

- `scripts/mods.lua:442-443`
- `scripts/mods.lua:577`

This means `modworldgenmain.lua` is not only for host UI.
It is the actual worldgen-side entry point.

## Entry File Routing

- `modmain.lua`
  - normal runtime gameplay code
  - prefab post-init, components, widgets, RPC handlers, actions, SG hooks, replicas
- `modworldgenmain.lua`
  - generation-time registrations and mutations
  - rooms, tasks, task sets, levels, start locations, set-piece/worldgen data
- `modservercreationmain.lua`
  - host setup and preset-facing frontend customization
  - options or preset descriptions needed before the world exists

## Add New Content Vs Patch Existing Content

Use the `Add...` function when you are introducing a new named object.
Use the `...PreInit` function when you are modifying a built-in object that already exists.

High-frequency pairs:

- `AddRoom(name, data)`
  - add a brand-new room definition
- `AddRoomPreInit(roomname, fn)`
  - patch an existing room before worldgen consumes it
- `AddTask(name, data)`
  - add a brand-new task definition
- `AddTaskPreInit(taskname, fn)`
  - patch an existing task definition
- `AddTaskSet(name, data)`
  - add a brand-new task set
- `AddTaskSetPreInit(tasksetname, fn)`
  - patch one existing task set
- `AddTaskSetPreInitAny(fn)`
  - patch all task sets
- `AddLevel(id, data)`
  - add a new level definition
- `AddLevelPreInit(levelid, fn)`
  - patch one existing level
- `AddLevelPreInitAny(fn)`
  - patch all levels
- `AddStartLocation(name, data)`
  - register a new start location

Official helper registration for these APIs is in `scripts/modutil.lua:237-309`.

## Host Customization And Preset Data

Not every worldgen task is "add a room" or "patch a task".
Some tasks are really about host-visible world customization options or preset composition.

Key official files:

- `scripts/map/customize.lua`
  - customization groups and items
  - `LEVELCATEGORY.SETTINGS` versus `LEVELCATEGORY.WORLDGEN`
  - start-location option wiring
- `scripts/map/levels.lua`
  - preset lookup, preset ids, preset names and descriptions
  - combined preset behavior across settings and worldgen
- `scripts/widgets/redux/worldsettings/worldsettingstab.lua`
  - server-creation UI flow
  - collects worldgen and settings options separately, then merges them
- `scripts/map/startlocations.lua`
  - start-location registration and frontend refresh

High-frequency customization helpers from `scripts/modutil.lua`:

- `AddCustomizeGroup(category, name, text, desc, atlas, order)`
- `RemoveCustomizeGroup(category, name)`
- `AddCustomizeItem(category, group, name, itemsettings)`
- `RemoveCustomizeItem(category, name)`

## `LEVELCATEGORY.SETTINGS` Vs `LEVELCATEGORY.WORLDGEN`

Official `scripts/map/customize.lua` assigns world customization items to one of two main categories:

- `LEVELCATEGORY.SETTINGS`
  - world settings such as simulation or seasonal behavior
- `LEVELCATEGORY.WORLDGEN`
  - map-generation options such as generated content distribution

If the task is about what appears in the host customization screen, confirm which category the option belongs to before adding it.
Do not throw all options into worldgen by default.

## Start Location Is Also A Customization Option

Official `scripts/map/customize.lua` wires `start_location` to `startlocations.GetGenStartLocations`.
That means a custom start location is not only generation data.
It also affects what the host can select in the world customization screen.

Practical consequence:

- register the location with `AddStartLocation(...)`
- then verify the host-facing selection flow in `scripts/map/customize.lua`
- if the task is about display or grouping in the setup UI, inspect `modservercreationmain.lua` too

## Preset Composition

Official `scripts/map/levels.lua` and `scripts/widgets/redux/worldsettings/worldsettingstab.lua` keep settings presets and worldgen presets separate, then combine them when needed.

Practical consequence:

- a "preset" may actually involve both `LEVELCATEGORY.SETTINGS` and `LEVELCATEGORY.WORLDGEN`
- changing one side does not automatically rewrite the other side
- if the user says "custom preset", confirm whether they mean worldgen-only, settings-only, or combined behavior

## Why Duplicate Names Fail

Official map modules reject duplicate room/task names:

- `scripts/map/rooms.lua`
  - duplicate room add suggests using `AddRoomPreInit(...)` instead
- `scripts/map/tasks.lua`
  - duplicate task add suggests using `AddTaskPreInit(...)` instead

If the user says "tweak `BGForest`" or "change `Make a pick` start task flow", do not register a second object with the same name.
Patch the existing one.

## Intent Index

Use this as a fast router from user intent to file and API.

- "Add a new room"
  - `modworldgenmain.lua`
  - inspect `scripts/map/rooms.lua`
  - usually `AddRoom(...)`
- "Adjust an existing room"
  - `modworldgenmain.lua`
  - usually `AddRoomPreInit(...)`
- "Add a new task"
  - `modworldgenmain.lua`
  - inspect `scripts/map/tasks.lua`
  - usually `AddTask(...)`
- "Adjust an existing task"
  - `modworldgenmain.lua`
  - usually `AddTaskPreInit(...)`
- "Patch a preset or task set"
  - `modworldgenmain.lua`
  - usually `AddTaskSetPreInit(...)` or `AddTaskSetPreInitAny(...)`
- "Patch level settings or override level data"
  - `modworldgenmain.lua`
  - usually `AddLevelPreInit(...)` or `AddLevelPreInitAny(...)`
- "Add or replace a start location"
  - `modworldgenmain.lua`
  - inspect `scripts/map/startlocations.lua`
  - usually `AddStartLocation(...)`
- "Change what the host sees in the world setup screen"
  - start from `modservercreationmain.lua`
  - then verify whether the real data mutation still belongs in `modworldgenmain.lua`
- "Add a world customization option"
  - inspect `scripts/map/customize.lua`
  - usually `AddCustomizeGroup(...)` and `AddCustomizeItem(...)`
  - choose `LEVELCATEGORY.SETTINGS` or `LEVELCATEGORY.WORLDGEN` explicitly
- "Hide or remove one vanilla customization option"
  - inspect `scripts/map/customize.lua`
  - usually `RemoveCustomizeItem(...)` or `RemoveCustomizeGroup(...)`
- "Add a new host-selectable start type"
  - inspect both `scripts/map/startlocations.lua` and `scripts/map/customize.lua`
  - usually `AddStartLocation(...)`
- "Patch preset ids, descriptions, or combined preset behavior"
  - inspect `scripts/map/levels.lua`
  - inspect `scripts/widgets/redux/worldsettings/worldsettingstab.lua`

## Common Failure Points

- Wrong entry file.
  - Worldgen code in `modmain.lua` often does nothing at generation time.
- Frontend and worldgen are mixed together.
  - `modservercreationmain.lua` can prepare host-facing setup, but actual generated content usually still belongs in `modworldgenmain.lua`.
- Duplicate room or task names.
  - Prefer `...PreInit` when the target already exists.
- Runtime globals are assumed to exist during worldgen.
  - Many normal gameplay assumptions from `modmain.lua` do not belong in worldgen bootstrap.
- Host setup changes are mistaken for generated-world changes.
  - Preset panel text and actual world content are related, but they are not the same step.
- Wrong customization category.
  - `LEVELCATEGORY.SETTINGS` and `LEVELCATEGORY.WORLDGEN` are not interchangeable.
- Start location is treated as pure backend data.
  - It also feeds the frontend customization selector.
- Combined preset assumptions are too broad.
  - Settings presets and worldgen presets can be resolved separately, then merged.

## Minimal Rule Of Thumb

- Use `modmain.lua` for gameplay runtime.
- Use `modworldgenmain.lua` for world generation content.
- Use `modservercreationmain.lua` for host setup and preset-facing frontend work.
- When patching a built-in room, task, task set, or level, prefer the matching `PreInit` helper.
