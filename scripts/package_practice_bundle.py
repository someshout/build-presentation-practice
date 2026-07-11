#!/usr/bin/env python3
"""Create presentation-assets.zip and presentation_manifest.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_root", type=Path)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--version")
    args = parser.parse_args()
    root = args.bundle_root.resolve()
    images = root / "images"
    if not images.is_dir():
        raise SystemExit("missing images/ directory")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    zip_path = output / "presentation-assets.zip"
    files = sorted(path for path in images.rglob("*.webp") if path.is_file())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
    data = zip_path.read_bytes()
    manifest = {
        "schema_version": 1,
        "version": args.version or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "filename": zip_path.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "files": [path.relative_to(root).as_posix() for path in files],
    }
    (output / "presentation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OK: packaged {len(files)} image(s) into {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
