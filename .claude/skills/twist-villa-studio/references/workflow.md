# Shorts production workflow — stage by stage

After each stage, update `projects/<slug>/project.yaml` → `stage` and `state/STATUS.md` →
next pending task, then commit the text files. ✋ = owner sign-off, 💲 = paid (needs approval).

## 1. Ideas (free) ✋
- Re-read `research/shorts-research.md` (principles, "do not copy" list) and
  `config/channel.yaml`.
- Pitch 3 ideas in `state/ideas-backlog.md`: logline, hook shot, clue, twist, echo ending,
  cast/locations, difficulty. Web-search each twist to check it isn't a known story.
- Recommend one. The owner picks.

## 2. Script (free) ✋
- Follow the beat sheet in `config/storytelling-framework.md` (target 58 s).
- 110–130 narration words; ≤ 2 dialogue lines. Mark the planted clue and its payoff.
- Self-check: is frame 1 striking? First line starts ≤ 0.5 s? New information every
  5–6 s? Twist at ~0:45–0:52? Final image echoes frame 1?

## 3. Bible (free)
- `bible.yaml`: `visual_lock` for the protagonist (face, hair, age, build, exact wardrobe and
  colours) and each location. These are pasted verbatim into every prompt.
- Narrator voice (Gemini TTS voice name + direction).

## 4. Storyboard (free) ✋
- 10–12 shots, 3–8 s each, summing to 55–60 s. Vertical framing notes on every shot.
- `tier: hero` for the hook, face close-ups, and the twist shot (~3 shots); the rest `standard`.
- `native_audio_db: -14` on shots whose Veo ambience/SFX you want in the mix.
- Anchor each narration line with `at_shot` + `offset`, and check the lines fit their shots.

## 5. Estimate and approval ✋💲
- `python -m studio estimate <slug>` → show the table → wait for approval.
- Record approvals per stage (`refs`, `pilot`, `footage`, `audio`). For `footage`, approve
  the footage estimate minus the pilot amount (the pilot shots are not regenerated).

## 6. Reference images 💲
- `python -m studio generate <slug> --stage refs`. Review them; the protagonist must look
  identical across all sheets.

## 7. Pilot (first ~12 s ≈ 3 shots) 💲
- `python -m studio generate <slug> --stage pilot`. Check: is it really 1080x1920 vertical?
  Does the face match the reference? Are the grade and grain right? Is there motion?
- If the API returns 16:9, stop, report it, and fix before spending more.
- Mark Veo `status: TESTED` in `config/providers.yaml` only after this works.

## 8. Footage 💲
- `python -m studio generate <slug> --stage footage` (existing files are skipped).
- QC every shot: on-model face and wardrobe, continuity of props and light direction,
  no warped hands or faces, no garbled text, subject framed for vertical. Regenerate
  failures within the approved amount.

## 9. Audio 💲 (cents)
- **Pilot only, optional voice A/B (free, manual):** the owner pastes the pilot narration into
  ShortsFaceless as a Custom Script, picks 1–2 voices, and downloads the result. We extract the
  audio (`ffmpeg -i sf.mp4 -vn sf.wav`) and compare it with Gemini TTS. If ShortsFaceless wins,
  and its export has no baked-in music, build an import step; otherwise use Gemini TTS.
- `python -m studio generate <slug> --stage audio` for narration.
- Music: a free YouTube Audio Library track → `media/<slug>/audio/music/M01.wav`; record the
  title in the description credits if its licence requires attribution.
- SFX: Veo native audio (`native_audio_db`) and library SFX → `media/<slug>/audio/sfx/`.

## 10. Assemble (free)
- `python -m studio assemble <slug>` produces `final.mp4` (1080x1920, 24 fps, captions burned
  in), `final.en.srt`, and `sync-report.json`.
- Automatic checks: resolution, fps, audio present, A/V sync ±0.10 s, runtime = storyboard.
- Manual checks: runtime is 55–60 s, captions match speech, no caption covers a face, the
  twist lands, and the loop into frame 1 feels intentional.

## 11. Packaging ✋
- `metadata.yaml`: title ≤ 50 characters, a 1–2 line description with the AI note,
  3–5 hashtags including #Shorts, and `contains_synthetic_media: true` for realistic humans.

## 12. Private upload ✋
- `python -m studio upload <slug>` uploads privately with captions. The owner reviews in
  YouTube Studio. **Public or scheduled publishing only on explicit approval.**
- Copy `final.mp4` to Google Drive and note the link in `project.yaml`.
