# DST Mod API Map

Use this file as a compact routing map.
Read exact signatures from the official source before writing code.

## Registration APIs In `scripts/modutil.lua`

- `AddPrefabPostInit`
  - Patch one prefab after construction.
- `AddPrefabPostInitAny`
  - Patch every prefab, usually for broad instrumentation or tagging.
- `AddPlayerPostInit`
  - Patch player instances without hard-coding a specific character prefab.
- `AddComponentPostInit`
  - Extend a component class after it loads.
- `AddBrainPostInit`
  - Patch a brain definition.
- `AddStategraphPostInit`
  - Patch a stategraph after it loads.
- `AddClassPostConstruct`
  - Patch a required class such as a widget or screen class by wrapping its constructor.
- `AddAction`
  - Register a custom action.
- `AddComponentAction`
  - Connect a component to action collectors.
- `AddStategraphActionHandler`
  - Register action handlers for stategraphs.
- `AddRecipe2`
  - Register recipes with modern filter support.
- `AddRecipeToFilter`
  - Attach a recipe to a crafting filter.
- `AddReplicableComponent`
  - Register a replica-side component.
- `AddModRPCHandler`
  - Register server-side mod RPC handlers.
- `AddClientModRPCHandler`
  - Register client-side mod RPC handlers.
- `AddModCharacter`
  - Register a mod character and its metadata.

## Instance Methods In `scripts/entityscript.lua`

Use `EntityScript` methods when a pattern depends on runtime behavior rather than loader APIs.

- Tags and components
  - `AddTag`
  - `RemoveTag`
  - `HasTag`
  - `AddComponent`
  - `RemoveComponent`
- Events and tasks
  - `ListenForEvent`
  - `PushEvent`
  - `PushEventImmediate`
  - `DoTaskInTime`
  - `DoPeriodicTask`
- Children and ownership
  - `SpawnChild`
  - `AddChild`
  - `RemoveChild`
- Brains and SG
  - `SetBrain`
  - `RestartBrain`
  - `StopBrain`
  - `SetStateGraph`
  - `ClearStateGraph`
- Actions
  - `PushBufferedAction`
  - `PerformBufferedAction`
  - `SetInherentSceneAction`
  - `SetInherentSceneAltAction`

## Setup Helpers In `scripts/standardcomponents.lua`

Read this file before hand-rolling common prefab setup.

- Burn and fire propagation
  - `MakeSmallBurnable`
  - `MakeMediumBurnable`
  - `MakeLargeBurnable`
  - `MakeSmallPropagator`
  - `MakeMediumPropagator`
  - `MakeLargePropagator`
- Freeze helpers
  - `MakeTinyFreezableCharacter`
  - `MakeSmallFreezableCharacter`
  - `MakeMediumFreezableCharacter`
  - `MakeLargeFreezableCharacter`
- Physics helpers
  - `MakeInventoryPhysics`
  - `MakeProjectilePhysics`
  - `MakeCharacterPhysics`
  - `MakeFlyingCharacterPhysics`
  - `MakeObstaclePhysics`
  - `MakeHeavyObstaclePhysics`
- Haunt helpers
  - `MakeHauntable`
  - `MakeHauntableLaunch`
  - `MakeHauntableWork`
  - `MakeHauntableIgnite`
  - `MakeHauntableChangePrefab`
- Miscellaneous helpers
  - `MakeInventoryFloatable`
  - `MakeDeployableFertilizer`
  - `MakeForgeRepairable`
  - `MakeWaxablePlant`

## Loader And Metadata Files

- `scripts/mods.lua`
  - Use for load order, `PrefabFiles`, `Assets`, and `modmain.lua` execution flow.
- `scripts/modindex.lua`
  - Use for `modinfo.lua` expectations such as API version, compatibility flags, and configuration options.
- `scripts/mainfunctions.lua`
  - Use for prefab registration and asset path resolution.

## Rule Of Thumb

- If the task starts with "patch an existing thing", start in `modutil.lua` and the concrete official target file.
- If the task starts with "why does this instance behave like this", start in `entityscript.lua` and the relevant component file.
- If the task starts with "set up a new prefab", start in a similar official prefab and `standardcomponents.lua`.
- If the task depends on server or client context, read `runtime-globals.md` before writing code.
