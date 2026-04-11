# Asset Patterns

Use this file when the task adds animation zips, inventory icons, minimap images, frontend assets, or atlas references.
If the task is specifically about lighting, FX prefabs, particle FX, or sound playback logic, also read `references/patterns/effects-patterns.md`.
If the task is specifically about atlas packing, TEX/XML unpacking, or PNG resizing workflow, also read `references/patterns/texture-patterns.md`.
If the task is mostly about strings or localization, read `references/patterns/string-patterns.md` instead of bloating asset registration with text logic.

## Prefab Assets

Prefab files usually declare an `assets` table near the top:

```lua
local assets =
{
    Asset("ANIM", "anim/my_item.zip"),
    Asset("MINIMAP_IMAGE", "my_item"),
}
```

Observed common asset kinds in official prefabs:

- `Asset("ANIM", "anim/<name>.zip")`
- `Asset("MINIMAP_IMAGE", "<name>")`
- `Asset("SOUND", "sound/<name>.fsb")`

Practical rule:

- keep prefab asset paths relative to the mod root
- register only the assets the prefab actually needs

Common split:

- visual or sound asset declaration
  - belongs here
- runtime playback logic, symbol overrides, or FX spawn flow
  - belongs in the prefab, SG, or `references/patterns/effects-patterns.md`

## Mod-Level `Assets`

`modmain.lua` can also define a top-level `Assets = { ... }`.

Observed loader flow:

- the mod loader creates a default `Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)`
- this collects mod-level assets for the mod package

Practical use:

- global mod assets
- shared atlases or images not tied to one single prefab file
- shared art referenced by several prefab files

## Inventory Images And Atlases

For item icons, mods commonly rely on atlas/xml plus texture pairs.

Typical asset declarations may include:

```lua
Asset("ATLAS", "images/inventoryimages/my_item.xml")
Asset("IMAGE", "images/inventoryimages/my_item.tex")
```

When a recipe or UI element needs an icon atlas, keep the atlas path explicit.

Practical consequence:

- texture files alone are not enough
- recipe, inventory, or UI code often also needs the explicit atlas path

Texture-workflow rule:

- asset registration belongs here
- atlas generation, atlas extraction, and PNG resizing belong in `references/patterns/texture-patterns.md`

## Minimap Images

For minimap icons, prefab files often declare:

```lua
Asset("MINIMAP_IMAGE", "my_prefab")
```

The asset name should match the minimap image resource expected by the prefab.

`modutil.lua` also exposes:

```lua
AddMinimapAtlas(atlaspath)
```

Use this when a minimap atlas must be registered explicitly.

## Frontend And Preload Assets

Observed mod environment helpers from `scripts/modutil.lua`:

```lua
FrontEndAssets = { ... }
PreloadAssets = { ... }
ReloadFrontEndAssets()
ReloadPreloadAssets()
```

Use these only when the task specifically needs frontend-only or preload asset behavior.

For most gameplay prefabs, normal `assets` or mod-level `Assets` are enough.

## Loader Reality

Observed in `scripts/mods.lua`:

```lua
Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)
```

Practical consequence:

- top-level `Assets` become part of the mod's default loader prefab
- this is why shared mod assets can live in `modmain.lua` even when no single gameplay prefab owns them

## Asset And String Cross-Checks

When a feature "looks missing", check both asset and string sides:

- recipe visible but icon missing
  - likely asset or atlas wiring
- icon exists but crafted item text is blank
  - likely `STRINGS` side
- runtime locale loader works but some icon paths break
  - locale and asset registration are separate problems

## Common Failure Points

- asset file exists but was never declared
  - loader never sees it
- atlas and image paths disagree with the code that references them
  - crafting or UI icon lookup breaks
- shared asset was kept inside one prefab-local `assets` table even though several systems need it
  - move it to top-level `Assets`
- tried to solve asset issues by editing strings or locale files
  - wrong subsystem

## Rule Of Thumb

- Put prefab-local assets in that prefab file's `assets` table.
- Put shared mod assets in top-level `Assets`.
- Use atlas/image pairs for UI or inventory icon resources.
- Use `AddMinimapAtlas` only when minimap registration needs it explicitly.
- If the user asks to pack, unpack, or resize texture files, switch to `references/patterns/texture-patterns.md`.
