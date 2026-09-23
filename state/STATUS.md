# Twist Villa Studio — Status

**Last updated:** 2026-09-23 · **Phase:** 0 — Setup & approvals · **Active video:** none yet

## Next pending task
**Owner decisions needed (no money is spent until these are made):**
1. Approve or edit the storytelling framework → `config/storytelling-framework.md`
2. Approve or edit channel direction → `config/channel.yaml`
3. Approve the tool stack (Google: Veo 3.1 + Veo 3.1 Fast, Gemini Image, Gemini TTS, Lyria)
4. Set budget caps → `config/budget.yaml` (proposed: $600 per video, $700 per month)
5. Create accounts/keys (free to create): Google AI Studio **paid-tier** API key,
   YouTube Data API key, YouTube OAuth client — then add them as cloud-environment secrets

**Then, in order:** run `python -m studio research-stats` (fills in real view counts,
free) → pick the first story idea (free) → screenplay (free) → story bible +
storyboard (free) → pilot minute (≈ $25–50, needs approval).

## Done
- 2026-09-23 · Repo inspected (was empty). Skill, CLAUDE.md, config, research, and
  pipeline code created.
- 2026-09-23 · Competitor research saved (`research/competitor-research.md`,
  `research/sources.yaml`). View counts pending — youtube.com blocked in this environment.
- 2026-09-23 · Tool/pricing research saved (`research/tool-research.md`).
- 2026-09-23 · **Tested (free, offline):** `python -m studio selftest` passed all
  checks — 1920x1080 / 24 fps export, audio present, A/V sync ±0.10 s, runtime match,
  captions (SRT) generated, duplicate-footage rejection, and budget guard refusals
  (no approval, over approval, over single-call cap, over per-video cap).

## Integration test status
| Integration | Status |
|---|---|
| FFmpeg assembly, mix, captions, sync check | ✅ TESTED with synthetic media |
| Budget guard / approvals / ledger | ✅ TESTED (selftest) |
| Veo 3.1 video (Gemini API) | ⏳ UNTESTED — needs GEMINI_API_KEY + approval |
| Gemini image (refs, thumbnail) | ⏳ UNTESTED |
| Gemini TTS (voice) | ⏳ UNTESTED |
| Lyria music | ⛔ NOT BUILT — request format to confirm from docs |
| YouTube research stats (API key) | ⏳ UNTESTED — needs YOUTUBE_API_KEY |
| YouTube private upload (OAuth) | ⏳ UNTESTED — needs OAuth setup |

## Blockers / environment notes
- Cloud environment network blocks youtube.com, elevenlabs.io, kling.ai, fal.ai,
  runwayml.com, replicate.com. Google APIs (`*.googleapis.com`) are reachable.
  To use Kling or ElevenLabs from here, add their API hosts in the environment's
  network settings.
- Container storage is temporary: finished videos must be copied to Google Drive.

## Spend to date
$0.00 (see `state/spend-ledger.csv`)
