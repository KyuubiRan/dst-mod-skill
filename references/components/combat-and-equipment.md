# Combat And Equipment Components

Use this file for `combat`, `weapon`, `equippable`, and `armor`.

## `combat`

Official file:

- `scripts/components/combat.lua`

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

Use it for:

- AI attack cadence and retargeting
- melee range or hit range changes
- direct combat hooks
- aggro and target sharing behavior

Common pitfalls:

- `combat` is tightly coupled with stategraph and brain logic
- changing damage alone does not fix attack timing, hit windows, or target retention
- for creatures, inspect the prefab and stategraph together with `combat.lua`

## `weapon`

Official file:

- `scripts/components/weapon.lua`

High-frequency methods:

- `SetDamage(dmg)`
- `SetRange(attack, hit)`
- `SetProjectile(projectile)`
- `SetProjectileOffset(offset)`
- `SetOnAttack(fn)`
- `SetOnProjectileLaunch(fn)`
- `SetOnProjectileLaunched(fn)`
- `SetElectric(damage_mult, wet_damage_mult)`
- `GetDamage(attacker, target)`

Use it for:

- melee weapon damage
- projectile weapon behavior
- electric or stimulus-based attacks
- attack callbacks

Common pitfalls:

- `weapon` defines weapon-side behavior; final combat flow still passes through `combat`
- projectile weapons usually need matching prefab and animation behavior, not just `SetProjectile(...)`
- range may need to align with both `weapon` and the attacker's `combat` setup

## `equippable`

Official file:

- `scripts/components/equippable.lua`

High-frequency methods:

- `SetOnEquip(fn)`
- `SetOnUnequip(fn)`
- `SetOnPocket(fn)`
- `Equip(owner, from_ground)`
- `Unequip(owner)`
- `GetWalkSpeedMult()`
- `SetPreventUnequipping(shouldprevent)`
- `ShouldPreventUnequipping()`
- `GetDapperness(owner, ignore_wetness)`
- `IsRestricted(target)`

Use it for:

- equip and unequip hooks
- slot-specific wearable behavior
- movement-speed or dapperness effects
- equip restrictions

Common pitfalls:

- equip visuals often also need `owner.AnimState:OverrideSymbol(...)`
- `equippable` alone does not give armor or weapon behavior
- restrictions may fail from save/load edge cases if only fresh spawns were tested

## `armor`

Official file:

- `scripts/components/armor.lua`

High-frequency methods:

- `InitCondition(amount, absorb_percent)`
- `InitIndestructible(absorb_percent)`
- `SetAbsorption(absorb_percent)`
- `SetCondition(amount)`
- `SetPercent(amount)`
- `GetPercent()`
- `TakeDamage(damage_amount)`
- `Repair(amount)`
- `SetOnFinished(fn)`

Use it for:

- durability-based protection
- percent absorption changes
- break and repair flows

Common pitfalls:

- `armor` handles durability and absorption, not equip slot behavior
- most wearable armor items need both `equippable` and `armor`
- if an armor item breaks visually or disappears, also inspect prefab and equip callbacks
