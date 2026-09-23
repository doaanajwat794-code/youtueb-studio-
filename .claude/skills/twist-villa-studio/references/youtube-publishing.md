# YouTube integration — setup, upload, disclosure

## One-time setup (owner, ~20 minutes, free)
1. Google Cloud Console → create project "Twist Villa Studio".
2. Enable **YouTube Data API v3**.
3. **API key** (for research stats): Credentials → Create API key → restrict it to
   YouTube Data API v3 → save as `YOUTUBE_API_KEY`.
4. **OAuth consent screen**: External, add your Google account as a test user, add
   scopes `youtube.upload` and `youtube.force-ssl`. Then set publishing status to
   **In production** (otherwise refresh tokens expire after 7 days).
5. **OAuth client**: Credentials → Create OAuth client ID → *Desktop app* → download
   the JSON (keep it OFF GitHub).
6. On your own computer: `pip install -r requirements.txt` then
   `python -m studio youtube-auth path/to/client_secret.json` → a browser opens → sign
   in with the account that owns Twist Villa → pick the Twist Villa channel.
7. Save `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` as
   secrets in the Claude Code cloud environment (and/or your local `.env`).

## Important platform limits
- **Unaudited API projects:** YouTube locks videos uploaded through API projects that
  have not passed YouTube's API compliance audit to **private**. That matches our
  "private first" rule, but to publish API-uploaded videos later you either
  (a) apply for the free compliance audit (the form is in the YouTube API Services
  docs), or (b) upload the final approved file manually in YouTube Studio.
  Verify the current rule during setup.
- **Quota:** default 10,000 units/day; one upload costs ~1,600 units, captions ~400,
  thumbnail ~50. Research stats cost a few units per call.
- **Thumbnails** via API require a verified channel (phone verification).

## Upload behaviour (enforced in `studio/youtube.py`)
- `privacyStatus` is hard-coded to `private`. No public/unlisted/scheduled path exists.
- Uploads captions (`final.en.srt`) and `thumbnail.jpg` if present.
- Sets `containsSyntheticMedia` from `metadata.yaml` (YouTube's altered/synthetic
  content disclosure). Decide per video; default `true` for realistic humans.

## Monetization safety (YouTube "inauthentic content" policy, July 2025)
- Every video must be clearly authored and different: original story, real motion
  footage, our own edit. No templated slideshows, no near-duplicate narrations.
