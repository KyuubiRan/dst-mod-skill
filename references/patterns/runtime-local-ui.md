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

Typical good uses:

- local HUD reactions
- local-only inspect helpers
- local input reactions
- "if this entity is my local player" checks

Typical bad uses:

- choosing the gameplay target in generic server logic
- replacing callback parameters such as `doer`, `giver`, `owner`, or `attacker`

## `TheFrontEnd`

- UI and screen management.
- Relevant to frontend and client-facing flows.
- Guard it away from dedicated-server-only paths.

Observed common uses:

- `TheFrontEnd:PushScreen(...)`
- `TheFrontEnd:PopScreen()`
- `TheFrontEnd:GetActiveScreen()`
- `TheFrontEnd:GetSound():PlaySound(...)`

Use `TheFrontEnd` for screen-stack and frontend sound behavior, not normal gameplay authority.

## Local HUD Reality

`ThePlayer` and `ThePlayer.HUD` are related but not interchangeable.

Practical rule:

- `ThePlayer ~= nil`
  - local player exists
- `ThePlayer.HUD ~= nil`
  - HUD-side UI is actually available

If the task touches event announcers, inventory bar widgets, or open screens, guard the HUD explicitly.

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

## Intent Index

- "show a local screen or popup"
  - start from `TheFrontEnd`
- "touch the local HUD"
  - guard `ThePlayer ~= nil and ThePlayer.HUD ~= nil`
- "play UI sound"
  - inspect `TheFrontEnd:GetSound()`
- "check whether this entity is me"
  - compare with `ThePlayer`
- "do something for the actor who triggered gameplay"
  - use callback parameters, not `ThePlayer`

## Common Mistake

- Wrong:
  - using `ThePlayer` inside generic server logic because the process is master sim
- Right:
  - use callback parameters such as `inst`, `doer`, `owner`, `giver`, or `attacker`
  - use `ThePlayer` only for local-player-specific behavior
