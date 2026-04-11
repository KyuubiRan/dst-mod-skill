# Shard Pitfalls

Use this file when logic works on one shard but breaks on caves, secondary shards, or during migration.

## Common Failure Shapes

- feature works on Master but not Caves
  - it probably assumed master-shard-only state or local `AllPlayers`
- portal or recall target looks valid but fails at runtime
  - destination shard availability was not checked
- player data is lost during migration
  - despawn and migration were treated as the same cleanup path
- cross-shard action used the wrong RPC channel
  - it needed shard mod RPC or existing migration flow
- saved position reloads on the wrong shard
  - `worldid` was never stored or compared

## Practical Rules

- do not assume `TheWorld.ismastersim` means master shard
- do not count cluster totals from local `AllPlayers` alone
- do not use same-shard position data without the shard id
- do not promise a cross-shard destination without `Shard_IsWorldAvailable(...)`

## Fast Router

- shard runtime structure is unclear
  - read `references/patterns/shard-patterns.md`
- ordinary one-shard replication issue
  - read `references/patterns/networking-patterns.md`
- migration and save behavior are mixed together
  - also read `references/patterns/persistence-patterns.md`
