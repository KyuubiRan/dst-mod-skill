# AnimState Patterns

Use this file when the task needs `inst.AnimState` behavior, animation playback control, symbol overrides, or animation-driven UI state.

`AnimState` itself is engine-side, not a normal Lua module.
There is no `scripts/animstate.lua` to read in `scripts.zip`.

For script-level truth, inspect real usage in:

- `scripts/prefabs/*.lua`
- `scripts/stategraphs/*.lua`
- `scripts/widgets/*.lua`
- `scripts/screens/*.lua`

The method list and the `layer` versus `symbol` explanation below are also informed by the public tutorial at `https://atjiu.github.io/dstmod-tutorial/#/animstate`.
Treat that page as practical supplementary guidance, not as the authoritative source of engine behavior.

## Start With These Concepts

- `bank`
  - animation set name used by the entity
- `build`
  - build or skin source that provides symbols and art
- animation name
  - the concrete clip passed to `PlayAnimation(...)` or `PushAnimation(...)`
- `symbol`
  - named art channel used by `OverrideSymbol(...)`, `HideSymbol(...)`, and `ShowSymbol(...)`
- `layer`
  - named animation layer used by `Hide(...)` and `Show(...)`

Practical rule:

- if you are swapping equipment art or a specific sprite part, think `symbol`
- if you are toggling a whole animation layer from the animation data, think `layer`

## High-Frequency Methods

### Basic Setup

Most prefab constructors follow this shape:

```lua
inst.entity:AddAnimState()

inst.AnimState:SetBank("my_item")
inst.AnimState:SetBuild("my_item")
inst.AnimState:PlayAnimation("idle")
```

Observed in many official prefabs such as `scripts/prefabs/mosquitomusk.lua`.

### Queue Animations

Use `PlayAnimation(...)` for the immediate current clip.
Use `PushAnimation(...)` to queue the next clip after the current one finishes.

Official example from `scripts/prefabs/oceanfishingbobber.lua`:

```lua
inst.AnimState:PlayAnimation("spin_pre", false)
inst.AnimState:PushAnimation("spin_loop", true)
```

Official example from `scripts/prefabs/spiderden.lua`:

```lua
inst.AnimState:PlayAnimation("cocoon_enter")
inst.AnimState:PushAnimation(inst.anims.idle, true)
```

### Hide Or Show A Layer

Use these when the target name is a layer from the animation data:

```lua
inst.AnimState:Hide("HORROR")
inst.AnimState:Show("CHEMICAL")
```

Observed in `scripts/prefabs/winona_battery_low.lua`.

The public tutorial is useful here because it explains that the layer names come from animation data such as `anim.bin`.
That distinction is not obvious from official script usage alone.

### Hide Or Show A Symbol

Use these when the target is a concrete symbol channel:

```lua
inst.AnimState:HideSymbol("bedazzled_flare")
```

Observed official usage:

- `HideSymbol(...)` in `scripts/prefabs/spiderden.lua`
- `ShowSymbol(...)` in `scripts/prefabs/nightmarefissure.lua`

### Override A Symbol

Use `OverrideSymbol(oldsymbol, newbuild, newsymbol)` when one symbol should render from another build.

Common equipment pattern:

```lua
owner.AnimState:OverrideSymbol("swap_body", "swap_icepack", "swap_body")
owner.AnimState:ClearOverrideSymbol("swap_body")
```

Observed in `scripts/prefabs/icepack.lua`, `scripts/prefabs/candybag.lua`, `scripts/prefabs/raincoat.lua`, and similar wearable prefabs.

Common frozen overlay pattern:

```lua
inst.AnimState:OverrideSymbol("swap_frozen", "frozen", "frozen")
inst.AnimState:ClearOverrideSymbol("swap_frozen")
```

Observed in `scripts/prefabs/spiderden.lua`.

### Freeze An Animation At A Progress Point

Use `SetPercent(animname, percent)` when the animation should represent a progress meter or a fixed point in the clip instead of playing normally.

Official UI example from `scripts/widgets/ringmeter.lua`:

```lua
self.meter:GetAnimState():SetPercent("progress", self.t / self.duration)
```

Official world example from `scripts/prefabs/worm_boss.lua`:

```lua
inst.AnimState:SetPercent(anim, time - adjust)
```

Practical rule:

- use this for progress bars, gauges, growth visuals, and synced pose updates
- do not expect `SetPercent(...)` alone to keep animating frame by frame; it is usually used to place the animation at a specific point

### Change Playback Speed

Use `SetDeltaTimeMultiplier(mult)` when the current animation should run faster or slower.

Observed official usage:

- `scripts/prefabs/pocketwatch_common.lua`
- `scripts/components/anchor.lua`
- `scripts/stategraphs/SGtentacle_arm.lua`

Practical rule:

- restore it to `1` when the speed override should end
- avoid leaving a shared entity stuck at a custom multiplier after a one-off action

### Query Current Playback State

Common read-side helpers from script usage:

- `AnimDone()`
  - used when code needs to know whether a clip finished
- `IsCurrentAnimation(animname)`
  - used when logic depends on the current clip name

Observed examples:

- `scripts/widgets/ringmeter.lua`
- `scripts/prefabs/worm_boss.lua`

## Typical Patterns

### Minimal Prefab Animation Setup

```lua
local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("my_item")
    inst.AnimState:SetBuild("my_item")
    inst.AnimState:PlayAnimation("idle", true)

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    return inst
end
```

### One-Shot Then Loop

```lua
inst.AnimState:PlayAnimation("place")
inst.AnimState:PushAnimation("idle", false)
```

This shape is common for place, hit, thaw, burst, and transition visuals.

### Equipment Or Skin Symbol Swap

```lua
local function onequip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_object", "swap_myweapon", "swap_myweapon")
end

local function onunequip(inst, owner)
    owner.AnimState:ClearOverrideSymbol("swap_object")
end
```

When this is for player-held items, confirm the real symbol names from official equipment prefabs before assuming `swap_object`, `swap_body`, or `backpack`.

### Progress-Driven Meter

```lua
local percent = math.clamp(current / max, 0, 1)
inst.AnimState:SetPercent("meter", percent)
```

This is the common shape for gauges, crop growth visuals, and radial UI bars.

## Where To Verify Names

When animation names or symbol names are uncertain:

1. Inspect the closest official prefab or widget that uses the same art family.
2. Inspect the relevant stategraph if the animation is actor-driven.
3. If the distinction is specifically `layer` versus `symbol`, use animation tooling to inspect the asset package.

Practical reality:

- official scripts tell you which names are actually used
- asset tooling tells you which names exist inside the animation package

## Common Pitfalls

- `SetBank(...)` and `SetBuild(...)` are not interchangeable.
- Reusing a build with the wrong bank often fails silently as "animation does not play".
- `PlayAnimation(...)` without a follow-up `PushAnimation(...)` often leaves transition animations stuck at the end.
- `OverrideSymbol(...)` fails visually if `newbuild` or `newsymbol` does not exist.
- `Hide(...)` targets layer names, while `HideSymbol(...)` targets symbol names.
- UI widgets often call `GetAnimState()` on a child widget, not `inst.AnimState`.
- When adjusting playback speed, remember to restore `SetDeltaTimeMultiplier(1)`.

## Rule Of Thumb

- For prefab startup visuals, start with `SetBank`, `SetBuild`, and `PlayAnimation`.
- For transition flows, add `PushAnimation`.
- For wearable or skinned visuals, inspect `OverrideSymbol` patterns first.
- For progress bars or fixed poses, inspect `SetPercent`.
- If a name looks uncertain, verify it against official script usage before assuming the tutorial naming matches your asset.
