# `health`

Use this file when the task changes HP, death flow, invincibility, regen, or max-health tuning.

Official source:

- `scripts/components/health.lua`

Close official prefab shapes:

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/glommer.lua`

High-frequency methods:

- `GetPercent()`
- `SetPercent(percent, overtime, cause)`
- `DoDelta(amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb)`
- `SetCurrentHealth(amount)`
- `SetMaxHealth(amount)`
- `SetPenalty(penalty)`
- `DeltaPenalty(delta)`
- `Kill()`
- `ForceKill()`
- `SetInvincible(val)`

Common pairings:

- `health` + `combat`
- `health` + `lootdropper`
- player-side `health` + `hunger` + `sanity`

Common pitfalls:

- `DoDelta(...)` and `SetPercent(...)` are not interchangeable.
- `Kill()` follows more normal death flow; `ForceKill()` is the hard override.
- health mutation is authoritative server logic.

Read next:

- `references/stategraph-patterns.md`
- `references/player-network-patterns.md`
