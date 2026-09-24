"""Make a vertical cover image (1080x1920) from a caption-free frame of the edit, with up to 3 words."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import config
from .media_tools import run

FONT_CANDIDATES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]


def _font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def make_thumbnail(slug: str, at: float, text: str = "") -> Path:
    media = config.media_dir(slug)
    render = config.providers()["render"]
    frame = media / "work" / "thumb-frame.png"
    frame.parent.mkdir(parents=True, exist_ok=True)
    clean = media / "work" / "picture.mp4"   # the edit before captions are burned in
    source = clean if clean.exists() else media / "final.mp4"
    run(["-ss", f"{at:.2f}", "-i", str(source), "-frames:v", "1", str(frame)])
    img = ImageOps.fit(Image.open(frame).convert("RGB"), (render["width"], render["height"]))
    if text:
        words = text.upper().split()[:3]
        draw = ImageDraw.Draw(img)
        font = _font(150)
        y = int(render["height"] * 0.16)
        for word in words:
            w = draw.textlength(word, font=font)
            draw.text(((render["width"] - w) / 2, y), word, font=font, fill=(255, 255, 255),
                      stroke_width=10, stroke_fill=(0, 0, 0))
            y += 170
    out = media / "thumbnail.jpg"
    img.save(out, quality=92)
    return out
