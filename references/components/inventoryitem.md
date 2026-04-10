# `inventoryitem`

Use this file when the task changes pickup, drop, owner transitions, inventory-slot presence, or icon override behavior.

Official source:

- `scripts/components/inventoryitem.lua`

Close official prefab shapes:

- `scripts/prefabs/rope.lua`
- `scripts/prefabs/spear.lua`

High-frequency methods:

- `SetOwner(owner)`
- `SetOnDroppedFn(fn)`
- `SetOnActiveItemFn(fn)`
- `SetOnPickupFn(fn)`
- `SetOnPutInInventoryFn(fn)`
- `OnPutInInventory(owner)`
- `OnDropped(randomdir, speedmult)`
- `OnPickup(pickupguy, src_pos)`
- `IsHeld()`
- `IsHeldBy(guy)`
- `RemoveFromOwner(wholestack, keepoverstacked)`
- `ChangeImageName(newname)`

Common pairings:

- `inventoryitem` + `inspectable`
- `inventoryitem` + `stackable`
- `inventoryitem` + `equippable`
- `inventoryitem` + `edible`, `fuel`, `finiteuses`, or `weapon`

Common pitfalls:

- `inventoryitem` belongs on the item entity, not the owner's whole inventory system.
- held and dropped behavior often needs both the owner-side `inventory` and the item-side `inventoryitem`.
- if an item cannot enter containers, inspect container-side filters too.

Read next:

- `references/components/inventory.md`
- `references/components/container.md`
