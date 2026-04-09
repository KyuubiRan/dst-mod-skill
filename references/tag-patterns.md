# Prefab Tag Patterns

Use this file when the task depends on prefab tags, action filters, AI targeting, search queries, collision flags, or helper entities that should or should not be interactable.

Tags in DST are often not just labels.
They are routing signals used by:

- action pickers
- AI and combat filters
- `FindEntities(...)` queries
- inventory and item filters
- collision or clickability rules
- world-system exclusion lists

Read this page together with the closest official prefab or component file.
If the task is specifically about lighting, visual FX prefabs, or sound helpers, also read `references/effects-patterns.md`.

## Two Sources Of Tags

### Prefab-Added Tags

These are explicitly added in prefab files with `inst:AddTag("...")`.

Typical examples:

- `structure`
- `backpack`
- `chest`
- `NOCLICK`
- `NOBLOCK`
- `FX`
- `projectile`
- `hostile`
- `monster`
- `companion`
- `smallcreature`
- `heavy`
- `plant`
- `bush`
- `renewable`
- `witherable`
- `show_spoilage`
- `irreplaceable`

### Component-Managed Tags

These are added or removed by component logic.

Verified in official component files:

- `inspectable`
  - added by `scripts/components/inspectable.lua`
- `weapon`
  - added by `scripts/components/weapon.lua`
- `pickable`
  - added by `scripts/components/pickable.lua`
- `barren`
  - managed by `scripts/components/pickable.lua`
- `quickpick`
  - managed by `scripts/components/pickable.lua`
- `jostlepick`
  - managed by `scripts/components/pickable.lua`
- `<ACTION>_workable`
  - managed by `scripts/components/workable.lua`, such as `DIG_workable` or `HAMMER_workable`
- `usesdepleted`
  - managed by `scripts/components/finiteuses.lua`

Practical rule:

- if a tag maps directly to a component state, do not add it manually unless the official pattern does
- if a tag is a prefab identity or routing hint, it usually belongs in the prefab constructor

## High-Frequency Manual Tags

### Interaction And Helper Entity Tags

- `NOCLICK`
  - common on FX, helper entities, reticules, visualizers, projectile helpers, and invisible logic prefabs
  - use when the entity should not be directly mouse-targetable
- `NOBLOCK`
  - common on helper entities, FX, herds, visual groups, and non-solid world entities
  - use when the entity should not block placement or movement
- `FX`
  - common on visual-only prefabs
  - usually appears together with `NOCLICK`, and sometimes also `NOBLOCK`

Observed official patterns:

- many FX prefabs add `FX` + `NOCLICK`
- ocean and boat helper prefabs often add `NOBLOCK`

### Structure And Storage Identity Tags

- `structure`
  - common on buildings, workstations, furnaces, altars, and chests
  - other systems often search or exclude by this tag
- `chest`
  - identity tag for chest-like structures
- `backpack`
  - common on wearable containers such as backpack-like items

Observed official patterns:

- `treasurechest.lua` adds `structure` and `chest`
- `backpack.lua`, `seedpouch.lua`, and `krampus_sack.lua` add `backpack`

### Combat And Creature Identity Tags

- `hostile`
  - marks hostile entities for many filters
- `monster`
  - common creature identity tag for hostile monsters
- `companion`
  - common for follower or ally-like entities
- `smallcreature`
  - used by some creature filters and interactions
- `projectile`
  - common on projectile entities or projectile-like temporary prefabs
- `heavy`
  - common on heavy-lift objects

Practical rule:

- combat and AI tags are often read by many systems, not just one prefab
- do not add creature identity tags casually without checking targeting and action side effects

### Resource And Plant Identity Tags

- `plant`
  - common on world plants
- `bush`
  - common on bush-type resources
- `renewable`
  - common on regrowable resources
- `witherable`
  - often paired with witherable logic or optimization assumptions

Observed official pattern:

- `berrybush.lua` adds `bush`, `plant`, `renewable`, `witherable`

### Item Routing Tags

- `show_spoilage`
  - common on items where spoilage UI should be shown
- `irreplaceable`
  - common on special quest, sign, pearl, or stash-like objects that should not be casually replaced by generic systems

Practical rule:

- these tags usually support higher-level systems or UI behavior
- use them when the item is expected to participate in an existing official pattern, not as decorative metadata

## Query-Side Internal Tags To Notice

Some tags show up mostly in filters and searches rather than obvious prefab `AddTag(...)` calls.
Treat these as query-side routing hints and verify them on a real official pattern before relying on them.

Observed in official component code:

- `_inventoryitem`
  - used in item search filters such as `nabbag.lua` and `aoeweapon_leap.lua`
- `_container`
  - used in exclusion filters
- `_combat`
  - used in some world-effect filtering

Inference:

- these internal-style tags are often more engine- or component-managed than prefab-authored
- if a mod depends on one of them, verify with the closest official file instead of assuming it appears automatically

## Intent Index

Use this as a quick tag checklist after choosing components.

- visual helper, reticule, projectile visualizer, placement ghost
  - think `FX`, `NOCLICK`, often `NOBLOCK`
- local light or sound helper
  - think `FX`, often `NOCLICK`
  - add `NOBLOCK` when it should not interfere with placement or movement
- chest or machine structure
  - think `structure`
  - add identity tags like `chest` only when it matches an official pattern
- wearable container
  - think `backpack`
- berry bush or plant resource
  - think `plant`, `bush`, `renewable`, often `witherable`
- hostile creature
  - think `monster`, `hostile`
- follower or ally creature
  - think `companion`
- weapon-like item
  - if it really owns a `weapon` component, the `weapon` tag is normally component-managed
- pickable world node
  - `pickable` is normally component-managed, not manually added
- hammerable or diggable target
  - rely on `workable` to manage `<ACTION>_workable` tags

## Example Bundles

These are expectation sketches, not mandatory bundles.

- weapon item
  - components: `inspectable`, `inventoryitem`, `weapon`, `equippable`, often `finiteuses`
  - tags to expect: component-managed `inspectable`, component-managed `weapon`
- backpack item
  - components: `inspectable`, `inventoryitem`, `equippable`, `container`
  - tags to expect: prefab-added `backpack`
- chest structure
  - components: `inspectable`, `container`, often `workable`
  - tags to expect: prefab-added `structure`, prefab-added `chest`
- berry bush
  - components: `pickable`, `inspectable`, often `workable`
  - tags to expect: prefab-added `plant`, `bush`, `renewable`, `witherable`, component-managed `pickable`
- FX helper
  - components: often none or only minimal helpers
  - tags to expect: prefab-added `FX`, `NOCLICK`, often `NOBLOCK`

## Common Pitfalls

- Do not manually add component-owned tags such as `inspectable`, `weapon`, or `pickable` when the component already manages them.
- Do not add `hostile`, `monster`, or `companion` casually; many unrelated systems filter on them.
- Do not use `NOCLICK` on something the player is meant to target directly.
- Do not assume a query-side internal tag such as `_inventoryitem` is safe to depend on without checking an official pattern.
- Tags are not a replacement for components; a `weapon` tag alone does not make an item deal weapon damage.

## Rule Of Thumb

- Choose components first.
- Add identity and routing tags second.
- Verify whether a tag is prefab-authored or component-managed before adding it by hand.
- If a feature depends on searches, AI, or action filters, inspect both the producer of the tag and the code that consumes it.
