# Template Patterns

Use this file when the task needs a practical starter template instead of just conceptual guidance.

These templates are intentionally minimal.
They are starting points, not drop-in complete mods.

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

Attach it from a prefab with:

```lua
inst:AddComponent("mycomponent")
```

## Minimal Widget Patch

```lua
AddClassPostConstruct("widgets/controls", function(self)
    -- patch constructor-time widget behavior here
end)
```

## Minimal Hotkey

```lua
if not TheNet:IsDedicated() then
    local my_key_handler = TheInput:AddKeyDownHandler(KEY_F, function()
        -- local hotkey logic
    end)
end
```

If the handler belongs to a widget or screen, store it and remove it during teardown.

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

Use this when the server should trigger a cue but the actual sound can be spawned locally on clients.

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

This is the recommended baseline when:

- the mod has common locale data and character speech overrides
- you want sparse locale files
- you want character speech to inherit missing lines from the default generic base

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

Attach it from the prefab with:

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

This pattern is recommended when:

- most setup is shared
- the differences are cleanly table-driven
- you want one file to own a whole item family

If the variants start needing many unrelated branches, split the file or move the shared helper down one level instead.

## Rule Of Thumb

- Start from the smallest template that fits.
- Replace placeholders only after reading the closest official file.
- Keep templates narrow; move complexity into dedicated files only when the feature actually needs it.
