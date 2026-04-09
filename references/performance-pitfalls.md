# Performance Pitfalls

Use this file for hot-path and broad-hook mistakes.

## `TheSim:FindEntities` Can Get Expensive Fast

- Use small radius values.
- Use tag filters aggressively.
- Avoid broad scans in periodic tasks or widely-triggered hooks.

Observed usage shape:

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
```

## `AddPrefabPostInitAny` Can Become A Trap

- It runs for every spawned prefab.
- Narrow immediately with cheap checks such as tags or prefab names.
- Use `AddPrefabPostInit` when a single prefab family is enough.
