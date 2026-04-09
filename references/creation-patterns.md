# Creation Patterns

Use this file when the task is about how DST mod content is defined and loaded.

This page focuses on the common creation path:

- `modmain.lua`
- `PrefabFiles`
- `prefabs/*.lua`
- `inst:AddComponent("name")`
- `scripts/components/*.lua`
- replica-side component support

## `modmain.lua` Is The Main Bootstrap

The official loader executes `modmain.lua` for enabled gameplay mods from `scripts/mods.lua`.

Observed flow:

- `ModWrangler:InitializeModMain(modname, mod, "modmain.lua")`
- the mod environment is prepared first
- `modimport(...)` is installed into that environment
- the mod's `scripts/` directory is added to `package.path`

Practical consequence:

- declare `PrefabFiles` in `modmain.lua`
- declare mod-level `Assets` in `modmain.lua`
- use `modimport("scripts/foo")` when you want to split logic into additional Lua files

## How `PrefabFiles` Are Loaded

After `modmain.lua` runs, the loader checks `mod.PrefabFiles` and loads each entry from `prefabs/<name>.lua`.

Observed official flow in `scripts/mods.lua`:

- iterate `mod.PrefabFiles`
- call `LoadPrefabFile("prefabs/" .. prefab_path, nil, MODS_ROOT .. modname .. "/")`
- collect returned `Prefab(...)` objects
- copy them into the global `Prefabs` table

Practical consequence:

- `PrefabFiles = { "my_item", "my_structure" }` means the mod should have:
  - `prefabs/my_item.lua`
  - `prefabs/my_structure.lua`
- the string in `PrefabFiles` is the prefab file path without `.lua`

## Typical Prefab File Shape

Official prefab files commonly look like this:

```lua
local assets =
{
    Asset("ANIM", "anim/my_item.zip"),
}

local prefabs =
{
    "collapse_small",
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst:AddTag("my_item")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")

    return inst
end

return Prefab("my_item", fn, assets, prefabs)
```

High-frequency prefab rules:

- create the entity in `fn()`
- add networked entity pieces before `SetPristine()`
- return early on clients after `SetPristine()` when the rest is server-only
- add server-authoritative components after the master-sim split
- return one or more `Prefab(...)` objects from the file

Many files also return:

- multiple `Prefab(...)` values
- `MakePlacer(...)` for placeable structures

If a prefab task is mostly about `inst.AnimState`, also read `references/animstate-patterns.md`.

## How Components Are Defined

Official components are typically classes under `scripts/components/<name>.lua`.

Common shape:

```lua
local MyComponent = Class(function(self, inst)
    self.inst = inst
end)

function MyComponent:OnRemoveFromEntity()
end

function MyComponent:OnSave()
    return {}
end

function MyComponent:OnLoad(data)
end

return MyComponent
```

Common lifecycle methods you will see:

- `OnRemoveFromEntity`
- `OnSave`
- `OnLoad`

Not every component needs all of them.

## How Components Are Attached To Prefabs

Inside a prefab constructor, attach a component with:

```lua
inst:AddComponent("mycomponent")
```

Official `EntityScript:AddComponent(name)` loads the module via:

```lua
require("components/" .. name)
```

Practical consequence for mods:

- a custom component named `mycomponent` should live at:
  - `scripts/components/mycomponent.lua`
- then the prefab can call:
  - `inst:AddComponent("mycomponent")`

This works because the mod loader adds the mod's `scripts/` directory to `package.path`.

## Existing Component Extension Versus New Component

Use these two routes differently:

- Extend an existing official component:
  - `AddComponentPostInit("health", fn)`
- Add a brand-new component to your own prefab:
  - define `scripts/components/mycomponent.lua`
  - call `inst:AddComponent("mycomponent")` in the prefab

Prefer `AddComponentPostInit` when the task is a small extension of official behavior.
Prefer a new component when the behavior is mod-owned and does not belong inside an existing official component.

## Replica Components For Clients

If a component needs client-readable state, inspect whether it also needs a replica-side partner.

Observed official pattern:

- server component is loaded from `components/<name>.lua`
- replica component is loaded from `components/<name>_replica.lua`
- custom component replication support is enabled with:

```lua
AddReplicableComponent("mycomponent")
```

Practical rule:

- if clients only need server-side authority, a normal component may be enough
- if clients need to read state locally, plan for replica and netvars instead of reading `inst.components` on clients

## File Placement Summary

- `modmain.lua`
  - top-level bootstrap, `PrefabFiles`, `Assets`, hooks, `modimport`
- `prefabs/<name>.lua`
  - prefab definition files returned through `Prefab(...)`
- `scripts/components/<name>.lua`
  - custom server-side component classes
- `scripts/<other>.lua`
  - helper modules loaded with `modimport(...)` or `require(...)`

## Rule Of Thumb

- If the mod adds a new world object or inventory item, start with a prefab file.
- If the behavior needs reusable stateful logic on an entity, start with a component.
- If the code is just glue or registration, keep it in `modmain.lua` or split it with `modimport(...)`.
- If clients need local reads, inspect replica patterns before writing net logic.
