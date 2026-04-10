# `inspectable`

Use this file when the task changes inspect text, status strings, name override behavior, or intentionally removes normal inspection.

Official source:

- `scripts/components/inspectable.lua`

Close official prefab shapes:

- `scripts/prefabs/treasurechest.lua`
- `scripts/prefabs/rope.lua`

High-frequency methods:

- `SetDescription(desc)`
- `SetNameOverride(nameoverride)`
- `GetStatus(viewer)`
- `GetDescription(viewer)`

Common pairings:

- almost any player-facing prefab
- `inspectable` + runtime `STRINGS`

Common pitfalls:

- many inspect bugs are really wrong prefab names or wrong `STRINGS` keys.
- `inspectable` is so common that its absence is usually the interesting choice.
- special inspect text often needs `references/string-patterns.md`.

Read next:

- `references/string-patterns.md`
- `references/tag-patterns.md`
