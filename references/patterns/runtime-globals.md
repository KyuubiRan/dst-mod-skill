# Runtime Globals

Use this page as a router for high-frequency runtime globals.

Read only the narrow page you need under `references/patterns/`:

- `references/patterns/runtime-authority.md`
  - `TheWorld.ismastersim`, `TheNet:IsDedicated()`, `TheNet:GetIsServer()`, `TheWorld.state`, `TheWorld.Map`
- `references/patterns/runtime-local-ui.md`
  - `ThePlayer`, `TheFrontEnd`, local HUD usage
- `references/patterns/persistent-string-patterns.md`
  - `TheSim:SetPersistentString(...)`, `GetPersistentString(...)`, and cross-save local storage
- `references/patterns/input-patterns.md`
  - `TheInput`, keyboard, mouse, move, and control handler usage
- `references/patterns/entity-query-patterns.md`
  - `TheSim:FindEntities(...)` usage shapes and performance rules

## Fast Intent Router

- "Should this logic run only on the server?"
  - read `references/patterns/runtime-authority.md`
- "Can I use `ThePlayer`, HUD, or screens here?"
  - read `references/patterns/runtime-local-ui.md`
- "How do I save local settings or cache across world saves?"
  - read `references/patterns/persistent-string-patterns.md`
- "Should this input or hotkey be local-only?"
  - read `references/patterns/input-patterns.md`
- "How do I scan nearby entities safely?"
  - read `references/patterns/entity-query-patterns.md`

## Two High-Level Questions First

Before using any runtime global, answer these first:

1. Is this code running in authoritative simulation, local client UI, or worldgen bootstrap?
2. Is the global process-local, world-local, or entity-local?

Practical rule:

- `TheWorld` and `TheNet`
  - authority and process context
- `ThePlayer`, `TheFrontEnd`, `TheInput`
  - local client process context
- `inst`, `doer`, `owner`, `giver`, `attacker`
  - gameplay instance context

If an entity callback already gives you `inst` or `doer`, prefer that over reaching for a global.

## Global Safety Boundary

The official runtime uses two different shapes here.
Do not treat them the same way.

Engine-managed singleton globals:

- `GLOBAL`
- `TheSim`
- `TheNet`
- `TheShard`
- `TheInput`
- `TheFrontEnd`
- `TheMixer`
- `TheCamera`
- `TheFocalPoint`
- `TheWorld`
- `ThePlayer`
- `AllPlayers`

Practical rule:

- do not overwrite or rebind these names in mod code
- read them, call their APIs, and guard availability
- `TheWorld` and `ThePlayer` are entity references, so entity-local fields may be attached to the entity if the feature really belongs there
- engine userdata or manager singletons such as `TheSim`, `TheNet`, `TheInput`, `TheFrontEnd`, `TheMixer`, and `TheCamera` should be treated as read or call handles, not ad-hoc storage tables

Shared registry tables that may be extended but not replaced:

- `TUNING`
- `STRINGS`
- `ACTIONS`
- `CUSTOM_RECIPETABS`
- `MOD_RPC`
- `CLIENT_MOD_RPC`
- `SHARD_MOD_RPC`

Practical rule:

- add the smallest needed field or registration
- do not replace the whole table with a new table
- prefer official helpers when they exist

Examples from official mod APIs:

- `AddAction(...)`
  - inserts into `ACTIONS[...]` and `STRINGS.ACTIONS[...]`
- `AddRecipe2(...)` and `AddRecipeToFilter(...)`
  - register recipes through the crafting APIs instead of replacing crafting tables
- `AddModRPCHandler(...)`, `AddClientModRPCHandler(...)`, `AddShardModRPCHandler(...)`
  - extend mod RPC registries without replacing RPC tables

Do not write custom mod ids directly into core `RPC`, `CLIENT_RPC`, or `SHARD_RPC`.
Use the mod RPC helper family instead.

## Common Mistake Pattern

Wrong sequence:

1. start with `ThePlayer`
2. then try to make it work on host, client, and dedicated server

Safer sequence:

1. start from the entity or callback parameters
2. gate authority with `TheWorld.ismastersim` when needed
3. only use `ThePlayer` or `TheFrontEnd` for genuinely local behavior
