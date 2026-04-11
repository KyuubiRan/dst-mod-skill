# Protected Call Patterns

Use this file when the task needs Lua protected calls such as `pcall(...)` or `xpcall(...)`, especially around `json.decode(...)`, `json.encode(...)`, optional `require(...)`, or fragile deserialization boundaries.

This page is about narrow Lua-side error containment.
If the task is mainly about persistent local files, also read `references/patterns/persistent-string-patterns.md`.
If the task is mainly about entity or world save lifecycle, also read `references/patterns/persistence-patterns.md`.

## What `pcall` And `xpcall` Are For

Use protected calls when one small boundary may fail and you want the caller to recover cleanly instead of crashing the whole flow.

Observed official fits:

- decode JSON from network or cached strings
- load local persistent profile data
- try an optional `require(...)`
- encode one payload and fall back when serialization fails

## Core Shapes

Basic protected call:

```lua
local ok, result = pcall(function()
    return json.decode(data)
end)
```

Argument-passing form:

```lua
local ok, speechfile = pcall(require, "speech_" .. character)
```

Protected call with an error handler:

```lua
local ok, result = xpcall(function()
    return json.encode(moddata)
end, generic_error)
```

Practical rule:

- `pcall(...)`
  - simplest recovery path
- `xpcall(...)`
  - use when you also want a custom error handler or richer logging path

## Observed Official Examples

- `scripts/craftingmenuprofile.lua`
  - protects `json.decode(data)` while loading local UI profile data
- `scripts/screens/modsscreen.lua`
  - protects JSON decode of remote result strings
- `scripts/screens/multiplayermainscreen.lua`
  - protects MOTD JSON decode before using cached data
- `scripts/screens/redux/multiplayermainscreen.lua`
  - protects stored JSON from generic KV values
- `scripts/tools/getmissingstrings.lua`
  - uses `pcall(require, ...)` for optional speech files
- `scripts/screens/worldgenscreen.lua`
  - uses `xpcall(..., generic_error)` when encoding mod worldgen payload

## `pcall` For Decode Paths

This is the most common official pattern.

Typical shape:

```lua
local ok, decoded = pcall(function()
    return json.decode(data)
end)

if ok and type(decoded) == "table" then
    -- use decoded data
end
```

Why this matters:

- cached files may be empty, stale, or malformed
- remote responses may not be valid JSON
- old formats may no longer decode cleanly

Practical rule:

- protect the decode call
- then validate the decoded type before using it

## `pcall` For Optional `require(...)`

Official code also uses the direct callable form:

```lua
local ok, mod = pcall(require, modulename)
```

Use this when:

- the file may not exist
- a compatibility module is optional
- the absence of the module should degrade gracefully

Do not use this to silently hide required hard dependencies.

## `xpcall` For Important Encode Steps

Observed official example:

- `scripts/screens/worldgenscreen.lua`

Use `xpcall(...)` when:

- serialization failure should be logged through a known handler
- the payload is important enough that you want better error reporting than a bare boolean

Practical rule:

- default to `pcall(...)`
- reach for `xpcall(...)` only when the custom error-handler path is actually useful

## Keep The Protected Boundary Narrow

Good:

- protect `json.decode(...)`
- protect `json.encode(...)`
- protect one optional `require(...)`

Bad:

- wrap a whole update function, screen constructor, or gameplay branch in one giant `pcall(...)`

Why:

- broad protected calls hide the real failing line
- they make state recovery unclear
- they can accidentally swallow real bugs

## Protected Call Plus Validation

A successful protected call does not mean the value is usable.

Still validate:

- `decoded ~= nil`
- `type(decoded) == "table"` when a table is expected
- required keys exist before use

Observed official style:

- decode
- check `status`
- check the decoded value shape
- only then assign live state

## Common Mistakes

- calling `pcall(json.decode(data))`
  - wrong, because the decode runs before `pcall(...)`
- assuming `ok == true` means the data shape is correct
- swallowing a failure and then continuing with partially-invalid state
- wrapping large unrelated logic instead of the fragile boundary itself
- using `xpcall(...)` without a meaningful error handler

## Minimal Templates

Safe JSON decode:

```lua
local ok, decoded = pcall(function()
    return json.decode(data)
end)

if ok and type(decoded) == "table" then
    state = decoded
end
```

Safe JSON encode with fallback:

```lua
local ok, encoded = pcall(function()
    return json.encode(tbl)
end)

if ok then
    TheSim:SetPersistentString(key, encoded, false)
else
    print("Failed to encode", key)
end
```

Optional require:

```lua
local ok, mod = pcall(require, "speech_" .. character)
if ok then
    return mod
end
```

## Rule Of Thumb

- protect narrow decode, encode, and optional-require boundaries
- validate the result after the protected call
- use `pcall(...)` by default
- use `xpcall(...)` when the custom error handler materially improves the failure path
