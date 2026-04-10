# `equippable`

Use this file when the task changes equip or unequip hooks, equip slots, walk speed, dapperness, or equip restrictions.

Official source:

- `scripts/components/equippable.lua`

Close official prefab shapes:

- `scripts/prefabs/backpack.lua`
- `scripts/prefabs/armor_grass.lua`

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

Common pairings:

- `equippable` + `inventoryitem`
- `equippable` + `weapon`
- `equippable` + `armor`
- `equippable` + `container`

Common pitfalls:

- equip visuals often also need `owner.AnimState:OverrideSymbol(...)`.
- `equippable` alone does not create armor or weapon behavior.
- restrictions should be tested across save or load and character swap edges.

Read next:

- `references/components/weapon.md`
- `references/components/armor.md`
