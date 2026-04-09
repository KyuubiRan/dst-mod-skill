# Execution Contexts

Use this file when deciding whether a mod is all-clients gameplay, client-only, or server-only.

## The Three Common Mod Shapes

### All-Clients Gameplay Mod

Use this when:

- The mod adds gameplay entities, components, recipes, actions, RPC, or anything that affects shared simulation.
- Clients must understand the same content definitions or net behavior as the server.

Common `modinfo.lua` shape:

```lua
dst_compatible = true
client_only_mod = false
all_clients_require_mod = true
```

Typical code shape:

- Shared prefab/network declarations before `SetPristine()`
- Early `if not TheWorld.ismastersim then return inst end`
- Server-only components and logic after that
- Client-side reads through replica or netvars where needed

### Client-Only Mod

Use this when:

- The mod is UI, QoL, local overlays, local controls, local indicators, or other client-local behavior.
- The server does not need the mod to understand gameplay state.

Common `modinfo.lua` shape:

```lua
dst_compatible = true
client_only_mod = true
all_clients_require_mod = false
```

Typical code shape:

- Heavy use of `ThePlayer`, HUD, widgets, and local screens
- Guard dedicated-server paths aggressively
- Avoid server-authoritative gameplay mutations

### Server-Only Mod

Use this when:

- The mod should run on the server and affect the world or server automation, but clients do not need the mod installed.
- The mod does not require clients to load custom gameplay definitions that the server expects the client to know about.

Common `modinfo.lua` shape:

```lua
dst_compatible = true
client_only_mod = false
all_clients_require_mod = false
```

Typical code shape:

- Focus on server simulation and server automation
- Avoid local-player HUD assumptions
- Be careful with custom actions, custom widgets, or client-side presentation that would require client install

## Decision Rule

Ask these questions:

1. Does the client need to know about new prefab, action, widget, recipe, or replica behavior?
2. Is the feature purely local UI or QoL?
3. Can the server run the feature alone without clients understanding any new game content?

If the feature changes shared gameplay definitions, default toward all-clients gameplay.
If the feature is purely local visual or input behavior, default toward client-only.
If the feature is administrative, automation, or pure server logic, consider server-only.

## Runtime Consequences

### All-Clients Gameplay

- Both client and server paths matter.
- Replica and netvars matter.
- `TheWorld.ismastersim` splits authoritative logic from client display logic.

### Client-Only

- `ThePlayer`, `TheFrontEnd`, HUD, widgets, and local input patterns matter more.
- `TheNet:IsDedicated()` guards are important.
- Do not rely on server-only components being present locally.

### Server-Only

- Avoid `ThePlayer` and HUD assumptions.
- `TheWorld.ismastersim` is usually central.
- Dedicated servers are the main target context.

## Bootstrap Guidance

When creating a new mod, ask the user which of these three shapes they want before generating `modinfo.lua`.
If they are unsure:

- Recommend all-clients gameplay for content mods.
- Recommend client-only for UI or personal QoL mods.
- Recommend server-only for automation, balance enforcement, or admin helpers that do not need client install.
