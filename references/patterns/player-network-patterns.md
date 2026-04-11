# Player Network Patterns

Use this file when a task needs player-specific replicated state, owner-scoped HUD data, `player_classified`, or player-side replica setup.

If the task is only "apply this to every player", read `references/patterns/player-patterns.md` first.
If the task is generic RPC, netvar, or replica design, also read `references/patterns/networking-patterns.md`.

## Fast Router

- one or two small player values that all relevant clients may read
  - put netvars on the player entity
- player feature should expose a clean client API such as `inst.replica.<name>`
  - use a replica component, with netvars on the player or a classified child
- owner-only or grouped player state for HUD, controller, or camera logic
  - use a classified child pattern
- purely local UI state with no authoritative meaning
  - keep it local and do not network it
- client wants to ask the server to mutate player state
  - use action flow or RPC, then replicate the result back

## Official Player Flow

Observed in `scripts/prefabs/player_common.lua`, `scripts/prefabs/player_classified.lua`, and `scripts/entityreplica.lua`:

- the master sim spawns `player_classified` and parents it to the player
- after the user id is assigned, `player_common.lua` calls `inst.player_classified.Network:SetClassifiedTarget(inst)`
- `player_classified.lua` defines many player-specific netvars on the classified entity itself
- `player_classified.lua` calls `SetPristine()` and assigns `inst.OnEntityReplicated = OnEntityReplicated` on clients
- `EntityScript:ReplicateEntity()` calls `OnEntityReplicated()` after replica components have already been created
- `player_classified:OnEntityReplicated()` attaches itself back to the parent player and then routes the same classified into selected replica or player-side components

Practical consequence:

- do not assume `inst.player_classified` exists at the earliest client construction point
- if client setup depends on replica or classified data, wait until replication is ready
- `OnEntityReplicated()` is the safe point for classified-dependent client wiring

## Choose Between Main-Entity Netvars, Replica, And Classified

### Main-Entity Netvars

Use this when:

- the state is small
- the state belongs naturally to the player entity itself
- all nearby clients may read it

Good fits:

- a compact mode flag
- a tiny counter
- one public boolean or byte-sized state

Avoid it when:

- the data should only be readable by the owning player
- several related values and dirty events travel together
- the feature wants attach or detach lifecycle

### Replica Component

Use this when:

- the feature should read through `inst.replica.<name>`
- the state is conceptually a component, not just a loose field
- the client needs helper methods rather than direct netvar access

Observed official shape:

- `EntityScript:ReplicateComponent(name)` loads `components/<name>_replica.lua`
- `AddReplicableComponent(name)` extends the allowed replica set for mod-owned components
- player replica components such as `sanity_replica` still attach to `player_classified`

Practical consequence:

- replica and classified are often complementary, not competing
- a player replica can expose the client API while the actual netvars live on a classified child

### Classified Child

Use this when:

- the state is owner-scoped
- multiple related values belong together
- the client side needs attach, detach, or dirty-event orchestration
- local HUD, action visibility, camera, or controller code should react to authoritative player data

Observed official shape:

- `player_common.lua` owns `AttachClassified`, `DetachClassified`, and cleanup
- `player_classified.lua` attaches itself to selected player replica components
- `inventory_replica.lua` and `sanity_replica.lua` listen for dirty events and detach on removal

Practical consequence:

- this is the right pattern for grouped player status, owner-only HUD state, or inventory-like client presentation
- if you only need one public bool, classified is too heavy

## Owner-Scoped Data

Observed official behavior:

- `player_common.lua` gives the owning player access to `player_classified` through `Network:SetClassifiedTarget(inst)`
- `inventory_replica.lua` toggles classified access and visibility with `Network:SetClassifiedTarget(...)` plus dirty events

Practical rule:

- if only the owning player should read the data, prefer a classified target pattern
- if every client may read the same value, prefer ordinary player netvars

## Recommended Mod Pattern

Prefer this escalation path:

1. small public player state
   - player netvar
2. player feature with a clean client API
   - mod-owned server component plus replica component
3. owner-only or structured player state
   - mod-owned classified child, optionally attached through a replica component

Patch the official `player_classified` path only when the feature truly belongs on players as a class and you understand its attach lifecycle.

## Common Failure Points

- trying to read `inst.player_classified` on clients before it attaches
- reading `inst.components` on clients instead of `inst.replica` or classified data
- using a classified child for one small public value
- forgetting dirty listeners when client presentation should react
- forgetting detach and cleanup on removal
- using player-classified patterns for a non-player prefab that only needed ordinary netvars

## Quick Examples

- owner-only custom stamina bar
  - player classified style
- public combo counter visible to nearby clients
  - player netvar or replica plus netvar
- player-owned system with several HUD helpers
  - component plus replica plus classified
