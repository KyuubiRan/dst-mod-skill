# UI Patterns

Use this file when the task creates or patches widgets, screens, HUD elements, or local input-driven UI.

This page is for local UI structure and patch routing.
If the task also depends on input handlers, read `references/input-patterns.md`.

## Where UI Code Lives

Common mod-side locations:

- `scripts/widgets/<name>.lua`
- `scripts/screens/<name>.lua`

The mod loader adds the mod's `scripts/` directory to `package.path`, so these package paths work:

```lua
require("widgets/mywidget")
require("screens/myscreen")
```

Common official UI targets:

- `widgets/controls`
- `widgets/inventorybar`
- `widgets/containerwidget`
- `widgets/crafting`
- `screens/playerhud`
- `screens/redux/*`

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
- `Image`
- `Text`
- `UIAnim`
- `ImageButton`

Common widget work:

- `self:AddChild(...)`
- `self:SetPosition(...)`
- `self:Show()`
- `self:Hide()`

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
- close or teardown handlers for screen exit

## How To Show Or Close A Screen

Client-local screens are usually pushed through:

```lua
TheFrontEnd:PushScreen(screen)
```

Closing is usually handled by:

- screen control hooks
- `TheFrontEnd:PopScreen(...)` patterns
- built-in close flow in the owning UI path

Rule:

- screens are local UI objects
- guard dedicated-server paths
- do not treat screen creation as gameplay authority

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
- patch constructor-built structure, then store your own handles on `self`

Common targets:

- `"widgets/controls"`
- `"widgets/inventorybar"`
- `"widgets/containerwidget"`
- `"screens/playerhud"`

## HUD Patching

Many HUD tasks are really `playerhud` or `controls` tasks, not generic screen work.

Typical shape:

- patch `widgets/controls` when you want to add or reposition persistent HUD children
- patch `screens/playerhud` when the task is about player HUD lifecycle or screen-owned flows

Common concerns:

- local player only
- ownership under HUD widget tree
- teardown when HUD rebuilds or screen changes

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

Safe local shape:

```lua
if ThePlayer ~= nil and ThePlayer.HUD ~= nil then
    -- local HUD logic
end
```

Also read:

- `references/runtime-local-ui.md`

## Input In UI

If UI code needs local input:

- prefer `AddControlHandler` when the feature should follow mapped controls
- prefer `AddKeyDownHandler` or `AddMouseButtonHandler` only when raw local input is truly needed
- store handler tokens and remove them during teardown

Also read:

- `references/input-patterns.md`

## Cleanup Matters

UI bugs often come from cleanup mistakes, not widget construction.

Common things to clean up:

- input handlers
- periodic tasks
- event listeners
- references to widgets or screen-owned children

Rule:

- if a widget or screen registers something long-lived, it should also remove or stop it
- do not leave local handlers active after the screen or widget is gone

## Intent Index

- "add a custom local widget"
  - create `scripts/widgets/<name>.lua`
- "add a full custom screen"
  - create `scripts/screens/<name>.lua`
  - push it with `TheFrontEnd:PushScreen(...)`
- "patch the existing HUD"
  - inspect `widgets/controls` or `screens/playerhud`
- "add a local hotkey to a widget"
  - patch the widget, then read `references/input-patterns.md`
- "UI exists but dedicated server crashes"
  - inspect local guards around `ThePlayer`, `TheFrontEnd`, and `TheInput`
- "UI duplicates or keeps responding after close"
  - inspect teardown and handler cleanup

## Common Failure Points

- UI code runs on dedicated server
  - missing guard for local-only globals
- patch works once but duplicates later
  - constructor patch creates children repeatedly without guarding ownership
- hotkeys keep firing after the screen closes
  - input handlers were not removed
- gameplay logic is mutated directly from UI
  - missing RPC or replica boundary

## Rule Of Thumb

- Create a new widget or screen when the UI is fully mod-owned.
- Use `AddClassPostConstruct` when you only need to patch an existing official UI class.
- Keep gameplay authority out of UI code.
- Local UI should read replica state or send RPC intent, not mutate server-only state directly.
