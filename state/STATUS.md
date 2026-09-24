# Twist Villa Studio — Status

**Last updated:** 2026-09-24 · **Format:** YouTube Shorts (55–60 s, 9:16, 1080x1920)
**Production model:** the owner generates clips in **Google Flow** (Veo 3.1 **Fast** for all shots) from
Claude's prompts and delivers them to the **local folder** via Claude Code on their Windows 11 PC.
Extra paid spending: **not approved** ($0 caps). Public publishing: **not approved**.

**Active Short:** `projects/face-not-recognized/` · code **FNR** · media `media/FNR/`
**Phase:** 2 — Pre-production package **v2** (continuity fixes) ready, **waiting for owner approval**

## Next pending task
**Owner reviews and approves the FNR production package:**
- `projects/face-not-recognized/script.md` (screenplay v2, 56.7 s)
- `projects/face-not-recognized/bible.yaml` (Elise young/old, Theo, corridor, look)
- `projects/face-not-recognized/storyboard.yaml` + `flow-prompts.md` (11 shots, copy-paste prompts)
- `projects/face-not-recognized/PRODUCTION-GUIDE.md` (the owner's steps, Windows setup, voice, music)
- `projects/face-not-recognized/metadata.yaml` (title/description/hashtags draft)

Then the owner:
1. Does the Flow account check (PRODUCTION-GUIDE step 0) and reports back.
2. Sets up Claude Code on Windows 11 (one time) and clones the repo.
3. Generates 5 reference images + 11 clips in Flow (≈ 300 Fast credits incl. retakes; check in Flow).
4. Makes the voices in Google Vids (if free for the account) and downloads 2 YouTube Audio Library tracks.
5. Puts everything in `media\FNR\incoming\` and tells Claude "Import my Face Not Recognized clips."

Then Claude (on the owner's PC): `import-clips` → frame QC → `make-sfx` → `assemble` → verify 55–60 s
→ `thumbnail` → final `metadata.yaml` for approval. **No upload/publish without approval.**

## Done
- 2026-09-23 · Initial long-form setup. **Archived** 2026-09-24 → `archive/longform/`.
- 2026-09-24 · Pivot to Shorts; Shorts research; ShortsFaceless investigated (not for footage).
- 2026-09-24 · Google Flow manual workflow (prompt sheet, clip importer, voice split, cover).
- 2026-09-24 · **Owner's final choices saved** (Fast only, local delivery, free Google voice only, $0 extra
  spend, private only). Project **Face Not Recognized** created: screenplay, bible, 11-shot storyboard,
  Flow prompt sheet, voice scripts, owner guide, packaging draft.
- 2026-09-24 · New tools: interface text overlays, timed SFX, original synthesised SFX (`make-sfx`),
  music/voice auto-import by file name, speaker-aware voice split, auto-fitting cover text.
- 2026-09-24 · **Tested (free):** selftest 16/16 PASS; **dress rehearsal of the real FNR storyboard** with
  dummy clips/voices/music: 57.6 s, 1080x1920, A/V in sync, 10 caption cues, 4 interface overlays
  checked by eye, no voice overlaps after fixing N07/N08 timing, cover text fits.

- 2026-09-24 · **Story v2 (owner's continuity notes):** the lens fails intermittently (weak → stutters →
  drops out in the mirror → flickers back → dies when Theo sees her); the mirror sequence follows the
  lens (ring on = young, ring off = truth, same framing for S05/S06); the lens is replaced on camera in
  S10 (the ring powers on) before she is young again in S11; biometric rule shown with interface text
  ("Paired lens: not detected" → "Lens paired ✓") + Theo's line. Bible `world_rules` added; new SFX
  `lens_boot`. Prompt sheet regenerated (11 shots, all Fast, ≈ 300 credits).
- 2026-09-24 · **Re-tested (free):** selftest 16/16 PASS; FNR v2 dress rehearsal: 56.7 s, 1080x1920,
  A/V in sync, 10 caption cues, 5 overlays incl. the 2-line "Lens paired" card checked by eye, no voice overlaps.

## Integration test status
| Integration | Status |
|---|---|
| Assembly (vertical), mix, burned captions, overlays, SFX, sync check, cover | ✅ TESTED with synthetic media (FNR rehearsal) |
| Flow prompt sheet · clip/music/voice import by file name · voice split | ✅ TESTED with synthetic files · ⏳ real Flow clips pending |
| Google Flow features in the owner's account (portrait + Fast, Ingredients, credits, 1080p download) | ⏳ UNVERIFIED — owner checks (guide step 0) |
| Google Vids AI voiceover (free Google voice) | ⏳ UNVERIFIED for the owner's account |
| Gemini TTS free tier | ⏳ UNTESTED — only with the owner's OK and a free key |
| Local run on Windows 11 (ffmpeg, caption font, hook) | ⏳ UNTESTED — first local session |
| YouTube private upload (OAuth) | ⏳ UNTESTED — or the owner uploads manually as Private |
| Veo API · Google Cloud TTS | ⛔ NOT USED (paid) |

## Blockers / environment notes
- The cloud session can't see the owner's PC; production with real clips happens in local Claude Code.
- The cloud environment can't open youtube.com, Flow, Vids, or ShortsFaceless.
- Repo: the only branch `claude/gracious-feynman-hiut4e` is also the GitHub **default branch**, so
  `git clone` on the PC gets everything without a merge.

## Spend to date
$0.00 (see `state/spend-ledger.csv`) · Caps $0 (additional paid spending not approved)
