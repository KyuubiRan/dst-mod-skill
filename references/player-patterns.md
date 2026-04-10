# Player Patterns

Use this file when the task patches players as a class rather than building one specific playable character.

Typical triggers:

- `AddPlayerPostInit(...)`
- "apply this to every player"
- player lifecycle events such as `playerentered`, `ms_playerjoined`, `playeractivated`, or `playerdeactivated`
- deciding between a global player patch and a character-local prefab change

If the task is mainly about one playable character prefab, read `references/character-patterns.md`.
If the task touches local HUD or screens, also read `references/runtime-local-ui.md`.
If the task touches player action states or prediction, also read `references/stategraph-patterns.md`.
If the task needs player-owned replicated state or `player_classified`, also read `references/player-network-patterns.md`.

## Choose The Narrowest Player Hook

Use these differently:

- `AddModCharacter(...)`
  - register a new playable character
- `AddPrefabPostInit("<character>", fn)`
  - patch one specific player prefab
- `AddPlayerPostInit(fn)`
  - patch every player-tagged instance

Observed official definition in `scripts/modutil.lua`:

- `AddPlayerPostInit(fn)` is implemented as `AddPrefabPostInitAny(...)`
- it only filters by `inst:HasTag("player")`

Practical consequence:

- this is a broad hook, not a character-specific one
- it affects vanilla characters and mod characters alike
- it does not distinguish local player, remote player, alive player, or ghost by itself
- because it is built on `AddPrefabPostInitAny(...)`, keep the callback narrow and cheap

## What `player_common.lua` Already Owns

Observed in `scripts/prefabs/player_common.lua`:

- calls `common_postinit(inst)` before `SetPristine()`
- returns early on clients after `inst.entity:SetPristine()`
- adds the large server baseline before `master_postinit(inst)`

Observed baseline pieces include:

- `talker`
- `skilltreeupdater`
- `combat`
- `inventory`
- `inspectable`
- `temperature`
- player burnable and freezable helpers

Practical consequence:

- do not rebuild the ordinary player baseline inside `AddPlayerPostInit(...)`
- if the change belongs to one character's identity, stats, or perks, prefer that character's prefab callbacks
- use player-wide patching for behavior that should truly affect every player instance

## Local Versus Remote Players

Every player entity can match `AddPlayerPostInit(...)`, but only one local player owns the HUD.

Practical rule:

- all players
  - `AddPlayerPostInit(...)`
- only the active local player
  - local guards plus `playeractivated` or `inst == ThePlayer`
- only authoritative gameplay
  - `TheWorld.ismastersim`

Do not assume `AddPlayerPostInit(...)` means "my local player".

## Player Lifecycle Events Worth Remembering

Observed in `scripts/prefabs/player_common.lua`:

- `playerentered`
  - pushed on both client and server when a player entity becomes relevant locally
- `ms_playerjoined`
  - pushed only on the master sim after a player has joined
- `playeractivated`
  - pushed when the local active player becomes active
- `playerdeactivated`
  - pushed when that active player is torn down or swapped out

Practical consequence:

- if the feature is "do something whenever any player entity appears", use `playerentered` or a player post-init
- if the feature is "do something for the real connected player on the server", use server-side join or authoritative callbacks
- if the feature is HUD, camera, or local-player-only setup, key off `playeractivated` instead of any random player entity existing

## Minimal Global Player Patch

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

## Minimal Local Active-Player Hook

```lua
AddPlayerPostInit(function(inst)
    if TheNet:IsDedicated() then
        return
    end

    inst:ListenForEvent("playeractivated", function(player)
        if player == ThePlayer and player.HUD ~= nil then
            -- local HUD or screen setup
        end
    end)
end)
```

## Common Failure Points

- using `AddPlayerPostInit(...)` when the task only targets one character
- forgetting that ghosts and remote players may still match the hook
- touching HUD or `ThePlayer` without a local-client guard
- doing expensive logic in a broad all-player callback
- duplicating baseline player setup that `player_common.lua` already owns

## Quick Router

- "patch every player with the same gameplay rule"
  - `AddPlayerPostInit(...)`
- "patch only one character prefab"
  - `AddPrefabPostInit("<character>", fn)` or character prefab callbacks
- "build a new playable character"
  - `references/character-patterns.md`
- "touch only the local active player's HUD or screen"
  - `playeractivated` plus `references/runtime-local-ui.md`
- "sync owner-only player HUD or controller state"
  - `references/player-network-patterns.md`
