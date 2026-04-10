# `cookable`

Use this file when the task changes raw-to-cooked prefab transformation or adds cook-time callbacks.

Official source:

- `scripts/components/cookable.lua`

Close official prefab shapes:

- `scripts/prefabs/berries.lua`

High-frequency methods:

- `SetOnCookedFn(fn)`
- `Cook(cooker, chef)`

Common pairings:

- `cookable` + `inventoryitem`
- `cookable` + `edible`

Common pitfalls:

- `cookable` is transformation logic, not nutrition by itself.
- the cooked output prefab still needs its own full setup.

Read next:

- `references/components/edible.md`
- `references/creation-patterns.md`
