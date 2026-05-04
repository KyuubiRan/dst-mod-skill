# Animation Build Patterns

Read this page when the task is about compiling `.scml`, rebuilding `anim/*.zip`, recovering a compiled animation zip into `.scml`, or understanding the `exported/<name>/` animation workspace produced by Don't Starve Mod Tools.

## Prefer Official Mod Tools

Use the local `Don't Starve Mod Tools` install as the source of truth for animation compilation.

High-value files:

- `mod_tools\scml.exe`
- `mod_tools\tools\scripts\buildanimation.py`
- `mod_tools\compiler_scripts\zipanim.py`
- `mod_tools\exported\export.py`

Practical rule:

- prefer official Mod Tools over third-party animation packers
- treat `build.bin`, `anim.bin`, and `atlas-*.tex` as compiled outputs, not hand-edited source
- when the task is only "rebuild the animation", compile first and edit `.scml` only if the user explicitly wants asset changes
- when original source `.scml` is missing and the user needs inspection or recovery, decompile the compiled zip with `scripts/anim_scml_tool.py`

## The Official Build Chain

The local Mod Tools chain works in two stages.

1. `scml.exe` reads one `.scml` file plus its sibling PNG folders.
2. It regenerates the same-folder intermediate `<name>.zip`.
3. It then drives the normal compiler flow and writes the final `anim/<name>.zip`.

Observed local behavior:

- input: `exported/huohuo/huohuo.scml`
- regenerated intermediate: `exported/huohuo/huohuo.zip`
- final compiled output: `<output_dir>/anim/huohuo.zip`

Practical rule:

- the regenerated same-folder zip is a build intermediate, not the primary user-authored source
- when the user says "compile this `.scml`", start from the `.scml` instead of asking them to point at the intermediate zip
- if that same-folder zip is open in another program and the build fails with a permission or lock error, explain that the tool is attempting to overwrite its own intermediate output

The final compiled zip contains files such as:

- `anim.bin`
- `build.bin`
- `atlas-0.tex`
- `atlas-1.tex`

## Recover A Compiled Animation Zip

Use `scripts/anim_scml_tool.py` when the user has a compiled `anim/<name>.zip` and wants to inspect or recover it as a Spriter project.

Example:

```bash
python scripts/anim_scml_tool.py decompile anim/huohuo.zip --output-dir .tmp/exported/huohuo_recovered --force
```

The script reads:

- `build.bin`
- `anim.bin`
- `atlas-*.tex`

It writes:

- `<buildname>.scml`
- symbol PNG folders referenced by the SCML

Practical rules:

- this is a recovery/decompilation workflow, not the preferred source workflow
- the input zip must contain both `build.bin` and `anim.bin`; some character build zips contain only `build.bin` plus atlases and are not standalone animations
- recovered SCML can lose fidelity because Spriter cannot express every DST-native transform such as shear
- prefer the user's original exported `.scml` and PNG folders when they exist
- use recovered output for inspection, small edits, or rebuilding a missing source workspace
- after editing recovered SCML, compile through `scripts/scml_build_tool.py build`, not by editing `anim.bin` or `build.bin`

## Important CLI Detail

`scml.exe` takes an output directory as its second argument.
Do not treat the second argument like a destination zip filename.

Example:

```bash
python scripts/scml_build_tool.py build .tmp/exported/huohuo/huohuo.scml --output-dir .tmp/exported/compiled
```

This produces:

- updated intermediate zip: `.tmp/exported/huohuo/huohuo.zip`
- final compiled zip: `.tmp/exported/compiled/anim/huohuo.zip`

If the output argument looks like `something.zip`, Mod Tools still treat it like a folder and will create `something.zip/anim/...`.

## Fast Path When Intermediate Zip Already Exists

If the exported folder already contains `<name>.zip`, you can skip the `.scml` step and compile that zip directly through `buildanimation.py`.

Example:

```bash
python scripts/scml_build_tool.py compile .tmp/exported/huohuo/huohuo.zip --output-dir .tmp/exported/compiled --force
```

Use this fast path when:

- the user already has a fresh exported zip
- the task is only to rebuild `anim/<name>.zip`
- you need a narrower debug loop around texture-format or atlas output

Do not switch to this path by default just because the exported folder happens to contain `<name>.zip`.
That zip usually exists because the official `.scml` build path generated it earlier.

## File Layout Expectations

The `.scml` file should sit at the root of one exported animation folder, with its referenced PNG folders beside it.

Typical shape:

```text
exported/huohuo/
  huohuo.scml
  huohuo.zip
  face/
  torso/
  hand/
  ...
```

Practical rule:

- keep the image folders beside the `.scml`
- do not move the PNG folders away from the `.scml` and then expect relative paths to keep working
- do not assume `bigportraits/` or other UI textures belong in the compiled `anim/*.zip`; animation compilation only consumes what the exported build references

## Validation Checklist

- confirm `Don't Starve Mod Tools` is installed locally before promising compile support
- confirm `scml.exe` exists before the `.scml` build path
- confirm `buildanimation.py` and the bundled Python 2.7 exist before the zip fast path
- after compilation, confirm the final zip exists under `anim/`
- if the compiled zip is suspiciously tiny or missing `build.bin` or `anim.bin`, treat the compile as failed
