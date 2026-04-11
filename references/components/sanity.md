# `sanity`

Use this file when the task changes sanity gain or loss, lunacy, aura immunity, or penalty-adjusted sanity limits.

Official source:

- `scripts/components/sanity.lua`

Close official prefab shapes:

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/wathgrithr.lua`

High-frequency methods:

- `GetPercent()`
- `GetRealPercent()`
- `SetPercent(per, overtime)`
- `DoDelta(delta, overtime)`
- `SetMax(amount)`
- `EnableLunacy(enable, source)`
- `AddSanityPenalty(key, mod)`
- `RemoveSanityPenalty(key)`
- `SetFullAuraImmunity(immunity, source)`
- `SetNegativeAuraImmunity(immunity, source)`

Common pairings:

- `sanity` + player replica or classified flow
- `sanity` + `talker`

Common pitfalls:

- `GetPercent()` may reflect penalty-adjusted values; compare with `GetRealPercent()` when debugging.
- lunacy and insanity are mode logic, not just a negative delta.
- ongoing aura or mode recalculation can overwrite one-off sanity writes.

Read next:

- `references/patterns/player-network-patterns.md`
- `references/components/talker.md`
