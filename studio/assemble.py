"""Assemble shots + voice + music + SFX into a 1920x1080 master with captions and a sync report.

Expected files (all under media/<slug>/):
  shots/<shot_id>.mp4          one generated clip per storyboard shot (no reuse allowed)
  audio/lines/<line_id>.wav    one file per narration/dialogue line
  audio/music/<cue_id>.wav     optional music cues
  audio/sfx/<name>.wav         optional sound effects referenced by shots[].sfx
"""
from __future__ import annotations

import json
from pathlib import Path

from . import config
from .media_tools import probe, run, sha256, stream_duration
from .subtitles import build_srt

SYNC_TOLERANCE_S = 0.10


class AssemblyError(SystemExit):
    pass


def _timeline(shots: list[dict]) -> dict[str, tuple[float, float]]:
    t, spans = 0.0, {}
    for shot in shots:
        spans[shot["id"]] = (t, t + float(shot["seconds"]))
        t += float(shot["seconds"])
    return spans


def assemble(slug: str) -> dict:
    board = config.load_yaml(config.project_dir(slug) / "storyboard.yaml")
    render = config.providers()["render"]
    media = config.media_dir(slug)
    work = media / "work"
    (work / "norm").mkdir(parents=True, exist_ok=True)
    shots = board["shots"]
    spans = _timeline(shots)
    W, H, FPS = render["width"], render["height"], render["fps"]

    # 1. validate shots: present, long enough, never reused
    seen: dict[str, str] = {}
    for shot in shots:
        src = media / "shots" / f"{shot['id']}.mp4"
        if not src.exists():
            raise AssemblyError(f"Missing shot file {src}")
        digest = sha256(src)
        if digest in seen:
            raise AssemblyError(f"Shot {shot['id']} is a duplicate of {seen[digest]} — repeated footage is not allowed")
        seen[digest] = shot["id"]
        need = float(shot.get("trim_start", 0)) + float(shot["seconds"])
        have = probe(src)["duration"]
        if have + 0.05 < need:
            raise AssemblyError(f"Shot {shot['id']} is {have:.2f}s but the storyboard needs {need:.2f}s")

    # 2. normalise each shot to exact size / fps / duration (picture only)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"fps={FPS},format=yuv420p,setsar=1")
    concat_list = work / "concat.txt"
    lines = []
    for shot in shots:
        src = media / "shots" / f"{shot['id']}.mp4"
        dst = work / "norm" / f"{shot['id']}.mp4"
        run(["-ss", str(shot.get("trim_start", 0)), "-i", str(src), "-t", str(shot["seconds"]),
             "-vf", vf, "-an", "-c:v", render["video_codec"], "-crf", str(render["crf"]),
             "-preset", render["preset"], str(dst)])
        lines.append(f"file '{dst.resolve()}'")
    concat_list.write_text("\n".join(lines), encoding="utf-8")
    picture = work / "picture.mp4"
    run(["-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(picture)])
    total = spans[shots[-1]["id"]][1]

    # 3. place voice lines on the timeline
    audio_cfg = board.get("audio", {})
    inputs: list[str] = []
    voice_labels, cues, warnings = [], [], []
    for line in audio_cfg.get("lines", []):
        wav = media / "audio" / "lines" / f"{line['id']}.wav"
        if not wav.exists():
            raise AssemblyError(f"Missing voice line {wav}")
        start = spans[line["at_shot"]][0] + float(line.get("offset", 0))
        dur = probe(wav)["duration"]
        cues.append({"id": line["id"], "start": start, "end": start + dur, "text": line["text"]})
        inputs += ["-i", str(wav)]
        voice_labels.append((len(inputs) // 2, start, float(line.get("gain_db", 0))))
    cues.sort(key=lambda c: c["start"])
    for a, b in zip(cues, cues[1:]):
        if b["start"] < a["end"] - 0.02:
            warnings.append(f"voice overlap: {a['id']} ends {a['end']:.2f}s, {b['id']} starts {b['start']:.2f}s")
    for c in cues:
        if c["end"] > total + 0.01:
            raise AssemblyError(f"Line {c['id']} runs past the end of the picture ({c['end']:.2f}s > {total:.2f}s)")

    music_labels = []
    for cue in audio_cfg.get("music", []):
        wav = media / "audio" / "music" / f"{cue['id']}.wav"
        if not wav.exists():
            raise AssemblyError(f"Missing music cue {wav}")
        start, end = spans[cue["start_shot"]][0], spans[cue["end_shot"]][1]
        inputs += ["-i", str(wav)]
        music_labels.append((len(inputs) // 2, start, end - start, float(cue.get("gain_db", -14))))

    sfx_labels = []
    for shot in shots:
        for name in shot.get("sfx", []) or []:
            wav = media / "audio" / "sfx" / name
            if not wav.exists():
                raise AssemblyError(f"Missing SFX {wav}")
            inputs += ["-i", str(wav)]
            sfx_labels.append((len(inputs) // 2, spans[shot["id"]][0], -8.0))

    # 4. build the mix: voice bus, music bus ducked under voice, sfx bus, loudness-normalised master
    parts: list[str] = []
    base = f"anullsrc=r={render['audio_sample_rate']}:cl=stereo,atrim=0:{total:.3f}"

    def placed(idx: int, start: float, gain: float, extra: str = "") -> str:
        ms = int(round(start * 1000))
        return (f"[{idx}:a]aresample={render['audio_sample_rate']},aformat=channel_layouts=stereo{extra},"
                f"volume={gain}dB,adelay={ms}|{ms}")

    def bus(name: str, items: list[str]) -> None:
        """Mix items onto a silent bed of exactly `total` seconds -> [name]."""
        parts.append(f"{base}[bed_{name}]")
        labels = []
        for i, chain in enumerate(items):
            parts.append(f"{chain}[{name}{i}]")
            labels.append(f"[{name}{i}]")
        parts.append(f"[bed_{name}]{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0,"
                     f"atrim=0:{total:.3f}[{name}]")

    bus("voice", [placed(i, s, g) for i, s, g in voice_labels])
    bus("music", [placed(i, s, g, f",atrim=0:{d:.3f},afade=t=in:d=1.5,afade=t=out:st={max(d - 2, 0):.3f}:d=2")
                  for i, s, d, g in music_labels])
    bus("sfx", [placed(i, s, g) for i, s, g in sfx_labels])
    parts.append("[voice]asplit=2[vmix][vkey]")
    parts.append("[music][vkey]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[ducked]")
    parts.append(f"[vmix][ducked][sfx]amix=inputs=3:normalize=0,"
                 f"loudnorm=I={render['loudness_lufs']}:TP=-1.5:LRA=11,"
                 f"aresample={render['audio_sample_rate']},atrim=0:{total:.3f}[mix]")
    graph = work / "mix.filter"
    graph.write_text(";\n".join(parts), encoding="utf-8")

    final = media / "final.mp4"
    run(["-i", str(picture), *inputs, "-filter_complex_script", str(graph),
         "-map", "0:v", "-map", "[mix]", "-c:v", "copy", "-c:a", render["audio_codec"],
         "-b:a", render["audio_bitrate"], "-ar", str(render["audio_sample_rate"]),
         "-movflags", "+faststart", "-t", f"{total:.3f}", str(final)])

    # 5. captions + sync report
    srt = media / "final.en.srt"
    n_cues = build_srt(cues, srt)
    report = verify(final, total, render)
    report.update({"captions": str(srt), "caption_cues": n_cues, "warnings": warnings,
                   "shots": len(shots), "voice_lines": len(cues)})
    (media / "sync-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["ok"]:
        raise AssemblyError(f"Export failed checks: {json.dumps(report, indent=2)}")
    return report


def verify(final: Path, expected: float, render: dict) -> dict:
    info = probe(final)
    v = stream_duration(final, "v")
    a = stream_duration(final, "a")
    checks = {
        "resolution_1920x1080": (info["width"], info["height"]) == (render["width"], render["height"]),
        "fps": abs(info["fps"] - render["fps"]) < 0.01,
        "has_audio": info["has_audio"],
        "av_sync": abs(v - a) <= SYNC_TOLERANCE_S,
        "duration_matches_storyboard": abs(v - expected) <= SYNC_TOLERANCE_S,
    }
    return {"ok": all(checks.values()), "checks": checks, "file": str(final),
            "video_seconds": round(v, 3), "audio_seconds": round(a, 3), "expected_seconds": round(expected, 3)}
