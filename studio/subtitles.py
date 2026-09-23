"""Build an SRT caption file from timed voice lines."""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

MAX_CHARS_PER_LINE = 42
MAX_LINES_PER_CUE = 2


def _ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def _chunks(text: str, per_line: int) -> list[str]:
    """Split text into caption-sized chunks, preferring sentence boundaries."""
    limit = per_line * MAX_LINES_PER_CUE
    sentences = re.split(r"(?<=[.!?…])\s+", text.strip())
    chunks, current = [], ""
    for sentence in sentences:
        for piece in textwrap.wrap(sentence, limit) or [""]:
            candidate = f"{current} {piece}".strip()
            if len(candidate) <= limit:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = piece
    if current:
        chunks.append(current)
    return chunks


def build_srt(cues: list[dict], out: Path, per_line: int = MAX_CHARS_PER_LINE) -> int:
    """cues: [{'start': s, 'end': s, 'text': str}] sorted by start. Returns cue count."""
    blocks, n = [], 0
    for cue in cues:
        pieces = _chunks(cue["text"], per_line)
        total_chars = sum(len(p) for p in pieces) or 1
        t = cue["start"]
        span = cue["end"] - cue["start"]
        for piece in pieces:
            dur = span * len(piece) / total_chars
            n += 1
            wrapped = "\n".join(textwrap.wrap(piece, per_line))
            blocks.append(f"{n}\n{_ts(t)} --> {_ts(t + dur)}\n{wrapped}\n")
            t += dur
    out.write_text("\n".join(blocks), encoding="utf-8")
    return n
