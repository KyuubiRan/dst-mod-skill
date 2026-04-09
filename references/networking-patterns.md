# Networking Patterns

Use this file when the task needs RPC, client-readable replicated state, classified entities, or netvars.

## Decide The Lowest Necessary Networking Tool

Use the simplest tool that matches the need:

- server-only behavior
  - no extra networking
- client needs read-only state
  - replica and netvars
- client needs private or structured replicated state
  - classified pattern
- client needs to request an authoritative action
  - mod RPC or an existing action flow

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

## `OnEntityReplicated`

Official replica flow calls `inst:OnEntityReplicated()` after replica setup when defined.

Use this hook when client-side setup must happen only after replica components are available.

## Preferred Order

1. decide whether the client truly needs local state or only a request path
2. if the client only sends intent, prefer an existing action flow or mod RPC
3. if the client needs reads, prefer replica/netvar patterns
4. use classified when the state is more complex or scoped

## Rule Of Thumb

- Use RPC for intent.
- Use netvars for replicated state.
- Use replica components for client-side reads.
- Use classified entities when the replicated state needs structure, attachment, or controlled exposure.
