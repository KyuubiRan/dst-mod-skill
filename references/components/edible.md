# `edible`

Use this file when the task changes hunger, health, sanity food values, on-eat side effects, or special eater-based overrides.

Official source:

- `scripts/components/edible.lua`

Close official prefab shapes:

- `scripts/prefabs/berries.lua`
- `scripts/prefabs/crumbs.lua`

High-frequency methods:

- `GetSanity(eater)`
- `GetHunger(eater)`
- `GetHealth(eater)`
- `SetOnEatenFn(fn)`
- `SetHandleRemoveFn(fn)`
- `SetOverrideStackMultiplierFn(fn)`
- `SetGetHealthFn(fn)`
- `SetGetSanityFn(fn)`
- `OnEaten(eater)`
- `GetStackMultiplier()`

Common pairings:

- `edible` + `inventoryitem`
- `edible` + `stackable`
- `edible` + `cookable`

Common pitfalls:

- `edible` means eatable behavior, not cooking transformation.
- stackable food may need override stack consumption behavior.
- final result still depends on eater-side systems.

Read next:

- `references/components/cookable.md`
- `references/components/stackable.md`
