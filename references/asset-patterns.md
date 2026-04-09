# Asset Patterns

Use this file when the task adds animation zips, inventory icons, minimap images, frontend assets, or atlas references.

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

## Mod-Level `Assets`

`modmain.lua` can also define a top-level `Assets = { ... }`.

Observed loader flow:

- the mod loader creates a default `Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)`
- this collects mod-level assets for the mod package

Practical use:

- global mod assets
- shared atlases or images not tied to one single prefab file

## Inventory Images And Atlases

For item icons, mods commonly rely on atlas/xml plus texture pairs.

Typical asset declarations may include:

```lua
Asset("ATLAS", "images/inventoryimages/my_item.xml")
Asset("IMAGE", "images/inventoryimages/my_item.tex")
```

When a recipe or UI element needs an icon atlas, keep the atlas path explicit.

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

## Rule Of Thumb

- Put prefab-local assets in that prefab file's `assets` table.
- Put shared mod assets in top-level `Assets`.
- Use atlas/image pairs for UI or inventory icon resources.
- Use `AddMinimapAtlas` only when minimap registration needs it explicitly.
