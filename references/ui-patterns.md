# UI Patterns

Use this file when the task creates or patches widgets, screens, HUD elements, or local input-driven UI.

## Where UI Code Lives

Common mod-side locations:

- `scripts/widgets/<name>.lua`
- `scripts/screens/<name>.lua`

The mod loader adds the mod's `scripts/` directory to `package.path`, so these package paths work:

```lua
require("widgets/mywidget")
require("screens/myscreen")
```

## Typical Widget Definition

Official widgets commonly look like this:

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
- `UIAnim`
- `ImageButton`

## Typical Screen Definition

Screens commonly look like this:

```lua
local Screen = require "widgets/screen"

local MyScreen = Class(Screen, function(self)
    Screen._ctor(self, "MyScreen")
end)

return MyScreen
```

Common screen behavior hooks:

- `OnControl(control, down)`
- `OnRawKey(key, down)`
- `OnMouseButton(button, down, x, y)`

## How To Show A Screen

Client-local screens are usually pushed through:

```lua
TheFrontEnd:PushScreen(screen)
```

This is local UI behavior, so dedicated-server guards matter.

## How To Patch Existing UI

For existing official widget or screen classes, use:

```lua
AddClassPostConstruct("widgets/somewidget", function(self, ...)
    -- patch constructor-time behavior
end)
```

Observed official behavior from `scripts/modutil.lua`:

- `AddClassPostConstruct(package, postfn)` does `require(package)`
- it wraps the class constructor `_ctor`
- it runs the original constructor first, then your patch

Practical consequence:

- pass a require-style package path without `.lua`
- patch narrowly instead of replacing the whole class

Common targets:

- `"widgets/controls"`
- `"widgets/inventorybar"`
- `"screens/playerhud"`

## Local Input In UI

If UI code needs local input:

- read `references/input-patterns.md`
- prefer `AddControlHandler` when the feature should follow mapped controls
- prefer `AddKeyDownHandler` or `AddMouseButtonHandler` only when raw local input is truly needed

## Local-Only Expectations

UI code usually depends on:

- `ThePlayer`
- `TheFrontEnd`
- `TheInput`
- HUD widgets

Guard dedicated-server paths:

```lua
if TheNet:IsDedicated() then
    return
end
```

## Rule Of Thumb

- Create a new widget or screen under `scripts/widgets/` or `scripts/screens/` when the UI is fully mod-owned.
- Use `AddClassPostConstruct` when you only need to patch an existing official UI class.
- Keep gameplay authority out of UI code; local UI should read replica state or send RPC/input, not mutate server-only state directly.
