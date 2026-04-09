# Debug Techniques

Use this file when a task needs targeted debugging or a narrow patch into an existing closure without copying the whole outer function.

This page includes a useful Lua debug technique derived from a third-party DST tutorial, not from official Klei scripts.
Treat it as a practical advanced tool, not the first default option.

## When This Technique Helps

Sometimes an official function looks like this:

```lua
local function foo()
end

local function bar()
end

local function onxxxfn()
    foo()
    bar()
end
```

A mod may want to change only the inner `bar()` behavior without copying the entire outer `onxxxfn()` chain.

That is where Lua debug helpers can help.

## High-Value Debug Helpers

Useful functions from Lua's debug library:

```lua
debug.getupvalue(f, up)
debug.setupvalue(f, up, value)
debug.getlocal(thread, level, local_index)
debug.setlocal(thread, level, local_index, value)
```

Practical intuition:

- `getupvalue` / `setupvalue`
  - inspect or replace referenced outer-scope values used by a function
- `getlocal` / `setlocal`
  - inspect or replace local variables inside a call frame

For DST mod patching, `getupvalue` and `setupvalue` are usually the higher-value pair.

## The Main Idea

If a target function closes over another helper function as an upvalue, you can:

1. inspect the target function's upvalues
2. locate the upvalue by name
3. replace it with a custom implementation

This lets you patch one inner dependency without re-copying the whole outer function body.

## Typical Pattern

```lua
local i = 0
local name, value

while name ~= "bar" do
    i = i + 1
    name, value = debug.getupvalue(onxxxfn, i)
end

debug.setupvalue(onxxxfn, i, function()
    print("bar?")
end)
```

This pattern:

- walks the upvalue list
- finds the one named `bar`
- swaps its implementation

## Why This Can Be Better Than Copying

Compared with copying the entire outer function and all nested helpers:

- less code duplication
- smaller compatibility surface when upstream code changes
- easier to patch one targeted helper only

This is especially useful when:

- the official outer function is large
- the real change is only one inner helper
- full replacement would be fragile

## Risks

This is an advanced technique.
Use it carefully.

Main risks:

- upvalue names or positions may change across game updates
- patching the wrong closure can silently do nothing or break behavior
- this is harder to read than a normal hook or post-init extension

## Preferred Order

Before using this technique, prefer:

1. a normal mod API hook
2. a post-init patch
3. a smaller override point already exposed by official code

Reach for debug upvalue patching only when those routes are not narrow enough.

## Rule Of Thumb

- Use `debug.getupvalue` / `debug.setupvalue` for narrow closure patching.
- Prefer upvalue replacement over wholesale function copying when only one inner helper needs to change.
- Document the target function and target upvalue clearly when you use this technique.
- Re-check this patch after game updates because closure layout is not a stable public API.
