"""Google Flow hand-off: printable prompt sheets, clip import, and Drive download.

The owner generates clips manually in Google Flow (existing subscription, no API cost).
This module turns the storyboard into copy-paste prompts and imports the returned clips.

Clip file names:  <CODE>_S<NN>_v<N>.mp4   e.g.  FNR_S03_v2.mp4
  CODE = project code in project.yaml, NN = shot number, N = take number (optional).
"""
from __future__ import annotations

import math
import re
import shutil
from pathlib import Path

import requests

from . import config
from .media_tools import probe, sha256
from .produce import compose_shot_prompt

CLIP_RE = re.compile(r"^(?P<code>[A-Za-z0-9]+)[_-]S(?P<shot>\d{2})(?:[_-]v(?P<ver>\d+))?\.(mp4|mov|webm|m4v)$",
                     re.IGNORECASE)
AUDIO_RULE = ("Audio: natural ambient sound and diegetic sound effects only. "
              "No music, no narration, no dialogue, no voices.")
TEXT_RULE = "No on-screen text, no subtitles, no captions, no logos, no watermarks."


class ImportError_(SystemExit):
    pass


def _project(slug: str) -> dict:
    return config.load_yaml(config.project_dir(slug) / "project.yaml")


def _flow_cfg() -> dict:
    return config.providers()["providers"]["video"]["primary"]


# ------------------------------------------------------------------ prompt sheet

def flow_prompt(shot: dict, bible: dict) -> str:
    """One copy-paste prompt for Flow: story prompt + locks + vertical framing + audio/text rules."""
    return " ".join([compose_shot_prompt(shot, bible),
                     "Vertical 9:16 composition, subject in the upper two-thirds of the frame.",
                     AUDIO_RULE, TEXT_RULE])


def credits_estimate(shots: list[dict]) -> dict:
    cfg = _flow_cfg()
    per = cfg["credits_per_generation"]
    retake = config.budget().get("estimation", {}).get("retake_rate", 0.3)
    gens = {"quality": 0, "fast": 0}
    for s in shots:
        gens["quality" if s.get("tier") == "hero" else "fast"] += 1
    credits = sum(math.ceil(n * (1 + retake)) * per[k] for k, n in gens.items())
    return {"generations": gens, "credits": credits, "retake_rate": retake,
            "per_generation": per}


def write_prompt_sheet(slug: str) -> Path:
    pdir = config.project_dir(slug)
    board = config.load_yaml(pdir / "storyboard.yaml")
    bible = config.load_yaml(pdir / "bible.yaml")
    code = _project(slug).get("code", "TV")
    shots = board["shots"]
    est = credits_estimate(shots)
    lines = [f"# Google Flow prompt sheet: {_project(slug).get('title', slug)}", "",
             "Generated from `storyboard.yaml` + `bible.yaml`. Don't edit by hand; change the storyboard",
             "and run `python -m studio flow-prompts " + slug + "` again.", "",
             "## Flow settings for every clip",
             "- **Aspect ratio:** 9:16 (portrait) · **Duration:** 8 s · **Outputs per prompt:** 1",
             "- **Model:** *Quality* for ⭐ hero shots, *Fast* for all others",
             "- **Download:** the highest resolution offered (1080p if available)",
             f"- **File name:** `{code}_S<NN>_v<take>.mp4`, e.g. `{code}_S01_v1.mp4` (rename after download)",
             "",
             f"**Credit estimate:** {est['generations']['quality']} Quality + {est['generations']['fast']} Fast shots "
             f"≈ **{est['credits']} credits** including {est['retake_rate']:.0%} retakes "
             f"(Quality {est['per_generation']['quality']}, Fast {est['per_generation']['fast']} credits each, "
             "web-reported; check the credit number Flow shows before you click).", ""]

    chars = bible.get("characters", [])
    locs = bible.get("locations", [])
    if chars or locs:
        lines += ["## Step 1: Reference images (make once, reuse as *Ingredients* in every clip)", ""]
        style = bible.get("look", {}).get("style_lock", "")
        for c in chars:
            for view in c.get("ref_views", ["front portrait", "three-quarter view", "full body"]):
                fname = f"{code}_REF_{c['id'].upper()}_{view.split()[0].upper()}.png"
                lines += [f"**{fname}**: {c['name']}, {view}", "```",
                          f"Character reference photo, {view}, plain neutral grey background, soft even light. "
                          f"{c['visual_lock']} {style}", "```", ""]
        for l in locs:
            fname = f"{code}_REF_{l['id'].upper()}.png"
            lines += [f"**{fname}**: {l['name']}", "```",
                      f"Location plate, vertical 9:16, no people. {l['visual_lock']} {style}", "```", ""]

    lines += ["## Step 2: Clips (generate in this order)", ""]
    t = 0.0
    for shot in shots:
        star = "⭐ Quality" if shot.get("tier") == "hero" else "Fast"
        mode = shot.get("flow_mode", "Ingredients to Video" if shot.get("characters") else "Text to Video")
        ingredients = [f"{code}_REF_{c.upper()}_FRONT.png" for c in shot.get("characters", [])]
        if shot.get("location"):
            ingredients.append(f"{code}_REF_{shot['location'].upper()}.png")
        lines += [f"### {shot['id']} · {shot.get('beat', '').upper()} · {t:.1f}–{t + float(shot['seconds']):.1f} s "
                  f"(uses {shot['seconds']} s of the 8 s clip)",
                  f"- **Save as:** `{code}_{shot['id']}_v1.mp4` · **Model:** {star} · **Mode:** {mode}"]
        if mode != "Text to Video" and ingredients:
            lines.append(f"- **Ingredients:** {', '.join(ingredients[:3])}")
        if shot.get("flow_notes"):
            lines.append(f"- **Note:** {shot['flow_notes']}")
        lines += ["```", flow_prompt(shot, bible), "```",
                  "- [ ] Face/wardrobe match the reference · [ ] vertical · [ ] no text/warping · [ ] real motion", ""]
        t += float(shot["seconds"])
    out = pdir / "flow-prompts.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    # narration script for ShortsFaceless / self-recording: one line per paragraph = one pause
    narration = [str(l["text"]).strip() for l in board.get("audio", {}).get("lines", [])]
    (pdir / "narration.txt").write_text("\n\n".join(narration) + "\n", encoding="utf-8")
    return out


# ------------------------------------------------------------------ import

def import_clips(slug: str, src: Path, picks: dict[str, int] | None = None) -> list[str]:
    """Copy owner-provided Flow clips from `src` into media/<slug>/shots/<shot>.mp4 with checks."""
    picks = picks or {}
    board = config.load_yaml(config.project_dir(slug) / "storyboard.yaml")
    code = _project(slug).get("code", "TV").upper()
    render = config.providers()["render"]
    wanted = {s["id"]: s for s in board["shots"]}
    found: dict[str, dict[int, Path]] = {}
    report, skipped = [], []
    for f in sorted(Path(src).rglob("*")):
        m = CLIP_RE.match(f.name)
        if not f.is_file() or not m:
            if f.is_file():
                skipped.append(f.name)
            continue
        if m["code"].upper() != code:
            skipped.append(f"{f.name} (code is not {code})")
            continue
        found.setdefault(f"S{m['shot']}", {})[int(m["ver"] or 1)] = f

    dest = config.media_dir(slug) / "shots"
    dest.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for sid, shot in wanted.items():
        takes = found.get(sid)
        if not takes:
            report.append(f"MISSING  {sid}: expected {code}_{sid}_v1.mp4")
            continue
        ver = picks.get(sid, max(takes))
        if ver not in takes:
            raise ImportError_(f"{sid}: take v{ver} not found (have {sorted(takes)})")
        f = takes[ver]
        info = probe(f)
        need = float(shot.get("trim_start", 0)) + float(shot["seconds"])
        notes = []
        if not info["has_video"]:
            report.append(f"BAD      {sid}: {f.name} has no video stream")
            continue
        if info["width"] >= info["height"]:
            notes.append(f"NOT VERTICAL ({info['width']}x{info['height']}); regenerate in 9:16")
        elif info["width"] < render["width"]:
            notes.append(f"{info['width']}x{info['height']} will be upscaled to "
                         f"{render['width']}x{render['height']} (download 1080p if Flow offers it)")
        if info["duration"] + 0.05 < need:
            notes.append(f"too short: {info['duration']:.1f}s < {need:.1f}s needed")
        digest = sha256(f)
        if digest in hashes:
            notes.append(f"identical file to {hashes[digest]} (repeated footage)")
        hashes[digest] = sid
        shutil.copy2(f, dest / f"{sid}.mp4")
        status = "WARN    " if notes else "OK      "
        report.append(f"{status} {sid}: {f.name} (take v{ver} of {sorted(takes)}, {info['duration']:.1f}s, "
                      f"{info['width']}x{info['height']}, audio={'yes' if info['has_audio'] else 'no'})"
                      + (f" | {'; '.join(notes)}" if notes else ""))
    extra = sorted(set(found) - set(wanted))
    if extra:
        report.append(f"IGNORED  clips for shots not in the storyboard: {', '.join(extra)}")
    if skipped:
        report.append(f"IGNORED  files not matching {code}_SNN_vN.mp4: {', '.join(skipped[:10])}")
    return report


# ------------------------------------------------------------------ Google Drive (shared folder)

def fetch_drive_folder(slug: str, folder_id: str) -> list[Path]:
    """Download every file from a Drive folder shared as 'Anyone with the link: Viewer'.

    STATUS: UNTESTED. Uses the Drive API v3 with GOOGLE_API_KEY (free key with the Drive API
    enabled). No OAuth and no password needed; the owner can un-share the folder afterwards.
    """
    key = config.secret("GOOGLE_API_KEY")
    api = "https://www.googleapis.com/drive/v3/files"
    out = config.media_dir(slug) / "incoming"
    out.mkdir(parents=True, exist_ok=True)
    files, token = [], None
    while True:
        params = {"q": f"'{folder_id}' in parents and trashed = false", "key": key,
                  "fields": "nextPageToken, files(id, name, size, mimeType)", "pageSize": 200}
        if token:
            params["pageToken"] = token
        r = requests.get(api, params=params, timeout=60)
        if r.status_code >= 400:
            raise SystemExit(f"Drive API {r.status_code}: {r.text[:400]} — is the folder shared as "
                             "'Anyone with the link' and the Drive API enabled for the key?")
        data = r.json()
        files += data.get("files", [])
        token = data.get("nextPageToken")
        if not token:
            break
    saved = []
    for f in files:
        if f["mimeType"] == "application/vnd.google-apps.folder":
            continue
        dest = out / f["name"]
        if dest.exists() and f.get("size") and dest.stat().st_size == int(f["size"]):
            saved.append(dest)
            continue
        with requests.get(f"{api}/{f['id']}", params={"alt": "media", "key": key}, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        saved.append(dest)
    return saved
