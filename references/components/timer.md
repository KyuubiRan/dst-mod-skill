# `timer`

Use this file when the task changes cooldowns, delayed state changes, or timers that must survive save and load.

Official source:

- `scripts/components/timer.lua`

Close official prefab shapes:

- `scripts/prefabs/farm_plow.lua`
- `scripts/prefabs/daywalker.lua`

High-frequency methods:

- `TimerExists(name)`
- `StartTimer(name, time, paused, initialtime_override)`
- `StopTimer(name)`
- `IsPaused(name)`
- `PauseTimer(name)`
- `ResumeTimer(name)`
- `GetTimeLeft(name)`
- `SetTimeLeft(name, time)`
- `GetTimeElapsed(name)`
- `LongUpdate(dt)`

Common pairings:

- `timer` + event listeners
- `timer` + save or load lifecycle

Common pitfalls:

- `timer` stores timed state; it does not perform gameplay behavior by itself.
- the prefab still needs listeners for timer completion events.
- if the world advances while unloaded, inspect `LongUpdate(...)`.

Read next:

- `references/persistence-patterns.md`
- `references/diagnostic-patterns.md`
