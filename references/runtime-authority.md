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

## World-Level Runtime

- `TheWorld.state`
  - Read world-state flags such as wetness and seasonal state.
- `TheWorld:PushEvent(event, data)`
  - World-scoped event dispatch.
- `TheWorld.Map`
  - Reach for map, tile, deploy, and spacing logic here.

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
