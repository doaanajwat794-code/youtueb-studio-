"""Free, offline self-test: fake shots + tones -> full assembly -> checks; plus budget-guard tests.

Uses synthetic test patterns only (no API calls, no cost). Writes to media/_selftest/.
"""
from __future__ import annotations

import shutil

from . import assemble, budget, config, flow, thumbnail, voice
from .media_tools import run

SLUG = "selftest"


def _make_inputs(root) -> None:
    """Simulate the owner's hand-off: Flow-named clips in incoming/, one narration recording."""
    media = config.media_dir(SLUG)
    incoming = media / "incoming"
    for sub in ("audio/music", "audio/sfx"):
        (media / sub).mkdir(parents=True, exist_ok=True)
    incoming.mkdir(parents=True, exist_ok=True)
    shots = []
    for i in range(6):
        sid = f"S{i + 1:02}"
        # unique pattern per clip, deliberately 720x1280 / 30 fps (like a 720p Flow download);
        # S03 carries its own audio track to test native (Veo-style) audio
        extra = ["-f", "lavfi", "-i", "sine=frequency=880:duration=8"] if i == 2 else []
        run(["-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30:duration=8", *extra,
             "-vf", f"hue=h={i * 60}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             *(["-c:a", "aac", "-shortest"] if extra else []), str(incoming / f"TST_{sid}_v1.mp4")])
        shots.append({"id": sid, "beat": "test", "seconds": 3.0, "tier": "standard" if i else "hero",
                      "characters": ["a"] if i % 2 == 0 else [], "location": "x",
                      "prompt": "test pattern", "sfx": ["whoosh.wav"] if i == 3 else [],
                      **({"native_audio_db": -12} if i == 2 else {})})
    # a second take of S02 (must be preferred) and a mis-named file (must be ignored)
    run(["-f", "lavfi", "-i", "testsrc2=size=720x1280:rate=30:duration=8", "-vf", "negate",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(incoming / "TST_S02_v2.mp4")])
    (incoming / "random-download.mp4").write_bytes(b"not a clip")
    texts = ["I didn't notice it the first time.",
             "The elevator only had one button, and it was already lit.",
             "Who pressed it?",
             "Nobody. That was the rule. Nobody ever pressed it, and yet here we were, "
             "going down to a floor that did not exist on any drawing of the building."]
    # one continuous narration recording: 4 "lines" separated by 0.6 s pauses
    parts, filters = [], []
    for i, _ in enumerate(texts):
        parts += ["-f", "lavfi", "-i", f"sine=frequency={300 + i * 110}:duration={1.4 + i * 0.5}:sample_rate=48000",
                  "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=0.6"]
    run([*parts, "-filter_complex", "".join(f"[{k}:a]" for k in range(len(parts) // 4))
         + f"concat=n={len(parts) // 4}:v=0:a=1[a]", "-map", "[a]", str(media / "narration.wav")])
    lines = [{"id": f"N{i + 1:02}", "type": "narration", "speaker": "narrator",
              "at_shot": shots[i + 1]["id"], "offset": 0.3, "text": t} for i, t in enumerate(texts)]
    run(["-f", "lavfi", "-i", "sine=frequency=110:duration=20:sample_rate=48000", "-ac", "2",
         str(media / "audio" / "music" / "M01.wav")])
    run(["-f", "lavfi", "-i", "anoisesrc=d=0.8:c=pink:a=0.3", str(media / "audio" / "sfx" / "whoosh.wav")])
    config.save_yaml(root / SLUG / "project.yaml", {"title": "Self Test", "code": "TST"})
    config.save_yaml(root / SLUG / "storyboard.yaml", {
        "shots": shots,
        "audio": {"lines": lines, "music": [{"id": "M01", "start_shot": "S01", "end_shot": "S06"}]},
        "overlays": [{"text": "✕  Face not recognized", "style": "alert", "at_shot": "S01", "offset": 0.5,
                      "duration": 2.0}],
    })
    config.save_yaml(root / SLUG / "bible.yaml", {
        "look": {"style_lock": "Test look."},
        "characters": [{"id": "a", "name": "Ava", "visual_lock": "Test character."}],
        "locations": [{"id": "x", "name": "Lab", "visual_lock": "Test room."}]})


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
    real = (config.PROJECTS, config.MEDIA, config.LEDGER, config.budget)
    config.PROJECTS, config.MEDIA, config.LEDGER = tmp / "projects", tmp / "media", tmp / "ledger.csv"
    # test the guard with small non-zero caps (the real config has $0 = spending not approved)
    config.budget = lambda: {"caps": {"per_video_usd": 45, "per_month_usd": 150, "pilot_usd": 10,
                                      "single_call_usd": 5},
                             "approval": {"overrun_tolerance_pct": 10}, "estimation": {"retake_rate": 0.3}}
    results = []
    try:
        _make_inputs(config.PROJECTS)
        sheet = flow.write_prompt_sheet(SLUG)
        ok = "TST_S01_v1.mp4" in sheet.read_text() and "TST_REF_A_FRONT.png" in sheet.read_text()
        results.append(f"{'PASS' if ok else 'FAIL'}  Flow prompt sheet written with file names and ingredients")
        imp = flow.import_clips(SLUG, config.media_dir(SLUG) / "incoming")
        ok = (sum(r.startswith(("OK", "WARN")) for r in imp) == 6
              and any("S02: TST_S02_v2.mp4" in r for r in imp) and any("random-download" in r for r in imp))
        results.append(f"{'PASS' if ok else 'FAIL'}  import-clips: 6 shots, latest take chosen, stray file ignored")
        vo = voice.import_narration(SLUG, config.media_dir(SLUG) / "narration.wav")
        results.append(f"{'PASS' if len(vo) == 4 else 'FAIL'}  import-voice split one recording into 4 lines")
        report = assemble.assemble(SLUG)
        for name, ok in report["checks"].items():
            results.append(f"{'PASS' if ok else 'FAIL'}  export check: {name}")
        thumb = thumbnail.make_thumbnail(SLUG, 4.0, "Test Cover")
        results.append(f"{'PASS' if thumb.exists() else 'FAIL'}  thumbnail written ({thumb.name})")
        frame = config.media_dir(SLUG) / "caption-check.png"
        run(["-ss", "4.0", "-i", str(config.media_dir(SLUG) / "final.mp4"), "-frames:v", "1", str(frame)])
        results.append(f"INFO  caption frame for visual check: {frame}")
        results.append(f"INFO  video {report['video_seconds']}s / audio {report['audio_seconds']}s, "
                       f"{report['caption_cues']} caption cues, warnings: {report['warnings'] or 'none'}")

        # duplicate footage must be rejected
        shots = config.media_dir(SLUG) / "shots"
        shutil.copy(shots / "S01.mp4", shots / "S02.mp4")
        results.append(_expect_refusal("duplicate shot rejected", lambda: assemble.assemble(SLUG)))

        # budget guard
        results.append(f"{'PASS' if (config.media_dir(SLUG) / 'work' / 'overlays.ass').exists() else 'FAIL'}"
                       "  interface text overlay burned in")
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
        config.PROJECTS, config.MEDIA, config.LEDGER, config.budget = real
    return results
