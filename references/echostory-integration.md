# EchoStory integration

## Goal

Display the correct Click-state screenshot while practicing one or more sentences, without changing the existing practice modes or blocking audio/text practice.

## Spec-first rollout

1. Update `EchoStory_PRD.md`:
   - Define `PresentationStep` as presentation material structure.
   - Keep `內容來源 / 練習模式 / 完成規則` separate.
   - State backward compatibility for stories without visual steps.
2. Update `UI_INTERACTION_SPEC.md`:
   - Place the image below NavList and above SentenceCard.
   - Switch image only when the current sentence enters another Click.
   - Keep one image while moving between sentences in the same Click.
   - Use a collapsible 25–32% viewport-height panel and tap-to-expand.
   - On load failure, show a lightweight placeholder and keep TTS/record/navigation enabled.
3. Update `docs/test_plan.md` with parser, model, widget, missing-image, and compatibility gates.
4. Commit Spec/Test Plan before test or product code.

## Data model

Prefer a story-level list because one Click may own multiple sentences:

```dart
class PresentationStep {
  const PresentationStep({
    required this.index,
    required this.visualRef,
    required this.sentenceIndexes,
  });

  final int index;
  final String visualRef;
  final List<int> sentenceIndexes;
}
```

Add `List<PresentationStep> presentationSteps` to `ApiStory`, defaulting to an empty list. Do not copy the same image path into every `SentenceItem`.

Resolve the active step deterministically:

```text
story.presentationSteps.firstWhere(sentenceIndexes contains current sentence index)
```

When there is no match, display no image.

## Secret Gist and local cache contract

Publish exactly three files to one Secret Gist:

```text
seeds_bundle.json
presentation_manifest.json
presentation-assets.zip
```

Store story references relative to the ZIP root:

```yaml
images/<presentation-slug>/<slide-id>-<click>.webp
```

Resolve the Gist from the local Settings ID through `https://api.github.com/gists/{id}`. Android verifies bytes and SHA-256, safely extracts to a version directory, and activates only a verified bundle. Web keeps a placeholder TODO.

## Importer

Extend `flutter/lib/services/corpus_importer.dart`:

- Preserve the current `###` slide-to-story split.
- Parse contiguous `#### Click n` blocks.
- Read one `<!-- visual: relative/path.webp -->` per block.
- Assign sentence indexes produced by that block to its `PresentationStep`.
- Reject malformed Click sequences during build tooling, but keep runtime import backward-compatible.
- Keep corpus without Click blocks unchanged.

## Test order

1. Model JSON round-trip and missing-field compatibility.
2. Corpus parser: one Click/one sentence, one Click/many sentences, multiple Clicks, missing visual, non-contiguous Clicks, legacy corpus.
3. Asset path validation: relative accepted; drive letter, root path, URI, and `..` rejected.
4. Training widget: initial image, same-Click sentence change, cross-Click image change, cross-story reset, missing image fallback, dispose safety.
5. Full Flutter tests, analyze, debug APK.

## Packaging and sync

- Keep authoring bundles outside EchoStory runtime storage.
- Generate the existing array-format seeds file plus a separate asset manifest and ZIP.
- Ensure seed JSON stores ZIP-root-relative `visual_ref` values.
- Treat private company slides as private assets; do not publish them to a public gist.

## Cross-machine deployment

Use this when the real slide screenshots live on a different computer than the one that validated this Skill.

1. **Capture assets.** Screenshot the state after each animation Click. Name files `{slide-id}-{click-index:00}.webp` (e.g. `s23-00.webp`, `s23-01.webp`); Click `00` is the initial state.
2. **Install the Skill.** Copy `dist/skills/build-presentation-practice.zip` (packaged in the EchoStory repo, verified to match this Skill directory byte-for-byte) to the other machine and unzip it to `%USERPROFILE%\.codex\skills\build-presentation-practice\`.
3. **Write the corpus.** Copy `assets/presentation_corpus_template.md` as a starting point:

   ```markdown
   ### S23｜title
   #### Click 0
   <!-- visual: images/{slide-id}/s23-00.webp -->

   | EN | 中文 |
   | --- | --- |
   | sentence | translation |
   ```

4. **Convert images if needed.** `pip install -r requirements.txt`, then `python scripts/convert_images_to_webp.py <bundle-root>` for source PNG/JPG.
5. **Validate.** `python scripts/validate_practice_bundle.py <bundle-root>`
6. **Package.** `python scripts/build_presentation_seeds.py <bundle-root>` then `python scripts/package_practice_bundle.py <bundle-root> <output-dir> --version v1`
7. **Publish.** Set `$env:GITHUB_TOKEN` (gist scope) in that shell, then `python scripts/publish_secret_gist.py <bundle-root> --output-dir <output-dir>`.
   - No existing `gist_id` in `<bundle-root>/.presentation-practice.local.json` → creates a new Secret Gist.
   - To update an already-verified Secret Gist instead of creating a new one, copy that Gist's `.presentation-practice.local.json` (containing `{"gist_id": "..."}`) into `<bundle-root>` first — never hard-code the ID in source or corpus files.
8. Report the resulting Gist ID back to whoever owns the EchoStory Settings config; the App side (`docs/presentation_visual_practice_progress.md`) still needs one more Android emulator/device smoke pass against real content before switching the App's default source.
