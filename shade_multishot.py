# -*- coding: utf-8 -*-
"""Mayu_multishot / Patti_multishot から編集室ページ用の向きを切り出し、
部屋の照明(夜・暗い部屋)に合わせたshaded版シートを作る。
- マユ: Mayu_back(後ろ姿・スクリーンを見ている) 12コマ → mayu_back_shaded.png
- パッチ: shomen(正面) 12コマ → patti_front_shaded.png
全コマ100ms均一なのでCSSの steps(12) 1.2s で再生する。原本asepriteには触らない。
先に: aseprite -b <multishot.aseprite> --sheet <ms.png> --data <ms.json> --sheet-type horizontal --list-tags --format json-array
"""
from PIL import Image
import os, json

d = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\studi\AppData\Local\Temp\claude\C--Users-studi-Desktop-Claude-apps\3485a72e-2b4a-48a5-8091-a6345c07fe32\scratchpad\chars"

AMB = (0.835, 0.851, 0.925)          # 夜のクールトーン(TOPのキャラと同係数)
EDGE = (0.78, 0.78, 0.90)
AMB_SKIN = (0.965, 0.905, 0.845)
EDGE_SKIN = (0.88, 0.84, 0.80)

def is_dark(c):
    return c[0] < 40 and c[1] < 40 and c[2] < 40

def is_skin(c):
    return c[0] >= 200 and c[1] >= 170 and c[2] >= 140 and c[0] > c[2]

def shade(im, FW):
    px = im.load()
    Wp, Hp = im.size
    orig = [[px[x, y] for y in range(Hp)] for x in range(Wp)]

    def alpha(x, y, fi):
        if not (0 <= x < Wp and 0 <= y < Hp) or x // FW != fi:
            return 0
        return orig[x][y][3]

    def probe_out(x, y, dx, dy, fi):
        for k in range(1, 4):
            tx, ty = x + dx * k, y + dy * k
            if alpha(tx, ty, fi) == 0:
                return True
            if not is_dark(orig[tx][ty][:3]):
                return False
        return False

    band = set()
    for x in range(Wp):
        fi = x // FW
        for y in range(Hp):
            c = orig[x][y]
            if c[3] == 0 or is_dark(c[:3]):
                continue
            if probe_out(x, y, -1, 0, fi) or probe_out(x, y, 0, 1, fi) \
               or probe_out(x, y, -1, 1, fi):
                band.add((x, y))
    for x in range(Wp):
        for y in range(Hp):
            c = orig[x][y]
            if c[3] == 0:
                continue
            amb = AMB_SKIN if is_skin(c) else AMB
            edg = EDGE_SKIN if is_skin(c) else EDGE
            r, g, b = (int(c[i] * amb[i]) for i in range(3))
            if (x, y) in band:
                r, g, b = int(r * edg[0]), int(g * edg[1]), int(b * edg[2])
            px[x, y] = (r, g, b, c[3])
    return im

def cut(ms_png, ms_json, tag, out_png):
    j = json.load(open(os.path.join(SRC, ms_json), encoding="utf-8"))
    sheet = Image.open(os.path.join(SRC, ms_png)).convert("RGBA")
    t = next(t for t in j["meta"]["frameTags"] if t["name"] == tag)
    fr = j["frames"][t["from"]]["frame"]
    FW, FH = fr["w"], fr["h"]
    n = t["to"] - t["from"] + 1
    out = Image.new("RGBA", (FW * n, FH), (0, 0, 0, 0))
    for i in range(n):
        f = j["frames"][t["from"] + i]["frame"]
        out.alpha_composite(sheet.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])), (i * FW, 0))
    out = shade(out, FW)
    out.save(os.path.join(d, out_png))
    print(out_png, out.size, "コマ", n, "コマ幅", FW)

cut("mayu_ms.png", "mayu_ms.json", "Mayu_back", "mayu_back_shaded.png")
cut("patti_ms.png", "patti_ms.json", "shomen", "patti_front_shaded.png")
