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
- `performance-pitfalls.md`
  - `FindEntities` scans, `AddPrefabPostInitAny`, broad hot-path work
