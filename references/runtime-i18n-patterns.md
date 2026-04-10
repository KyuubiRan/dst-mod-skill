# Runtime I18n Patterns

Use this file when the task designs or refactors runtime localization for a mod.

This page is about normal mod runtime text, not `modinfo.lua`.
For `modinfo.lua` metadata localization, read `references/modinfo-patterns.md` instead.

## Official Runtime Foundations

Verified in official files:

- `scripts/modutil.lua`
  - mod environment exposes `LoadPOFile(path, lang)`
- `scripts/translator.lua`
  - `Translator:LoadPOFile(...)`
  - `TranslateStringTable(tbl)`
- `scripts/languages/loc.lua`
  - official language swaps call `TranslateStringTable(STRINGS)`
- `scripts/stringutil.lua`
  - runtime lookups use `GetString(...)`

Practical consequence:

- the official runtime translation system exists
- it is `.po` plus translator based
- runtime text still resolves through `STRINGS`

## Recommended Mod-Owned Runtime Strategy

For most mods, prefer a Lua-table runtime i18n layer over generating full Lua dumps from `.po`.

Recommended approach:

1. choose the locale once in a small loader module
2. load one locale-specific common table for mod-owned strings
3. merge that table into `STRINGS`
4. for character speech, deep-copy the default base speech table first
5. apply only sparse locale overrides for the custom character

Why this is recommended:

- smaller locale files
- easier reviews
- less generated noise
- character mods can inherit future default lines automatically from the base table
- common strings and character speech stay conceptually separate

## Recommended Directory Shape

A clean layout is:

```text
scripts/languages/
├─ i18n.lua
├─ common_en.lua
├─ common_zh.lua
├─ speech_mychar_en.lua
├─ speech_mychar_zh.lua
├─ speech_sidekick_en.lua
└─ speech_sidekick_zh.lua
```

Use these roles:

- `i18n.lua`
  - locale selection and loading orchestration
- `common_<locale>.lua`
  - mod-owned additions to `STRINGS`
- `speech_<character>_<locale>.lua`
  - sparse overrides for the character speech table
- sidekick or companion speech files
  - separate localized tables, preferably keyed by speech path or symbolic id

## Common Strings Should Be Mod-Owned Additions

Recommended shape for `common_<locale>.lua`:

```lua
return {
    NAMES = {
        MY_ITEM = "My Item",
    },
    RECIPE_DESC = {
        MY_ITEM = "Craft a thing.",
    },
    ACTIONS = {
        MY_ACTION = "Use",
    },
    UI = {
        TOOLTIP = {
            MY_TOOLTIP = "Drag with RMB.",
        },
    },
    CHARACTERS = {
        GENERIC = {
            DESCRIBE = {
                MY_ITEM = "A custom thing.",
            },
        },
    },
    MYMOD = {
        SKILLS = {
            TITLE = "Skill",
        },
    },
}
```

Practical rule:

- `common_<locale>.lua` should only describe strings your mod owns
- do not mirror the entire global `STRINGS` tree when only a few branches are needed

## Character Speech Should Start From `STRINGS.CHARACTERS.GENERIC`

Verified in `scripts/stringutil.lua`:

- `GetString(...)` resolves character strings
- when a character-specific branch misses a value, it falls back to `STRINGS.CHARACTERS.GENERIC`

Practical rule:

- for character mods, the correct base speech table is `STRINGS.CHARACTERS.GENERIC`
- do not build a full copied speech file from scratch when you only need differences
- do not think of the base as a `WILSON` table; the default fallback table is `GENERIC`

Recommended pattern:

1. deep-copy `STRINGS.CHARACTERS.GENERIC`
2. merge the custom character's sparse locale overrides into that copy
3. assign the merged result to `STRINGS.CHARACTERS.<YOURCHAR>`

## Sparse Character Speech File

Recommended shape for `speech_mychar_<locale>.lua`:

```lua
return {
    DESCRIBE = {
        MY_ITEM = "This is mine.",
    },
    BATTLECRY = {
        GENERIC = "Let's do this.",
    },
    ANNOUNCE_ENTER_DARK = "Too dark...",
}
```

Practical rule:

- keep only changed lines here
- inherit everything else from the copied generic base

## Standard Loader Shape

Recommended `scripts/languages/i18n.lua` structure:

```lua
local supported = {
    en = true,
    zh = true,
}

local function ResolveLocale()
    local lang = GetModConfigData("LANGUAGE")
    if lang == nil or lang == "auto" then
        lang = LOC.GetLocaleCode()
    end
    if not supported[lang] then
        lang = "en"
    end
    return lang
end

local function DeepCopy(value)
    if type(value) ~= "table" then
        return value
    end

    local result = {}
    for k, v in pairs(value) do
        result[k] = DeepCopy(v)
    end
    return result
end

local function DeepMerge(dst, src)
    for k, v in pairs(src) do
        if type(v) == "table" then
            if type(dst[k]) ~= "table" then
                dst[k] = {}
            end
            DeepMerge(dst[k], v)
        else
            dst[k] = v
        end
    end
end

local locale = ResolveLocale()

local common = require("languages/common_" .. locale)
DeepMerge(STRINGS, common)

local speech = DeepCopy(STRINGS.CHARACTERS.GENERIC)
DeepMerge(speech, require("languages/speech_mychar_" .. locale))
STRINGS.CHARACTERS.MYCHAR = speech
```

## Companion Or Proxy Speaker Text

If a second speaker responds to the main character's lines, do not key that table by the final translated sentence text.

Avoid this pattern:

- using localized output strings as lookup keys
- for example indexing by `STRINGS.CHARACTERS.MYCHAR.DESCRIBE.MY_ITEM`

Why it is fragile:

- line text changes break the lookup
- different locales change keys
- punctuation or override edits become data-breaking

Prefer one of these:

- path-keyed tables
  - `DESCRIBE.MY_ITEM`
  - `BATTLECRY.GENERIC`
- symbolic ids
  - `MYITEM_DESCRIBE`
  - `GENERIC_BATTLECRY`

Recommended shape:

```lua
return {
    DESCRIBE = {
        MY_ITEM = "Don't touch that.",
    },
    BATTLECRY = {
        GENERIC = "Go!",
    },
}
```

Then read from the same path on the current locale table instead of using the translated string as the key.

## Optional Official `.po` Route

The official mod environment exposes:

```lua
LoadPOFile(path, lang)
```

And official runtime translation is based on:

- `LanguageTranslator:LoadPOFile(...)`
- `TranslateStringTable(STRINGS)`

Practical rule:

- this is a real official runtime capability
- use it when you explicitly want `.po`-based workflow
- for many gameplay mods, a Lua delta-table approach is simpler to maintain

## Intent Index

Use this when the user describes the problem in plain language.

- "I want proper runtime i18n for my mod"
  - start with locale-selected common tables plus a small loader
- "I want to avoid generating giant speech files"
  - deep-copy `STRINGS.CHARACTERS.GENERIC` and merge sparse overrides
- "I am making a character mod"
  - treat `STRINGS.CHARACTERS.GENERIC` as the speech base
- "I have common strings and character speech mixed together"
  - split `common_<locale>.lua` from `speech_<character>_<locale>.lua`
- "I have a second speaker that keys by translated lines"
  - replace text-as-key with path-keyed or symbolic-id tables
- "I want `.po` based localization"
  - inspect `LoadPOFile(...)` and `TranslateStringTable(STRINGS)`

## Common Failure Points

- locale files are huge and hard to diff
  - mirrored too much of `STRINGS`
- character speech drifts from base game over time
  - copied full speech tables instead of inheriting from `GENERIC`
- runtime text lookup breaks after translation edits
  - keyed companion logic by translated sentence values
- common strings accidentally overwrite too much global state
  - merged a full tree instead of a sparse mod-owned branch set
- runtime i18n and `modinfo.lua` i18n got mixed together
  - two different systems were treated as one

## Rule Of Thumb

- `modinfo.lua` localization is one system.
- runtime localization is another system.
- For runtime text, keep locale files sparse.
- For character mods, copy `STRINGS.CHARACTERS.GENERIC` and override only the differences.
