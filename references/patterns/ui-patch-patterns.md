# UI Patch Patterns

Use this file when the hard part is choosing which UI layer should own the patch.

This page is specifically about routing between `controls`, `playerhud`, transient widgets, popup screens, `widgets/screen`, and `frontend`.
If the task also needs raw input, read `references/patterns/input-patterns.md`.
If the task should change real gameplay state, read `references/patterns/networking-patterns.md` or `references/patterns/action-patterns.md`.

## Layer Model

Read the UI stack from top to bottom like this:

1. `scripts/frontend.lua`
   - owns `screenstack`, `screenroot`, `overlayroot`, frontend sound, and raw key or text input plumbing
2. `scripts/widgets/screen.lua`
   - shared screen base behavior such as `OnBecomeActive()`, `OnBecomeInactive()`, `OnDestroy()`, and `default_focus`
3. `scripts/screens/playerhud.lua`
   - the in-game HUD screen, overlay roots, popup orchestration, and screen-owned HUD lifecycle
4. `scripts/widgets/controls.lua`
   - the persistent HUD widget tree under the player HUD
5. transient widgets such as `scripts/widgets/containerwidget.lua`
   - open or close around one feature and clean up per-open state

Practical rule:

- patch as low as possible
- move upward only when the lower layer does not own the behavior

## Fast Router

- add a persistent corner widget, meter, badge, or HUD layout child
  - patch `widgets/controls`
- add a fullscreen overlay, popup flow, or screen-owned HUD behavior
  - patch `screens/playerhud`
- patch one open or close widget that rebuilds itself each time
  - patch that widget class directly, such as `widgets/containerwidget`
- add a transient confirm screen or modal dialog
  - create or patch a screen such as `screens/redux/popupdialog`
- fix focus, default focus, or active or inactive screen lifecycle
  - inspect `widgets/screen`
- change screen stack behavior, global fades, frontend-only sound, or top-level raw input flow
  - inspect `scripts/frontend.lua`

## `widgets/controls`: Persistent HUD Child Ownership

Patch `widgets/controls` when:

- the widget should live as part of the ordinary in-game HUD
- the feature belongs near status, inventory, map controls, chat queues, or other persistent HUD children
- the task is mainly about layout, anchor, scale, or always-available HUD presence

Observed in official code:

- `Controls(owner)` builds large persistent child trees in the constructor
- it owns many root widgets and long-lived HUD children
- it is not just a generic helper; it is the real HUD layout owner for many widgets

Good fits:

- add one always-visible counter
- reposition a persistent HUD element
- attach a local HUD child that should survive ordinary gameplay UI flow

Bad fits:

- popup orchestration
- top-level screen stack behavior
- one container's per-open state

## `screens/playerhud`: Screen-Owned HUD Lifecycle

Patch `screens/playerhud` when:

- the task needs HUD overlay ordering or screen-owned roots
- the behavior depends on HUD lifecycle, popup coordination, or world event listeners owned by the HUD screen
- the feature should live in `overlayroot`, `under_root`, `root`, `over_root`, or `popupstats_root`

Observed in official code:

- the constructor registers world and global listeners
- `CreateOverlays(owner)` rebuilds overlay branches
- `OnDestroy()` closes owned popup state and tears down screen-owned resources
- many popup screens are pushed and popped from here

Good fits:

- add a fullscreen warning overlay
- coordinate a popup screen with existing HUD flow
- attach world-event-driven HUD behavior that belongs to the HUD screen lifecycle

Bad fits:

- one always-visible status widget that could live directly in `controls`
- generic frontend stack behavior that belongs above the HUD

## `widgets/containerwidget`: Transient Open Or Close Widgets

Patch `widgets/containerwidget` or a similar feature widget when:

- the widget rebuilds itself in `Open(...)`
- the widget cleans up in `Close()`
- the task is really about one open UI surface, not the whole HUD

Observed in official code:

- `Open(...)` creates button and slot children, registers listeners, and binds replica container state
- `Close()` kills transient children and removes callbacks
- the same widget instance may open repeatedly for different containers

Good fits:

- add a button to a container UI
- add one extra per-open visual
- patch slot behavior that only matters while the container is open

Bad fits:

- long-lived HUD widgets
- global input handlers that should survive after close

## `screens/redux/popupdialog`: Clean Transient Screen Shape

Use or mimic popup-style screens when:

- the task is a modal confirm or notice flow
- the screen should own its own close behavior
- controller focus should land on a default widget immediately

Observed in official code:

- the screen sets `self.default_focus`
- `OnControl(...)` routes controller input
- `Close()` delegates to `TheFrontEnd:PopScreen(self)`

Good fits:

- confirm or cancel dialogs
- one-step local popup screens
- tiny mod-owned modal UI

## `widgets/screen`: Shared Screen Lifecycle

Read `widgets/screen` when the patch is really about screen behavior itself.

Observed in official code:

- `OnBecomeInactive()` stores `last_focus`
- `OnBecomeActive()` restores `last_focus` or `default_focus`
- `OnDestroy()` kills the screen

Practical consequence:

- if focus restoration is broken, inspect `widgets/screen`
- if controller navigation should land on a known widget, set `default_focus`
- if teardown is missing, check whether the screen implements `OnDestroy()`

## `scripts/frontend.lua`: Screen Stack And Frontend Root

Patch or inspect `frontend.lua` only when the behavior really belongs to the top-level frontend system.

Observed in official code:

- `FrontEnd` owns `screenstack`, `screenroot`, and `overlayroot`
- `PushScreen(screen)` inactivates the previous top screen, adds the new one, then calls `screen:OnBecomeActive()`
- `PopScreen(screen)` destroys the popped screen and reactivates the new top screen
- `FrontEnd:GetSound()` returns the frontend sound emitter
- constructor-time input handlers call `OnRawKey(...)` and `OnTextInput(...)`

Good fits:

- frontend-only sound or global fade behavior
- true screen-stack orchestration
- top-level debugging or instrumentation of screen transitions

Bad fits:

- adding one mod-owned screen
- patching one HUD element
- ordinary popup behavior that already fits in a screen class

Rule:

- do not patch `frontend.lua` just to open one custom screen
- prefer creating a screen and pushing it through `TheFrontEnd`

## Constructor Versus Active Or Inactive Versus Destroy

Use constructor patching when:

- the child tree should exist for every future instance
- the change is structural

Use `OnBecomeActive()` or `OnBecomeInactive()` when:

- focus or visibility depends on top-of-stack transitions
- the feature should react when a screen is covered or restored

Use `OnDestroy()` or widget-specific `Close()` when:

- input handlers, event listeners, or tasks must be removed
- transient children must be killed

## Cleanup Checklist

If the patch registers any of these, also define the cleanup path:

- `TheInput` handlers
- `ListenForEvent(...)` callbacks
- `DoTaskInTime(...)` or periodic tasks
- transient child widgets
- screen references cached on `self`

## Focus And Controller Rule

If the screen should be usable on controller:

- set `default_focus`
- implement `OnControl(...)` when needed
- do not assume mouse-only interaction

## Intent Index

- "add a new persistent meter near status"
  - patch `widgets/controls`
- "add a weather or danger overlay across the HUD"
  - patch `screens/playerhud`
- "add a button inside a container panel"
  - patch `widgets/containerwidget`
- "open a confirm popup from local UI"
  - create or mimic `screens/redux/popupdialog`
- "play a click sound with no world entity involved"
  - use `TheFrontEnd:GetSound()`
- "track which screen is on top"
  - inspect `scripts/frontend.lua`

## Minimal Patterns

Persistent HUD patch:

```lua
AddClassPostConstruct("widgets/controls", function(self)
    if self.mywidget ~= nil then
        return
    end
    self.mywidget = self.top_root:AddChild(require("widgets/mywidget")(self.owner))
end)
```

Transient popup:

```lua
local MyScreen = Class(Screen, function(self)
    Screen._ctor(self, "MyScreen")
    self.default_focus = self:AddChild(MyDialog())
end)

function MyScreen:Close()
    TheFrontEnd:PopScreen(self)
end
```
