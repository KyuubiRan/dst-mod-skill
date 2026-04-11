# Networking Patterns

Use this file when the task needs RPC, client-readable replicated state, classified entities, or netvars.
Use `references/templates/networking-templates.md` when the task has already been classified and now needs the smallest practical implementation shape.
Use `references/patterns/runtime-authority.md` too when the real confusion is "which side owns this mutation?"
Use `references/patterns/player-network-patterns.md` too when the task is specifically about player-owned state, `player_classified`, or owner-only HUD data.
Use `references/patterns/shard-patterns.md` too when the task crosses Master/Caves boundaries or needs shard-aware migration or shard RPC.

## Decide The Lowest Necessary Networking Tool

Use the simplest tool that matches the need:

- server-only behavior
  - no extra networking
- client needs read-only state
  - replica and netvars
- client needs private or structured replicated state
  - classified pattern
- player owner-only HUD, controller, or grouped status data
  - player-classified-style pattern
- client needs to request an authoritative action
  - mod RPC or an existing action flow
- data must cross shard boundaries at runtime
  - shard pattern or shard mod RPC

Fast router:

- one or two replicated booleans, counters, or compact values
  - netvars
- clean client API for a custom component
  - replica component plus netvars
- owner-scoped or structured state with attach/detach lifecycle
  - classified
- local input or UI asks the server to do something
  - action flow or mod RPC
- feature crosses shard boundaries
  - `references/patterns/shard-patterns.md`

## Mod RPC Registration

Register handlers in `modmain.lua`:

```lua
AddModRPCHandler("mynamespace", "dosomething", function(player, ...)
    -- server-side handler
end)

AddClientModRPCHandler("mynamespace", "showthing", function(...)
    -- client-side handler
end)
```

Official mod environment helpers also expose:

```lua
GetModRPC("mynamespace", "dosomething")
GetClientModRPC("mynamespace", "showthing")
SendModRPCToServer(id_table, ...)
SendModRPCToClient(id_table, ...)
```

Practical send shape:

```lua
SendModRPCToServer(GetModRPC("mynamespace", "dosomething"), ...)
```

## Netvars

Official prefabs commonly define netvars on the entity itself:

```lua
inst._enabled = net_bool(inst.GUID, "myprefab._enabled", "enableddirty")
inst._level = net_byte(inst.GUID, "myprefab._level")
inst._state = net_smallbyte(inst.GUID, "myprefab._state", "statedirty")
```

Observed common netvar families:

- `net_bool`
- `net_byte`
- `net_tinybyte`
- `net_smallbyte`

Practical rule:

- define netvars before or around the pristine split as needed by the prefab pattern you are following
- listen for dirty events on the client side when presentation must react

Common correct shape:

1. declare netvars before the master-sim return
2. `SetPristine()`
3. client dirty listeners or client-only setup
4. server writes values authoritatively

## Replica Components

If a component must be readable on clients, plan for a replica-side partner.

Observed official pattern:

- server component file:
  - `components/mycomponent.lua`
- replica component file:
  - `components/mycomponent_replica.lua`
- registration:

```lua
AddReplicableComponent("mycomponent")
```

Official replica loading path comes from `EntityScript:ReplicateComponent(name)`, which loads:

```lua
require("components/" .. name .. "_replica")
```

Practical consequence:

- do not read `inst.components.mycomponent` on clients
- use `inst.replica.mycomponent` or the relevant classified/netvar path

Observed official replica trigger:

- `EntityScript:AddComponent(name)` calls `self:ReplicateComponent(name)`
- `EntityScript:ReplicateComponent(name)` loads `components/<name>_replica.lua` when the component is marked replicable

Practical rule:

- a custom replica is not only a file-placement convention
- it must also be reachable through the replicable registration path

## Classified Pattern

Classified entities are used when clients need replicated data that should be attached or exposed in a controlled way.

Observed official inventory pattern:

- server or owning side creates a classified prefab
- it is parented to the main entity
- replica attaches through `AttachClassified(classified)`
- netvars live on the classified entity
- dirty events update local presentation

This is a stronger pattern than a single bare netvar and is useful when:

- many related fields travel together
- ownership or visibility matters
- the client-side API should be wrapped cleanly

Use classified when the state has its own lifecycle:

- attach on spawn or ownership
- listen for dirty events
- detach on removal or ownership loss

If the state is only one or two plain values, classified is usually too heavy.

## `OnEntityReplicated`

Official replica flow calls `inst:OnEntityReplicated()` after replica setup when defined.

Use this hook when client-side setup must happen only after replica components are available.

This is often the right place for:

- replica-dependent event hookup
- client-only cached references that rely on replica existence
- UI/local presentation setup that should not run before replica attachment

## Preferred Order

1. decide whether the client truly needs local state or only a request path
2. if the client only sends intent, prefer an existing action flow or mod RPC
3. if the client needs reads, prefer replica/netvar patterns
4. use classified when the state is more complex or scoped

## Common Failure Points

- wrote a custom replica file but never called `AddReplicableComponent(...)`
- client reads `inst.components` instead of `inst.replica`
- used RPC for state that should really be replicated afterward
- built a classified entity when one netvar would have been enough
- forgot dirty listeners or attach/detach flow on the client side

## Rule Of Thumb

- Use RPC for intent.
- Use netvars for replicated state.
- Use replica components for client-side reads.
- Use classified entities when the replicated state needs structure, attachment, or controlled exposure.
