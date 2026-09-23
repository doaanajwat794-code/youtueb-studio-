# Production Tool Research — APIs, pricing, commercial terms

> **Shorts update (2026-09-24):** still valid for Shorts. Veo 3.1 supports native 9:16 at 1080p
> (to verify in the pilot). A 58-second Short costs about $19–27 on the Google stack
> (see `state/ideas-backlog.md`). Music comes from the free YouTube Audio Library.

**Collected:** 2026-09-23 via web search. Official pricing pages (ai.google.dev,
kling.ai, elevenlabs.io, fal.ai) were **blocked** from the research environment, so
prices below are as reported by search results and third-party guides.
**Re-check each official page before approving spend.** Nothing here is tested yet.

## Network reachability from this cloud environment (tested 2026-09-23)

| Host | Reachable? | Meaning |
|---|---|---|
| `www.googleapis.com` (YouTube Data API) | ✅ yes | Research stats + uploads can run here |
| `oauth2.googleapis.com` | ✅ yes | YouTube OAuth token exchange works here |
| `generativelanguage.googleapis.com` (Gemini API: Veo, Imagen/Gemini Image, TTS, Lyria) | ✅ yes | Whole Google stack can run here |
| `api.elevenlabs.io`, `api.klingai.com`, `queue.fal.run`, `api.dev.runwayml.com`, `api.replicate.com` | ❌ blocked | Would need the environment's network policy changed, or running on your own computer |
| `www.youtube.com` | ❌ blocked | Can't browse YouTube pages; the API works instead |

## Video generation

| Tool | API? | Reported price | Notes |
|---|---|---|---|
| **Google Veo 3.1** (Gemini API / Vertex AI) | Yes, pay-as-you-go | $0.40/s (1080p, with audio); **Fast** $0.15/s; Lite from ~$0.03/s (lower res, no audio) | 4/6/8 s clips; reference images for consistency; native audio; SynthID watermark. [pricing guide](https://www.atlascloud.ai/blog/tips/veo-3.1-api-pricing), [MindStudio](https://www.mindstudio.ai/blog/veo-3-1-vs-veo-3-1-fast-vs-veo-3-1-light-comparison), [Veo docs](https://ai.google.dev/gemini-api/docs/veo) |
| **Kling 3.0** | Yes (official prepaid packs; resellers pay-as-you-go) | ~$0.075–0.17/s | Strong motion and value; failed tasks not charged (official). Blocked here. [Kling dev pricing](https://kling.ai/dev/pricing), [costbench](https://costbench.com/software/ai-media-apis/kling-api/) |
| **Runway Gen-4 / 4.5** | Yes (dev.runwayml.com, separate credits from app plans) | Gen-4 Turbo $0.05/s, Gen-4.5 $0.12/s | $10 minimum top-up. [Runway pricing guides](https://apiframe.ai/guides/runway-api-guide) |
| **Seedance 2.x** (ByteDance) | Via fal / Replicate / BytePlus | ~$0.34–0.68/s at 1080p | Official BytePlus route not sold in US/UK/CA/AU/NZ. [comparison](https://apiframe.ai/blog/seedance-2.0-api-providers) |
| **OpenAI Sora 2** | Being retired | $0.10–0.70/s | API reported to shut down **24 Sep 2026** — excluded. [source](https://unifically.com/blogs/sora-api) |

**Web subscriptions ≠ API access.** Google AI Pro/Ultra (Flow), Kling app plans, and
Runway app plans do **not** include API credits; each API is billed separately.

## Images (character sheets, location plates, thumbnail)
- **Gemini 3 Pro Image ("Nano Banana Pro")** — ~$0.134 per 1K/2K image, ~half in
  batch mode; identity preservation across up to five subjects; SynthID.
  ([OpenRouter](https://openrouter.ai/google/gemini-3-pro-image))

## Voice
- **Gemini TTS** — ~$20 per 1M audio output tokens, ~25 tokens per second of audio
  → roughly **$0.03 per minute** of speech. ([pricing guide](https://the-rogue-marketing.github.io/google-gemini-tts-speech-audio-api-pricing-may-2026/))
- **ElevenLabs** — API ~$0.10 per 1K characters (v3 / Multilingual v2). **Commercial
  licence requires a paid subscription** (Starter ~$6/mo and up); reports say
  pay-as-you-go API use has no commercial licence. Best-in-class emotion; blocked
  here. ([BIGVU guide](https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/))

## Music
- **Google Lyria 3 Pro / 3.5** (Gemini API) — ~$0.08 per track, up to ~3 min.
  ([Lyria overview](https://invideo.io/blog/lyria-ai-music-generator/))
- ElevenLabs Music API — ~$0.15/min (needs subscription for commercial use).

## Commercial use & platform rules
- **Google (paid API tier):** outputs usable commercially per Google's terms;
  SynthID invisible watermark is embedded. Use the *paid* tier — free-tier inputs
  may be used to improve Google products.
- **Copyright:** purely AI-generated material may not be copyrightable (US Copyright
  Office position); human authorship (our script, edit, direction) strengthens our
  claim. We still own our script, edit and channel brand.
- **YouTube disclosure:** creators must toggle "Altered or synthetic content" when
  realistic content could mislead viewers (real people/places/events). Clearly
  fictional sci-fi usually doesn't require it, but we decide per video.
  ([YouTube Blog](https://blog.youtube/news-and-events/disclosing-ai-generated-content/))
- **YouTube monetization:** the July 2025 "inauthentic content" rule demonetizes
  mass-produced, templated AI videos. Original, authored, varied films are fine.

## Recommendation
**Google stack for everything** (Veo 3.1 + Veo 3.1 Fast, Gemini 3 Pro Image,
Gemini TTS, Lyria) because it is (a) one API key and one bill, (b) reachable from
this cloud environment today, (c) commercially licensed on the paid tier, and
(d) competitively priced. Keep **Kling 3.0** as the budget/motion alternative and
**ElevenLabs** as the premium narrator option if Gemini TTS doesn't sound human
enough in the pilot.
