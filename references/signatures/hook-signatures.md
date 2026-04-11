# Hook Signatures

Exact signatures copied from `scripts/modutil.lua`.
Use `references/patterns/hook-selection-patterns.md` when the real question is which hook should own the patch.

```lua
AddCustomizeGroup(category, name, text, desc, atlas, order)
RemoveCustomizeGroup(category, name)
AddCustomizeItem(category, group, name, itemsettings)
RemoveCustomizeItem(category, name)
GetCustomizeDescription(description)

AddLevelPreInit(levelid, fn)
AddLevelPreInitAny(fn)
AddTaskSetPreInit(tasksetname, fn)
AddTaskSetPreInitAny(fn)
AddTaskPreInit(taskname, fn)
AddRoomPreInit(roomname, fn)
AddLocation(arg1, ...)
AddLevel(arg1, arg2, ...)
AddTaskSet(arg1, ...)
AddTask(arg1, ...)
AddRoom(arg1, ...)
AddStartLocation(arg1, ...)

AddClassPostConstruct(package, fn)
AddGlobalClassPostConstruct(package, classname, fn)
AddAction(id, str, fn)
AddComponentAction(actiontype, component, fn)
AddStategraphActionHandler(stategraph, handler)
AddStategraphPostInit(stategraph, fn)
AddComponentPostInit(component, fn)
AddPrefabPostInitAny(fn)
AddPlayerPostInit(fn)
AddPrefabPostInit(prefab, fn)
AddBrainPostInit(brain, fn)
AddModCharacter(name, gender, modes)
AddRecipeToFilter(recipe_name, filter_name)
AddRecipe2(name, ingredients, tech, config, filters)
AddMinimapAtlas(atlaspath)
AddReplicableComponent(name)
AddModRPCHandler(namespace, name, fn)
AddClientModRPCHandler(namespace, name, fn)
AddShardModRPCHandler(namespace, name, fn)
GetModRPC(namespace, name)
GetClientModRPC(namespace, name)
GetShardModRPC(namespace, name)
SendModRPCToServer(id_table, ...)
SendModRPCToClient(id_table, ...)
SendModRPCToShard(id_table, ...)
LoadPOFile(path, lang)
```

## Fast Router

- world customization option or preset-facing host setup
  - `AddCustomizeGroup`, `AddCustomizeItem`, `RemoveCustomizeGroup`, `RemoveCustomizeItem`
- patch existing worldgen content
  - `AddLevelPreInit`, `AddTaskSetPreInit`, `AddTaskPreInit`, `AddRoomPreInit`
- register new room, task, task set, level, or start location
  - `AddRoom`, `AddTask`, `AddTaskSet`, `AddLevel`, `AddStartLocation`
- patch runtime prefab, component, SG, or UI class
  - `AddPrefabPostInit`, `AddComponentPostInit`, `AddStategraphPostInit`, `AddClassPostConstruct`, `AddGlobalClassPostConstruct`
- patch every player-tagged instance
  - `AddPlayerPostInit`
- register a playable character, optionally with wardrobe or loadout preview modes
  - `AddModCharacter`
- add networking glue
  - `AddReplicableComponent`, `AddModRPCHandler`, `AddClientModRPCHandler`, `AddShardModRPCHandler`, `Get*RPC`, `SendModRPCTo*`
- add explicit minimap or runtime `.po` translation support
  - `AddMinimapAtlas`, `LoadPOFile`
