# Networking Templates

Use this file when a task needs practical server/client templates rather than only networking concepts.

This page complements `references/networking-patterns.md`.
Read that file first for the decision framework, then use this file for implementation shapes.
If the target is player-owned owner-only state, also read `references/player-network-patterns.md`.

## Choose The Smallest Template That Fits

- server-only gameplay change
  - no extra networking
- client needs one or two replicated fields
  - netvars on the entity
- client needs a replica API for reads
  - server component + replica component + optional netvars
- client needs structured or scoped replicated state
  - classified entity pattern
- player owner-only HUD, controller, or grouped status data
  - player-classified-style pattern
- client needs to request an authoritative action
  - action flow or mod RPC

## Template: Bare Netvar On The Main Entity

Use this when the client only needs a small amount of replicated state.

```lua
local function OnEnabledDirty(inst)
    if inst._enabled:value() then
        -- client presentation update
    end
end

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddNetwork()

    inst._enabled = net_bool(inst.GUID, "my_prefab._enabled", "enableddirty")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        inst:ListenForEvent("enableddirty", OnEnabledDirty)
        return inst
    end

    inst._enabled:set(false)

    return inst
end
```

Observed official pattern:

- many prefabs define `net_bool`, `net_byte`, `net_smallbyte`, `net_float`, or `net_entity` directly on `inst`

Use it for:

- small replicated booleans
- simple counters or compact states
- visual presentation updates

Keep the order intact:

1. create networked entity pieces
2. declare netvars
3. `SetPristine()`
4. client listener branch
5. server-authoritative writes

## Template: Server Component Plus Replica Component

Use this when the client should read through `inst.replica.<name>` instead of touching server components.

Server side:

```lua
-- scripts/components/mycomponent.lua
local MyComponent = Class(function(self, inst)
    self.inst = inst
end)

return MyComponent
```

Replica side:

```lua
-- scripts/components/mycomponent_replica.lua
local MyComponent = Class(function(self, inst)
    self.inst = inst
end)

function MyComponent:IsEnabled()
    return self.inst._enabled ~= nil and self.inst._enabled:value()
end

return MyComponent
```

Registration:

```lua
AddReplicableComponent("mycomponent")
```

Practical rule:

- server writes go through `inst.components.mycomponent`
- client reads go through `inst.replica.mycomponent`
- replicated fields still usually live on `inst` or a classified child as netvars

Do not stop after creating the replica file.
You still need `AddReplicableComponent("mycomponent")`.

## Template: Classified Entity

Use this when:

- many related fields travel together
- visibility or ownership matters
- the client API should be attached and detached cleanly

Observed official references:

- `scripts/components/inventory_replica.lua`
- `scripts/prefabs/player_common.lua`

Observed official flow:

1. server or owner creates a classified prefab
2. classified entity is parented to the main entity
3. main entity stores or attaches the classified reference
4. client replica calls `AttachClassified(classified)`
5. dirty events and local UI update from classified netvars
6. detach and cleanup happen on removal

Official example details:

- `player_common.lua`
  - attaches and detaches `player_classified`
- `inventory_replica.lua`
  - `AttachClassified(classified)`
  - listens for dirty events such as `visibledirty`
  - toggles visibility with `Network:SetClassifiedTarget(...)`

Practical rule:

- choose this only when bare entity netvars would become messy
- classified is especially useful for inventory-like or owner-scoped state

Typical warning sign that classified is warranted:

- the state wants attach, detach, ownership, and multiple related dirty events

## Template: `OnEntityReplicated`

Use this when client-side setup must happen after replica components exist.

```lua
function inst:OnEntityReplicated()
    -- client-only setup that needs replica availability
end
```

Use it for:

- post-replica initialization
- client-side hook setup that depends on replica components

## Template: RPC For Intent

Use RPC when the client must request an authoritative action, not when it only needs to read state.

```lua
AddModRPCHandler("my_mod", "do_thing", function(player, ...)
    -- server-side authoritative logic
end)

local function SendThing(...)
    SendModRPCToServer(GetModRPC("my_mod", "do_thing"), ...)
end
```

Practical rule:

- RPC carries intent
- replicated state still needs netvars, replica, or classified if clients must read it later

If a built-in world action already gives you the right authority and prediction path, prefer that over inventing a new RPC route.

## Common Pitfalls

- Do not read `inst.components.foo` on clients.
- Do not use RPC where a normal action flow would already give you authority and prediction.
- Do not build a classified entity when one or two plain netvars would be enough.
- Do not forget dirty listeners on the client if presentation must react.
- Do not forget detach and cleanup when using classified patterns.

## Rule Of Thumb

- One or two fields: use netvars.
- Client API for reads: add replica.
- Structured owner-scoped state: use classified.
- Client request path: use action flow or RPC.
