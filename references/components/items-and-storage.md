# Item And Storage Components

Use this file for item-side, inventory-side, storage-side, and consumable-side components:
`inspectable`, `inventoryitem`, `stackable`, `finiteuses`, `inventory`, `container`, `edible`, `cookable`, `fuel`, `tool`.

## `inspectable`

Official file:

- `scripts/components/inspectable.lua`

High-frequency methods:

- `SetDescription(desc)`
- `SetNameOverride(nameoverride)`
- `GetStatus(viewer)`
- `GetDescription(viewer)`

Use it for:

- normal inspect text
- special inspect strings or status routing
- name overrides for shared prefab logic
- cases where a prefab intentionally should not expose normal inspect behavior

Common pitfalls:

- `inspectable` is so common on player-facing prefabs that its presence is rarely the interesting design choice
- many inspect issues are actually wrong `STRINGS` keys or wrong prefab naming
- custom inspect text often also needs `references/string-patterns.md`

## `inventoryitem`

Official file:

- `scripts/components/inventoryitem.lua`

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

Use it for:

- making something a real inventory item
- pickup, drop, and owner transitions
- inventory icon image overrides
- item behavior that depends on being held or dropped

Common pitfalls:

- `inventoryitem` is for the item entity itself, not the owner's whole inventory
- items that should be equippable or usable often need other components too
- if an item cannot enter containers, also inspect `cangoincontainer` and container rules

## `stackable`

Official file:

- `scripts/components/stackable.lua`

High-frequency methods:

- `IsStack()`
- `StackSize()`
- `IsFull()`
- `SetStackSize(sz)`
- `Get(num)`
- `RoomLeft()`
- `Put(item, source_pos)`
- `SetOnDeStack(fn)`

Use it for:

- consumable materials
- food stacks
- ammo or throwable stacks

Common pitfalls:

- stack behavior usually assumes the item is also an `inventoryitem`
- some item logic must handle partial stack removal, not just whole-item removal
- edible or fuel logic may need stack-aware behavior

## `finiteuses`

Official file:

- `scripts/components/finiteuses.lua`

High-frequency methods:

- `SetConsumption(action, uses)`
- `SetMaxUses(val)`
- `SetUses(val)`
- `GetUses()`
- `Use(num)`
- `GetPercent()`
- `SetPercent(amount)`
- `SetOnFinished(fn)`
- `Repair(repairvalue)`
- `SetIgnoreCombatDurabilityLoss(value)`

Use it for:

- tool durability
- weapon durability
- limited-use utility items
- only when the prefab should actually lose uses over time

Common pitfalls:

- `finiteuses` is use-count durability, not armor condition and not fuel burn time
- combat loss and action loss can be configured separately
- zero-use behavior belongs in `SetOnFinished(...)`
- a weapon or tool does not automatically need `finiteuses`

Observed official counterexamples:

- `hambat`
  - weapon behavior without `finiteuses`
- `lucy`
  - `weapon` + `tool` behavior without `finiteuses`

## `inventory`

Official file:

- `scripts/components/inventory.lua`

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

Use it for:

- player inventory behavior
- follower or boss hidden inventories
- equipment access and active-item flow

Common pitfalls:

- `inventory` is not the same thing as `container`
- many item interactions go through both the owner's `inventory` and the item's `inventoryitem`
- if the task is UI-facing storage, inspect `container` too

## `container`

Official file:

- `scripts/components/container.lua`

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
- `FindItems(fn)`
- `HasItemWithTag(tag, amount)`
- `DestroyContents(onpredestroyitemcallbackfn)`

Use it for:

- backpack, chest, fridge, bundle, portable container, and side-widget inventory logic
- slot count and widget configuration
- insert, remove, filter, and open or close behavior

Common pitfalls:

- `WidgetSetup(...)` and UI layout assumptions must match the actual widget config
- open or close behavior can involve tags, state, or replica-side UI expectations
- item acceptance issues are often caused by `CanTakeItemInSlot(...)` or widget data mismatches

## `edible`

Official file:

- `scripts/components/edible.lua`

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

Use it for:

- food effects
- non-food oddities that are still edible in gameplay terms
- custom on-eaten behavior

Common pitfalls:

- `edible` only means "can be eaten", not "can be cooked"
- if stackable food has special behavior, account for stack consumption
- final eater behavior also depends on eater-side systems

## `cookable`

Official file:

- `scripts/components/cookable.lua`

High-frequency methods:

- `SetOnCookedFn(fn)`
- `Cook(cooker, chef)`

Use it for:

- raw ingredients that transform into a cooked prefab
- special cook-time callbacks

Common pitfalls:

- `cookable` is about transformation, not nutrition values by itself
- cooked output still needs its own prefab setup, often including `edible`, `inventoryitem`, and `inspectable`

## `fuel`

Official file:

- `scripts/components/fuel.lua`

High-frequency methods:

- `SetOnTakenFn(fn)`
- `Taken(target)`

Use it for:

- items that can be consumed as fuel by another target
- fuel-side callbacks when the target takes the fuel item

Common pitfalls:

- `fuel` is the item being consumed, not the fueled target
- if the task is about burn time or fuel level on a structure, inspect the target's `fueled` component instead

## `tool`

Official file:

- `scripts/components/tool.lua`

High-frequency methods:

- `EnableToughWork(tough)`
- `CanDoToughWork()`
- `GetEffectiveness(action)`
- `SetAction(action, effectiveness)`
- `CanDoAction(action)`

Use it for:

- worker-side harvesting or destruction actions such as chop, mine, hammer, dig, or net-like collection
- tools that need different effectiveness per action type

Common pitfalls:

- `tool` belongs on the acting item
- `workable` belongs on the target being worked
- action flow also depends on `ACTIONS`, component actions, and target-side setup
