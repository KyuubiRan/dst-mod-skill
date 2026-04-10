#!/usr/bin/env python3
"""
Pack and unpack DST atlas TEX/XML pairs.

This script is intentionally self-contained for atlas layout and KTEX handling.
It does not require Don't Starve Mod Tools at runtime.

Requirements:
- Pillow for PNG read and write

Supported today:
- unpack official/local `argb` and `dxt5` KTEX files
- split atlas entries by XML coordinates
- pack multiple PNGs into one atlas PNG + XML + uncompressed `argb` KTEX
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import sys
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

KTEX_MAGIC = b"KTEX"
FORMAT_ARGB = "argb"
FORMAT_DXT5 = "dxt5"
FORMAT_CODES_WRITE = {
    FORMAT_ARGB: 0xFFFC6240,
}
FORMAT_CODES_READ = {
    0xFFFC6240: FORMAT_ARGB,
    0xFFFD8240: FORMAT_ARGB,
    0xFFFC6220: FORMAT_DXT5,
    0xFFFD8220: FORMAT_DXT5,
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
        default=Path("output") / "images",
        help="Output root directory. Defaults to ./output/images",
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
        default=Path("output") / "images",
        help="Output directory. Defaults to ./output/images",
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
        choices=[FORMAT_ARGB],
        default=FORMAT_ARGB,
        help="Pure Python packing currently supports argb only.",
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


def normalize_official_entry(source: str, suffix: str) -> str:
    entry = source.replace("\\", "/")
    if entry.endswith(suffix):
        if "/" in entry:
            return entry
        return f"images/{entry}"
    if "/" in entry:
        return f"{entry}{suffix}"
    return f"images/{entry}{suffix}"


def parse_ktex_header(data: bytes) -> KTexHeader:
    if len(data) < 18 or data[:4] != KTEX_MAGIC:
        raise ValueError("Not a valid KTEX file.")

    format_code = struct.unpack_from("<I", data, 4)[0]
    format_name = FORMAT_CODES_READ.get(format_code)
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
        y1 = round(v1 * atlas_height - 0.5)
        y2 = round(v2 * atlas_height - 0.5)

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


def build_atlas_xml(
    atlas_name: str, placements: list[Placement], atlas_size: int, padding: int
) -> bytes:
    root = ET.Element("Atlas")
    texture = ET.SubElement(root, "Texture")
    texture.set("filename", f"{atlas_name}.tex")
    elements_node = ET.SubElement(root, "Elements")

    for placement in sorted(placements, key=lambda item: item.packed.name.lower()):
        inner_x = placement.x + padding
        inner_y = placement.y + padding
        width, height = placement.packed.image.size

        element = ET.SubElement(elements_node, "Element")
        element.set("name", placement.packed.name)
        element.set("u1", repr((inner_x + 0.5) / atlas_size))
        element.set("u2", repr((inner_x + width - 0.5) / atlas_size))
        element.set("v1", repr((inner_y + 0.5) / atlas_size))
        element.set("v2", repr((inner_y + height - 0.5) / atlas_size))

    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def load_pngs(input_dir: Path) -> list[PackedImage]:
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    packed_images: list[PackedImage] = []
    for path in sorted(input_dir.glob("*.png")):
        image = Image.open(path).convert("RGBA")
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


def try_pack_square(
    images: list[PackedImage], atlas_size: int, padding: int
) -> list[Placement] | None:
    placements: list[Placement] = []
    x = 0
    y = 0
    row_height = 0

    for packed in images:
        width, height = packed.image.size
        cell_width = width + 2 * padding
        cell_height = height + 2 * padding

        if cell_width > atlas_size or cell_height > atlas_size:
            return None

        if x + cell_width > atlas_size:
            x = 0
            y += row_height
            row_height = 0

        if y + cell_height > atlas_size:
            return None

        placements.append(Placement(packed=packed, x=x, y=y))
        x += cell_width
        row_height = max(row_height, cell_height)

    return placements


def pack_images(
    images: list[PackedImage], max_size: int, padding: int
) -> tuple[int, list[Placement]]:
    if max_size < 1 or max_size & (max_size - 1) != 0:
        raise ValueError("--max-size must be a positive power of two.")

    images_sorted = sorted(
        images,
        key=lambda packed: (
            -packed.image.size[1],
            -packed.image.size[0],
            packed.name.lower(),
        ),
    )

    largest = max(
        max(image.image.size[0], image.image.size[1]) + 2 * padding
        for image in images_sorted
    )
    size = next_power_of_two(largest)
    while size <= max_size:
        placements = try_pack_square(images_sorted, size, padding)
        if placements is not None:
            return size, placements
        size *= 2

    raise ValueError(f"Could not fit atlas into a {max_size}x{max_size} texture.")


def paste_with_padding(dst: Image.Image, src: Image.Image, x: int, y: int, padding: int) -> None:
    width, height = src.size
    inner_x = x + padding
    inner_y = y + padding

    dst.paste(src, (inner_x, inner_y))

    if padding <= 0:
        return

    top = src.crop((0, 0, width, 1))
    bottom = src.crop((0, height - 1, width, height))
    left = src.crop((0, 0, 1, height))
    right = src.crop((width - 1, 0, width, height))
    corner_tl = src.crop((0, 0, 1, 1))
    corner_tr = src.crop((width - 1, 0, width, 1))
    corner_bl = src.crop((0, height - 1, 1, height))
    corner_br = src.crop((width - 1, height - 1, width, height))

    for step in range(padding):
        dst.paste(top, (inner_x, inner_y - step - 1))
        dst.paste(bottom, (inner_x, inner_y + height + step))
        dst.paste(left, (inner_x - step - 1, inner_y))
        dst.paste(right, (inner_x + width + step, inner_y))

    for dx in range(padding):
        for dy in range(padding):
            dst.paste(corner_tl, (inner_x - dx - 1, inner_y - dy - 1))
            dst.paste(corner_tr, (inner_x + width + dx, inner_y - dy - 1))
            dst.paste(corner_bl, (inner_x - dx - 1, inner_y + height + dy))
            dst.paste(corner_br, (inner_x + width + dx, inner_y + height + dy))


def build_argb_ktex(image: Image.Image) -> bytes:
    rgba = image.convert("RGBA")
    mip_images = [rgba]
    current = rgba
    while current.size != (1, 1):
        next_width = max(1, current.size[0] // 2)
        next_height = max(1, current.size[1] // 2)
        current = current.resize((next_width, next_height), Image.Resampling.BOX)
        mip_images.append(current)

    header = bytearray()
    header.extend(KTEX_MAGIC)
    header.extend(struct.pack("<I", FORMAT_CODES_WRITE[FORMAT_ARGB]))

    payload = bytearray()
    for mip in mip_images:
        width, height = mip.size
        flipped = mip.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        raw = flipped.tobytes("raw", "RGBA")
        header.extend(struct.pack("<HHHI", width, height, width * 4, len(raw)))
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
    print(f"size: {atlas_image.width}x{atlas_image.height}")
    print(f"elements: {len(elements)}")
    print(f"atlas_png: {atlas_png_path}")
    print(f"atlas_xml: {atlas_xml_path}")
    print(f"split_dir: {split_dir}")
    return 0


def command_pack(args: argparse.Namespace) -> int:
    images = load_pngs(args.input_dir)
    atlas_size, placements = pack_images(images, args.max_size, args.padding)

    atlas_image = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))
    for placement in placements:
        paste_with_padding(
            atlas_image,
            placement.packed.image,
            placement.x,
            placement.y,
            args.padding,
        )

    output_dir = ensure_dir(args.output)
    atlas_png_path = output_dir / f"{args.atlas_name}.png"
    atlas_xml_path = output_dir / f"{args.atlas_name}.xml"
    atlas_tex_path = output_dir / f"{args.atlas_name}.tex"

    atlas_image.save(atlas_png_path)
    atlas_xml_path.write_bytes(
        build_atlas_xml(args.atlas_name, placements, atlas_size, args.padding)
    )
    atlas_tex_path.write_bytes(build_argb_ktex(atlas_image))

    print(f"atlas: {args.atlas_name}")
    print(f"format: {args.format}")
    print(f"size: {atlas_size}x{atlas_size}")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
