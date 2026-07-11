#!/usr/bin/env python3
"""Create or update the three-file EchoStory Secret Gist via git push."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

FILES = ("seeds_bundle.json", "presentation_manifest.json", "presentation-assets.zip")


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def create_secret_gist(token: str, seeds: Path, manifest: Path) -> str:
    payload = json.dumps({
        "description": "EchoStory presentation corpus",
        "public": False,
        "files": {
            seeds.name: {"content": seeds.read_text(encoding="utf-8")},
            manifest.name: {"content": manifest.read_text(encoding="utf-8")},
        },
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/gists",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "build-presentation-practice",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))["id"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.bundle_root.resolve()
    output = args.output_dir.resolve()
    config_path = (args.config or root / ".presentation-practice.local.json").resolve()
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    gist_id = str(config.get("gist_id", "")).strip()
    for filename in FILES:
        if not (output / filename).is_file():
            raise SystemExit(f"missing upload file: {output / filename}")
    if args.dry_run:
        print(f"OK: dry-run validated three upload files; existing_gist={bool(gist_id)}")
        return 0
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    if not gist_id:
        gist_id = create_secret_gist(token, output / FILES[0], output / FILES[1])
        config_path.write_text(json.dumps({"gist_id": gist_id}, indent=2), encoding="utf-8")

    encoded = urllib.parse.quote(token, safe="")
    remote = f"https://x-access-token:{encoded}@gist.github.com/{gist_id}.git"
    with tempfile.TemporaryDirectory(prefix="presentation-gist-") as temp:
        checkout = Path(temp) / "gist"
        run("git", "clone", remote, str(checkout))
        for filename in FILES:
            shutil.copy2(output / filename, checkout / filename)
        run("git", "config", "user.name", "EchoStory Publisher", cwd=checkout)
        run("git", "config", "user.email", "publisher@echostory.local", cwd=checkout)
        run("git", "add", "--", *FILES, cwd=checkout)
        status = subprocess.run(
            ("git", "status", "--porcelain"), cwd=checkout, check=True,
            stdout=subprocess.PIPE, text=True
        ).stdout
        if status.strip():
            run("git", "commit", "-m", "update presentation practice bundle", cwd=checkout)
            run("git", "push", "origin", "HEAD", cwd=checkout)
    print(f"OK: published Secret Gist {gist_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
