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
    config.save_yaml(pdir / "project.yaml", {"title": args.title, "slug": slug, "stage": "idea",
                                             "created": dt.date.today().isoformat()})
    print(f"Created projects/{slug}/")


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
    s = sub.add_parser("new", help="create a new video project")
    s.add_argument("title")
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
