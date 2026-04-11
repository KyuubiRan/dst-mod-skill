# Input Patterns

Use this file when code listens to local keyboard, mouse, pointer movement, or control input.

`TheInput` is local-process input state.
Treat it as client-local UI/input machinery, not server-authoritative gameplay state.

## High-Frequency `TheInput` Handlers

These signatures come from `scripts/input.lua`.

```lua
TheInput:AddKeyUpHandler(key, fn)
TheInput:AddKeyDownHandler(key, fn)
TheInput:AddKeyHandler(fn)
TheInput:AddMouseButtonHandler(fn)
TheInput:AddMoveHandler(fn)
TheInput:AddControlHandler(control, fn)
TheInput:AddGeneralControlHandler(fn)
TheInput:AddControlMappingHandler(fn)
TheInput:AddTextInputHandler(fn)
```

## Common Uses

- `AddKeyDownHandler`
  - Listen for one concrete keyboard key.
- `AddKeyHandler`
  - Listen for raw key up/down events centrally.
- `AddMouseButtonHandler`
  - Listen for left, right, middle, or wheel button events.
- `AddMoveHandler`
  - Track mouse or pointer movement.
- `AddControlHandler`
  - Listen to a specific mapped control such as `CONTROL_PRIMARY`.
- `AddGeneralControlHandler`
  - Listen to control events broadly.
- `AddControlMappingHandler`
  - Listen for control-rebinding changes in control-settings UI or similar tooling.

## Prefer The Narrowest Handler

- Use `AddKeyDownHandler(key, fn)` when a single hotkey is enough.
- Use `AddMouseButtonHandler(fn)` when the interaction is pointer-button-based.
- Use `AddControlHandler(control, fn)` when the feature should respect DST control mapping.
- Prefer control handlers over raw keys when the action concept is "primary", "secondary", "inspect", or another mapped control.
- Use `AddKeyHandler(fn)` only when raw keyboard handling is genuinely needed.

## Local-Only Expectations

- `TheInput` is for local input handling.
- Guard dedicated-server paths.
- Do not use local input handlers as proof that the server should mutate gameplay directly.
- If local input should trigger authoritative gameplay, route that intent through the correct RPC or existing client-to-server action flow.

Safe shape:

```lua
if TheNet:IsDedicated() then
    return
end

local handler = TheInput:AddKeyDownHandler(KEY_F, function()
    -- local input reaction
end)
```

## `TheInput` Vs Widget Methods

Do not route every UI input task through global `TheInput` handlers.
Official widgets and screens also override local methods such as:

```lua
widget:OnControl(control, down)
widget:OnMouseButton(button, down, x, y)
widget:OnKeyDown(key)
```

Practical rule:

- Use `TheInput:*Handler` when the input listener should exist outside one focused widget or needs process-level local input.
- Use widget or screen `OnControl` / `OnMouseButton` / `OnKeyDown` overrides when the behavior is owned by that UI object.

## Mouse Button Notes

Common button constants from `scripts/constants.lua`:

```lua
MOUSEBUTTON_LEFT
MOUSEBUTTON_RIGHT
MOUSEBUTTON_MIDDLE
MOUSEBUTTON_SCROLLUP
MOUSEBUTTON_SCROLLDOWN
```

Common mapped controls from `scripts/constants.lua`:

```lua
CONTROL_PRIMARY
CONTROL_SECONDARY
CONTROL_ACCEPT
CONTROL_CANCEL
```

Typical callback shape:

```lua
TheInput:AddMouseButtonHandler(function(button, down, x, y)
    -- x/y are screen-space positions
end)
```

## Cleanup Matters

Input handlers should usually be removed when the owning widget, screen, or helper object goes away.

Official code commonly stores the returned handler token and removes it later.
Observed removal shape:

```lua
TheInput.onmousebutton:RemoveHandler(handler)
TheInput.oncontrol:RemoveHandler(handler)
```

Practical rule:

- Store the returned handler.
- Remove it during widget teardown, screen close, or component cleanup.
- Do not leave long-lived local handlers registered accidentally.

## Small Routing Index

- "I need one local hotkey"
  - `AddKeyDownHandler`
- "I need left or right click anywhere in a local screen flow"
  - `AddMouseButtonHandler`
- "I need controls that respect player keybinds"
  - `AddControlHandler` or widget `OnControl`
- "I need to react when the user remaps controls"
  - `AddControlMappingHandler`
- "I only need input while this widget is focused"
  - prefer widget `OnControl`, `OnMouseButton`, or `OnKeyDown`
