# Entity Query Patterns

Use this file when scanning nearby entities or building AOE logic.

Also read `references/patterns/tag-patterns.md` when the query depends on prefab tags or action-filter tags.

## `TheSim:FindEntities`

- One of the highest-frequency runtime queries in official DST code.
- Observed official call shape:

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
```

- This is an observed call signature from official usage patterns because `TheSim` is engine-provided.

## Parameter Meaning

- `x, y, z`
  - world position to scan around
- `radius`
  - search radius in world units
- `musttags`
  - entity must have all tags in this list
- `canttags`
  - entity must have none of these tags
- `oneoftags`
  - entity must have at least one tag from this list

Practical rule:

- use `musttags` for strong identity filters
- use `canttags` to exclude common junk such as FX, dead targets, placeholders, or invalid interaction classes
- use `oneoftags` when several different target families are acceptable

## Common Call Shapes

```lua
TheSim:FindEntities(x, y, z, radius)
```

```lua
TheSim:FindEntities(x, y, z, radius, MUST_TAGS, CANT_TAGS)
```

```lua
TheSim:FindEntities(x, y, z, radius, nil, CANT_TAGS, ONE_OF_TAGS)
```

Observed official families:

- AOE hit scans
  - often `nil, CANT_TAGS, ONE_OF_TAGS`
- structure or station scans
  - often `MUST_TAGS, CANT_TAGS`
- family or nearby-count checks
  - often just `MUST_TAGS`
- raw occupancy or blocker checks
  - sometimes only radius, but usually on narrow radii

## Use Cases

- AOE damage or effects
- Nearby target selection
- Blocker checks
- Container or pickup search
- Proximity-based AI logic

Observed official file families:

- `scripts/brains/`
  - target search and utility search
- `scripts/stategraphs/`
  - AOE hit windows and attack-state queries
- `scripts/components/`
  - automation, pickup routing, spawn checks
- `scripts/prefabs/`
  - local gameplay rules and validation checks

## Prefer Simutil Helpers When The Shape Already Exists

Official `scripts/simutil.lua` wraps common query patterns:

- `FindEntity(inst, radius, fn, musttags, canttags, mustoneoftags)`
  - return the first matching visible entity
- `FindClosestEntity(inst, radius, ignoreheight, musttags, canttags, mustoneoftags, fn)`
  - return the closest matching visible entity
- `GetRandomInstWithTag(tag, inst, radius)`
  - simple random tagged entity query
- `GetClosestInstWithTag(tag, inst, radius)`
  - closest tagged entity shortcut

Use these when the helper already matches the needed behavior.
Do not re-hand-roll the same scan loop unless the task needs a materially different filter or ordering rule.

## Filtering Strategy

Official code usually combines tag-side narrowing with a final Lua predicate.

Typical pattern:

1. narrow candidates with `musttags`, `canttags`, and `oneoftags`
2. then apply gameplay-specific checks in Lua
3. only then perform the final effect, target pick, or count

Practical consequence:

- tag filtering is the first line of performance control
- Lua predicates should refine, not replace, tag filtering
- if a query is in an update loop, SG tick, or periodic task, narrow before iterating

## Intent Index

- "damage or affect nearby combat targets"
  - start from `canttags + oneoftags`
  - inspect a combat prefab or SG AOE example
- "find the closest valid target"
  - inspect `FindClosestEntity(...)` in `scripts/simutil.lua`
- "count nearby blockers or family members"
  - use a tight radius and `musttags`
- "search pickup items nearby"
  - inspect pickup-style `canttags` and one-of-tag filtering in `scripts/simutil.lua`
- "find all nearby structures or stations of one type"
  - start from `musttags`

## Performance Rules

- Prefer tight radius values.
- Prefer `musttags`, `canttags`, and `oneoftags` instead of broad scans.
- Do not put unfiltered scans in hot paths.
- If you are in `AddPrefabPostInitAny`, narrow aggressively before doing area scans.
- If a query only needs the closest match, use a closest-style helper or stop early.
- If the search runs repeatedly, avoid using "no tags at all" scans unless the radius is tiny and verified.
