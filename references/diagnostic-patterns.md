# Diagnostic Patterns

Use this file when a DST mod feature does not behave as expected and you need a fast symptom-driven checklist.

This page is not a replacement for the narrower pitfall pages.
Use it to choose the first checks quickly.

## Prefab Does Not Exist Or Never Appears

Check in this order:

1. Is the prefab file listed in `PrefabFiles` in `modmain.lua`?
2. Does the file path match `prefabs/<name>.lua` exactly?
3. Does the prefab file return `Prefab("name", fn, ...)`?
4. Does the returned prefab name match what the code later spawns or references?
5. If the prefab is spawned manually, is the code calling the correct prefab name in `SpawnPrefab(...)`?

Common misses:

- forgot to add the prefab file to `PrefabFiles`
- file name and prefab name do not match
- prefab file returns nothing

## Prefab Loads But Behaves Wrong On Clients

Check in this order:

1. Does the prefab follow the normal network split?
2. Are `AddTransform`, `AddAnimState`, and `AddNetwork` created before `SetPristine()` when needed?
3. Does the file return early on clients after `SetPristine()`?
4. Are server-only components added only after `if not TheWorld.ismastersim then return inst end`?
5. Is client code reading `inst.replica` or netvars instead of `inst.components`?

If this smells like a sync issue, also read `references/networking-pitfalls.md`.

## Recipe Does Not Show Up

Check in this order:

1. Was the recipe added with `AddRecipe2(...)`?
2. Is the recipe name correct and unique?
3. Did the recipe get added to at least one expected filter?
4. If it is character-gated, does the config actually include `builder_tag` or `builder_skill`?
5. If it depends on a placer, does the placer prefab exist?

Common misses:

- using deprecated `AddRecipe` assumptions
- forgetting the intended filter
- expecting a character recipe without a character gate

## Placer Does Not Show Up

Check in this order:

1. Does the prefab file return `MakePlacer(...)`?
2. Does the recipe config point to the correct placer name?
3. Do the placer bank, build, and anim names match real assets?
4. If placement rules are custom, is `postinit_fn` or `onfailedplacement` blocking placement unexpectedly?

Common misses:

- recipe points to the wrong placer id
- placer exists but uses missing art resources

## Inventory Icon Or Atlas Does Not Show Up

Check in this order:

1. Are the atlas and texture files declared in assets if needed?
2. Is the atlas path written exactly as the UI or recipe expects?
3. If this is a shared mod asset, should it live in top-level `Assets` instead of one prefab file?
4. If it is a minimap resource, did you need `AddMinimapAtlas(...)`?

Common misses:

- atlas/xml and texture/tex pair are incomplete
- path casing or relative path is wrong

## UI Patch Does Not Run

Check in this order:

1. Is this really a client-local/UI task?
2. Is the code guarded away accidentally by `TheNet:IsDedicated()` or an early return?
3. Does `AddClassPostConstruct(...)` use the correct require-style package path?
4. Are you patching the actual widget/screen class that is instantiated in this flow?
5. If input is involved, is the handler registered on the local client?

Common misses:

- wrong package path, such as a file path instead of require path
- trying to patch gameplay code as if it were UI code
- UI patch runs only on clients, but the test was done in the wrong context

## Hotkey Or Mouse Input Does Not Fire

Check in this order:

1. Is this code running on a local client and not a dedicated-server-only path?
2. Are you using the right handler type for the feature?
3. Is the handler stored and still alive, or did the owner object get destroyed?
4. If the feature should follow controls, should it use `AddControlHandler(...)` instead of raw key handling?

Common misses:

- registering input on a non-local path
- handler gets lost with the owning widget or screen

## Animation Does Not Play Or Looks Wrong

Check in this order:

1. Does the prefab or widget actually create an `AnimState`?
2. Do `SetBank(...)`, `SetBuild(...)`, and the animation name match real asset names?
3. If this is a transition, should `PushAnimation(...)` queue the idle or loop clip?
4. If a symbol swap is involved, do the `OverrideSymbol(...)` build and symbol names really exist?
5. If the code calls `Hide(...)` or `Show(...)`, is the target a layer name rather than a symbol name?
6. If the animation was speed-adjusted, did code restore `SetDeltaTimeMultiplier(1)` afterward?

Common misses:

- wrong bank and build pairing
- wrong clip name
- using `HideSymbol(...)` when the target is actually a layer
- forgetting `ClearOverrideSymbol(...)` after a temporary swap

## Action Never Appears In The Action Picker

Check in this order:

1. Was the action registered with `AddAction(...)`?
2. Was it exposed through the correct `AddComponentAction(...)` action type?
3. Does the relevant prefab or item actually have the component that the collector expects?
4. Does the collector insert the action under the right conditions?
5. If the performer is a player, did you wire the action into the relevant stategraph?

Common misses:

- used the wrong component action type
- action exists but no collector ever offers it
- `wilson` or `wilson_client` handler is missing

## RPC Sends But Nothing Happens

Check in this order:

1. Was the handler registered with the correct namespace and name?
2. Does the sending side use the same namespace and name via `GetModRPC(...)` or `GetClientModRPC(...)`?
3. Is the send direction correct: client to server or server to client?
4. Is the target logic actually allowed in that runtime context?

Common misses:

- namespace/name mismatch
- used client RPC helper for a server RPC or vice versa

## Replica Or Netvar Reads Do Not Update

Check in this order:

1. Is the state truly replicated, or only stored in `inst.components`?
2. If this is a custom component, was `AddReplicableComponent(...)` registered?
3. Does the replica file exist at `components/<name>_replica.lua`?
4. Are dirty events or replica reads wired on the client side?
5. If the state is more structured, should this actually be a classified pattern instead?

Common misses:

- reading server component data on the client
- forgot the replica-side file
- netvar exists but nothing listens for updates

## Brain Does Not Seem To Control The Creature

Check in this order:

1. Does the prefab `require("brains/<name>")` successfully?
2. Does the prefab actually call `inst:SetBrain(brain)`?
3. Does the prefab also have the expected stategraph?
4. Does the brain set `self.bt = BT(self.inst, root)` in `OnStart()`?
5. If patching official AI, did you use the correct brain name in `AddBrainPostInit(...)`?

Common misses:

- prefab forgot to attach the brain
- brain exists but never assigns `self.bt`
- trying to fix stategraph behavior by changing only the brain

## Fast Triage Rule

Use this mapping:

- feature never loads at all
  - check file placement and registration first
- feature loads but is absent from UI or crafting
  - check filter, atlas, or patch target next
- feature works on host but not client
  - check replica, netvars, and authority split next
- creature exists but acts wrong
  - check brain and stategraph together
