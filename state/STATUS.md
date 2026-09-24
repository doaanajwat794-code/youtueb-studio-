# Twist Villa Studio — Status

**Last updated:** 2026-09-24 · **Format:** YouTube Shorts (55–60 s, 9:16, 1080x1920)
**Production model:** owner generates footage in **Google Flow** from Claude's prompts; ShortsFaceless
only for narration (optional). Extra spend target **$0**.
**Phase:** 1 — Pick the first Short · **Active Short:** none yet

## Next pending task
**Owner picks one of the 3 ideas** in `state/ideas-backlog.md` (recommended: #1 "Face Not Recognized"),
and answers 3 quick choices:
1. Flow model mix: all Fast (≈300 credits) or hook + twist on Quality (≈540 credits)?
2. Hand-off: a Google Drive shared folder (needs a free `GOOGLE_API_KEY`) or Claude Code on your computer?
3. Narration A/B: try the ShortsFaceless voice and/or the free Google voice and/or your own voice?

Then Claude does (all free), in order:
1. `python -m studio new "<title>" --code XXX`, then the screenplay (`script.md`, 58 s, 110–130 words)
2. Bible: character references (young/old looks), locations, look, voice → `bible.yaml`
3. Storyboard: 11 shots with timed narration → `storyboard.yaml`
4. `python -m studio flow-prompts <slug>` → `flow-prompts.md` (copy-paste prompts, file names, credits) + `narration.txt`
5. Owner generates in Flow → hand-off → `import-clips` → narration → music/SFX → `assemble` → cover → private upload (with approval)

## Done
- 2026-09-23 · Initial long-form setup. **Archived** 2026-09-24 → `archive/longform/`.
- 2026-09-24 · Pivot to Shorts (config, Skill, framework, research, templates).
- 2026-09-24 · Shorts research saved (`research/shorts-research.md`, `research/shorts-sources.yaml`).
- 2026-09-24 · ShortsFaceless investigated (web only): no public API; animated stills, so not usable for footage.
- 2026-09-24 · **Switched to the Google Flow manual workflow** (owner-approved): new commands
  `flow-prompts`, `import-clips`, `fetch-drive`, `import-voice`, `thumbnail`; owner guide
  `.claude/skills/twist-villa-studio/references/flow-handoff.md`; paid Veo API disabled.
- 2026-09-24 · **Tested (free, offline selftest, 15 checks):** Flow prompt sheet, clip import (naming,
  latest take chosen, stray files ignored), one-recording narration split into lines, 1080x1920
  export, audio, A/V sync ±0.10 s, runtime, burned captions, cover image, duplicate-footage rejection,
  budget-guard refusals.

## Integration test status
| Integration | Status |
|---|---|
| FFmpeg assembly (vertical), mix, burned captions, sync check, cover | ✅ TESTED with synthetic media |
| Flow prompt sheet + clip import + narration split | ✅ TESTED with synthetic files · ⏳ first real Flow clips pending |
| Google Drive folder download (`fetch-drive`) | ⏳ UNTESTED — needs a free GOOGLE_API_KEY + a shared folder |
| ShortsFaceless voice export → import-voice | ⏳ UNTESTED — does the export allow music off? |
| Gemini TTS free tier (narration option 2) | ⏳ UNTESTED — needs a free GEMINI_API_KEY |
| YouTube private upload (OAuth) | ⏳ UNTESTED — or the owner uploads manually in YouTube Studio |
| Veo API | ⛔ DISABLED by the owner (Flow is used instead) |

## Blockers / environment notes
- The cloud environment can't open youtube.com, Flow, or ShortsFaceless websites; it can reach
  `www.googleapis.com` (Drive/YouTube APIs). The Drive *connector* can't transfer large videos,
  hence the shared-folder + API-key method, or local Claude Code.
- Container storage is temporary: copy finished Shorts to Google Drive.
- Repo: the only branch, `claude/gracious-feynman-hiut4e`, is also the GitHub **default branch**,
  so new sessions load these files without any merge.

## Spend to date
$0.00 (see `state/spend-ledger.csv`) · Safety caps $5/Short, $20/month (only with approval)
