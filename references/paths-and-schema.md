# Paths and schema

## Portable bundle

```text
presentation-practice/
├── corpus/
│   └── presentation.md
├── images/
│   └── presentation-slug/
│       ├── s20-00.webp
│       ├── s20-01.webp
│       └── s20-02.webp
└── output/
    ├── seeds_bundle.json
    ├── presentation_manifest.json
    └── presentation-assets.zip
```

All metadata paths are relative to `presentation-practice/`:

```markdown
<!-- visual: images/presentation-slug/s20-01.webp -->
```

Valid:

- `images/iinxpress/s23-00.webp`
- `corpus/technical-presentation.md`

Invalid:

- `D:\EchoStory\flutter\assets\...`
- `C:\Users\name\Pictures\...`
- `/home/name/slides/...`
- `../shared/s23.webp`
- `file:///...`

## Corpus schema

```markdown
### S23｜System Configuration Overview

#### Click 0
<!-- visual: images/iinxpress/s23-00.webp -->

| EN | 中文 |
| --- | --- |
| This is the main view. | 這是主要畫面。 |

#### Click 1
<!-- visual: images/iinxpress/s23-01.webp -->

| EN | 中文 |
| --- | --- |
| At the top is the Function Tab. | 上方是 Function Tab。 |
| It switches between working views. | 它用來切換不同工作視圖。 |
```

Rules:

- `###` identifies one slide/story.
- `#### Click n` identifies one ordered animation state.
- Each Click has exactly one `visual` comment.
- A Click owns one or more bilingual table rows.
- Click indices start at `0` and remain contiguous within a slide.
- Multiple sentences may share one Click image.
- Use `<!-- visual: none -->` for a text-only Click that has no screenshot (e.g. an opening/closing segment). Validation and seed generation treat it as an intentional empty `visual_ref`, not a missing-file error.

## EchoStory runtime destination

The Android App downloads the ZIP and extracts it into its application documents directory:

```text
presentation_assets/
├── active_version.txt
└── <version>/images/iinxpress/s23-00.webp
```

The story always stores a ZIP-root-relative reference:

```text
images/iinxpress/s23-00.webp
```

Do not preserve the source computer's extraction directory.

## Model shape

```json
{
  "presentation_steps": [
    {
      "index": 0,
      "visual_ref": "assets/presentation_practice/iinxpress/s23-00.webp",
      "sentence_indexes": [0]
    },
    {
      "index": 1,
      "visual_ref": "assets/presentation_practice/iinxpress/s23-01.webp",
      "sentence_indexes": [1, 2]
    }
  ]
}
```

Existing stories without `presentation_steps` remain valid.
