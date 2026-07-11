#!/usr/bin/env python3
"""Validate portable presentation corpus paths and Click image references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath


VISUAL_RE = re.compile(r"<!--\s*visual:\s*(.+?)\s*-->")
CLICK_RE = re.compile(r"^####\s+Click\s+(\d+)\s*$", re.MULTILINE)
DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")


def portable_relative(value: str) -> bool:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return not (
        DRIVE_RE.match(value)
        or normalized.startswith("/")
        or "://" in normalized
        or ".." in path.parts
    )


def validate(bundle_root: Path) -> list[str]:
    errors: list[str] = []
    corpus_root = bundle_root / "corpus"
    if not corpus_root.is_dir():
        return ["missing corpus/ directory"]

    markdown_files = sorted(corpus_root.rglob("*.md"))
    if not markdown_files:
        return ["corpus/ contains no Markdown files"]

    visual_count = 0
    for markdown in markdown_files:
        text = markdown.read_text(encoding="utf-8")
        clicks = [int(value) for value in CLICK_RE.findall(text)]
        if clicks and clicks[0] != 0:
            errors.append(f"{markdown.relative_to(bundle_root)}: Click sequence must start at 0")
        for previous, current in zip(clicks, clicks[1:]):
            if current not in (0, previous + 1):
                errors.append(
                    f"{markdown.relative_to(bundle_root)}: non-contiguous Click {previous} -> {current}"
                )

        visuals = VISUAL_RE.findall(text)
        visual_count += len(visuals)
        if clicks and len(visuals) != len(clicks):
            errors.append(
                f"{markdown.relative_to(bundle_root)}: {len(clicks)} Click blocks but {len(visuals)} visual refs"
            )
        for value in visuals:
            if value.strip().lower() == "none":
                continue
            if not portable_relative(value):
                errors.append(f"{markdown.relative_to(bundle_root)}: non-portable visual path: {value}")
                continue
            target = (bundle_root / Path(*PurePosixPath(value).parts)).resolve()
            try:
                target.relative_to(bundle_root)
            except ValueError:
                errors.append(f"{markdown.relative_to(bundle_root)}: visual escapes bundle: {value}")
                continue
            if not target.is_file():
                errors.append(f"{markdown.relative_to(bundle_root)}: missing visual: {value}")
            elif target.suffix.lower() != ".webp":
                errors.append(f"{markdown.relative_to(bundle_root)}: visual must be .webp: {value}")
            else:
                header = target.read_bytes()[:12]
                if len(header) < 12 or header[:4] != b"RIFF" or header[8:12] != b"WEBP":
                    errors.append(f"{markdown.relative_to(bundle_root)}: invalid WebP file: {value}")

    if visual_count == 0:
        errors.append("no visual references found")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_root", type=Path)
    args = parser.parse_args()
    root = args.bundle_root.resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: portable presentation bundle validated: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
