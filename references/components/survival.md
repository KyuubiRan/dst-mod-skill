# Survival Components

Use this file for survival stats and state changes: `health`, `hunger`, `sanity`.

## `health`

Official file:

- `scripts/components/health.lua`

High-frequency methods:

- `GetPercent()`
- `SetPercent(percent, overtime, cause)`
- `DoDelta(amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb)`
- `SetCurrentHealth(amount)`
- `SetMaxHealth(amount)`
- `SetPenalty(penalty)`
- `DeltaPenalty(delta)`
- `Kill()`
- `ForceKill()`
- `IsDead()`
- `SetInvincible(val)`

Use it for:

- direct healing or damage
- max health changes
- death, revive, and damage gating flows
- health penalty systems

Common pitfalls:

- `DoDelta(...)` and `SetPercent(...)` are not interchangeable
- `Kill()` respects more normal flow; `ForceKill()` bypasses invincibility
- health changes are server-authoritative

## `hunger`

Official file:

- `scripts/components/hunger.lua`

High-frequency methods:

- `GetPercent()`
- `SetPercent(p, overtime)`
- `SetCurrent(current, overtime)`
- `DoDelta(delta, overtime, ignore_invincible)`
- `SetMax(amount)`
- `SetRate(rate)`
- `Pause()`
- `Resume()`
- `IsStarving()`

Use it for:

- changing hunger values directly
- changing hunger drain rate
- pausing drain during special states
- starvation behavior

Common pitfalls:

- `SetRate(...)` changes ongoing drain, not current hunger value
- starvation damage flow is tied to hunger update logic
- hunger changes should usually be made on the server side

## `sanity`

Official file:

- `scripts/components/sanity.lua`

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
- `IsSane()`
- `IsInsane()`
- `IsLunacyMode()`

Use it for:

- sanity gain and loss
- lunacy mode or enlightenment behavior
- aura immunity or penalty systems
- max sanity tuning

Common pitfalls:

- `GetPercent()` may reflect penalty-adjusted behavior; when debugging, also compare with `GetRealPercent()`
- lunacy and insanity logic is more than just subtracting sanity
- one-off writes can be overridden by ongoing sanity or aura updates
