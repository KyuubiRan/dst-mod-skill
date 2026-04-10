# Modmain Patterns

Use this file when the task is mainly about `modmain.lua` itself:

- what the gameplay-side entry file is responsible for
- `PrefabFiles` or top-level `Assets`
- `modimport(...)` versus `require(...)`
- shared startup glue, minimap atlases, or character registration
- splitting a large `modmain.lua` into smaller registration files

If the task is mainly about prefab constructors or component classes after registration has already been decided, also read `references/creation-patterns.md`.

## What `modmain.lua` Actually Is

The official loader runs `modmain.lua` as the normal gameplay-side mod entry file.

Observed loader flow in `scripts/mods.lua`:

- the mod environment is prepared first
- the mod `scripts/?.lua` path is added to `package.path`
- `modimport(...)` is installed into the mod environment
- `ModWrangler:InitializeModMain(modname, mod, "modmain.lua")` runs the file
- after that, prefab files listed in `PrefabFiles` are loaded separately

Practical consequence:

- `modmain.lua` is the registration hub, not the place where prefab instances are created
- worldgen and server-creation logic belong in `modworldgenmain.lua` or `modservercreationmain.lua`, not here

If `modmain.lua` is missing, the loader skips it rather than crashing on that fact alone.

## What Usually Belongs In `modmain.lua`

High-value `modmain.lua` work is usually one of these:

- declare `PrefabFiles`
- declare top-level shared `Assets`
- optionally declare `FrontEndAssets` or `PreloadAssets`
- register hooks such as prefab, component, SG, widget, or class post-inits
- register actions, component actions, recipes, RPC handlers, or replicable components
- load shared string, tuning, and configuration glue
- register minimap atlases and mod characters
- split startup work into smaller files with `modimport(...)`

Good rule:

- if the code mostly says "register this", "load this", or "wire these systems together", it probably belongs in `modmain.lua`
- if the code mostly says "create this entity instance" or "run this entity behavior every time", it probably belongs in `prefabs/*.lua`, a component, a brain, or an SG

## What Usually Does Not Belong Here

- worldgen or host-setup logic
- per-instance prefab construction
- heavy top-level runtime logic that assumes `TheWorld`, `ThePlayer`, or a spawned entity already exists
- guard code that assumes `TheWorld` already exists at mod-load time
- large reusable modules that should be returned from `require(...)`

Top-level `modmain.lua` code runs during mod loading, so prefer registrations and setup over ordinary gameplay execution.

## Common Environment Passthrough

Many mods use a small passthrough so unprefixed globals resolve against `GLOBAL`:

```lua
local GLOBAL = GLOBAL
setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})
```

This is a convenience pattern, not a requirement.

Practical rule:

- use it when the mod will frequently touch global DST APIs
- keep it near the top of `modmain.lua`
- do not confuse it with registration; it only changes name lookup behavior

## `modimport(...)` Versus `require(...)`

These are different tools.

Observed `modimport(...)` behavior in `scripts/mods.lua`:

- loads from `env.MODROOT .. modulename`
- appends `.lua` if missing
- executes inside the mod environment

Practical rule:

- use `modimport("scripts/modmain/init")` or similar for ordered startup files that mainly perform side-effect registrations
- use `require("widgets/foo")`, `require("brains/foo")`, or similar for reusable modules that should return a table, class, or constructor

Good heuristic:

- `modimport(...)` is for "run this file now"
- `require(...)` is for "load this module and use its return value"

## `PrefabFiles` Only Registers Prefab Files

`PrefabFiles` does not create prefab instances by itself.

Observed flow in `scripts/mods.lua`:

- `modmain.lua` finishes first
- `RegisterPrefabs()` iterates `mod.PrefabFiles`
- each entry is loaded from `prefabs/<name>.lua`
- returned `Prefab(...)` objects are copied into the global prefab table

Practical consequence:

- `PrefabFiles = { "my_item" }` means the loader should look for `prefabs/my_item.lua`
- if a new prefab "does not exist", check `PrefabFiles` before debugging its constructor
- the string should be the prefab file path without `.lua`

## Top-Level `Assets` Are Shared Mod Assets

Top-level `Assets` in `modmain.lua` are not tied to one gameplay prefab file.

Observed flow in `scripts/mods.lua`:

- after prefab registration, the loader creates `Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)`
- that default mod prefab carries the mod-level asset table

Practical consequence:

- use top-level `Assets` for shared atlases, portraits, character art, skill atlases, or shared anim zips
- keep one-off gameplay prefab assets in the prefab file that actually owns them
- register global minimap atlases from `modmain.lua` with `AddMinimapAtlas(...)`

Related helpers exposed from `scripts/modutil.lua`:

- `AddMinimapAtlas(...)`
- `ReloadFrontEndAssets()`
- `ReloadPreloadAssets()`

If the task is mainly about asset declarations or texture paths, also read `references/asset-patterns.md`.

## Split Large `modmain.lua` Files On Purpose

When `modmain.lua` starts turning into a giant mixed file, split it into small registration files and keep the root file as the hub.

A clean pattern is:

1. set up the environment passthrough
2. declare `PrefabFiles` and shared `Assets`
3. `modimport("scripts/modmain/init.lua")`
4. keep only small startup glue after imports

Inside `scripts/modmain/init.lua`, group by concern:

- configuration
- strings or i18n bootstrap
- recipes and actions
- UI
- replicas or RPC
- hooks
- SG registration
- linkage or compatibility glue

Because `modimport(...)` executes immediately, keep the load order explicit instead of treating it like an unordered module list.

## Character-Mod Glue Often Starts Here

Character mods often keep this registration in `modmain.lua`:

- character portraits and select-screen assets in top-level `Assets`
- `AddMinimapAtlas("images/map_icons/<name>.xml")`
- `AddModCharacter("<name>", "FEMALE")` or the matching gender
- startup item glue through tuning tables
- `TUNING.STARTING_ITEM_IMAGE_OVERRIDE[...]` when custom starter items need correct icons

Keep metadata-only localization in `modinfo.lua`.
Keep runtime speech and gameplay strings in runtime string files instead.

## Runtime Guards In `modmain.lua`

Do not treat `modmain.lua` like a prefab constructor.

Useful guard rules:

- local input or HUD wiring often belongs behind `if not TheNet:IsDedicated() then`
- authoritative entity behavior usually belongs in prefab constructors, components, or post-init callbacks guarded by `TheWorld.ismastersim`
- do not assume `TheWorld` already exists while `modmain.lua` is loading
- avoid a blanket top-level `if not TheWorld.ismastersim then return end` unless you are sure the mod has no client-side registrations at all

That last mistake is common because it can accidentally skip:

- local UI patches
- input handlers
- replica setup helpers
- client-visible strings or assets

## Quick Routing

- "Why is my prefab file not loading?"
  - check `PrefabFiles`
- "Where should shared portraits, atlases, or anim zips be declared?"
  - check top-level `Assets`
- "My `modmain.lua` is too large."
  - split with `modimport("scripts/modmain/...")`
- "Why is my character not appearing correctly?"
  - check `AddModCharacter(...)`, top-level character assets, and `modinfo.lua`
- "Where should config-driven startup tweaks live?"
  - keep the glue in `modmain.lua`, then move the real behavior into prefab or component code
