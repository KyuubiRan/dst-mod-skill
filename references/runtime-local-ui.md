# Runtime Local UI

Use this file when code touches local player state, HUD, widgets, or screens.

## `ThePlayer`

- Local player reference.
- Commonly exists on clients and on the local host process of a listen server.
- Usually `nil` on dedicated servers.
- Safe uses are intentionally local:
  - `if inst == ThePlayer then ... end`
  - `if ThePlayer ~= nil and ThePlayer.HUD ~= nil then ... end`

Do not use `ThePlayer` as a generic gameplay owner or doer.

## `TheFrontEnd`

- UI and screen management.
- Relevant to frontend and client-facing flows.
- Guard it away from dedicated-server-only paths.

## Safe Local Guards

```lua
if ThePlayer ~= nil and ThePlayer.HUD ~= nil then
    -- local HUD logic
end
```

```lua
if not TheNet:IsDedicated() then
    -- local-only visuals or screen logic
end
```

## Common Mistake

- Wrong:
  - using `ThePlayer` inside generic server logic because the process is master sim
- Right:
  - use callback parameters such as `inst`, `doer`, `owner`, `giver`, or `attacker`
  - use `ThePlayer` only for local-player-specific behavior
