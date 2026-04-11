# Recipe Patterns

Use this file when the task adds craftable content, recipe filters, crafting-station routing, character-gated recipes, or placers.

This page is for recipe registration and placement preview flow.
If the task is mainly about the structure or item prefab itself, also read `references/feature-recipes.md` and `references/patterns/creation-patterns.md`.

## Usually Involved Files

When a user says "make this craftable", the task often spans more than one registration call.

Common file set:

- `modmain.lua`
  - recipe registration
  - optional filter routing
- `prefabs/<prefab>.lua`
  - the real item or structure
  - often the `MakePlacer(...)` return too
- `strings`
  - `STRINGS.NAMES.<PREFAB>`
  - `STRINGS.RECIPE_DESC.<PREFAB>`
- inventory atlas pair if the crafted result has a custom icon
- animation assets if the crafted result is a visible structure or item

## Prefer `AddRecipe2`

Observed official mod API in `scripts/modutil.lua`:

```lua
AddRecipe2(name, ingredients, tech, config, filters)
AddRecipeToFilter(recipe_name, filter_name)
```

`AddRecipe` still exists but is explicitly deprecated in official code.

Rule:

- use `AddRecipe2` for new work
- do not start new work on deprecated tab-based recipe APIs

## Typical Recipe Flow

Common registration shape in `modmain.lua`:

```lua
AddRecipe2(
    "my_item",
    {
        Ingredient("rocks", 2),
    },
    TECH.SCIENCE_ONE,
    {
        placer = "my_structure_placer",
        min_spacing = 2,
    },
    {
        "STRUCTURES",
    }
)
```

Observed `AddRecipe2` behavior:

- creates `Recipe2(...)`
- adds the recipe to default filter routing used by official modern crafting
- then applies any extra filters you pass in

Practical consequence:

- recipe registration is usually short
- the real complexity is often in config, filters, placer wiring, and the prefab that the recipe produces

## Common `AddRecipe2` Concerns

The arguments usually answer five separate questions:

1. what prefab name is being crafted
2. what ingredients it costs
3. what tech gate or station gate applies
4. what config flags affect placement or unlock behavior
5. which crafting filters should show it

If the task is vague, classify those five things before writing code.

## Common Config Fields

The exact fields depend on the recipe shape, but these come up often:

- `placer`
  - placement preview prefab name
- `min_spacing`
  - placement spacing
- `nounlock`
  - station-style availability instead of permanent unlock
- `numtogive`
  - crafted stack count
- `builder_tag`
  - character or entity tag gate
- `builder_skill`
  - skill-tree gate
- deploy or atlas-related fields when UI or placement needs explicit metadata

Rule:

- keep recipe config focused on recipe behavior
- move gameplay logic to the prefab, component, or placement callback rather than hiding it in recipe config

## Character Recipes

For character-gated recipes, official mod API also exposes:

```lua
AddCharacterRecipe(name, ingredients, tech, config, extra_filters)
```

This routes recipes toward the `CHARACTER` filter when character-specific gating is involved.

Use it for:

- character-locked recipes
- recipes gated by `builder_tag`
- recipes gated by `builder_skill`

Rule:

- if a recipe is only craftable by one character or skill route, make that explicit in the recipe setup rather than burying it in runtime failure logic

## Filters

Use `AddRecipeToFilter(recipe_name, filter_name)` when a recipe should appear in a specific crafting filter.

Rule:

- prefer modern crafting filters
- do not rely on deprecated tab-based organization for new work
- if a recipe belongs in more than one place conceptually, use extra filter routing instead of duplicating the recipe

Typical cases:

- structure recipes
- character recipes
- custom mod categories if the user has already established them

## Recipe Strings

Most recipe tasks also need string work.

Common targets:

```lua
STRINGS.NAMES.MY_ITEM = "My Item"
STRINGS.RECIPE_DESC.MY_ITEM = "Builds a thing."
STRINGS.CHARACTERS.GENERIC.DESCRIBE.MY_ITEM = "It exists."
```

Rule:

- if the crafted result is new, expect at least `NAMES` and usually `RECIPE_DESC`
- if the crafted result is inspectable, expect `DESCRIBE` too

Also read:

- `references/patterns/string-patterns.md`

## Recipe Assets And Icons

If the crafted result needs a custom icon, the recipe task usually also touches atlas assets.

Common asset declarations:

```lua
Asset("ATLAS", "images/inventoryimages/my_item.xml")
Asset("IMAGE", "images/inventoryimages/my_item.tex")
```

Rule:

- the recipe registration is only one piece
- if the crafted item icon is missing in the crafting UI, also inspect atlas assets and texture files

Also read:

- `references/patterns/asset-patterns.md`
- `references/patterns/texture-patterns.md`

## Placers

Placeable structures commonly use a placer prefab so the player can preview placement.

Official helper signature from `scripts/prefabutil.lua`:

```lua
MakePlacer(name, bank, build, anim, onground, snap, metersnap, scale, fixedcameraoffset, facing, postinit_fn, offset, onfailedplacement)
```

Typical prefab return shape:

```lua
return Prefab("my_structure", fn, assets, prefabs),
    MakePlacer("my_structure_placer", "my_structure", "my_structure", "idle")
```

## What `MakePlacer` Does

Observed official behavior:

- returns a `Prefab(name, fn)`
- creates a non-networked preview entity
- adds tags `CLASSIFIED`, `NOCLICK`, and `placer`
- adds the `placer` component
- sets placement behavior such as grid snapping and on-ground mode
- optionally runs `postinit_fn`

Practical consequence:

- placers are usually returned from the same prefab file as the structure or deployable
- recipes reference the placer name through recipe config
- if a task is really about the preview helper rather than the final structure, also read `references/patterns/tag-patterns.md`

## Recipe To Placer To Prefab Chain

For placeable content, the normal chain is:

1. `AddRecipe2(...)` references `config.placer`
2. `prefabs/<thing>.lua` returns both the real `Prefab(...)` and `MakePlacer(...)`
3. the crafted result spawns or deploys the real prefab

If one part is missing, placement usually breaks in a predictable way:

- no placer name
  - no preview
- no `MakePlacer(...)`
  - bad or missing placement helper
- wrong prefab or asset names
  - missing art or invalid preview animation

## Intent Index

- "make this item craftable"
  - use `AddRecipe2(...)`
  - ensure `STRINGS.RECIPE_DESC` exists
- "make this structure placeable"
  - use `AddRecipe2(...)` plus `MakePlacer(...)`
- "put this recipe in a filter"
  - use `AddRecipeToFilter(...)`
- "make this recipe character-only"
  - inspect `AddCharacterRecipe(...)`, `builder_tag`, or `builder_skill`
- "the recipe exists but icon is missing"
  - inspect atlas assets and texture files
- "the recipe exists but placement preview is broken"
  - inspect `placer`, `MakePlacer(...)`, and preview animation assets

## Common Failure Points

- recipe shows up in the wrong crafting category
  - filter routing is wrong or incomplete
- recipe crafts the right prefab but placement preview is missing
  - `placer` config or `MakePlacer(...)` is missing
- structure can be crafted but not placed correctly
  - `min_spacing`, placer setup, or deployable behavior is mismatched
- crafting entry exists but icon or description is wrong
  - atlas assets or `STRINGS.RECIPE_DESC` are missing
- character-specific recipe leaks to everyone
  - the wrong helper or gating fields were used

## Rule Of Thumb

- Use `AddRecipe2` for new recipes.
- Use `AddRecipeToFilter` for explicit filter routing.
- Use `MakePlacer` for structures or deployables that need placement preview.
- Expect recipe tasks to also touch strings, assets, and often the prefab file itself.
- Keep recipe, prefab, and placer names aligned so the loading path stays obvious.
