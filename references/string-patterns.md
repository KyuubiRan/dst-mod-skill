# String Patterns

Use this file when the task adds names, inspect text, UI text, speech, or localization-related content.
Read `references/runtime-i18n-patterns.md` too when the task is about the overall runtime i18n architecture rather than one or two direct `STRINGS` writes.
Read `references/modinfo-patterns.md` instead when the text belongs in `modinfo.lua` metadata or config UI.

## Runtime Strings Usually Modify `STRINGS` Directly

For normal mod runtime strings, the common pattern is to assign into `STRINGS` from `modmain.lua` or a file loaded by `modimport(...)`.

Typical targets:

```lua
STRINGS.NAMES.MY_PREFAB = "My Prefab"
STRINGS.RECIPE_DESC.MY_PREFAB = "Builds a thing."
STRINGS.CHARACTERS.GENERIC.DESCRIBE.MY_PREFAB = "It exists."
STRINGS.ACTIONS.MY_ACTION = "Use"
```

Practical consequence:

- there is no special mod string file required for basic runtime localization
- many mods keep string writes in a separate helper file and call `modimport("strings")`

For larger runtime localization systems, do not stop at ad hoc assignments.
Use a locale loader plus sparse locale tables as described in `references/runtime-i18n-patterns.md`.

## Keep Keys Uppercase

Official string tables commonly use uppercase keys.

Typical shape:

```lua
STRINGS.NAMES[string.upper("my_prefab")] = "My Prefab"
```

For prefab and action identifiers, uppercase keys are the safest default when writing into `STRINGS`.

## Common String Families

- `STRINGS.NAMES`
  - display names
- `STRINGS.RECIPE_DESC`
  - crafting descriptions
- `STRINGS.CHARACTERS.<CHAR>.DESCRIBE`
  - inspect speech
- `STRINGS.ACTIONS`
  - action button labels
- `STRINGS.UI`
  - UI-facing text

## Asset And String Are Separate Wires

Do not confuse text registration with icon or asset registration.

Typical split:

- `STRINGS.NAMES.MY_ITEM`
  - display text
- `Asset("ATLAS", "images/inventoryimages/my_item.xml")`
  - icon resource declaration

If a recipe entry exists but the icon is missing, the bug may be in assets, not strings.
If the icon exists but the text is blank, the bug may be in `STRINGS`, not assets.

## `modinfo.lua` Localization Is A Separate Case

For broader `modinfo.lua` rules such as config grouping and environment limits, also read `references/modinfo-patterns.md`.

Observed official `modinfo.lua` environment includes:

- `locale`
- `ChooseTranslationTable(tbl)`

Practical consequence:

- mod metadata can choose localized strings inside `modinfo.lua`
- this is separate from runtime `STRINGS` mutation
- for standardized new code, prefer explicit names such as `MODINFO_TRANSLATIONS` and `Translate(key)`
- do not reuse the modinfo translation helper as the default runtime i18n approach

Typical modinfo-side shape:

```lua
name = ChooseTranslationTable({
    "English Name",
    ["zh"] = "中文名",
})
```

## Splitting String Files

A clean mod pattern is:

- keep registrations in `modmain.lua`
- keep long string tables in a separate file
- load it through `modimport(...)`

Example:

```lua
modimport("scripts/my_strings")
```

Use this when:

- direct `STRINGS` assignments are getting long
- the mod does not yet need a full locale loader
- you want runtime text split out without overengineering i18n

If the mod later grows real locale tables, that helper file can become the loader entry point.

## Fast Router

- one or two fixed runtime strings
  - direct `STRINGS` writes are enough
- many runtime strings but one language
  - split with `modimport(...)`
- real locale switching or sparse locale tables
  - read `references/runtime-i18n-patterns.md`
- metadata or config labels in `modinfo.lua`
  - read `references/modinfo-patterns.md`

## Rule Of Thumb

- Use `STRINGS` for runtime names, descriptions, speech, and UI text.
- Use `ChooseTranslationTable` only for `modinfo.lua` metadata localization.
- Split large string blocks into helper files, but keep the loading path explicit.
- When the mod has real runtime localization, prefer sparse locale tables and a dedicated loader module.
