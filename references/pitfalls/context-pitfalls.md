# Context Pitfalls

Use this file for server/client/local-player context mistakes.

## Do Not Rebind Engine Globals

- `GLOBAL`, `TheSim`, `TheNet`, `TheShard`, `TheInput`, `TheFrontEnd`, `TheMixer`, `TheCamera`, `TheFocalPoint`, `TheWorld`, `ThePlayer`, and `AllPlayers` are engine-owned globals.
- Read them, call their APIs, and guard their availability when needed.
- Do not overwrite them, replace them with a table, or redefine them to mean something else.
- A local passthrough alias that keeps the same value is fine, for example `local GLOBAL = GLOBAL`.
- `TheWorld` and `ThePlayer` are entity references, so world- or player-owned fields may live on the entity. Do not replace the global binding itself.
- Shared registries such as `TUNING`, `STRINGS`, `ACTIONS`, and mod RPC registries may be extended narrowly, but do not replace the entire table.

Wrong shape:

```lua
TheWorld = {}
local ThePlayer = inst
TheSim = nil
TUNING = {}
STRINGS = {}
RPC = {}
```

Safer shape:

```lua
local player = inst

TUNING.MYMOD_SPEED = 6
STRINGS.NAMES.MYMOD_ITEM = "My Item"

if ThePlayer ~= nil and player == ThePlayer then
    -- local-player-specific logic
end
```

## `ThePlayer` Is Not A Generic Player Handle

- `ThePlayer` is local-process player state.
- It is often present on clients and listen hosts.
- It is usually `nil` on dedicated servers.
- Do not treat `TheWorld.ismastersim` as proof that `ThePlayer` exists.

Safe guard:

```lua
if ThePlayer ~= nil and ThePlayer.HUD ~= nil then
    -- local-player UI logic
end
```

Wrong shape:

```lua
local target = ThePlayer
```

Safer shape:

```lua
local target = doer or owner or inst
```

Then use `ThePlayer` only if the behavior is intentionally local-player-specific.

## `ThePlayer` Is Not The Same As `doer` Or `owner`

- In gameplay callbacks, use actual callback parameters such as `inst`, `doer`, `owner`, `giver`, or `attacker`.
- Only use `ThePlayer` when the behavior is intentionally local-player-specific.

## `TheWorld.ismastersim` And `TheNet:IsDedicated()` Are Different

- `TheWorld.ismastersim`
  - authoritative world simulation
- `TheNet:IsDedicated()`
  - process has no local frontend

Both checks matter, but for different reasons.

Wrong shape:

```lua
if TheWorld.ismastersim then
    -- assume HUD or ThePlayer exists
end
```

Safer shape:

```lua
if not TheNet:IsDedicated() then
    -- local presentation path
end
```

```lua
if not TheWorld.ismastersim then
    return inst
end
```

## Listen Host Confusion

A listen server can be:

- authoritative simulation
- a local player process
- a frontend/UI process

At the same time.

That means code can accidentally appear to work on host while still being wrong for:

- remote clients
- dedicated servers
- pure client-local UI flows

## Fast Router

- if the bug is "works on host but not on remote client"
  - read `references/pitfalls/networking-pitfalls.md`
- if the bug is "works on host but crashes on dedicated"
  - read `references/patterns/runtime-local-ui.md`
- if the bug is "I used `ThePlayer` where gameplay passed me `doer`"
  - fix callback ownership first
