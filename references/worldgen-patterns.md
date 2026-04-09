# Worldgen Patterns

Use this file when the task touches world presets, level generation, tasks, set pieces, or server-creation customization.

## The Four Common Mod Entry Files

Official mod loading recognizes these root-level entry files:

- `modinfo.lua`
- `modmain.lua`
- `modworldgenmain.lua`
- `modservercreationmain.lua`

## What `modworldgenmain.lua` Is For

`modworldgenmain.lua` is the world-generation-side entry point.

Observed official behavior:

- frontend loading runs it for world customization flows
- gameplay/worldgen loading also runs it

Practical use:

- worldgen tasks
- level or task-set changes
- set pieces
- worldgen-specific helpers
- generation-time registrations that should not live in normal gameplay bootstrap

## What `modservercreationmain.lua` Is For

Observed official frontend flow in `scripts/mods.lua`:

- frontend loading runs `modservercreationmain.lua`
- then it runs `modworldgenmain.lua`
- comment says this is used to populate the presets panel and related setup

Practical use:

- server-creation screen presets
- customization options shown before the world exists
- frontend-only setup related to hosting or preset selection

Do not treat it as a replacement for normal gameplay bootstrap.

## Runtime Differences

- `modmain.lua`
  - normal gameplay/runtime bootstrap
- `modworldgenmain.lua`
  - worldgen-side bootstrap
- `modservercreationmain.lua`
  - frontend/server-creation bootstrap

If a task is about actual generated world content, start in `modworldgenmain.lua`.
If a task is about the host setup UI or preset panel behavior, inspect `modservercreationmain.lua`.

## Rule Of Thumb

- Use `modmain.lua` for gameplay code.
- Use `modworldgenmain.lua` for world generation logic.
- Use `modservercreationmain.lua` for server-creation and preset-facing setup.
- Do not mix worldgen-only assumptions into normal runtime code without checking the entry context.
