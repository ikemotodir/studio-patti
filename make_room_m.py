# -*- coding: utf-8 -*-
"""スマホ(縦画面)用の TOP の部屋 room_m.png を組み立てる。

方針:
 ・PC版の部屋(room.png)で描いた家具や小物は、プロップ単位の切り出し
   (room_layers/objects/*.png・陰影込み)をそのまま等倍で使う。絵の質を落とさない
 ・縦画面に合わせて「奥壁を正面から見る」構図に組み替える。
   上から: ガーランド / ギャラリー+楕円窓 / 時計・Spookの額・絵本の小棚 /
   看板(戸口のすぐ上) / デザイン室・編集室の戸口+カウンター(COMPANYモニタ) /
   床(ジュークボックス・ポスト・二人)
 ・壁と床はこのスクリプトで同じパレットで描き直す(縦横比が違うので流用できない)
 ・置いた物は全部 PLACED に登録し、意図しない重なりがあれば build を失敗させる
   (看板が物を隠す・地球儀がモニタに乗る、といった事故を構造的に防ぐ)
 出力: room_m.png / garland_m.png / winbars_m.png / globe_spin_m.png / room_m.json
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
PLACED = []                      # (名前, x, y, w, h) — 重なり検査用


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


def put(name, sp, x, y):
    """プロップを置いて、位置を登録する。"""
    im.alpha_composite(sp, (x, y))
    PLACED.append((name, x, y, sp.size[0], sp.size[1]))
    return (x, y, sp.size[0], sp.size[1])


def mark(name, x, y, w, h):
    PLACED.append((name, x, y, w, h))
    return (x, y, w, h)


# ═══════════ 壁と床(PC版と同じパレット・同じ作法) ═══════════
WALL0, WALL1 = 10, 214                              # 奥壁の範囲(下端で床と見切る)
R(0, 0, W, H, 'n2')
# 天井
R(0, 0, W, 8, 'ink')
R(0, 5, W, 1, 'q1')
R(0, 8, W, 2, 'q0')
for x in range(4, W, 24):
    PXL(x, 3, 'r1'); PXL(x + 1, 3, 'r1')
# 奥壁: 上が明るく、下へ多段で落ちる
R(0, WALL0, W, 30, 'n3')
DI(0, 26, W, 6, 'n4', 'n3', 1)
DI(0, 40, W, 12, 'n3', 'n2')
R(0, 52, W, 84, 'n2')
DI(0, 136, W, 12, 'n2', 'n1')
R(0, 148, W, WALL1 - 148, 'n1')
DI(0, 200, W, WALL1 - 200, 'n1', 'n0')
R(0, WALL1, W, 4, 'ink')                             # 壁と床の見切り
R(0, WALL1 + 4, W, 2, 'q0')

# 床: 手前ほど広がる板。継ぎ目はマゼンタに光る(PC版と同じ流儀)
FL0 = WALL1 + 6
R(0, FL0, W, H - FL0, 'q1')
R(0, FL0, W, 3, 'q0')
SEAMS = [232, 248, 266, 286, 308, 332, 358, 386, 416, 448]
for i, y in enumerate(SEAMS):
    R(0, y, W, 1, 'm0')
    for x in range(0, W, 16):
        PXL(x + (i * 5) % 16, y + 1, 'm1')
VPX, VPY = W / 2.0, 140.0                            # 消失点(奥壁の中ほど)
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
for x, y in [(30, 240), (150, 256), (90, 276), (180, 296), (60, 318), (140, 344), (40, 372), (170, 402), (100, 434)]:
    R(x, y, 3, 1, 'q0')
for sx in range(24, W - 16, 24):
    PXL(sx, 244, 'm1'); PXL(sx + 12, 262, 'm0')
DI(0, 462, W, 8, 'q1', 'q0')
DI(0, 470, W, 10, 'q0', 'ink')

# ═══════════ 戸口(正面から見た平らな入口。光が中からもれる) ═══════════
def door(name, x, y, w, h, warm):
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
    # 登録はまぐさ〜敷居まで(枠込み)。開口そのものは HOT に別登録
    mark(name, x - 2, y - 4, w + 4, h + 7)
    return (x, y, w, h)


DOOR_Y, DOOR_H = 149, 62                             # 敷居の下端が壁と床の見切りに乗る
DOOR_L = door('doorL', 6, DOOR_Y, 30, DOOR_H, True)
DOOR_R = door('doorR', 178, DOOR_Y, 30, DOOR_H, False)

# ═══════════ 看板(戸口のすぐ上に掛かる札。まぐさの上に直に乗せる) ═══════════
def plaque(name, x, y, w, h, textfile):
    R(x, y, w, h, 'q0')
    R(x, y, w, 1, 'q4'); R(x, y, 1, h, 'q4')
    R(x, y + h - 1, w, 1, 'ink'); R(x + w - 1, y, 1, h, 'ink')
    t = Image.open(os.path.join(WEB, textfile)).convert("RGBA")
    tx = x + (w - t.size[0]) // 2
    ty = y + (h - t.size[1]) // 2
    im.alpha_composite(t, (tx, ty))
    return mark(name, x, y, w, h)


SIGN_W, SIGN_H = 45, 16
SIGN_Y = DOOR_Y - 4 - SIGN_H                         # 札の下端 = まぐさの上端
def sign_x(door):                                    # 戸口(枠込み)の中心に札の中心を合わせる
    cx = (door[0] - 2) + (door[2] + 4) / 2.0
    return max(0, min(W - SIGN_W, int(round(cx - SIGN_W / 2.0))))
SIGN_L = plaque('signL', sign_x(DOOR_L), SIGN_Y, SIGN_W, SIGN_H, "sign_design_s.png")
SIGN_R = plaque('signR', sign_x(DOOR_R), SIGN_Y, SIGN_W, SIGN_H, "sign_hensyu_s.png")

# ═══════════ プロップを置く(PC版の切り出しを等倍で) ═══════════
HOT = {}
# ガーランド(3コマ)。room には1コマ目、動くぶんは garland_m.png へ
g = Image.open(os.path.join(WEB, "garland.png")).convert("RGBA")
GX0, GW = 84, W
gm = Image.new("RGBA", (GW * 3, 26), (0, 0, 0, 0))
for f in range(3):
    gm.alpha_composite(g.crop((f * 384 + GX0, 0, f * 384 + GX0 + GW, 26)), (f * GW, 0))
gm.save(os.path.join(WEB, "garland_m.png"))
GARLAND_Y = 4
put('garland', gm.crop((0, 0, GW, 26)), 0, GARLAND_Y)

# 上段: ギャラリー(左)と楕円窓(右)
HOT['gallery'] = put('gallery', sprite("props__016_"), 8, 30)
win = sprite("window__001_")
# 窓ガラスの中の「暗い雲」はスマホでは欠けに見えるので、まわりの空のディザで埋める
wp = win.load()
for yy in range(6, 34):
    for xx in range(8, 46):
        r_, g_, b_, a_ = wp[xx, yy]
        if a_ and r_ + g_ + b_ < 60 and (r_, g_, b_) != P['ink']:
            for dx in range(1, 40):                      # 同じ行・同じ市松位相の空の色を借りる
                for sx in (xx - 2 * dx, xx + 2 * dx):
                    if 8 <= sx < 46 and sum(wp[sx, yy][:3]) >= 60 and wp[sx, yy][3]:
                        wp[xx, yy] = wp[sx, yy]; break
                else:
                    continue
                break
HOT['window'] = put('window', win, 116, 30)

# 中段: 時計(左) / Spookの額(中央・モニタの真上) / 絵本と鉢植えの小棚(右)
HOT['clock'] = put('clock', sprite("furniture__009_"), 6, 94)
HOT['spook'] = put('spook', sprite("props__017_"), 76, 100)
SHELF = (DOOR_R[0] - 2, 125, DOOR_R[2] + 4, 3)       # 戸口の幅と同じ小さな棚板
R(SHELF[0], SHELF[1], SHELF[2], 1, 'q4')
R(SHELF[0], SHELF[1] + 1, SHELF[2], 1, 'q3')
R(SHELF[0], SHELF[1] + 2, SHELF[2], 1, 'ink')
mark('shelf', *SHELF)
ehn = sprite("furniture__008_")
HOT['book'] = put('book', ehn, SHELF[0] + 2, SHELF[1] - ehn.size[1])
plt = sprite("furniture__012_")
put('plant', plt, SHELF[0] + SHELF[2] - plt.size[0], SHELF[1] - plt.size[1])

# 下段: カウンター(両端66pxを残して真ん中を詰める。端の造作を切らない)
ctr = sprite("furniture__010_")
CTR_X, CTR_Y, END = 42, 200, 66
put('counterL', ctr.crop((0, 0, END, ctr.size[1])), CTR_X, CTR_Y)
put('counterR', ctr.crop((ctr.size[0] - END, 0, ctr.size[0], ctr.size[1])), CTR_X + END, CTR_Y)
CTR_W = END * 2
glb = sprite("furniture__011_")
GLOBE = put('globe', glb, CTR_X, CTR_Y - glb.size[1])                    # 左端に地球儀
mon = sprite("furniture__013_")
MON = put('monitor', mon, GLOBE[0] + GLOBE[2] + 2, 158)                  # その右にモニタ
HOT['company'] = MON
SCREEN = [MON[0] + 4, MON[1] + 4, 92, 28]                                # 画面の内側
kbd = sprite("furniture__014_")
put('keyboard', kbd, MON[0] + (MON[2] - kbd.size[0]) // 2, CTR_Y + 1)
pen = sprite("props__026_")
put('pen', pen, MON[0] + MON[2] + 2, CTR_Y - pen.size[1])

# 床の上: ジュークボックス(左端)とポスト(右端)。戸口の前には立たせない
GROUND = 288
jbx = sprite("furniture__019_")
HOT['jukebox'] = put('jukebox', jbx, 0, GROUND - jbx.size[1])
pst = sprite("props__018_")
HOT['post'] = put('post', pst, DOOR_R[0] - 2, GROUND - pst.size[1])
HOT['doorL'] = DOOR_L
HOT['doorR'] = DOOR_R

# 二人の居場所(HTML側と同じ数字)。重なり検査のために登録だけする
MAYU = mark('mayu', 60 + 9, GROUND - 44, 57, 44)          # 76x58 を .75 倍(足元基準)
PATTI = mark('patti(walk)', 126 + 4, GROUND - 36, 10 + 27, 36)  # x 126..136 を歩く

# 窓の桟(おばけが桟の向こうを飛ぶ用)。PC版の桟から窓の範囲だけ切り出す
bars = Image.open(os.path.join(WEB, "window_bars.png")).convert("RGBA")
bars.crop((244, 10, 244 + win.size[0], 10 + win.size[1])).save(os.path.join(WEB, "winbars_m.png"))

# 地球儀の回転アニメ: PC版のコマ(背景つき)から、地球儀の形だけを抜く
gs = Image.open(os.path.join(WEB, "globe_spin.png")).convert("RGBA")
gmask = glb.getchannel("A")
gsm = Image.new("RGBA", (glb.size[0] * 6, glb.size[1]), (0, 0, 0, 0))
for f in range(6):
    fr = gs.crop((f * 24 + 2, 2, f * 24 + 2 + glb.size[0], 2 + glb.size[1]))
    fr.putalpha(gmask)
    gsm.paste(fr, (f * glb.size[0], 0))
gsm.save(os.path.join(WEB, "globe_spin_m.png"))

# ═══════════ 重なり検査(意図した重なり以外があれば失敗) ═══════════
ALLOWED = {
    frozenset(('monitor', 'counterL')), frozenset(('monitor', 'counterR')),   # モニタの台はカウンターに乗る
    frozenset(('keyboard', 'counterL')), frozenset(('keyboard', 'counterR')),
    frozenset(('keyboard', 'monitor')),                                       # PC版と同じくキーボードは台の手前
    frozenset(('jukebox', 'doorL')),                                          # 見切りの1行(敷居下のインク線)だけ
}
def isect(a, b):
    ax0, ay0, ax1, ay1 = a[1], a[2], a[1] + a[3], a[2] + a[4]
    bx0, by0, bx1, by1 = b[1], b[2], b[1] + b[3], b[2] + b[4]
    return min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0)
bad = []
for i in range(len(PLACED)):
    for j in range(i + 1, len(PLACED)):
        a, b = PLACED[i], PLACED[j]
        ow, oh = isect(a, b)
        if ow > 0 and oh > 0:
            key = frozenset((a[0], b[0]))
            if key == frozenset(('jukebox', 'doorL')) and oh <= 1:
                continue
            if key not in ALLOWED:
                bad.append("%s x %s (%dx%d)" % (a[0], b[0], ow, oh))
for nm, x, y, w, h in PLACED:
    if x < 0 or y < 0 or x + w > W or y + h > H:
        bad.append("%s が画面からはみ出す (%d,%d,%d,%d)" % (nm, x, y, w, h))
if bad:
    raise SystemExit("重なり事故:\n  " + "\n  ".join(bad))

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
    "screen": SCREEN,                            # COMPANYモニタの画面の内側
    "globe": list(GLOBE[:2]), "globe_size": list(GLOBE[2:]),
    "clock": list(HOT['clock'][:2]), "window": list(HOT['window'][:2]),
    "signs": {"L": list(SIGN_L), "R": list(SIGN_R)},
    "hot": {k: list(v) for k, v in HOT.items()},
    "placed": [list(p) for p in PLACED],
}
json.dump(meta, io.open(os.path.join(WEB, "room_m.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("room_m.png", im.size, "/ garland_m.png / winbars_m.png / globe_spin_m.png / room_m.json  重なり事故 0")
