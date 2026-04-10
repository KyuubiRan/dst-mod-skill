# Modinfo Patterns

Use this file when the task edits `modinfo.lua`. It covers metadata, compatibility flags, and `configuration_options`.

## `modinfo.lua` Is Not Normal Runtime Lua

- treat `modinfo.lua` as a constrained metadata environment
- do not assume runtime globals or Lua standard-library helpers are available
- prefer literal tables, numeric `for`, and direct string concatenation
- avoid `pairs`, `ipairs`, `tostring`, `type`, `string`, `table`, and similar assumptions
- keep helpers tiny and intent-revealing

## Read These Fields Early

- `name`
- `description`
- `author`
- `version`
- `api_version`
- `dst_compatible`
- `client_only_mod`
- `all_clients_require_mod`
- `mod_dependencies`
- `configuration_options`

If config already exists, inspect its layout before adding new options.

## `mod_dependencies`

Use:

```lua
mod_dependencies = {
    "workshop-1234567890",
}
```

- use this for hard dependencies, not soft compatibility hints
- inspect this first when the task mentions dependency mods

## Localization In `modinfo.lua`

For standardized skill output, prefer:

- `MODINFO_TRANSLATIONS`
- `Translate(key)`

```lua
local MODINFO_TRANSLATIONS = {
    en = {
        ModName = "Example Mod",
    },
    zh = {
        ModName = "示例模组",
    },
}

local function Translate(key)
    return (MODINFO_TRANSLATIONS[locale] or MODINFO_TRANSLATIONS.en)[key] or key
end
```

- `modinfo.lua` localization is separate from runtime `STRINGS`
- keep the helper minimal
- do not depend on standard-library helpers while building localized config

## `configuration_options`

Typical shape:

```lua
configuration_options = {
    {
        name = "EXAMPLE_TOGGLE",
        label = "Example Toggle",
        hover = "Short explanation.",
        options = {
            { description = "Off", data = false },
            { description = "On", data = true },
        },
        default = false,
    },
}
```

High-frequency fields:

- `name`
- `label`
- `hover`
- `options`
- `default`

Rules:

- keep option names stable after release when possible
- keep `data` values simple and explicit
- keep `default` identical to one of the option `data` values

## Config Section Headers

Use a fake config entry as a section label when grouping character, equipment, UI, or debug options.

Recommended helper:

```lua
local function MakeConfigSectionHeader(label)
    return {
        name = "",
        label = label,
        options = {
            {
                description = "",
                data = false,
            },
        },
        default = false,
    }
end
```

- `titlefn` describes shape, not intent
- `MakeConfigSectionHeader` states what the helper returns

Use it like this:

```lua
configuration_options = {
    MakeConfigSectionHeader("General"),
    {
        name = "EXAMPLE_TOGGLE",
        label = "Example Toggle",
        options = {
            { description = "Off", data = false },
            { description = "On", data = true },
        },
        default = false,
    },

    MakeConfigSectionHeader("UI"),
    {
        name = "SHOW_EXAMPLE",
        label = "Show Example",
        options = {
            { description = "Yes", data = true },
            { description = "No", data = false },
        },
        default = true,
    },
}
```

## Safe Helper Style

Good helper traits:

- small
- table-literal heavy
- no standard-library dependency
- no hidden runtime assumptions

Good examples:

- localized lookup helper with direct table access
- boolean option builder
- config section-header builder
- numeric `for` loop over a literal option list

Bad examples:

- building config with `pairs(...)`
- using `table.insert(...)`
- using `string.format(...)`
- using `tostring(...)`
- assuming runtime-only globals from `modmain.lua`

## Key Mapping Options

If the user wants hotkey config inside `configuration_options`, keep the helper literal and conservative.

```lua
local default_suffix = " (Default)"

local function MakeKeyOptions(default_value)
    local options = {
        { description = "A", data = 97 },
        { description = "B", data = 98 },
        { description = "C", data = 99 },
        { description = "D", data = 100 },
        { description = "E", data = 101 },
        { description = "F", data = 102 },
        { description = "G", data = 103 },
        { description = "H", data = 104 },
        { description = "I", data = 105 },
        { description = "J", data = 106 },
        { description = "K", data = 107 },
        { description = "L", data = 108 },
        { description = "M", data = 109 },
        { description = "N", data = 110 },
        { description = "O", data = 111 },
        { description = "P", data = 112 },
        { description = "Q", data = 113 },
        { description = "R", data = 114 },
        { description = "S", data = 115 },
        { description = "T", data = 116 },
        { description = "U", data = 117 },
        { description = "V", data = 118 },
        { description = "W", data = 119 },
        { description = "X", data = 120 },
        { description = "Y", data = 121 },
        { description = "Z", data = 122 },
    }

    for i = 1, #options do
        if options[i].data == default_value then
            options[i].description = options[i].description .. default_suffix
            break
        end
    end

    return options
end
```

```lua
{
    name = "HOTKEY_SKILL",
    label = "Skill Hotkey",
    hover = "Hotkey for the skill.",
    options = MakeKeyOptions(122),
    default = 122,
}
```

Rules:

- use explicit keycode tables in `modinfo.lua`
- mark the default option by mutating the matched literal entry in a numeric loop
- keep key labels and keycode values close together
- if the list gets large, still prefer a literal table; split it into a tiny helper table if needed
- avoid `string.char(...)`, `table.insert(...)`, `pairs(...)`, `ipairs(...)`, and `string.format(...)`

## Intent Index

- "I need to classify the mod type"
  - inspect `client_only_mod` and `all_clients_require_mod`
- "I need to add dependency workshop mods"
  - inspect `mod_dependencies`
- "I need to split config into sections"
  - use `MakeConfigSectionHeader(...)`
- "I need to add hotkey config in `modinfo.lua`"
  - use a literal key option builder such as `MakeKeyOptions(...)`
- "I need localized mod metadata"
  - keep localization inside `modinfo.lua`
  - prefer `MODINFO_TRANSLATIONS` and `Translate(...)`
- "I need to add config helpers"
  - keep them minimal and standard-library-free

## Common Failure Points

- game fails while loading mod metadata
  - `modinfo.lua` used unavailable helpers or globals
- config section label breaks option parsing
  - fake header entry shape does not match normal config-entry expectations
- localized metadata works but config builder crashes
  - helper function used unavailable library calls
- option defaults behave strangely
  - `default` does not exactly match one of the option `data` values

## Rule Of Thumb

- Keep `modinfo.lua` boring.
- Prefer literals over abstraction.
- If you add a helper, make it tiny and intent-revealing.
- For config grouping, prefer `MakeConfigSectionHeader(...)` over vague names like `titlefn`.
