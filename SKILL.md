---
name: build-presentation-practice
description: Convert animated presentation slides into portable Click-by-Click screenshot and speaking-practice bundles for EchoStory. Use when Codex needs to organize PowerPoint or slide animation states, map each Click screenshot to one or more bilingual practice sentences, define relative asset paths, validate a presentation corpus, compress images, or package the result as a transferable ZIP for another computer.
---

# Build Presentation Practice

Create a portable hierarchy:

```text
Presentation -> Slide -> PresentationStep (Click) -> 1..n sentences
```

Treat `PresentationStep` as material structure, not a new practice mode.

## Workflow

1. Inventory slide IDs, Click order, screenshots, and bilingual sentences.
2. Copy `assets/presentation_corpus_template.md` as the corpus starting point.
3. Name screenshots `{slide-id}-{click-index:00}.webp`, including `00` for the initial state.
4. Keep all stored paths relative. Never write drive letters, user profiles, `file://` URLs, or machine-specific absolute paths into corpus or manifest files.
5. Map each `#### Click n` to exactly one screenshot and one or more sentence rows.
6. Read [references/paths-and-schema.md](references/paths-and-schema.md) for directory layout, schema, compatibility, and EchoStory destinations.
7. Run `scripts/convert_images_to_webp.py <bundle-root>` when source PNG/JPG images need conversion; install `requirements.txt` first.
8. Run `scripts/validate_practice_bundle.py <bundle-root>`.
9. Run `scripts/build_presentation_seeds.py <bundle-root>` to generate the array-format `seeds_bundle.json`.
10. Run `scripts/package_practice_bundle.ps1 -BundleRoot <bundle-root> -OutputDirectory <output-dir>` to create `presentation-assets.zip` and `presentation_manifest.json`.
11. Run `scripts/publish_secret_gist.py <bundle-root> --output-dir <output-dir>` to create or update the fixed three-file Secret Gist.
12. When App integration is requested, read [references/echostory-integration.md](references/echostory-integration.md) and follow its Spec/Test-first rollout.

## Path rules

- Resolve `visual` from the bundle root, using `/` in stored metadata.
- Prefer `images/{presentation-slug}/{slide-id}-{click-index:00}.webp`.
- Keep corpus paths such as `corpus/presentation.md` relative to the bundle root.
- Keep `visual_ref` relative to the downloaded ZIP root; never rewrite it to the authoring computer's path.
- Reject `..` traversal and absolute paths during validation.

## Image rules

- Capture the state after each animation Click; use Click `00` for the initial state.
- Use WebP, 1280–1600 px wide, typically 100–300 KB per image.
- Reuse one Click image for all sentences belonging to that Click.
- Do not duplicate a screenshot per sentence.
- If an image is missing, preserve text practice and report the missing relative path.

## Packaging result

The generated upload set must contain:

```text
seeds_bundle.json
presentation_manifest.json
presentation-assets.zip
```

Store only relative POSIX-style paths and SHA-256 hashes. Exclude source images, cache, temporary, hidden, local configuration, and existing ZIP files.

## EchoStory compatibility

- Preserve existing corpus without `#### Click` blocks.
- Model a slide as one story and Click states as ordered `presentation_steps`.
- Resolve the displayed image as the current sentence's step image.
- Do not block TTS, recording, navigation, or text practice when an image cannot load.
- Update Spec and tests before implementing importer or Flutter model changes.
