# `fuel`

Use this file when the task changes the consumed fuel item, not the fueled target.

Official source:

- `scripts/components/fuel.lua`

Close official prefab shapes:

- `scripts/prefabs/rope.lua`
- `scripts/prefabs/cattoy_mouse.lua`

High-frequency methods:

- `SetOnTakenFn(fn)`
- `Taken(target)`

Common pairings:

- `fuel` + `inventoryitem`
- `fuel` + `stackable`

Common pitfalls:

- `fuel` is the item being consumed.
- if the task is about fuel level on a machine or fire source, inspect the target's `fueled` component instead.

Read next:

- `references/patterns/world-system-patterns.md`
- `references/components/inventoryitem.md`
