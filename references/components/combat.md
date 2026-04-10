# `combat`

Use this file when the task changes targeting, attack cadence, melee range, aggro, or direct hit and attacked flow.

Official source:

- `scripts/components/combat.lua`

Close official prefab shapes:

- `scripts/prefabs/glommer.lua`
- `scripts/prefabs/birchnutdrake.lua`

High-frequency methods:

- `SetDefaultDamage(damage)`
- `SetAttackPeriod(period)`
- `SetRange(attack, hit)`
- `SetTarget(target)`
- `DropTarget(hasnexttarget)`
- `HasTarget()`
- `CanAttack(target)`
- `TryAttack(target)`
- `DoAttack(targ, weapon, projectile, stimuli, instancemult, instrangeoverride, instpos)`
- `GetAttacked(attacker, damage, weapon, stimuli, spdamage)`
- `SetRetargetFunction(period, fn)`
- `SetKeepTargetFunction(fn)`
- `ShareTarget(target, range, fn, maxnum, musttags)`
- `CalcDamage(target, weapon, multiplier)`

Common pairings:

- `combat` + `health`
- `combat` + SG
- `combat` + brain
- `combat` + `weapon`

Common pitfalls:

- changing damage alone does not fix attack timing or hit windows.
- creature combat is tightly coupled to brain and SG logic.
- target retention bugs often live in retarget or keep-target functions, not in `SetTarget(...)` alone.

Read next:

- `references/brain-patterns.md`
- `references/stategraph-patterns.md`
