# String Patterns

Use this file when the task adds names, inspect text, UI text, speech, or localization-related content.

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

## `modinfo.lua` Localization Is A Separate Case

Observed official `modinfo.lua` environment includes:

- `locale`
- `ChooseTranslationTable(tbl)`

Practical consequence:

- mod metadata can choose localized strings inside `modinfo.lua`
- this is separate from runtime `STRINGS` mutation

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

## Rule Of Thumb

- Use `STRINGS` for runtime names, descriptions, speech, and UI text.
- Use `ChooseTranslationTable` only for `modinfo.lua` metadata localization.
- Split large string blocks into helper files, but keep the loading path explicit.
