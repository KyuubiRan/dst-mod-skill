# Runtime Authority

Use this file when deciding which side owns logic.

## Core Checks

- `TheWorld.ismastersim`
  - High-frequency authority gate.
  - Common official pattern:
    ```lua
    if not TheWorld.ismastersim then
        return inst
    end
    ```
  - Use to keep authoritative components, tasks, and gameplay mutations off clients.
- `TheNet:IsDedicated()`
  - Process-type check for dedicated servers with no local frontend.
- `TheNet:GetIsServer()`
  - Process is acting as a server.

## Distinction

- `TheWorld.ismastersim`
  - Is this Lua context the authoritative world simulation?
- `TheNet:IsDedicated()`
  - Is this process a dedicated server with no local player UI?

Do not use one as a replacement for the other.

## Common Split Pattern

Observed high-frequency official prefab shape:

```lua
inst.entity:SetPristine()

if not TheWorld.ismastersim then
    return inst
end
```

Use this when:

- clients need the networked shell and visuals
- only the master sim should add authoritative components, tasks, or mutations

This is different from:

```lua
if not TheNet:IsDedicated() then
    -- local-only visual, sound, or UI path
end
```

That branch is about process-local presentation, not simulation authority.

## World-Level Runtime

- `TheWorld.state`
  - Read world-state flags such as wetness and seasonal state.
- `TheWorld:PushEvent(event, data)`
  - World-scoped event dispatch.
- `TheWorld.Map`
  - Reach for map, tile, deploy, and spacing logic here.

## Practical Routing

- add components, run combat logic, mutate inventory, change real gameplay state
  - gate with `TheWorld.ismastersim`
- spawn local-only presentation, use HUD, or touch screens
  - gate with `not TheNet:IsDedicated()`
- listen to replicated world state
  - read `TheWorld.state`
- do map, tile, or placement checks
  - inspect `TheWorld.Map`

## `GetIsServer()` Versus `ismastersim`

Use `TheNet:GetIsServer()` when the question is about the process role.
Use `TheWorld.ismastersim` when the question is about whether this Lua context owns gameplay authority.

Practical rule:

- entity prefab construction usually cares about `TheWorld.ismastersim`
- frontend or cluster-level branching may care about `TheNet:GetIsServer()`

## Common Patterns

### Server-authoritative prefab logic

```lua
if not TheWorld.ismastersim then
    return inst
end
```

### Dedicated-server-safe local branch

```lua
if not TheNet:IsDedicated() then
    -- local visuals, screen, or HUD work
end
```

### Listen server mixed path

```lua
if not TheNet:IsDedicated() then
    -- host-local presentation
end

if not TheWorld.ismastersim then
    return inst
end

-- authoritative gameplay logic
```

This shape matters because a listen server can have both local presentation and server authority in the same process.

## Common Failure Points

- using `ThePlayer` or HUD logic just because the process is master sim
- treating `TheNet:IsDedicated()` as if it were a gameplay-authority check
- putting authoritative components before the normal `SetPristine()` and master-sim split
- forgetting that a listen server may execute both local UI and authoritative gameplay branches
