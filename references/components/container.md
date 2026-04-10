# `container`

Use this file when the task changes slot count, widget setup, open or close flow, acceptance filters, or storage-side item removal.

Official source:

- `scripts/components/container.lua`

Close official prefab shapes:

- `scripts/prefabs/backpack.lua`
- `scripts/prefabs/treasurechest.lua`

High-frequency methods:

- `WidgetSetup(prefab, data)`
- `GetWidget()`
- `SetNumSlots(numslots)`
- `CanTakeItemInSlot(item, slot)`
- `GiveItem(item, slot, src_pos, drop_on_fail)`
- `RemoveItemBySlot(slot, keepoverstacked)`
- `RemoveAllItems()`
- `GetItemInSlot(slot)`
- `GetAllItems()`
- `Open(doer)`
- `Close(doer)`
- `IsOpen()`
- `CanOpen()`
- `FindItem(fn)`
- `HasItemWithTag(tag, amount)`
- `DestroyContents(onpredestroyitemcallbackfn)`

Common pairings:

- `container` + `inventoryitem`
- `container` + `equippable`
- `container` + `workable`

Common pitfalls:

- widget layout data must match the real slot behavior.
- many open or close bugs are replica or UI expectation bugs, not only server container logic.
- item acceptance issues often come from `CanTakeItemInSlot(...)` or widget mismatch.

Read next:

- `references/ui-patterns.md`
- `references/player-network-patterns.md`
