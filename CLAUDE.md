# Twist Villa Studio — project memory

This repository is the production studio for the YouTube channel **Twist Villa**
(https://www.youtube.com/@TwistVela).

**Current format: YouTube Shorts ONLY.** Each Short is 55–60 seconds, 9:16, 1080x1920,
in English: realistic AI-generated moving footage with consistent characters, natural movement,
strong opening hooks, and unexpected endings, plus original narration, SFX, music, captions
and cinematic editing. Genres: cinematic mystery, science fiction, psychological thriller,
technology and human identity.

**Production model (approved 2026-09-24):** use the owner's existing subscriptions.
- **Google Flow** (paid subscription): the owner generates every clip manually from Claude's
  `flow-prompts.md` and hands the files back. **No paid video API. Never ask the owner to
  buy a Veo API plan.**
- **ShortsFaceless** (30 videos/month): only where it genuinely helps (e.g. the narration
  voice). **Never** use its animated still images as footage.
- Claude does research, ideas, scripts, storyboards, Flow prompts, import, edit, narration,
  SFX, music, captions, export, and the title/description/hashtags/cover.

**Long-form is archived** (`archive/longform/`). Never produce long-form, and never use
the archived files as the main reference, unless the owner explicitly asks.

The owner is not a software developer. Explain in plain language, keep answers
structured and specific, and never make them re-explain what is already saved here.

## Start of every session (mandatory)

Use the `twist-villa-studio` skill for any work in this repo. Before anything else, read:

1. `state/STATUS.md` — current phase, active Short, and the **next pending task**
2. `config/channel.yaml` — channel identity and Shorts format
3. `config/budget.yaml` — extra-spend target $0; approval rules
4. `state/decisions.md` — permanent decisions the owner already approved

Then continue from the next pending task in `state/STATUS.md`. Read
`config/storytelling-framework.md`, `config/providers.yaml` (subscriptions + render settings),
`research/shorts-research.md`, `state/ideas-backlog.md`, and the Skill's
`references/flow-handoff.md` when the task touches them.

## Hard rules

- **Money:** use the existing subscriptions. Never buy a subscription or call a paid API
  without the owner's explicit approval of a written cost estimate for that step. Every spend is logged in `state/spend-ledger.csv`.
  The code enforces this (`studio/budget.py`); never bypass or weaken the guard.
- **Publishing:** uploads are always `private`. Never make a video public, unlisted,
  or scheduled without explicit owner approval in the current conversation.
- **Secrets:** API keys and OAuth tokens live in `.env` / environment secrets / the
  user config dir — never in git. Never print a key into a file that is committed.
- **Media:** rendered video, audio and images go in `media/` (git-ignored) and then to
  external storage (Google Drive). Only code, config, scripts and text go in git.
- **Honesty:** do not claim an integration works until it has been run and verified.
  Mark anything untested as `UNTESTED`. Do not invent view counts or analytics.
- **Originality:** learn patterns from references; never copy their scripts,
  characters, footage, or distinctive storylines.
- **Permanent changes:** when the owner approves a permanent change, update the
  relevant `config/` file, add a dated line to `state/decisions.md`, and commit.

## Layout

- `.claude/skills/twist-villa-studio/` — the Skill (Shorts workflow + reference guides)
- `config/` — approved channel, Shorts framework, provider/render, and budget settings
- `research/` — Shorts research and tool/pricing research with source links
- `state/` — status, pending tasks, ideas backlog, decisions log, spend ledger
- `projects/<slug>/` — per-Short text assets (idea, script, bible, storyboard, metadata)
- `studio/` — Python pipeline (`python -m studio --help`)
- `archive/longform/` — inactive long-form research and settings
- `media/` — large generated files (git-ignored)
