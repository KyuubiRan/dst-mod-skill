# Diagnostic Patterns

Use this file when a DST mod feature does not behave as expected and you need a fast symptom-driven checklist.

This page is not a replacement for the narrower pitfall pages.
Use it to choose the first checks quickly.

## Read The Log Before Guessing

Check logs early when the user says things like:

- "报错了"
- "崩了"
- "红字"
- "客户端有问题"
- "重启后又没了"

Default client-log locations:

- Windows: `~/Documents/Klei/DoNotStarveTogether/client_log.txt`
- macOS: `~/Documents/Klei/DoNotStarveTogether/client_log.txt`
- Linux: `~/.klei/DoNotStarveTogether/client_log.txt`

Companion log paths:

- `backup/`
  - rotated history after a refresh or restart
- `master_server_log.txt`
  - listen-host or local master-shard runtime issues
- `caves_server_log.txt`
  - local caves-shard runtime issues

Fast rule:

1. Search for `LUA ERROR stack traceback:` first.
2. If found, identify the first mod-owned file in the stack and work outward from there.
3. If not found, distinguish between warning noise, asset problems, shutdown noise, and a real hard failure.
4. If the game has already been restarted, inspect `backup/` before concluding the log is clean.
5. After extracting the stack, determine whether the user only wants the cause explained or is actively debugging the mod.
6. If this is active debugging, confirm whether the failing file belongs to the current target mod before planning edits.
7. Explain the error first, then ask whether the user wants help fixing it.
8. Do not edit code unless the user clearly confirms that they want a fix.

If the first mod-owned stack frame looks like `../mods/workshop-<workshop-id>/main/hook.lua:116`, treat it as a Workshop-installed mod:

1. Extract the numeric workshop id from `workshop-<workshop-id>`.
2. Resolve the Workshop root in this order:
   - infer it from the current workspace if the workspace already sits under `steamapps/workshop/content/322330/...`
   - otherwise derive it from the already-known game root under the same Steam library
   - only then try common default Workshop roots for Windows, Linux, or macOS
3. Map the id to `<workshop-root>/<workshop-id>`.
4. Open the matching file inside that Workshop mod root, such as `main/hook.lua`.
5. Read the surrounding function and nearby helpers before deciding whether the immediate line is the real cause.
6. If the directory is missing, tell the user you detected a crash-related Workshop mod but could not find its install path, then ask for that path explicitly.
7. Only after reading the real Workshop source should you explain the cause or propose a fix.

Do not assume a `workshop-<id>` stack belongs to the current workspace mod.
It often points at a separately installed dependency or another active Workshop mod.

Common non-fatal noise examples:

- missing default texture warnings
- shutdown-time `Could not unload undefined prefab (...)`
- orphaned resource cleanup lines

These may still matter, but they are not the same thing as a Lua exception with a stack trace.

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

If this smells like a sync issue, also read `references/pitfalls/networking-pitfalls.md`.

## World Setting, Preset, Or Start Location Does Not Show Up

Check in this order:

1. Is this task in `modworldgenmain.lua` or `modservercreationmain.lua`, rather than ordinary runtime `modmain.lua`?
2. If it is a customization option, did you use the correct category: `LEVELCATEGORY.SETTINGS` or `LEVELCATEGORY.WORLDGEN`?
3. If it is a host-visible option, did you add it through `AddCustomizeGroup(...)` or `AddCustomizeItem(...)`?
4. If it is a start type, did you register it with `AddStartLocation(...)`?
5. If it is a preset problem, are you changing the settings side, the worldgen side, or both?

Common misses:

- putting world customization logic in `modmain.lua`
- wrong `LEVELCATEGORY`
- start location registered as backend data but not considered as host-facing selection flow

Also read:

- `references/patterns/worldgen-patterns.md`

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

Also read:

- `references/patterns/ui-patch-patterns.md`
- `references/pitfalls/ui-pitfalls.md`

## Local FX Or Sound Works Only On One Side

Check in this order:

1. Is the effect supposed to be purely local, networked, or a proxy that spawns local-only presentation?
2. Is the code incorrectly gated by `TheWorld.ismastersim` when it really needs a `not TheNet:IsDedicated()` local path?
3. If the server triggers the presentation, should the prefab use a network proxy pattern instead?
4. If the sound is UI/frontend-only, should it be on `TheFrontEnd:GetSound()` rather than an entity `SoundEmitter`?
5. If the sound or FX is animation-timed, should it live in the SG timeline instead of ad hoc code?

Common misses:

- local presentation is gated out on non-dedicated clients
- dedicated-server-safe branch is confused with gameplay authority
- entity sound was expected in a frontend-only flow

Also read:

- `references/patterns/effects-patterns.md`
- `references/patterns/runtime-authority.md`

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

If this is specifically a player HUD or owner-only player sync issue, also read `references/patterns/player-network-patterns.md`.

## State Resets After Save, Reload, Or Time Skip

Check in this order:

1. Was the state actually written in `OnSave(...)`?
2. Is the restore happening in the right phase: `OnPreLoad(...)`, `OnLoad(...)`, or `OnLoadPostPass(...)`?
3. If the data points at other entities, are those links repaired in `LoadPostPass(...)` instead of ordinary `OnLoad(...)`?
4. If time should advance while unloaded, does the entity or component implement `LongUpdate(dt)`?
5. If a helper child or owned item should persist, should it use `GetSaveRecord()` or `GetPersistData()`?

Common misses:

- saved a live entity reference instead of a GUID or save record
- restored cross-entity links too early in `OnLoad(...)`
- forgot offline catch-up with `LongUpdate(dt)`
- recreated the helper entity but never called `SetPersistData(...)`

Also read:

- `references/patterns/persistence-patterns.md`
- `references/pitfalls/persistence-pitfalls.md`

## Local Settings Or Cache Reset After Full Restart

Check in this order:

1. Is this data really local cross-save data rather than one world-save entity state?
2. Was the table serialized to string before `TheSim:SetPersistentString(...)`?
3. Does `TheSim:GetPersistentString(...)` restore inside its callback instead of expecting an immediate return value?
4. Is the file key stable and namespaced for this mod?
5. If the data should be host-configurable from the mod settings screen, did the task actually belong in `modinfo.lua` instead?

Common misses:

- used `OnSave(...)` and `OnLoad(...)` for data that should survive across different worlds
- used plain persistent strings for something that should have stayed world-specific
- forgot to decode JSON or handle decode failure

Also read:

- `references/patterns/persistent-string-patterns.md`
- `references/patterns/modinfo-patterns.md`

## Decode, Encode, Or Optional `require(...)` Fails Intermittently

Check in this order:

1. Is the fragile boundary wrapped narrowly with `pcall(...)` or `xpcall(...)`?
2. If this is a decode path, is the decoded value also type-checked before use?
3. If this is an encode path, is there a sane fallback when serialization fails?
4. If this is `require(...)`, is the module truly optional rather than a hidden hard dependency?
5. Is the code protecting only the risky call instead of a huge unrelated logic block?

Common misses:

- called the risky function before `pcall(...)` actually runs
- treated `ok == true` as if the decoded structure must already be valid
- used a broad protected block that hides the real failing line

Also read:

- `references/patterns/protected-call-patterns.md`

## Works On Master But Breaks On Caves Or During Migration

Check in this order:

1. Is this logic meant for the current shard, the master shard, or any shard?
2. Did the code confuse `TheWorld.ismastersim` with `TheWorld.ismastershard`?
3. If the feature depends on a location or recall target, was `worldid` stored and compared?
4. If the destination shard can disappear or fill up, was `Shard_IsWorldAvailable(...)` checked?
5. If the behavior happens during migration, did the code treat migration differently from ordinary despawn?

Common misses:

- counted only local `AllPlayers`
- used one-shard RPC for a cross-shard problem
- forgot shard-aware position checks
- portal visuals were patched without `worldmigrator` status logic

Also read:

- `references/patterns/shard-patterns.md`
- `references/pitfalls/shard-pitfalls.md`

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

## `modinfo.lua` Causes Load Failure Or Settings Screen Breakage

Check in this order:

1. Did `modinfo.lua` stay inside the constrained environment instead of using normal Lua stdlib assumptions?
2. If config text is localized, does it use the modinfo-side translation pattern rather than runtime `STRINGS`?
3. If config sections are grouped, is the helper tiny and self-contained?
4. If key configuration was added, do the option values and labels match the intended key map shape?

Common misses:

- using stdlib helpers casually in `modinfo.lua`
- mixing runtime localization assumptions into metadata localization

Also read:

- `references/patterns/modinfo-patterns.md`

## Fast Console Checks

Official `scripts/consolecommands.lua` exposes high-value commands for quick triage:

- `c_spawn("prefab")`
  - verify prefab registration quickly
- `c_find("prefab")`
  - locate nearby prefab instances
- `c_findtag("tag")`
  - check whether expected tagged entities exist
- `c_selectnear("prefab")`
  - grab the nearest matching entity for inspection
- `c_list("prefab")`
  - count or list loaded entities of one prefab
- `c_listtag("tag")`
  - count or list tagged entities
- `c_dumpworldstate()`
  - inspect current world state values

Use these for verification before deeper code changes when the bug is "I think this thing does not exist" or "I think this runtime branch never happens."

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
- explicit error or crash report
  - read the newest log first, then the newest `backup/` log if the game already restarted
