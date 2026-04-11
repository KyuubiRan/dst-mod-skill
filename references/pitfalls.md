# Common Pitfalls

Use this page as a router for common DST mistakes.

Read only the narrow page you need under `references/pitfalls/` or the diagnostic page under `references/patterns/`:

- `references/patterns/diagnostic-patterns.md`
  - symptom-driven checklists for prefab, recipe, placer, UI, RPC, replica, and brain failures
- `references/patterns/debug-techniques.md`
  - advanced Lua debug helpers such as `getupvalue` and `setupvalue` for narrow closure patching
- `references/pitfalls/context-pitfalls.md`
  - `ThePlayer`, local UI, `ismastersim` versus `IsDedicated()`
- `references/pitfalls/networking-pitfalls.md`
  - `components` versus `replica`, prefab init split, server/client mutation boundaries
- `references/pitfalls/ui-pitfalls.md`
  - wrong UI patch layer, cleanup leaks, focus issues, and over-broad frontend patches
- `references/pitfalls/persistence-pitfalls.md`
  - save/load lifecycle mistakes, post-load reference repair, and offline catch-up errors
- `references/pitfalls/shard-pitfalls.md`
  - master versus secondary shard mistakes, migration assumptions, and shard-aware world ids
- `references/pitfalls/performance-pitfalls.md`
  - `FindEntities` scans, `AddPrefabPostInitAny`, broad hot-path work

## Fast Router

- "works on host but not remote client"
  - start with `references/pitfalls/networking-pitfalls.md`
- "UI duplicates, leaks, or patches the wrong screen"
  - start with `references/pitfalls/ui-pitfalls.md`
- "works on host but breaks on dedicated"
  - start with `references/pitfalls/context-pitfalls.md`
- "it exists but the wrong thing is visible, craftable, or selectable"
  - start with `references/patterns/diagnostic-patterns.md`
- "I may need to patch a closed-over local helper"
  - start with `references/patterns/debug-techniques.md`
- "it works until reload or world time skip"
  - start with `references/pitfalls/persistence-pitfalls.md`
- "it works on Master but breaks on Caves or during migration"
  - start with `references/pitfalls/shard-pitfalls.md`
- "the code technically works but feels too heavy"
  - start with `references/pitfalls/performance-pitfalls.md`
