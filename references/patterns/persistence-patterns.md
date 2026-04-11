# Persistence Patterns

Use this file when the task needs entity or world save lifecycle, offline progression, post-load reference repair, or nested owned-entity persistence.

If the task mainly needs ready-to-copy shapes, also read `references/templates/persistence-templates.md`.
If the task is really about cross-save local settings or `TheSim:SetPersistentString(...)`, read `references/patterns/persistent-string-patterns.md` instead.
If the task needs guarded decode or encode around serialized payloads, also read `references/patterns/protected-call-patterns.md`.

## Official Lifecycle Order

Observed in `scripts/entityscript.lua`:

1. `EntityScript:GetPersistData()`
   - calls each component `OnSave()`
   - then calls entity `OnSave(inst, data)`
2. `EntityScript:SetPersistData(data, newents)`
   - optionally adds missing components when saved data requests it
   - calls entity `OnPreLoad(data, newents)` first
   - then calls each component `OnLoad(v, newents)`
   - then calls entity `OnLoad(data, newents)`
3. `EntityScript:LoadPostPass(newents, savedata)`
   - calls each component `LoadPostPass(newents, v)`
   - then calls entity `OnLoadPostPass(newents, savedata)`
4. `EntityScript:LongUpdate(dt)`
   - calls entity `OnLongUpdate(dt)`
   - then calls each component `LongUpdate(dt)`

Practical consequence:

- plain scalar data belongs in `OnSave` and `OnLoad`
- cross-entity references usually belong in `LoadPostPass`
- offline elapsed-time simulation belongs in `LongUpdate`

## Choose The Narrowest Persistence Tool

- simple booleans, numbers, strings, or small tables
  - `OnSave` and `OnLoad`
- need setup before component `OnLoad(...)` runs
  - `OnPreLoad`
- need to reconnect other saved entities after all of them exist
  - `LoadPostPass`
- need progress while the entity was unloaded
  - `LongUpdate`
- owned child entity should be saved as a nested object
  - `GetSaveRecord()` and `SpawnSaveRecord(...)`
- helper child only needs its inner persist data, not a full top-level prefab record
  - `GetPersistData()` and `SetPersistData(...)`
- local profile-like settings, cache, or cross-save local mod data
  - `references/patterns/persistent-string-patterns.md`

## Scalar State

Use plain `OnSave` and `OnLoad` when the data is local to the entity and does not depend on other entities already existing.

Observed examples:

- `scripts/prefabs/glommer.lua`
- `scripts/components/armor.lua`
- `scripts/components/fueled.lua`

Good fits:

- a phase flag
- a mode or level number
- current condition or counters
- simple custom booleans

## Cross-Entity References

Use `OnSave` plus `LoadPostPass` when the saved data points at other entities.

Observed in `scripts/components/childspawner.lua`:

- `OnSave()` returns both `data` and `references`
- saved data stores GUIDs such as `childrenoutside`
- `LoadPostPass(newents, savedata)` resolves those GUIDs back to spawned entities

Practical rule:

- do not assume the target entity already exists during ordinary `OnLoad(...)`
- save the GUIDs or reference keys
- repair the live links in `LoadPostPass(...)`

## Nested Owned Entities

Use full save records when an entity owns another entity as data rather than only referencing it.

Observed in `scripts/prefabs/player_common.lua`:

- `inst._sleepinghandsitem:GetSaveRecord()`
- `SpawnSaveRecord(data.sleepinghandsitem)`

Observed in `scripts/components/inventory.lua` and `scripts/components/container.lua`:

- held items are saved as save records and respawned through `SpawnSaveRecord(...)`

Use this when:

- the parent owns the child entity's full state
- the child should respawn with its own prefab, components, and data

## Nested Persist Data Without A Full Save Record

Use `GetPersistData()` and `SetPersistData(...)` when a helper entity already exists and you only need to serialize its internal persist block.

Observed in `scripts/components/slingshotmods.lua`:

- `self.containerinst:GetPersistData()`
- `self.containerinst:SetPersistData(data.parts, newents)`

Use this when:

- the helper entity is recreated by code
- only its inner component state needs to be restored

## Offline Progress And Time Catch-Up

Use `LongUpdate(dt)` when the entity should advance while unloaded or while world time jumps forward.

Observed examples:

- `scripts/components/timer.lua`
- `scripts/components/pickable.lua`
- `scripts/components/perishable.lua`
- `scripts/components/childspawner.lua`

Practical rule:

- `LongUpdate(dt)` is for elapsed-time catch-up
- it is not a replacement for ordinary frame updates

## `OnPreLoad`

Use `OnPreLoad(data, newents)` only when some setup must happen before component `OnLoad(...)` runs.

Observed in `scripts/prefabs/player_common.lua`:

- shard migration data is prepared in `OnPreLoad(...)`

Use it sparingly.
Most ordinary restore logic belongs in `OnLoad(...)`.

## `OnLoadPostPass`

Use this when the entity itself, not only a component, must reconnect after all spawned entities are available.

Observed examples:

- `scripts/prefabs/winona_battery_low.lua`
- `scripts/prefabs/daywalker.lua`
- `scripts/prefabs/spiderden.lua`

Typical fits:

- reconnect tracked entities
- re-run linkage that depends on spawned neighbors
- repair visuals or AI state that depends on resolved references

## Save Migration And Optional Components

Observed in `scripts/entityscript.lua`:

- save data may request `add_component_if_missing`
- `SetPersistData(...)` can add the component before `OnLoad(...)`

Observed in `scripts/components/deathloothandler.lua`:

- component `OnSave()` returns `add_component_if_missing = true`

Use this only when old saves may load into a newer prefab shape that now needs that component.

## Common Failure Points

- stored live entity references directly in saved data instead of GUIDs or save records
- tried to reconnect external entities in `OnLoad(...)` before they existed
- used `LongUpdate(...)` for logic that should really be immediate restore in `OnLoad(...)`
- forgot that components load before entity `OnLoad(...)`
- saved nested child state manually when `GetSaveRecord()` already matched the need

## Rule Of Thumb

- local scalar state: `OnSave` and `OnLoad`
- cross-entity links: `LoadPostPass`
- owned child entities: `GetSaveRecord()` and `SpawnSaveRecord(...)`
- offline elapsed time: `LongUpdate(dt)`
- cross-save local settings or cache: `TheSim:SetPersistentString(...)` and `GetPersistentString(...)`
