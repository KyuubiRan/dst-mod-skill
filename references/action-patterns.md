# Action Patterns

Use this file when a mod adds custom actions or hooks action collection into stategraphs.
If the task also needs deeper SG patching, prediction, or `wilson` versus `wilson_client` routing, also read `references/stategraph-patterns.md`.

## The Core Registration Chain

Custom actions usually involve these pieces from `modmain.lua`:

```lua
local MY_ACTION = AddAction("MY_ACTION", "Do Thing", function(act)
    -- server-authoritative action body
end)

AddComponentAction("SCENE", "mycomponent", function(inst, doer, actions, right)
    table.insert(actions, ACTIONS.MY_ACTION)
end)

AddStategraphActionHandler("wilson", ActionHandler(MY_ACTION, "dolongaction"))
AddStategraphActionHandler("wilson_client", ActionHandler(MY_ACTION, "dolongaction"))
```

This is the usual flow:

1. register the action
2. expose it through component action collection
3. teach the relevant stategraphs how to execute it

Read `scripts/componentactions.lua` whenever the collector site is unclear.
That file is the practical source of truth for how action collection is split.

## `AddAction`

Use `AddAction(id, str, fn)` to create a new `ACTIONS.<id>` entry.

Observed official behavior in `scripts/modutil.lua`:

- the action is registered into `ACTIONS`
- its display string is written into `STRINGS.ACTIONS[action.id]`
- mod-local action code mappings are also stored

Practical consequence:

- this is the action definition
- the function body should match the authoritative execution path you want

## `AddComponentAction`

Use `AddComponentAction(actiontype, component, fn)` to expose the action in collectors.

Observed official action types from `scripts/componentactions.lua`:

- `SCENE`
  - using an object in the world
- `USEITEM`
  - using an inventory item on a world object
- `POINT`
  - using an inventory item on a world point
- `EQUIPPED`
  - using an equipped item on self or a world object
- `INVENTORY`
  - using an inventory item
- `ISVALID`
  - validating whether an action is still allowed

Choose the narrowest action type that matches the intended interaction.

Official collector argument shapes from `scripts/componentactions.lua`:

- `SCENE`
  - `inst, doer, actions, right`
- `USEITEM`
  - `inst, doer, target, actions, right`
- `POINT`
  - `inst, doer, pos, actions, right, target`
- `EQUIPPED`
  - `inst, doer, target, actions, right`
- `INVENTORY`
  - `inst, doer, actions, right`
- `ISVALID`
  - `inst, action, right`

Practical consequence:

- pick the action type from the interaction site first
- only then choose the component that will offer the action

## Collector Routing Quick Map

Use this when the user describes the interaction in plain language:

- click a world object with empty hands
  - start with `SCENE`
- use an inventory item on a world object
  - start with `USEITEM`
- use an inventory item on ground position
  - start with `POINT`
- use an equipped item on self or target
  - start with `EQUIPPED`
- trigger an action directly from inventory context
  - start with `INVENTORY`
- keep or reject an already offered action
  - inspect `ISVALID`

## Stategraph Routing

If a player or creature must perform a custom action animation/state, add an action handler to the relevant stategraph.

Typical player targets:

- `wilson`
- `wilson_client`

Practical rule:

- if the action is player-facing, think about both server and client stategraphs
- if the action is creature-specific, inspect that creature's stategraph under `scripts/stategraphs/`

Important distinction:

- `AddStategraphActionHandler(...)`
  - mod API hook used from `modmain.lua`
- `ActionHandler(...)`
  - the stategraph-side mapping object

Official stategraphs contain many built-in `ActionHandler(...)` examples.
Read the closest official SG file before inventing a new action state.

## Reuse Official Actions Aggressively

Before adding a new custom action, inspect whether the behavior can fit an official action route such as:

- `ACTIONS.HAMMER`
- `ACTIONS.CHOP`
- `ACTIONS.MINE`
- `ACTIONS.DIG`
- `ACTIONS.PICK`
- `ACTIONS.HARVEST`
- `ACTIONS.GIVE`
- `ACTIONS.DEPLOY`
- `ACTIONS.STORE`

Practical rule:

- if the semantics already match, reuse the official action
- only create a new action when the interaction meaning is genuinely different

## Existing Actions Versus New Actions

Use these routes differently:

- Existing action already fits:
  - reuse `ACTIONS.HAMMER`, `ACTIONS.CHOP`, `ACTIONS.MINE`, and similar official actions
- New interaction truly needs new semantics:
  - create a custom action with `AddAction`

Prefer reusing an official action flow whenever possible.

## Buffered Action Flow

Many official systems ultimately run actions through `BufferedAction(...)`.

That means the practical action chain is often:

- component action collector offers action
- player action picker selects it
- stategraph action handler routes it
- buffered action executes it

That means action bugs can come from any of these layers, not just the action function body.

## Common Failure Points

- action never appears
  - wrong collector type or missing collector
- action appears but performer does nothing
  - missing stategraph action handler
- action runs on host but breaks on client
  - missing `wilson_client` route or wrong authority assumptions
- action should have reused an official route
  - unnecessary custom action increased complexity

## Rule Of Thumb

- choose the collector site first
- reuse an official action whenever possible
- add SG routing only for the performers that really need it
- debug the whole action chain, not only the action body
