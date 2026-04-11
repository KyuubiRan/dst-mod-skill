# `tool`

Use this file when the task changes worker-side action effectiveness such as chop, mine, hammer, dig, or other tool action support.

Official source:

- `scripts/components/tool.lua`

Close official prefab shapes:

- `scripts/prefabs/axe.lua`
- `scripts/prefabs/lucy.lua`

High-frequency methods:

- `EnableToughWork(tough)`
- `CanDoToughWork()`
- `GetEffectiveness(action)`
- `SetAction(action, effectiveness)`
- `CanDoAction(action)`

Common pairings:

- `tool` + `inventoryitem`
- `tool` + `finiteuses`
- `tool` + `equippable`

Common pitfalls:

- `tool` belongs on the acting item.
- target-side work logic lives in `workable`.
- if the request says infinite durability, omit `finiteuses`.

Read next:

- `references/components/workable.md`
- `references/patterns/action-patterns.md`
