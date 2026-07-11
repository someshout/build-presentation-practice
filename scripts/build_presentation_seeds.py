#!/usr/bin/env python3
"""Build EchoStory array-format seeds from presentation Click corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SLIDE_RE = re.compile(r"^###\s+(.+)$")
CLICK_RE = re.compile(r"^####\s+Click\s+(\d+)\s*$")
VISUAL_RE = re.compile(r"<!--\s*visual:\s*(.+?)\s*-->")


def slug(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", value).strip("-")
    return value.lower() or "presentation"


def parse_table(lines: list[str]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"EN", "---"} or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append((cells[0], cells[1]))
    return rows


def file_topic(markdown: Path) -> str | None:
    for line in markdown.read_text(encoding="utf-8").splitlines()[:20]:
        if line.startswith("input:"):
            value = line.split(":", 1)[1].strip().strip("'\"")
            if value:
                return value
    return None


def bundle_topic(files: list[Path]) -> str:
    """One shared topic for every corpus file in the bundle, so multi-file
    decks still collapse into a single EchoStory folder instead of one
    folder per file. Uses the first file's `input:` frontmatter, or its
    stem if absent."""
    for markdown in files:
        topic = file_topic(markdown)
        if topic:
            return topic
    return files[0].stem if files else "presentation"


def build(markdown: Path, topic: str) -> list[dict]:
    lines = markdown.read_text(encoding="utf-8").splitlines()
    stories: list[dict] = []
    slide_title: str | None = None
    click_index: int | None = None
    visual = ""
    click_lines: list[str] = []
    sentences: list[dict] = []
    steps: list[dict] = []

    def flush_click() -> None:
        nonlocal click_lines, visual
        if click_index is None:
            click_lines = []
            return
        indexes: list[int] = []
        for en, zh in parse_table(click_lines):
            index = len(sentences)
            indexes.append(index)
            sentences.append({"index": index, "text_en": en, "text_zh": zh})
        if indexes:
            steps.append({"index": click_index, "visual_ref": visual, "sentence_indexes": indexes})
        click_lines = []
        visual = ""

    def flush_slide() -> None:
        nonlocal sentences, steps
        flush_click()
        if slide_title and sentences:
            stable = hashlib.sha1(f"{topic}|{slide_title}".encode("utf-8")).hexdigest()[:10]
            stories.append({
                "id": f"{slug(topic)}_speech_{stable}",
                "title": f"{topic} — 演講：{slide_title}",
                "category": "情境",
                "topic": topic,
                "material_type": "演講",
                "tags": ["technical-presentation", "public-speaking"],
                "status": "generated",
                "generated_en": " ".join(item["text_en"] for item in sentences),
                "presentation_steps": steps,
                "sentences": sentences,
            })
        sentences = []
        steps = []

    for line in lines:
        slide = SLIDE_RE.match(line)
        if slide:
            flush_slide()
            slide_title = slide.group(1).strip()
            click_index = None
            continue
        click = CLICK_RE.match(line)
        if click:
            flush_click()
            click_index = int(click.group(1))
            continue
        visual_match = VISUAL_RE.search(line)
        if visual_match:
            visual = visual_match.group(1).strip()
            continue
        click_lines.append(line)
    flush_slide()
    return stories


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.bundle_root.resolve()
    files = sorted((root / "corpus").glob("*.md"))
    topic = bundle_topic(files)
    stories: list[dict] = []
    for markdown in files:
        stories.extend(build(markdown, topic))
    output = args.output or root / "output" / "seeds_bundle.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(stories, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: wrote {len(stories)} stories to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
