# Hook Selection Patterns

Use this file when the real question is which patch hook should own the change.

If you only need exact function signatures, read `references/hook-signatures.md`.
If the task is specifically about players as a class, also read `references/player-patterns.md`.

## Fast Router

- one named prefab or a short list of prefab names
  - `AddPrefabPostInit(...)`
- every player-tagged entity
  - `AddPlayerPostInit(...)`
- every instance that adds one component
  - `AddComponentPostInit(...)`
- widget, screen, or other class module that returns a class
  - `AddClassPostConstruct(...)`
- class that must be fetched from `_G`
  - `AddGlobalClassPostConstruct(...)`
- every spawned prefab regardless of type
  - `AddPrefabPostInitAny(...)`, only when a narrower hook cannot work
- stategraph or brain target
  - use `AddStategraphPostInit(...)` or `AddBrainPostInit(...)` instead of the generic hooks above

## Official Hook Timing

Observed in `scripts/mainfunctions.lua`:

- `AddPrefabPostInit(prefab, fn)` callbacks run right after `prefab.fn(TheSim)` creates the instance
- `AddPrefabPostInitAny(fn)` runs afterward for every spawned prefab
- both run before `TheWorld:PushEvent("entity_spawned", inst)`

Observed in `scripts/modutil.lua`:

- `AddPlayerPostInit(fn)` is literally `AddPrefabPostInitAny(...)` plus `inst:HasTag("player")`

Observed in `scripts/entityscript.lua`:

- `AddComponentPostInit(component, fn)` runs after `loadedcmp = cmp(self)`
- it runs before `self:RegisterComponentActions(name)`

Observed in `scripts/modutil.lua`:

- `AddClassPostConstruct(package, postfn)` requires the module and wraps `classdef._ctor`
- `AddGlobalClassPostConstruct(package, classname, postfn)` loads the module, resolves the class from `_G`, then wraps `_ctor`

Practical consequence:

- prefab hooks patch instances
- component hooks patch future component construction
- class postconstruct hooks patch future class instances, not already-created ones

## Default Choice: `AddPrefabPostInit`

Use this when:

- the target is one existing prefab
- the feature belongs to that prefab instance
- you know the prefab name

Good fits:

- adding tags
- adding listeners
- adjusting prefab-local component setup
- patching one item, creature, structure, or one specific character prefab

This should usually be the first choice for an existing prefab patch.

## Broadest Choice: `AddPrefabPostInitAny`

Use this only when:

- the patch truly applies to arbitrary spawned prefabs
- the target set cannot be expressed cleanly as a short prefab list or one component family
- you are doing broad instrumentation, filtering, or compatibility glue

Observed official warning in `modutil.lua`:

- this hook is powerful
- it should stay cheap
- you should filter aggressively inside the callback

Practical rule:

- check prefab, tags, or other cheap guards immediately
- do not put expensive scans or large logic here without an early exit

## Player-Wide Choice: `AddPlayerPostInit`

Use this when:

- the patch should affect all player-tagged entities
- the target is players as a class rather than one character

Remember:

- this is still a broad global hook
- it matches local players, remote players, and ghost players unless you filter further
- it is not the same thing as "my local HUD player"

If the task is really about owner-only player sync, also read `references/player-network-patterns.md`.

## System-Wide Choice: `AddComponentPostInit`

Use this when:

- the behavior belongs to a component family rather than one prefab
- every future instance of that component should gain the same patch
- method wrapping or default tuning should live next to the component itself

Good fits:

- wrap or extend a component method
- add small shared listeners
- apply consistent default behavior across all prefabs that add the component

Avoid it when:

- only one or two prefabs should change
- the task is really UI or widget logic
- the component is so common that a broad patch would create collateral behavior

## UI Choice: `AddClassPostConstruct`

Use this when:

- the target is a widget, screen, or other class module
- the module returns the class directly from `require(...)`

Good fits:

- HUD widgets
- screen controls
- frontend classes
- constructor-time widget extension

Practical rule:

- patch the smallest class that is actually instantiated in the flow you care about
- this affects future instances only
- if the hard part is choosing the class rather than the hook, read `references/ui-patch-patterns.md`

## `_G`-Resolved UI Choice: `AddGlobalClassPostConstruct`

Use this only when:

- the class is not returned directly in a convenient way
- the class must be resolved from `_G`

Prefer `AddClassPostConstruct(...)` when the module already returns the class.

## Common Mistakes

- using `AddPrefabPostInitAny(...)` when `AddPrefabPostInit(...)` was enough
- using `AddPlayerPostInit(...)` for local-only HUD work without local guards
- using `AddComponentPostInit(...)` for one prefab-specific tweak
- using `AddClassPostConstruct(...)` on gameplay prefab code instead of UI classes
- forgetting that class postconstruct patches only future instances
- forgetting that player post-init is just a filtered global prefab post-init

## Quick Examples

- "tweak only spear behavior"
  - `AddPrefabPostInit("spear", fn)`
- "every player gets one authoritative death listener"
  - `AddPlayerPostInit(fn)` with a master-sim guard
- "every container component should expose one helper"
  - `AddComponentPostInit("container", fn)`
- "add a HUD widget into controls"
  - `AddClassPostConstruct("widgets/controls", fn)`
- "temporarily log every spawned prefab for debugging"
  - `AddPrefabPostInitAny(fn)` with immediate filtering and logging only
