# Production workflow — stage by stage

Each stage ends with: update `projects/<slug>/project.yaml` → `stage`, update
`state/STATUS.md` → next pending task, commit text files. Ask for owner sign-off at
every ✋.

## 1. Idea (free) ✋
- Re-read `research/competitor-research.md` (patterns, what NOT to copy) and
  `config/channel.yaml` (genres, avoid-list).
- Write 3 loglines in `idea.md` using the framework's one-sentence test.
- Web-search each logline's core twist to check it isn't a known film/short.
- Recommend one, with a reason. Owner picks.

## 2. Screenplay (free) ✋
- Follow `config/storytelling-framework.md` beat table, scaled to the target length.
- Word budget: minutes × 140 (narration + dialogue). Mark every clue in the tracker.
- Dialogue exchanges ≤ 4 lines; staged to avoid heavy lip-sync (OTS, silhouettes,
  screens, intercoms, back-of-head, hands).
- Self-review before showing: hook in first 15 s? mini-cliffhanger every 3–4 min?
  midpoint flip? all clues paid off? final image mirrors the opening?

## 3. Story bible (free) ✋
- `bible.yaml`: one `visual_lock` paragraph per character and location, written as
  concrete physical facts (age, hair, wardrobe colours, materials, light). These
  strings are pasted verbatim into every prompt — that is how continuity is enforced.
- Choose narrator + character voices (Gemini TTS voice names; confirm in pilot).

## 4. Storyboard (free) ✋
- `storyboard.yaml`: one entry per shot, 3–8 s each, average ~5 s.
- Every shot: one action, one camera move, location + characters from the bible.
- `tier: hero` only for faces-in-close-up, dialogue and reveal shots (~25 %).
- Anchor each voice line to a shot (`at_shot` + `offset`); check line length fits.
- Run `python -m studio estimate <slug>` and show the full cost table.

## 5. Reference images (paid) ✋💲
- `python -m studio estimate <slug> --stage refs` → owner approves →
  `python -m studio approve <slug> --stage refs --usd <amount>` →
  `python -m studio generate <slug> --stage refs`.
- Review the sheets with the owner; regenerate any off-model image (inside budget).

## 6. Pilot (paid, small) ✋💲
- First ~60 s of the storyboard, full quality. Assemble it with placeholder or real
  narration. Judge: character consistency, look, motion quality, voice quality.
- Update `config/providers.yaml` statuses to TESTED for what worked. If something
  failed, fix prompts/tools before the main spend.

## 7. Full footage (paid, main cost) ✋💲
- Approve once for the stage; the guard stops at approval +10 %.
- Generation is resumable: existing shot files are skipped.
- QC every shot: on-model? continuity (wardrobe, props, light direction)? no
  artefacts on faces/hands? no text/watermarks? Re-generate failures within budget.
- Never reuse a shot; the assembler rejects duplicate files.

## 8. Voice, music, SFX (paid, small) ✋💲
- `python -m studio generate <slug> --stage audio` for narration/dialogue.
- Listen to every line; re-generate unnatural reads with a `direction` note.
- Music: Lyria cues (adapter pending docs check) or licensed library tracks — record
  the licence in `metadata.yaml` description credits.
- SFX: CC0/licensed library files in `media/<slug>/audio/sfx/`.

## 9. Assembly (free)
- `python -m studio assemble <slug>` → `media/<slug>/final.mp4`, `final.en.srt`,
  `sync-report.json`. It normalises to 1920x1080 / 24 fps, ducks music under voice,
  normalises loudness to −14 LUFS, and verifies resolution, fps, audio, A/V sync
  (±0.10 s) and runtime.
- Watch the full export before calling it done. Check caption line breaks.

## 10. Packaging ✋
- `metadata.yaml`: title (≤ 60 chars, honest), description (hook, AI note, chapters,
  credits), tags, synthetic-media flag. Thumbnail: 6 candidates (paid, small),
  owner picks; add ≤ 3 words of text in the edit, not in the AI image.

## 11. Private upload (free) ✋
- `python -m studio upload <slug>` → private video + captions + thumbnail.
- Owner reviews in YouTube Studio. **Public/scheduled only on explicit approval.**
- Move `media/<slug>/final.mp4` and sources to Google Drive; note the Drive link in
  `project.yaml`.

## Session hand-off checklist
- [ ] `state/STATUS.md` updated (done / next pending task / blockers)
- [ ] `state/decisions.md` updated if a permanent change was approved
- [ ] Text/config committed and pushed; no media or secrets staged
