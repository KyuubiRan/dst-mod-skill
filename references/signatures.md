# High-Frequency Signatures

Use this page as a router for signature lookups.

Read only the narrow page you need under `references/signatures/`:

- `references/signatures/hook-signatures.md`
  - registration APIs from `modutil.lua`
- `references/signatures/entityscript-signatures.md`
  - high-frequency `EntityScript` methods
- `references/signatures/helper-signatures.md`
  - high-frequency helpers from `standardcomponents.lua`
- `references/signatures/runtime-signatures.md`
  - observed high-frequency runtime globals

## Fast Router

- "I need an exact `modutil.lua` registration signature"
  - read `references/signatures/hook-signatures.md`
- "I need a common prefab helper signature"
  - read `references/signatures/helper-signatures.md`
- "I need the exact `inst:` call shape"
  - read `references/signatures/entityscript-signatures.md`
- "I need a runtime global or input method shape"
  - read `references/signatures/runtime-signatures.md`

## Rule Of Thumb

- use these pages to stop guessing parameter order
- then verify the closest official caller before writing real mod code
