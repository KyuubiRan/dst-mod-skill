# UI Pitfalls

Use this file when a DST UI patch works in one context, duplicates, leaks, or touches the wrong layer.

If the route itself is unclear, read `references/ui-patch-patterns.md` first.

## Fast Router

- patch runs, but the wrong screen or widget owns the behavior
  - check wrong-layer patching
- widget appears twice or keeps rebuilding
  - check constructor duplication
- hotkeys or callbacks keep firing after close
  - check teardown leaks
- host works but dedicated crashes
  - check local-only globals and guards
- button clicks but gameplay state does not sync correctly
  - check UI versus authority boundary
- controller or keyboard navigation feels broken
  - check `default_focus` and `OnControl(...)`

## Patching The Wrong Layer

Common mistake:

- patch `frontend.lua` for a feature that really belongs to one screen
- patch `playerhud` for a small persistent HUD child that should live in `controls`
- patch `controls` when the real issue is screen-owned popup flow or overlay ordering in `playerhud`

Fix:

- map the feature to `controls`, `playerhud`, transient widget, popup screen, or `frontend` before editing

## Constructor Duplication

`AddClassPostConstruct(...)` runs after every future constructor call.

Common mistake:

- blindly add a child each time without checking whether the instance already owns it

Symptoms:

- duplicate HUD widgets
- multiple buttons on the same panel
- the patch looks fine once, then duplicates after rebuild

Fix:

- store the handle on `self`
- guard with `if self.somechild ~= nil then return end`

## Teardown Leaks

UI often breaks because handlers outlive the widget.

Common mistake:

- register input handlers, listeners, or tasks
- never remove them in `Close()` or `OnDestroy()`

Symptoms:

- hotkeys keep firing after the screen closes
- callbacks run against dead widgets
- reopened UI responds multiple times

Fix:

- pair every registration with an explicit cleanup path

## Local Globals On The Wrong Runtime

Common mistake:

- use `ThePlayer`, `TheFrontEnd`, or `TheInput` in code that also runs on dedicated server

Symptoms:

- works in a listen server test
- crashes or silently fails on dedicated

Fix:

- guard local UI code with `if TheNet:IsDedicated() then return end`
- guard HUD access with `if ThePlayer ~= nil and ThePlayer.HUD ~= nil then ... end`

## UI Mutates Gameplay Directly

Common mistake:

- UI button calls server-only components directly
- client widget reads `inst.components` instead of replica data

Symptoms:

- host works
- remote clients desync or no-op

Fix:

- keep UI local
- read replica or netvars on clients
- send intent through RPC or action flow for authoritative changes

## Wrong Root Or Wrong Draw Order

Common mistake:

- add a fullscreen overlay under the wrong root
- add a HUD child to a branch that gets hidden or ordered behind other UI

Symptoms:

- widget exists but is invisible
- popup appears behind another layer
- overlay clips or anchors incorrectly

Fix:

- inspect `playerhud` roots such as `overlayroot`, `under_root`, `root`, and `over_root`
- inspect `controls` root ownership before attaching children

## Focus And Controller Breakage

Common mistake:

- build a popup screen without `default_focus`
- assume mouse-only interaction

Symptoms:

- controller cannot focus the dialog
- keyboard confirm or cancel does nothing

Fix:

- set `default_focus`
- implement `OnControl(...)` when the screen should consume controls
- inspect `widgets/screen.lua` and `screens/redux/popupdialog.lua`

## Over-Patching `frontend.lua`

Common mistake:

- patch the top-level frontend stack for a feature that could be a normal screen or widget

Why it is risky:

- `frontend.lua` owns global screen stack behavior
- broad patches here can affect unrelated menus or screens

Fix:

- prefer a custom screen plus `TheFrontEnd:PushScreen(...)`
- patch `frontend.lua` only for true screen-stack or frontend-root behavior

## Alpha Fade Trap

Observed official warning in `scripts/frontend.lua`:

- the `"alpha"` fade mode can leave screen children non-clickable and visually wrong afterward

Practical rule:

- do not casually reuse the alpha fade on screens that will stay interactive
- inspect the existing frontend fade flow before patching fade behavior
