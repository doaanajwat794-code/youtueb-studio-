# The Crown Trial — episode editor (Claude's cut).
# Usage: python projects/crown-trial/tools/build_episode.py projects/crown-trial/edit-e01.yaml
# Cuts each clip, applies speed (setpts/atempo), upscales to 1080x1920, adds white hit-flashes,
# an original synthesised war-drum score, boom/whoosh SFX, hook text, name cards, subtitles, end cards.
import sys, subprocess, wave, yaml, numpy as np
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
W, H, FPS = 1080, 1920, 24


def run(args):
    subprocess.run([FF, "-loglevel", "error", "-y", *args], check=True)


def wav(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    with wave.open(str(path), "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def score(total, hits, bpm=100, calm_from=None):
    """Original war-drum score: taiko-like hits, low drone, rising string-like pad; quieter after calm_from."""
    n = int(total * SR); t = np.arange(n) / SR; out = np.zeros(n)
    beat = 60 / bpm
    def drum(at, gain=1.0, f0=58):
        i = int(at * SR); L = int(0.9 * SR); tt = np.arange(L) / SR
        f = f0 * (1 + 1.8 * np.exp(-tt * 18))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5.5) * gain
        s += 0.25 * np.random.default_rng(i).standard_normal(L) * np.exp(-tt * 40) * gain
        out[i:i + L] += s[: max(0, min(L, n - i))]
    k = 0; b = 0.0
    while b < total:
        pat = [1.0, 0, 0.55, 0.35, 0.9, 0, 0.55, 0.7][k % 8]
        if pat and not (calm_from and b > calm_from and k % 2): drum(b, pat)
        b += beat / 2; k += 1
    for h in hits: drum(h, 1.4, 45)
    drone = 0.12 * (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t))
    pad = 0.05 * sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.2 * t)) for f in (220, 261.6, 329.6))
    swell = np.clip(t / total, 0, 1)
    out += drone + pad * (0.3 + swell)
    out *= np.clip(t / 0.3, 0, 1) * np.clip((total - t) / 1.2, 0, 1)
    return 0.55 * out / (np.abs(out).max() + 1e-9)


def boom(L=1.6):
    tt = np.arange(int(L * SR)) / SR
    return 0.9 * np.sin(2 * np.pi * 42 * tt * (1 + np.exp(-tt * 9))) * np.exp(-tt * 2.8)


def whoosh(L=1.2):
    tt = np.arange(int(L * SR)) / SR
    noise = np.random.default_rng(3).standard_normal(len(tt))
    from scipy.signal import butter, lfilter
    b, a = butter(2, [300 / (SR / 2), 2500 / (SR / 2)], "band")
    env = np.sin(np.pi * tt / L) ** 2
    return 0.5 * lfilter(b, a, noise) * env


def ass_time(s):
    h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def main(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    src = Path(cfg["clips_dir"]); work = Path(cfg["work_dir"]); work.mkdir(parents=True, exist_ok=True)
    parts, t = [], 0.0
    starts = []
    for i, s in enumerate(cfg["segments"]):
        f = src / s["file"]; a, b = s["in"], s["out"]; sp = s.get("speed", 1.0)
        dur = (b - a) / sp
        vf = [f"setpts=(PTS-STARTPTS)/{sp}", f"scale={W}:{H}:flags=lanczos", "unsharp=5:5:0.6", f"fps={FPS}"]
        if s.get("flash"):
            vf.append("eq=brightness='if(lt(t,0.07),0.35,0)':eval=frame")
        at = []
        rem = sp
        while rem > 2.0: at.append("atempo=2.0"); rem /= 2
        while rem < 0.5: at.append("atempo=0.5"); rem /= 0.5
        at.append(f"atempo={rem:.4f}")
        out = work / f"seg{i:02d}.mp4"
        run(["-ss", str(a), "-t", str(b - a), "-i", str(f), "-vf", ",".join(vf),
             "-af", ",".join(at) + f",volume={s.get('gain', 1.0)},aresample={SR}", "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", str(SR), "-ac", "2", str(out)])
        parts.append(out); starts.append(t); t += dur
    total = t
    lst = work / "list.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    picture = work / "picture.mp4"
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(picture)])

    def seg_t(ref):  # "3+0.5" -> start of segment 3 + 0.5 s
        k, off = (ref.split("+") + ["0"])[:2] if isinstance(ref, str) else (ref, 0)
        return starts[int(k)] + float(off)

    hits = [seg_t(h) for h in cfg.get("drum_hits", [])]
    mus = score(total, hits, calm_from=seg_t(cfg["calm_from"]) if cfg.get("calm_from") else None)
    fx = np.zeros(len(mus))
    for e in cfg.get("sfx", []):
        clip = boom() if e["type"] == "boom" else whoosh()
        i = int(seg_t(e["at"]) * SR); fx[i:i + len(clip)] += clip[: len(fx) - i] * e.get("gain", 1.0)
    wav(work / "music.wav", mus * cfg.get("music_gain", 0.6)); wav(work / "fx.wav", fx)

    font = cfg.get("font", "DejaVu Sans")
    ev = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
          "[V4+ Styles]",
          "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
          f"Style: hook,{font},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,2,0,1,8,4,5,40,40,0,1",
          f"Style: name,{font},96,&H0037C8FF,&H0037C8FF,&H00000000,&H90000000,1,0,0,0,100,100,4,0,1,8,4,5,40,40,0,1",
          f"Style: title,{font},54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,6,0,1,5,3,5,40,40,0,1",
          f"Style: sub,{font},62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,6,3,2,60,60,300,1",
          f"Style: end,{font},84,&H0037C8FF,&H0037C8FF,&H00000000,&H90000000,1,0,0,0,100,100,2,0,1,8,4,5,40,40,0,1",
          "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for o in cfg.get("text", []):
        a = seg_t(o["at"]); b = a + o["dur"]
        pos = "" if o["style"] == "sub" else f"\\pos({W // 2},{int(H * o.get('y', 0.2))})"
        pop = "\\fscx120\\fscy120\\t(0,160,\\fscx100\\fscy100)" if o["style"] in ("hook", "name", "end") else ""
        txt = o["text"].replace("\n", "\\N")
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},{o['style']},,0,0,0,,{{{pos}{pop}\\fad(80,150)}}{txt}")
    (work / "text.ass").write_text("\n".join(ev) + "\n", encoding="utf-8")

    final = Path(cfg["output"])
    ass = str((work / "text.ass").resolve()).replace(":", "\\:")
    run(["-i", str(picture), "-i", str(work / "music.wav"), "-i", str(work / "fx.wav"),
         "-filter_complex",
         f"[0:v]ass='{ass}',format=yuv420p[v];"
         f"[0:a]volume=1.0[d];[1:a]volume=1.0[m];[2:a]volume=1.0[x];"
         f"[d][m][x]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample={SR}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(final)])
    print(f"built {final}  {total:.2f} s  {len(parts)} segments")
    for i, s0 in enumerate(starts): print(f"  seg{i:02d} @ {s0:6.2f}s  {cfg['segments'][i].get('note', '')}")


if __name__ == "__main__":
    main(sys.argv[1])
