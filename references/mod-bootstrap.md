# Mod Bootstrap

Use this file when `modinfo.lua` or `modmain.lua` is missing and the task looks like a new mod.

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
