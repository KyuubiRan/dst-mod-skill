# Brain Patterns

Use this file when the task creates or patches NPC AI behavior.
If the issue is mostly performer animation, action timing, or hit windows, read `references/patterns/stategraph-patterns.md` instead of treating it as a brain problem.

This page focuses on the common DST brain path:

- `scripts/brains/<name>.lua`
- `require("brains/<name>")`
- `inst:SetBrain(brain)`
- optional `AddBrainPostInit(...)`

## Typical Brain File Shape

Official brains commonly look like this:

```lua
require "behaviours/wander"
require "behaviours/runaway"
require "behaviours/doaction"

local MyBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function MyBrain:OnStart()
    local root = PriorityNode({
        Wander(self.inst, function() return self.inst:GetPosition() end, 4),
    }, .25)

    self.bt = BT(self.inst, root)
end

return MyBrain
```

Common brain pieces:

- `Class(Brain, function(self, inst) ...)`
- `Brain._ctor(self, inst)`
- `function MyBrain:OnStart()`
- `self.bt = BT(self.inst, root)`

## Common Behaviour Nodes

High-frequency nodes seen in official brains:

- `PriorityNode(...)`
- `WhileNode(testfn, name, node)`
- `Wander(...)`
- `RunAway(...)`
- `Follow(...)`
- `DoAction(...)`
- `FaceEntity(...)`
- `ChaseAndAttack(...)`
- `ChattyNode(...)`

These are usually imported from `behaviours/*` files or helper brain modules.

## How A Prefab Uses A Brain

Official prefab pattern:

```lua
local brain = require("brains/mybrain")

...

inst:SetBrain(brain)
inst:SetStateGraph("SGmycreature")
```

Practical consequence:

- the brain file normally lives under `scripts/brains/`
- the prefab loads it with `require("brains/<name>")`
- the actual creature prefab attaches it through `inst:SetBrain(brain)`
- the prefab usually also sets the matching SG right next to it

## Brain And Stategraph Are Separate

Brain answers:

- what the creature wants to do
- what target or action to choose
- when to flee, wander, follow, or attack

Stategraph answers:

- how the creature performs that decision
- what animation/state to enter
- what tags, timing, and action handlers apply

Do not collapse both into one system mentally.

Fast distinction:

- "what should I do next?"
  - brain
- "how do I animate and time that?"
  - stategraph

If a creature chooses the right target but attacks badly, the bug may be SG-side.
If a creature animates correctly but keeps making bad choices, the bug may be brain-side.

## When To Write A New Brain

Write a new brain when:

- the prefab is mod-owned and needs custom decision logic
- the behavior tree is the core of the creature's AI

Prefer patching an existing brain when:

- the task is a small tweak to existing official AI
- the official decision structure already matches closely

## `AddBrainPostInit`

For small extensions to official brains, use:

```lua
AddBrainPostInit("pigguardbrain", function(brain)
    -- patch existing brain object or methods
end)
```

Use this narrowly.
If the AI shape is fundamentally different, a custom brain is usually cleaner.

## Behaviour Tree Is The Core Output

In practice, `OnStart()` must produce a real behavior tree:

```lua
self.bt = BT(self.inst, root)
```

If the brain file exists but never assigns `self.bt`, the creature usually will not behave as expected.

## Common Routing

- mod-owned new creature
  - new brain file plus matching SG
- tweak one official target choice or priority
  - inspect `AddBrainPostInit(...)`
- AI seems wrong only during attack, hit, sleep, freeze, or locomotion execution
  - inspect SG and `commonstates.lua`
- creature logic depends on nearby scans
  - also read `references/patterns/entity-query-patterns.md`

## Read The Closest Official Brain First

Before writing AI:

- find the closest official creature under `scripts/prefabs/`
- inspect its `require("brains/...")` line
- read that brain under `scripts/brains/`
- inspect any helper modules it depends on, such as `brains/braincommon`

## Rule Of Thumb

- New creature AI: create a dedicated brain file under `scripts/brains/`.
- Existing official AI tweak: prefer `AddBrainPostInit`.
- Keep decision logic in the brain and execution details in the stategraph.
- Always inspect the matching official prefab and stategraph together before changing AI.
