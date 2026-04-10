# Feature Recipes

Use this file when the user describes a whole feature shape such as "make a weapon", "make a container", "make a creature", or "make a playable character".

This page is a task-entry layer:

- what files are usually involved
- which components are usually present
- which tags or strings usually matter
- which adjacent reference pages should be opened next

For minimal code snippets, also read `references/template-patterns.md`.

## Weapon Item

Use this when the user wants a normal hand-held weapon.

Usually involved:

- `modmain.lua`
  - add the prefab to `PrefabFiles`
- `prefabs/<weapon>.lua`
  - define the item prefab
- `images/inventoryimages/<weapon>.xml + .tex`
  - inventory icon atlas pair when a custom icon is needed
- `anim/<weapon>.zip`
  - ground or inventory animation
- often `anim/swap_<weapon>.zip`
  - equip visual for the player hand
- `strings`
  - `STRINGS.NAMES.<WEAPON>`
  - `STRINGS.CHARACTERS.GENERIC.DESCRIBE.<WEAPON>`

Typical components:

- `inspectable`
- `inventoryitem`
- `weapon`
- `equippable`
- optional `finiteuses`

Common adjacent work:

- `owner.AnimState:OverrideSymbol(...)` in equip callbacks
- `SetDamage(...)`
- optional `SetProjectile(...)`
- optional `SetOnAttack(...)`

Common routing:

- read `references/component-patterns.md`
- read `references/animstate-patterns.md`
- read `references/asset-patterns.md`

## Armor Or Clothing

Use this when the user wants a wearable that changes defense, dapperness, or movement.

Usually involved:

- `modmain.lua`
- `prefabs/<item>.lua`
- `anim/<item>.zip`
- often `anim/swap_<item>.zip`
- inventory icon atlas pair if custom
- `strings`

Typical components:

- `inspectable`
- `inventoryitem`
- `equippable`
- optional `armor`

Common adjacent work:

- slot selection
- equip and unequip callbacks
- symbol override for wearable visuals
- optional `SetAbsorption(...)` or `InitCondition(...)`

Common routing:

- read `references/components/combat-and-equipment.md`
- read `references/animstate-patterns.md`

## Container Item Or Structure

Use this when the user wants a backpack, chest, fridge, or portable container.

Usually involved:

- `modmain.lua`
- `prefabs/<container>.lua`
- possibly `scripts/widgets/<widget>.lua` or existing container widget config
- icon atlas pair if it is an inventory item
- `strings`

Typical components:

- inventory item route
  - `inspectable`
  - `inventoryitem`
  - `equippable` if wearable
  - `container`
- structure route
  - `inspectable`
  - `container`
  - often `workable`

Common adjacent work:

- `WidgetSetup(...)`
- slot count and acceptance rules
- open and close behavior
- replica-side UI expectations

Common routing:

- read `references/components/items-and-storage.md`
- read `references/ui-patterns.md`
- read `references/tag-patterns.md` if interaction filtering matters

## Pickable Plant Or Harvest Node

Use this when the user wants berries, saplings, herbs, or a world node with regrowth.

Usually involved:

- `modmain.lua`
- `prefabs/<plant>.lua`
- animation assets for full, empty, barren, or regrown state
- loot strings and inspect strings

Typical components:

- `inspectable`
- `pickable`
- often `workable`
- often `lootdropper`

Common adjacent work:

- `SetUp(product, regen, number)`
- pick, regen, barren, or fertilize callbacks
- animation state updates for harvested vs grown state

Common routing:

- read `references/components/world-and-utility.md`
- read `references/world-system-patterns.md`
- read `references/animstate-patterns.md`

## Creature Or Mob

Use this when the user wants a normal AI creature, follower, or boss-like enemy.

Usually involved:

- `modmain.lua`
- `prefabs/<creature>.lua`
- `brains/<brain>.lua`
- `stategraphs/SG<creature>.lua`
- animation assets
- speech or inspect strings

Typical components:

- `health`
- `combat`
- often `lootdropper`
- often `inspectable`
- often `talker`
- often locomotion-related world helpers from standardcomponents

Common adjacent work:

- `inst:SetBrain(...)`
- `inst:SetStateGraph(...)`
- retarget and keep-target logic
- attack timing in the SG
- optional chatter or boss lines

Common routing:

- read `references/brain-patterns.md`
- read `references/stategraph-patterns.md`
- read `references/components/combat-and-equipment.md`
- read `references/components/world-and-utility.md`

## Structure

Use this when the user wants a station, machine, altar, deployable building, or inspectable world prop.

Usually involved:

- `modmain.lua`
- `prefabs/<structure>.lua`
- recipe and placer registration
- animation assets
- minimap or inventory assets if needed
- strings

Typical components:

- `inspectable`
- often `workable`
- optional `container`
- optional `prototyper`
- optional `trader`
- optional `fueled`, `burnable`, `hauntable`

Common adjacent work:

- `AddRecipe2(...)`
- `MakePlacer(...)`
- placement spacing and tags
- structure state animation and sounds
- optional light or FX helpers

Common routing:

- read `references/world-system-patterns.md`
- read `references/recipe-patterns.md`
- read `references/effects-patterns.md` if the structure glows or emits FX

## Playable Character

Use this when the user wants a full character mod rather than a normal creature.

Usually involved:

- `modmain.lua`
- character prefab file
- speech strings
- runtime i18n files if localized
- avatar, map icon, select screen, or inventory icon assets
- optional `scripts/prefabs/skilltree_<name>.lua`
- optional custom SG or post-init hooks for player behavior

Typical components or systems:

- player prefab hooks through `prefabs/player_common.lua`
- `MakePlayerCharacter(...)`
- survival stat tuning
- character-specific strings under `STRINGS.CHARACTERS.<NAME>`
- optional custom crafting, actions, RPC, or UI
- optional skill-gated recipes or progression

Common adjacent work:

- classify the mod type from `modinfo.lua`
- register the character from `modmain.lua`
- inherit character speech from `STRINGS.CHARACTERS.GENERIC`
- patch player initialization carefully
- decide whether the character actually needs a skill tree

Common routing:

- read `references/character-patterns.md`
- read `references/player-patterns.md` if the request is really a player-wide patch rather than one character's local identity
- read `references/runtime-i18n-patterns.md`
- read `references/string-patterns.md`
- read `references/stategraph-patterns.md`
- read `references/recipe-patterns.md` if the character has skill-gated or character-gated crafting
- read `references/networking-patterns.md` if custom client-visible systems are added

## Lit, FX, Or Sound-Driven Prefab

Use this when the user primarily wants presentation behavior rather than a stat-heavy gameplay object.

Usually involved:

- prefab file
- animation assets or atlas resources
- optional shader or particle textures
- optional sound events

Typical tags or entity pieces:

- `FX`
- optional `NOCLICK`
- `AddLight()`
- `AddSoundEmitter()`
- `AddAnimState()`
- optional `AddVFXEffect()`

Common routing:

- read `references/effects-patterns.md`
- read `references/animstate-patterns.md`
- read `references/asset-patterns.md`

## World Preset, Customization Option, Or Start Location

Use this when the user wants a host-selectable world option, a preset-facing tweak, or a custom spawn start.

Usually involved:

- `modworldgenmain.lua`
  - generation-side registration
- sometimes `modservercreationmain.lua`
  - host-facing setup or preset-facing frontend behavior
- `scripts/map/customize.lua`
  - category and option routing
- `scripts/map/levels.lua`
  - preset lookup and combined preset behavior
- `scripts/map/startlocations.lua`
  - start-location definitions

Typical helpers:

- `AddCustomizeGroup`
- `AddCustomizeItem`
- `RemoveCustomizeGroup`
- `RemoveCustomizeItem`
- `AddStartLocation`
- sometimes `AddLevelPreInit`
- sometimes `AddTaskSetPreInit`

Common adjacent work:

- choosing `LEVELCATEGORY.SETTINGS` versus `LEVELCATEGORY.WORLDGEN`
- confirming whether the change is preset-facing, generation-facing, or both
- checking combined preset behavior
- verifying host setup UI refresh behavior

Common routing:

- read `references/worldgen-patterns.md`
- read `references/task-playbook.md`
- read `references/mod-api-map.md`

## Rule Of Thumb

- Use this page to map the requested feature to the likely file set.
- Then open the narrow subsystem pages for the exact implementation details.
- If the user gives a negative constraint such as "infinite durability" or "non-inspectable", remove the default piece that would normally be present.
