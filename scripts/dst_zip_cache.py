#!/usr/bin/env python3
"""
Short-lived cache helpers for DST zip inspection tools.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_ROOT = REPO_ROOT / ".tmp" / "zip_cache"
DEFAULT_INDEX_TTL_SECONDS = 300
DEFAULT_TEXT_TTL_SECONDS = 180
DEFAULT_MAX_TEXT_ENTRIES = 64


def _read_int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(0, parsed)


def get_cache_root() -> Path:
    env_value = os.environ.get("DST_ZIP_CACHE_DIR")
    if env_value:
        return Path(env_value).expanduser()
    return DEFAULT_CACHE_ROOT


def get_index_ttl_seconds() -> int:
    return _read_int_env("DST_ZIP_INDEX_CACHE_TTL_SECONDS", DEFAULT_INDEX_TTL_SECONDS)


def get_text_ttl_seconds() -> int:
    return _read_int_env("DST_ZIP_TEXT_CACHE_TTL_SECONDS", DEFAULT_TEXT_TTL_SECONDS)


def get_max_text_entries() -> int:
    return _read_int_env("DST_ZIP_MAX_TEXT_CACHE_ENTRIES", DEFAULT_MAX_TEXT_ENTRIES)


def _zip_fingerprint(zip_path: Path) -> dict[str, Any]:
    stat = zip_path.stat()
    return {
        "zip_path": str(zip_path.resolve()),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _fingerprint_hash(fingerprint: dict[str, Any]) -> str:
    encoded = json.dumps(fingerprint, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _now() -> int:
    return int(time.time())


class ZipContextCache:
    def __init__(self, zip_path: Path):
        self.zip_path = zip_path.resolve()
        self.fingerprint = _zip_fingerprint(self.zip_path)
        self.fingerprint_hash = _fingerprint_hash(self.fingerprint)
        self.root = get_cache_root()
        self.archive_root = self.root / self.fingerprint_hash
        self.index_path = self.archive_root / "index.json"
        self.text_root = self.archive_root / "text"
        self.index_ttl_seconds = get_index_ttl_seconds()
        self.text_ttl_seconds = get_text_ttl_seconds()
        self.max_text_entries = get_max_text_entries()

    def _is_fresh(self, created_at: int, ttl_seconds: int) -> bool:
        if ttl_seconds <= 0:
            return False
        return _now() - created_at <= ttl_seconds

    def _safe_entry_key(self, entry_name: str) -> str:
        return hashlib.sha256(entry_name.encode("utf-8")).hexdigest()

    def _read_json(self, path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
            newline="\n",
        )

    def _purge_stale_archives(self) -> None:
        if not self.root.exists():
            return

        now = _now()
        archive_ttl = max(self.index_ttl_seconds, self.text_ttl_seconds, 1)
        for child in self.root.iterdir():
            if not child.is_dir():
                continue
            if child.name == self.fingerprint_hash:
                continue
            try:
                if now - int(child.stat().st_mtime) > archive_ttl * 2:
                    for nested in sorted(child.rglob("*"), reverse=True):
                        if nested.is_file():
                            nested.unlink(missing_ok=True)
                        elif nested.is_dir():
                            nested.rmdir()
                    child.rmdir()
            except OSError:
                continue

    def load_entry_names(self) -> list[str] | None:
        payload = self._read_json(self.index_path)
        if payload is None:
            return None
        if payload.get("fingerprint") != self.fingerprint:
            return None
        created_at = int(payload.get("created_at", 0))
        if not self._is_fresh(created_at, self.index_ttl_seconds):
            return None
        entries = payload.get("entries")
        if not isinstance(entries, list):
            return None
        if not all(isinstance(entry, str) for entry in entries):
            return None
        return entries

    def store_entry_names(self, entries: list[str]) -> None:
        self._purge_stale_archives()
        payload = {
            "created_at": _now(),
            "fingerprint": self.fingerprint,
            "entries": entries,
        }
        self._write_json(self.index_path, payload)

    def load_text_lines(self, entry_name: str) -> list[str] | None:
        key = self._safe_entry_key(entry_name)
        payload = self._read_json(self.text_root / f"{key}.json")
        if payload is None:
            return None
        if payload.get("fingerprint") != self.fingerprint:
            return None
        if payload.get("entry_name") != entry_name:
            return None
        created_at = int(payload.get("created_at", 0))
        if not self._is_fresh(created_at, self.text_ttl_seconds):
            return None
        lines = payload.get("lines")
        if not isinstance(lines, list):
            return None
        if not all(isinstance(line, str) for line in lines):
            return None
        return lines

    def store_text_lines(self, entry_name: str, lines: list[str]) -> None:
        self._purge_stale_archives()
        self.text_root.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": _now(),
            "entry_name": entry_name,
            "fingerprint": self.fingerprint,
            "lines": lines,
        }
        path = self.text_root / f"{self._safe_entry_key(entry_name)}.json"
        self._write_json(path, payload)
        self._trim_text_cache()

    def _trim_text_cache(self) -> None:
        if self.max_text_entries <= 0 or not self.text_root.exists():
            return
        files = [path for path in self.text_root.glob("*.json") if path.is_file()]
        if len(files) <= self.max_text_entries:
            return
        files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        for stale in files[self.max_text_entries :]:
            stale.unlink(missing_ok=True)
