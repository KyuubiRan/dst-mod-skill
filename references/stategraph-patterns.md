# Stategraph Patterns

Use this file when a task adds or patches stategraph behavior.

Read the official files first:

- `scripts/stategraph.lua`
- `scripts/stategraphs/commonstates.lua`
- the concrete target under `scripts/stategraphs/`

This page is for the practical questions that keep coming up in DST modding:

- which SG hook should I use
- do I need `wilson`, `wilson_client`, or both
- should this be an action handler, event handler, or whole state
- where do tags, timeline, and timeout fit
- when should I reuse `CommonStates`

## Core SG Objects

Verified in `scripts/stategraph.lua`:

- `ActionHandler(action, state, condition)`
  - maps an action to a destination state
- `EventHandler(name, fn)`
  - handles pushed SG events
- `TimeEvent(time, fn)`
  - runs logic at a time offset inside the state
- `FrameEvent(frame, fn)`
  - convenience wrapper around `TimeEvent(frame * FRAMES, fn)`
- `SoundTimeEvent(time, sound_event)`
  - convenience wrapper that calls `inst.SoundEmitter:PlaySound(...)`
- `SoundFrameEvent(frame, sound_event)`
  - frame-based sound helper
- `State{ ... }`
  - the state definition object itself

Practical distinction:

- action handler
  - how an action chooses a state
- event handler
  - how the SG reacts after an event is pushed
- state
  - the actual animation, tags, and timing logic

## The `State{}` Shape

Verified in `scripts/stategraph.lua`, a state commonly contains:

- `name`
- `tags`
- `onenter`
- `onexit`
- `onupdate`
- `ontimeout`
- `events`
- `timeline`

Practical meaning:

- `tags`
  - routing flags such as `busy`, `doing`, `pausepredict`, `attack`, `idle`
- `onenter`
  - setup, animation start, locomotor stop, preview action, timeout setup
- `events`
  - reactions to `animover`, `timeout`, hit events, or custom pushed events
- `timeline`
  - exact frame or time windows for buffered action execution, sounds, FX, damage, or tag removal
- `onupdate`
  - prediction correction or continuous state checks
- `ontimeout`
  - cleanup or fallback exit when the state should not run forever
- `onexit`
  - cleanup for interruption, tag-sensitive rollback, or controller re-enable

## Server And Client Player SGs

For player-facing actions, always inspect both:

- `scripts/stategraphs/SGwilson.lua`
- `scripts/stategraphs/SGwilson_client.lua`

Observed official pattern:

- server SG owns authoritative execution
- client SG owns prediction and preview behavior
- client states often declare `server_states = { ... }`

Practical rule:

- if a custom action can be issued by players, think about both `wilson` and `wilson_client`
- if the action is creature-only, inspect only that creature's SG unless prediction is also involved

Common signs you need the client SG too:

- the action works on host but not on clients
- the client shows no animation or instantly snaps back
- preview action timing is missing

## Prediction-Side Clues

Verified in `scripts/stategraph.lua` and `SGwilson_client.lua`:

- client-player states may define `server_states`
- client-player states may use `forward_server_states`
- server-player states may use `no_predict_fastforward`

Observed official client flow:

- `PerformPreviewBufferedAction()`
- `ServerStateMatches()`
- `FlattenMovementPrediction()`

Practical consequence:

- do not copy a server player state into `wilson_client` blindly
- inspect the closest official client state with similar timing first
- client states are often simpler and focused on preview, timeout, and reconciliation

## SG Hook APIs From `modmain.lua`

Verified in `scripts/modutil.lua`:

- `AddStategraphActionHandler(stategraph, handler)`
- `AddStategraphState(stategraph, state)`
- `AddStategraphEvent(stategraph, event)`
- `AddStategraphPostInit(stategraph, fn)`

Use them differently:

- `AddStategraphActionHandler`
  - add a new action-to-state route
- `AddStategraphState`
  - add a whole new state object
- `AddStategraphEvent`
  - add a new event handler
- `AddStategraphPostInit`
  - patch existing states, events, tags, or handlers in place

Practical rule:

- if the closest official state already exists and only needs a small change, prefer `AddStategraphPostInit`
- if your mod owns a genuinely new performer state, add a new `State`

## `ActionHandler` Versus Reusing Official Action Flow

Before writing a custom action route, inspect whether an official action already maps to an existing state you can reuse.

Observed in `SGwilson.lua` and `SGwilson_client.lua`:

- many actions route to shared states such as `doshortaction`, `dolongaction`, `give`, `terraform`, `jumpin_pre`
- some handlers choose the state dynamically with a function

Practical rule:

- reuse official action semantics when possible
- only add a new action handler when the performer truly needs a different SG path

## `EventHandler` Versus `timeline`

Use them for different timing problems:

- `EventHandler("animover", ...)`
  - leave the state when the current animation finishes
- `TimeEvent(...)` or `FrameEvent(...)`
  - precise timing inside the animation
- `SoundTimeEvent(...)` or `SoundFrameEvent(...)`
  - precise sound timing

Observed official pattern:

- action execution often happens in `timeline`
- state exit often happens in `animover`
- timeout is used when prediction or fallback timing matters

## Reuse `CommonStates` Aggressively

Verified in `scripts/stategraphs/commonstates.lua`:

- `CommonStates.AddSimpleState(...)`
- `CommonStates.AddSimpleActionState(...)`
- `CommonStates.AddShortAction(...)`
- `CommonStates.AddRunStates(...)`
- `CommonStates.AddWalkStates(...)`
- `CommonStates.AddSleepStates(...)`
- `CommonStates.AddFrozenStates(...)`
- `CommonStates.AddCombatStates(...)`
- `CommonStates.AddHitState(...)`
- `CommonStates.AddDeathState(...)`
- many other family helpers

Practical rule:

- if the creature matches a common locomotion, combat, frozen, hit, sleep, or death pattern, start in `commonstates.lua`
- only hand-write a full custom state when the common helper no longer matches

## Intent Index

Use this when the user describes the problem in plain language.

- "I added a custom action and it shows up but does nothing"
  - inspect action handler routing in both `wilson` and `wilson_client`
  - start with `AddStategraphActionHandler(...)`
- "I need a new player action animation"
  - inspect the closest official player state in `SGwilson.lua`
  - then mirror the prediction shape in `SGwilson_client.lua`
- "I need to run logic on a specific animation frame"
  - start with `timeline`
  - use `FrameEvent(...)` or `TimeEvent(...)`
- "I need sound tied to animation timing"
  - start with `SoundFrameEvent(...)` or `SoundTimeEvent(...)`
- "I only need to tweak an existing state"
  - start with `AddStategraphPostInit(...)`
- "I need to react to a pushed event"
  - start with `EventHandler(...)`
  - then use `AddStategraphEvent(...)` or patch `events` in post-init
- "I am adding AI movement, hit, sleep, or death states"
  - inspect `commonstates.lua` before hand-writing a custom state family

## Common Failure Points

- action appears but nothing animates
  - missing SG action handler
- action works for host only
  - missing `wilson_client` route or wrong prediction shape
- state never leaves
  - missing `animover` handling or timeout
- interrupt cleanup is broken
  - `onexit` did not restore controller, sound, or temporary tags
- copied server state into client SG directly
  - prediction fields and preview flow do not match
- wrote a full custom state when `CommonStates` already covers it
  - unnecessary complexity

## Practical Reading Order

1. Read `scripts/stategraph.lua` if the SG object model is unclear.
2. Read `scripts/stategraphs/commonstates.lua` if the feature looks like a common locomotion or combat family.
3. Read the concrete SG file that already does something similar.
4. If the performer is a player, inspect both `SGwilson.lua` and `SGwilson_client.lua`.
5. Read `scripts/modutil.lua` for the narrow SG hook you plan to use.

## Rule Of Thumb

- Choose the smallest SG hook that matches the change.
- Reuse official action states before inventing new ones.
- For player actions, think in server plus client pairs.
- Put exact frame logic in `timeline`, not in guessed delays.
