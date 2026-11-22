#!/usr/bin/env python3
"""Generate a high-resolution SEM showcase with Night Tariff from original PNG.

Requires Pillow. Intended for deterministic rendering by GitHub Actions,
so the real binary PNG lands in the repository without embedding base64.
"""
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont

SOURCE = Path("assets/Sungrow Energy Manager for Home Assistant(1).png")
OUTPUT = Path("assets/sungrow-energy-manager-night-tariff.png")
original = Image.open(SOURCE).convert("RGB")
w, h = original.size
scale = w / 1672
out = Image.new("RGB", (w, h + round(330 * scale)), (239, 248, 255))
out.paste(original, (0, 0))
draw = ImageDraw.Draw(out)


def px(v):
    return round(v * scale)


def box(coords, radius, color, outline=None, width=1):
    draw.rounded_rectangle([px(v) for v in coords], radius=px(radius),
                           fill=color, outline=outline, width=px(width))


def caption(x, y, words, size, color, bold=False):
    fontname = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    font = ImageFont.truetype(fontname, px(size))
    draw.text((px(x), px(y)), words, font=font, fill=color)


for y in range(h, out.height):
    frac = (y - h) / max(out.height - h - 1, 1)
    color = (round(247 - 19 * frac), round(251 - 10 * frac), 255)
    draw.line((0, y, w, y), fill=color)

box((35, 966, 212, 1010), 22, (223, 235, 255))
caption(55, 976, "NEW FEATURE", 19, (33, 102, 223), True)
caption(232, 959, "Night Tariff Mode", 37, (11, 31, 62), True)
caption(45, 1030, "Automated scene switching during discounted nights - independent of Grid Target.",
        19, (83, 105, 134))

panels = [
    (40, 1087, 535, 1207),
    (550, 1087, 1045, 1207),
    (1060, 1087, 1632, 1207),
]
for left, top, right, bottom in panels:
    box((left + 4, top + 8, right + 4, bottom + 8), 22, (204, 222, 242))
    box((left, top, right, bottom), 22, (255, 255, 255),
        outline=(216, 230, 245), width=2)

box((61, 1110, 114, 1162), 15, (224, 237, 255))
draw.ellipse([px(i) for i in (76, 1119, 104, 1147)], fill=(38, 98, 219))
draw.ellipse([px(i) for i in (87, 1115, 109, 1137)], fill=(224, 237, 255))
caption(128, 1100, "23:00 - 07:00", 28, (10, 31, 65), True)
caption(128, 1145, "Discount window - editable", 17, (88, 108, 137))

box((571, 1110, 624, 1162), 15, (225, 247, 239))
draw.rectangle([px(i) for i in (582, 1123, 614, 1149)],
               outline=(23, 156, 99), width=px(3))
draw.line([(px(582), px(1131)), (px(614), px(1131))],
          fill=(23, 156, 99), width=px(3))
caption(638, 1100, "Sun - Thu", 28, (10, 31, 65), True)
caption(638, 1145, "Friday/Saturday starts excluded", 16, (88, 108, 137))

box((1081, 1110, 1134, 1162), 15, (230, 239, 255))
draw.polygon([(px(x), px(y)) for x, y in [
    (1111, 1117), (1091, 1141), (1105, 1141),
    (1101, 1155), (1126, 1129), (1113, 1129),
]], fill=(36, 109, 227))
caption(1149, 1099, "Grid at night - Battery by day", 22, (10, 31, 65), True)
caption(1149, 1144, "No-discharge scene / Max-discharge scene", 15, (88, 108, 137))
caption(45, 1244,
        "Self-Consumption mode changes automatically. Verify the no-discharge scene on your Sungrow inverter.",
        13, (90, 116, 147))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
out.save(OUTPUT, optimize=True)
legacy = Path("docs/images/sungrow_grid_pid_energy_infographic.png")
legacy.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(OUTPUT, legacy)
print(f"Created {OUTPUT}: {out.width}x{out.height}, {OUTPUT.stat().st_size} bytes")
print(f"Refreshed legacy infographic path: {legacy}")
