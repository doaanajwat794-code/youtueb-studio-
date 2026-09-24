# Approved decisions log

Permanent choices the owner has approved. Newest last. These override defaults
anywhere else. Format: `YYYY-MM-DD · decision · (file updated)`.

- 2026-09-23 · ~~Long-form only: 15–30 min, 16:9, 1920x1080; no Shorts.~~ **SUPERSEDED 2026-09-24** (see below).
- 2026-09-23 · Owner approval is required before any paid API charge, and before any public/unlisted/scheduled publication. Uploads are private. (config/budget.yaml, studio/youtube.py)
- 2026-09-23 · Credentials are never stored in GitHub; large media stays outside git. (.gitignore)
- 2026-09-24 · **Format = YouTube Shorts only:** 55–60 s, 9:16, 1080x1920, English. Genres: cinematic mystery, psychological thriller, and science fiction about human identity and technology. Fully AI-generated moving video with original narration, SFX, music and cinematic editing. (config/channel.yaml, config/providers.yaml → render)
- 2026-09-24 · **Do not return to long-form** unless the owner explicitly asks. Long-form research and settings are archived in `archive/longform/` and are not the main reference. (CLAUDE.md, SKILL.md)
- 2026-09-24 · **Budget:** preferred $50–150 per month. Caps set to $150/month and $45 per Short. (config/budget.yaml)
- 2026-09-24 · Use the existing tested editing pipeline (FFmpeg) for assembly. (studio/assemble.py)
- 2026-09-24 · Owner has an **active ShortsFaceless subscription**. Rule: check existing subscriptions before any paid service; never buy a new subscription, generate paid footage, or publish without approval. (SKILL.md rule 8, config/providers.yaml → owner_subscriptions)

- 2026-09-24 · **Production model: existing subscriptions only.** The owner generates all footage manually in **Google Flow** (paid subscription) from Claude's `flow-prompts.md` and hands the clips back; Claude does research, ideas, scripts, storyboards, prompts, import, edit, narration, SFX, music, captions, export, and packaging. **No paid Veo/video API; never ask the owner to buy one.** (CLAUDE.md, SKILL.md, config/providers.yaml → video.primary)
- 2026-09-24 · **ShortsFaceless (30 videos/month):** used only where it genuinely improves the workflow (narration voice option); its animated still images are **never** used as footage. (config/providers.yaml → owner_subscriptions)
- 2026-09-24 · **Style:** realistic moving footage, consistent characters/clothing/environments, natural movement, strong opening hooks, unexpected endings. (config/channel.yaml → style)
- 2026-09-24 · **Budget:** extra-spend target $0 per Short; safety caps $5/Short and $20/month for any separately approved paid call. Supersedes the $45/$150 caps. (config/budget.yaml)
- 2026-09-24 · **Clip naming:** `CODE_SNN_vN.mp4` (e.g. `FNR_S03_v2.mp4`); references `CODE_REF_<NAME>_<VIEW>.png`; narration `CODE_VOICE_vN.*`. (SKILL.md, references/flow-handoff.md)

## Pending owner approval
- Choice of the first Short idea (state/ideas-backlog.md), recommended #1 "Face Not Recognized"
- Hand-off method: Google Drive shared folder (needs a free GOOGLE_API_KEY) or Claude Code on your computer
- Narration voice: A/B test on the first Short (ShortsFaceless voice vs free Google voice vs your own voice)
- Flow model mix: all Fast (≈300 credits) or hook + twist on Quality (≈540 credits)
- Shorts framework "60 Seconds, One Twist" (config/storytelling-framework.md)

## Superseded
- 2026-09-24 · ~~Veo 3.1 via the Gemini API for footage (≈ $24–26.50 per Short)~~ → replaced by Google Flow (manual).
- 2026-09-24 · ~~Caps $45 per Short / $150 per month~~ → replaced by the $0 target and $5/$20 safety caps.
