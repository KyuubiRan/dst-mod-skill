# Skin Patterns

Use this file when the task is specifically about the official skin data system:

- `PREFAB_SKINS`
- `CreatePrefabSkin(...)`
- wardrobe or loadout skin selection
- character base skins beyond normal portraits and preview modes

Do not use this file for ordinary mod art variants.
If the task is only "swap to another build", "make a powered-up form", or "add several look variants with the same gameplay", prefer:

- `references/animstate-patterns.md`
- `references/creation-patterns.md`
- `references/template-patterns.md`

## Two Different Problems

Keep these separate:

- preview modes for a mod character
  - `AddModCharacter(name, gender, modes)`
- real official skin data and wardrobe ownership flow
  - `PREFAB_SKINS`, `CreatePrefabSkin(...)`, `TheInventory:CheckOwnership(...)`

A mod character can use preview modes without using the full official skin inventory system.

## Official Files To Read First

- `scripts/prefabskin.lua`
  - defines `CreatePrefabSkin(...)`
- `scripts/prefabskins.lua`
  - generated `PREFAB_SKINS` and `PREFAB_SKINS_IDS`
- `scripts/prefabs/skinprefabs.lua`
  - generated skin prefab data
- `scripts/skinsutils.lua`
  - `GetSkinData(...)`, `GetBuildForItem(...)`, `GetPortraitNameForItem(...)`, `GetSkinModes(...)`
- `scripts/widgets/redux/loadoutselect.lua`
  - preview-mode routing and base-skin UI behavior
- `scripts/screens/redux/defaultskinselection.lua`
  - ownership-gated skin list building

## Loader Reality

Observed official flow:

- `scripts/mods.lua`
  - loads `modmain.lua` before it registers the mod's `PrefabFiles`
- `scripts/mainfunctions.lua`
  - loads each prefab file through `LoadPrefabFile(...)`
- `scripts/prefabs.lua`
  - when `Prefab(name, ...)` is constructed, appends any names from `PREFAB_SKINS[name]` into that prefab's dependency list
- `scripts/skinsutils.lua`
  - `GetAllItemCategories()` starts with `Prefabs`, so loaded skin prefabs become discoverable through `GetSkinData(...)`

Practical consequence:

- there is no dedicated `PrefabSkinFiles` mod hook
- mod skin prefabs still come through ordinary `PrefabFiles`
- if a mod wants custom skin metadata, populate `PREFAB_SKINS.<base_prefab>` before the base prefab file is loaded, usually in `modmain.lua`

## Mod Character Limitation You Must Remember

Observed in `scripts/widgets/redux/loadoutselect.lua`:

- `self.have_base_option = table.contains(DST_CHARACTERLIST, self.currentcharacter)`
- mod characters therefore do not get the normal base-skin selector by default

Observed in `scripts/screens/redux/defaultskinselection.lua`:

- skin choices are filtered by `TheInventory:CheckOwnership(item_type)`

Practical consequence:

- do not promise Klei-style wardrobe-selectable base skins for a mod character unless you are also patching the UI and the ownership assumptions
- for most mod characters, preview modes plus normal portrait and asset wiring are the stable path

## Character Base Skin Data Shape

Official character skin entries such as `wormwood_none`, `wormwood_victorian`, `wurt_none`, and `wurt_victorian` use `CreatePrefabSkin(...)` with `type = "base"`.

High-frequency fields:

- `base_prefab`
- `type = "base"`
- `skin_tags`
- `build_name_override` on the default `_none` skin when needed
- `skins = { normal_skin = ..., ghost_skin = ..., extra_mode = ... }`

Observed official examples:

- `wormwood_none`
  - maps `stage_2`, `stage_3`, and `stage_4`
- `wurt_none`
  - maps `powerup`

Practical consequence:

- the `skins` keys are the bridge between base skin data and preview modes
- the default character base skin is usually named `<character>_none`
- if you add custom preview modes such as `powerup` or `young_skin`, each real base skin should provide matching `skins.<mode_key>` entries

## Advanced Mod-Owned Data Pattern

Use this only when the task really needs official-style skin metadata.
This is not the default path for a first playable-character mod.

`modmain.lua`:

```lua
PrefabFiles = {
    "mychar",
    "mychar_skinprefabs",
}

PREFAB_SKINS.mychar = {
    "mychar_none",
    "mychar_formal",
}
```

`prefabs/mychar_skinprefabs.lua`:

```lua
local prefs = {
    CreatePrefabSkin("mychar_none", {
        base_prefab = "mychar",
        type = "base",
        build_name_override = "mychar",
        skin_tags = { "BASE", "CHARACTER", "MYCHAR" },
        skins = {
            normal_skin = "mychar",
            ghost_skin = "ghost_mychar_build",
            powerup = "mychar_powerup",
        },
    }),
    CreatePrefabSkin("mychar_formal", {
        base_prefab = "mychar",
        type = "base",
        skin_tags = { "BASE", "MYCHAR", "FORMAL" },
        skins = {
            normal_skin = "mychar_formal",
            ghost_skin = "ghost_mychar_formal",
            powerup = "mychar_formal_powerup",
        },
    }),
}

return unpack(prefs)
```

Important note:

- this only registers skin metadata
- it does not grant ownership, add wardrobe UI, or unlock selection flow by itself
- declare the real anim zips and portrait assets separately through normal prefab or mod `Assets`

## Do Not Cargo-Cult The Whole Generated Table

Official generated skin data also carries deeper fields such as geometry hints, clothing-body metadata, beard links, sounds, or FX hooks.

Practical rule:

- only copy advanced fields after reading the matching official character or item example
- if the task is still just "multiple looks for one mod character", stop and use preview modes or normal runtime `AnimState` logic instead

## Quick Router

- "I want a mod character with alternate preview poses or forms in the loadout UI."
  - stay in `references/character-patterns.md`
- "I want full official-style character skin data or wardrobe base-skin behavior."
  - read this file and treat it as an advanced UI-plus-data problem
- "I only need several art variants with shared gameplay."
  - use factory-prefab or normal `AnimState` patterns instead of the skin system
