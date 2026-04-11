# Persistence Templates

Use this file when a task already knows it needs entity or world save logic and now wants the smallest practical implementation shape.

Read `references/patterns/persistence-patterns.md` first for lifecycle and routing.
If the task is actually a local persistent file such as mod settings or cached profile data, read `references/patterns/persistent-string-patterns.md` instead.
If the task needs safe decode or encode wrappers, also read `references/patterns/protected-call-patterns.md`.

## Template: Plain Scalar State

Use this for local booleans, numbers, and compact tables.

```lua
local function OnSave(inst, data)
    data.mode = inst._mode
    data.level = inst._level > 0 and inst._level or nil
end

local function OnLoad(inst, data)
    if data ~= nil then
        inst._mode = data.mode or "idle"
        inst._level = data.level or 0
    end
end
```

## Template: Resolve Other Saved Entities In `LoadPostPass`

Use this when the data points at other saved entities by GUID.

```lua
local function OnSave(inst, data)
    local refs = {}
    if inst._linked ~= nil then
        data.linked = inst._linked.GUID
        refs[1] = inst._linked.GUID
    end
    return refs
end

local function OnLoadPostPass(inst, newents, data)
    if data ~= nil and data.linked ~= nil then
        local record = newents[data.linked]
        inst._linked = record ~= nil and record.entity or nil
    end
end
```

Practical rule:

- save identifiers in `data`
- return the same GUIDs as `refs`
- reconnect in `OnLoadPostPass(...)`

## Template: Owned Child Entity Save Record

Use this when the parent owns a full child entity state.

```lua
local function OnSave(inst, data)
    if inst._child ~= nil and inst._child:IsValid() then
        data.child = inst._child:GetSaveRecord()
    end
end

local function OnLoad(inst, data)
    if data ~= nil and data.child ~= nil then
        local child = SpawnSaveRecord(data.child)
        if child ~= nil then
            inst._child = child
        end
    end
end
```

## Template: Helper Entity Persist Block

Use this when code recreates the helper entity and only its persist data must be restored.

```lua
function MyComponent:OnSave()
    if self.helper ~= nil then
        local helper_data, refs = self.helper:GetPersistData()
        return { helper = helper_data }, refs
    end
end

function MyComponent:OnLoad(data, newents)
    if data ~= nil and data.helper ~= nil then
        self:CreateHelper()
        self.helper:SetPersistData(data.helper, newents)
    end
end
```

## Template: Offline Catch-Up With `LongUpdate`

Use this when the entity should advance while unloaded.

```lua
function MyComponent:LongUpdate(dt)
    if self.cooldown > 0 then
        self.cooldown = math.max(0, self.cooldown - dt)
        if self.cooldown == 0 then
            self.inst:PushEvent("cooldownfinished")
        end
    end
end
```

Good fits:

- cooldowns
- regrowth
- perish timers
- delayed phase changes

## Template: Save Migration With `add_component_if_missing`

Use this only when old saves may load into a newer prefab shape that now expects a component.

```lua
function MyComponent:OnSave()
    return
    {
        value = self.value,
        add_component_if_missing = true,
    }
end
```

Observed official loader behavior:

- `EntityScript:SetPersistData(...)` can add the missing component before `OnLoad(...)`

## Quick Router

- plain fields
  - scalar template
- GUID references to other entities
  - `LoadPostPass` template
- parent owns a child entity
  - save-record template
- helper entity already recreated elsewhere
  - persist-block template
- offline time must advance state
  - `LongUpdate` template
