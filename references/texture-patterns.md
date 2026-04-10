# Texture Patterns

Use this file when the task is about atlas `tex+xml`, inventory icons, PNG resizing, or extracting official textures from `images.zip`.

This page is about texture workflow, not `AnimState` bank/build logic.
If the task also touches prefab asset registration, read `references/asset-patterns.md`.
If the task is about animation resource compile, keep using the game's official `autocompiler` flow instead of extending these texture scripts.

## Common Cases

- unpack an official atlas from `images.zip`
- unpack a local atlas from `my_atlas.tex + my_atlas.xml`
- pack many PNGs into one atlas `tex+xml`
- resize one icon or a whole icon directory to better fit DST UI or atlas usage
- inspect a known official icon atlas such as `images/inventoryimages1.tex`

## Default Official Source

When the user asks for an official atlas and does not provide a path, use `images.zip`.

Common archive path:

- `...\Don't Starve Together\data\databundles\images.zip`

Useful official entries:

- `images/inventoryimages1.tex`
- `images/inventoryimages1.xml`

Default unpack output:

- `.output/images/`

## Helper Scripts

### `scripts/tex_atlas_tool.py`

Use this when the task is about atlas packing or unpacking.

Current supported workflow:

- unpack official `dxt5` atlases from `images.zip`
- unpack local `argb` or `dxt5` atlases from a `.tex + .xml` pair
- split atlas entries into individual PNG files
- pack multiple PNGs into one atlas PNG + XML + `argb` TEX

Common commands:

```bash
python scripts/tex_atlas_tool.py unpack inventoryimages1
```

```bash
python scripts/tex_atlas_tool.py unpack --tex path/to/my_atlas.tex --xml path/to/my_atlas.xml
```

```bash
python scripts/tex_atlas_tool.py pack path/to/png_dir my_atlas
```

Rules:

- official atlas names are usually read from `images/<name>.tex` and `images/<name>.xml`
- if the user omits an output path, unpack defaults to `.output/images/`
- packing currently writes `argb` TEX in pure Python
- unpacking supports official `dxt5` icon atlases

### `scripts/resize_png.py`

Use this when the task is about resizing one PNG or many PNGs before atlas packing or icon replacement.

Common commands:

```bash
python scripts/resize_png.py path/to/icon.png 64x64
```

```bash
python scripts/resize_png.py path/to/icon_dir 64x64 --mode contain --output .output/resized_icons
```

Supported resize modes:

- `contain`
  - preserve aspect ratio, pad to exact target size
- `cover`
  - preserve aspect ratio, fill target size by cropping
- `stretch`
  - force exact target size
- `fit-width`
  - set width, keep aspect ratio
- `fit-height`
  - set height, keep aspect ratio

Rules:

- use `contain` for most inventory-icon fitting
- use `stretch` only when distortion is acceptable or explicitly desired
- use `cover` when the destination slot shape matters more than preserving the full source bounds

## Intent Index

- "unpack an official atlas"
  - use `python scripts/tex_atlas_tool.py unpack <atlas_name>`
- "unpack a local tex+xml pair"
  - use `python scripts/tex_atlas_tool.py unpack --tex ... --xml ...`
- "pack many PNGs into one atlas"
  - use `python scripts/tex_atlas_tool.py pack <input_dir> <atlas_name>`
- "resize an image to 64x64 or 128x128"
  - use `python scripts/resize_png.py ... <size>`
- "resize many images, then pack them"
  - resize first with `resize_png.py`, then pack with `tex_atlas_tool.py`
- "inspect official inventory textures"
  - unpack `inventoryimages1`

## Rule Of Thumb

- If the task is about asset declaration, read `references/asset-patterns.md`.
- If the task is about texture file generation or extraction, read this page first.
- For official atlas inspection, prefer `images.zip` over ad hoc extracted copies.
