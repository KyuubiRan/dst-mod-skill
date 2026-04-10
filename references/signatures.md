# High-Frequency Signatures

Use this page as a router for signature lookups.

Read only the narrow page you need:

- `hook-signatures.md`
  - registration APIs from `modutil.lua`
- `entityscript-signatures.md`
  - high-frequency `EntityScript` methods
- `helper-signatures.md`
  - high-frequency helpers from `standardcomponents.lua`
- `runtime-signatures.md`
  - observed high-frequency runtime globals

## Fast Router

- "I need an exact `modutil.lua` registration signature"
  - read `hook-signatures.md`
- "I need a common prefab helper signature"
  - read `helper-signatures.md`
- "I need the exact `inst:` call shape"
  - read `entityscript-signatures.md`
- "I need a runtime global or input method shape"
  - read `runtime-signatures.md`

## Rule Of Thumb

- use these pages to stop guessing parameter order
- then verify the closest official caller before writing real mod code
