# Runtime Signatures

Observed or mixed-source high-frequency runtime signatures.

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
TheWorld:PushEvent(event, data)
TheNet:IsDedicated()
TheNet:GetIsServer()
```

Notes:

- `TheSim:FindEntities` is engine-provided, so treat this as an observed official usage shape.
- `TheWorld.ismastersim` is a field check, not a function call.
- `ThePlayer` is a global local-player reference, not a function call.
