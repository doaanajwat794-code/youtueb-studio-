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

## Pending owner approval
- Choice of the first Short idea (state/ideas-backlog.md)
- Tool stack for Shorts: Veo 3.1 + Veo 3.1 Fast (9:16), Gemini Image, Gemini TTS, free YouTube Audio Library music (config/providers.yaml)
- Shorts framework "60 Seconds, One Twist" (config/storytelling-framework.md)
