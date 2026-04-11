# DST Mod Development Skill

[Chinese](./README_zh.md)

This repository packages a local skill for Don't Starve Together mod development.
It is designed to help Codex work from official DST source files first, then choose the narrowest safe implementation path for mod code.

## What This Skill Helps With

- reading `modinfo.lua`, `modmain.lua`, and related entry files
- classifying a mod as `all-clients`, `client-only`, or `server-only`
- routing tasks across prefabs, components, brains, stategraphs, widgets, screens, RPC, replica, persistence, and shard runtime
- matching feature requests to common component bundles and prefab tags
- debugging host versus client issues, save or load bugs, and Master versus Caves problems
- reading `client_log.txt`, server logs, and `backup/` history before guessing at error causes
- inspecting official game source and texture atlases quickly

## Included In The Repository

- `SKILL.md`
  - the core skill instructions and routing rules
- `references/`
  - root router docs plus grouped detail folders such as `patterns/`, `signatures/`, `pitfalls/`, `templates/`, and `components/`
- `scripts/check_skill.py`
  - lightweight repository validation
- `scripts/dst_zip_tool.py`
  - search, read, and extract files from the official DST `scripts.zip`
- `scripts/init_dst_mod.py`
  - scaffold a basic DST mod
- `scripts/bundle_release.py`
  - build a release directory with exclusion and incremental sync support
- `scripts/tex_atlas_tool.py`
  - unpack official or local atlas TEX/XML data, or pack multiple PNGs into one atlas
- `scripts/resize_png.py`
  - resize one PNG or a whole PNG directory for DST texture workflows

## Source Of Truth

This skill is built around one rule:

- prefer local official DST files over memory

In practice that means:

- inspect `data/databundles/scripts.zip` for code behavior
- inspect `data/databundles/images.zip` for official texture atlases
- avoid copying large official functions when a smaller hook already fits
- separate server, client, local UI, persistence, and shard concerns before editing

## Typical Use Cases

- "Read this mod and tell me whether it is client-only or all-clients."
- "Add a weapon prefab and wire the right components."
- "Patch an existing container without rewriting the whole widget."
- "Debug why the feature works on host but not on remote clients."
- "Find the correct save or load phase for this data."
- "Inspect how official migration or shard logic handles this case."
- "Unpack an official icon atlas and show me the files."

## Setup Requirements

- a local Don't Starve Together installation
- Python 3
- Pillow for `tex_atlas_tool.py` and `resize_png.py`

Common DST install paths:

- Windows:
  - `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Linux:
  - `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- macOS:
  - `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`

Common script bundle path:

- `data/databundles/scripts.zip`

Common texture bundle path:

- `data/databundles/images.zip`

If your local install path differs, provide it explicitly when using the skill.

When you pass game paths into shell commands, quote or escape them correctly.
This matters for paths such as `Don't Starve Together`, because special characters like the apostrophe can make the first command fail if they are not escaped.

## Example Commands

Search official source:

```bash
python scripts/dst_zip_tool.py grep AddPrefabPostInit --path-glob "scripts/*.lua"
```

Read a source range:

```bash
python scripts/dst_zip_tool.py show scripts/entityscript.lua --start 600 --end 700
```

Scaffold a new mod:

```bash
python scripts/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

Build a release directory:

```bash
python scripts/bundle_release.py . --output ..\MyMod_release
```

Unpack an official atlas:

```bash
python scripts/tex_atlas_tool.py unpack inventoryimages1
```

Resize an icon:

```bash
python scripts/resize_png.py path/to/icon.png 64x64
```

Run a quick repository check:

```bash
python scripts/check_skill.py
```

## Where To Start

If you are new to the repository, the most useful entry points are:

- `SKILL.md`
- `references/task-playbook.md`
- `references/official-examples.md`
- `references/patterns.md`
- `references/patterns/modinfo-patterns.md`
- `references/patterns/modmain-patterns.md`
- `references/component-patterns.md`
- `references/feature-recipes.md`
- `references/patterns/networking-patterns.md`
- `references/patterns/persistence-patterns.md`
- `references/patterns/shard-patterns.md`
- `references/patterns/ui-patterns.md`
- `references/patterns/effects-patterns.md`

## Recommended Workflow

1. Confirm the local DST path if it is not in a standard location.
2. Read the target mod's `modinfo.lua`.
3. Classify the mod type before touching runtime code.
4. Inspect the smallest official source file that already matches the requested feature.
5. Implement with the narrowest hook that fits.
6. Validate the result instead of assuming the first patch point is correct.
