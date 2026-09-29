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


top = Image.open(top_p).convert("RGB").crop((0, 80, 720, 900))
bot = Image.open(bot_p).convert("RGB").crop((0, 120, 720, 1100))
top = ImageEnhance.Contrast(fit(top, W, 1100, 0.5, 0.35)).enhance(1.15)
bot = ImageEnhance.Contrast(fit(bot, W, 1100, 0.5, 0.4)).enhance(1.12)

canvas = Image.new("RGB", (W, H)); canvas.paste(top, (0, 0))
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).polygon([(0, 1040), (W, 860), (W, H), (0, H)], fill=255)
lower = Image.new("RGB", (W, H)); lower.paste(bot, (0, H - 1100))
canvas = Image.composite(lower, canvas, mask).convert("RGBA")

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).line([(0, 1040), (W, 860)], fill=(255, 190, 60, 255), width=16)
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
dr = ImageDraw.Draw(canvas)


def text(t, y, size, fill, stroke):
    f = ImageFont.truetype(F, size); w = dr.textlength(t, font=f)
    while w > W - 60:
        size -= 4; f = ImageFont.truetype(F, size); w = dr.textlength(t, font=f)
    dr.text(((W - w) / 2, y), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


text(big, 70, 170, (255, 255, 255), 12)
text(sub, 265, 64, (255, 200, 70), 7)
cx, cy = W // 2, 950
dr.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(15, 10, 5, 235), outline=(255, 200, 70), width=10)
f = ImageFont.truetype(F, 200); w = dr.textlength("VS", font=f)
dr.text((cx - w / 2, cy - 125), "VS", font=f, fill=(255, 200, 70), stroke_width=6, stroke_fill=(0, 0, 0))
text(foot, 1780, 70, (255, 255, 255), 7)
canvas.convert("RGB").save(out, quality=93)
print("wrote", out)
