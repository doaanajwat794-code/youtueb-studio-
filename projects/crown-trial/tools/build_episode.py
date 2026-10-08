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


def epic_score(total, hits, drop=None, resume=None, bpm=132):
    """Original orchestral-style war score (D minor): driving low-string ostinato, brass stabs, choir pad,
    taiko pattern, a riser into the drop. Warm (low-passed) so it never sounds buzzy or harsh."""
    from scipy.signal import butter, sosfilt
    n = int(total * SR); out = np.zeros(n); t_all = np.arange(n) / SR
    beat = 60 / bpm; bar = 4 * beat; six = beat / 4
    D2, A1, Bb1, C2 = 73.42, 55.0, 58.27, 65.41
    prog = [(D2, "m"), (D2, "m"), (Bb1, "M"), (C2, "M"), (D2, "m"), (D2, "m"), (Bb1, "M"), (A1, "M")]
    def saw(f, L, nh=10, det=0.0):
        tt = np.arange(L) / SR; ph = 2 * np.pi * f * (1 + det) * tt
        return sum(np.sin(k * ph) / k for k in range(1, nh + 1))
    def add(x, at):
        i = int(at * SR)
        if i >= n: return
        L = min(len(x), n - i); out[i:i + L] += x[:L]
    lp = lambda x, fc: sosfilt(butter(2, fc / (SR / 2), output="sos"), x)
    strings = np.zeros(n); brass = np.zeros(n); choir = np.zeros(n); drums = np.zeros(n); bass = np.zeros(n)
    def put(buf, x, at):
        i = int(at * SR)
        if i >= n: return
        L = min(len(x), n - i); buf[i:i + L] += x[:L]
    pat = [1, 1, 1.5, 1, 1, 2, 1.5, 1, 1, 1, 1.5, 1, 2, 1.5, 1.2, 1]   # 16th-note ostinato (ratios of the root)
    b = 0; t0 = 0.0
    while t0 < total:
        root, q = prog[b % len(prog)]
        third = root * (1.189 if q == "m" else 1.26); fifth = root * 1.498
        for k, r in enumerate(pat):                       # low strings, 3 detuned voices, short bowed notes
            L = int(six * 0.95 * SR); env = np.minimum(1, np.arange(L) / (0.006 * SR)) * np.exp(-np.arange(L) / (0.09 * SR))
            note = sum(saw(root * 2 * r, L, 28, d) for d in (-0.003, 0, 0.003)) * env * (1.15 if k % 4 == 0 else 0.8)
            note += 0.45 * sum(saw(root * 4 * r, L, 18, d) for d in (-0.002, 0.002)) * env   # violins an octave up
            put(strings, note, t0 + k * six)
        Lb = int(bar * SR); envb = np.minimum(1, np.arange(Lb) / (0.02 * SR)) * np.exp(-np.arange(Lb) / (1.2 * SR))
        put(bass, saw(root, Lb, 6) * envb, t0)
        for at, g in ((0, 1.0), (2 * beat, 0.7) if b % 2 else (3.5 * beat, 0.6)):   # brass stabs
            L = int(0.7 * SR); tt = np.arange(L) / SR
            env = np.minimum(1, tt / 0.035) * np.exp(-tt / 0.35)
            chord = sum(saw(f * 2, L, 22, d) for f in (root, third, fifth) for d in (-0.002, 0.002))
            put(brass, chord * env * g, t0 + at)
        Lc = int(bar * SR); tt = np.arange(Lc) / SR                                  # choir "ah" pad
        envc = np.minimum(1, tt / 0.5) * np.minimum(1, (bar - tt) / 0.3) * (1 + 0.15 * np.sin(2 * np.pi * 5 * tt))
        put(choir, sum(saw(f * 4, Lc, 16, d) for f in (root, third, fifth) for d in (-0.004, 0.004)) * envc, t0)
        for at, g in ((0, 1.0), (1.5 * beat, 0.55), (2 * beat, 0.8), (3 * beat, 0.6), (3.5 * beat, 0.5)):   # taiko
            L = int(0.8 * SR); tt = np.arange(L) / SR; f = 52 * (1 + 1.5 * np.exp(-tt * 20))
            hit = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.random.default_rng(b * 7 + int(at * 10)).standard_normal(L) * np.exp(-tt * 45)) * np.exp(-tt * 6)
            put(drums, hit * g, t0 + at)
        t0 += bar; b += 1
    for h in hits:                                                                   # big impacts
        L = int(1.4 * SR); tt = np.arange(L) / SR; f = 40 * (1 + 2 * np.exp(-tt * 14))
        put(drums, 1.1 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2), h)
    hp = lambda x, fc: sosfilt(butter(2, fc / (SR / 2), "high", output="sos"), x)
    crash = np.zeros(n)                                                              # cymbal on every 2nd bar
    for k in range(0, int(total / bar) + 1, 2):
        L = int(1.2 * SR); tt = np.arange(L) / SR
        put(crash, np.random.default_rng(100 + k).standard_normal(L) * np.exp(-tt * 3.5), k * bar)
    strings = hp(lp(strings, 3800), 90); brass = hp(lp(brass, 3200), 110); bass = lp(bass, 220)
    choir = sosfilt(butter(2, [450 / (SR / 2), 2600 / (SR / 2)], "band", output="sos"), choir)
    drums = hp(lp(drums, 5000), 45); crash = hp(crash, 6000)
    build = np.clip(0.6 + 0.4 * t_all / total, 0, 1)
    nz = lambda x: x / (np.abs(x).max() + 1e-9)
    mix = 0.46 * nz(strings) + 0.36 * nz(brass) * build + 0.26 * nz(choir) * build + 0.08 * nz(bass) \
        + 0.30 * nz(drums) + 0.07 * nz(crash)
    if drop is not None:                                                             # rising swell into the drop
        L = int(1.6 * SR); tt = np.arange(L) / SR
        rise = sosfilt(butter(2, 2500 / (SR / 2), "high", output="sos"), np.random.default_rng(5).standard_normal(L)) * (tt / 1.6) ** 2
        i = int(drop * SR) - L
        if i > 0: mix[i:i + L] += 0.12 * rise / (np.abs(rise).max() + 1e-9)
    mix = mix + 1.2 * hp(mix, 700) + 1.5 * hp(mix, 2200)   # tilt EQ: presence for phone speakers
    mix *= np.clip(t_all / 0.05, 0, 1) * np.clip((total - t_all) / 1.5, 0, 1)
    mix = np.tanh(1.4 * mix / (np.abs(mix).max() + 1e-9))
    return 0.8 * mix / (np.abs(mix).max() + 1e-9)


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
        if f.suffix.lower() in (".jpg", ".jpeg", ".png"):  # still image (e.g. a closing wide shot) + silent audio
            src_in = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(f),
                      "-f", "lavfi", "-t", f"{dur:.3f}", "-i", f"anullsrc=r={SR}:cl=stereo"]
            vf[0] = "setpts=PTS-STARTPTS"; at = ["anull"]
        else:
            src_in = ["-ss", str(a), "-t", str(b - a), "-i", str(f)]
        run([*src_in, "-vf", ",".join(vf),
             "-af", ",".join(at) + f",volume={s.get('gain', cfg.get('clip_gain', 1.0))}" + (("," + cfg["clip_af"]) if cfg.get("clip_af") else "") + f",aresample={SR}", "-t", f"{dur:.3f}",
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
    if cfg.get("music_file"):  # a real track supplied by the owner (licensed/royalty-free) replaces the synth score
        raw = subprocess.run([FF, "-loglevel", "error", "-ss", str(cfg.get("music_start", 0)), "-i", str(cfg["music_file"]),
                              "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
        mus = np.frombuffer(raw, np.int16).astype(float) / 32768
        n = int(total * SR); mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
        tt = np.arange(n) / SR
        mus = mus * np.clip(tt / 0.15, 0, 1) * np.clip((total - tt) / 1.5, 0, 1)
        mus = 0.9 * mus / (np.abs(mus).max() + 1e-9)
    elif cfg.get("score_style") == "epic":
        mus = epic_score(total, hits, drop=seg_t(cfg["mute_from"]) if cfg.get("mute_from") else None)
    else:
        mus = score(total, hits, calm_from=seg_t(cfg["calm_from"]) if cfg.get("calm_from") else None)
    if cfg.get("mute_from"):  # sudden silence of the music (a "drop" before the big moment)
        i = int(seg_t(cfg["mute_from"]) * SR); env = np.exp(-np.arange(len(mus) - i) / (0.08 * SR))
        if cfg.get("music_resume"):  # bring the music back after the drop
            j = int(seg_t(cfg["music_resume"]) * SR) - i
            if 0 < j < len(env): env[j:] = np.clip(np.arange(len(env) - j) / (0.25 * SR), 0, 1)
        mus[i:] *= env
    fx = np.zeros(len(mus))
    for at, kind in (cfg.get("_sfx_auto", []) if cfg.get("transition_sfx", True) else []):  # soft whoosh on every whip/zoom transition
        clip = whoosh(0.4) * 0.6; i = max(0, int(at * SR)); fx[i:i + len(clip)] += clip[: max(0, len(fx) - i)]
    if cfg.get("smooth") and cfg.get("ambience_gain", 1.0) > 0:
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
         f"[d][m][x]amix=inputs=3:normalize=0,{cfg.get('final_eq', 'anull')},loudnorm=I={cfg.get('target_lufs', -14)}:TP=-1.5:LRA=11,aresample={SR}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(final)])
    print(f"built {final}  {total:.2f} s  {len(parts)} segments")
    for i, s0 in enumerate(starts): print(f"  seg{i:02d} @ {s0:6.2f}s  {cfg['segments'][i].get('note', '')}")


if __name__ == "__main__":
    main(sys.argv[1])
