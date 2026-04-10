#!/usr/bin/env python3
"""
Resize one PNG or a whole directory of PNGs for DST mod texture workflows.

Requirements:
- Pillow
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install Pillow"
    ) from exc


RESAMPLE_MAP = {
    "nearest": Image.Resampling.NEAREST,
    "bilinear": Image.Resampling.BILINEAR,
    "bicubic": Image.Resampling.BICUBIC,
    "lanczos": Image.Resampling.LANCZOS,
}


def parse_size(value: str) -> tuple[int, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Size must look like WIDTHxHEIGHT, for example 64x64.")
    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Width and height must be integers.") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Width and height must be positive.")
    return width, height


def parse_color(value: str) -> tuple[int, int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) == 6:
        raw += "FF"
    if len(raw) != 8:
        raise argparse.ArgumentTypeError("Color must be RRGGBB or RRGGBBAA.")
    try:
        return tuple(int(raw[i : i + 2], 16) for i in range(0, 8, 2))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Invalid hex color.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resize one PNG or a directory of PNGs.")
    parser.add_argument("input", type=Path, help="Input PNG file or directory.")
    parser.add_argument("size", type=parse_size, help="Target size, for example 64x64.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output file or directory. "
            "Defaults to ./.output/resized_pngs for directory input, "
            "or <stem>_<width>x<height>.png next to the source file."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["contain", "cover", "stretch", "fit-width", "fit-height"],
        default="contain",
        help="Resize mode. Defaults to contain.",
    )
    parser.add_argument(
        "--background",
        type=parse_color,
        default=(0, 0, 0, 0),
        help="Background color for contain mode, as RRGGBB or RRGGBBAA. Defaults to transparent.",
    )
    parser.add_argument(
        "--resample",
        choices=sorted(RESAMPLE_MAP),
        default="lanczos",
        help="Resampling filter. Defaults to lanczos.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def iter_pngs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".png":
            raise FileNotFoundError(f"Input file is not a PNG: {input_path}")
        return [input_path]
    if input_path.is_dir():
        files = sorted(path for path in input_path.glob("*.png") if path.is_file())
        if not files:
            raise FileNotFoundError(f"No PNG files found in {input_path}")
        return files
    raise FileNotFoundError(f"Input path not found: {input_path}")


def resize_image(
    image: Image.Image,
    size: tuple[int, int],
    mode: str,
    background: tuple[int, int, int, int],
    resample: Image.Resampling,
) -> Image.Image:
    src = image.convert("RGBA")
    target_width, target_height = size

    if mode == "stretch":
        return src.resize(size, resample)

    if mode == "contain":
        canvas = Image.new("RGBA", size, background)
        contained = ImageOps.contain(src, size, method=resample)
        offset = (
            (target_width - contained.width) // 2,
            (target_height - contained.height) // 2,
        )
        canvas.paste(contained, offset, contained)
        return canvas

    if mode == "cover":
        return ImageOps.fit(src, size, method=resample, centering=(0.5, 0.5))

    if mode == "fit-width":
        new_height = max(1, round(src.height * target_width / src.width))
        return src.resize((target_width, new_height), resample)

    if mode == "fit-height":
        new_width = max(1, round(src.width * target_height / src.height))
        return src.resize((new_width, target_height), resample)

    raise ValueError(f"Unsupported mode: {mode}")


def output_path_for_file(source: Path, output: Path | None, size: tuple[int, int]) -> Path:
    if output is not None:
        return output
    width, height = size
    return source.with_name(f"{source.stem}_{width}x{height}.png")


def output_dir_for_batch(output: Path | None) -> Path:
    if output is not None:
        return ensure_dir(output)
    return ensure_dir(Path(".output") / "resized_pngs")


def main() -> int:
    args = parse_args()
    resample = RESAMPLE_MAP[args.resample]

    try:
        pngs = iter_pngs(args.input)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.input.is_file():
        source = pngs[0]
        output_path = output_path_for_file(source, args.output, args.size)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        image = Image.open(source)
        resized = resize_image(
            image=image,
            size=args.size,
            mode=args.mode,
            background=args.background,
            resample=resample,
        )
        resized.save(output_path)
        print(output_path)
        return 0

    output_dir = output_dir_for_batch(args.output)
    for source in pngs:
        image = Image.open(source)
        resized = resize_image(
            image=image,
            size=args.size,
            mode=args.mode,
            background=args.background,
            resample=resample,
        )
        resized.save(output_dir / source.name)

    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
