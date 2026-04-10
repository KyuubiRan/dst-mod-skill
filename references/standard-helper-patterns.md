# Standard Helper Patterns

Use this file when the task is mainly about choosing or applying `Make*` helper constructors from `scripts/standardcomponents.lua`.

Read `references/helper-signatures.md` for exact parameter order.
Read `references/world-system-patterns.md` when the task is mainly about component behavior rather than helper selection.

## Why This Page Exists

Many DST prefabs are not assembled only from raw components.
They also rely on helper constructors such as:

- `MakeInventoryPhysics(...)`
- `MakeInventoryFloatable(...)`
- `MakeSmallBurnable(...)`
- `MakeObstaclePhysics(...)`
- `MakeSnowCoveredPristine(...)`

The helper choice often determines tags, collision groups, animation behavior, or hidden defaults.

## Physics Helpers

Observed in `scripts/standardcomponents.lua`:

- `MakeInventoryPhysics(...)`
  - item collision group
  - sphere physics
  - collides with world, obstacles, and small obstacles
- `MakeProjectilePhysics(...)`
  - item collision group
  - ground-only collision mask
- `MakeCharacterPhysics(...)`
  - character collision group
  - capsule physics
  - collides with characters and giants too
- `MakeObstaclePhysics(...)`
  - adds `blocker`
  - static obstacle physics
- `MakeSmallObstaclePhysics(...)`
  - adds `blocker`
  - small-obstacle collision group
- `MakeHeavyObstaclePhysics(...)`
  - adds `blocker`
  - intended for heavy-liftable obstacles

Practical consequence:

- do not use item physics for a creature or structure just because both "need collision"
- obstacle helpers already add the high-frequency `blocker` tag
- `MakeHeavyObstaclePhysics(...)` is not just "stronger obstacle physics"; the official comment says to pair it with the `heavyobstaclephysics` component

Observed official examples:

- `scripts/prefabs/spear.lua`
  - `MakeInventoryPhysics(inst)`
- `scripts/prefabs/berrybush.lua`
  - `MakeSmallObstaclePhysics(inst, .1)`
- `scripts/prefabs/treasurechest.lua`
  - `MakeHeavyObstaclePhysics(inst, SUNKEN_PHYSICS_RADIUS)`

## `MakeInventoryFloatable(...)`

Observed in `scripts/standardcomponents.lua` and `scripts/components/floater.lua`:

- adds the `floater` component
- configures size, vertical offset, and scale
- optional `swap_bank` enables the special `floating_item` bank while floating
- `float_index` chooses a paused frame and side
- optional `swap_data` controls the bank, anim, and symbol restored or overridden on float

Practical consequence:

- this helper is more than "show splash FX"
- official items often call it before `SetPristine()` because the floater owns client-visible behavior too
- if an item needs a special floating symbol or a different default bank on return, inspect `swap_data`

Observed official examples:

- `scripts/prefabs/spear.lua`
  - `MakeInventoryFloatable(inst, "med", 0.05, {1.1, 0.5, 1.1}, true, -9)`
- `scripts/prefabs/backpack.lua`
  - `MakeInventoryFloatable(inst, "small", 0.2, nil, nil, nil, swap_data)`

Good rule:

- use plain size and offset for ordinary icons or pickups
- use `swap_data` when the prefab needs a specific bank or symbol when returning from float mode

## Burnable And Propagator Helpers

Observed in `scripts/standardcomponents.lua`:

- burnable helpers add the component, burn FX level, burn time, and default ignite/extinguish/burnt callbacks
- propagator helpers add heat acceptance, flash point handling, and default propagation numbers

Practical consequence:

- if the goal is a normal burnable item or structure, start with the helper instead of rebuilding the whole burn callback chain
- structure burn behavior differs from loose-item burn behavior through the `structure` argument

Observed official examples:

- `scripts/prefabs/backpack.lua`
  - `MakeSmallBurnable(inst)`
  - `MakeSmallPropagator(inst)`
- `scripts/prefabs/berrybush.lua`
  - `MakeLargeBurnable(inst)`
  - `MakeMediumPropagator(inst)`

## Snow And Seasonal Helpers

Observed in `scripts/standardcomponents.lua`:

- `MakeSnowCoveredPristine(...)`
  - overrides the `snow` symbol
  - adds the `SnowCovered` tag
  - hides the snow layer
- `MakeSnowCovered(...)`
  - shows or hides the snow layer from world state
  - may also attach lunar-hail buildup handling on networked master-sim prefabs
- `MakeNoGrowInWinter(...)`
  - watches `iswinter`
  - expects the prefab to already have `pickable`

Practical consequence:

- `MakeSnowCoveredPristine(...)` and `MakeSnowCovered(...)` are usually a pair
- call the pristine helper before `SetPristine()` when the snow symbol must exist on clients
- only call `MakeNoGrowInWinter(...)` after the `pickable` component exists

Observed official example:

- `scripts/prefabs/berrybush.lua`
  - `MakeSnowCoveredPristine(inst)` before `SetPristine()`
  - `MakeSnowCovered(inst)` and `MakeNoGrowInWinter(inst)` later on the master path

## Hauntable Helper Reality

Observed in the current `scripts/standardcomponents.lua`:

- `MakeHauntableLaunch(...)` actively launches the item
- `MakeHauntableLaunchAndDropFirstItem(...)` is used broadly on containers
- `MakeHauntableWork(...)` contains `#HAUNTFIX` commented logic and currently returns `false`
- `MakeHauntableIgnite(...)` contains `#HAUNTFIX` commented logic and currently returns `false`

Practical consequence:

- do not assume every haunt helper family member is equally "live"
- launch-style helpers are stable references
- work or ignite helpers must be verified against the current official source and the target prefab
- if the desired ghost interaction must definitely work, inspect whether the prefab also adds a custom haunt reaction or custom `hauntable` callback

Observed official examples:

- `scripts/prefabs/backpack.lua`
  - `MakeHauntableLaunchAndDropFirstItem(inst)`
- `scripts/prefabs/berrybush.lua`
  - `MakeHauntableIgnite(inst)`
  - plus `AddHauntableCustomReaction(inst, OnHaunt, false, false, true)`

## Quick Router

- "this is a loose inventory item"
  - start with `MakeInventoryPhysics(...)`
- "this should float in the ocean"
  - add `MakeInventoryFloatable(...)`
- "this blocks movement in the world"
  - choose obstacle or heavy-obstacle physics, not inventory physics
- "this should burn normally"
  - start with a burnable helper plus the matching propagator helper
- "this should react to ghosts"
  - verify the exact haunt helper instead of assuming the name is enough
- "this should show snow or stop growing in winter"
  - use the snow or seasonal helpers at the same lifecycle stage as official prefabs
