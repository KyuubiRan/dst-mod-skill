# `pickable`

Use this file when the task changes harvesting, regrowth, barren state, or fertilize flow on a world node.

Official source:

- `scripts/components/pickable.lua`

Close official prefab shapes:

- `scripts/prefabs/berrybush.lua`

High-frequency methods:

- `SetUp(product, regen, number)`
- `SetOnPickedFn(fn)`
- `SetOnRegenFn(fn)`
- `SetMakeBarrenFn(fn)`
- `SetMakeEmptyFn(fn)`
- `CanBeFertilized()`
- `Fertilize(fertilizer, doer)`
- `CanBePicked()`
- `Regen()`
- `MakeBarren()`
- `MakeEmpty()`
- `Pick(picker)`

Common pairings:

- `pickable` + `inspectable`
- `pickable` + `workable`

Common pitfalls:

- `pickable` is for world harvestables, not loose inventory items.
- many harvestables also use `workable` for dig-up or destruction behavior.
- regrowth bugs often involve save, load, or `LongUpdate(...)`, not only `Pick(...)`.

Read next:

- `references/components/workable.md`
- `references/persistence-patterns.md`
