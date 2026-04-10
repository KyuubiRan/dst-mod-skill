# Mod Bootstrap

Use this file when `modinfo.lua` or `modmain.lua` is missing and the task looks like a new mod.
Read `references/modinfo-patterns.md` too when the scaffold should include dependencies or non-trivial `configuration_options`.

## When To Offer Scaffolding

Offer to scaffold a mod when:

- The target folder has no `modinfo.lua`
- The target folder has no `modmain.lua`
- The user describes a new mod idea rather than an edit to an existing mod

If `modinfo.lua` already exists, do not jump straight to scaffolding.
Read the existing flags first and infer whether the mod is client-only, server-only, or all-clients gameplay.

## What To Ask First

Ask only the minimum blocking questions:

1. If `modinfo.lua` is missing, what type of mod is this:
   - all-clients gameplay
   - client-only
   - server-only
2. What display name should appear in `modinfo.lua`?
3. What short description should it use?
4. Should the scaffold include configuration options?

Ask for author or version only if the user cares or if the task explicitly requests them.

If `modinfo.lua` exists but the flags are incomplete or contradictory, ask only the missing classification question instead of re-asking everything.

## What To Generate

At minimum:

- `modinfo.lua`
- `modmain.lua`

Optional later additions:

- prefab folders
- images or icons
- configuration option entries
- helper directories for `scripts/`, `widgets/`, `stategraphs/`, or `prefabs/`

## Minimal File Families By Mod Shape

- client-only UI or QoL mod
  - `modinfo.lua`
  - `modmain.lua`
  - optional `scripts/` for widgets, screens, or helpers
- server-only world or automation mod
  - `modinfo.lua`
  - `modmain.lua`
  - optional `modworldgenmain.lua` or `modservercreationmain.lua` if it touches presets, rooms, tasks, or start locations
- all-clients gameplay/content mod
  - `modinfo.lua`
  - `modmain.lua`
  - often `prefabs/`
  - optional `scripts/components/`, `scripts/replicas/`, `scripts/widgets/`, `scripts/stategraphs/`, `scripts/brains/`

Practical rule:

- do not create `modworldgenmain.lua` by habit
- add it only when the feature really belongs to worldgen or host setup flow

## Recommended Defaults

- `api_version = 10`
- `dst_compatible = true`
- Version string like `0.1.0`
- Empty `PrefabFiles` and `Assets` lists
- `modmain.lua` with `GLOBAL` environment passthrough and a clean server/client split

## Use The Scaffold Script

Use `scripts/init_dst_mod.py` when the user wants deterministic bootstrap output.

Example:

```bash
python scripts/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

Add `--with-config` if the user wants starter `configuration_options`.

## After Scaffolding

The next file depends on the first real feature:

- entry-point layout, `PrefabFiles`, `Assets`, or `modimport(...)`
  - read `references/modmain-patterns.md`
- item, creature, structure, or FX prefab
  - read `references/template-patterns.md`
- metadata, dependencies, or key config
  - read `references/modinfo-patterns.md`
- worldgen or presets
  - read `references/worldgen-patterns.md`
- runtime strings or locale loader
  - read `references/string-patterns.md`
  - then `references/runtime-i18n-patterns.md` if needed

## Common Failure Points

- scaffolded the wrong mod shape
  - fix `client_only_mod` and `all_clients_require_mod` first
- generated worldgen files for an ordinary runtime mod
  - unnecessary file surface makes routing worse
- started writing prefabs before `PrefabFiles` exists in `modmain.lua`
  - registration path breaks later
- kept too much real gameplay logic at the top level of `modmain.lua`
  - move instance behavior back into prefab, component, brain, SG, or post-init code
