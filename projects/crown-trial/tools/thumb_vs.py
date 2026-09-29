# Split "VS" cover for a Crown Trial episode.
# Usage: python thumb_vs.py TOP.png BOTTOM.png OUT.jpg "BIG TEXT" "SUB TEXT" "FOOTER"
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1920
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
top_p, bot_p, out, big, sub, foot = sys.argv[1:7]


def fit(img, w, h, cx=0.5, cy=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    x = int((img.width - w) * cx); y = int((img.height - h) * cy)
    return img.crop((x, y, x + w, y + h))


top = Image.open(top_p).convert("RGB").crop((110, 60, 610, 620))
import os
BC = tuple(int(v) for v in os.environ.get("BOT_CROP", "0,120,720,1100").split(","))
bot = Image.open(bot_p).convert("RGB").crop(BC)
top = ImageEnhance.Contrast(fit(top, W, 1100, 0.5, 0.0)).enhance(1.15)
bot = ImageEnhance.Contrast(fit(bot, W, 1100, 0.5, 0.4)).enhance(1.25)
top = ImageEnhance.Color(top).enhance(1.15)

canvas = Image.new("RGB", (W, H)); canvas.paste(top.resize((W, 1100)).filter(ImageFilter.GaussianBlur(30)), (0, 0)); canvas.paste(top.crop((0, 0, W, 870)), (0, 170))
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).polygon([(0, 1040), (W, 860), (W, H), (0, H)], fill=255)
lower = Image.new("RGB", (W, H)); lower.paste(bot, (0, H - 1100))
canvas = Image.composite(lower, canvas, mask).convert("RGBA")

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).line([(0, 1040), (W, 860)], fill=(255, 90, 20, 255), width=22)
canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(10)))
line = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(line).line([(0, 1040), (W, 860)], fill=(255, 235, 170, 255), width=5)
canvas = Image.alpha_composite(canvas, line)

grad = Image.new("L", (1, H))
for y in range(H):
    a = 200 * max(0, 1 - y / 420) ** 1.5 + 170 * max(0, (y - 1600) / 320) ** 1.5
    grad.putpixel((0, y), int(min(255, a)))
dark = Image.new("RGBA", (W, H), (0, 0, 0, 255)); dark.putalpha(grad.resize((W, H)))
canvas = Image.alpha_composite(canvas, dark)
import random
random.seed(7)
red = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(red)
rd.rectangle([0, 0, W, H], outline=(200, 20, 10, 255), width=60)
canvas = Image.alpha_composite(canvas, red.filter(ImageFilter.GaussianBlur(45)))
emb = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ed = ImageDraw.Draw(emb)
for _ in range(140):
    x, y, r = random.randint(0, W), random.randint(300, H - 200), random.choice([2, 3, 4, 5])
    ed.ellipse([x - r, y - r, x + r, y + r], fill=(255, random.randint(120, 200), 40, random.randint(150, 255)))
canvas = Image.alpha_composite(canvas, emb.filter(ImageFilter.GaussianBlur(1.2)))
dr = ImageDraw.Draw(canvas)


def text(t, y, size, fill, stroke):
    f = ImageFont.truetype(F, size); w = dr.textlength(t, font=f)
    while w > W - 60:
        size -= 4; f = ImageFont.truetype(F, size); w = dr.textlength(t, font=f)
    dr.text(((W - w) / 2, y), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


text(big, 70, 170, (255, 255, 255), 12)
text(sub, 265, 64, (255, 200, 70), 7)
cx = W - 190; cy = int(1040 - 180 * cx / W)
dr.ellipse([cx - 135, cy - 135, cx + 135, cy + 135], fill=(15, 10, 5, 235), outline=(255, 200, 70), width=10)
f = ImageFont.truetype(F, 175); w = dr.textlength("VS", font=f)
dr.text((cx - w / 2, cy - 110), "VS", font=f, fill=(255, 200, 70), stroke_width=6, stroke_fill=(0, 0, 0))
text(foot, 1780, 70, (255, 255, 255), 7)
canvas.convert("RGB").save(out, quality=93)
print("wrote", out)
