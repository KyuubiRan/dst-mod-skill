# `talker`

Use this file when the task changes speech bubbles, chatter, NPC or boss lines, or intentionally omits normal speech.

Official source:

- `scripts/components/talker.lua`

Close official prefab shapes:

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/daywalker.lua`

High-frequency methods:

- `MakeChatter()`
- `Chatter(strtbl, strid, time, forcetext, echotochatpriority)`
- `Say(script, time, noanim, force, nobroadcast, colour, text_filter_context, original_author_netid, onfinishedlinesfn, sgparam)`
- `ShutUp()`
- `IgnoreAll(source)`
- `StopIgnoringAll(source)`

Common pairings:

- `talker` + `inspectable`
- `talker` + strings
- `talker` + net-aware player or creature presentation

Common pitfalls:

- speech presentation also depends on caller context and string keys, not just `talker.lua`.
- many creature-like prefabs already include `talker`; missing it is often an intentional choice.
- chat echo, local bubble display, and force text are separate concerns.

Read next:

- `references/string-patterns.md`
- `references/player-patterns.md`
