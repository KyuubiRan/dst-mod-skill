# Hook Signatures

Exact signatures copied from `scripts/modutil.lua`.

```lua
AddClassPostConstruct(package, fn)
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
AddReplicableComponent(name)
AddModRPCHandler(namespace, name, fn)
AddClientModRPCHandler(namespace, name, fn)
```
