# High-Frequency Component Patterns

Use this file when a task is primarily about common official components rather than a whole subsystem.

If the task also depends on prefab tags or action/query routing, read `references/tag-patterns.md` too.
If the task also depends on lighting, FX prefabs, or sound playback, read `references/effects-patterns.md` too.

This page is a routing guide for the most frequently touched components in DST modding:

- item basics
  - `inspectable`
  - `inventoryitem`
  - `stackable`
  - `finiteuses`
- storage and holding
  - `inventory`
  - `container`
- item behavior
  - `edible`
  - `cookable`
  - `fuel`
  - `tool`
- world interaction
  - `pickable`
  - `workable`
  - `timer`
  - `talker`
- survival
  - `health`
  - `hunger`
  - `sanity`
- combat
  - `combat`
  - `weapon`
  - `armor`
  - `equippable`

Read exact signatures from the official component files before editing behavior.

Important framing:

- these bundles are common patterns, not mandatory checklists
- start from the smallest component set that matches the intended behavior
- add a component only when the prefab truly needs the capability that component provides
- if the request includes a negative constraint such as "infinite durability" or "non-inspectable", remove the default component you would otherwise expect

## When This Page Is Worth Reading

Read this page first when the user asks for things like:

- health gain, damage, invincibility, max HP, death flow
- hunger drain, starvation, food-style consumption behavior
- sanity gain or loss, lunacy, aura immunity, penalty
- combat targeting, attack range, attack timing, damage logic
- wearable behavior, equip and unequip callbacks, slot restrictions
- armor durability or absorption
- weapon damage, projectile behavior, attack callbacks
- whether something should be pick-up-able, stackable, edible, cookable, fuel, or limited-use
- whether the behavior belongs on the item side, inventory side, or world-target side
- chest, backpack, fridge, or custom inventory container logic

## Appearance Timing And Where These Components Usually Show Up

Use this quick mental model before choosing components:

- `inspectable`
  - almost every player-facing object or item
  - usually added very early unless the prefab is intentionally hidden from normal inspection
  - like `talker` on many creatures, its absence can be more informative than its presence
- `inventoryitem`
  - when the thing can physically enter an inventory slot or be dropped on the ground as an item
- `stackable`
  - when many copies of the same item should merge in one inventory slot
- `finiteuses`
  - when the item has use-count durability instead of fuel or armor condition
- `inventory`
  - usually on players, followers, or special entities that hold items internally
- `container`
  - on backpacks, chests, fridges, bundles, portable storage, or openable structures
- `edible`
  - on items that can be eaten directly
- `cookable`
  - on raw ingredients or creatures that can transform into a cooked prefab
- `fuel`
  - on items that can be consumed by a fueled target
- `pickable`
  - on world resources that are harvested from the world instead of picked up as loose items
- `tool`
  - on the worker side, usually items like axe, pickaxe, hammer, shovel, or tool-like weapons
- `workable`
  - on the target side, usually trees, boulders, chests, structures, or diggable plants
- `timer`
  - when the prefab has delayed phases, cooldowns, or scheduled state changes that should save or load cleanly
- `talker`
  - common on players and many creatures that can speak, chatter, or emit scripted text
  - when a creature intentionally has no speech behavior, that absence is worth noticing

## Survival Components

### `health`

Official file:

- `scripts/components/health.lua`

High-frequency methods:

- `GetPercent()`
- `SetPercent(percent, overtime, cause)`
- `DoDelta(amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb)`
- `SetCurrentHealth(amount)`
- `SetMaxHealth(amount)`
- `SetPenalty(penalty)`
- `DeltaPenalty(delta)`
- `Kill()`
- `ForceKill()`
- `IsDead()`
- `SetInvincible(val)`

Use it for:

- direct healing or damage
- max health changes
- death, revive, and damage gating flows
- health penalty systems

Common pitfalls:

- `DoDelta(...)` and `SetPercent(...)` are not interchangeable.
- `Kill()` respects more normal flow; `ForceKill()` bypasses invincibility.
- Health changes are server-authoritative; do not expect client-local mutation to be valid gameplay logic.

### `hunger`

Official file:

- `scripts/components/hunger.lua`

High-frequency methods:

- `GetPercent()`
- `SetPercent(p, overtime)`
- `SetCurrent(current, overtime)`
- `DoDelta(delta, overtime, ignore_invincible)`
- `SetMax(amount)`
- `SetRate(rate)`
- `Pause()`
- `Resume()`
- `IsStarving()`

Use it for:

- changing hunger values directly
- changing hunger drain rate
- pausing drain during special states
- starvation behavior

Common pitfalls:

- `SetRate(...)` changes ongoing drain, not the current hunger value.
- Starvation damage flow is tied to hunger update logic, not just the visible meter.
- Hunger changes should usually be made on the server side.

### `sanity`

Official file:

- `scripts/components/sanity.lua`

High-frequency methods:

- `GetPercent()`
- `GetRealPercent()`
- `SetPercent(per, overtime)`
- `DoDelta(delta, overtime)`
- `SetMax(amount)`
- `EnableLunacy(enable, source)`
- `AddSanityPenalty(key, mod)`
- `RemoveSanityPenalty(key)`
- `SetFullAuraImmunity(immunity, source)`
- `SetNegativeAuraImmunity(immunity, source)`
- `IsSane()`
- `IsInsane()`
- `IsLunacyMode()`

Use it for:

- sanity gain and loss
- lunacy mode or enlightenment behavior
- aura immunity or penalty systems
- max sanity tuning

Common pitfalls:

- `GetPercent()` may reflect penalty-adjusted behavior; when debugging, compare with `GetRealPercent()`.
- Lunacy and insanity mode logic is more than just subtracting sanity.
- Sanity drain and aura behavior are recalculated over time; one-off writes can be overridden by ongoing updates.

## Item Basics And Utility Components

### `inspectable`

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

- `inspectable` is so common on player-facing prefabs that its presence is usually not the interesting design choice.
- many prefab bugs are not inspectable bugs; they are missing `STRINGS` keys or wrong prefab naming
- custom inspect text often also needs `string-patterns.md`

### `inventoryitem`

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
- if an item cannot enter containers, check `cangoincontainer` and container rules before blaming `inventoryitem`

### `stackable`

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
- some item logic must account for partial stack removal, not just whole-item removal
- edible or fuel logic may need stack-aware behavior

### `finiteuses`

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
- if the item should vanish, break, or transform at zero uses, that belongs in `SetOnFinished(...)`
- a weapon or tool does not automatically need `finiteuses`

Observed official counterexamples:

- `hambat`
  - weapon behavior without `finiteuses`
- `lucy`
  - `weapon` + `tool` behavior without `finiteuses`

### `inventory`

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

### `fuel`

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

### `tool`

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

## Combat And Equipment Components

### `combat`

Official file:

- `scripts/components/combat.lua`

High-frequency methods:

- `SetDefaultDamage(damage)`
- `SetAttackPeriod(period)`
- `SetRange(attack, hit)`
- `SetTarget(target)`
- `DropTarget(hasnexttarget)`
- `HasTarget()`
- `CanAttack(target)`
- `TryAttack(target)`
- `DoAttack(targ, weapon, projectile, stimuli, instancemult, instrangeoverride, instpos)`
- `GetAttacked(attacker, damage, weapon, stimuli, spdamage)`
- `SetRetargetFunction(period, fn)`
- `SetKeepTargetFunction(fn)`
- `ShareTarget(target, range, fn, maxnum, musttags)`
- `CalcDamage(target, weapon, multiplier)`

Use it for:

- AI attack cadence and retargeting
- melee range or hit range changes
- direct combat hooks
- aggro and target sharing behavior

Common pitfalls:

- `combat` behavior is tightly coupled with stategraph and brain logic.
- Changing damage alone does not fix attack timing, hit windows, or target retention.
- For creatures, always inspect the matching prefab and stategraph together with `combat.lua`.

### `weapon`

Official file:

- `scripts/components/weapon.lua`

High-frequency methods:

- `SetDamage(dmg)`
- `SetRange(attack, hit)`
- `SetProjectile(projectile)`
- `SetProjectileOffset(offset)`
- `SetOnAttack(fn)`
- `SetOnProjectileLaunch(fn)`
- `SetOnProjectileLaunched(fn)`
- `SetElectric(damage_mult, wet_damage_mult)`
- `GetDamage(attacker, target)`

Use it for:

- melee weapon damage
- projectile weapon behavior
- electric or stimulus-based attacks
- attack callbacks

Common pitfalls:

- `weapon` defines weapon-side behavior; final combat flow still passes through `combat`.
- Projectile weapons usually need matching prefab and animation behavior, not just `SetProjectile(...)`.
- Range may need to align with both `weapon` and the attacker's `combat` setup.

### `equippable`

Official file:

- `scripts/components/equippable.lua`

High-frequency methods:

- `SetOnEquip(fn)`
- `SetOnUnequip(fn)`
- `SetOnPocket(fn)`
- `Equip(owner, from_ground)`
- `Unequip(owner)`
- `GetWalkSpeedMult()`
- `SetPreventUnequipping(shouldprevent)`
- `ShouldPreventUnequipping()`
- `GetDapperness(owner, ignore_wetness)`
- `IsRestricted(target)`

Use it for:

- equip and unequip hooks
- slot-specific wearable behavior
- movement-speed or dapperness effects
- equip restrictions

Common pitfalls:

- equip visuals often also need `owner.AnimState:OverrideSymbol(...)`
- `equippable` alone does not give armor or weapon behavior; combine it with `armor` or `weapon` when appropriate
- restrictions may fail from save/load edge cases if you only test fresh spawns

### `armor`

Official file:

- `scripts/components/armor.lua`

High-frequency methods:

- `InitCondition(amount, absorb_percent)`
- `InitIndestructible(absorb_percent)`
- `SetAbsorption(absorb_percent)`
- `SetCondition(amount)`
- `SetPercent(amount)`
- `GetPercent()`
- `TakeDamage(damage_amount)`
- `Repair(amount)`
- `SetOnFinished(fn)`

Use it for:

- durability-based protection
- percent absorption changes
- break and repair flows

Common pitfalls:

- `armor` handles durability and absorption, not equip slot behavior.
- Most wearable armor items need both `equippable` and `armor`.
- If an armor item breaks visually or disappears, inspect prefab and equip callbacks, not just `armor.lua`.

## Storage Component

### `container`

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

- `WidgetSetup(...)` and UI layout assumptions must match the actual container widget config.
- Open or close behavior can involve tags, state, or replica-side UI expectations.
- Item acceptance issues are often caused by `CanTakeItemInSlot(...)` or widget data mismatches, not by `GiveItem(...)` itself.

### `pickable`

Official file:

- `scripts/components/pickable.lua`

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

Use it for:

- berry bushes, saplings, crops, and world-harvest nodes
- harvest and regrow loops
- fertilize or barren state logic

Common pitfalls:

- `pickable` is for world harvestables, not loose items on the ground
- many pickables also use `workable` for digging up the plant or structure
- harvest behavior usually also needs inspect, loot, and animation state updates

### `workable`

Official file:

- `scripts/components/workable.lua`

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

Use it for:

- trees, boulders, diggable plants, hammerable structures, and breakable objects
- work-progress and finish callbacks

Common pitfalls:

- `workable` is the target-side component
- if a tool cannot affect the target, inspect both `tool` and `workable`
- work flow often also needs lootdropper, burnable, or structure-specific callbacks

### `timer`

Official file:

- `scripts/components/timer.lua`

High-frequency methods:

- `TimerExists(name)`
- `StartTimer(name, time, paused, initialtime_override)`
- `StopTimer(name)`
- `IsPaused(name)`
- `PauseTimer(name)`
- `ResumeTimer(name)`
- `GetTimeLeft(name)`
- `SetTimeLeft(name, time)`
- `GetTimeElapsed(name)`

Use it for:

- cooldowns
- delayed spawns or phase changes
- state changes that must survive save or load

Common pitfalls:

- `timer` is state storage plus timing; it does not perform behavior by itself
- the prefab still needs event listeners or callbacks for timer completion
- if a timer drives UI or animation, that other system also needs inspection

### `talker`

Official file:

- `scripts/components/talker.lua`

High-frequency methods:

- `MakeChatter()`
- `Chatter(strtbl, strid, time, forcetext, echotochatpriority)`
- `Say(script, time, noanim, force, nobroadcast, colour, text_filter_context, original_author_netid, onfinishedlinesfn, sgparam)`
- `ShutUp()`
- `IgnoreAll(source)`
- `StopIgnoringAll(source)`

Use it for:

- player speech bubbles
- creature, boss, or NPC lines
- chatter loops and ambient comments
- cases where a creature should intentionally omit normal speaking behavior

Common pitfalls:

- `talker` is common enough on creature-like prefabs that "missing talker" can itself be a meaningful design choice
- speech display may also depend on net, string keys, and client presentation
- if the task is dialogue logic, inspect the speaking caller and strings, not just `talker.lua`

### `edible`

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
- final eater behavior also depends on eater-side systems, not only the food item

### `cookable`

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

## Common Component Combinations

Assume `inspectable` is present on most player-facing prefabs unless the prefab is intentionally non-inspectable.
The combinations below keep listing it because it is commonly part of the final bundle, but it is often not the deciding component.
Treat each line as a candidate bundle that can be reduced when the request explicitly excludes a capability.

- loose inventory material
  - `inspectable` + `inventoryitem`
- stackable material
  - `inspectable` + `inventoryitem` + `stackable`
- edible item
  - `inspectable` + `inventoryitem` + `edible`
- raw ingredient that can also be cooked
  - `inspectable` + `inventoryitem` + `edible` + `cookable`
- fuel item
  - `inspectable` + `inventoryitem` + often `stackable` + `fuel`
- tool item
  - `inspectable` + `inventoryitem` + `finiteuses` + `tool` + often `equippable`
- creature combatant
  - `health` + `combat`
- player survival tuning
  - `health` + `hunger` + `sanity`
- weapon item
  - `inspectable` + `inventoryitem` + `finiteuses` + `weapon` + `equippable`
- infinite-durability weapon item
  - `inspectable` + `inventoryitem` + `weapon` + `equippable`
  - omit `finiteuses`
- wearable armor
  - `equippable` + `armor`
- wearable container
  - `inspectable` + `inventoryitem` + `equippable` + `container`
- infinite-durability tool item
  - `inspectable` + `inventoryitem` + `tool` + often `equippable`
  - omit `finiteuses`
- world harvest plant
  - `pickable` + `inspectable` + often `workable`
- hammerable or diggable structure
  - `inspectable` + `workable` + often `container` or `lootdropper`
- storage item or structure
  - `container` + often `inspectable`

## Intent Index

Use this when the user describes a feature in plain language rather than by component name.

Assume `inspectable` for most normal player-facing prefabs unless the request explicitly implies the object should not be inspectable.
Apply subtractive reasoning here: if the request rules out a capability, remove the component that normally provides it.

- "I want to add a weapon item"
  - start from `inspectable` + `inventoryitem` + `finiteuses` + `weapon` + `equippable`
  - then inspect equip visuals and `AnimState` if it is player-held
- "I want to add an infinite-durability weapon"
  - start from `inspectable` + `inventoryitem` + `weapon` + `equippable`
  - do not add `finiteuses`
  - verify against official counterexamples such as `hambat`
- "I want to add armor or clothing"
  - start from `inspectable` + `inventoryitem` + `equippable`
  - add `armor` if it should absorb damage
- "I want to add a backpack"
  - start from `inspectable` + `inventoryitem` + `equippable` + `container`
- "I want to add a chest or storage structure"
  - start from `inspectable` + `container`
  - add `workable` if it can be hammered or dismantled
- "I want to add a basic material item"
  - start from `inspectable` + `inventoryitem`
  - add `stackable` if it should merge in inventory
  - add `fuel` if it can be burned as fuel
- "I want to add a food item"
  - start from `inspectable` + `inventoryitem` + `edible`
  - add `stackable` if it should stack
  - add `cookable` if it should transform when cooked
- "I want to add a cookable ingredient"
  - start from `inspectable` + `inventoryitem` + often `edible` + `cookable`
- "I want to add a tool item"
  - start from `inspectable` + `inventoryitem` + `finiteuses` + `tool`
  - add `equippable` if it is hand-equipped
- "I want to add an infinite-durability tool"
  - start from `inspectable` + `inventoryitem` + `tool`
  - add `equippable` if it is hand-equipped
  - do not add `finiteuses`
  - verify against official counterexamples such as `lucy`
- "I want to add a pickable world plant or resource"
  - start from `pickable` + `inspectable`
  - add `workable` if it can also be dug up or destroyed
- "I want to add a hammerable or diggable structure"
  - start from `inspectable` + `workable`
  - add `container` if it stores items
- "I want to add something with timed state changes"
  - start from `timer`
  - then pair it with the gameplay component it is timing
- "I want to add a creature that intentionally does not use `talker`"
  - first verify the closest official creature prefab, because many creature-like prefabs do include `talker`
  - treat missing `talker` as an intentional design choice, not a default assumption
  - then check whether speech, chatter, or string-driven events must be removed or replaced elsewhere
- "I want to add a prefab that intentionally does not use `inspectable`"
  - first verify the closest official prefab, because most normal player-facing prefabs do include `inspectable`
  - treat missing `inspectable` as an intentional interaction choice, not a default assumption
  - then check whether the prefab should instead be hidden, helper-only, `NOCLICK`, or UI-inaccessible

## Practical Reading Order

1. Read the component file itself under `scripts/components/`.
2. Read the closest official prefab that uses the component in the same way.
3. If the component affects animation or action flow, also read the relevant stategraph or `AnimState` reference.
4. If the component affects client UI, also inspect replica, widget, or local-runtime pages.

## Rule Of Thumb

- If the task changes one stat, start in that one component file.
- If the task changes battle behavior, read `combat.lua` plus the prefab and SG.
- If the task changes an item worn by players, read `equippable.lua` plus `armor.lua` or `weapon.lua` and the item's equip visuals.
- If the task changes storage UX, read `container.lua` plus the widget config path.
- If the user describes an item by function instead of component name, map the intent to a component bundle first, then verify with the closest official prefab.
- If the user also specifies what the prefab should not do, remove the matching default component from the bundle before implementing.
