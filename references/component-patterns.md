# High-Frequency Component Patterns

Use this file when a task is mainly about common official components rather than a whole subsystem.

If the task also depends on prefab tags or action/query routing, read `references/patterns/tag-patterns.md`.
If the task also depends on lighting, FX prefabs, or sound playback, read `references/patterns/effects-patterns.md`.

This page is the routing and prediction layer. Method lists and per-component pitfalls live under `references/components/`.

## Per-Component Detail Pages

- [components/health.md](components/health.md)
- [components/hunger.md](components/hunger.md)
- [components/sanity.md](components/sanity.md)
- [components/inspectable.md](components/inspectable.md)
- [components/inventoryitem.md](components/inventoryitem.md)
- [components/stackable.md](components/stackable.md)
- [components/finiteuses.md](components/finiteuses.md)
- [components/inventory.md](components/inventory.md)
- [components/container.md](components/container.md)
- [components/edible.md](components/edible.md)
- [components/cookable.md](components/cookable.md)
- [components/fuel.md](components/fuel.md)
- [components/tool.md](components/tool.md)
- [components/combat.md](components/combat.md)
- [components/weapon.md](components/weapon.md)
- [components/equippable.md](components/equippable.md)
- [components/armor.md](components/armor.md)
- [components/pickable.md](components/pickable.md)
- [components/workable.md](components/workable.md)
- [components/timer.md](components/timer.md)
- [components/talker.md](components/talker.md)

## Bundle Summary Pages

- [components/survival.md](components/survival.md)
  - `health`, `hunger`, `sanity`
- [components/items-and-storage.md](components/items-and-storage.md)
  - `inspectable`, `inventoryitem`, `stackable`, `finiteuses`, `inventory`, `container`, `edible`, `cookable`, `fuel`, `tool`
- [components/combat-and-equipment.md](components/combat-and-equipment.md)
  - `combat`, `weapon`, `equippable`, `armor`
- [components/world-and-utility.md](components/world-and-utility.md)
  - `pickable`, `workable`, `timer`, `talker`

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

## Quick Component Map

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

Rules:

- these bundles are common patterns, not mandatory checklists
- start from the smallest component set that matches the intended behavior
- add a component only when the prefab truly needs that capability
- if the request includes a negative constraint such as "infinite durability" or "non-inspectable", remove the default component you would otherwise expect

## Appearance Timing And Usual Placement

Use this as the first routing pass before opening detail pages:

- `inspectable`
  - almost every player-facing object or item
  - its absence is often more informative than its presence
- `inventoryitem`
  - when the thing can enter an inventory slot or exist as a loose item
- `stackable`
  - when many copies should merge in one slot
- `finiteuses`
  - when the item has use-count durability instead of fuel or armor condition
- `inventory`
  - usually on players, followers, or special holders
- `container`
  - on backpacks, chests, fridges, bundles, portable storage, or openable structures
- `edible`
  - on things that can be eaten directly
- `cookable`
  - on things that transform into another prefab when cooked
- `fuel`
  - on the consumed fuel item, not the fueled target
- `tool`
  - on the acting item
- `pickable`
  - on world harvest nodes, not loose items
- `workable`
  - on the target being worked
- `timer`
  - when delayed phases or cooldowns should save or load cleanly
- `talker`
  - common on players and many creature-like prefabs
  - missing `talker` can be an intentional design signal

## Common Component Combinations

Assume `inspectable` for most player-facing prefabs unless the prefab is intentionally non-inspectable.
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
  - treat missing `talker` as an intentional design choice
- "I want to add a prefab that intentionally does not use `inspectable`"
  - first verify the closest official prefab, because most player-facing prefabs do include `inspectable`
  - treat missing `inspectable` as an intentional interaction choice

## Practical Reading Order

1. Use this page to predict the likely component bundle.
2. Open the matching per-component page under `references/components/`.
3. Use the bundle summary pages only when the task spans several neighboring components.
4. Read the official component file itself under `scripts/components/`.
5. Read the closest official prefab that uses the component in the same way.
6. If the component affects animation, actions, or networking, also inspect the matching narrow reference page.

## Rule Of Thumb

- Use this page to decide what probably belongs on the prefab.
- Use the per-component files under `references/components/` to inspect methods and common pitfalls.
- Use the bundle summary pages when several adjacent components are involved at once.
- Then verify everything against the closest official prefab.
