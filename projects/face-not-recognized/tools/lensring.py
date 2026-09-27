# Adds a thin tracked AR-lens ring around both irises (and optionally removes a dark spot).
# Usage: python lensring.py SRC OUT T0 DUR --eyes x1,y1,x2,y2 --r 13 --mode steady|flicker [--mole x,y]
import sys, argparse, subprocess, numpy as np
from scipy import ndimage as nd
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('t0', type=float); ap.add_argument('dur', type=float)
ap.add_argument('--eyes', required=True); ap.add_argument('--r', type=float, default=21)
ap.add_argument('--mode', default='flicker'); ap.add_argument('--mole'); ap.add_argument('--search', type=int, default=14)
ap.add_argument('--strength', type=float, default=1.0)
ap.add_argument('--irisonly', action='store_true', help='only paint on darker iris pixels (not sclera or lids)')
ap.add_argument('--pairsep', type=float, help='derive the left eye from the right eye at this pixel distance (when the left locks onto lashes)')
a = ap.parse_args()
W, H, fps = 720, 1280, 24
raw = subprocess.run([FF, '-loglevel', 'error', '-ss', str(a.t0), '-i', a.src, '-t', str(a.dur), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).copy()
v = [float(x) for x in a.eyes.split(',')]
eyes = [np.array(v[0:2]), np.array(v[2:4])]
mole = np.array([float(x) for x in a.mole.split(',')]) if a.mole else None
yy, xx = np.mgrid[0:H, 0:W]
rng = np.random.default_rng(7)
def env(t):
    if a.mode == 'steady':
        return 0.8 + 0.06 * np.sin(t * 9) + rng.uniform(-0.03, 0.03)
    if t < 0.25: return 0
    for lo, hi, val in [(0.25, 0.33, 0.9), (0.33, 0.45, 0), (0.45, 0.52, 0.8), (0.52, 0.70, 0), (0.70, 0.78, 0.7)]:
        if lo <= t < hi: return val
    return 0.42 + 0.12 * np.sin(t * 23) + rng.uniform(-0.1, 0.1)
def detect_pair(img, prev):
    L = nd.gaussian_laplace(img.mean(2), a.r / 1.414) * (a.r ** 2)
    band = np.zeros_like(L, bool)
    cy = (prev[0][1] + prev[1][1]) / 2
    band[int(cy - 45):int(cy + 45), 200:680] = True
    Lm = np.where(band, L, -1e9)
    mx = (Lm == nd.maximum_filter(Lm, size=9)) & (Lm > 0)
    ys, xs = np.nonzero(mx)
    order = np.argsort(-Lm[ys, xs])[:25]
    pts = [(xs[k], ys[k], Lm[ys[k], xs[k]]) for k in order]
    sep0 = np.hypot(*(prev[1] - prev[0]))
    best, bp = -1e18, prev
    for p1 in pts:
        for p2 in pts:
            if p2[0] <= p1[0]: continue
            sep = p2[0] - p1[0]; dy = abs(p2[1] - p1[1])
            if not (0.8 * sep0 < sep < 1.25 * sep0) or dy > 18: continue
            mv = np.hypot(p1[0] - prev[0][0], p1[1] - prev[0][1]) + np.hypot(p2[0] - prev[1][0], p2[1] - prev[1][1])
            sc = p1[2] + p2[2] - 2.0 * mv
            if sc > best: best, bp = sc, [np.array(p1[:2], float), np.array(p2[:2], float)]
    return bp
track = []; prev = [e.copy() for e in eyes]
for i in range(len(fr)):
    prev = detect_pair(fr[i].astype(float), prev); track.append([p.copy() for p in prev])
T = np.array([[t[0][0], t[0][1], t[1][0], t[1][1]] for t in track])
T = nd.median_filter(T, size=(5, 1)); T = nd.uniform_filter1d(T, 3, axis=0)
if a.pairsep: T[:, 0] = T[:, 2] - a.pairsep; T[:, 1] = T[:, 3]
for i in range(len(fr)):
    f = fr[i].astype(float)
    eyes = [T[i, 0:2], T[i, 2:4]]
    if mole is not None:
        x, y = mole.astype(int); s = 10
        sub = g[y - s:y + s, x - s:x + s]; dy, dx = np.unravel_index(sub.argmin(), sub.shape)
        mole = 0.5 * mole + 0.5 * np.array([x - s + dx, y - s + dy], float)
        if sub.min() < 90:
            mx, my = mole.astype(int); sl = (slice(my - 20, my + 20), slice(mx - 20, mx + 20))
            patch = nd.median_filter(f[sl], size=(15, 15, 1))
            al = np.clip((9 - np.hypot(xx[sl] - mole[0], yy[sl] - mole[1])) / 3, 0, 1)[..., None]
            f[sl] = f[sl] * (1 - al) + patch * al
    e = env(i / fps) * a.strength
    if e > 0:
        ring = np.zeros((H, W))
        for c in eyes:
            d = np.hypot(xx - c[0], yy - c[1]); ring = np.maximum(ring, np.exp(-((d - a.r) / (a.r * 0.055)) ** 2))
        glow = nd.gaussian_filter(ring, a.r * 0.14) * 0.6
        notskin = np.clip((75 - (f[..., 0] - f[..., 2])) / 35, 0, 1)
        if a.irisonly: notskin = notskin * np.clip((150 - f.mean(2)) / 40, 0, 1)
        al = np.clip((ring + glow) * e, 0, 1) * notskin
        f = f + al[..., None] * np.array([40, 170, 255.]) * 0.9
    fr[i] = np.clip(f, 0, 255).astype(np.uint8)
    if i % 24 == 0: print(f'{i/fps:.1f}s eyes {eyes[0].round()} {eyes[1].round()}')
p = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-', '-ss', str(a.t0), '-t', str(a.dur), '-i', a.src,
                      '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', a.out], stdin=subprocess.PIPE)
p.stdin.write(fr.tobytes()); p.stdin.close(); p.wait()
