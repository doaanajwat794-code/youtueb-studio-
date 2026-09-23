# Twist Villa Studio — Status

**Last updated:** 2026-09-24 · **Format:** YouTube Shorts (55–60 s, 9:16, 1080x1920)
**Phase:** 1 — Pick the first Short · **Active Short:** none yet

## Next pending task
**Owner picks one of the 3 pitched ideas** in `state/ideas-backlog.md`
(recommended: #1 "Face Not Recognized").

Then, in order (the first four steps are free):
1. `python -m studio new "<title>"`, then write the full script (58 s, 110–130 words)
2. Story bible (locked character/location descriptions + narrator voice)
3. Storyboard: 11 shots with timed narration
4. `python -m studio estimate <slug>` → show the cost (~$19–27) → **wait for owner approval**
5. Keys needed before any generation: `GEMINI_API_KEY` (Google AI Studio, paid tier), plus
   YouTube OAuth for the private upload. See `.env.example`.
6. Paid: reference images (~$1.40) → pilot = first ~12 s, 3 shots (~$7.30; checks that 9:16 works)
   → remaining footage → narration → assemble → private upload.

## Done
- 2026-09-23 · Initial long-form setup (Skill, config, research, pipeline, selftest). **Archived** 2026-09-24 → `archive/longform/`.
- 2026-09-24 · **Pivot to Shorts approved by the owner.** Updated CLAUDE.md, the Skill, channel/budget/provider config,
  story framework, templates, and workflow guides. Long-form files archived, not deleted.
- 2026-09-24 · Shorts research saved (`research/shorts-research.md`, `research/shorts-sources.yaml`).
  View counts are pending because youtube.com is blocked here; third-party figures are labelled.
- 2026-09-24 · Pipeline adapted: 1080x1920 render, burned-in captions, Veo native audio in the mix,
  9:16 requests to Veo and the image model.
- 2026-09-24 · **Tested (free, offline):** `python -m studio selftest` passed: 1080x1920 / 24 fps,
  audio present, A/V sync ±0.10 s, runtime match, burned captions checked on a frame, duplicate
  footage rejected, and all budget-guard refusals work.
- 2026-09-24 · Three original Short ideas pitched (`state/ideas-backlog.md`).

## Integration test status
| Integration | Status |
|---|---|
| FFmpeg assembly (vertical), mix, burned captions, sync check | ✅ TESTED with synthetic media |
| Budget guard / approvals / ledger | ✅ TESTED (selftest) |
| Veo 3.1 video, 9:16 (Gemini API) | ⏳ UNTESTED — needs GEMINI_API_KEY + approval; the pilot verifies 9:16 |
| Gemini image (reference sheets) | ⏳ UNTESTED |
| Gemini TTS (narration) | ⏳ UNTESTED |
| Music | Free YouTube Audio Library (manual download); the Lyria adapter is NOT BUILT |
| YouTube research stats (API key) | ⏳ UNTESTED — needs YOUTUBE_API_KEY |
| YouTube private upload (OAuth) | ⏳ UNTESTED — needs OAuth setup |

## Blockers / environment notes
- This cloud environment blocks youtube.com, elevenlabs.io, kling.ai, fal.ai, runwayml.com and
  replicate.com. Google APIs (`*.googleapis.com`) are reachable, so the Google stack works here.
- Container storage is temporary: copy finished Shorts to Google Drive.

## Spend to date
$0.00 (see `state/spend-ledger.csv`) · Monthly cap $150 · Per-Short cap $45
