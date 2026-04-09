# Recipe Patterns

Use this file when the task adds craftable content, recipe filters, crafting station routing, or placers.

## Prefer `AddRecipe2`

Observed official mod API in `scripts/modutil.lua`:

```lua
AddRecipe2(name, ingredients, tech, config, filters)
AddRecipeToFilter(recipe_name, filter_name)
```

`AddRecipe` still exists but is explicitly deprecated in official code.

## Typical Recipe Flow

Common registration shape in `modmain.lua`:

```lua
AddRecipe2(
    "my_item",
    { Ingredient("rocks", 2) },
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
- automatically adds the recipe to the `MODS` filter in common cases
- or to `CRAFTING_STATION` when `config.nounlock` applies
- then adds any extra filters you pass in

## Character Recipes

For character-gated recipes, official mod API also exposes:

```lua
AddCharacterRecipe(name, ingredients, tech, config, extra_filters)
```

This routes recipes toward the `CHARACTER` filter when `builder_tag` or `builder_skill` is present.

## Filters

Use `AddRecipeToFilter(recipe_name, filter_name)` when a recipe should appear in a specific crafting filter.

Practical rule:

- prefer modern crafting filters
- do not rely on deprecated tab-based recipe organization for new work

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
- adds the `placer` component
- sets placement behavior such as grid snapping and on-ground mode
- optionally runs `postinit_fn`

Practical consequence:

- placers are usually returned from the same prefab file as the deployable structure
- recipes reference the placer name through recipe config

## Rule Of Thumb

- Use `AddRecipe2` for new recipes.
- Use `AddRecipeToFilter` to place the recipe in the intended crafting filter.
- Use `MakePlacer` for structures or deployables that need placement preview.
- Keep the recipe, prefab, and placer names aligned so the loading path stays obvious.
