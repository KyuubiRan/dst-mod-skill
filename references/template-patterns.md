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

## Rule Of Thumb

- Start from the smallest template that fits.
- Replace placeholders only after reading the closest official file.
- Keep templates narrow; move complexity into dedicated files only when the feature actually needs it.
