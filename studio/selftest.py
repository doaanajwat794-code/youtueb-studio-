"""Free, offline self-test: fake shots + tones -> full assembly -> checks; plus budget-guard tests.

Uses synthetic test patterns only (no API calls, no cost). Writes to media/_selftest/.
"""
from __future__ import annotations

import shutil

from . import assemble, budget, config
from .media_tools import run

SLUG = "selftest"


def _make_inputs(root) -> None:
    media = config.media_dir(SLUG)
    for sub in ("shots", "audio/lines", "audio/music", "audio/sfx"):
        (media / sub).mkdir(parents=True, exist_ok=True)
    shots = []
    for i in range(6):
        sid = f"S01-{i + 1:03}"
        # unique pattern per shot, deliberately 720x1280 / 30 fps to prove normalisation;
        # shot 3 carries its own audio track to test native (Veo-style) audio
        extra = ["-f", "lavfi", "-i", "sine=frequency=880:duration=4"] if i == 2 else []
        run(["-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30:duration=4", *extra,
             "-vf", f"hue=h={i * 60}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             *(["-c:a", "aac", "-shortest"] if extra else []), str(media / "shots" / f"{sid}.mp4")])
        shots.append({"id": sid, "seconds": 3.0, "tier": "standard" if i else "hero",
                      "prompt": "test pattern", "sfx": ["whoosh.wav"] if i == 3 else [],
                      **({"native_audio_db": -12} if i == 2 else {})})
    lines = []
    for i, text in enumerate(["I didn't notice it the first time.",
                              "The elevator only had one button, and it was already lit.",
                              "Who pressed it?",
                              "Nobody. That was the rule. Nobody ever pressed it, and yet here we were, "
                              "going down to a floor that did not exist on any drawing of the building."]):
        lid = f"N{i + 1:03}"
        dur = 1.6 + i * 0.6
        run(["-f", "lavfi", "-i", f"sine=frequency={300 + i * 110}:duration={dur}:sample_rate=24000",
             "-ac", "1", str(media / "audio" / "lines" / f"{lid}.wav")])
        lines.append({"id": lid, "type": "narration", "speaker": "narrator",
                      "at_shot": shots[i + 1]["id"], "offset": 0.3, "text": text})
    run(["-f", "lavfi", "-i", "sine=frequency=110:duration=20:sample_rate=48000", "-ac", "2",
         str(media / "audio" / "music" / "M01.wav")])
    run(["-f", "lavfi", "-i", "anoisesrc=d=0.8:c=pink:a=0.3", str(media / "audio" / "sfx" / "whoosh.wav")])
    config.save_yaml(root / SLUG / "storyboard.yaml", {
        "shots": shots,
        "audio": {"lines": lines, "music": [{"id": "M01", "start_shot": "S01-001", "end_shot": "S01-006"}]},
    })
    config.save_yaml(root / SLUG / "bible.yaml", {"characters": [{"id": "a"}], "locations": [{"id": "x"}]})


def _expect_refusal(label: str, fn) -> str:
    try:
        fn()
    except SystemExit as exc:
        return f"PASS  {label}: refused ({str(exc)[:90]}…)"
    raise AssertionError(f"FAIL  {label}: was NOT refused")


def run_selftest() -> list[str]:
    tmp = config.MEDIA / "_selftest"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    real = (config.PROJECTS, config.MEDIA, config.LEDGER)
    config.PROJECTS, config.MEDIA, config.LEDGER = tmp / "projects", tmp / "media", tmp / "ledger.csv"
    results = []
    try:
        _make_inputs(config.PROJECTS)
        report = assemble.assemble(SLUG)
        for name, ok in report["checks"].items():
            results.append(f"{'PASS' if ok else 'FAIL'}  export check: {name}")
        frame = config.media_dir(SLUG) / "caption-check.png"
        run(["-ss", "4.0", "-i", str(config.media_dir(SLUG) / "final.mp4"), "-frames:v", "1", str(frame)])
        results.append(f"INFO  caption frame for visual check: {frame}")
        results.append(f"INFO  video {report['video_seconds']}s / audio {report['audio_seconds']}s, "
                       f"{report['caption_cues']} caption cues, warnings: {report['warnings'] or 'none'}")

        # duplicate footage must be rejected
        shots = config.media_dir(SLUG) / "shots"
        shutil.copy(shots / "S01-001.mp4", shots / "S01-002.mp4")
        results.append(_expect_refusal("duplicate shot rejected", lambda: assemble.assemble(SLUG)))

        # budget guard
        results.append(_expect_refusal("spend without approval", lambda: budget.SpendGuard(SLUG, "footage")))
        est = budget.estimate(SLUG, "footage")
        results.append(f"INFO  footage estimate for 6 test shots: ${est['usd']} ({est['detail']})")
        budget.record_approval(SLUG, "footage", 2.00, note="selftest")
        guard = budget.SpendGuard(SLUG, "footage")
        guard.charge(1.50, provider="test")
        results.append("PASS  charge within approval accepted")
        results.append(_expect_refusal("charge beyond approval", lambda: guard.charge(1.00, provider="test")))
        results.append(_expect_refusal("single call above cap", lambda: guard.charge(999, provider="test")))
        results.append(_expect_refusal("approval above per-video cap",
                                       lambda: budget.record_approval(SLUG, "audio", 10_000)))
    finally:
        config.PROJECTS, config.MEDIA, config.LEDGER = real
    return results
