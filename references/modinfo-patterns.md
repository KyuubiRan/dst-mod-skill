# Modinfo Patterns

Use this file when the task edits `modinfo.lua`.

This page is for metadata, compatibility flags, and `configuration_options` structure.
Read it before writing non-trivial `modinfo.lua` logic.

## `modinfo.lua` Is Not Normal Runtime Lua

Practical rule:

- treat `modinfo.lua` as a constrained metadata environment
- do not assume normal runtime globals or standard-library helpers are available
- keep the file simple and data-first

Important limitation observed in real mod usage:

- do not rely on Lua standard-library helpers inside `modinfo.lua`
- avoid `pairs`, `ipairs`, `tostring`, `type`, and similar assumptions
- also avoid depending on `string`, `table`, and other library namespaces being present

Practical consequence:

- prefer literal tables
- prefer numeric `for` loops over iterator helpers when you truly need a loop
- prefer explicit string concatenation over helper formatting
- do not write clever meta-programming in `modinfo.lua`

## Read These Fields Early

When inspecting an existing mod, start here:

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

If the mod already has config, inspect the config layout before adding more options.

## `mod_dependencies`

Use:

```lua
mod_dependencies = {
    "workshop-1234567890",
}
```

Use it for:

- hard dependency declaration
- forcing workshop dependency install or load expectations

Practical rule:

- use this for actual dependencies, not soft compatibility hints

## Localization In `modinfo.lua`

Existing patterns may use:

- `locale`
- `ChooseTranslationTable(...)`
- a custom translation table plus a small lookup helper

For standardized skill output, prefer this format:

- `MODINFO_TRANSLATIONS`
- `Translate(key)`

Recommended standardized shape:

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

Practical rule:

- metadata localization in `modinfo.lua` is separate from runtime `STRINGS`
- keep the translation helper extremely small
- do not depend on standard-library helpers while building localized config structures
- this local translation-table pattern is a recommended way to organize `modinfo.lua` text
- do not treat that pattern as the runtime i18n solution for normal mod code

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

Practical rule:

- keep option names stable after release when possible
- keep `data` values simple and explicit
- keep `default` identical to one of the option `data` values

## Config Section Headers

Observed practical pattern from real mod usage:

- insert a fake config entry that only acts as a section label

This is useful for:

- grouping character options
- grouping equipment options
- grouping UI or debug options

Recommended helper name:

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

Why this name:

- `titlefn` describes implementation shape, not intent
- `MakeConfigSectionHeader` states exactly what the helper produces
- the name is still short enough for repeated use in `configuration_options`

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

## Safe Helper Style For `modinfo.lua`

Good helper traits:

- small
- table-literal heavy
- no standard-library dependency
- no hidden runtime assumptions

Good examples:

- localized lookup helper with direct table access
- boolean yes or no option builder
- config section-header builder
- numeric `for` loop over a literal option list

Bad examples:

- building config with `pairs(...)`
- using `table.insert(...)`
- using `string.format(...)`
- using `tostring(...)`
- assuming runtime-only globals from `modmain.lua`

## Key Mapping Options In `modinfo.lua`

If the user wants hotkey config inside `configuration_options`, keep the key mapping helper literal and conservative.

Recommended shape:

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

Use it like this:

```lua
{
    name = "HOTKEY_SKILL",
    label = "Skill Hotkey",
    hover = "Hotkey for the skill.",
    options = MakeKeyOptions(122),
    default = 122,
}
```

Why this shape is safe:

- literal table, no runtime-generated alphabet
- numeric `for`, not `pairs` or `ipairs`
- string concatenation only
- no `string.char`, `table.insert`, or other standard-library dependency

## Key Mapping Rules

Practical rule:

- use explicit keycode tables in `modinfo.lua`
- mark the default option by mutating the matched literal entry in a numeric loop
- keep key labels and keycode values close together for later editing

If the key list gets large:

- still prefer a literal table over dynamic generation inside `modinfo.lua`
- if readability becomes a problem, split the list into a tiny helper table in the same file

Avoid these patterns in `modinfo.lua`:

- generating `A` to `Z` through `string.char(...)`
- appending options with `table.insert(...)`
- walking option tables with `pairs(...)` or `ipairs(...)`
- formatting labels with `string.format(...)`

## Intent Index

Use this when the user describes the need in plain language.

- "I need to classify the mod type"
  - inspect `client_only_mod` and `all_clients_require_mod`
- "I need to add dependency workshop mods"
  - inspect `mod_dependencies`
- "I need to split config into sections"
  - use `MakeConfigSectionHeader(...)`
- "I need to add hotkey config in `modinfo.lua`"
  - use a literal key option builder such as `MakeKeyOptions(...)`
  - avoid Lua standard-library helpers while building the option list
- "I need localized mod metadata"
  - keep localization inside `modinfo.lua`
  - prefer standardized names such as `MODINFO_TRANSLATIONS` and `Translate(...)`
  - do not mix it with runtime `STRINGS`
- "I need to add config helpers"
  - keep them minimal and standard-library-free

## Common Failure Points

- game fails while loading mod metadata
  - `modinfo.lua` used unavailable helpers or globals
- config section label breaks option parsing
  - fake header entry shape does not match normal config-entry expectations
- localized metadata works but config builder crashes
  - helper function used library calls not available in `modinfo.lua`
- option defaults behave strangely
  - `default` does not exactly match one of the option `data` values

## Rule Of Thumb

- Keep `modinfo.lua` boring.
- Prefer literals over abstraction.
- If you add a helper, make it tiny and intent-revealing.
- For config grouping, prefer `MakeConfigSectionHeader(...)` over vague names like `titlefn`.
