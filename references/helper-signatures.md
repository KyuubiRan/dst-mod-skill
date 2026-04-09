# Helper Signatures

High-frequency helper signatures copied from `scripts/standardcomponents.lua`.

```lua
MakeSmallBurnable(inst, time, offset, structure, sym)
MakeMediumBurnable(inst, time, offset, structure, sym)
MakeLargeBurnable(inst, time, offset, structure, sym)

MakeSmallPropagator(inst)
MakeMediumPropagator(inst)
MakeLargePropagator(inst)

MakeTinyFreezableCharacter(inst, sym, offset)
MakeSmallFreezableCharacter(inst, sym, offset)
MakeMediumFreezableCharacter(inst, sym, offset)
MakeLargeFreezableCharacter(inst, sym, offset)

MakeInventoryPhysics(inst, mass, rad)
MakeProjectilePhysics(inst, mass, rad)
MakeCharacterPhysics(inst, mass, rad)
MakeFlyingCharacterPhysics(inst, mass, rad)
MakeObstaclePhysics(inst, rad, height)
MakeHeavyObstaclePhysics(inst, rad, height)

MakeHauntable(inst, cooldown, haunt_value)
MakeHauntableLaunch(inst, chance, speed, cooldown, haunt_value)
MakeHauntableWork(inst, chance, cooldown, haunt_value)
MakeHauntableIgnite(inst, chance, cooldown, haunt_value)
MakeHauntableChangePrefab(inst, newprefab, chance, haunt_value, nofx)

MakeInventoryFloatable(inst, size, offset, scale, swap_bank, float_index, swap_data)
MakeDeployableFertilizerPristine(inst)
MakeDeployableFertilizer(inst)
MakeForgeRepairable(inst, material, onbroken, onrepaired)
```
