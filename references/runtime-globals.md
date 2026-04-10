# Runtime Globals

Use this page as a router for high-frequency runtime globals.

Read only the narrow page you need:

- `runtime-authority.md`
  - `TheWorld.ismastersim`, `TheNet:IsDedicated()`, `TheNet:GetIsServer()`, `TheWorld.state`, `TheWorld.Map`
- `runtime-local-ui.md`
  - `ThePlayer`, `TheFrontEnd`, local HUD usage
- `persistent-string-patterns.md`
  - `TheSim:SetPersistentString(...)`, `GetPersistentString(...)`, and cross-save local storage
- `input-patterns.md`
  - `TheInput`, keyboard, mouse, move, and control handler usage
- `entity-query-patterns.md`
  - `TheSim:FindEntities(...)` usage shapes and performance rules

## Fast Intent Router

- "Should this logic run only on the server?"
  - read `runtime-authority.md`
- "Can I use `ThePlayer`, HUD, or screens here?"
  - read `runtime-local-ui.md`
- "How do I save local settings or cache across world saves?"
  - read `persistent-string-patterns.md`
- "Should this input or hotkey be local-only?"
  - read `input-patterns.md`
- "How do I scan nearby entities safely?"
  - read `entity-query-patterns.md`

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

## Common Mistake Pattern

Wrong sequence:

1. start with `ThePlayer`
2. then try to make it work on host, client, and dedicated server

Safer sequence:

1. start from the entity or callback parameters
2. gate authority with `TheWorld.ismastersim` when needed
3. only use `ThePlayer` or `TheFrontEnd` for genuinely local behavior
