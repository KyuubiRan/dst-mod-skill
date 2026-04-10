# Character Patterns

Use this file when the task is a playable character mod rather than a normal creature prefab.

If the task is mainly about entry-file choice first, read `references/entrypoint-patterns.md`.
If the task is mainly about runtime i18n layout, also read `references/runtime-i18n-patterns.md`.
If the task is mainly about recipes unlocked by character progression, also read `references/recipe-patterns.md`.

## Playable Characters Do Not Start From A Normal Creature Prefab

Official playable characters are built through `scripts/prefabs/player_common.lua`.

Observed official shape:

- character prefab files such as `scripts/prefabs/wilson.lua`, `scripts/prefabs/wendy.lua`, and `scripts/prefabs/wormwood.lua`
- `local MakePlayerCharacter = require("prefabs/player_common")`
- `return MakePlayerCharacter(name, prefabs, assets, common_postinit, master_postinit, starting_inventory)`

Practical consequence:

- do not start a playable character from a plain `CreateEntity()` item or creature template
- use the player-character pattern first, then add custom behavior inside the post-init callbacks

## Typical Mod File Set

Usually involved:

- `modinfo.lua`
- `modmain.lua`
- `prefabs/<character>.lua`
- runtime string files
- character art and portrait assets
- optional `scripts/prefabs/skilltree_<character>.lua`

Common asset families:

- `images/avatars/`
- `images/map_icons/`
- `images/saveslot_portraits/`
- `images/selectscreen_portraits/`
- `bigportraits/`
- optional skill atlas or skill background art

## What Belongs In `modmain.lua`

For character mods, `modmain.lua` usually owns:

- `PrefabFiles = { "<character>" }`
- top-level shared `Assets`
- `AddMinimapAtlas("images/map_icons/<character>.xml")`
- `AddModCharacter("<character>", "FEMALE")` or the matching gender
- optional startup item glue
- optional skill-tree registration glue

Keep the root file as the registration hub.
Move the actual player prefab logic into `prefabs/<character>.lua`.

## Character Prefab Shape

Official character prefabs usually contain:

- local `assets`
- local `prefabs`
- optional starting-inventory table routing by game mode
- `common_postinit(inst)`
- `master_postinit(inst)`
- `return MakePlayerCharacter(...)`

Practical rule:

- put client-visible tags, AnimState overrides, netvars, and local helper methods in `common_postinit`
- put authoritative stat tuning, server-only components, and authoritative listeners in `master_postinit`

## What `player_common.lua` Already Gives You

Observed in `scripts/prefabs/player_common.lua`:

- player entity pieces and common tags
- talker and many baseline player systems
- client/server split and `SetPristine()`
- classified, inventory, locomotor, combat, health, hunger, sanity, and other baseline player components
- `skilltreeupdater`

Practical consequence:

- do not rebuild the whole player baseline by hand
- tune or extend the existing player instead of re-adding ordinary player systems from scratch
- a character mod usually does not need to add `talker` manually because the shared player base already does

## `common_postinit` Versus `master_postinit`

Observed vanilla patterns:

- `common_postinit`
  - add character identity tags
  - set client-visible animation overrides
  - define local helper methods or net events
  - add client-visible components that belong before the pristine split
- `master_postinit`
  - assign `starting_inventory`
  - tune `health`, `hunger`, `sanity`, or combat
  - add server-only character components
  - register authoritative listeners and callbacks

Good rule:

- if the logic depends on authoritative components and real gameplay mutation, put it in `master_postinit`
- if the logic must exist on both sides or before the client/server return split, put it in `common_postinit`

## Strings And Speech

Character mods usually need both:

- common runtime strings
- character speech under `STRINGS.CHARACTERS.<NAME>`

Recommended routing:

- common strings
  - runtime string files
- speech
  - start from `STRINGS.CHARACTERS.GENERIC`
  - then sparsely override only the differences

Read next:

- `references/string-patterns.md`
- `references/runtime-i18n-patterns.md`

## Optional Skill Tree

Treat the skill tree as optional character-specific progression, not mandatory boilerplate.

Use it when the character really needs:

- unlockable passive perks
- branching progression
- skill-gated recipes or forms
- character-specific progression UI

Skip it when the character only needs:

- fixed stats
- fixed perks
- no unlockable progression

## Official Skill-Tree Wiring

Observed official pieces:

- `scripts/prefabs/player_common.lua`
  - adds `skilltreeupdater` to the player baseline
- `scripts/components/skilltreeupdater.lua`
  - activates skills, awards skill XP, saves skill data, and routes RPC/client updates
- `scripts/prefabs/skilltree_defs.lua`
  - stores `SKILLTREE_DEFS`, `SKILLTREE_ORDERS`, and helper functions such as `CreateSkillTreeFor(...)`
- `scripts/prefabs/skilltree_<character>.lua`
  - returns the data model for one character's skill tree

Practical consequence:

- a playable character can exist without a custom skill tree
- if you add one, design it as a separate data module instead of mixing the whole tree into the character prefab file

## Recommended Mod-Owned Skill-Tree Pattern

This is the recommended mod pattern inferred from `scripts/prefabs/skilltree_defs.lua` and the vanilla `skilltree_<character>.lua` files.

1. Add `Asset("SCRIPT", "scripts/prefabs/skilltree_<character>.lua")` to the character prefab assets when the tree exists.
2. Create `scripts/prefabs/skilltree_<character>.lua` that returns:
   - `SKILLS`
   - `ORDERS`
   - optional `BACKGROUND_SETTINGS`
   - optional `CUSTOM_FUNCTIONS`
3. In `modmain.lua` or an imported startup file, require `prefabs/skilltree_defs`.
4. Build the character's skill-tree data module.
5. Call `CreateSkillTreeFor("<character>", data.SKILLS)`.
6. Fill `SKILLTREE_ORDERS["<character>"] = data.ORDERS`.
7. If present, fill `SKILLTREE_METAINFO["<character>"].BACKGROUND_SETTINGS`.
8. If present, fill `CUSTOM_FUNCTIONS["<character>"]`.

Minimal registration shape:

```lua
local skilltreedefs = require("prefabs/skilltree_defs")
local BuildMyCharSkillTreeData = require("prefabs/skilltree_mychar")

local data = BuildMyCharSkillTreeData(skilltreedefs.FN)

skilltreedefs.CreateSkillTreeFor("mychar", data.SKILLS)
skilltreedefs.SKILLTREE_ORDERS.mychar = data.ORDERS

if data.BACKGROUND_SETTINGS ~= nil then
    skilltreedefs.SKILLTREE_METAINFO.mychar.BACKGROUND_SETTINGS = data.BACKGROUND_SETTINGS
end

if data.CUSTOM_FUNCTIONS ~= nil then
    skilltreedefs.CUSTOM_FUNCTIONS.mychar = data.CUSTOM_FUNCTIONS
end
```

## Skill-Tree Data Rules Worth Remembering

Observed in `scripts/prefabs/skilltree_defs.lua`:

- the tree should have one `defaultfocus` skill for controller navigation
- skills should be connected through `root`, `connects`, or `locks`
- more than 32 actual skills breaks networking visibility

Practical consequence:

- avoid floating skills
- keep the tree readable
- do not oversize the first version of a modded tree

## Skill-Gated Recipes

Skill trees do not only affect passive stats.
They also route into recipe gating.

Observed official behavior:

- `scripts/recipe.lua`
  - recipe data supports `builder_skill`
- `scripts/components/builder.lua`
  - checks whether the builder has the required skill
- `scripts/components/builder_replica.lua`
  - mirrors that check on the client

Practical consequence:

- use `builder_skill = "mychar_some_skill"` on `Recipe2(...)` when a recipe should unlock from the tree
- keep skill names stable because the recipe, UI, and skill tree all depend on the same key

## Quick Routing

- "I need a normal modded character with stats, tags, portraits, and speech."
  - stop at the base character pattern
- "I need unlockable perks or skill-gated recipes."
  - add the optional skill tree
- "I need custom player actions or SG changes."
  - read `references/action-patterns.md` and `references/stategraph-patterns.md`
- "I need local UI or a custom character panel."
  - read `references/ui-patterns.md`
