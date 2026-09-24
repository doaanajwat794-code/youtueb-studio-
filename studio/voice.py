"""Import one continuous narration recording (e.g. a ShortsFaceless export or your own recording)
and split it into the storyboard's narration lines at the longest pauses.

STATUS: tested with synthetic audio only. Works best when the recording has no background music
and a clear pause (≥ 0.3 s) between lines.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from . import config
from .config import ffmpeg
from .media_tools import probe, run


def _silences(src: Path, noise_db: float, min_len: float) -> list[tuple[float, float]]:
    proc = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(src), "-vn", "-af",
                           f"silencedetect=noise={noise_db}dB:d={min_len}", "-f", "null", "-"],
                          capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", proc.stderr)]
    return list(zip(starts, ends))


def import_narration(slug: str, src: Path, noise_db: float = -35, min_len: float = 0.3) -> list[str]:
    board = config.load_yaml(config.project_dir(slug) / "storyboard.yaml")
    lines = [l for l in board.get("audio", {}).get("lines", [])]
    n = len(lines)
    if n == 0:
        raise SystemExit("Storyboard has no narration lines")
    total = probe(src)["duration"]
    gaps = [g for g in _silences(src, noise_db, min_len) if 0.05 < g[0] and g[1] < total - 0.05]
    if len(gaps) < n - 1:
        raise SystemExit(f"Found only {len(gaps)} pauses but need {n - 1} to split {n} lines. "
                         "Re-export with a clear pause between lines, or lower --noise.")
    cuts = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[: n - 1])
    bounds = [0.0] + [(a + b) / 2 for a, b in cuts] + [total]
    out = config.media_dir(slug) / "audio" / "lines"
    out.mkdir(parents=True, exist_ok=True)
    report = []
    for line, start, end in zip(lines, bounds, bounds[1:]):
        dst = out / f"{line['id']}.wav"
        run(["-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src), "-vn", "-ac", "1", "-ar", "48000",
             "-af", "silenceremove=start_periods=1:start_threshold=-45dB,"
                    "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
             str(dst)])
        dur = probe(dst)["duration"]
        report.append(f"{line['id']}: {dur:.2f}s  «{line['text'][:60]}»")
    return report
