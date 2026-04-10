# `armor`

Use this file when the task changes protection amount, durability condition, break flow, or armor repair.

Official source:

- `scripts/components/armor.lua`

Close official prefab shapes:

- `scripts/prefabs/armor_grass.lua`

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

Common pairings:

- `armor` + `equippable`
- `armor` + `inventoryitem`

Common pitfalls:

- `armor` is protection and durability logic, not equip-slot ownership.
- break behavior often also needs item and equip callbacks.
- indestructible armor is different from ordinary high condition armor.

Read next:

- `references/components/equippable.md`
- `references/components/inventoryitem.md`
