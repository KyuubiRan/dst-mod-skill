# Runtime Signatures

Observed or mixed-source high-frequency runtime signatures.

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
TheSim:SetPersistentString(name, data, encode, callback)
TheSim:GetPersistentString(name, callback)
TheSim:ErasePersistentString(name, callback)
TheSim:CheckPersistentStringExists(name, callback)
TheWorld:PushEvent(event, data)
TheNet:IsDedicated()
TheNet:GetIsServer()
TheFrontEnd:PushScreen(screen)
TheFrontEnd:PopScreen(screen)
TheFrontEnd:GetSound()
TheInput:AddKeyUpHandler(key, fn)
TheInput:AddKeyDownHandler(key, fn)
TheInput:AddKeyHandler(fn)
TheInput:AddMouseButtonHandler(fn)
TheInput:AddMoveHandler(fn)
TheInput:AddControlHandler(control, fn)
TheInput:AddGeneralControlHandler(fn)
TheInput:AddControlMappingHandler(fn)
TheInput:AddTextInputHandler(fn)
```

Notes:

- `TheSim:FindEntities` is engine-provided, so treat this as an observed official usage shape.
- `TheSim:GetPersistentString(...)` is callback-driven; observed usage shape is `function(success, data) ... end`.
- `TheSim:SetPersistentString(...)` and `ErasePersistentString(...)` are also commonly used with callbacks.
- for local mod config, `data` should usually be a JSON string produced by `json.encode(...)`, then restored with guarded `json.decode(...)`.
- `TheWorld.ismastersim` is a field check, not a function call.
- `ThePlayer` is a global local-player reference, not a function call.
- `TheInput` is local input state; use dedicated-server guards and prefer narrow handlers.

## Fast Router

- local screen-stack work
  - `TheFrontEnd:PushScreen`, `TheFrontEnd:PopScreen`
- cross-save local settings or cache
  - `TheSim:SetPersistentString`, `TheSim:GetPersistentString`
- frontend sound
  - `TheFrontEnd:GetSound()`
- mapped control rebinding
  - `TheInput:AddControlMappingHandler`
- ordinary local input
  - the `TheInput:Add*Handler(...)` family
