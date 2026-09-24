# Shorts workflow (Google Flow edition): stage by stage

✋ = owner decision. After each stage: update `project.yaml → stage` and `state/STATUS.md`,
then commit the text files.

## 1. Ideas ✋
- Use `research/shorts-research.md` (principles and the "do not copy" list) and `config/channel.yaml`.
- Pitch 3 ideas in `state/ideas-backlog.md`: logline, hook, clue, twist, echo ending, cast and
  locations, **Flow feasibility** (how many characters and locations, any hard VFX), and a credit estimate.
- Web-search each twist for originality. Recommend one.

## 2. Project + script ✋
- `python -m studio new "<Title>" --code ABC` (2–4 letter code used in every file name).
- `script.md`: the table from the framework (58 s, 110–130 words, ≤ 2 dialogue lines, clue → payoff marked).

## 3. Bible
- `bible.yaml`: `visual_lock` per character (age, face, skin, eyes, hair, build, exact wardrobe with
  colours and materials, one distinctive detail) and per location; `look.style_lock`; `look.negative`.
- Keep casts tiny: 1 visible protagonist; others as voices, silhouettes, hands, or reflections.

## 4. Storyboard ✋
- `storyboard.yaml`: 10–12 shots, 3–8 s each, total 55–60 s; ids `S01…S12`.
- Per shot: `beat`, `seconds`, `trim_start` (skip the first ~0.3–0.5 s of Flow clips), `tier`
  (`hero` → Flow Quality for hook, twist and key close-ups; `standard` → Fast), `characters`,
  `location`, `camera`, `prompt`, optional `flow_mode` and `flow_notes`, and `native_audio_db` (keep
  Flow's ambience/SFX at e.g. −16 dB).
- Narration lines are anchored with `at_shot` + `offset`.

## 5. Flow prompt sheet
- `python -m studio flow-prompts <slug>` writes `flow-prompts.md` (reference-image prompts, one
  prompt per shot, file names, ingredients, credit estimate) and `narration.txt`.
- Show the owner the credit estimate and the file-naming rule. Point them to `references/flow-handoff.md`.

## 6. Owner generates in Flow ✋
- The owner makes the reference images first, then the clips in order; downloads the highest
  resolution; renames `CODE_SNN_vN.mp4`.

## 7. Hand-off + import
- Drive: `python -m studio fetch-drive <slug> <folderId>` (needs `GOOGLE_API_KEY`), then import.
- Local: files are already in `media/<slug>/incoming/`.
- `python -m studio import-clips <slug>` reports OK / WARN / MISSING per shot: not vertical,
  too short, low resolution (upscaled), identical files.
- QC every imported clip by extracting frames: face and wardrobe match the bible, continuity, no
  warped hands or faces, no garbled text, real motion. Ask the owner to regenerate failures (name
  the shot and say exactly what to fix in the prompt).

## 8. Narration
- First Short: A/B test the options in `config/providers.yaml → narration_and_dialogue`; the owner
  picks the permanent voice (log it in `decisions.md`).
- One recording → `python -m studio import-voice <slug> <file>` splits it at the pauses into `N01…`.
- Check each line's length fits its shots; adjust `offset`s.

## 9. Music + SFX
- Music: a free YouTube Audio Library track (the owner or Claude downloads it) →
  `media/<slug>/audio/music/M01.wav`; credit it in the description if required.
- SFX: Flow's own clip audio via `native_audio_db`, plus library SFX in `audio/sfx/`.
- The music drops out ~1 s before the twist; a signature sting marks the reveal.

## 10. Assemble + verify
- `python -m studio assemble <slug>` → `final.mp4` (1080x1920, 24 fps, captions burned in),
  `final.en.srt`, `sync-report.json`.
- Automatic checks: resolution, fps, audio, A/V sync ±0.10 s, runtime = storyboard.
- Manual checks: 55–60 s; captions match speech and don't cover faces; the hook lands in < 2 s;
  the twist is clear; the echo loops into frame 1.

## 11. Packaging ✋
- `metadata.yaml`: title ≤ 50 characters, description with a hook, the AI note, and music credit;
  3–5 hashtags incl. #Shorts; `contains_synthetic_media: true`.
- Cover: `python -m studio thumbnail <slug> --at <sec> --text "≤3 WORDS"` (caption-free frame).

## 12. Upload ✋
- Private upload via `python -m studio upload <slug>` (after YouTube OAuth setup), **or** the owner
  uploads `final.mp4` in YouTube Studio as Private. Public/scheduled only on explicit approval.
- Copy `final.mp4` to Google Drive; note the link in `project.yaml`.
