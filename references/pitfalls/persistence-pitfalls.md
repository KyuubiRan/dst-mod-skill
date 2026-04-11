# Persistence Pitfalls

Use this file when save or load logic technically runs, but restored state is wrong after reload, migration, or time skip.

## Common Failure Shapes

- state resets after reload
  - `OnSave(...)` never wrote it or `OnLoad(...)` never restored it
- linked entity is nil after reload
  - it should probably be resolved in `LoadPostPass(...)`
- offline time passed but crops, timers, or perish state did not advance
  - `LongUpdate(dt)` is missing or incomplete
- child helper respawns empty
  - it likely needed `GetSaveRecord()` or `GetPersistData()`
- old saves crash or lose new behavior
  - optional component migration may need `add_component_if_missing`
- local settings keep resetting between runs
  - the task may have used entity save hooks instead of `TheSim` persistent strings
- world-specific data leaks across different saves
  - plain persistent strings were used where world or entity save lifecycle was required

## Practical Rules

- do not store live entity objects directly in save data
- do not reconnect other saved entities in `OnLoad(...)` if they may not exist yet
- do not use `LongUpdate(...)` for ordinary immediate restore logic
- do not save huge redundant state when one canonical field is enough

## Fast Router

- lifecycle order is unclear
  - read `references/patterns/persistence-patterns.md`
- cross-save local config or cache is the real need
  - read `references/patterns/persistent-string-patterns.md`
- malformed serialized data may be the real problem
  - read `references/patterns/protected-call-patterns.md`
- need minimal implementation shape
  - read `references/templates/persistence-templates.md`
- symptom-led debugging
  - also read `references/patterns/diagnostic-patterns.md`
