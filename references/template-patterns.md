# Template Patterns

Use this file when the task needs a practical starter template instead of conceptual guidance. These templates are minimal starting points, not drop-in complete mods.

Pick the smallest template that matches the requested feature shape.
Do not combine unrelated templates just because they all seem useful.

## Minimal `modmain.lua`

```lua
local GLOBAL = GLOBAL
setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})

PrefabFiles = {
    "my_item",
}

Assets = {
}

-- Shared declarations and registrations go here.

if not TheWorld.ismastersim then
    return
end

-- Server-authoritative logic goes here.
```

Use this when:

- the mod is not purely worldgen-side
- `modmain.lua` is the normal runtime entry point
- you still want the usual global passthrough and authority split

## Minimal Player-Wide Patch In `modmain.lua`

```lua
AddPlayerPostInit(function(inst)
    inst:AddTag("my_mod_player")

    if not TheWorld.ismastersim then
        return
    end

    inst:ListenForEvent("death", function(player)
        -- authoritative player-wide behavior
    end)
end)
```

Use this when:

- the feature should affect every player, not one character prefab
- the main missing piece is a safe `AddPlayerPostInit(...)` skeleton
- local HUD or screen work, if any, will be guarded separately

## Minimal Character Registration In `modmain.lua`

```lua
local GLOBAL = GLOBAL
setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})

PrefabFiles = {
    "mychar",
}

Assets = {
    Asset("IMAGE", "images/avatars/avatar_mychar.tex"),
    Asset("ATLAS", "images/avatars/avatar_mychar.xml"),
    Asset("IMAGE", "images/avatars/avatar_ghost_mychar.tex"),
    Asset("ATLAS", "images/avatars/avatar_ghost_mychar.xml"),
    Asset("IMAGE", "images/avatars/self_inspect_mychar.tex"),
    Asset("ATLAS", "images/avatars/self_inspect_mychar.xml"),
    Asset("IMAGE", "images/saveslot_portraits/mychar.tex"),
    Asset("ATLAS", "images/saveslot_portraits/mychar.xml"),
    Asset("IMAGE", "images/selectscreen_portraits/mychar.tex"),
    Asset("ATLAS", "images/selectscreen_portraits/mychar.xml"),
    Asset("IMAGE", "images/selectscreen_portraits/mychar_silho.tex"),
    Asset("ATLAS", "images/selectscreen_portraits/mychar_silho.xml"),
    Asset("IMAGE", "bigportraits/mychar.tex"),
    Asset("ATLAS", "bigportraits/mychar.xml"),
    Asset("IMAGE", "bigportraits/mychar_none.tex"),
    Asset("ATLAS", "bigportraits/mychar_none.xml"),
}

AddMinimapAtlas("images/map_icons/mychar.xml")
AddModCharacter("mychar", "FEMALE")
```

Use this when:

- the task is a real character mod
- the main missing piece is registration plus frontend assets
- the actual player logic will live in `prefabs/mychar.lua`

If the character has alternate wardrobe or loadout preview forms, pass an optional third argument:

```lua
local character_modes = {
    { type = "young_skin", play_emotes = true },
    { type = "old_skin", play_emotes = true, scale = 0.9 },
}

AddModCharacter("mychar", "FEMALE", character_modes)
```

Use this only for frontend preview modes.
It does not replace the real gameplay-side form switching logic.

## Minimal `modworldgenmain.lua`

```lua
AddRoomPreInit("BGForest", function(room)
    room.contents = room.contents or {}
    room.contents.distributeprefabs = room.contents.distributeprefabs or {}
    room.contents.distributeprefabs.my_worldgen_prefab = 0.03
end)
```

Use this when:

- the task is generation-time only
- the feature belongs to rooms, tasks, levels, or start locations
- runtime gameplay hooks are not the main change

## Minimal `modservercreationmain.lua`

```lua
AddCustomizeGroup(LEVELCATEGORY.WORLDGEN, "mygroup", "My Group", "Host-facing mod group.", nil, 50)

AddCustomizeItem(LEVELCATEGORY.WORLDGEN, "mygroup", "my_option", {
    text = "My Option",
    desc = "Host-facing worldgen toggle.",
    items = {
        { data = "default", text = "Default", desc = "Use the default behavior." },
        { data = "often", text = "Often", desc = "Bias toward this option." },
    },
})
```

Use this when:

- the host setup screen must expose a mod-owned option
- the task is preset-facing or setup-UI-facing
- the generated content itself may still need matching worldgen-side logic elsewhere

## Minimal Prefab

```lua
local assets =
{
    Asset("ANIM", "anim/my_item.zip"),
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("my_item")
    inst.AnimState:SetBuild("my_item")
    inst.AnimState:PlayAnimation("idle")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")

    return inst
end

return Prefab("my_item", fn, assets)
```

Use this when:

- the task needs a bare networked prefab shell
- the real behavior will be added afterward through components
- you want a safe `SetPristine()` split before adding logic

## Minimal Custom Component

```lua
local MyComponent = Class(function(self, inst)
    self.inst = inst
end)

function MyComponent:OnRemoveFromEntity()
end

function MyComponent:OnSave()
    return nil
end

function MyComponent:OnLoad(data)
end

return MyComponent
```

Attach from a prefab with:

```lua
inst:AddComponent("mycomponent")
```

## Minimal Widget Patch

```lua
AddClassPostConstruct("widgets/controls", function(self)
    -- patch constructor-time widget behavior here
end)
```

Use this only for classes that are already `require(...)`-loaded by the game.
If the user really wants a brand-new widget class, create the widget file first and then patch or instantiate it from the owning screen.

## Minimal Hotkey

```lua
if not TheNet:IsDedicated() then
    local my_key_handler = TheInput:AddKeyDownHandler(KEY_F, function()
        -- local hotkey logic
    end)
end
```

If the handler belongs to a widget or screen, store it and remove it during teardown.

If the feature should respect control remapping, prefer a control-based template over raw key handling.

## Minimal Mod RPC

```lua
AddModRPCHandler("my_mod", "do_thing", function(player, ...)
    -- server-side authoritative handler
end)

if not TheNet:IsDedicated() then
    local function SendThing(...)
        SendModRPCToServer(GetModRPC("my_mod", "do_thing"), ...)
    end
end
```

Use this when:

- local input or UI should request an authoritative server-side action
- the state mutation does not belong purely on the client

## Minimal Netvar On A Prefab

```lua
local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddNetwork()

    inst._enabled = net_bool(inst.GUID, "my_prefab._enabled", "enableddirty")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst._enabled:set(true)

    return inst
end
```

Use this when:

- clients need a small replicated value
- a full replica component would be overkill

## Minimal One-Shot FX Prefab

Use this for a short visual effect that should not persist or be directly clickable.

```lua
local assets =
{
    Asset("ANIM", "anim/my_fx.zip"),
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()

    inst:AddTag("FX")
    inst:AddTag("NOCLICK")

    inst.entity:SetCanSleep(false)
    inst.persists = false

    inst.AnimState:SetBank("my_fx")
    inst.AnimState:SetBuild("my_fx")
    inst.AnimState:PlayAnimation("idle")

    inst:ListenForEvent("animover", inst.Remove)

    return inst
end

return Prefab("my_fx", fn, assets)
```

## Minimal Lit Prefab

Use this for a normal gameplay prefab that owns a simple light source.

```lua
local assets =
{
    Asset("ANIM", "anim/my_lamp.zip"),
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddLight()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("my_lamp")
    inst.AnimState:SetBuild("my_lamp")
    inst.AnimState:PlayAnimation("idle")

    inst.Light:SetFalloff(0.7)
    inst.Light:SetIntensity(0.8)
    inst.Light:SetRadius(2)
    inst.Light:SetColour(180 / 255, 195 / 255, 150 / 255)
    inst.Light:EnableClientModulation(true)

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")

    return inst
end

return Prefab("my_lamp", fn, assets)
```

## Minimal Sound-Only Proxy

Use this when the server should trigger a cue but the sound can be spawned locally on clients.

```lua
local function PlayLocalSound(proxy, sound)
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddSoundEmitter()
    inst.entity:SetParent(TheFocalPoint.entity)

    inst.SoundEmitter:PlaySound(sound)
    inst:Remove()
end

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddNetwork()

    inst:AddTag("FX")
    inst:AddTag("NOCLICK")

    if not TheNet:IsDedicated() then
        inst:DoTaskInTime(0, PlayLocalSound, "dontstarve/common/click_stone")
    end

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst.entity:SetCanSleep(false)
    inst.persists = false
    inst:DoTaskInTime(1, inst.Remove)

    return inst
end

return Prefab("my_sound_proxy", fn)
```

## Minimal Recipe And Placer

```lua
AddRecipe2(
    "my_structure",
    {
        Ingredient("rocks", 4),
    },
    TECH.NONE,
    {
        placer = "my_structure_placer",
        min_spacing = 2,
    },
    {
        "STRUCTURES",
    }
)
```

```lua
return Prefab("my_structure", fn, assets),
    MakePlacer("my_structure_placer", "my_structure", "my_structure", "idle")
```

## Minimal Strings

```lua
STRINGS.NAMES.MY_ITEM = "My Item"
STRINGS.RECIPE_DESC.MY_STRUCTURE = "Place a structure."
STRINGS.CHARACTERS.GENERIC.DESCRIBE.MY_ITEM = "A custom thing."
```

Use direct assignments for small string additions.
If the task is "real locale support", stop here and switch to `references/runtime-i18n-patterns.md`.

## Minimal Runtime I18n Loader

Use this when the mod needs real runtime localization instead of a few direct string writes.

```lua
local supported = {
    en = true,
    zh = true,
}

local function ResolveLocale()
    local locale = GetModConfigData("LANGUAGE")
    if locale == nil or locale == "auto" then
        locale = LOC.GetLocaleCode()
    end
    if not supported[locale] then
        locale = "en"
    end
    return locale
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

DeepMerge(STRINGS, require("languages/common_" .. locale))

local speech = DeepCopy(STRINGS.CHARACTERS.GENERIC)
DeepMerge(speech, require("languages/speech_mychar_" .. locale))
STRINGS.CHARACTERS.MYCHAR = speech
```

Recommended when:

- the mod has common locale data and character speech overrides
- locale files should stay sparse
- character speech should inherit missing lines from the generic base

Do not copy this into `modinfo.lua`.
This is runtime-side only.

## Minimal Playable Character Prefab

```lua
local MakePlayerCharacter = require("prefabs/player_common")

local assets =
{
    Asset("SCRIPT", "scripts/prefabs/player_common.lua"),
    Asset("ANIM", "anim/player_mychar.zip"),
    Asset("ANIM", "anim/player_idles_mychar.zip"),
}

local prefabs = {}

local start_inv = {}
for mode, items in pairs(TUNING.GAMEMODE_STARTING_ITEMS) do
    start_inv[string.lower(mode)] = items.MYCHAR
end

local function common_postinit(inst)
    inst:AddTag("mychar")
    inst.customidleanim = "idle_mychar"
end

local function master_postinit(inst)
    inst.starting_inventory = start_inv[TheNet:GetServerGameMode()] or start_inv.default

    inst.components.health:SetMaxHealth(TUNING.MYCHAR_HEALTH)
    inst.components.hunger:SetMax(TUNING.MYCHAR_HUNGER)
    inst.components.sanity:SetMax(TUNING.MYCHAR_SANITY)
end

return MakePlayerCharacter("mychar", prefabs, assets, common_postinit, master_postinit)
```

Use this when:

- the task is a real playable character
- you need the normal player baseline from `player_common.lua`
- the character does not need a custom skill tree yet

## Minimal Character Skill-Tree Registration

Use this only when the character really needs unlockable progression.

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

Pair this with:

- `Asset("SCRIPT", "scripts/prefabs/skilltree_mychar.lua")`
- a `scripts/prefabs/skilltree_mychar.lua` data module
- optional `builder_skill` recipe gates for skill-unlocked crafts

## Minimal Brain

```lua
require "behaviours/wander"

local MyBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function MyBrain:OnStart()
    local root = PriorityNode({
        Wander(self.inst, function() return self.inst:GetPosition() end, 6),
    }, .25)

    self.bt = BT(self.inst, root)
end

return MyBrain
```

Attach from the prefab with:

```lua
local brain = require("brains/mybrain")

...

inst:SetBrain(brain)
inst:SetStateGraph("SGmycreature")
```

## Variant Prefab Factory

Use this when many prefabs share the same setup and only differ by a small config table.

```lua
local assets =
{
    Asset("ANIM", "anim/my_weapons.zip"),
    Asset("ANIM", "anim/swap_my_weapons.zip"),
}

local variants =
{
    {
        prefab = "my_blade_red",
        anim = "red",
        damage = 34,
        uses = 100,
    },
    {
        prefab = "my_blade_blue",
        anim = "blue",
        damage = 42,
        uses = nil, -- infinite durability
    },
}

local function MakeWeaponVariant(data)
    local function fn()
        local inst = CreateEntity()

        inst.entity:AddTransform()
        inst.entity:AddAnimState()
        inst.entity:AddNetwork()

        inst.AnimState:SetBank("my_weapons")
        inst.AnimState:SetBuild("my_weapons")
        inst.AnimState:PlayAnimation(data.anim)

        inst.entity:SetPristine()

        if not TheWorld.ismastersim then
            return inst
        end

        inst:AddComponent("inspectable")
        inst:AddComponent("inventoryitem")
        inst:AddComponent("equippable")
        inst:AddComponent("weapon")
        inst.components.weapon:SetDamage(data.damage)

        if data.uses ~= nil then
            inst:AddComponent("finiteuses")
            inst.components.finiteuses:SetMaxUses(data.uses)
            inst.components.finiteuses:SetUses(data.uses)
        end

        return inst
    end

    return Prefab(data.prefab, fn, assets)
end

local prefabs = {}
for _, data in ipairs(variants) do
    table.insert(prefabs, MakeWeaponVariant(data))
end

return unpack(prefabs)
```

Recommended when:

- most setup is shared
- the differences are table-driven
- one file should own a whole item family

If the variants start needing many unrelated branches, split the file or move the shared helper down one level.

This is the right default when the user asks for:

- a whole staff or gem family
- several foods with the same base flow
- multiple weapon or armor variants that differ mostly by table data

## Rule Of Thumb

- Start from the smallest template that fits.
- Replace placeholders only after reading the closest official file.
- Keep templates narrow; move complexity into dedicated files only when needed.
- If the task has explicit negative constraints such as "no durability", "not inspectable", or "client-only", remove the template pieces that violate that constraint before coding.
