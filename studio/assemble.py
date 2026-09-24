"""Assemble shots + voice + music + SFX into the render-size master (Shorts: 1080x1920) with captions.

Expected files (all under media/<slug>/):
  shots/<shot_id>.mp4          one generated clip per storyboard shot (no reuse allowed)
  audio/lines/<line_id>.wav    one file per narration/dialogue line
  audio/music/<cue_id>.wav     optional music cues
  audio/sfx/<name>.wav         optional sound effects referenced by shots[].sfx
Shots with `native_audio_db` also contribute their own generated audio (e.g. Veo ambience/SFX).
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
        if shot.get("native_audio_db") is not None and probe(src)["has_audio"]:
            native = work / "norm" / f"{shot['id']}.native.wav"
            run(["-ss", str(shot.get("trim_start", 0)), "-i", str(src), "-t", str(shot["seconds"]),
                 "-vn", "-ac", "2", "-ar", str(render["audio_sample_rate"]), str(native)])
            shot["_native"] = native
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
        if shot.get("_native"):
            inputs += ["-i", str(shot["_native"])]
            sfx_labels.append((len(inputs) // 2, spans[shot["id"]][0], float(shot["native_audio_db"])))
        for item in shot.get("sfx", []) or []:
            spec = item if isinstance(item, dict) else {"file": item}
            wav = media / "audio" / "sfx" / spec["file"]
            if not wav.exists():
                raise AssemblyError(f"Missing SFX {wav}")
            inputs += ["-i", str(wav)]
            sfx_labels.append((len(inputs) // 2, spans[shot["id"]][0] + float(spec.get("offset", 0)),
                               float(spec.get("gain_db", -8))))

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

    # 5. captions: sidecar SRT always; burned into the picture for Shorts
    subs = render.get("subtitles", {})
    srt = media / "final.en.srt"
    n_cues = build_srt(cues, srt, per_line=int(subs.get("max_chars_per_line", 42)))
    video_args = ["-map", "0:v", "-c:v", "copy"]
    filters = []
    if subs.get("burn_in") and n_cues:
        style = (f"FontName={subs.get('font', 'DejaVu Sans')},FontSize={subs.get('font_size', 10)},"
                 f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
                 f"Bold=1,Alignment=2,MarginV={subs.get('margin_v', 70)}")
        filters.append(f"subtitles='{_ff_path(srt)}':force_style='{style}'")
    overlays = board.get("overlays", [])
    if overlays:
        ass = work / "overlays.ass"
        write_overlays(overlays, spans, ass, render, subs.get("font", "DejaVu Sans"))
        filters.append(f"ass='{_ff_path(ass)}'")
    if filters:
        video_args = ["-filter_complex", f"[0:v]{','.join(filters)}[vout]",
                      "-map", "[vout]", "-c:v", render["video_codec"], "-crf", str(render["crf"]),
                      "-preset", render["preset"], "-pix_fmt", render["pixel_format"]]
        mixed = work / "mix.wav"
        run(["-i", str(picture), *inputs, "-filter_complex_script", str(graph), "-map", "[mix]",
             "-t", f"{total:.3f}", str(mixed)])
        inputs, graph = ["-i", str(mixed)], None

    final = media / "final.mp4"
    audio_map = ["-map", "1:a"] if graph is None else ["-filter_complex_script", str(graph), "-map", "[mix]"]
    run(["-i", str(picture), *inputs, *audio_map, *video_args, "-c:a", render["audio_codec"],
         "-b:a", render["audio_bitrate"], "-ar", str(render["audio_sample_rate"]),
         "-movflags", "+faststart", "-t", f"{total:.3f}", str(final)])

    # 6. sync report
    report = verify(final, total, render)
    report.update({"captions": str(srt), "caption_cues": n_cues, "warnings": warnings,
                   "shots": len(shots), "voice_lines": len(cues)})
    (media / "sync-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["ok"]:
        raise AssemblyError(f"Export failed checks: {json.dumps(report, indent=2)}")
    return report


def _ff_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


OVERLAY_STYLES = {  # ASS colours are &HAABBGGRR
    "alert": "&H00FFFFFF,&H00FFFFFF,&H003030D0,&H40000000",    # white text on red box
    "success": "&H00FFFFFF,&H00FFFFFF,&H0050A040,&H40000000",  # white text on green box
    "info": "&H00FFFFFF,&H00FFFFFF,&H00302820,&H40000000",     # white text on dark box
}


def _ass_time(t: float) -> str:
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def write_overlays(overlays: list[dict], spans: dict, out: Path, render: dict, font: str) -> None:
    """Precise interface text (phone/door screens) as boxed labels, e.g.
    {text: "Face not recognized", style: alert, at_shot: S01, offset: 1.0, duration: 3.0, y: 0.30}"""
    W, H = render["width"], render["height"]
    head = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"]
    for name, colours in OVERLAY_STYLES.items():
        head.append(f"Style: {name},{font},58,{colours},1,0,0,0,100,100,1,0,3,18,0,5,40,40,0,1")
    head += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for o in overlays:
        start = spans[o["at_shot"]][0] + float(o.get("offset", 0))
        end = start + float(o.get("duration", 2.5))
        x, y = int(W * float(o.get("x", 0.5))), int(H * float(o.get("y", 0.30)))
        text = str(o["text"]).replace("\n", "\\N")
        head.append(f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},{o.get('style', 'info')},,0,0,0,,"
                    f"{{\\pos({x},{y})\\fad(120,180)}}{text}")
    out.write_text("\n".join(head) + "\n", encoding="utf-8")


def verify(final: Path, expected: float, render: dict) -> dict:
    info = probe(final)
    v = stream_duration(final, "v")
    a = stream_duration(final, "a")
    checks = {
        f"resolution_{render['width']}x{render['height']}": (info["width"], info["height"]) == (render["width"], render["height"]),
        "fps": abs(info["fps"] - render["fps"]) < 0.01,
        "has_audio": info["has_audio"],
        "av_sync": abs(v - a) <= SYNC_TOLERANCE_S,
        "duration_matches_storyboard": abs(v - expected) <= SYNC_TOLERANCE_S,
    }
    return {"ok": all(checks.values()), "checks": checks, "file": str(final),
            "video_seconds": round(v, 3), "audio_seconds": round(a, 3), "expected_seconds": round(expected, 3)}
