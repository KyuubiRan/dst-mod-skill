# Official Example Index

Use this file when you already know the subsystem, but still need a concrete official DST example to open first.

This page is a fast example router, not a replacement for the narrower pattern pages.
Pick one close official file, read it, then drill into the subsystem page that explains the underlying pattern.

## Item And Equipment Examples

- `scripts/prefabs/spear.lua`
  - simple weapon item
- `scripts/prefabs/armor_grass.lua`
  - simple wearable armor
- `scripts/prefabs/backpack.lua`
  - wearable container
- `scripts/prefabs/treasurechest.lua`
  - chest structure with container and workable flow
- `scripts/prefabs/berrybush.lua`
  - pickable world plant
- `scripts/prefabs/coldfirepit.lua`
  - lit structure with burn and fuel-related behavior
- `scripts/prefabs/winona_battery_low.lua`
  - fueled machine, helper entities, sound loops, and richer structure setup

Read next:

- `references/component-patterns.md`
- `references/patterns/world-system-patterns.md`
- `references/patterns/animstate-patterns.md`

## Bootstrap And Registration Examples

- `scripts/mods.lua`
  - loader flow for mod environment setup, `modimport(...)`, `modmain.lua`, `PrefabFiles`, and mod-level `Assets`
- `scripts/modutil.lua`
  - registration APIs that `modmain.lua` usually calls
- `scripts/prefabs/staff.lua`
  - a grouped prefab-file family that shows what `PrefabFiles` can point at after bootstrap

Read next:

- `references/patterns/entrypoint-patterns.md`
- `references/patterns/modmain-patterns.md`
- `references/patterns/creation-patterns.md`

## Creature, Brain, And SG Examples

- `scripts/prefabs/glommer.lua`
  - creature prefab with brain and SG wiring
- `scripts/brains/glommerbrain.lua`
  - compact behavior-tree example
- `scripts/stategraphs/SGglommer.lua`
  - matching execution-side SG
- `scripts/prefabs/player_common.lua`
  - player-side SG and networking wiring
- `scripts/stategraphs/SGwilson.lua`
  - authoritative player action states
- `scripts/stategraphs/SGwilson_client.lua`
  - predicted player action states

Read next:

- `references/patterns/brain-patterns.md`
- `references/patterns/stategraph-patterns.md`
- `references/patterns/networking-patterns.md`

## Playable Character And Skill Tree Examples

- `scripts/modutil.lua`
  - `AddModCharacter(...)` registration and optional mod character mode storage
- `scripts/prefabs/player_common.lua`
  - shared player-character constructor, client/server split, and baseline player systems
- `scripts/prefabs/wilson.lua`
  - compact vanilla character example with `common_postinit` and `master_postinit`
- `scripts/prefabs/wormwood.lua`
  - richer character example with custom assets and skill-tree asset registration
- `scripts/prefabs/skilltree_defs.lua`
  - central skill-tree registry, validation helpers, and `CreateSkillTreeFor(...)`
- `scripts/prefabs/skilltree_wilson.lua`
  - character-local skill-tree data module
- `scripts/screens/lobbyscreen.lua`
  - frontend consumer for `images/names_<character>.xml` and `bigportraits/...`
- `scripts/screens/redux/serverslotscreen.lua`
  - mod-character save-slot portrait lookup
- `scripts/widgets/inventorybar.lua`
  - self-inspect avatar lookup
- `scripts/widgets/redux/loadoutselect.lua`
  - mod-character preview mode routing through `MODCHARACTERMODES`
- `scripts/widgets/skinspuppet.lua`
  - wardrobe puppet build and anim selection for skin modes
- `scripts/skinsutils.lua`
  - default `GetSkinModes(...)` data and skinned-character helpers
- `scripts/widgets/redux/skilltreewidget.lua`
  - skill-tree background image contract
- `scripts/widgets/redux/skilltreebuilder.lua`
  - skill-tree icon lookup contract

Read next:

- `references/patterns/character-patterns.md`
- `references/patterns/runtime-i18n-patterns.md`
- `references/patterns/recipe-patterns.md`

## Player-Wide Patch Examples

- `scripts/modutil.lua`
  - `AddPlayerPostInit(...)` is implemented through `AddPrefabPostInitAny(...)` plus the `player` tag
- `scripts/prefabs/player_common.lua`
  - player baseline setup, `common_postinit`, `master_postinit`, and player lifecycle events

Read next:

- `references/patterns/player-patterns.md`
- `references/patterns/player-network-patterns.md`
- `references/patterns/hook-selection-patterns.md`
- `references/patterns/runtime-local-ui.md`
- `references/patterns/runtime-authority.md`

## Skin System Examples

- `scripts/prefabskin.lua`
  - `CreatePrefabSkin(...)` and shared skin helper functions
- `scripts/prefabskins.lua`
  - generated `PREFAB_SKINS` and `PREFAB_SKINS_IDS`
- `scripts/prefabs/skinprefabs.lua`
  - generated base-skin and item-skin data
- `scripts/skinsutils.lua`
  - skin data lookup, build-name resolution, portrait naming, and skin modes
- `scripts/widgets/redux/loadoutselect.lua`
  - mod-character preview modes and vanilla-character base-skin UI behavior
- `scripts/screens/redux/defaultskinselection.lua`
  - ownership-gated skin list building

Read next:

- `references/patterns/skin-patterns.md`
- `references/patterns/character-patterns.md`
- `references/patterns/creation-patterns.md`

## Standard Helper Examples

- `scripts/standardcomponents.lua`
  - official `Make*` helper definitions
- `scripts/prefabs/spear.lua`
  - `MakeInventoryPhysics(...)`, `MakeInventoryFloatable(...)`, and `MakeHauntableLaunch(...)`
- `scripts/prefabs/backpack.lua`
  - `MakeInventoryFloatable(...)`, burnable or propagator helpers, and `MakeHauntableLaunchAndDropFirstItem(...)`
- `scripts/prefabs/berrybush.lua`
  - obstacle physics, snow-covered helpers, seasonal growth helper, and haunt custom reaction
- `scripts/prefabs/treasurechest.lua`
  - structure-side burnable setup and heavy obstacle physics

Read next:

- `references/patterns/standard-helper-patterns.md`
- `references/patterns/world-system-patterns.md`
- `references/signatures/helper-signatures.md`

## FX, Light, And Sound Examples

- `scripts/prefabs/moon_altar.lua`
  - lit world structure
- `scripts/prefabs/lighterfire_common.lua`
  - child light helper with replicated range
- `scripts/prefabs/moose_nest_fx.lua`
  - one-shot FX prefab and proxy-style trigger
- `scripts/prefabs/deer_fx.lua`
  - shared FX factory with optional light and sound
- `scripts/prefabs/atrium_gate_pulsesfx.lua`
  - sound-only proxy pattern
- `scripts/prefabs/torchfire_barber.lua`
  - `AddVFXEffect()` particle system

Read next:

- `references/patterns/effects-patterns.md`
- `references/patterns/tag-patterns.md`
- `references/patterns/asset-patterns.md`

## UI And Frontend Examples

- `scripts/widgets/controls.lua`
  - persistent HUD child ownership
- `scripts/screens/playerhud.lua`
  - player HUD lifecycle and screen-owned UI flow
- `scripts/widgets/containerwidget.lua`
  - transient open or close widget with per-open listeners and cleanup
- `scripts/screens/redux/popupdialog.lua`
  - compact modal screen with `default_focus`, `OnControl(...)`, and `Close()`
- `scripts/widgets/screen.lua`
  - base screen lifecycle, focus restore, and `OnBecomeActive()` or `OnBecomeInactive()`
- `scripts/screens/redux/servercreationscreen.lua`
  - server setup screen flow
- `scripts/frontend.lua`
  - screen stack, top-level input plumbing, fade flow, and frontend sound helpers

Read next:

- `references/patterns/ui-patterns.md`
- `references/patterns/ui-patch-patterns.md`
- `references/pitfalls/ui-pitfalls.md`
- `references/patterns/hook-selection-patterns.md`
- `references/patterns/input-patterns.md`
- `references/patterns/runtime-local-ui.md`

## Action And Interaction Examples

- `scripts/componentactions.lua`
  - official action collectors and action-type routing
- `scripts/stategraphs/SGwilson.lua`
  - player performer-side action states
- `scripts/stategraphs/SGwilson_client.lua`
  - predicted client performer states
- `scripts/modutil.lua`
  - mod-side action registration APIs

Read next:

- `references/patterns/action-patterns.md`
- `references/patterns/stategraph-patterns.md`

## Networking And Classified Examples

- `scripts/entityreplica.lua`
  - replica loading and `AddReplicableComponent(...)` path
- `scripts/prefabs/player_common.lua`
  - player-side networking and classified attach flow
- `scripts/prefabs/player_classified.lua`
  - large classified entity example
- `scripts/components/inventory_replica.lua`
  - replica-side API and classified attach pattern
- `scripts/networkclientrpc.lua`
  - RPC namespace and id routing

Read next:

- `references/patterns/networking-patterns.md`
- `references/templates/networking-templates.md`
- `references/patterns/player-network-patterns.md`
- `references/patterns/runtime-authority.md`

## Save, Load, And Offline Progress Examples

- `scripts/entityscript.lua`
  - core save and load lifecycle: `GetPersistData()`, `SetPersistData()`, `LoadPostPass()`, `LongUpdate()`
- `scripts/components/childspawner.lua`
  - save refs plus `LoadPostPass(...)` reference repair
- `scripts/components/slingshotmods.lua`
  - nested helper persist data via `GetPersistData()` and `SetPersistData(...)`
- `scripts/prefabs/player_common.lua`
  - special-case nested save records on players
- `scripts/prefabs/winona_battery_low.lua`
  - `OnLoadPostPass(...)` for post-load reconnection
- `scripts/components/timer.lua`
  - timer persistence plus `LongUpdate(dt)`
- `scripts/components/pickable.lua`
  - regrowth catch-up through `LongUpdate(dt)`

Read next:

- `references/patterns/persistence-patterns.md`
- `references/templates/persistence-templates.md`
- `references/patterns/diagnostic-patterns.md`

## Persistent String And Local Profile Storage Examples

- `scripts/mainfunctions.lua`
  - `SavePersistentString(...)` and `ErasePersistentString(...)` wrappers around `TheSim`
- `scripts/util/savedata.lua`
  - reusable persistent-file wrapper with dirty flag, load, save, and erase flow
- `scripts/generickv.lua`
  - simple key-value storage persisted through one file
- `scripts/craftingmenuprofile.lua`
  - local crafting UI preferences saved as JSON
- `scripts/plantregistrydata.lua`
  - larger local registry data saved with `DataDumper(...)`
- `scripts/skilltreedata.lua`
  - local profile progression data persisted outside one world save

Read next:

- `references/patterns/persistent-string-patterns.md`
- `references/patterns/persistence-patterns.md`
- `references/patterns/modinfo-patterns.md`

## Protected Call And Safe Decode Examples

- `scripts/craftingmenuprofile.lua`
  - `pcall(...)` around JSON decode for persistent local UI profile data
- `scripts/screens/modsscreen.lua`
  - `pcall(...)` around remote JSON decode
- `scripts/screens/multiplayermainscreen.lua`
  - `pcall(...)` around cached MOTD JSON decode
- `scripts/screens/redux/multiplayermainscreen.lua`
  - `pcall(...)` around stored JSON from generic KV
- `scripts/tools/getmissingstrings.lua`
  - `pcall(require, ...)` for optional speech files
- `scripts/screens/worldgenscreen.lua`
  - `xpcall(..., generic_error)` around JSON encode with fallback

Read next:

- `references/patterns/protected-call-patterns.md`
- `references/patterns/persistent-string-patterns.md`
- `references/patterns/diagnostic-patterns.md`

## Shard And Migration Examples

- `scripts/prefabs/world.lua`
  - `TheWorld.ismastershard` setup
- `scripts/prefabs/world_network.lua`
  - world-side shard client runtime
- `scripts/prefabs/shard_network.lua`
  - shard-side runtime aggregation object
- `scripts/components/worldmigrator.lua`
  - portal availability and migration activation
- `scripts/components/playerspawner.lua`
  - player migration save and spawn flow
- `scripts/components/recallmark.lua`
  - same-shard versus different-shard mark storage
- `scripts/components/shard_players.lua`
  - master-shard cluster player count aggregation
- `scripts/components/shardtransactionsteps.lua`
  - robust shard-to-shard transfer reference

Read next:

- `references/patterns/shard-patterns.md`
- `references/patterns/persistence-patterns.md`
- `references/patterns/networking-patterns.md`

## Worldgen And Preset Examples

- `scripts/map/rooms.lua`
  - room registration and duplicate-name behavior
- `scripts/map/tasks.lua`
  - task registration and duplicate-name behavior
- `scripts/map/tasksets.lua`
  - task set definitions
- `scripts/map/startlocations.lua`
  - start location registration and frontend refresh
- `scripts/map/customize.lua`
  - host-visible world customization items and categories
- `scripts/map/levels.lua`
  - preset ids, lists, and combined preset composition
- `scripts/screens/redux/servercreationscreen.lua`
  - host-facing world setup flow

Read next:

- `references/patterns/worldgen-patterns.md`
- `references/task-playbook.md`

## Text And Localization Examples

- `scripts/strings.lua`
  - global `STRINGS` tree shape
- `scripts/stringutil.lua`
  - runtime string lookup behavior
- `scripts/translator.lua`
  - `TranslateStringTable(...)`
- `scripts/languages/loc.lua`
  - official locale load and translate flow
- `scripts/modutil.lua`
  - mod-exposed `LoadPOFile(...)`

Read next:

- `references/patterns/string-patterns.md`
- `references/patterns/runtime-i18n-patterns.md`
- `references/patterns/modinfo-patterns.md`

## Practical Rule

- Use this page to pick the closest official starter file.
- Then switch to the narrower reference page for the real implementation rules.
- Do not read five official examples when one close example already matches the requested shape.
