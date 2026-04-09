# Context Pitfalls

Use this file for server/client/local-player context mistakes.

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

## `ThePlayer` Is Not The Same As `doer` Or `owner`

- In gameplay callbacks, use actual callback parameters such as `inst`, `doer`, `owner`, `giver`, or `attacker`.
- Only use `ThePlayer` when the behavior is intentionally local-player-specific.

## `TheWorld.ismastersim` And `TheNet:IsDedicated()` Are Different

- `TheWorld.ismastersim`
  - authoritative world simulation
- `TheNet:IsDedicated()`
  - process has no local frontend

Both checks matter, but for different reasons.
