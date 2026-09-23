# Competitor Research — Long-form AI Sci-Fi / Mystery / Thriller

**Collected:** 2026-09-23 · **Method:** web search (articles, reviews, festival
coverage, creator interviews) · **Structured list:** `research/sources.yaml`

## Limits of this research (read first)

- **youtube.com is blocked in the research environment.** I could not open the
  videos, read live view counts, or watch them frame by frame.
- So: titles, URLs and channels are verified from search results; durations and
  dates come from third-party sources; **view counts are mostly `pending`**.
- Performance-vs-age and vs-channel-typical comparisons need real numbers. The
  script `python -m studio research-stats` fills them in automatically from the
  official YouTube Data API once a free API key is added (see `state/STATUS.md`).
- The creative analysis below comes from reviews, festival juries, creator
  interviews and published synopses — not from my own viewing. Treat it as strong
  hypotheses to confirm when you (or a later session with YouTube access) watch them.

## Reference set

| # | Video | Channel | Length | Published | Views | AI? |
|---|---|---|---|---|---|---|
| 1 | [Oneiric](https://www.youtube.com/watch?v=aAg9iDh9_BQ) | Higgsfield AI | ~20 min | ~Aug 2026 | pending | Yes |
| 2 | [Hell Grind](https://www.youtube.com/watch?v=t33k2tn4GpA) | Higgsfield AI | 95 min | May 2026 | pending | Yes |
| 3 | [Nano](https://www.youtube.com/watch?v=TAHGZSeGVww) | DUST | 14 min | pending | 38M+ (3rd-party) | No |
| 4 | [A Kind World](https://www.youtube.com/watch?v=xYuGb4dbz5Q) | DUST | pending | 2025-04-25 | pending | "DUST AI" |
| 5 | [AI-POCALYPSE](https://www.youtube.com/watch?v=0KtrQJcKeyk) | DUST | pending | pending | pending | pending |
| 6 | [Simulation](https://www.youtube.com/watch?v=H6-N1v1REu8) | Hashem Al-Ghaili | 24 min | 2019 | pending | No |
| 7 | [The Frost](https://www.youtube.com/watch?v=QW-NFkVDfdA) | Waymark | 12 min | 2023 | pending | Yes |
| 8 | [Total Pixel Space](https://www.youtube.com/watch?v=zpAeygE4d1A) | Jacob Adler | 9:28 | 2025 | pending | Yes |
| 9 | [SUPPLY](https://www.youtube.com/watch?v=Vssy98rFgRM) | Beyond Frames | pending | May 2026 | pending | Yes |
| 10 | [Discarded Companion](https://www.youtube.com/watch?v=YY-M5bxTY28) | pending | pending | pending | pending | Yes |

Channels studied: [DUST](https://www.youtube.com/@watchdust) (≈3.4M subs, ≈417M
views — 3rd-party), [Neural Viz](https://www.youtube.com/@NeuralViz) (≈238K subs,
Jul 2026 — 3rd-party), [Aze Alter](https://www.youtube.com/@AzeAlter),
[Higgsfield Originals](https://www.youtube.com/playlist?list=PLaQe6ms8V2M7BR3p0FXxiR-HuHDsDzXav),
HFY narration channels ([1](https://www.youtube.com/channel/UCwK-GaTUuOQlXA7Ubhp2S-w),
[2](https://www.youtube.com/@Sci-FiHFYStories)).

## What the evidence says

### 1. Story beats technology — the #1 failure of long AI films is story
- **Hell Grind** (95 min, $500K, 15 people, 14 days) was widely praised as a tech demo
  and criticised as a film: "artificial look, choppy editing, weak story, lack of
  emotional depth"; characters "change accents" and have "synthetic voices".
  ([Notebookcheck](https://www.notebookcheck.net/First-95-minute-AI-movie-with-skateboards-demons-and-plenty-of-online-criticism.1308627.0.html),
  [JoBlo](https://www.joblo.com/we-saw-a-full-length-ai-generated-feature/))
- **Reply AI Film Festival** juror (IndieWire): entries ran 2–30+ min, most 7–15;
  some "even at just a few minutes in length felt unbearably long".
  ([IndieWire](https://www.indiewire.com/features/commentary/what-i-learned-watching-6-hours-gen-ai-short-films-reply-ai-1235206110/))
- **Takeaway:** length must be *earned* with a mystery engine and mini-cliffhangers,
  not filled with spectacle.

### 2. Design the format around what AI does well
- **Neural Viz** studied the tools first: AI is good at talking heads, weak at action,
  so he chose a mockumentary format, non-human characters (no uncanny valley) and a
  grainy retro-TV look that hides artefacts. Performance is driven by his own acting.
  ([The Daring Creatives](https://www.thedaringcreatives.com/creator-stories/neural-viz-ai-tv-universe/))
- **Total Pixel Space** won the 2025 Runway AIFF Grand Prix as a *narrated essay*
  film — voice + ideas + evolving imagery, no complex acting required.
  ([Artnet](https://news.artnet.com/art-world/total-pixel-space-jacob-adler-a-i-film-festival-2662774))
- **Takeaway for Twist Villa:** narrator-led storytelling, sparse dialogue shot to
  avoid heavy lip-sync, a stylised grade and grain, and "presences" (systems,
  screens, voices) as characters.

### 3. A frame device holds long runtimes together
- **Oneiric** (~20 min) uses a simple frame — four students and a "plug your mind
  anywhere" technology — then plays each fantasy as a genre vignette, ending on the
  emotional one (one friend just wants one more day together).
  ([Higgsfield](https://higgsfield.ai/original-series/oneiric/full-film),
  [The Awesomer](https://theawesomer.com/oneiric-short-film/812730/))
- **Takeaway:** a clear "rule of the world" + episodic investigation beats + an
  emotional final turn. Save the most human beat for last.

### 4. The proven human-made benchmark: idea-first near-future thrillers
- **DUST**'s most-viewed film, **Nano** (14 min, 38M+ views, 3rd-party figure), is a
  near-future "one law changes society" thriller. DUST's catalogue (3–20 min) is
  consistently "Black Mirror"-like: one technology, one moral cost.
  ([Wikitubia](https://youtube.fandom.com/wiki/DUST))
- DUST now also distributes films labelled **"DUST AI"** — the biggest sci-fi shorts
  channel treats AI-made films as legitimate programming.
- **Takeaway:** "one new technology / rule → personal moral cost → twist" is the
  proven premise shape for this audience.

### 5. Packaging patterns (titles)
- Genre-labelled titles are the norm: `Sci-Fi Short Film "Nano" | DUST`,
  `Oneiric | AI Sci-Fi Short Film | …`.
- Twist-promise titles are rising: "This Sci-Fi AI Film Has a Brutal Twist – SUPPLY".
- **Takeaway:** title = intriguing name + genre tag; the *promise of a twist* is a
  selling point, but it must be honest.

### 6. Risk zone: mass-produced narration channels
- Long narrated sci-fi (HFY) channels with AI visuals show demand for 20–40 min
  story content — but this is exactly what YouTube's **"inauthentic content"** rule
  (YPP update, 15 Jul 2025) targets: templated, mass-produced narration with
  superficial variation or slideshows.
  ([Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/),
  [YouTube Help](https://support.google.com/youtube/answer/1311392?hl=en))
- **Takeaway:** fewer, better films. Real motion footage, original stories, visible
  authorship (a consistent Twist Villa voice and world).

## Per-dimension summary (patterns to adopt)

| Dimension | Pattern to adopt | Source signal |
|---|---|---|
| Opening hook | Cold open from late in the story; question in the first 15 s | Genre norm; retention logic |
| Structure | Rule → break → investigation → midpoint flip → twist → mirror ending | DUST, Oneiric |
| Pacing | Mini-cliffhanger every 3–4 min; average shot ~5 s | IndieWire jury on "long-feeling" films |
| Characters | Small cast; stylised or partly-obscured faces; one voice carries it | Neural Viz, Hell Grind criticism |
| Visual style | Consistent grade + grain; locked locations; real motion | Neural Viz, The Frost (stills look dated) |
| Narration | First-person, intimate, human-sounding; consistent accents | Hell Grind voice criticism |
| Sound | Leitmotif, room tone, music drops before reveals | Craft best-practice |
| Title/thumbnail | Name + genre tag; honest twist promise; one image, one idea | DUST, Beyond Frames |
| Ending | Final image re-frames the opening → re-watch value | Twist-genre convention |

## What we will NOT copy
No premises, characters, names, dialogue, footage, or signature images from any
video above. No "plug your mind into any time" frame (Oneiric), no nanotech-law
premise (Nano), no simulated-alien-prison premise (Simulation).

## Next research step
Add `YOUTUBE_API_KEY`, then run `python -m studio research-stats` to fill every
`pending` field and compute **views per day since publish** and **ratio to the
channel's median of its last 30 uploads** — the fair way to compare videos of
different ages and channel sizes.
