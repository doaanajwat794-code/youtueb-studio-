"""Paid generation stages. Each stage needs a recorded owner approval (see budget.SpendGuard).

Files already on disk are skipped, so an interrupted stage resumes without paying twice.
"""
from __future__ import annotations

from . import config
from .budget import SpendGuard
from .providers import google


def _bible(slug: str) -> dict:
    return config.load_yaml(config.project_dir(slug) / "bible.yaml")


def compose_shot_prompt(shot: dict, bible: dict) -> str:
    """Shot prompt + locked character/location descriptions + global look = continuity."""
    chars = {c["id"]: c for c in bible.get("characters", [])}
    locs = {l["id"]: l for l in bible.get("locations", [])}
    parts = [shot["prompt"].strip()]
    if shot.get("camera"):
        parts.append(f"Camera: {shot['camera']}.")
    for cid in shot.get("characters", []):
        c = chars[cid]
        parts.append(f"{c.get('prompt_name', c['name'])}: {c['visual_lock']}")
    if shot.get("location"):
        loc = locs[shot["location"]]
        parts.append(f"Location — {loc['name']}: {loc['visual_lock']}")
    look = bible.get("look", {})
    if look.get("style_lock"):
        parts.append(look["style_lock"])
    return " ".join(parts)


def _refs_for(shot: dict, slug: str) -> list:
    refs = config.media_dir(slug) / "refs"
    found = []
    for cid in shot.get("characters", [])[:2]:
        found += sorted(refs.glob(f"char_{cid}_*.png"))[:1]
    if shot.get("location"):
        found += sorted(refs.glob(f"loc_{shot['location']}_*.png"))[:1]
    return found[:3]


def footage(slug: str, stage: str = "footage") -> int:
    guard = SpendGuard(slug, stage)
    prov = config.providers()["providers"]["video"]["api_optional"]
    board = config.load_yaml(config.project_dir(slug) / "storyboard.yaml")
    bible = _bible(slug)
    shots = board["shots"]
    if stage == "pilot":
        pilot_s = config.budget().get("estimation", {}).get("pilot_seconds", 60)
        picked, total = [], 0.0
        for s in shots:
            if total >= pilot_s:
                break
            picked.append(s)
            total += float(s["seconds"])
        shots = picked
    made = 0
    for shot in shots:
        out = config.media_dir(slug) / "shots" / f"{shot['id']}.mp4"
        if out.exists():
            continue
        tier = shot.get("tier", "standard")
        google.generate_video(
            guard, model=prov["models"][tier], prompt=compose_shot_prompt(shot, bible), out=out,
            usd=prov["clip_seconds"] * prov["usd_per_second"][tier],
            negative_prompt=bible.get("look", {}).get("negative", ""),
            reference_images=_refs_for(shot, slug), seconds=prov["clip_seconds"], resolution=prov["resolution"],
            aspect_ratio=prov.get("aspect_ratio", "9:16"))
        made += 1
    return made


def refs(slug: str) -> int:
    guard = SpendGuard(slug, "refs")
    img = config.providers()["providers"]["images"]
    model = img.get("model", "gemini-3-pro-image-preview")
    est = config.budget().get("estimation", {})
    bible = _bible(slug)
    style = bible.get("look", {}).get("style_lock", "")
    out_dir = config.media_dir(slug) / "refs"
    made = 0
    jobs = []
    for c in bible.get("characters", []):
        for i, view in enumerate(["front portrait", "three-quarter view", "full body", "profile"]
                                 [:est.get("refs_images_per_character", 4)]):
            jobs.append((out_dir / f"char_{c['id']}_{i}.png",
                         f"Character reference sheet, {view}, neutral background. {c['visual_lock']} {style}"))
    for l in bible.get("locations", []):
        for i, time_of_day in enumerate(["establishing vertical frame", "medium detail", "reverse angle"]
                                        [:est.get("refs_images_per_location", 3)]):
            jobs.append((out_dir / f"loc_{l['id']}_{i}.png",
                         f"Location plate, {time_of_day}, no people. {l['visual_lock']} {style}"))
    for path, prompt in jobs:
        if path.exists():
            continue
        google.generate_image(guard, model=model, prompt=prompt, out=path, usd=img["usd_per_image"],
                              aspect_ratio=config.providers()["providers"]["video"]["api_optional"].get("aspect_ratio", "9:16"))
        made += 1
    return made


def audio(slug: str) -> int:
    guard = SpendGuard(slug, "audio")
    tts = config.providers()["providers"]["narration_and_dialogue"]["primary"]
    model = tts.get("model", "gemini-2.5-pro-preview-tts")
    board = config.load_yaml(config.project_dir(slug) / "storyboard.yaml")
    voices = {c["id"]: c for c in _bible(slug).get("characters", [])}
    voices.setdefault("narrator", _bible(slug).get("narrator", {}))
    made = 0
    for line in board.get("audio", {}).get("lines", []):
        out = config.media_dir(slug) / "audio" / "lines" / f"{line['id']}.wav"
        if out.exists():
            continue
        speaker = voices.get(line.get("speaker", "narrator"), {})
        seconds = len(line["text"].split()) / 150 * 60
        usd = max(seconds * 25 * tts["usd_per_million_output_tokens"] / 1e6, 0.001)
        google.synthesize_speech(guard, model=model, text=line["text"], out=out, usd=usd,
                                 voice=speaker.get("voice", "Charon"),
                                 style=line.get("direction") or speaker.get("voice_direction", ""))
        made += 1
    return made
