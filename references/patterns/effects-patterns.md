# Light, FX, And Sound Patterns

Use this file when a task adds lighting, a visual FX prefab, particle FX, or sound playback. Read the closest official prefab first.

Common official shapes:

- a structure with a real light
- a hand-held light child entity
- a one-shot animation FX prefab
- a network proxy that spawns local-only FX
- a sound-only proxy
- a particle effect built with `AddVFXEffect`
- a sound tied to SG timeline frames

## Core Engine Pieces

Observed in official prefabs:

- `inst.entity:AddLight()`
- `inst.entity:AddSoundEmitter()`
- `inst.entity:AddVFXEffect()`
- `inst.entity:AddAnimState()`
- `inst.entity:AddNetwork()`

Distinction:

- `Light`
  - engine light attached to an entity
- `SoundEmitter`
  - sound playback on an entity
- `AnimState`
  - traditional anim-bank visual playback
- `VFXEffect`
  - particle-style effect system with emitters, textures, shaders, and envelopes

## Quick Map

- one-shot visual helper
  - tags: `FX`, often `NOCLICK`
- helper that should not block placement or movement
  - tags: often `NOBLOCK`, often also `FX` and `NOCLICK`
- light-emitting structure
  - entity pieces: `AddLight`, usually `AddAnimState`, often `AddSoundEmitter`
  - gameplay side often still includes `inspectable`, `burnable`, `fueled`, or `prototyper`
- hand-held or follower light helper
  - entity pieces: proxy entity + child light entity
  - networking often uses a netvar if clients must see range or state changes
- SG-timed sound
  - stategraph timeline helpers: `SoundTimeEvent`, `SoundFrameEvent`

Rules:

- `FX` is usually a routing tag, not a behavior system
- light and sound are not components in the usual DST component sense
- if a lit object also burns, consumes fuel, or works as an item, that behavior still belongs in normal components

## Pattern: Lit World Structure

Observed official reference:

- `scripts/prefabs/moon_altar.lua`

Common shape:

- `AddTransform`
- `AddAnimState`
- `AddLight`
- often `AddMiniMapEntity`
- `AddSoundEmitter`
- `AddNetwork`

Observed light setup:

- `SetFalloff(...)`
- `SetIntensity(...)`
- `SetRadius(...)`
- `SetColour(...)`
- `EnableClientModulation(true)`

Use for stations, altars, glowing structures, and other persistent light sources.

## Pattern: Portable Or Attached Light Helper

Observed official reference:

- `scripts/prefabs/lighterfire_common.lua`

Observed shape:

- main prefab has `AddSoundEmitter()` and `AddNetwork()`
- a separate non-networked child entity is created with `AddLight()`
- parent and child are attached with `SetParent(...)`
- light range is replicated through a netvar
- cleanup removes the child light entity on parent removal

Rules:

- the visible light may live on a child helper, not on the main gameplay entity
- this is often cleaner for hand-held flames, follower lights, or client-visible light state

## Pattern: One-Shot Anim FX Prefab

Observed official reference:

- `scripts/prefabs/moose_nest_fx.lua`

Observed shape:

- local non-networked entity with `AddAnimState()` and `AddSoundEmitter()`
- tags usually include `FX`
- `inst.persists = false`
- listen for `animover`
- remove on animation completion

Rules:

- use for impact flashes, bursts, electric pops, and other short scripted visuals
- if the effect is purely presentational and short-lived, keep it non-persistent
- if it should not be targeted, add `NOCLICK`

## Pattern: Network Proxy That Spawns Local-Only FX

Observed official reference:

- `scripts/prefabs/moose_nest_fx.lua`

Observed flow:

1. spawn a small networked proxy prefab
2. on non-dedicated clients, delay one frame and spawn the local FX entity
3. on the server, keep the proxy short-lived and non-persistent

Use for synchronized presentation triggers where clients only need local visuals.

## Pattern: Sound-Only Proxy

Observed official reference:

- `scripts/prefabs/atrium_gate_pulsesfx.lua`

Observed flow:

- spawn a small networked proxy with `FX`
- on non-dedicated clients, spawn a local non-networked sound emitter entity
- parent it relative to `TheFocalPoint` when the sound should be listener-relative
- play the sound
- remove the local sound entity immediately

Use for warning pings, area-localized cues, and other client-heard sound events without a persistent world object.

## Pattern: Combined Anim FX With Optional Sound And Light

Observed official reference:

- `scripts/prefabs/deer_fx.lua`

Observed shape:

- `AddAnimState()`
- optional `AddSoundEmitter()`
- optional `AddLight()`
- `AddNetwork()`
- `FX` tag
- optional netvar-driven fade updates for light
- `inst.persists = false` on the server
- one-shot removal or looping animation depending on data

Rules:

- use for elemental spell FX, charge-up circles, looping auras, and other shared FX families
- if you have many similar variants, use one factory function plus a data table

## Pattern: Particle FX With `AddVFXEffect`

Observed official reference:

- `scripts/prefabs/torchfire_barber.lua`

Observed shape:

- register particle textures and shaders as assets
- add colour and scale envelopes through `EnvelopeManager`
- call `inst.entity:AddVFXEffect()`
- initialize one or more emitters
- configure render resources, particle counts, lifetimes, blend mode, UV frame size, bloom, and sort offsets
- drive particle spawning from tasks or update logic

Use this when:

- `AnimState` sprite animation is not expressive enough
- the effect is really a particle system
- you need smoke, embers, sparks, fire plumes, or similar layered particles

Rule:

- use `AnimState` for ordinary sprite animation
- use `VFXEffect` only when the effect is truly particle-oriented

## Sound Playback Patterns

Observed official usage:

- `inst.SoundEmitter:PlaySound("event/path")`
- `inst.SoundEmitter:PlaySound("event/path", "loop")`
- `inst.SoundEmitter:KillSound("loop")`
- `inst.SoundEmitter:PlayingSound("loop")`
- `inst.SoundEmitter:SetParameter("loop", "intensity", value)`

Typical use:

- one-shot cue
  - `PlaySound("event/path")`
- looping ambience or machine hum
  - `PlaySound("event/path", "loop")` and later `KillSound("loop")`
- parameter-driven loop
  - reuse the named loop and adjust with `SetParameter(...)`

Observed official references:

- `winona_battery_low.lua`
- `moon_altar.lua`
- `spiderden.lua`

## SG-Timed Sound

Verified in `scripts/stategraph.lua` and observed in SG files such as `SGhound.lua`:

- `SoundTimeEvent(time, "event/path")`
- `SoundFrameEvent(frame, "event/path")`

Rules:

- use this when the sound must line up with a hit frame or animation state
- if timing belongs to a performer animation, put it in the SG timeline
- do not replace frame-accurate SG timing with ad hoc delayed tasks unless the official pattern does

## Tag Index

High-frequency tags around light, FX, and sound:

- `FX`
  - visual or presentation helper entity
- `NOCLICK`
  - helper should not be mouse-targetable
- `NOBLOCK`
  - helper should not block placement or movement

Observed official examples:

- many helper and FX prefabs use `FX` + `NOCLICK`
- placement-safe helpers often add `NOBLOCK`

Rules:

- choose these tags from interaction needs, not habit
- a world object the player should inspect or click usually should not be marked `NOCLICK`

## Intent Index

- "I want to add a glowing structure"
  - start from the lit world-structure pattern
  - inspect `moon_altar.lua`
- "I want to add a hand-held or attached light"
  - start from the child-light helper pattern
  - inspect `lighterfire_common.lua`
- "I want to add a one-shot visual effect prefab"
  - start from the one-shot anim FX prefab
  - inspect `moose_nest_fx.lua`
- "I want the server to trigger an FX but clients spawn it locally"
  - start from the network-proxy FX pattern
  - inspect `moose_nest_fx.lua`
- "I want a sound-only cue or warning"
  - start from the sound-only proxy pattern
  - inspect `atrium_gate_pulsesfx.lua`
- "I want a looping aura or spell effect with optional light and sound"
  - start from the shared FX factory pattern
  - inspect `deer_fx.lua`
- "I want smoke, sparks, or fire particles"
  - start from `AddVFXEffect`
  - inspect `torchfire_barber.lua`
- "I want sound exactly on an animation frame"
  - start from `SoundFrameEvent(...)`
  - inspect the closest official SG that already does it

## Common Failure Points

- effect persists forever
  - forgot `animover` removal, timed removal, or `persists = false`
- helper catches mouseover or blocks placement
  - missing `NOCLICK` or `NOBLOCK`
- light exists on server but not on clients
  - wrong replication shape or missing client-side helper creation
- used `VFXEffect` for something a simple `AnimState` prefab could handle
  - unnecessary complexity
- sound loop never stops
  - missing `KillSound(...)` path on shutdown or removal
- added sound or light logic to the wrong runtime side
  - inspect whether the official pattern uses a proxy, child entity, or SG timeline

## Practical Reading Order

1. Read the closest official prefab that matches the effect shape.
2. If the task also changes interaction, inspect `references/patterns/tag-patterns.md`.
3. If the task also changes burn, fuel, or placement logic, inspect the matching world-system or component page.
4. If the timing belongs to animation states, inspect `references/patterns/stategraph-patterns.md`.
5. If the effect needs custom assets, also read `references/patterns/asset-patterns.md`.

## Rule Of Thumb

- Use `AnimState` FX for ordinary sprite effects.
- Use `VFXEffect` for true particle systems.
- Use proxy patterns when clients only need local presentation.
- Choose `FX`, `NOCLICK`, and `NOBLOCK` from interaction needs, not by default.
