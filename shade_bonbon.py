# -*- coding: utf-8 -*-
"""bonbon.png → bonbon_shaded.png
月のおばけ。暗い紫味を、窓の青白い月の色味に寄せる。原本Bonbon.asepriteは不触。"""
from PIL import Image
import os

d = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(d, "bonbon.png")).convert("RGBA")
px = im.load()
W, H = im.size
MOON = (198, 222, 252)      # 月あかりの青白

for x in range(W):
    for y in range(H):
        r, g, b, a = px[x, y]
        if a == 0:
            continue
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if lum < 40:        # 輪郭や目の黒はそのまま
            continue
        t = 0.34 if lum > 120 else 0.24
        px[x, y] = (int(r + (MOON[0] - r) * t),
                    int(g + (MOON[1] - g) * t),
                    int(b + (MOON[2] - b) * t), a)

im.save(os.path.join(d, "bonbon_shaded.png"))
print("bonbon_shaded.png written", im.size)
