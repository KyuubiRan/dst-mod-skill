# Shard Patterns

Use this file when the task touches Master/Caves runtime boundaries, shard-aware positions, player or item migration, cluster-wide shard state, or shard mod RPC.

If the task is really about world generation or host setup, read `references/worldgen-patterns.md` instead.
If the task is ordinary client/server replication on one shard, read `references/networking-patterns.md` instead.

## Core Checks

Observed official runtime checks:

- `TheShard:GetShardId()`
- `TheShard:IsMaster()`
- `TheShard:IsSecondary()`
- `TheWorld.ismastershard`
- `Shard_IsWorldAvailable(worldid)`
- `Shard_IsWorldFull(worldid)`

Observed in `scripts/prefabs/world.lua`:

- `TheWorld.ismastershard = inst.ismastersim and not TheShard:IsSecondary()`

Practical consequence:

- `TheWorld.ismastersim` is not enough when the logic only belongs on the master shard
- cross-shard routing usually needs a `worldid`, not just a position

## Fast Router

- only need to know whether stored data belongs to this shard
  - store and compare `worldid` with `TheShard:GetShardId()`
- need a portal, staircase, or recall destination that may cross shards
  - inspect `worldmigrator`, `recallmark`, and `Shard_IsWorldAvailable(...)`
- need cluster totals, not just current-shard counts
  - inspect master-shard aggregation patterns
- need data to move from one shard to another at runtime
  - prefer shard mod RPC or an existing migration flow
- need durable cross-shard transfer that survives shard reconnect or save timing
  - inspect `shardtransactionsteps.lua` before inventing a custom protocol

## Runtime World Split

Observed in official prefabs:

- `scripts/prefabs/world_network.lua`
  - networked world-side classified object
- `scripts/prefabs/shard_network.lua`
  - master-sim shard-side classified object

Observed official shape:

- `world_network.lua` adds `AddShardClient()` and world-side components such as `clock`, `seasons`, and `worldreset`
- `shard_network.lua` adds `AddShardNetwork()` and shard components such as `shard_players`, `shard_worldreset`, and `shard_autosaver`

Practical consequence:

- cluster or shard-wide bookkeeping does not belong on ordinary gameplay prefabs by default
- master-shard aggregation often lives on shard-network components

## Same-Shard Versus Other-Shard Data

Observed in `scripts/components/recallmark.lua`:

- marks save `recall_worldid`
- same-shard checks compare it to `TheShard:GetShardId()`
- position is only returned when the target world id matches the current shard

Practical rule:

- if a saved mark, death position, or warp point may cross shards, save both local coordinates and `worldid`
- do not treat a position as globally valid without the shard id that owns it

## Player Migration

Observed in `scripts/components/worldmigrator.lua`:

- player activation pushes `ms_playerdespawnandmigrate`
- item migration uses shard transaction flow
- portal status reacts to `Shard_IsWorldAvailable(...)`

Observed in `scripts/components/playerspawner.lua`:

- despawn writes `player.migration = { worldid, portalid, sessionid, ... }`
- respawn checks whether the saved `migration.worldid` differs from `TheShard:GetShardId()`
- migration pets are repositioned after arrival

Observed in `scripts/prefabs/player_common.lua`:

- `OnSave(...)` stores migration data
- `OnPreLoad(...)` restores migration state early
- `OnDespawn(inst, migrationdata)` avoids normal drop-everything behavior when migration is happening

Practical consequence:

- migrating players are not the same as ordinary despawned players
- if a feature depends on death position, inventories, followers, or pets, verify migration behavior explicitly

## World Migrator Runtime

Observed in `scripts/components/worldmigrator.lua`:

- `ValidateAndPushEvents()` raises:
  - `migration_available`
  - `migration_full`
  - `migration_unavailable`
- linked portals expose shard availability and fullness through status events

Observed in `scripts/prefabs/migration_portal.lua` and `scripts/prefabs/cave_exit.lua`:

- runtime visuals listen to those migration events

Practical rule:

- if the task is a shard portal or cross-world staircase, patch `worldmigrator` behavior first
- do not hardcode portal availability without checking shard status

## Cluster-Wide Counts And Master-Shard Aggregation

Observed in `scripts/components/shard_players.lua`:

- master shard combines local `AllPlayers` with secondary-shard counts from `TheShard:GetSecondaryShardPlayerCounts(...)`
- then it publishes a unified `ms_playercounts` world event

Practical consequence:

- if the user wants cluster-wide player totals, counting local `AllPlayers` on one shard is wrong
- cluster totals should usually be sourced from master-shard aggregation

## Shard Mod RPC

Observed in `scripts/modutil.lua`:

- `AddShardModRPCHandler(namespace, name, fn)`
- `GetShardModRPC(namespace, name)`
- `SendModRPCToShard(id_table, ...)`

Practical rule:

- use shard mod RPC only when data must cross shard boundaries at runtime
- prefer ordinary mod RPC for client/server work on one shard
- prefer existing migration, persistent world state, or master-shard aggregation when they already solve the problem

## Internal Shard Transactions

Observed in `scripts/components/shardtransactionsteps.lua`:

- official shard transactions use `SendRPCToShard(SHARD_RPC...)`
- the flow tracks initiate, accepted, and finalized states
- the design explicitly handles save-state and reconnection safety

Practical consequence:

- this file is the authoritative reference for robust cross-shard transfer
- it is too heavy to copy casually for ordinary mod features
- use it as a study reference when a feature truly needs reliable shard-to-shard transfer semantics

## Common Failure Points

- counted only local-shard players when the task wanted cluster totals
- stored coordinates without a shard id
- used ordinary client/server RPC for a shard-to-shard problem
- assumed the destination shard was always available
- treated migration like normal despawn and accidentally dropped or cleared the wrong state
- patched a portal visual without checking `worldmigrator` status flow

## Rule Of Thumb

- current shard identity: `TheShard:GetShardId()`
- master-shard-only cluster logic: `TheWorld.ismastershard`
- cross-shard destinations: save `worldid` and check `Shard_IsWorldAvailable(...)`
- shard runtime transfer: prefer shard mod RPC or existing migration flow
