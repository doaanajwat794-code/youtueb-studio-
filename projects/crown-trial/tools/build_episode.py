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


def wind(total):
    """Continuous arena ambience (cold wind + low rumble) so the sound never resets at a cut."""
    from scipy.signal import butter, lfilter
    n = int(total * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    b, a = butter(2, [180 / (SR / 2), 900 / (SR / 2)], "band")
    w = lfilter(b, a, rng.standard_normal(n)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t) * np.sin(2 * np.pi * 0.047 * t + 1))
    b, a = butter(2, 90 / (SR / 2), "low")
    r = lfilter(b, a, rng.standard_normal(n)) * 2.0
    out = w + r
    out *= np.clip(t / 0.4, 0, 1) * np.clip((total - t) / 0.8, 0, 1)
    return 0.12 * out / (np.abs(out).max() + 1e-9)


# transition types (into a segment): ffmpeg xfade name, duration, auto sfx
TR = {"cut": ("fade", 1 / FPS, None), "whip": ("hblur", 0.14, "whoosh"), "zoom": ("zoomin", 0.16, "whoosh"),
      "flash": ("fadewhite", 0.12, None), "dissolve": ("dissolve", 0.28, None), "dip": ("fadeblack", 0.45, None),
      "slide": ("smoothleft", 0.16, "whoosh")}


def seg_color(path):
    """Mean RGB of the middle of a segment (for shot-to-shot colour matching)."""
    r = subprocess.run([FF, "-loglevel", "error", "-i", str(path), "-vf", "scale=54:96", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, check=True).stdout
    f = np.frombuffer(r, np.uint8).reshape(-1, 96, 54, 3).astype(float)
    k = len(f); return f[k // 4: max(k // 4 + 1, 3 * k // 4)].mean((0, 1, 2))


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
        if s.get("push"):  # slow push-in so a dialogue hold never looks frozen
            vf.append(f"zoompan=z='1+{s['push']}*on':x='iw/2-(iw/zoom/2)':y='ih*0.4-(ih/zoom*0.4)':d=1:s={W}x{H}:fps={FPS}")
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
    picture = work / "picture.mp4"
    smooth = cfg.get("smooth", False)
    if not smooth:
        lst = work / "list.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(picture)])
    else:
        # Professional join: every shot is colour-matched to the episode's look, and every cut is a real
        # transition (whip / zoom punch / flash / dissolve / dip) or at least a 1-frame blend + audio crossfade,
        # so the sound and picture never "reset" between Flow clips.
        cols = [seg_color(p) for p in parts]
        target = np.median(cols, 0); tl = target.mean()
        lens = [imageio_ffmpeg.count_frames_and_secs(str(p))[0] / FPS for p in parts]  # real lengths, frame-exact
        fc, starts, cur, acc = [], [], "v0", lens[0]
        for i, c in enumerate(cols):
            chroma = (target / tl) / (c / c.mean())            # match colour cast
            luma = (tl / c.mean()) ** cfg.get("luma_match", 0.35)  # partly match brightness
            g = np.clip(chroma ** 0.8 * luma, 0.6, 1.6)
            fc.append(f"[{i}:v]colorchannelmixer=rr={g[0]:.3f}:gg={g[1]:.3f}:bb={g[2]:.3f},settb=AVTB,format=yuv420p[v{i}]")
            fc.append(f"[{i}:a]acompressor=threshold=0.08:ratio=3:attack=5:release=120,asetpts=PTS-STARTPTS[a{i}]")
        starts.append(0.0); curA = "a0"; sfx_auto = []
        for i in range(1, len(parts)):
            name, d, fx = TR[cfg["segments"][i].get("tr", "cut")]
            d = cfg["segments"][i].get("trd", d)
            off = acc - d
            fc.append(f"[{cur}][v{i}]xfade=transition={name}:duration={d:.3f}:offset={off:.3f}[x{i}]")
            fc.append(f"[{curA}][a{i}]acrossfade=d={d:.3f}:c1=tri:c2=tri[y{i}]")
            cur, curA = f"x{i}", f"y{i}"
            starts.append(off)
            if fx: sfx_auto.append((off + d / 2 - 0.2, fx))
            acc = off + lens[i]
        total = acc
        run([*sum((["-i", str(p)] for p in parts), []), "-filter_complex", ";".join(fc),
             "-map", f"[{cur}]", "-map", f"[{curA}]", "-c:v", "libx264", "-crf", "15", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", str(SR), "-ac", "2", str(picture)])
        cfg["_sfx_auto"] = sfx_auto

    def seg_t(ref):  # "3+0.5" -> start of segment 3 + 0.5 s
        k, off = (ref.split("+") + ["0"])[:2] if isinstance(ref, str) else (ref, 0)
        return starts[int(k)] + float(off)

    hits = [seg_t(h) for h in cfg.get("drum_hits", [])]
    mus = score(total, hits, calm_from=seg_t(cfg["calm_from"]) if cfg.get("calm_from") else None)
    if cfg.get("mute_from"):  # sudden silence of the score (e.g. when the masked Champion appears)
        i = int(seg_t(cfg["mute_from"]) * SR); mus[i:] *= np.exp(-np.arange(len(mus) - i) / (0.08 * SR))
    fx = np.zeros(len(mus))
    for at, kind in cfg.get("_sfx_auto", []):  # soft whoosh on every whip/zoom transition
        clip = whoosh(0.4) * 0.6; i = max(0, int(at * SR)); fx[i:i + len(clip)] += clip[: max(0, len(fx) - i)]
    if cfg.get("smooth"):
        fx += wind(len(fx) / SR) * cfg.get("ambience_gain", 1.0)
    for e in cfg.get("sfx", []):
        clip = boom() if e["type"] == "boom" else whoosh()
        i = int(seg_t(e["at"]) * SR); fx[i:i + len(clip)] += clip[: len(fx) - i] * e.get("gain", 1.0)
    wav(work / "music.wav", mus * cfg.get("music_gain", 0.6)); wav(work / "fx.wav", fx)

    font = cfg.get("font", "DejaVu Sans")
    ev = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
          "[V4+ Styles]",
          "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
          f"Style: hook,{font},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,2,0,1,8,4,5,40,40,0,1",
          f"Style: name,{font},96,&H0037C8FF,&H0037C8FF,&H00000000,&H90000000,1,0,0,0,100,100,4,0,1,8,4,5,40,40,0,1",
          f"Style: title,{font},54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,6,0,1,5,3,5,40,40,0,1",
          f"Style: sub,{font},62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,6,3,2,60,60,300,1",
          f"Style: end,{font},70,&H0037C8FF,&H0037C8FF,&H00000000,&H90000000,1,0,0,0,100,100,2,0,1,8,4,5,40,40,0,1",
          "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for o in cfg.get("text", []):
        a = seg_t(o["at"]); b = a + o["dur"]
        pos = "" if o["style"] == "sub" else f"\\pos({W // 2},{int(H * o.get('y', 0.2))})"
        pop = "\\fscx120\\fscy120\\t(0,160,\\fscx100\\fscy100)" if o["style"] in ("hook", "name", "end") else ""
        txt = o["text"].replace("\n", "\\N")
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},{o['style']},,0,0,0,,{{{pos}{pop}\\fad(80,150)}}{txt}")
    (work / "text.ass").write_text("\n".join(ev) + "\n", encoding="utf-8")

    final = Path(cfg["output"])
    look = ""
    if cfg.get("smooth"):  # one camera, one film stock across all Flow clips
        look = ("crop=w=iw*0.955:h=ih*0.955:x=(iw-ow)/2+iw*0.006*sin(2*PI*t*0.53)+iw*0.003*sin(2*PI*t*1.7):"
                "y=(ih-oh)/2+ih*0.005*sin(2*PI*t*0.41+1)+ih*0.002*sin(2*PI*t*2.3),"
                f"scale={W}:{H}:flags=lanczos,"
                "eq=contrast=1.06:saturation=1.06,colorbalance=bs=0.05:bm=0.02:rh=0.04:gh=0.01,"
                "vignette=angle=PI/5,noise=c0s=6:c0f=t+u,")
    ass = str((work / "text.ass").resolve()).replace(":", "\\:")
    run(["-i", str(picture), "-i", str(work / "music.wav"), "-i", str(work / "fx.wav"),
         "-filter_complex",
         f"[0:v]{look}ass='{ass}',format=yuv420p[v];"
         f"[0:a]volume=1.0[d];[1:a]volume=1.0[m];[2:a]volume=1.0[x];"
         f"[d][m][x]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample={SR}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(final)])
    print(f"built {final}  {total:.2f} s  {len(parts)} segments")
    for i, s0 in enumerate(starts): print(f"  seg{i:02d} @ {s0:6.2f}s  {cfg['segments'][i].get('note', '')}")


if __name__ == "__main__":
    main(sys.argv[1])
