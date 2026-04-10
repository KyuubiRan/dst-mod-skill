# `finiteuses`

Use this file when the task changes use-count durability on tools, weapons, or limited-use utility items.

Official source:

- `scripts/components/finiteuses.lua`

Close official prefab shapes:

- `scripts/prefabs/spear.lua`
- `scripts/prefabs/saddlehorn.lua`

High-frequency methods:

- `SetConsumption(action, uses)`
- `SetMaxUses(val)`
- `SetUses(val)`
- `GetUses()`
- `Use(num)`
- `GetPercent()`
- `SetPercent(amount)`
- `SetOnFinished(fn)`
- `Repair(repairvalue)`
- `SetIgnoreCombatDurabilityLoss(value)`

Common pairings:

- `finiteuses` + `tool`
- `finiteuses` + `weapon`
- `finiteuses` + `inventoryitem`

Common pitfalls:

- `finiteuses` is use-count durability, not armor condition and not fuel time.
- action consumption and combat consumption are separate decisions.
- if the request says infinite durability, omit `finiteuses` entirely.

Read next:

- `references/components/tool.md`
- `references/components/weapon.md`
