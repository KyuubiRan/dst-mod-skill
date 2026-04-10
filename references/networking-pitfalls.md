# Networking Pitfalls

Use this file when code crosses server/client boundaries.

## Client Uses `replica`, Server Uses `components`

- Server-authoritative state usually lives in `inst.components`.
- Client-side reads should usually come from `inst.replica` or netvars.
- Do not assume `inst.components.foo` is valid inside client-only branches.

Wrong shape:

```lua
if not TheWorld.ismastersim then
    local value = inst.components.mycomponent:GetValue()
end
```

Safer shape:

```lua
if not TheWorld.ismastersim then
    local value = inst.replica.mycomponent ~= nil and inst.replica.mycomponent:GetValue() or nil
end
```

If the component is mod-owned and clients need reads, also verify `AddReplicableComponent(...)` and the replica file.

## Do Not Copy Server Logic Into Client Branches

- Clients should usually:
  - read replica state
  - play local FX
  - update local UI
  - send RPC or input
- Servers should usually:
  - mutate authoritative components
  - spawn gameplay entities
  - change persistent world state

If the client needs to request a server change:

- send intent through action flow or RPC
- let the server mutate the real gameplay state
- then let clients observe via replica or netvars

## Prefab Initialization Needs A Clean Split

Many official prefabs use this order:

```lua
inst.entity:AddTransform()
inst.entity:AddAnimState()
inst.entity:AddNetwork()

inst.entity:SetPristine()

if not TheWorld.ismastersim then
    return inst
end

-- server-only components and logic
```

If this split is broken, replication bugs and nil access issues become more likely.

## Netvars Are Not Optional Decorations

Official prefabs frequently declare netvars before the master-sim split when clients need state such as:

- booleans
- small counters
- target entities
- dirty events for local presentation

Practical rule:

- if clients must react without reading server components, add the minimal netvar or replica shape
- keep the authoritative mutation on the server side

## Common Failure Shapes

- host sees it, remote client does not
  - missing replica, missing netvar, or client reads server components
- client sends intent but server never changes
  - wrong RPC direction or missing authoritative handler
- prefab exists on clients but nil-crashes after `SetPristine()`
  - server-only setup leaked into the client branch
- replicated shell exists but local presentation never updates
  - netvar dirty event or local listener is missing

## Fast Router

- if the task needs implementation shape, read `networking-templates.md`
- if the task is specifically about player-owned or owner-only player state, read `player-network-patterns.md`
- if the bug is mostly authority confusion, read `runtime-authority.md`
- if the bug is mostly symptom-driven, read `diagnostic-patterns.md`
