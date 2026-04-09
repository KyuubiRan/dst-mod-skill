# Action Patterns

Use this file when a mod adds custom actions or hooks action collection into stategraphs.

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

## Stategraph Routing

If a player or creature must perform a custom action animation/state, add an action handler to the relevant stategraph.

Typical player targets:

- `wilson`
- `wilson_client`

Practical rule:

- if the action is player-facing, think about both server and client stategraphs
- if the action is creature-specific, inspect that creature's stategraph under `scripts/stategraphs/`

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

## Rule Of Thumb

- Use `AddAction` only when an existing official action cannot express the behavior cleanly.
- Use `AddComponentAction` to surface the action at the right interaction site.
- Use `AddStategraphActionHandler` to wire the action into the actual performer stategraph.
- Reuse official action/state names whenever possible instead of inventing a fully custom flow.
