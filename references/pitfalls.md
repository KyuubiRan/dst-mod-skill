# Common Pitfalls

Use this page as a router for common DST mistakes.

Read only the narrow page you need:

- `diagnostic-patterns.md`
  - symptom-driven checklists for prefab, recipe, placer, UI, RPC, replica, and brain failures
- `debug-techniques.md`
  - advanced Lua debug helpers such as `getupvalue` and `setupvalue` for narrow closure patching
- `context-pitfalls.md`
  - `ThePlayer`, local UI, `ismastersim` versus `IsDedicated()`
- `networking-pitfalls.md`
  - `components` versus `replica`, prefab init split, server/client mutation boundaries
- `ui-pitfalls.md`
  - wrong UI patch layer, cleanup leaks, focus issues, and over-broad frontend patches
- `persistence-pitfalls.md`
  - save/load lifecycle mistakes, post-load reference repair, and offline catch-up errors
- `shard-pitfalls.md`
  - master versus secondary shard mistakes, migration assumptions, and shard-aware world ids
- `performance-pitfalls.md`
  - `FindEntities` scans, `AddPrefabPostInitAny`, broad hot-path work

## Fast Router

- "works on host but not remote client"
  - start with `networking-pitfalls.md`
- "UI duplicates, leaks, or patches the wrong screen"
  - start with `ui-pitfalls.md`
- "works on host but breaks on dedicated"
  - start with `context-pitfalls.md`
- "it exists but the wrong thing is visible, craftable, or selectable"
  - start with `diagnostic-patterns.md`
- "I may need to patch a closed-over local helper"
  - start with `debug-techniques.md`
- "it works until reload or world time skip"
  - start with `persistence-pitfalls.md`
- "it works on Master but breaks on Caves or during migration"
  - start with `shard-pitfalls.md`
- "the code technically works but feels too heavy"
  - start with `performance-pitfalls.md`
