#!/usr/bin/env python3
"""
Pack and unpack DST atlas TEX/XML pairs.

This script is intentionally self-contained for atlas layout and KTEX handling.
It does not require Don't Starve Mod Tools at runtime.

Requirements:
- Pillow for PNG read and write

Supported today:
- unpack official/local 2D `argb` and `dxt5` KTEX files whose format code encodes mip count
- split atlas entries by XML coordinates
- pack multiple PNGs into one atlas PNG + XML + `argb` or `dxt5` KTEX
- prefer Klei `TextureConverter.exe` when local Don't Starve Mod Tools are installed
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import subprocess
import sys
import tempfile
from collections import deque
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install Pillow"
    ) from exc


DEFAULT_IMAGES_ZIP_PATHS = [
    Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\images.zip"
    ),
    Path(
        r"D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\images.zip"
    ),
    Path.home()
    / ".local"
    / "share"
    / "Steam"
    / "steamapps"
    / "common"
    / "Don't Starve Together"
    / "data"
    / "databundles"
    / "images.zip",
    Path.home()
    / "Library"
    / "Application Support"
    / "Steam"
    / "steamapps"
    / "common"
    / "Don't Starve Together"
    / "data"
    / "databundles"
    / "images.zip",
]

DEFAULT_TEXTURE_CONVERTER_PATHS = [
    Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools\mod_tools\tools\bin\TextureConverter.exe"
    ),
    Path(
        r"D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools\mod_tools\tools\bin\TextureConverter.exe"
    ),
]

KTEX_MAGIC = b"KTEX"
FORMAT_ARGB = "argb"
FORMAT_DXT5 = "dxt5"

# Post-caves KTEX headers encode more than just the pixel format.
# The low bits describe the texture kind, while the mip count lives in bits 13:17.
KTEX_PLATFORM_SHIFT = 0
KTEX_PLATFORM_MASK = 0xF
KTEX_PIXEL_FORMAT_SHIFT = 4
KTEX_PIXEL_FORMAT_MASK = 0x1F
KTEX_TEXTURE_TYPE_SHIFT = 9
KTEX_TEXTURE_TYPE_MASK = 0xF
KTEX_MIP_COUNT_SHIFT = 13
KTEX_MIP_COUNT_MASK = 0x1F
KTEX_FLAGS_SHIFT = 18
KTEX_FLAGS_MASK = 0x3
KTEX_PADDING_MASK = 0xFFF00000
KTEX_TEXTURE_TYPE_2D = 1
KTEX_FLAGS_DEFAULT = 0x3
KTEX_PADDING_DEFAULT = 0xFFF00000

KTEX_PIXEL_FORMATS_READ = {
    2: FORMAT_DXT5,
    4: FORMAT_ARGB,
}
KTEX_PIXEL_FORMATS_WRITE = {
    FORMAT_DXT5: 2,
    FORMAT_ARGB: 4,
}


@dataclass(frozen=True)
class KTexMip:
    width: int
    height: int
    pitch: int
    size: int


@dataclass(frozen=True)
class KTexHeader:
    format_code: int
    format_name: str
    declared_mip_count: int
    mips: list[KTexMip]
    data_offset: int


@dataclass(frozen=True)
class AtlasElement:
    name: str
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class PackedImage:
    source: Path
    name: str
    image: Image.Image


@dataclass(frozen=True)
class Placement:
    packed: PackedImage
    x: int
    y: int


@dataclass(frozen=True)
class BBox:
    x: int
    y: int
    w: int
    h: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pack and unpack DST TEX/XML atlases.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    unpack_parser = subparsers.add_parser(
        "unpack",
        help="Unpack an official atlas from images.zip or a local TEX/XML pair.",
    )
    unpack_parser.add_argument(
        "source",
        nargs="?",
        default="inventoryimages1",
        help=(
            "Official atlas base name such as inventoryimages1. "
            "Ignored when --tex and --xml are both provided."
        ),
    )
    unpack_parser.add_argument(
        "--images-zip",
        type=Path,
        default=None,
        help="Path to official images.zip. Defaults to DST_IMAGES_ZIP or common install paths.",
    )
    unpack_parser.add_argument("--tex", type=Path, default=None, help="Local .tex path.")
    unpack_parser.add_argument("--xml", type=Path, default=None, help="Local .xml path.")
    unpack_parser.add_argument(
        "--tex-entry",
        default=None,
        help="Archive entry for .tex. Defaults to images/<source>.tex",
    )
    unpack_parser.add_argument(
        "--xml-entry",
        default=None,
        help="Archive entry for .xml. Defaults to images/<source>.xml",
    )
    unpack_parser.add_argument(
        "--output",
        type=Path,
        default=Path(".tmp") / ".output" / "images",
        help="Output root directory. Defaults to ./.tmp/.output/images",
    )

    pack_parser = subparsers.add_parser(
        "pack",
        help="Pack multiple PNGs into one atlas PNG + XML + TEX.",
    )
    pack_parser.add_argument("input_dir", type=Path, help="Directory containing PNG files.")
    pack_parser.add_argument("atlas_name", help="Output atlas base name without extension.")
    pack_parser.add_argument(
        "--output",
        type=Path,
        default=Path(".tmp") / ".output" / "images",
        help="Output directory. Defaults to ./.tmp/.output/images",
    )
    pack_parser.add_argument(
        "--max-size",
        type=int,
        default=2048,
        help="Maximum power-of-two atlas size. Defaults to 2048.",
    )
    pack_parser.add_argument(
        "--padding",
        type=int,
        default=1,
        help="Padding around each sprite, duplicated from edge pixels. Defaults to 1.",
    )
    pack_parser.add_argument(
        "--format",
        choices=[FORMAT_ARGB, FORMAT_DXT5],
        default=FORMAT_ARGB,
        help="KTEX output format. Pure Python packing supports argb and dxt5.",
    )
    pack_parser.add_argument(
        "--single-mip",
        action="store_true",
        help="Write only mip0. Useful for UI textures that are scaled in-game.",
    )
    pack_parser.add_argument(
        "--texture-converter",
        type=Path,
        default=None,
        help=(
            "Path to Klei TextureConverter.exe. "
            "If omitted, common Don't Starve Mod Tools locations are tried first."
        ),
    )
    pack_parser.add_argument(
        "--pure-python",
        action="store_true",
        help="Force the fallback pure-Python KTEX writer instead of TextureConverter.exe.",
    )

    return parser.parse_args()


def resolve_images_zip(candidate: Path | None) -> Path:
    env_value = os.environ.get("DST_IMAGES_ZIP")
    if candidate is not None:
        candidate = candidate.expanduser()
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"images.zip not found at {candidate}")

    if env_value:
        path = Path(env_value).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(
            f"images.zip not found at {path}. Fix DST_IMAGES_ZIP or pass --images-zip."
        )

    for path in DEFAULT_IMAGES_ZIP_PATHS:
        expanded = path.expanduser()
        if expanded.is_file():
            return expanded

    tried = "\n".join(f"- {path.expanduser()}" for path in DEFAULT_IMAGES_ZIP_PATHS)
    raise FileNotFoundError(
        "images.zip not found in common locations. Pass --images-zip or set DST_IMAGES_ZIP.\n"
        f"Tried:\n{tried}"
    )


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_texture_converter(candidate: Path | None) -> Path | None:
    if candidate is not None:
        candidate = candidate.expanduser()
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"TextureConverter.exe not found at {candidate}")

    env_value = os.environ.get("DST_TEXTURE_CONVERTER")
    if env_value:
        path = Path(env_value).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(
            f"TextureConverter.exe not found at {path}. Fix DST_TEXTURE_CONVERTER or pass --texture-converter."
        )

    for path in DEFAULT_TEXTURE_CONVERTER_PATHS:
        expanded = path.expanduser()
        if expanded.is_file():
            return expanded

    return None


def normalize_official_entry(source: str, suffix: str) -> str:
    entry = source.replace("\\", "/")
    if entry.endswith(suffix):
        if "/" in entry:
            return entry
        return f"images/{entry}"
    if "/" in entry:
        return f"{entry}{suffix}"
    return f"images/{entry}{suffix}"


def parse_format_code(format_code: int) -> tuple[str | None, int]:
    pixel_format = (format_code >> KTEX_PIXEL_FORMAT_SHIFT) & KTEX_PIXEL_FORMAT_MASK
    texture_type = (format_code >> KTEX_TEXTURE_TYPE_SHIFT) & KTEX_TEXTURE_TYPE_MASK
    mip_count = (format_code >> KTEX_MIP_COUNT_SHIFT) & KTEX_MIP_COUNT_MASK

    if texture_type != KTEX_TEXTURE_TYPE_2D:
        return None, mip_count

    return KTEX_PIXEL_FORMATS_READ.get(pixel_format), mip_count


def build_format_code(format_name: str, mip_count: int) -> int:
    pixel_format = KTEX_PIXEL_FORMATS_WRITE[format_name]
    if mip_count < 1 or mip_count > KTEX_MIP_COUNT_MASK:
        raise ValueError(f"Unsupported mip count for KTEX header: {mip_count}")

    return (
        KTEX_PADDING_DEFAULT
        | (KTEX_FLAGS_DEFAULT << KTEX_FLAGS_SHIFT)
        | (mip_count << KTEX_MIP_COUNT_SHIFT)
        | (KTEX_TEXTURE_TYPE_2D << KTEX_TEXTURE_TYPE_SHIFT)
        | (pixel_format << KTEX_PIXEL_FORMAT_SHIFT)
    )


def parse_ktex_header(data: bytes) -> KTexHeader:
    if len(data) < 18 or data[:4] != KTEX_MAGIC:
        raise ValueError("Not a valid KTEX file.")

    format_code = struct.unpack_from("<I", data, 4)[0]
    format_name, declared_mip_count = parse_format_code(format_code)
    if format_name is None:
        raise ValueError(f"Unsupported KTEX format code: 0x{format_code:08X}")

    mips: list[KTexMip] = []
    for mip_count in range(1, 32):
        offset = 8 + (mip_count - 1) * 10
        if offset + 10 > len(data):
            break
        width, height, pitch, size = struct.unpack_from("<HHHI", data, offset)
        mips.append(KTexMip(width, height, pitch, size))
        header_size = 8 + mip_count * 10
        payload_size = sum(mip.size for mip in mips)
        if header_size + payload_size == len(data):
            return KTexHeader(
                format_code=format_code,
                format_name=format_name,
                declared_mip_count=declared_mip_count,
                mips=mips[:],
                data_offset=header_size,
            )
        if header_size + payload_size > len(data):
            break

    raise ValueError("Could not determine KTEX mip layout.")


def decode_rgb565(value: int) -> tuple[int, int, int]:
    r = ((value >> 11) & 0x1F) * 255 // 31
    g = ((value >> 5) & 0x3F) * 255 // 63
    b = (value & 0x1F) * 255 // 31
    return r, g, b


def decode_dxt5_image(data: bytes, width: int, height: int) -> Image.Image:
    block_width = math.ceil(width / 4)
    block_height = math.ceil(height / 4)
    expected_size = block_width * block_height * 16
    if len(data) != expected_size:
        raise ValueError(
            f"Unexpected DXT5 mip size: got {len(data)}, expected {expected_size}"
        )

    pixels = [(0, 0, 0, 0)] * (width * height)
    offset = 0

    for block_y in range(block_height):
        for block_x in range(block_width):
            block = data[offset : offset + 16]
            offset += 16

            alpha0 = block[0]
            alpha1 = block[1]
            alpha_bits = int.from_bytes(block[2:8], "little")
            alpha_table = [alpha0, alpha1]
            if alpha0 > alpha1:
                for step in range(1, 7):
                    alpha_table.append(
                        ((7 - step) * alpha0 + step * alpha1) // 7
                    )
            else:
                for step in range(1, 5):
                    alpha_table.append(
                        ((5 - step) * alpha0 + step * alpha1) // 5
                    )
                alpha_table.extend([0, 255])

            color0 = struct.unpack_from("<H", block, 8)[0]
            color1 = struct.unpack_from("<H", block, 10)[0]
            c0 = decode_rgb565(color0)
            c1 = decode_rgb565(color1)
            color_table = [
                c0,
                c1,
                tuple((2 * c0[i] + c1[i]) // 3 for i in range(3)),
                tuple((c0[i] + 2 * c1[i]) // 3 for i in range(3)),
            ]
            color_bits = int.from_bytes(block[12:16], "little")

            for pixel_index in range(16):
                px = pixel_index % 4
                py = pixel_index // 4
                x = block_x * 4 + px
                y = block_y * 4 + py
                if x >= width or y >= height:
                    continue

                alpha_index = (alpha_bits >> (3 * pixel_index)) & 0x7
                color_index = (color_bits >> (2 * pixel_index)) & 0x3
                r, g, b = color_table[color_index]
                a = alpha_table[alpha_index]
                pixels[y * width + x] = (r, g, b, a)

    image = Image.new("RGBA", (width, height))
    image.putdata(pixels)
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def decode_argb_image(data: bytes, width: int, height: int) -> Image.Image:
    expected_size = width * height * 4
    if len(data) != expected_size:
        raise ValueError(
            f"Unexpected argb mip size: got {len(data)}, expected {expected_size}"
        )
    image = Image.frombytes("RGBA", (width, height), data)
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def decode_ktex_mip0(data: bytes) -> tuple[KTexHeader, Image.Image]:
    header = parse_ktex_header(data)
    mip0 = header.mips[0]
    mip0_data = data[header.data_offset : header.data_offset + mip0.size]

    if header.format_name == FORMAT_ARGB:
        image = decode_argb_image(mip0_data, mip0.width, mip0.height)
    elif header.format_name == FORMAT_DXT5:
        image = decode_dxt5_image(mip0_data, mip0.width, mip0.height)
    else:
        raise ValueError(f"Unsupported decode format: {header.format_name}")

    return header, image


def read_atlas_xml(xml_bytes: bytes, atlas_width: int, atlas_height: int) -> list[AtlasElement]:
    root = ET.fromstring(xml_bytes)
    elements_parent = root.find("Elements")
    if elements_parent is None:
        raise ValueError("Atlas XML is missing the Elements node.")

    elements: list[AtlasElement] = []
    for element in elements_parent.findall("Element"):
        name = element.attrib["name"]
        u1 = float(element.attrib["u1"])
        u2 = float(element.attrib["u2"])
        v1 = float(element.attrib["v1"])
        v2 = float(element.attrib["v2"])

        x1 = round(u1 * atlas_width - 0.5)
        x2 = round(u2 * atlas_width - 0.5)
        # DST atlas XML stores V coordinates in bottom-left texture space.
        # Convert them back into top-left image coordinates before cropping.
        y1 = round((1 - v2) * atlas_height - 0.5)
        y2 = round((1 - v1) * atlas_height - 0.5)

        elements.append(
            AtlasElement(
                name=name,
                x=x1,
                y=y1,
                width=x2 - x1 + 1,
                height=y2 - y1 + 1,
            )
        )

    return elements


def clamp(lower: float, upper: float, value: float) -> float:
    return max(lower, min(upper, value))


def build_atlas_xml(
    atlas_name: str,
    placements: list[Placement],
    atlas_width: int,
    atlas_height: int,
    padding: int,
) -> bytes:
    root = ET.Element("Atlas")
    texture = ET.SubElement(root, "Texture")
    texture.set("filename", f"{atlas_name}.tex")
    elements_node = ET.SubElement(root, "Elements")

    offset_amount = padding + 0.5
    offset_amount_x = offset_amount / atlas_width
    offset_amount_y = offset_amount / atlas_height

    for placement in sorted(placements, key=lambda item: item.packed.name.lower()):
        bbox = BBox(
            x=placement.x,
            y=placement.y,
            w=placement.packed.image.size[0],
            h=placement.packed.image.size[1],
        )

        element = ET.SubElement(elements_node, "Element")
        element.set("name", placement.packed.name)
        u1 = clamp(0.0, 1.0, bbox.x / float(atlas_width) + offset_amount_x)
        v1 = clamp(0.0, 1.0, 1.0 - (bbox.y + bbox.h) / float(atlas_height) + offset_amount_y)
        u2 = clamp(0.0, 1.0, (bbox.x + bbox.w) / float(atlas_width) - offset_amount_x)
        v2 = clamp(0.0, 1.0, 1.0 - bbox.y / float(atlas_height) - offset_amount_y)

        element.set("u1", repr(u1))
        element.set("v1", repr(v1))
        element.set("u2", repr(u2))
        element.set("v2", repr(v2))

    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def build_mip_images(image: Image.Image) -> list[Image.Image]:
    rgba = image.convert("RGBA")
    mip_images = [rgba]
    current = rgba
    while current.size != (1, 1):
        next_width = max(1, current.size[0] // 2)
        next_height = max(1, current.size[1] // 2)
        current = current.resize((next_width, next_height), Image.Resampling.BOX)
        mip_images.append(current)
    return mip_images


def build_ktex_with_converter(
    mip_images: list[Image.Image],
    dest_filename: Path,
    format_name: str,
    converter_path: Path,
) -> None:
    converter_format = {
        FORMAT_ARGB: "argb",
        FORMAT_DXT5: "bc3",
    }[format_name]

    with tempfile.TemporaryDirectory(prefix="dst_tex_atlas_") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        mip_paths: list[str] = []
        for index, mip in enumerate(mip_images):
            mip_path = temp_dir / f"mip{index}.png"
            mip.save(mip_path)
            mip_paths.append(str(mip_path))

        command = [
            str(converter_path),
            "--swizzle",
            "--format",
            converter_format,
            "--platform",
            "opengl",
            "-i",
            ";".join(mip_paths),
            "-o",
            str(dest_filename),
            "--premultiply",
        ]
        if len(mip_images) > 1:
            command.append("--mipmap")

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "TextureConverter.exe failed with exit code "
                f"{result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def bleed_transparent_pixels(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()

    queue: deque[tuple[int, int]] = deque()
    visited = [[False] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if pixels[x, y][3] != 0:
                visited[y][x] = True
                queue.append((x, y))

    if not queue or len(queue) == width * height:
        return rgba

    while queue:
        x, y = queue.popleft()
        r, g, b, _ = pixels[x, y]

        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= width or ny >= height or visited[ny][nx]:
                continue

            nr, ng, nb, na = pixels[nx, ny]
            if na == 0:
                pixels[nx, ny] = (r, g, b, 0)
                visited[ny][nx] = True
                queue.append((nx, ny))

    return rgba


def expand_with_border(image: Image.Image, border_size: int) -> Image.Image:
    rgba = image.convert("RGBA")
    if border_size <= 0:
        return rgba

    expanded = Image.new(
        "RGBA",
        (rgba.size[0] + border_size * 2, rgba.size[1] + border_size * 2),
        (0, 0, 0, 0),
    )
    expanded.paste(rgba, (border_size, border_size))

    for index in range(border_size):
        left = border_size - index
        right = border_size + rgba.size[0] + index
        top = border_size - index
        bottom = border_size + rgba.size[1] + index - 1

        top_line = expanded.crop((left, top, right, top + 1))
        bottom_line = expanded.crop((left, bottom, right, bottom + 1))
        expanded.paste(top_line, (left, top - 1, right, top))
        expanded.paste(bottom_line, (left, bottom + 1, right, bottom + 2))

        left_line = expanded.crop((left, top - 1, left + 1, bottom + 2))
        right_line = expanded.crop((right - 1, top - 1, right, bottom + 2))
        expanded.paste(left_line, (left - 1, top - 1, left, bottom + 2))
        expanded.paste(right_line, (right, top - 1, right + 1, bottom + 2))

    return expanded


def load_pngs(input_dir: Path, padding: int) -> list[PackedImage]:
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    packed_images: list[PackedImage] = []
    for path in sorted(input_dir.glob("*.png")):
        image = expand_with_border(bleed_transparent_pixels(Image.open(path)), padding)
        packed_images.append(
            PackedImage(source=path, name=f"{path.stem}.tex", image=image)
        )

    if not packed_images:
        raise FileNotFoundError(f"No PNG files found in {input_dir}")

    return packed_images


def next_power_of_two(value: int) -> int:
    if value <= 1:
        return 1
    return 1 << (value - 1).bit_length()


def next_multiple_of(value: int, target: int) -> int:
    mod = value % target
    if mod == 0:
        return value
    return value + (target - mod)


def get_atlas_dimension(images: list[PackedImage], max_texture_size: int) -> int:
    area = sum(image.image.size[0] * image.image.size[1] for image in images)
    maxdim = next_multiple_of(
        max(max(image.image.size[0], image.image.size[1]) for image in images),
        4,
    )
    dimension = max(
        2 ** math.ceil(math.log(math.sqrt(area * 1.25), 2)),
        2 ** math.ceil(math.log(maxdim, 2)),
    )
    return int(min(max_texture_size, dimension))


def bbox_intersects(lhs: BBox, rhs: BBox) -> bool:
    if rhs.x >= lhs.x + lhs.w or rhs.x + rhs.w <= lhs.x:
        return False
    if rhs.y + rhs.h <= lhs.y or rhs.y >= lhs.y + lhs.h:
        return False
    return True


def try_insert_image(width: int, height: int, boxes: list[BBox], atlas_size: int) -> BBox | None:
    align = 4
    x = 0
    y = 0

    while y + height < atlas_size:
        min_y: int | None = None
        y_test_bbox = BBox(0, y, atlas_size, height)
        overlapping = [box for box in boxes if bbox_intersects(box, y_test_bbox)]

        while x + width <= atlas_size:
            test_bbox = BBox(x, y, width, height)
            intersects = False
            for box in overlapping:
                if bbox_intersects(box, test_bbox):
                    x = next_multiple_of(box.x + box.w, align)
                    candidate_y = box.h + box.y
                    min_y = candidate_y if min_y is None else min(min_y, candidate_y)
                    intersects = True
                    break
            if not intersects:
                return test_bbox

        if min_y is not None:
            y = max(next_multiple_of(min_y, align), y + align)
        else:
            y += align
        x = 0

    return None


def pack_images_official(images: list[PackedImage], max_size: int) -> tuple[int, int, list[Placement]]:
    if max_size < 1 or max_size & (max_size - 1) != 0:
        raise ValueError("--max-size must be a positive power of two.")

    images_sorted = sorted(
        images,
        key=lambda packed: packed.image.size[0] * packed.image.size[1],
        reverse=True,
    )
    atlas_size = get_atlas_dimension(images_sorted, max_size)
    placed_boxes: list[BBox] = []
    placements: list[Placement] = []

    for packed in images_sorted:
        width, height = packed.image.size
        if width > atlas_size or height > atlas_size:
            raise ValueError(
                f"Image {packed.source.name} is larger than the atlas size {atlas_size}."
            )
        bbox = try_insert_image(width, height, placed_boxes, atlas_size)
        if bbox is None:
            raise ValueError(
                "Could not fit all PNG files into one atlas with the official packing layout. "
                "Split the atlas, reduce image sizes, or increase --max-size."
            )
        placed_boxes.append(bbox)
        placements.append(Placement(packed=packed, x=bbox.x, y=bbox.y))

    atlas_width = atlas_size
    atlas_height = atlas_size
    max_y = max(placement.y + placement.packed.image.size[1] for placement in placements)
    max_x = max(placement.x + placement.packed.image.size[0] for placement in placements)
    if max_y <= atlas_height // 2:
        atlas_height //= 2
    if max_x <= atlas_width // 2:
        atlas_width //= 2

    return atlas_width, atlas_height, placements


def build_atlas_image(
    atlas_width: int,
    atlas_height: int,
    placements: list[Placement],
) -> Image.Image:
    atlas_image = Image.new("RGBA", (atlas_width, atlas_height))
    for placement in placements:
        atlas_image.paste(placement.packed.image, (placement.x, placement.y))
    return atlas_image


def build_atlas_mips_official(
    atlas_width: int,
    atlas_height: int,
    placements: list[Placement],
) -> list[Image.Image]:
    mips: list[Image.Image] = []
    divisor = 1
    width = atlas_width
    height = atlas_height

    while width >= 1 or height >= 1:
        mip_image = Image.new("RGBA", (width, height))
        for placement in placements:
            src = placement.packed.image
            mip_width = src.size[0] // divisor
            mip_height = src.size[1] // divisor
            if mip_width > 0 and mip_height > 0:
                resized = src.resize((mip_width, mip_height), Image.Resampling.LANCZOS)
                mip_x = placement.x // divisor
                mip_y = placement.y // divisor
                mip_image.paste(resized, (mip_x, mip_y))
        mips.append(mip_image)

        if width == 1 and height == 1:
            break

        divisor <<= 1
        width = max(1, width >> 1)
        height = max(1, height >> 1)

    return mips


def encode_rgb565(color: tuple[int, int, int]) -> int:
    r, g, b = color
    return ((r * 31 + 127) // 255) << 11 | ((g * 63 + 127) // 255) << 5 | ((b * 31 + 127) // 255)


def color_distance_sq(lhs: tuple[int, int, int], rhs: tuple[int, int, int]) -> int:
    return sum((lhs[index] - rhs[index]) ** 2 for index in range(3))


def make_dxt5_alpha_table(alpha0: int, alpha1: int) -> list[int]:
    alpha_table = [alpha0, alpha1]
    if alpha0 > alpha1:
        for step in range(1, 7):
            alpha_table.append(((7 - step) * alpha0 + step * alpha1) // 7)
    else:
        for step in range(1, 5):
            alpha_table.append(((5 - step) * alpha0 + step * alpha1) // 5)
        alpha_table.extend([0, 255])
    return alpha_table


def choose_color_endpoints(block_pixels: list[tuple[int, int, int, int]]) -> tuple[int, int]:
    colors_565 = {encode_rgb565(pixel[:3]) for pixel in block_pixels}
    if not colors_565:
        return 0, 0
    if len(colors_565) == 1:
        value = next(iter(colors_565))
        return value, value

    decoded = [(value, decode_rgb565(value)) for value in colors_565]
    best_pair = (decoded[0][0], decoded[1][0])
    best_distance = -1
    for index, (lhs_raw, lhs_color) in enumerate(decoded):
        for rhs_raw, rhs_color in decoded[index + 1 :]:
            distance = color_distance_sq(lhs_color, rhs_color)
            if distance > best_distance:
                best_distance = distance
                best_pair = (lhs_raw, rhs_raw)

    color0, color1 = best_pair
    if color0 < color1:
        color0, color1 = color1, color0
    return color0, color1


def encode_dxt5_block(block_pixels: list[tuple[int, int, int, int]]) -> bytes:
    alpha_values = [pixel[3] for pixel in block_pixels]
    alpha0 = max(alpha_values)
    alpha1 = min(alpha_values)
    alpha_table = make_dxt5_alpha_table(alpha0, alpha1)
    alpha_bits = 0
    for index, alpha in enumerate(alpha_values):
        best = min(range(8), key=lambda candidate: abs(alpha - alpha_table[candidate]))
        alpha_bits |= best << (3 * index)

    color0, color1 = choose_color_endpoints(block_pixels)
    if color0 == color1:
        palette = [decode_rgb565(color0)] * 4
    else:
        c0 = decode_rgb565(color0)
        c1 = decode_rgb565(color1)
        palette = [
            c0,
            c1,
            tuple((2 * c0[channel] + c1[channel]) // 3 for channel in range(3)),
            tuple((c0[channel] + 2 * c1[channel]) // 3 for channel in range(3)),
        ]

    color_bits = 0
    for index, pixel in enumerate(block_pixels):
        rgb = pixel[:3]
        best = min(range(4), key=lambda candidate: color_distance_sq(rgb, palette[candidate]))
        color_bits |= best << (2 * index)

    return b"".join(
        [
            bytes((alpha0, alpha1)),
            alpha_bits.to_bytes(6, "little"),
            struct.pack("<HH", color0, color1),
            color_bits.to_bytes(4, "little"),
        ]
    )


def encode_dxt5_image(image: Image.Image) -> tuple[int, bytes]:
    width, height = image.size
    block_width = math.ceil(width / 4)
    block_height = math.ceil(height / 4)
    pixels = image.load()

    payload = bytearray()
    for block_y in range(block_height):
        for block_x in range(block_width):
            block_pixels: list[tuple[int, int, int, int]] = []
            for py in range(4):
                for px in range(4):
                    sx = min(block_x * 4 + px, width - 1)
                    sy = min(block_y * 4 + py, height - 1)
                    block_pixels.append(pixels[sx, sy])
            payload.extend(encode_dxt5_block(block_pixels))

    pitch = max(16, block_width * 16)
    return pitch, bytes(payload)


def build_argb_ktex(image: Image.Image, single_mip: bool = False) -> bytes:
    mip_images = [image.convert("RGBA")] if single_mip else build_mip_images(image)

    header = bytearray()
    header.extend(KTEX_MAGIC)
    header.extend(struct.pack("<I", build_format_code(FORMAT_ARGB, len(mip_images))))

    payload = bytearray()
    for mip in mip_images:
        width, height = mip.size
        flipped = mip.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        raw = flipped.tobytes("raw", "RGBA")
        header.extend(struct.pack("<HHHI", width, height, width * 4, len(raw)))
        payload.extend(raw)

    return bytes(header + payload)


def build_dxt5_ktex(image: Image.Image, single_mip: bool = False) -> bytes:
    mip_images = [image.convert("RGBA")] if single_mip else build_mip_images(image)

    header = bytearray()
    header.extend(KTEX_MAGIC)
    header.extend(struct.pack("<I", build_format_code(FORMAT_DXT5, len(mip_images))))

    payload = bytearray()
    for mip in mip_images:
        width, height = mip.size
        flipped = mip.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        pitch, raw = encode_dxt5_image(flipped)
        header.extend(struct.pack("<HHHI", width, height, pitch, len(raw)))
        payload.extend(raw)

    return bytes(header + payload)


def write_unpack_outputs(
    atlas_name: str,
    atlas_image: Image.Image,
    xml_bytes: bytes,
    elements: list[AtlasElement],
    output_root: Path,
) -> tuple[Path, Path, Path]:
    ensure_dir(output_root)

    atlas_png_path = output_root / f"{atlas_name}.png"
    atlas_xml_path = output_root / f"{atlas_name}.xml"
    split_dir = ensure_dir(output_root / atlas_name)

    atlas_image.save(atlas_png_path)
    atlas_xml_path.write_bytes(xml_bytes)

    for element in elements:
        cropped = atlas_image.crop(
            (element.x, element.y, element.x + element.width, element.y + element.height)
        )
        cropped.save(split_dir / f"{Path(element.name).stem}.png")

    return atlas_png_path, atlas_xml_path, split_dir


def command_unpack(args: argparse.Namespace) -> int:
    if (args.tex is None) != (args.xml is None):
        raise ValueError("--tex and --xml must be provided together.")

    if args.tex is not None and args.xml is not None:
        tex_bytes = args.tex.read_bytes()
        xml_bytes = args.xml.read_bytes()
        atlas_name = args.tex.stem
    else:
        images_zip = resolve_images_zip(args.images_zip)
        tex_entry = args.tex_entry or normalize_official_entry(args.source, ".tex")
        xml_entry = args.xml_entry or normalize_official_entry(args.source, ".xml")
        atlas_name = Path(tex_entry).stem
        with zipfile.ZipFile(images_zip) as zf:
            try:
                tex_bytes = zf.read(tex_entry)
            except KeyError as exc:
                raise FileNotFoundError(f"Archive entry not found: {tex_entry}") from exc
            try:
                xml_bytes = zf.read(xml_entry)
            except KeyError as exc:
                raise FileNotFoundError(f"Archive entry not found: {xml_entry}") from exc

    header, atlas_image = decode_ktex_mip0(tex_bytes)
    elements = read_atlas_xml(xml_bytes, atlas_image.width, atlas_image.height)
    atlas_png_path, atlas_xml_path, split_dir = write_unpack_outputs(
        atlas_name=atlas_name,
        atlas_image=atlas_image,
        xml_bytes=xml_bytes,
        elements=elements,
        output_root=args.output,
    )

    print(f"atlas: {atlas_name}")
    print(f"format: {header.format_name} (0x{header.format_code:08X})")
    if header.declared_mip_count != len(header.mips):
        print(
            "warning: format code declares "
            f"{header.declared_mip_count} mips but payload contains {len(header.mips)}",
            file=sys.stderr,
        )
    print(f"size: {atlas_image.width}x{atlas_image.height}")
    print(f"elements: {len(elements)}")
    print(f"atlas_png: {atlas_png_path}")
    print(f"atlas_xml: {atlas_xml_path}")
    print(f"split_dir: {split_dir}")
    return 0


def command_pack(args: argparse.Namespace) -> int:
    images = load_pngs(args.input_dir, args.padding)
    atlas_width, atlas_height, placements = pack_images_official(images, args.max_size)
    atlas_image = build_atlas_image(atlas_width, atlas_height, placements)
    mip_images = [atlas_image] if args.single_mip else build_atlas_mips_official(
        atlas_width,
        atlas_height,
        placements,
    )

    output_dir = ensure_dir(args.output)
    atlas_png_path = output_dir / f"{args.atlas_name}.png"
    atlas_xml_path = output_dir / f"{args.atlas_name}.xml"
    atlas_tex_path = output_dir / f"{args.atlas_name}.tex"

    atlas_image.save(atlas_png_path)
    atlas_xml_path.write_bytes(
        build_atlas_xml(args.atlas_name, placements, atlas_width, atlas_height, args.padding)
    )

    converter_path = None if args.pure_python else resolve_texture_converter(args.texture_converter)
    if converter_path is not None:
        build_ktex_with_converter(
            mip_images=mip_images,
            dest_filename=atlas_tex_path,
            format_name=args.format,
            converter_path=converter_path,
        )
        writer_label = f"TextureConverter ({converter_path})"
    elif args.format == FORMAT_ARGB:
        atlas_tex_path.write_bytes(build_argb_ktex(atlas_image, single_mip=args.single_mip))
        writer_label = "pure-python fallback"
        if not args.pure_python:
            print(
                "warning: TextureConverter.exe not found. "
                "For best compatibility, install Don't Starve Mod Tools (Steam App ID 245850).",
                file=sys.stderr,
            )
    elif args.format == FORMAT_DXT5:
        atlas_tex_path.write_bytes(build_dxt5_ktex(atlas_image, single_mip=args.single_mip))
        writer_label = "pure-python fallback"
        if not args.pure_python:
            print(
                "warning: TextureConverter.exe not found. "
                "For best compatibility, install Don't Starve Mod Tools (Steam App ID 245850).",
                file=sys.stderr,
            )
    else:
        raise ValueError(f"Unsupported pack format: {args.format}")

    print(f"atlas: {args.atlas_name}")
    print(f"format: {args.format}")
    print(f"writer: {writer_label}")
    print(f"size: {atlas_width}x{atlas_height}")
    print(f"sprites: {len(placements)}")
    print(f"atlas_png: {atlas_png_path}")
    print(f"atlas_xml: {atlas_xml_path}")
    print(f"atlas_tex: {atlas_tex_path}")
    return 0


def main() -> int:
    args = parse_args()
    try:
        if args.command == "unpack":
            return command_unpack(args)
        if args.command == "pack":
            return command_pack(args)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
