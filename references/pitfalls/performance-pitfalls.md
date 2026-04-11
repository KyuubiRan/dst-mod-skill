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

Common expensive shape:

```lua
inst:DoPeriodicTask(FRAMES, function()
    local ents = TheSim:FindEntities(x, y, z, 30)
end)
```

Safer shape:

```lua
inst:DoPeriodicTask(period, function()
    local ents = TheSim:FindEntities(x, y, z, radius, MUST_TAGS, CANT_TAGS, ONE_OF_TAGS)
end)
```

Then keep `period`, `radius`, and tag filtering as tight as the feature allows.

## `AddPrefabPostInitAny` Can Become A Trap

- It runs for every spawned prefab.
- Narrow immediately with cheap checks such as tags or prefab names.
- Use `AddPrefabPostInit` when a single prefab family is enough.

Common expensive shape:

```lua
AddPrefabPostInitAny(function(inst)
    -- heavy work for everything
end)
```

Safer shape:

```lua
AddPrefabPostInitAny(function(inst)
    if inst.prefab ~= "target_prefab" then
        return
    end
    -- narrow work
end)
```

## Periodic Tasks Need Justification

Official DST uses many `DoPeriodicTask(...)` loops, but usually with one or more of these constraints:

- narrow ownership
- coarse update interval
- small-radius queries
- cheap early exits

Practical rule:

- if a task runs every frame or every few frames, assume it is performance-sensitive
- if the task scans the world, prove the radius and filter are tight
- if the behavior can be event-driven, prefer that over polling

## Fast Router

- if the issue is broad area scanning, read `references/patterns/entity-query-patterns.md`
- if the issue is over-broad hook choice, inspect `references/mod-api-map.md`
- if the issue is really authority or local UI confusion, do not blame performance first
