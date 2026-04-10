# World And Utility Components

Use this file for `pickable`, `workable`, `timer`, and `talker`.

## `pickable`

Official file:

- `scripts/components/pickable.lua`

High-frequency methods:

- `SetUp(product, regen, number)`
- `SetOnPickedFn(fn)`
- `SetOnRegenFn(fn)`
- `SetMakeBarrenFn(fn)`
- `SetMakeEmptyFn(fn)`
- `CanBeFertilized()`
- `Fertilize(fertilizer, doer)`
- `CanBePicked()`
- `Regen()`
- `MakeBarren()`
- `MakeEmpty()`
- `Pick(picker)`

Use it for:

- berry bushes, saplings, crops, and world-harvest nodes
- harvest and regrow loops
- fertilize or barren state logic

Common pitfalls:

- `pickable` is for world harvestables, not loose items on the ground
- many pickables also use `workable` for digging up the plant or structure
- harvest behavior usually also needs inspect, loot, and animation state updates

## `workable`

Official file:

- `scripts/components/workable.lua`

High-frequency methods:

- `SetRequiresToughWork(tough)`
- `SetWorkAction(act)`
- `GetWorkAction()`
- `SetWorkable(able)`
- `SetWorkLeft(work)`
- `GetWorkLeft()`
- `CanBeWorked()`
- `SetMaxWork(work)`
- `WorkedBy(worker, numworks)`
- `SetOnWorkCallback(fn)`
- `SetOnFinishCallback(fn)`

Use it for:

- trees, boulders, diggable plants, hammerable structures, and breakable objects
- work-progress and finish callbacks

Common pitfalls:

- `workable` is the target-side component
- if a tool cannot affect the target, inspect both `tool` and `workable`
- work flow often also needs lootdropper, burnable, or structure-specific callbacks

## `timer`

Official file:

- `scripts/components/timer.lua`

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

Use it for:

- cooldowns
- delayed spawns or phase changes
- state changes that must survive save or load

Common pitfalls:

- `timer` is state storage plus timing; it does not perform behavior by itself
- the prefab still needs listeners or callbacks for timer completion
- if a timer drives UI or animation, that other system also needs inspection

## `talker`

Official file:

- `scripts/components/talker.lua`

High-frequency methods:

- `MakeChatter()`
- `Chatter(strtbl, strid, time, forcetext, echotochatpriority)`
- `Say(script, time, noanim, force, nobroadcast, colour, text_filter_context, original_author_netid, onfinishedlinesfn, sgparam)`
- `ShutUp()`
- `IgnoreAll(source)`
- `StopIgnoringAll(source)`

Use it for:

- player speech bubbles
- creature, boss, or NPC lines
- chatter loops and ambient comments
- cases where a creature should intentionally omit normal speaking behavior

Common pitfalls:

- `talker` is common enough on creature-like prefabs that "missing talker" can itself be meaningful
- speech display may also depend on net, string keys, and client presentation
- if the task is dialogue logic, inspect the speaking caller and strings, not just `talker.lua`
