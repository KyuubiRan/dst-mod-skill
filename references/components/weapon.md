# `weapon`

Use this file when the task changes weapon-side damage, projectile behavior, electric hits, or attack callbacks.

Official source:

- `scripts/components/weapon.lua`

Close official prefab shapes:

- `scripts/prefabs/spear.lua`
- `scripts/prefabs/slingshot.lua`

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

Common pairings:

- `weapon` + `equippable`
- `weapon` + `inventoryitem`
- `weapon` + `combat`
- `weapon` + optional `finiteuses`

Common pitfalls:

- final attack flow still passes through the attacker's `combat`.
- projectile weapons usually need matching prefab, SG, and animation behavior.
- range often has to align on both `weapon` and attacker `combat`.

Read next:

- `references/components/combat.md`
- `references/animstate-patterns.md`
