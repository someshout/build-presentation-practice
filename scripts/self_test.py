#!/usr/bin/env python3
"""Run portable Skill fixtures without network or secrets."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*args: str) -> None:
    subprocess.run((sys.executable, *args), check=True)


def main() -> int:
    scripts = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="presentation-skill-test-") as temp:
        root = Path(temp) / "portable-bundle"
        (root / "corpus").mkdir(parents=True)
        (root / "images" / "demo").mkdir(parents=True)
        (root / "images" / "demo" / "s01-00.webp").write_bytes(
            b"RIFF\x04\x00\x00\x00WEBP"
        )
        (root / "corpus" / "demo.md").write_text(
            """---
input: Demo
---
### S01｜Demo
#### Click 0
<!-- visual: images/demo/s01-00.webp -->

| EN | 中文 |
| --- | --- |
| Hello. | 哈囉。 |
""",
            encoding="utf-8",
        )
        output = root / "output"
        run(str(scripts / "validate_practice_bundle.py"), str(root))
        run(str(scripts / "build_presentation_seeds.py"), str(root))
        run(str(scripts / "package_practice_bundle.py"), str(root), str(output),
            "--version", "test-v1")
        config = root / ".presentation-practice.local.json"
        config.write_text(json.dumps({"gist_id": "secret123"}), encoding="utf-8")
        run(str(scripts / "publish_secret_gist.py"), str(root),
            "--output-dir", str(output), "--config", str(config), "--dry-run")
    print("OK: Skill self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
