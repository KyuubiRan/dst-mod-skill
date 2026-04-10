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

## Minimal Rule Of Thumb

- Use `modmain.lua` for gameplay runtime.
- Use `modworldgenmain.lua` for world generation content.
- Use `modservercreationmain.lua` for host setup and preset-facing frontend work.
- When patching a built-in room, task, task set, or level, prefer the matching `PreInit` helper.
