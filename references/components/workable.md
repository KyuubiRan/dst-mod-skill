# `workable`

Use this file when the task changes hammer, mine, chop, dig, or other target-side work progress and finish callbacks.

Official source:

- `scripts/components/workable.lua`

Close official prefab shapes:

- `scripts/prefabs/treasurechest.lua`
- `scripts/prefabs/berrybush.lua`

High-frequency methods:

- `SetRequiresToughWork(tough)`
- `SetWorkAction(act)`
- `GetWorkAction()`
- `SetWorkable(able)`
- `SetWorkLeft(work)`
- `GetWorkLeft()`
- `CanBeWorked()`
- `SetMaxWork(work)`
- `WorkedBy(worker, numworks)`
- `SetOnWorkCallback(fn)`
- `SetOnFinishCallback(fn)`

Common pairings:

- `workable` + `lootdropper`
- `workable` + `pickable`
- `workable` + `tool`

Common pitfalls:

- `workable` is target-side; the acting item usually needs `tool`.
- many destroy flows also need loot, burn, or structure cleanup.
- if finish behavior seems wrong after load, inspect save or load callbacks too.

Read next:

- `references/components/tool.md`
- `references/patterns/world-system-patterns.md`
