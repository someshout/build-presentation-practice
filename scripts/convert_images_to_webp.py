#!/usr/bin/env python3
"""Convert bundle images-source PNG/JPG files to portable WebP images."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment message
    raise SystemExit("Pillow is required: python -m pip install -r requirements.txt") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_root", type=Path)
    parser.add_argument("--max-width", type=int, default=1600)
    parser.add_argument("--quality", type=int, default=82)
    args = parser.parse_args()
    source = args.bundle_root.resolve() / "images-source"
    output = args.bundle_root.resolve() / "images"
    if not source.is_dir():
        raise SystemExit("missing images-source/ directory")
    count = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        relative = path.relative_to(source).with_suffix(".webp")
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(path) as image:
            image = image.convert("RGB")
            if image.width > args.max_width:
                height = round(image.height * args.max_width / image.width)
                image = image.resize((args.max_width, height), Image.Resampling.LANCZOS)
            image.save(target, "WEBP", quality=args.quality, method=6)
        count += 1
    print(f"OK: converted {count} image(s) into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
