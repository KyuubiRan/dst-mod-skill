# `inventory`

Use this file when the task changes active item flow, equipment access, hidden inventories, or owner-side item lookup and consumption.

Official source:

- `scripts/components/inventory.lua`

Close official prefab shapes:

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/molehill.lua`

High-frequency methods:

- `GetActiveItem()`
- `GetEquippedItem(eslot)`
- `FindItem(fn)`
- `FindItems(fn)`
- `GiveItem(inst, slot, src_pos)`
- `DropItem(item, wholestack, randomdir, pos, keepoverstacked)`
- `Equip(item, old_to_active, no_animation, force_ui_anim)`
- `Unequip(equipslot, slip, force)`
- `HasItemWithTag(tag, amount)`
- `GetItemByName(item, amount, checkallcontainers)`
- `ConsumeByName(item, amount)`
- `Open()`
- `Close(keepactiveitem)`

Common pairings:

- `inventory` + `inventoryitem`
- `inventory` + `equippable`
- player `inventory` + `container`

Common pitfalls:

- `inventory` is owner-side holding logic, not slot-widget storage UI.
- many interactions cross both `inventory` and `inventoryitem`.
- if the task is chest or backpack UI behavior, inspect `container` too.

Read next:

- `references/components/inventoryitem.md`
- `references/components/container.md`
