"""Command line: python -m studio <command> ..."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re

from . import budget, config


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48]


def cmd_status(_):
    print((config.STATE / "STATUS.md").read_text(encoding="utf-8"))
    month = dt.date.today().strftime("%Y-%m")
    caps = config.budget()["caps"]
    print(f"\nSpend this month: ${budget.spent(month=month):.2f} of ${caps['per_month_usd']} cap")


def cmd_new(args):
    slug = _slugify(args.title)
    pdir = config.project_dir(slug)
    if pdir.exists():
        raise SystemExit(f"Project {slug} already exists")
    template = config.PROJECTS / "_template"
    pdir.mkdir(parents=True)
    for f in template.iterdir():
        (pdir / f.name).write_text(f.read_text(encoding="utf-8").replace("{{title}}", args.title)
                                   .replace("{{slug}}", slug), encoding="utf-8")
    code = (args.code or "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", args.title))[:4]).upper()
    config.save_yaml(pdir / "project.yaml", {"title": args.title, "slug": slug, "code": code,
                                             "stage": "idea", "created": dt.date.today().isoformat()})
    print(f"Created projects/{slug}/ (clip code {code})")


def cmd_estimate(args):
    stages = budget.STAGES if args.stage == "all" else [args.stage]
    total = 0.0
    for stage in stages:
        try:
            e = budget.estimate(args.slug, stage)
        except FileNotFoundError as exc:
            print(f"{stage:10} (skipped: {exc.filename} not written yet)")
            continue
        if stage == "pilot" and args.stage == "all":
            print(f"{stage:10} ${e['usd']:>8.2f}  (subset of footage; not added)  {e['detail']}")
            continue
        total += e["usd"]
        print(f"{stage:10} ${e['usd']:>8.2f}  {e['detail']}")
    if len(stages) > 1:
        print(f"{'TOTAL':10} ${total:>8.2f}  (excluding pilot)")


def cmd_approve(args):
    budget.record_approval(args.slug, args.stage, args.usd, note=args.note or "")
    print(f"Recorded owner approval: {args.slug} / {args.stage} up to ${args.usd:.2f}")


def cmd_generate(args):
    from . import produce

    fn = {"refs": produce.refs, "pilot": lambda s: produce.footage(s, "pilot"),
          "footage": produce.footage, "audio": produce.audio}[args.stage]
    print(f"Generated {fn(args.slug)} new files for {args.slug} / {args.stage}")


def cmd_assemble(args):
    from .assemble import assemble

    print(json.dumps(assemble(args.slug), indent=2))


def cmd_flow_prompts(args):
    from .flow import write_prompt_sheet

    print(f"Wrote {write_prompt_sheet(args.slug)}")


def cmd_import_clips(args):
    from pathlib import Path

    from .flow import import_clips

    src = Path(args.source) if args.source else config.media_dir(args.slug) / "incoming"
    picks = {k.upper(): int(v.lstrip("vV")) for k, v in (p.split("=") for p in args.pick or [])}
    print("\n".join(import_clips(args.slug, src, picks)))


def cmd_fetch_drive(args):
    from .flow import fetch_drive_folder

    files = fetch_drive_folder(args.slug, args.folder_id)
    print(f"Downloaded {len(files)} files to media/{args.slug}/incoming/")


def cmd_import_voice(args):
    from pathlib import Path

    from .voice import import_narration

    print("\n".join(import_narration(args.slug, Path(args.file), noise_db=args.noise, speaker=args.speaker)))


def cmd_thumbnail(args):
    from .thumbnail import make_thumbnail

    print(f"Wrote {make_thumbnail(args.slug, args.at, args.text or '')}")


def cmd_make_sfx(args):
    from .sfx import make_sfx

    print("Wrote: " + ", ".join(make_sfx(args.slug)))


def cmd_selftest(_):
    from .selftest import run_selftest

    results = run_selftest()
    print("\n".join(results))
    if any(r.startswith("FAIL") for r in results):
        raise SystemExit(1)


def cmd_research_stats(_):
    from .youtube import refresh_research_stats

    for v in refresh_research_stats():
        print(f"{v.get('views', '?'):>12}  {v.get('views_per_day', '?'):>9}/day  "
              f"x{v.get('vs_channel_median', '?')} vs channel  {v['title'][:60]}")


def cmd_youtube_auth(args):
    from pathlib import Path

    from .youtube import authorize_interactively

    token = authorize_interactively(Path(args.client_secrets))
    print("\nStore this as the secret YOUTUBE_REFRESH_TOKEN (never commit it):\n")
    print(token)


def cmd_upload(args):
    from .youtube import upload_private

    vid = upload_private(args.slug)
    print(f"Uploaded PRIVATE: https://studio.youtube.com/video/{vid}/edit")


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio", description="Twist Villa Studio pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="show saved status and this month's spend").set_defaults(fn=cmd_status)
    s = sub.add_parser("new", help="create a new Short project")
    s.add_argument("title")
    s.add_argument("--code", help="2–4 letter clip code, e.g. FNR")
    s.set_defaults(fn=cmd_new)
    s = sub.add_parser("estimate", help="estimate cost of a stage (free)")
    s.add_argument("slug")
    s.add_argument("--stage", default="all", choices=[*budget.STAGES, "all"])
    s.set_defaults(fn=cmd_estimate)
    s = sub.add_parser("approve", help="record the OWNER's approval for a paid stage")
    s.add_argument("slug")
    s.add_argument("--stage", required=True, choices=budget.STAGES)
    s.add_argument("--usd", required=True, type=float)
    s.add_argument("--note")
    s.set_defaults(fn=cmd_approve)
    s = sub.add_parser("generate", help="run a PAID stage (requires approval)")
    s.add_argument("slug")
    s.add_argument("--stage", required=True, choices=["refs", "pilot", "footage", "audio"])
    s.set_defaults(fn=cmd_generate)
    s = sub.add_parser("assemble", help="edit, mix, caption and export final.mp4 (free)")
    s.add_argument("slug")
    s.set_defaults(fn=cmd_assemble)
    s = sub.add_parser("flow-prompts", help="write projects/<slug>/flow-prompts.md for Google Flow (free)")
    s.add_argument("slug")
    s.set_defaults(fn=cmd_flow_prompts)
    s = sub.add_parser("import-clips", help="import Flow clips named CODE_SNN_vN.mp4 (free)")
    s.add_argument("slug")
    s.add_argument("--from", dest="source", help="folder with clips (default media/<slug>/incoming)")
    s.add_argument("--pick", nargs="*", help="choose takes, e.g. S03=v1 S07=v2 (default: highest take)")
    s.set_defaults(fn=cmd_import_clips)
    s = sub.add_parser("fetch-drive", help="download a link-shared Google Drive folder into incoming/")
    s.add_argument("slug")
    s.add_argument("folder_id")
    s.set_defaults(fn=cmd_fetch_drive)
    s = sub.add_parser("import-voice", help="split one narration recording into storyboard lines")
    s.add_argument("slug")
    s.add_argument("file")
    s.add_argument("--noise", type=float, default=-35, help="silence threshold in dB")
    s.add_argument("--speaker", help="only lines of this speaker, e.g. narrator or theo")
    s.set_defaults(fn=cmd_import_voice)
    s = sub.add_parser("thumbnail", help="vertical cover from a frame of final.mp4 (free)")
    s.add_argument("slug")
    s.add_argument("--at", type=float, default=1.0, help="time in seconds")
    s.add_argument("--text", help="up to 3 words")
    s.set_defaults(fn=cmd_thumbnail)
    s = sub.add_parser("make-sfx", help="synthesise original UI/cinematic sound effects (free)")
    s.add_argument("slug")
    s.set_defaults(fn=cmd_make_sfx)
    sub.add_parser("selftest", help="offline end-to-end test with fake media (free)").set_defaults(fn=cmd_selftest)
    sub.add_parser("research-stats", help="fill research/sources.yaml from the YouTube API") \
        .set_defaults(fn=cmd_research_stats)
    s = sub.add_parser("youtube-auth", help="one-time OAuth on your own computer")
    s.add_argument("client_secrets")
    s.set_defaults(fn=cmd_youtube_auth)
    s = sub.add_parser("upload", help="upload final.mp4 as PRIVATE")
    s.add_argument("slug")
    s.set_defaults(fn=cmd_upload)
    args = p.parse_args(argv)
    args.fn(args)
