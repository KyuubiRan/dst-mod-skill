# World System Patterns

Use this file when a task touches common world-side gameplay systems rather than a single narrow component.

This page focuses on high-frequency official systems that often appear together in prefabs:

- `fueled`
- `burnable`
- `freezable`
- `lootdropper`
- `trader`
- `hauntable`
- `deployable`

Read exact signatures from the official component files first.
Then inspect the closest official prefab that combines them in the same way.

## Why This Page Exists

These systems are common enough that mod tasks often sound like:

- "this structure should accept fuel"
- "this plant should burn and drop loot"
- "this creature should freeze correctly"
- "this object should be hauntable"
- "this item should deploy into a structure"
- "this NPC should accept trade items"

The official pattern usually depends on a component combination rather than one component alone.

## `fueled`

Official file:

- `scripts/components/fueled.lua`

High-frequency methods:

- `SetSectionCallback(fn)`
- `SetDepletedFn(fn)`
- `SetSections(num)`
- `CanAcceptFuelItem(item)`
- `SetCanTakeFuelItemFn(fn)`
- `SetTakeFuelItemFn(fn)`
- `TakeFuelItem(item, doer)`
- `SetUpdateFn(fn)`
- `GetPercent()`
- `SetPercent(amount)`
- `StartConsuming()`
- `StopConsuming()`
- `DoDelta(amount, doer)`

Use it for:

- structures or items that store and consume fuel
- machines with visible fuel state
- battery-like or burn-time gameplay systems

Important distinction:

- `fuel`
  - the item being consumed as fuel
- `fueled`
  - the target that accepts and spends fuel

Observed official pattern:

- `winona_battery_low.lua`
  - fueled target with sectioned visual state and updates

Common pitfalls:

- do not confuse `fuel` and `fueled`
- if the fueled thing also has visible state, inspect its `AnimState` or netvar path too
- if fuel can be added by item use, action routing matters in addition to the component itself

## `burnable`

Official file:

- `scripts/components/burnable.lua`

High-frequency methods:

- `SetOnSmolderingFn(fn)`
- `SetOnStopSmolderingFn(fn)`
- `SetOnIgniteFn(fn)`
- `SetOnBurntFn(fn)`
- `SetOnExtinguishFn(fn)`
- `SetBurnTime(time)`
- `IsBurning()`
- `IsSmoldering()`
- `Ignite(immediate, source, doer)`
- `SmotherSmolder(smotherer)`
- `Extinguish(resetpropagator, heatpct, smotherer)`
- `AddBurnFX(prefab, offset, followsymbol, followaschild, scale, followlayered)`

High-frequency helpers from `scripts/standardcomponents.lua`:

- `MakeSmallBurnable(...)`
- `MakeMediumBurnable(...)`
- `MakeLargeBurnable(...)`
- character-specific burnable helpers

Use it for:

- burnable items or structures
- smoldering and ignition flow
- fire FX and burn completion callbacks

Observed official combinations:

- `backpack.lua`
  - `container` + `burnable` + propagator + hauntable drop behavior
- `treasurechest.lua`
  - `container` + `workable` + `lootdropper` + burnable structure handling

Common pitfalls:

- prefer `MakeSmallBurnable` or its siblings before hand-building the setup
- structures often need different burn behavior than loose items
- burning frequently changes loot, open containers, or visual state, so inspect the prefab callbacks too

## `freezable`

Official file:

- `scripts/components/freezable.lua`

High-frequency methods:

- `SetResistance(resist)`
- `SetDefaultWearOffTime(wearofftime)`
- `AddShatterFX(prefab, offset, followsymbol)`
- `SpawnShatterFX()`
- `IsFrozen()`
- `IsThawing()`
- `AddColdness(coldness, freezetime, nofreeze)`
- `Freeze(freezetime)`
- `Unfreeze()`
- `Thaw(thawtime)`

High-frequency helpers from `scripts/standardcomponents.lua`:

- `MakeTinyFreezableCharacter(...)`
- `MakeSmallFreezableCharacter(...)`
- `MakeMediumFreezableCharacter(...)`
- `MakeLargeFreezableCharacter(...)`

Use it for:

- creatures that can be frozen or thawed
- coldness accumulation
- freeze-specific FX and wear-off timing

Observed official pattern:

- `spiderden.lua`
  - freeze and thaw behavior tied to `AnimState`, sounds, and symbol overrides

Common pitfalls:

- freezing behavior usually includes SG, sound, and animation consequences, not just the component call
- use the size-appropriate helper when possible

## `lootdropper`

Official file:

- `scripts/components/lootdropper.lua`

High-frequency methods:

- `SetChanceLootTable(name)`
- `SetLoot(loots)`
- `SetLootSetupFn(fn)`
- `AddRandomLoot(prefab, weight)`
- `AddChanceLoot(prefab, chance)`
- `GenerateLoot()`
- `SpawnLootPrefab(lootprefab, pt, linked_skinname, skin_id, userid)`
- `DropLoot(pt, prefabs)`

Use it for:

- creature death loot
- structure destruction loot
- randomized loot tables

Observed official pattern:

- `treasurechest.lua`
  - `container` + `workable` + `lootdropper` for hammer and break flow

Common pitfalls:

- if destruction or work completion should drop stored contents too, inspect container teardown flow as well
- loot callbacks often belong to prefab-level destruction logic, not only `lootdropper`

## `trader`

Official file:

- `scripts/components/trader.lua`

High-frequency methods:

- `Enable()`
- `Disable()`
- `SetAcceptTest(fn)`
- `SetAbleToAcceptTest(fn)`
- `SetOnAccept(fn)`
- `SetOnRefuse(fn)`
- `SetAcceptStacks()`
- `AbleToAccept(item, giver, count)`
- `WantsToAccept(item, giver, count)`
- `AcceptGift(giver, item, count)`

Use it for:

- NPCs or structures that accept gifts or trade items
- custom acceptance rules
- on-accept and on-refuse behavior

Common pitfalls:

- acceptance flow usually also depends on action routing such as `GIVE`
- if the trade target has dialogue or FX, inspect `talker`, `lootdropper`, or prefab callbacks too

## `hauntable`

Official file:

- `scripts/components/hauntable.lua`

High-frequency methods:

- `SetOnHauntFn(fn)`
- `SetOnUnHauntFn(fn)`
- `SetHauntValue(val)`
- `Panic(panictime)`
- `DoHaunt(doer)`

High-frequency helpers from `scripts/standardcomponents.lua`:

- `MakeHauntable(...)`
- `MakeHauntableLaunch(...)`
- `MakeHauntableWork(...)`
- `MakeHauntableIgnite(...)`
- `MakeHauntableLaunchAndDropFirstItem(...)`
- other `MakeHauntable*` combinations

Use it for:

- ghost interaction
- panic, launch, ignite, work, or transform haunt effects

Observed official combinations:

- `backpack.lua`
  - `MakeHauntableLaunchAndDropFirstItem(inst)`
- `berrybush.lua`
  - `MakeHauntableIgnite(inst)` plus custom haunt reaction

Common pitfalls:

- prefer the standard helper if it already matches the intended haunt behavior
- only drop to a custom haunt callback when the official helper family is not enough

## `deployable`

Official file:

- `scripts/components/deployable.lua`

High-frequency methods:

- `SetDeployMode(mode)`
- `GetDeployMode()`
- `SetDeploySpacing(spacing)`
- `SetUseGridPlacer(usegridplacer)`
- `SetDeployTossSymbolOverride(data)`
- `IsDeployable(deployer)`
- `CanDeploy(pt, mouseover, deployer, rot)`
- `Deploy(pt, deployer, rot)`

Use it for:

- items that place structures or world objects
- deploy spacing and deploy mode rules
- item-to-world transformation

Common pitfalls:

- deployable item logic usually also needs recipe or placer alignment
- preview behavior often depends on `MakePlacer(...)` or placement configuration, not only the deployable component

## Common World-System Combinations

- burnable storage structure
  - `container` + `workable` + `lootdropper` + `burnable`
- wearable burnable container
  - `inventoryitem` + `equippable` + `container` + `burnable`
- harvestable world plant
  - `pickable` + `inspectable` + often `workable` + `lootdropper` + `burnable`
- fueled machine
  - `fueled` + visible animation/state updates + often `inspectable`
- hauntable item or structure
  - normal gameplay component set + `hauntable` helper matching the desired ghost effect
- deployable placeable item
  - `inventoryitem` + `deployable` + placer/recipe alignment

## Practical Reading Order

1. Read the exact component file.
2. Read `scripts/standardcomponents.lua` if a helper likely exists.
3. Read the closest official prefab that combines the same systems.
4. If visuals matter, inspect animation or FX handling too.
5. If player interaction matters, inspect action routing too.

## Rule Of Thumb

- Prefer official helper constructors for burnable, freezable, and hauntable behavior.
- Use component combinations as the unit of reasoning, not isolated components.
- When destruction, burning, or harvesting changes stored contents or loot, inspect the prefab teardown path in full.
