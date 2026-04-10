# `stackable`

Use this file when the task changes stack size, partial consumption, split behavior, or stack-aware item logic.

Official source:

- `scripts/components/stackable.lua`

Close official prefab shapes:

- `scripts/prefabs/rope.lua`
- `scripts/prefabs/crumbs.lua`

High-frequency methods:

- `IsStack()`
- `StackSize()`
- `IsFull()`
- `SetStackSize(sz)`
- `Get(num)`
- `RoomLeft()`
- `Put(item, source_pos)`
- `SetOnDeStack(fn)`

Common pairings:

- `stackable` + `inventoryitem`
- `stackable` + `edible`
- `stackable` + `fuel`

Common pitfalls:

- stack logic must handle partial removal, not just whole-item transitions.
- edible and fuel behavior may need stack-aware callbacks.
- overstack or room-left bugs are usually item-side, not inventory UI bugs.

Read next:

- `references/components/inventoryitem.md`
- `references/components/edible.md`
