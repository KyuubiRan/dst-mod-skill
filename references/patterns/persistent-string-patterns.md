# Persistent String Patterns

Use this file when the task needs `TheSim:SetPersistentString(...)`, `TheSim:GetPersistentString(...)`, or cross-save local storage that is not tied to one entity or one world save.

This page is about `TheSim`-level persistent files.
If the task is ordinary entity or world save lifecycle, read `references/patterns/persistence-patterns.md` instead.
If the task is user-facing host config in the mod configuration screen, read `references/patterns/modinfo-patterns.md` instead.
If the task is mainly about `pcall(...)` or `xpcall(...)` around decode or encode boundaries, also read `references/patterns/protected-call-patterns.md`.

## What This Storage Is For

Use plain persistent strings when the data should survive switching worlds or save slots and is owned by the local process rather than one saved entity.

Observed official fits:

- local UI or profile settings
- cookbook, plant registry, and skill-tree profile data
- frontend caches such as MOTD or countdown data
- local statistics or small mod-owned cache files

## What This Storage Is Not For

Do not use plain persistent strings for:

- one prefab's ordinary save state
- cross-entity reference repair
- offline world progression through `LongUpdate(dt)`
- host-visible `modinfo.lua` configuration options

For those cases:

- entity or world save lifecycle
  - `references/patterns/persistence-patterns.md`
- host config screen
  - `references/patterns/modinfo-patterns.md`
- shard or slot scoped files
  - `references/patterns/shard-patterns.md`

## Observed Core API

Observed official usage shapes:

```lua
TheSim:SetPersistentString(name, data, encode, callback)
TheSim:GetPersistentString(name, callback)
TheSim:ErasePersistentString(name, callback)
TheSim:CheckPersistentStringExists(name, callback)
```

Observed callback shapes:

- `GetPersistentString(name, function(success, data) ... end)`
- `SetPersistentString(name, data, encode, function(success) ... end)`
- `ErasePersistentString(name, function(success) ... end)`
- `CheckPersistentStringExists(name, function(exists) ... end)`

Practical rule:

- treat these as asynchronous callback APIs
- do not expect `GetPersistentString(...)` to return the loaded value immediately

## What To Store

The stored payload is a string.
Official code usually serializes a Lua table first, then writes the resulting string.

Observed official serialization choices:

- `json.encode(...)`
  - `scripts/craftingmenuprofile.lua`
  - `scripts/skilltreedata.lua`
  - `scripts/generickv.lua`
- `DataDumper(...)`
  - `scripts/plantregistrydata.lua`
  - `scripts/util/savedata.lua`

Practical rule:

- prefer `json.encode/decode` for ordinary mod settings and cache tables
- for mod-local config saved through `TheSim:SetPersistentString(...)`, treat JSON as the default storage format unless the task explicitly requires another official format
- use `DataDumper` only when the data already matches that official Lua-chunk style and the loader intentionally uses `RunInSandbox(...)`
- protect decode or encode boundaries with `pcall(...)` or `xpcall(...)` when malformed data is plausible

## The `encode` Argument

Observed official patterns:

- profile, cache, and settings style files often pass `false`
- save-wrapper code such as `scripts/util/savedata.lua` may pass `ENCODE_SAVES`

Practical rule:

- for mod-owned local settings or cache, start with `false`
- only use encoded save-style output when you intentionally want the official save-file path behavior

## `SavePersistentString(...)` Wrapper

Observed in `scripts/mainfunctions.lua`:

- global `SavePersistentString(name, data, encode, callback)` wraps `TheSim:SetPersistentString(...)`
- if `TheFrontEnd` exists, it shows and hides the saving indicator around the write

Practical consequence:

- this wrapper is about frontend save indicator behavior
- it does not change the storage model
- it does not preserve the raw `success` argument the way direct `TheSim:SetPersistentString(...)` callbacks do

Official modules still commonly call `TheSim:SetPersistentString(...)` directly.

## Naming And Scope

Treat `name` like a small file key.

Good practice for mods:

- prefix keys with a stable mod-owned namespace
- keep the file small and focused
- add a schema version inside the stored table when future migration is likely

Good examples:

- `my_mod_local_settings`
- `my_mod_cache_v1`
- `my_mod_seen_tutorials`

Avoid generic names such as:

- `settings`
- `data`
- `profile`

## Client, Server, And Save-Slot Scope

Plain `TheSim:GetPersistentString(...)` and `SetPersistentString(...)` are process-local persistent storage calls.

Practical consequence:

- on a local client, this is local machine data
- on a dedicated server, this is server-side local data
- this is not automatically tied to one world save slot or one shard

If the task really belongs to a cluster slot or shard file, official code also uses:

- `TheSim:GetPersistentStringInClusterSlot(...)`
- `TheSim:SetPersistentStringInClusterSlot(...)`

Do not default to those cluster-slot variants for ordinary local mod preferences.

## Recommended Mod Pattern

Use this shape for mod-owned cross-save local settings.
This is also the default pattern for local mod config stored through `TheSim:SetPersistentString(...)`:

```lua
local SETTINGS_KEY = "my_mod_local_settings"

local settings =
{
    version = 1,
    enabled = true,
    hotkey = 122,
}

local function SaveSettings()
    TheSim:SetPersistentString(SETTINGS_KEY, json.encode(settings), false)
end

local function LoadSettings(on_done)
    TheSim:GetPersistentString(SETTINGS_KEY, function(success, data)
        if success and data ~= nil and data ~= "" then
            local ok, decoded = pcall(json.decode, data)
            if ok and type(decoded) == "table" then
                settings = decoded
            end
        end

        if on_done ~= nil then
            on_done(settings)
        end
    end)
end
```

Good traits:

- stable namespaced key
- explicit version field
- callback-based load flow
- tolerant decode failure handling

For the Lua protected-call side of this pattern, also read `references/patterns/protected-call-patterns.md`.

## Official Example Router

- `scripts/craftingmenuprofile.lua`
  - local crafting UI preferences with JSON
- `scripts/plantregistrydata.lua`
  - larger local registry data with `DataDumper(...)`
- `scripts/skilltreedata.lua`
  - local profile progression data
- `scripts/generickv.lua`
  - simple key-value storage wrapper
- `scripts/util/savedata.lua`
  - reusable save-file wrapper with dirty flag and erase support
- `scripts/mainfunctions.lua`
  - `SavePersistentString(...)` and `ErasePersistentString(...)` wrappers

## Common Failure Points

- expected `GetPersistentString(...)` to return data synchronously
- wrote a Lua table directly instead of serializing to string first
- used plain persistent strings for world-owned entity state
- used a generic file key that may collide later
- forgot decode failure handling for old or bad data
- stored authoritative gameplay state in a local client file and expected all players to share it

## Rule Of Thumb

- world or entity save state
  - use `OnSave(...)`, `OnLoad(...)`, `OnLoadPostPass(...)`, or `LongUpdate(dt)`
- host config visible in mod settings
  - use `modinfo.lua`
- local mod preferences, cache, or cross-save profile data
  - use `TheSim:SetPersistentString(...)` and `GetPersistentString(...)`
