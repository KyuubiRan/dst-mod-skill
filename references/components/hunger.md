# `hunger`

Use this file when the task changes hunger value, drain rate, pause or resume flow, or starvation behavior.

Official source:

- `scripts/components/hunger.lua`

Close official prefab shapes:

- `scripts/prefabs/player_common.lua`

High-frequency methods:

- `SetMax(amount)`
- `SetRate(rate)`
- `Pause()`
- `Resume()`
- `IsStarving()`
- `GetPercent()`
- `SetPercent(p, overtime)`
- `SetCurrent(current, overtime)`
- `DoDelta(delta, overtime, ignore_invincible)`
- `LongUpdate(dt)`

Common pairings:

- player `hunger` + `health`
- player `hunger` + `sanity`

Common pitfalls:

- `SetRate(...)` changes ongoing drain, not the current hunger value.
- starvation damage comes from the hunger update path, not from one isolated write.
- save or load behavior often needs `LongUpdate(...)` awareness.

Read next:

- `references/components/health.md`
- `references/persistence-patterns.md`
