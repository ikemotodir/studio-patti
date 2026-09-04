# -*- coding: utf-8 -*-
"""スマホ(縦画面)用の TOP の部屋 room_m.png を組み立てる。

方針:
 ・PC版の部屋(room.png)で描いた家具や小物は、プロップ単位の切り出し
   (room_layers/objects/*.png・陰影込み)をそのまま等倍で使う。絵の質を落とさない
 ・縦画面に合わせて「奥壁を正面から見る」構図に組み替える。
   上から: ガーランド / 吊り看板 / ギャラリー+楕円窓 / 時計+Spookの額+本棚 /
   デザイン室・編集室の戸口+カウンター(COMPANYモニタ) / 床(ジュークボックス・ポスト・二人)
 ・壁と床はこのスクリプトで同じパレットで描き直す(縦横比が違うので流用できない)
 出力: room_m.png / garland_m.png / winbars_m.png / room_m.json(当たり判定)
"""
import glob
import io
import json
import os

from PIL import Image, ImageDraw

WEB = os.path.dirname(os.path.abspath(__file__))
OBJ = os.path.join(WEB, "room_layers", "objects")
W, H = 216, 480

P = {
 'ink':  (4, 2, 26),
 'n0': (0, 1, 43),  'n1': (0, 1, 57),  'n2': (1, 32, 68),  'n3': (2, 39, 74),  'n4': (10, 53, 96),
 'q0': (22, 9, 58), 'q1': (40, 11, 76), 'q2': (52, 16, 89), 'q3': (74, 21, 78), 'q4': (81, 35, 80),
 'q5': (110, 45, 107),
 'm0': (128, 36, 93), 'm1': (171, 37, 95), 'm2': (216, 65, 106), 'm3': (240, 106, 148), 'm4': (255, 159, 190),
 'r0': (92, 10, 44),  'r1': (152, 13, 57),
 'cor2': (253, 176, 140),
 'y1': (252, 200, 0), 'y2': (255, 227, 138),
 'b1': (36, 73, 185),
 'o0': (196, 106, 32), 'o1': (247, 152, 54), 'o2': (255, 214, 140),
}

im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
d = ImageDraw.Draw(im)


def C(c):
    return P[c] + (255,)


def R(x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=C(c))


def PXL(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        d.point((x, y), fill=C(c))


def DI(x, y, w, h, a, b, ph=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            PXL(xx, yy, a if (xx + yy + ph) % 2 == 0 else b)


def sprite(prefix):
    """objects/ のプロップを不透明部分だけ切り出して返す(プレフィックスで指定)。"""
    fs = glob.glob(os.path.join(OBJ, prefix + "*.png"))
    assert len(fs) == 1, prefix + " が1つに決まらない: %r" % fs
    s = Image.open(fs[0]).convert("RGBA")
    bb = s.getchannel("A").getbbox()
    return s.crop(bb)


def paste(sp, x, y):
    im.alpha_composite(sp, (x, y))


# ═══════════ 壁と床(PC版と同じパレット・同じ作法) ═══════════
R(0, 0, W, H, 'n2')
# 天井
R(0, 0, W, 8, 'ink')
R(0, 5, W, 1, 'q1')
R(0, 8, W, 2, 'q0')
for x in range(4, W, 24):
    PXL(x, 3, 'r1'); PXL(x + 1, 3, 'r1')
# 奥壁: 上が明るく、下へ多段で落ちる
WALL0, WALL1 = 10, 228
R(0, WALL0, W, 30, 'n3')
DI(0, 26, W, 6, 'n4', 'n3', 1)
DI(0, 40, W, 12, 'n3', 'n2')
R(0, 52, W, 96, 'n2')
DI(0, 148, W, 12, 'n2', 'n1')
R(0, 160, W, 68, 'n1')
DI(0, 212, W, 16, 'n1', 'n0')
R(0, 228, W, 4, 'ink')                               # 壁と床の見切り
R(0, 232, W, 2, 'q0')

# 床: 手前ほど広がる板。継ぎ目はマゼンタに光る(PC版と同じ流儀)
FL0 = 234
R(0, FL0, W, H - FL0, 'q1')
R(0, FL0, W, 3, 'q0')
SEAMS = [246, 262, 280, 300, 322, 346, 372, 400, 430, 462]
for i, y in enumerate(SEAMS):
    R(0, y, W, 1, 'm0')
    for x in range(0, W, 16):
        PXL(x + (i * 5) % 16, y + 1, 'm1')
VPX, VPY = W / 2.0, 150.0                            # 消失点(奥壁の中ほど)
for k in range(-4, 5):                               # 縦の継ぎ目は消失点へ向かう
    xb = VPX + k * 44
    for yy in range(FL0, H):
        t = (yy - VPY) / (H - VPY)
        xx = int(VPX + (xb - VPX) * t + 0.5)
        if 0 <= xx < W and yy not in SEAMS:
            PXL(xx, yy, 'q0')
for bi in range(len(SEAMS) - 1):                     # 板ごとのトーン差
    if bi % 2 == 0:
        for yy in range(SEAMS[bi] + 2, SEAMS[bi + 1] - 2):
            for xx in range(W):
                if (xx + yy + bi) % 6 == 0:
                    PXL(xx, yy, 'q2')
for x, y in [(30, 254), (150, 268), (90, 290), (180, 308), (60, 332), (140, 356), (40, 386), (170, 416), (100, 448)]:
    R(x, y, 3, 1, 'q0')
for rx in range(66, 150, 7):                         # モニタの光の床への映り込み(壁ぎわ)
    R(rx, FL0 + 1, 1, 5 - (rx // 7) % 3, 'b1')
    R(rx + 1, FL0 + 1, 1, 2, 'b1')
for sx in range(24, W - 16, 24):
    PXL(sx, 258, 'm1'); PXL(sx + 12, 276, 'm0')
DI(0, 462, W, 8, 'q1', 'q0')
DI(0, 470, W, 10, 'q0', 'ink')

# ═══════════ 戸口(正面から見た平らな入口。光が中からもれる) ═══════════
def door(x, y, w, h, warm):
    R(x - 2, y - 2, w + 4, h + 3, 'q3')              # 枠
    R(x - 2, y - 2, w + 4, 1, 'q4')
    R(x - 2, y - 2, 1, h + 3, 'q5')
    R(x, y, w, h, 'ink')                             # 開口
    a, b, c = ('r0', 'o0', 'o1') if warm else ('m0', 'm2', 'm3')
    DI(x + 1, y + 1, w - 2, h // 3, 'q0', a)         # 奥は暗い
    DI(x + 1, y + 1 + h // 3, w - 2, h // 3, a, b)   # 中ほどから明るい
    DI(x + 1, y + 1 + 2 * (h // 3), w - 2, h - 2 * (h // 3) - 1, b, c)
    R(x + 1, y + h - 5, w - 2, 4, c)                 # 足元は光でいっぱい
    for yy in range(y + 1 + h // 3, y + h - 5):      # 奥の廊下の明かりが縦に差す
        if (yy - y) % 2 == 0:
            PXL(x + w // 2, yy, c); PXL(x + w // 2 - 1, yy, c)
    R(x - 2, y - 4, w + 4, 2, 'q4')                  # まぐさ(上枠)
    R(x - 2, y - 4, w + 4, 1, 'q5')
    R(x, y + h, w, 2, 'q3')                          # 敷居
    R(x, y + h + 2, w, 1, 'ink')


DOOR_Y, DOOR_H = 156, 66
door(4, DOOR_Y, 30, DOOR_H, True)
door(182, DOOR_Y, 30, DOOR_H, False)

# ═══════════ 吊り看板(天井から下がる札。文字は既存の小型スプライト) ═══════════
def sign(x, y, w, h, textfile, warm):
    for sx in (x + 5, x + w - 6):                    # 吊りひも
        R(sx, WALL0, 1, y - WALL0, 'q3')
    R(x, y, w, h, 'q0')
    R(x, y, w, 1, 'q4'); R(x, y, 1, h, 'q4')
    R(x, y + h - 1, w, 1, 'ink'); R(x + w - 1, y, 1, h, 'ink')
    t = Image.open(os.path.join(WEB, textfile)).convert("RGBA")
    tx = x + (w - t.size[0]) // 2
    ty = y + (h - t.size[1]) // 2
    paste(t, tx, ty)


sign(2, 28, 45, 15, "sign_design_s.png", True)
sign(169, 28, 45, 16, "sign_hensyu_s.png", False)

# ═══════════ プロップを置く(PC版の切り出しを等倍で) ═══════════
HOT = {}
# ガーランド(3コマ)。room には1コマ目、動くぶんは garland_m.png へ
g = Image.open(os.path.join(WEB, "garland.png")).convert("RGBA")
GX0, GW = 84, W
gm = Image.new("RGBA", (GW * 3, 26), (0, 0, 0, 0))
for f in range(3):
    gm.alpha_composite(g.crop((f * 384 + GX0, 0, f * 384 + GX0 + GW, 26)), (f * GW, 0))
gm.save(os.path.join(WEB, "garland_m.png"))
paste(gm.crop((0, 0, GW, 26)), 0, 4)
GARLAND_Y = 4

gal = sprite("props__016_"); paste(gal, 8, 42);          HOT['gallery'] = (8, 42, gal.size[0], gal.size[1])
wbg = sprite("bg__022_");    paste(wbg, 138, 102)
win = sprite("window__001_"); paste(win, 116, 36);       HOT['window'] = (116, 36, win.size[0], win.size[1])
clk = sprite("furniture__009_"); paste(clk, 8, 112);     HOT['clock'] = (8, 112, clk.size[0], clk.size[1])
spk = sprite("props__017_"); paste(spk, 52, 104);        HOT['spook'] = (52, 104, spk.size[0], spk.size[1])
sbg = sprite("bg__027_");    paste(sbg, 132, 118)
shf = sprite("furniture__006_"); paste(shf, 130, 114)
bks = sprite("furniture__007_"); paste(bks, 132, 98)
ehn = sprite("furniture__008_"); paste(ehn, 154, 122);   HOT['book'] = (154, 122, ehn.size[0], ehn.size[1])
# カウンター: 両端の70pxを残して真ん中を詰める(端の造作を切らない)
ctr = sprite("furniture__010_")
paste(ctr.crop((0, 0, 70, ctr.size[1])), 38, 200)
paste(ctr.crop((ctr.size[0] - 70, 0, ctr.size[0], ctr.size[1])), 108, 200)
mbg = sprite("bg__021_");    paste(mbg, 48, 150)
mon = sprite("furniture__013_"); paste(mon, 58, 158);    HOT['company'] = (58, 158, mon.size[0], mon.size[1])
kbd = sprite("furniture__014_"); paste(kbd, 98, 201)
glb = sprite("furniture__011_"); paste(glb, 44, 176)
pen = sprite("props__026_");    paste(pen, 150, 185)
plt = sprite("furniture__012_"); paste(plt, 160, 188)
GROUND = 288
jbx = sprite("furniture__019_"); paste(jbx, 10, GROUND - jbx.size[1]);   HOT['jukebox'] = (10, GROUND - jbx.size[1], jbx.size[0], jbx.size[1])
pst = sprite("props__018_");    paste(pst, 172, GROUND - pst.size[1]);   HOT['post'] = (172, GROUND - pst.size[1], pst.size[0], pst.size[1])
HOT['doorL'] = (4, DOOR_Y, 30, DOOR_H)
HOT['doorR'] = (182, DOOR_Y, 30, DOOR_H)

# 窓の桟(おばけが桟の向こうを飛ぶ用)。PC版の桟から窓の範囲だけ切り出す
bars = Image.open(os.path.join(WEB, "window_bars.png")).convert("RGBA")
bars.crop((244, 10, 244 + win.size[0], 10 + win.size[1])).save(os.path.join(WEB, "winbars_m.png"))

# ═══════════ ビネット(四隅を沈める。PC版の空気感に合わせる) ═══════════
px = im.load()
for yy in range(H):
    for xx in range(W):
        dx = abs(xx - W / 2.0) / (W / 2.0)
        dy = abs(yy - 180.0) / 200.0
        dd = (dx ** 2.3 + dy ** 2.3) ** 0.5
        n = 2 if dd > 1.06 else (1 if dd > 0.93 else (1 if dd > 0.84 and (xx + yy) % 2 == 0 else 0))
        if n:
            r, g_, b, a = px[xx, yy]
            k = 0.88 if n == 1 else 0.76
            px[xx, yy] = (int(r * k), int(g_ * k), int(b * k), a)

im.convert("RGB").save(os.path.join(WEB, "room_m.png"))
meta = {
    "w": W, "h": H, "ground": GROUND, "garland_y": GARLAND_Y,
    "screen": [62, 162, 92, 28],                 # COMPANYモニタの画面の内側
    "globe": [42, 174], "clock": [8, 112], "window": [116, 36],
    "hot": {k: list(v) for k, v in HOT.items()},
}
json.dump(meta, io.open(os.path.join(WEB, "room_m.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("room_m.png", im.size, "/ garland_m.png / winbars_m.png / room_m.json")
