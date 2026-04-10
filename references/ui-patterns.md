# UI Patterns

Use this file when the task creates or patches widgets, screens, HUD elements, or local frontend flow.

This page is a router.
If the hard part is choosing between `controls`, `playerhud`, `containerwidget`, popup screens, or `frontend`, read `references/ui-patch-patterns.md`.
If the task also depends on input handlers, read `references/input-patterns.md`.
If the UI should trigger real gameplay authority, also read `references/networking-patterns.md` or `references/action-patterns.md`.
If the task is mostly about local globals such as `ThePlayer` or `TheFrontEnd`, also read `references/runtime-local-ui.md`.

## Fast Router

- fully mod-owned widget
  - create `scripts/widgets/<name>.lua`
- fully mod-owned screen or popup
  - create `scripts/screens/<name>.lua`
  - push it with `TheFrontEnd:PushScreen(...)`
- persistent HUD child, status widget, inventory-adjacent element, or layout patch
  - read `references/ui-patch-patterns.md`
  - start from `widgets/controls`
- player HUD overlay roots, popup orchestration, or screen-owned HUD lifecycle
  - read `references/ui-patch-patterns.md`
  - start from `screens/playerhud`
- transient open/close widget such as a container-like panel
  - read `references/ui-patch-patterns.md`
  - start from `widgets/containerwidget`
- screen stack, global fade, frontend sound, or top-level input plumbing
  - read `references/ui-patch-patterns.md`
  - start from `scripts/frontend.lua`

## Common File Locations

Common mod-side locations:

- `scripts/widgets/<name>.lua`
- `scripts/screens/<name>.lua`

The mod loader adds the mod's `scripts/` directory to `package.path`, so these package paths work:

```lua
require("widgets/mywidget")
require("screens/myscreen")
```

## Typical Widget Definition

```lua
local Widget = require "widgets/widget"

local MyWidget = Class(Widget, function(self, owner)
    Widget._ctor(self, "MyWidget")
    self.owner = owner
end)

return MyWidget
```

Common widget base classes:

- `Widget`
- `Button`
- `Image`
- `Text`
- `UIAnim`
- `ImageButton`

## Typical Screen Definition

```lua
local Screen = require "widgets/screen"

local MyScreen = Class(Screen, function(self)
    Screen._ctor(self, "MyScreen")
end)

return MyScreen
```

Typical screen behavior hooks:

- `OnControl(control, down)`
- `OnRawKey(key, down)`
- `OnMouseButton(button, down, x, y)`
- `OnBecomeActive()`
- `OnBecomeInactive()`
- `OnDestroy()`

## Patch Existing UI Narrowly

For existing official widget or screen classes, the default hook is:

```lua
AddClassPostConstruct("widgets/somewidget", function(self, ...)
    -- patch constructor-time behavior
end)
```

Observed in `scripts/modutil.lua`:

- `AddClassPostConstruct(package, postfn)` uses a require-style package path
- it wraps the class constructor `_ctor`
- it runs the original constructor first, then your patch

Practical rule:

- patch the smallest instantiated class that already owns the behavior
- do not replace the whole class when a narrow constructor patch is enough
- if the route is unclear, stop and read `references/ui-patch-patterns.md`

## Local-Only Rules

UI code usually depends on:

- `ThePlayer`
- `TheFrontEnd`
- `TheInput`
- HUD widgets and replica data

Guard dedicated-server paths:

```lua
if TheNet:IsDedicated() then
    return
end
```

Safe HUD guard:

```lua
if ThePlayer ~= nil and ThePlayer.HUD ~= nil then
    -- local HUD logic
end
```

## UI Versus Gameplay Authority

Keep local presentation separate from authoritative gameplay changes.

Stay in UI code when:

- a button opens or closes a local screen
- a widget toggles local display state
- the feature is only local feedback

Route through action or networking when:

- the UI should change real gameplay state
- the server must validate the result
- the client should only send intent

## Cleanup Rule

If a widget or screen registers something long-lived, it should also remove or stop it.

Common cleanup targets:

- input handlers
- event listeners
- periodic tasks
- transient child widgets

If cleanup is the likely failure mode, read `references/ui-pitfalls.md`.

## Intent Index

- "add a custom local widget"
  - create `scripts/widgets/<name>.lua`
- "add a full custom screen"
  - create `scripts/screens/<name>.lua`
  - push it with `TheFrontEnd:PushScreen(...)`
- "patch the existing HUD"
  - start with `references/ui-patch-patterns.md`
- "add a local hotkey to a widget"
  - patch the widget
  - read `references/input-patterns.md`
- "add a button that should perform a real gameplay action"
  - patch the UI locally
  - route the authoritative side through networking or action flow
- "UI duplicates or keeps responding after close"
  - read `references/ui-pitfalls.md`

## Rule Of Thumb

- Create a new widget or screen when the UI is fully mod-owned.
- Use `AddClassPostConstruct(...)` when you only need to patch an existing official UI class.
- Keep gameplay authority out of UI code.
- Local UI should read replica state or send RPC intent, not mutate server-only state directly.
