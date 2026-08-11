"""mayu.png → mayu_shaded.png
部屋の照明(夜・暗い部屋)に合わせてマユちゃんを環境トーンに落とす。
- 全色を夜のクールトーンへ(パッチくんと同じ係数)
- 輪郭の左・下に1段深い影バンド(シルエット判定つき、目や口など内部の黒には反応しない)
原本 Mayu.aseprite には一切触らない。
"""
from PIL import Image
import os, json

d = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(d, "mayu.png")).convert("RGBA")
meta = json.load(open(os.path.join(d, "mayu.json")))
FW = meta["frames"][0]["frame"]["w"]
px = im.load()
Wp, Hp = im.size

AMB = (0.835, 0.851, 0.925)          # 夜のクールトーン(パッチくんと同係数)
EDGE = (0.78, 0.78, 0.90)            # 影バンド追加係数

orig = [[px[x, y] for y in range(Hp)] for x in range(Wp)]

def alpha(x, y, fi):
    if not (0 <= x < Wp and 0 <= y < Hp) or x // FW != fi:
        return 0
    return orig[x][y][3]

def is_dark(c):
    return c[0] < 40 and c[1] < 40 and c[2] < 40

def probe_out(x, y, dx, dy, fi):
    """輪郭(暗色)を通って3px以内に透明へ抜けるならシルエット側"""
    for k in range(1, 4):
        tx, ty = x + dx * k, y + dy * k
        a = alpha(tx, ty, fi)
        if a == 0:
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

def is_skin(c):
    return c[0] >= 200 and c[1] >= 170 and c[2] >= 140 and c[0] > c[2]

AMB_SKIN = (0.965, 0.905, 0.845)     # 肌は血色を残す(クール寄せしない)
EDGE_SKIN = (0.88, 0.84, 0.80)

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

# ── 足先の描き足し ─────────────────────────────────────────
# Mayu.aseprite のキャンバスは70x58で、伸ばした足がコマの右端(x=69)で
# 切り落とされている。そのまま部屋に置くと「足がカーペットの下に潜っている」
# ように見えるので、コマを右へPAD分広げて足先を丸く閉じる。
PAD = 6
NFW = FW + PAD
NF = Wp // FW
wide = Image.new("RGBA", (NFW * NF, Hp), (0, 0, 0, 0))
for fi in range(NF):
    wide.alpha_composite(im.crop((fi * FW, 0, fi * FW + FW, Hp)), (fi * NFW, 0))
wp = wide.load()
for fi in range(NF):
    ex = fi * NFW + FW - 1                    # 切り落とされている最終列
    runs, y = [], 0
    while y < Hp:                             # 最終列で縦に続いている区間を拾う
        if wp[ex, y][3]:
            y0 = y
            while y < Hp and wp[ex, y][3]:
                y += 1
            runs.append((y0, y - 1))
        else:
            y += 1
    for (y0, y1) in runs:
        if y1 - y0 < 2:                       # ごく短い切れ端は伸ばさない
            continue
        for k in range(1, PAD + 1):
            top = y0 + k * 2                  # 上から2pxずつ絞って丸く納める
            if top > y1:
                break
            for yy in range(top, y1 + 1):
                wp[ex + k, yy] = wp[ex, yy]
            wp[ex + k, top] = wp[ex, y0]      # 上端に輪郭色を置いて縁を締める

im = wide
im.save(os.path.join(d, "mayu_shaded.png"))
# コマ幅が変わるので専用JSONも書き出す(Aseprite出力の mayu.json は触らない)
meta["frames"] = [{"filename": f["filename"],
                   "frame": {"x": i * NFW, "y": 0, "w": NFW, "h": Hp},
                   "rotated": False, "trimmed": False,
                   "spriteSourceSize": {"x": 0, "y": 0, "w": NFW, "h": Hp},
                   "sourceSize": {"w": NFW, "h": Hp},
                   "duration": f["duration"]}
                  for i, f in enumerate(meta["frames"])]
meta["meta"]["size"] = {"w": NFW * NF, "h": Hp}
json.dump(meta, open(os.path.join(d, "mayu_shaded.json"), "w"), ensure_ascii=False)
print("mayu_shaded.png / mayu_shaded.json written", im.size, "コマ幅", NFW)
