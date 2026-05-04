#!/usr/bin/env python3
"""
Decompile DST animation zips/directories into a Spriter SCML project.

This is a small Python implementation of the practical `anim.bin` + `build.bin`
to SCML workflow. It is intended for inspection and editable recovery, not as a
guarantee of perfect round-tripping: Spriter cannot represent every transform
used by Klei's native animation format.
"""

from __future__ import annotations

import argparse
import math
import shutil
import struct
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO
from xml.etree import ElementTree as ET

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError as exc:  # pragma: no cover - dependency message
    raise SystemExit("Pillow is required. Install it with: python -m pip install pillow") from exc

try:
    from tex_atlas_tool import decode_ktex_mip0
except ImportError as exc:  # pragma: no cover - script should live beside tex_atlas_tool.py
    raise SystemExit("Could not import tex_atlas_tool.py from the scripts directory.") from exc


FACING_SUFFIXES = {
    1 << 0: "_right",
    1 << 1: "_up",
    1 << 2: "_left",
    1 << 3: "_down",
    1 << 4: "_upright",
    1 << 5: "_upleft",
    1 << 6: "_downright",
    1 << 7: "_downleft",
    (1 << 0) | (1 << 2): "_side",
    (1 << 4) | (1 << 5): "_upside",
    (1 << 6) | (1 << 7): "_downside",
    (1 << 4) | (1 << 5) | (1 << 6) | (1 << 7): "_45s",
    (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3): "_90s",
}


class FormatError(ValueError):
    pass


class BinaryReader:
    def __init__(self, fp: BinaryIO, source: str):
        self.fp = fp
        self.source = source
        self.endian = "<"

    def tell(self) -> int:
        return self.fp.tell()

    def read_exact(self, size: int) -> bytes:
        data = self.fp.read(size)
        if len(data) != size:
            raise FormatError(f"{self.source}: unexpected EOF at offset {self.tell()}")
        return data

    def read_magic_and_version(self, magic: bytes) -> int:
        actual = self.read_exact(4)
        if actual != magic:
            raise FormatError(f"{self.source}: expected {magic!r}, got {actual!r}")

        raw = self.read_exact(4)
        version_le = struct.unpack("<i", raw)[0]
        if version_le & 0xFFFF:
            self.endian = "<"
            return version_le

        self.endian = ">"
        return struct.unpack(">i", raw)[0]

    def u8(self) -> int:
        return self.read_exact(1)[0]

    def u32(self) -> int:
        return struct.unpack(self.endian + "I", self.read_exact(4))[0]

    def f32(self) -> float:
        return struct.unpack(self.endian + "f", self.read_exact(4))[0]

    def string(self) -> str:
        length = self.u32()
        data = self.read_exact(length)
        return data.decode("utf-8", errors="replace")

    def at_eof(self) -> bool:
        current = self.fp.tell()
        data = self.fp.read(1)
        self.fp.seek(current)
        return data == b""


@dataclass
class BBox:
    x: float
    y: float
    w: float
    h: float

    @property
    def int_w(self) -> int:
        return max(1, int(round(self.w)))

    @property
    def int_h(self) -> int:
        return max(1, int(round(self.h)))


@dataclass
class BuildFrame:
    frame_number: int
    duration: int
    bbox: BBox
    alpha_count: int
    uv_triangles: list[list[tuple[float, float, float]]] = field(default_factory=list)
    atlas_depth: int = 0
    atlas_bbox: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)

    def atlas_index(self, sampler_offset: int) -> int:
        return self.atlas_depth - sampler_offset


@dataclass
class BuildSymbol:
    hash: int
    frames: list[BuildFrame]
    name: str = ""

    def frame_index_for(self, frame_number: int) -> int:
        selected = 0
        for idx, frame in enumerate(self.frames):
            if frame.frame_number <= frame_number:
                selected = idx
            else:
                break
        return selected


@dataclass
class Build:
    name: str
    atlases: list[str]
    symbols: dict[int, BuildSymbol]

    def sampler_offset(self) -> int:
        depths = [frame.atlas_depth for symbol in self.symbols.values() for frame in symbol.frames]
        return min(depths) if depths else 0


@dataclass
class AnimElement:
    hash: int
    build_frame: int
    layer_hash: int
    matrix: tuple[float, float, float, float, float, float]
    z: float
    name: str = ""
    layer_name: str = ""


@dataclass
class AnimFrame:
    bbox: BBox
    events: dict[int, str]
    elements: list[AnimElement]


@dataclass
class Anim:
    name: str
    facing: int
    bank_hash: int
    frame_rate: float
    frames: list[AnimFrame]
    bank_name: str = ""

    @property
    def full_name(self) -> str:
        return self.name + FACING_SUFFIXES.get(self.facing, "")

    @property
    def frame_duration(self) -> float:
        return 1.0 / self.frame_rate if self.frame_rate else 0.0

    @property
    def duration(self) -> float:
        return len(self.frames) * self.frame_duration


def parse_build(data: bytes, source: str) -> Build:
    reader = BinaryReader(fp=memoryview_to_file(data), source=source)
    version = reader.read_magic_and_version(b"BILD")
    if not 5 <= version <= 6:
        raise FormatError(f"{source}: unsupported build version {version}")

    symbol_count = reader.u32()
    _frame_count = reader.u32()
    build_name = reader.string()

    atlas_count = reader.u32()
    if atlas_count == 0:
        raise FormatError(f"{source}: build has no atlases")
    atlases = [reader.string() for _ in range(atlas_count)]

    symbols: dict[int, BuildSymbol] = {}
    for _ in range(symbol_count):
        symbol_hash = reader.u32()
        frames: list[BuildFrame] = []
        frame_count = reader.u32()
        for _ in range(frame_count):
            frame_number = reader.u32()
            duration = reader.u32()
            bbox = BBox(reader.f32(), reader.f32(), reader.f32(), reader.f32())
            _alpha_index = reader.u32()
            alpha_count = reader.u32()
            if alpha_count % 6 != 0:
                raise FormatError(f"{source}: corrupt build frame vertex count {alpha_count}")
            frames.append(BuildFrame(frame_number, duration, bbox, alpha_count))
        symbols[symbol_hash] = BuildSymbol(symbol_hash, frames)

    expected_vertices = sum(frame.alpha_count for symbol in symbols.values() for frame in symbol.frames)
    stored_vertices = reader.u32()
    if expected_vertices != stored_vertices:
        raise FormatError(
            f"{source}: vertex count mismatch, header={stored_vertices}, parsed={expected_vertices}"
        )

    for symbol_hash in sorted(symbols):
        for frame in symbols[symbol_hash].frames:
            uv_points: list[tuple[float, float, float]] = []
            triangle_count = frame.alpha_count // 3
            for _ in range(triangle_count):
                triangle: list[tuple[float, float, float]] = []
                for _ in range(3):
                    _x = reader.f32()
                    _y = reader.f32()
                    _z = reader.f32()
                    u = reader.f32()
                    v = reader.f32()
                    w = reader.f32()
                    triangle.append((u, v, w))
                    uv_points.append((u, v, w))
                frame.uv_triangles.append(triangle)

            if uv_points:
                us = [point[0] for point in uv_points]
                # Build UVs use texture space with V measured from the bottom.
                # decode_ktex_mip0 returns a normal top-left-origin image.
                vs = [1.0 - point[1] for point in uv_points]
                ws = [point[2] for point in uv_points]
                min_u = max(0.0, min(us))
                max_u = min(1.0, max(us))
                min_v = max(0.0, min(vs))
                max_v = min(1.0, max(vs))
                frame.atlas_bbox = (min_u, min_v, max_u, max_v)
                frame.atlas_depth = int(math.floor(sum(ws) / len(ws) + 0.5))

    if version >= 6 and not reader.at_eof():
        hash_count = reader.u32()
        for _ in range(hash_count):
            symbol_hash = reader.u32()
            name = reader.string()
            if symbol_hash in symbols:
                symbols[symbol_hash].name = name

    for symbol_hash, symbol in symbols.items():
        if not symbol.name:
            symbol.name = f"symbol_{symbol_hash:x}"

    return Build(build_name, atlases, symbols)


def parse_anim(data: bytes, source: str) -> list[Anim]:
    reader = BinaryReader(fp=memoryview_to_file(data), source=source)
    version = reader.read_magic_and_version(b"ANIM")
    if not 3 <= version <= 4:
        raise FormatError(f"{source}: unsupported anim version {version}")

    expected_elements = reader.u32()
    expected_frames = reader.u32()
    expected_events = reader.u32()
    anim_count = reader.u32()

    anims: list[Anim] = []
    for _ in range(anim_count):
        name = reader.string()
        facing = reader.u8()
        bank_hash = reader.u32()
        frame_rate = reader.f32()
        frame_count = reader.u32()
        frames: list[AnimFrame] = []
        for _ in range(frame_count):
            bbox = BBox(reader.f32(), reader.f32(), reader.f32(), reader.f32())
            event_count = reader.u32()
            events = {reader.u32(): "" for _ in range(event_count)}
            element_count = reader.u32()
            elements: list[AnimElement] = []
            for _ in range(element_count):
                element_hash = reader.u32()
                build_frame = reader.u32()
                layer_hash = reader.u32()
                matrix = (
                    reader.f32(),
                    reader.f32(),
                    reader.f32(),
                    reader.f32(),
                    reader.f32(),
                    reader.f32(),
                )
                z = reader.f32()
                elements.append(AnimElement(element_hash, build_frame, layer_hash, matrix, z))
            frames.append(AnimFrame(bbox, events, elements))
        anims.append(Anim(name, facing, bank_hash, frame_rate, frames))

    if sum(len(frame.elements) for anim in anims for frame in anim.frames) != expected_elements:
        raise FormatError(f"{source}: element count mismatch")
    if sum(len(anim.frames) for anim in anims) != expected_frames:
        raise FormatError(f"{source}: frame count mismatch")
    if sum(len(frame.events) for anim in anims for frame in anim.frames) != expected_events:
        raise FormatError(f"{source}: event count mismatch")

    names: dict[int, str] = {}
    if version >= 4 and not reader.at_eof():
        hash_count = reader.u32()
        for _ in range(hash_count):
            name_hash = reader.u32()
            names[name_hash] = reader.string()

    for anim in anims:
        anim.bank_name = names.get(anim.bank_hash, f"bank_{anim.bank_hash:02x}")
        for frame in anim.frames:
            for event_hash in list(frame.events):
                frame.events[event_hash] = names.get(event_hash, f"event_{event_hash:02x}")
            for element in frame.elements:
                element.name = names.get(element.hash, f"element_{element.hash:02x}")
                element.layer_name = names.get(element.layer_hash, f"layer_{element.layer_hash:02x}")

    return anims


def memoryview_to_file(data: bytes) -> BinaryIO:
    from io import BytesIO

    return BytesIO(data)


def fmt(value: float | int | str) -> str:
    if isinstance(value, float):
        if math.isfinite(value):
            text = f"{value:.6f}".rstrip("0").rstrip(".")
            return text if text else "0"
        return str(value)
    return str(value)


def tomilli(seconds: float) -> int:
    return int(math.ceil(1000.0 * seconds))


def decompose_matrix(matrix: tuple[float, float, float, float, float, float], last: dict[str, float]) -> tuple[float, float, float, int]:
    a, b, c, d, _tx, _ty = matrix
    scale_x = math.sqrt(a * a + b * b)
    scale_y = math.sqrt(c * c + d * d)
    det = a * d - c * b
    is_first = bool(last.get("is_first", True))

    if det < 0:
        if is_first or last["scale_x"] <= last["scale_y"]:
            scale_x = -scale_x
            is_first = False
        else:
            scale_y = -scale_y

    if abs(scale_x) < 1e-3 or abs(scale_y) < 1e-3:
        angle = last["angle"]
    else:
        sin_approx = 0.5 * (c / scale_y - b / scale_x)
        cos_approx = 0.5 * (a / scale_x + d / scale_y)
        angle = math.atan2(sin_approx, cos_approx)

    spin = 1 if abs(angle - last["angle"]) <= math.pi else -1
    if angle < last["angle"]:
        spin = -spin

    last["scale_x"] = scale_x
    last["scale_y"] = scale_y
    last["angle"] = angle
    last["is_first"] = is_first
    return scale_x, scale_y, angle, spin


@dataclass
class FileMeta:
    folder_id: int
    file_id: int
    pivot_x: float
    pivot_y: float


@dataclass
class TimelineState:
    timeline: ET.Element
    timeline_id: int
    name: str
    frames: list[tuple[int, AnimElement]]
    is_dupe: bool = False

    @property
    def last_time(self) -> int:
        return self.frames[-1][0]


def export_scml(build: Build, anims: list[Anim], output_dir: Path) -> Path:
    root = ET.Element(
        "spriter_data",
        {
            "scml_version": "1.0",
            "generator": "DST anim_scml_tool.py",
            "generator_version": "1",
        },
    )

    file_meta: dict[tuple[int, int], FileMeta] = {}
    folder_id = 0
    for symbol_hash in sorted(build.symbols):
        symbol = build.symbols[symbol_hash]
        folder = ET.SubElement(root, "folder", {"id": str(folder_id), "name": symbol.name})
        for file_id, frame in enumerate(symbol.frames):
            width = frame.bbox.int_w
            height = frame.bbox.int_h
            pivot_x = 0.5 - frame.bbox.x / width
            pivot_y = 0.5 + frame.bbox.y / height
            filename = f"{symbol.name}/{symbol.name}-{frame.frame_number}.png"
            ET.SubElement(
                folder,
                "file",
                {
                    "id": str(file_id),
                    "name": filename,
                    "width": str(width),
                    "height": str(height),
                    "pivot_x": fmt(pivot_x),
                    "pivot_y": fmt(pivot_y),
                },
            )
            file_meta[(symbol_hash, file_id)] = FileMeta(folder_id, file_id, pivot_x, pivot_y)
        folder_id += 1

    banks: dict[int, list[Anim]] = {}
    bank_names: dict[int, str] = {}
    for anim in anims:
        banks.setdefault(anim.bank_hash, []).append(anim)
        bank_names[anim.bank_hash] = anim.bank_name

    for entity_id, bank_hash in enumerate(sorted(banks)):
        entity = ET.SubElement(root, "entity", {"id": str(entity_id), "name": bank_names[bank_hash]})
        for animation_id, anim in enumerate(sorted(banks[bank_hash], key=lambda item: item.full_name)):
            export_animation(entity, animation_id, build, file_meta, anim)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t")
    scml_path = output_dir / f"{build.name}.scml"
    tree.write(scml_path, encoding="utf-8", xml_declaration=True)
    return scml_path


def export_animation(
    entity: ET.Element,
    animation_id: int,
    build: Build,
    file_meta: dict[tuple[int, int], FileMeta],
    anim: Anim,
) -> None:
    animation = ET.SubElement(
        entity,
        "animation",
        {"id": str(animation_id), "name": anim.full_name, "length": str(tomilli(anim.duration))},
    )
    mainline = ET.SubElement(animation, "mainline")

    timeline_id = 0
    key_id = 0
    running_time = 0.0
    timeline_by_hash: dict[int, list[TimelineState]] = {}
    first_by_hash: dict[int, TimelineState] = {}
    seen_hash_count: dict[int, int] = {}

    frames_to_write = list(anim.frames)
    if frames_to_write:
        frames_to_write.append(anim.frames[-1])

    for frame in frames_to_write:
        start_time = tomilli(running_time)
        running_time += anim.frame_duration
        main_key = ET.SubElement(mainline, "key", {"id": str(key_id), "time": str(start_time)})
        sorted_elements = sorted(frame.elements, key=lambda element: element.z)
        z_index = len(sorted_elements)
        object_ref_id = 0

        for element in sorted_elements:
            symbol = build.symbols.get(element.hash)
            if symbol is None:
                continue
            symbol_frame_idx = symbol.frame_index_for(element.build_frame)
            meta = file_meta.get((element.hash, symbol_frame_idx))
            if meta is None:
                continue

            timelines = timeline_by_hash.setdefault(element.hash, [])
            state = next((item for item in timelines if item.last_time < start_time), None)
            if state is None:
                dupe_count = seen_hash_count.get(element.hash, 0)
                timeline_name = element.name
                if dupe_count == 1 and element.hash in first_by_hash:
                    first = first_by_hash[element.hash]
                    first.is_dupe = True
                    first.timeline.set("name", f"{first.name}_0")
                if dupe_count > 0:
                    timeline_name = f"{timeline_name}_{dupe_count}"

                timeline = ET.SubElement(animation, "timeline", {"id": str(timeline_id), "name": timeline_name})
                state = TimelineState(timeline, timeline_id, element.name, [])
                timelines.append(state)
                if dupe_count == 0:
                    first_by_hash[element.hash] = state
                seen_hash_count[element.hash] = dupe_count + 1
                timeline_id += 1

            state.frames.append((start_time, element))
            object_key = len(state.frames) - 1

            ET.SubElement(
                main_key,
                "object_ref",
                {
                    "id": str(object_ref_id),
                    "name": element.name,
                    "abs_x": "0",
                    "abs_y": "0",
                    "abs_pivot_x": fmt(meta.pivot_x),
                    "abs_pivot_y": fmt(meta.pivot_y),
                    "abs_angle": "0",
                    "abs_scale_x": "1",
                    "abs_scale_y": "1",
                    "abs_a": "1",
                    "timeline": str(state.timeline_id),
                    "key": str(object_key),
                    "z_index": str(z_index),
                },
            )
            object_ref_id += 1
            z_index -= 1
            state.frames[-1] = (start_time, element)

        key_id += 1

    for states in timeline_by_hash.values():
        for state in states:
            export_timeline_keys(build, file_meta, state)


def export_timeline_keys(
    build: Build,
    file_meta: dict[tuple[int, int], FileMeta],
    state: TimelineState,
) -> None:
    last = {"scale_x": 1.0, "scale_y": 1.0, "angle": 0.0, "is_first": True}
    for key_id, (start_time, element) in enumerate(state.frames):
        symbol = build.symbols[element.hash]
        symbol_frame_idx = symbol.frame_index_for(element.build_frame)
        meta = file_meta[(element.hash, symbol_frame_idx)]
        scale_x, scale_y, angle_rad, spin = decompose_matrix(element.matrix, last)
        angle = angle_rad
        if angle < 0:
            angle += 2 * math.pi
        angle_deg = angle * 180.0 / math.pi
        _a, _b, _c, _d, tx, ty = element.matrix

        timeline_key = ET.SubElement(
            state.timeline,
            "key",
            {"id": str(key_id), "time": str(start_time), "spin": str(spin)},
        )
        ET.SubElement(
            timeline_key,
            "object",
            {
                "folder": str(meta.folder_id),
                "file": str(meta.file_id),
                "x": fmt(tx),
                "y": fmt(-ty),
                "scale_x": fmt(scale_x),
                "scale_y": fmt(scale_y),
                "angle": fmt(angle_deg),
            },
        )


def resolve_atlas_entry(entries: dict[str, bytes], atlas_name: str, index: int) -> tuple[str, bytes] | None:
    candidates = []
    normalized = atlas_name.replace("\\", "/")
    candidates.append(normalized)
    if not normalized.lower().endswith(".tex"):
        candidates.append(normalized + ".tex")
    candidates.append(f"atlas-{index}.tex")

    lower_entries = {name.lower(): name for name in entries}
    for candidate in candidates:
        match = lower_entries.get(candidate.lower())
        if match is not None:
            return match, entries[match]
    return None


def export_symbol_images(build: Build, entries: dict[str, bytes], output_dir: Path) -> int:
    atlas_images: list[Image.Image] = []
    for idx, atlas_name in enumerate(build.atlases):
        resolved = resolve_atlas_entry(entries, atlas_name, idx)
        if resolved is None:
            raise FormatError(f"Could not find atlas texture for build atlas {atlas_name!r}")
        _entry_name, tex_data = resolved
        _header, image = decode_ktex_mip0(tex_data)
        atlas_images.append(image.convert("RGBA"))

    sampler_offset = build.sampler_offset()
    count = 0
    for symbol in build.symbols.values():
        symbol_dir = output_dir / symbol.name
        symbol_dir.mkdir(parents=True, exist_ok=True)
        for frame in symbol.frames:
            atlas_index = frame.atlas_index(sampler_offset)
            if atlas_index < 0 or atlas_index >= len(atlas_images):
                raise FormatError(
                    f"Symbol {symbol.name} frame {frame.frame_number} requests atlas index {atlas_index}"
                )
            frame_image = crop_symbol_frame(atlas_images[atlas_index], frame)
            frame_image.save(symbol_dir / f"{symbol.name}-{frame.frame_number}.png")
            count += 1
    return count


def crop_symbol_frame(atlas: Image.Image, frame: BuildFrame) -> Image.Image:
    width, height = atlas.size
    min_u, min_v, max_u, max_v = frame.atlas_bbox
    left = max(0, min(width - 1, int(math.floor(width * min_u))))
    upper = max(0, min(height - 1, int(math.floor(height * min_v))))
    right = max(left + 1, min(width, int(math.floor(width * max_u + 0.5))))
    lower = max(upper + 1, min(height, int(math.floor(height * max_v + 0.5))))

    crop = atlas.crop((left, upper, right, lower))
    mask = Image.new("L", crop.size, 0)
    draw = ImageDraw.Draw(mask)
    for triangle in frame.uv_triangles:
        points = [((u - min_u) * width, ((1.0 - v) - min_v) * height) for u, v, _w in triangle]
        draw.polygon(points, fill=255)

    result = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    result.alpha_composite(crop)
    alpha = ImageChops.multiply(crop.getchannel("A"), mask)
    result.putalpha(alpha)
    return result.resize((frame.bbox.int_w, frame.bbox.int_h), Image.Resampling.LANCZOS)


def load_entries(input_path: Path) -> dict[str, bytes]:
    if input_path.is_dir():
        entries: dict[str, bytes] = {}
        for path in input_path.rglob("*"):
            if path.is_file():
                entries[path.relative_to(input_path).as_posix()] = path.read_bytes()
        return entries

    if zipfile.is_zipfile(input_path):
        with zipfile.ZipFile(input_path) as zf:
            return {info.filename: zf.read(info) for info in zf.infolist() if not info.is_dir()}

    raise SystemExit(f"Input must be a DST anim zip or directory: {input_path}")


def find_required_entry(entries: dict[str, bytes], name: str) -> tuple[str, bytes]:
    lower_entries = {entry.lower(): entry for entry in entries}
    match = lower_entries.get(name.lower())
    if match is None:
        if name.lower() == "anim.bin":
            raise FormatError(
                "Missing required entry: anim.bin. This looks like a build-only animation zip; "
                "choose a compiled animation zip that contains both build.bin and anim.bin."
            )
        raise FormatError(f"Missing required entry: {name}")
    return match, entries[match]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decompile one DST anim zip or extracted anim directory to Spriter SCML."
    )
    parser.add_argument("input", type=Path, help="Animation .zip or directory containing build.bin and anim.bin.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to .tmp/.output/<input_stem>_scml.",
    )
    parser.add_argument("--bank", action="append", default=[], help="Keep only the named animation bank.")
    parser.add_argument("--rename-build", default=None, help="Rename the SCML/build root name.")
    parser.add_argument("--rename-bank", default=None, help="Rename all animation banks to this name.")
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Write SCML only and skip extracting symbol PNGs from atlas textures.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete the output directory before writing it.",
    )
    argv = sys.argv[1:]
    if argv and argv[0] == "decompile":
        argv = argv[1:]
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir is not None
        else (Path(".tmp") / ".output" / f"{input_path.stem}_scml").resolve()
    )

    if args.force and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = load_entries(input_path)
    build_entry_name, build_data = find_required_entry(entries, "build.bin")
    anim_entry_name, anim_data = find_required_entry(entries, "anim.bin")

    build = parse_build(build_data, build_entry_name)
    if args.rename_build:
        build.name = args.rename_build

    anims = parse_anim(anim_data, anim_entry_name)
    if args.bank:
        allowed = set(args.bank)
        anims = [anim for anim in anims if anim.bank_name in allowed]
    if args.rename_bank:
        for anim in anims:
            anim.bank_name = args.rename_bank

    image_count = 0
    if not args.no_images:
        image_count = export_symbol_images(build, entries, output_dir)
    scml_path = export_scml(build, anims, output_dir)

    print(f"input: {input_path}")
    print(f"output_dir: {output_dir}")
    print(f"scml: {scml_path}")
    print(f"symbols: {len(build.symbols)}")
    print(f"animations: {len(anims)}")
    print(f"images: {image_count}")
    print("warning: SCML is an approximate editable recovery format; DST-native shears may lose fidelity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
