# Entity Query Patterns

Use this file when scanning nearby entities or building AOE logic.

## `TheSim:FindEntities`

- One of the highest-frequency runtime queries in official DST code.
- Observed official call shape:

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
```

- This is an observed call signature from official usage patterns because `TheSim` is engine-provided.

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

## Use Cases

- AOE damage or effects
- Nearby target selection
- Blocker checks
- Container or pickup search
- Proximity-based AI logic

## Performance Rules

- Prefer tight radius values.
- Prefer `musttags`, `canttags`, and `oneoftags` instead of broad scans.
- Do not put unfiltered scans in hot paths.
- If you are in `AddPrefabPostInitAny`, narrow aggressively before doing area scans.
