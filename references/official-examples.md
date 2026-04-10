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
- `references/world-system-patterns.md`
- `references/animstate-patterns.md`

## Bootstrap And Registration Examples

- `scripts/mods.lua`
  - loader flow for mod environment setup, `modimport(...)`, `modmain.lua`, `PrefabFiles`, and mod-level `Assets`
- `scripts/modutil.lua`
  - registration APIs that `modmain.lua` usually calls
- `scripts/prefabs/staff.lua`
  - a grouped prefab-file family that shows what `PrefabFiles` can point at after bootstrap

Read next:

- `references/entrypoint-patterns.md`
- `references/modmain-patterns.md`
- `references/creation-patterns.md`

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

- `references/brain-patterns.md`
- `references/stategraph-patterns.md`
- `references/networking-patterns.md`

## Playable Character And Skill Tree Examples

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

Read next:

- `references/character-patterns.md`
- `references/runtime-i18n-patterns.md`
- `references/recipe-patterns.md`

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

- `references/effects-patterns.md`
- `references/tag-patterns.md`
- `references/asset-patterns.md`

## UI And Frontend Examples

- `scripts/widgets/controls.lua`
  - persistent HUD child ownership
- `scripts/screens/playerhud.lua`
  - player HUD lifecycle and screen-owned UI flow
- `scripts/widgets/containerwidget.lua`
  - container UI behavior
- `scripts/screens/redux/servercreationscreen.lua`
  - server setup screen flow
- `scripts/frontend.lua`
  - screen stack and frontend sound helpers

Read next:

- `references/ui-patterns.md`
- `references/input-patterns.md`
- `references/runtime-local-ui.md`

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

- `references/action-patterns.md`
- `references/stategraph-patterns.md`

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

- `references/networking-patterns.md`
- `references/networking-templates.md`
- `references/runtime-authority.md`

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

- `references/worldgen-patterns.md`
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

- `references/string-patterns.md`
- `references/runtime-i18n-patterns.md`
- `references/modinfo-patterns.md`

## Practical Rule

- Use this page to pick the closest official starter file.
- Then switch to the narrower reference page for the real implementation rules.
- Do not read five official examples when one close example already matches the requested shape.
