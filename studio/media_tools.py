"""Small FFmpeg helpers (the bundled imageio-ffmpeg binary has no ffprobe)."""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

from .config import ffmpeg


def run(args: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run([ffmpeg(), "-hide_banner", "-y", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {' '.join(args[:6])} …\n{proc.stderr[-2000:]}")
    return proc


def _hms(text: str) -> float:
    h, m, s = text.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def probe(path: Path) -> dict:
    """Return container duration, width, height, fps, has_audio for a media file."""
    proc = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    err = proc.stderr
    info = {"duration": 0.0, "width": 0, "height": 0, "fps": 0.0, "has_audio": " Audio:" in err,
            "has_video": " Video:" in err}
    if m := re.search(r"Duration: (\d+:\d+:\d+\.\d+)", err):
        info["duration"] = _hms(m.group(1))
    if m := re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", err):
        info["width"], info["height"] = int(m.group(1)), int(m.group(2))
    if m := re.search(r"([\d.]+) fps", err):
        info["fps"] = float(m.group(1))
    return info


def stream_duration(path: Path, stream: str) -> float:
    """Decode one stream type ('v' or 'a') to null and return its real duration."""
    proc = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(path), "-map", f"0:{stream}:0",
                           "-f", "null", "-"], capture_output=True, text=True)
    times = re.findall(r"time=(\d+:\d+:\d+\.\d+)", proc.stderr)
    return _hms(times[-1]) if times else 0.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
