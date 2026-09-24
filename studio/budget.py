"""Cost estimates, owner approvals, and the spend guard.

Every paid API call must go through SpendGuard.charge(). It refuses to spend unless the
owner's approval for that project+stage is recorded and all caps in config/budget.yaml hold.
"""
from __future__ import annotations

import csv
import datetime as dt
import math

from . import config

STAGES = ("refs", "pilot", "footage", "audio", "thumbnail")
LEDGER_FIELDS = ["timestamp", "slug", "stage", "provider", "usd", "note"]


class BudgetError(SystemExit):
    pass


# ---------------------------------------------------------------- estimates

def _prices() -> dict:
    p = config.providers()["providers"]
    return {
        "video": p["video"]["api_optional"]["usd_per_second"],
        "clip_seconds": p["video"]["api_optional"]["clip_seconds"],
        "image": p["images"]["usd_per_image"],
        "tts_per_token": p["narration_and_dialogue"]["primary"]["usd_per_million_output_tokens"] / 1e6,
        "music": float(p["music"]["primary"].get("cost", p["music"]["primary"].get("usd_per_track", 0))),
    }


def _est() -> dict:
    defaults = {"retake_rate": 0.3, "refs_images_per_character": 4, "refs_images_per_location": 3,
                "thumbnail_candidates": 6, "pilot_seconds": 60, "words_per_minute": 140,
                "tts_tokens_per_second": 25}
    defaults.update(config.budget().get("estimation", {}))
    return defaults


def _shots_cost(shots: list[dict], prices: dict, retake: float) -> tuple[float, float]:
    seconds = 0.0
    usd = 0.0
    for shot in shots:
        gen = prices["clip_seconds"] * max(1, math.ceil(float(shot["seconds"]) / prices["clip_seconds"]))
        seconds += gen
        usd += gen * prices["video"][shot.get("tier", "standard")]
    return seconds * (1 + retake), usd * (1 + retake)


def estimate(slug: str, stage: str) -> dict:
    """Return {'usd': float, 'detail': str} for one stage of one project."""
    if stage not in STAGES:
        raise BudgetError(f"Unknown stage {stage!r}. Stages: {', '.join(STAGES)}")
    pdir = config.project_dir(slug)
    prices, est = _prices(), _est()
    retake = est["retake_rate"]

    if stage == "refs":
        bible = config.load_yaml(pdir / "bible.yaml")
        n = (len(bible.get("characters", [])) * est["refs_images_per_character"]
             + len(bible.get("locations", [])) * est["refs_images_per_location"])
        usd = n * prices["image"] * (1 + retake)
        return {"usd": round(usd, 2), "detail": f"{n} reference images × ${prices['image']} (+{retake:.0%} retakes)"}

    if stage == "thumbnail":
        n = est["thumbnail_candidates"]
        return {"usd": round(n * prices["image"], 2), "detail": f"{n} thumbnail candidates × ${prices['image']}"}

    board = config.load_yaml(pdir / "storyboard.yaml")
    shots = board.get("shots", [])

    if stage in ("pilot", "footage"):
        if stage == "pilot":
            picked, total = [], 0.0
            for shot in shots:
                if total >= est["pilot_seconds"]:
                    break
                picked.append(shot)
                total += float(shot["seconds"])
            shots = picked
        gen_s, usd = _shots_cost(shots, prices, retake)
        runtime = sum(float(s["seconds"]) for s in shots)
        return {"usd": round(usd, 2),
                "detail": f"{len(shots)} shots, {runtime:.0f} s on screen, ~{gen_s:.0f} s generated "
                          f"(Veo hero ${prices['video']['hero']}/s, standard ${prices['video']['standard']}/s, "
                          f"+{retake:.0%} retakes)"}

    # audio
    lines = board.get("audio", {}).get("lines", [])
    words = sum(len(str(l.get("text", "")).split()) for l in lines)
    speech_s = words / est["words_per_minute"] * 60
    tts = speech_s * est["tts_tokens_per_second"] * prices["tts_per_token"] * (1 + retake) * 3  # ×3 voice takes
    tracks = len(board.get("audio", {}).get("music", []))
    music = tracks * prices["music"] * (1 + retake) * 2  # ×2 candidates per cue
    return {"usd": round(tts + music, 2),
            "detail": f"{words} words (~{speech_s:.0f} s speech, 3 takes) + {tracks} music cues "
                      f"(${prices['music']}/track)"}


# ---------------------------------------------------------------- approvals

def _approvals_path(slug: str):
    return config.project_dir(slug) / "approvals.yaml"


def approvals(slug: str) -> list[dict]:
    path = _approvals_path(slug)
    return config.load_yaml(path).get("approvals", []) if path.exists() else []


def record_approval(slug: str, stage: str, usd: float, note: str = "") -> None:
    """Call ONLY after the owner explicitly approved this amount for this stage."""
    if stage not in STAGES:
        raise BudgetError(f"Unknown stage {stage!r}")
    caps = config.budget()["caps"]
    committed = sum(a["usd"] for a in approvals(slug) if a["stage"] != stage) + usd
    if committed > caps["per_video_usd"]:
        raise BudgetError(f"Approvals for {slug} would total ${committed:.2f}, above the per-video cap "
                          f"${caps['per_video_usd']}. Raise the cap in config/budget.yaml first (owner decision).")
    items = [a for a in approvals(slug) if a["stage"] != stage]
    items.append({"stage": stage, "usd": round(float(usd), 2),
                  "approved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                  "note": note})
    config.save_yaml(_approvals_path(slug), {"approvals": items})


# ---------------------------------------------------------------- ledger

def ledger() -> list[dict]:
    if not config.LEDGER.exists():
        return []
    with open(config.LEDGER, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _append_ledger(row: dict) -> None:
    new = not config.LEDGER.exists()
    with open(config.LEDGER, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow(row)


def spent(slug: str | None = None, stage: str | None = None, month: str | None = None) -> float:
    total = 0.0
    for row in ledger():
        if slug and row["slug"] != slug:
            continue
        if stage and row["stage"] != stage:
            continue
        if month and not row["timestamp"].startswith(month):
            continue
        total += float(row["usd"])
    return total


class SpendGuard:
    """Gatekeeper for one project stage. Use: guard = SpendGuard(slug, stage); guard.charge(usd, ...)."""

    def __init__(self, slug: str, stage: str):
        self.slug, self.stage = slug, stage
        self.caps = config.budget()["caps"]
        self.tolerance = config.budget()["approval"]["overrun_tolerance_pct"] / 100
        match = [a for a in approvals(slug) if a["stage"] == stage]
        if not match:
            raise BudgetError(f"No owner approval recorded for {slug} / {stage}. "
                              f"Run `python -m studio estimate {slug} --stage {stage}`, show the owner, "
                              "and record approval only after they say yes.")
        self.approved = float(match[0]["usd"])

    def charge(self, usd: float, provider: str, note: str = "") -> None:
        """Check all limits, then log the spend. Call immediately BEFORE submitting a paid request."""
        month = dt.date.today().strftime("%Y-%m")
        checks = [
            (usd <= self.caps["single_call_usd"],
             f"single call ${usd:.2f} exceeds single_call_usd ${self.caps['single_call_usd']}"),
            (spent(self.slug, self.stage) + usd <= self.approved * (1 + self.tolerance),
             f"stage {self.stage} would exceed its approved ${self.approved:.2f} (+{self.tolerance:.0%})"),
            (spent(self.slug) + usd <= self.caps["per_video_usd"],
             f"project would exceed per_video_usd ${self.caps['per_video_usd']}"),
            (spent(month=month) + usd <= self.caps["per_month_usd"],
             f"month {month} would exceed per_month_usd ${self.caps['per_month_usd']}"),
        ]
        for ok, message in checks:
            if not ok:
                raise BudgetError(f"STOPPED — {message}. Ask the owner before continuing.")
        _append_ledger({"timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                        "slug": self.slug, "stage": self.stage, "provider": provider,
                        "usd": f"{usd:.4f}", "note": note})
