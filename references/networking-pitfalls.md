# Networking Pitfalls

Use this file when code crosses server/client boundaries.

## Client Uses `replica`, Server Uses `components`

- Server-authoritative state usually lives in `inst.components`.
- Client-side reads should usually come from `inst.replica` or netvars.
- Do not assume `inst.components.foo` is valid inside client-only branches.

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
