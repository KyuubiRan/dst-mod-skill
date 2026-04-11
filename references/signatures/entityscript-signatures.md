# EntityScript Signatures

Exact signatures copied from `scripts/entityscript.lua`.

```lua
inst:AddTag(tag)
inst:RemoveTag(tag)
inst:AddOrRemoveTag(tag, condition)
inst:HasTag(tag)
inst:HasTags(...)
inst:HasOneOfTags(...)
inst:AddComponent(name)
inst:RemoveComponent(name)
inst:ListenForEvent(event, fn, source)
inst:RemoveEventCallback(event, fn, source)
inst:PushEvent(event, data)
inst:PushEventImmediate(event, data)
inst:SpawnChild(name)
inst:AddChild(child)
inst:RemoveChild(child)
inst:SetBrain(brainfn)
inst:RestartBrain(reason)
inst:StopBrain(reason)
inst:SetStateGraph(name)
inst:ClearStateGraph()
inst:DoPeriodicTask(time, fn, initialdelay, ...)
inst:DoTaskInTime(time, fn, ...)
inst:PushEventInTime(time, eventname, data)
inst:PushBufferedAction(bufferedaction)
inst:PerformBufferedAction()
inst:SetInherentSceneAction(action)
inst:SetInherentSceneAltAction(action)
```
