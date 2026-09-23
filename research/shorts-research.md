# Shorts Research — cinematic AI mystery / sci-fi / twist Shorts

**Collected:** 2026-09-24 · **Method:** web search · **Structured list:** `research/shorts-sources.yaml`
**Status:** this is the primary research for production. The long-form research is archived
in `archive/longform/` and is not the main reference.

## Honest limits
- youtube.com is blocked in this environment. I found real Short URLs and dates through
  search, but **I could not verify their view counts or durations**. Every view figure below
  comes from a third party and is marked that way.
- I found **no well-documented, verified channel** doing exactly "cinematic AI identity-twist
  Shorts" at scale. That is a gap in the evidence, and possibly an opening for the channel.
- Fix: add a free `YOUTUBE_API_KEY` and run `python -m studio research-stats`. It fills in
  views, dates, durations, views/day and views vs. the channel's median automatically.

## What the evidence says

### 1. The first 2–3 seconds decide everything
- 50–60 % of viewers who drop off do so in the first 3 seconds; aim to hold > 80 % there
  ([Shortimize](https://www.shortimize.com/blog/youtube-shorts-retention-rate),
  [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention)).
- For 30–60 s Shorts, keep swipe-away in the first 3 s below ~35 %
  ([Retensis](https://retensis.com/blog/youtube-shorts-analytics-metrics-explained)).
- Burned-in captions help stop the early drop.
- **Rule for us:** frame 1 is already the strongest, strangest image, with the first
  narration line starting before second 1. No logo, no title card, no slow fade-in.

### 2. Completion and re-watches drive distribution
- In 2026, completed views and re-watches matter more than swipe rate
  ([Socialync](https://www.socialync.io/blog/youtube-shorts-algorithm-2026)).
- Mystery and horror stories report high completion because viewers stay for the answer
  (85–95 % claimed; third party).
- Strong payoffs correlated with 65–80 % retention in a 1.8M-view two-sentence-horror case
  ([Medium case study](https://medium.com/@NoahBourland/use-ai-to-make-10k-month-with-viral-horror-short-videos-587d9027d41e)).
- **Rule for us:** hold the answer until second 45–52, and end on an image that sends viewers
  back to frame 1 (a loop). The twist must re-frame a clue they already saw.

### 3. Recurring characters and a recognisable format build channels
- A recurring AI character (the BigfootBoyz Veo 3 vlogs) reportedly grew to 330K followers
  and 15M views in 3 days ([Superprompt](https://superprompt.com/blog/how-to-make-viral-ai-character-vlogs)).
  Neural Viz grew by building one consistent universe.
- **Rule for us:** a consistent "Twist Villa" world and look (grade, grain, narrator voice,
  a signature sound at the twist), so each Short feels like an episode of one anthology.

### 4. Story shapes that fit 60 seconds
From the short AI films found ([EPILOGUE](https://www.youtube.com/watch?v=vz3iTY38vF4),
[THE BLACK RIDGE](https://www.youtube.com/watch?v=36JtIiXWXrA),
[SUPPLY](https://www.youtube.com/watch?v=Vssy98rFgRM),
[RESET](https://www.youtube.com/watch?v=BMLTQ0ouz1U)), based on their published synopses:
- **One character, one impossible signal:** a message, a voice, a number that shouldn't exist.
- **Identity reversal:** the character is not what they think they are (copy, AI, simulation).
- **Loop / reset:** the ending restarts the beginning. This is common, so it needs a fresh angle.
- **Rule for us:** one character, 1–2 locations, one impossible detail in frame 1, one twist.
  Avoid premises already taken by these films (manufactured memories à la SUPPLY, plain resets
  à la RESET).

### 5. AI-slop risk is real, and it's about low effort, not AI
- YouTube reports that 1 in 5 Shorts recommended to new users is low-quality mass-produced AI.
  It has deleted major slop channels, and the CEO's 2026 letter targets it
  ([OutlierKit](https://outlierkit.com/resources/youtube-ai-slop-crackdown-2026/),
  [Search Engine Journal](https://www.searchenginejournal.com/youtubes-ai-slop-problem-and-how-marketers-can-compete/567297/)).
- YouTube says AI labels **don't** reduce reach or monetization, and AI with genuine human
  direction stays monetizable
  ([YouTube policy summary](https://support.google.com/youtube/answer/1311392?hl=en)).
- **Rule for us:** every Short is an original, authored story with real motion footage and our
  own edit. No templates, no slideshows, no recycled narration. Toggle the synthetic-content
  disclosure for realistic humans.

### 6. Production facts
- Veo 3.1 supports native **9:16** and **1080p** output
  ([Google](https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/),
  [AlternativeTo](https://alternativeto.net/news/2025/9/veo-3-and-veo-3-fast-now-in-gemini-api-with-9-16-and-1080p-support)).
  One developer-forum report says the API returned 16:9 anyway
  ([forum](https://discuss.ai.google.dev/t/veo-3-1-api-aspect-ratio-parameter/107902)).
  **The pilot checks this first.**
- Shorts can run up to 3 minutes; we deliberately stay at 55–60 s
  ([Riverside](https://riverside.com/blog/how-long-can-youtube-shorts-be)).

## Reusable principles (the Twist Villa Shorts playbook)
| Dimension | Principle |
|---|---|
| Hook (0–2 s) | Frame 1 = one impossible, specific image + a first line that asks a question |
| Structure | Hook → rule → escalation ×2 → twist (≈ 0:45) → echo image (loop) |
| Character | One protagonist, same face/wardrobe locked in every prompt; the others are voices/screens |
| Visuals | 10–12 shots, 3–8 s each, always moving; vertical composition with the subject in the upper two-thirds |
| Pacing | A new piece of information every 5–6 s; no shot repeats |
| Narration | 110–130 words, first person, intimate; dialogue ≤ 2 short lines |
| Sound | Room tone always; one signature "twist sting"; music drops out just before the reveal |
| Captions | Burned-in, large, 2 lines max, kept clear of the bottom UI |
| Ending | The last image mirrors frame 1 so a re-watch reveals the planted clue |
| Packaging | Title ≤ 50 characters with a curiosity gap; 3–5 hashtags incl. #Shorts |

## What we will not copy
No premises, characters, footage or dialogue from any reference. Specifically avoid:
manufactured-memory-as-product (SUPPLY), a lone Mars astronaut transmission (THE BLACK RIDGE),
a generic "reset" loop (RESET), and a companion-robot twist (AI Movie Companion).
