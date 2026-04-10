# Runtime I18n Patterns

Use this file when the task designs or refactors runtime localization for a mod. This page is for runtime text, not `modinfo.lua` metadata.

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

Implication:

- official runtime translation exists
- it is `.po` plus translator based
- runtime text still resolves through `STRINGS`

Verified mod-side helper:

- `scripts/modutil.lua`
  - exposes `LoadPOFile(path, lang)` in the mod environment

## Recommended Runtime Strategy

For most mods, prefer a Lua-table runtime i18n layer over generating full Lua dumps from `.po`.

Recommended approach:

1. choose the locale once in a small loader module
2. load one locale-specific common table for mod-owned strings
3. merge that table into `STRINGS`
4. deep-copy the base speech table for character speech
5. apply only sparse locale overrides for the custom character

Benefits:

- smaller locale files
- easier reviews
- less generated noise
- character mods inherit future default lines from the base table
- common strings and character speech stay separate

Practical rule:

- use Lua delta tables when maintainability matters more than matching the official `.po` pipeline
- use `.po` when the project explicitly wants translator tooling or existing `.po` workflow

## Recommended Directory Shape

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

Roles:

- `i18n.lua`
  - locale selection and loading orchestration
- `common_<locale>.lua`
  - mod-owned additions to `STRINGS`
- `speech_<character>_<locale>.lua`
  - sparse overrides for a character speech table
- sidekick or companion speech files
  - separate localized tables keyed by speech path or symbolic id

## Common Strings Should Be Mod-Owned Additions

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

- `common_<locale>.lua` should only describe strings your mod owns
- do not mirror the entire global `STRINGS` tree when only a few branches are needed

## Character Speech Should Start From `STRINGS.CHARACTERS.GENERIC`

Verified in `scripts/stringutil.lua`:

- `GetString(...)` resolves character strings
- missing character-specific values fall back to `STRINGS.CHARACTERS.GENERIC`

Rules:

- the correct base speech table is `STRINGS.CHARACTERS.GENERIC`
- do not build a full copied speech file from scratch when you only need differences
- do not think of the base as `WILSON`; the default fallback table is `GENERIC`

Recommended pattern:

1. deep-copy `STRINGS.CHARACTERS.GENERIC`
2. merge sparse locale overrides into that copy
3. assign the merged result to `STRINGS.CHARACTERS.<YOURCHAR>`

## Sparse Character Speech File

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

- keep only changed lines here
- inherit everything else from the copied generic base

## Standard Loader Shape

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

## Asset, String, And I18n Boundaries

Keep these systems separate:

- runtime i18n
  - locale choice, table merge, optional `.po` loading
- runtime strings
  - the final `STRINGS` tree content
- assets
  - atlases, textures, anim zips, sounds

Translating a name does not register an icon.
Registering an icon does not populate a localized `STRINGS.NAMES` entry.

## Companion Or Proxy Speaker Text

Do not key a second speaker table by the final translated sentence text.

- avoid localized output strings as lookup keys, for example `STRINGS.CHARACTERS.MYCHAR.DESCRIBE.MY_ITEM`
- line text changes, locale changes, and punctuation edits will break the lookup

Prefer:

- path-keyed tables
  - `DESCRIBE.MY_ITEM`
  - `BATTLECRY.GENERIC`
- symbolic ids
  - `MYITEM_DESCRIBE`
  - `GENERIC_BATTLECRY`

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

Read from the same path on the current locale table instead of using translated text as the key.

## Optional Official `.po` Route

The official mod environment exposes:

```lua
LoadPOFile(path, lang)
```

Official runtime translation is based on:

- `LanguageTranslator:LoadPOFile(...)`
- `TranslateStringTable(STRINGS)`

- this is a real official runtime capability
- use it when you explicitly want `.po` workflow
- for many gameplay mods, a Lua delta-table approach is simpler to maintain

Minimal official-style route:

1. call `LoadPOFile(path, lang)`
2. ensure the target strings exist in `STRINGS`
3. call or rely on `TranslateStringTable(STRINGS)` in the relevant flow

If the project does not already want `.po`, the Lua-table route is usually simpler.

## Intent Index

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
- runtime locale files tried to solve missing asset or atlas issues
  - wrong subsystem
- direct string writes and locale loader both overwrite the same branch without a clear order
  - final runtime text becomes unpredictable

## Fast Router

- "I only need a few new strings"
  - read `references/string-patterns.md`
- "I need runtime locale switching"
  - stay on this page
- "I need metadata/config translation"
  - read `references/modinfo-patterns.md`
- "the text is right but art is missing"
  - read `references/asset-patterns.md`

## Rule Of Thumb

- `modinfo.lua` localization is one system.
- runtime localization is another system.
- keep runtime locale files sparse.
- for character mods, copy `STRINGS.CHARACTERS.GENERIC` and override only the differences.
