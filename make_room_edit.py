# -*- coding: utf-8 -*-
"""編集室(CONTENTS CREATIVE)の部屋 - 池本さんスケッチ準拠。
TOPの部屋(make_room.py)と同じ描法・同じパレット・同じ照明パイプライン。
レイアウト: 左壁=スタジオへ戻る戸口(白光)+スタジオ看板 / 奥壁=メニューパネル+大スクリーン+
カテゴリ表示+数字ボタンパネル / 手前=編集卓(ボタンいっぱい)+ゲーミングチェア。
Layers: bg / furniture / props / light
"""
from PIL import Image, ImageDraw, ImageChops
import os, json, math, io, re

WEB = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(WEB, "room_edit_layers")
os.makedirs(LAY, exist_ok=True)
W, H = 384, 240

P = {
 'ink':  (4, 2, 26),
 'n0': (0, 1, 43),  'n1': (0, 1, 57),  'n2': (1, 32, 68),  'n3': (2, 39, 74),  'n4': (10, 53, 96),
 'q0': (22, 9, 58), 'q1': (40, 11, 76),'q2': (52, 16, 89), 'q3': (74, 21, 78), 'q4': (81, 35, 80),
 'q5': (110, 45, 107),
 'mauve': (168, 96, 139),
 'm0': (128, 36, 93), 'm1': (171, 37, 95), 'm2': (216, 65, 106), 'm3': (240, 106, 148), 'm4': (255, 159, 190),
 'r0': (92, 10, 44),  'r1': (152, 13, 57), 'r2': (194, 44, 80),
 'brick': (145, 49, 61),
 'cor': (252, 125, 103), 'cor2': (253, 176, 140), 'cream': (253, 227, 209),
 'y0': (184, 122, 14), 'y1': (252, 200, 0), 'y2': (255, 227, 138),
 'g0': (20, 73, 60), 'g1': (58, 168, 138), 'g2': (112, 215, 180), 'g3': (189, 243, 223),
 'b0': (21, 47, 116), 'b1': (36, 73, 185), 'b2': (49, 93, 196), 'b3': (91, 138, 232),
 'b4': (156, 199, 247), 'b5': (217, 236, 255),
 'gray0': (110, 102, 96), 'gray1': (154, 144, 138), 'gray2': (201, 194, 184),
 'wht': (255, 255, 255),
 'o0': (196, 106, 32), 'o1': (247, 152, 54), 'o2': (255, 214, 140),
 'cool1': (96, 86, 168), 'cool2': (150, 140, 214),
 'ivory': (247, 238, 216), 'ivory2': (206, 194, 172),
 'pnk0': (132, 54, 96), 'pnk1': (186, 88, 140),
 'pnk2': (236, 148, 190), 'pnkc': (255, 212, 232),
 'wwht': (58, 56, 92),
 'cyn0': (16, 84, 104), 'cyn1': (44, 164, 186), 'cyn2': (126, 224, 235), 'cync': (214, 250, 252),
}

names = ["bg", "furniture", "props", "light"]
L = {n: Image.new("RGBA", (W, H), (0, 0, 0, 0)) for n in names}
D = {n: ImageDraw.Draw(L[n]) for n in names}

def C(c, a=255):
    return (P[c] + (a,)) if isinstance(c, str) else (tuple(c) + (a,))

# ── オブジェクト単位の切り分け(Aseprite のレイヤー分け用) ──
OWNER = {n: Image.new("I", (W, H), 0) for n in names}
OD = {n: ImageDraw.Draw(OWNER[n]) for n in names}
OBJ_ID, _OSEQ, _OCUR = {}, [0], [None]

def obj(name=None):
    _OCUR[0] = name

def _oid(l):
    if _OCUR[0] is None:
        return None
    key = (l, _OCUR[0])
    if key not in OBJ_ID:
        _OSEQ[0] += 1
        OBJ_ID[key] = _OSEQ[0]
    return OBJ_ID[key]

def R(l, x, y, w, h, c, a=255):
    if w <= 0 or h <= 0: return
    D[l].rectangle([x, y, x + w - 1, y + h - 1], fill=C(c, a))
    i = _oid(l)
    if i: OD[l].rectangle([x, y, x + w - 1, y + h - 1], fill=i)

def PXL(l, x, y, c, a=255):
    D[l].point((x, y), fill=C(c, a))
    i = _oid(l)
    if i: OD[l].point((x, y), fill=i)

def O(l, x, y, w, h, fill, out):
    R(l, x, y, w, h, out)
    R(l, x + 1, y + 1, w - 2, h - 2, fill)

def DI(l, x, y, w, h, cA, cB, ph=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            PXL(l, xx, yy, cA if (xx + yy + ph) % 2 == 0 else cB)

def EL(l, x0, y0, x1, y1, fill=None, out=None, ow=1):
    D[l].ellipse([x0, y0, x1, y1], fill=C(fill) if fill else None,
                 outline=C(out) if out else None, width=ow)
    i = _oid(l)
    if i:
        if fill:
            OD[l].ellipse([x0, y0, x1, y1], fill=i)
        else:
            OD[l].ellipse([x0, y0, x1, y1], outline=i, width=ow)

def dpatch(l, x, y, w, h, c, den=2, ph=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx + yy + ph) % den == 0:
                PXL(l, xx, yy, c)

# 数字(5x5) - 数字ボタン用
NFONT = {
 '1': "010 110 010 010 111", '2': "110 001 010 100 111",
 '3': "110 001 010 001 110", '4': "101 101 111 001 001",
}
def NTXT(l, x, y, ch, c):
    rows = NFONT[ch].split()
    for ry, row in enumerate(rows):
        for rx, bit in enumerate(row):
            if bit == '1': PXL(l, x + rx, y + ry, c)

# ═══════════════ 主要座標(ここだけ見れば配置が分かる) ═══════════════
MENU = (47, 24, 79, 114)        # メニューパネル外形 x,y,w,h (デスクに立つボード)
SCR  = (134, 26, 142, 80)       # スクリーン画面(16:9, センター205=チェアと同心)
CATP = (283, 22, 55, 26)        # カテゴリ名表示パネル
BTNP = (283, 54, 55, 56)        # 数字ボタンパネル
BTNC = [(297, 69), (324, 69), (297, 95), (324, 95)]   # 丸ボタン中心(18px)
DESK_Y = 138                    # 編集卓の天板
CHAIR = (185, 116)              # ゲーミングチェア左上(センター205)
EDITC = (150, 120, 110)         # 編集機 x,y,幅 (センター205)

# ═══════════════ bg : TOPの部屋と同じ壁・床・天井 ═══════════════
obj()
R('bg', 0, 0, W, H, 'n2')
R('bg', 0, 0, W, 10, 'ink')
R('bg', 0, 6, W, 1, 'q1')
R('bg', 0, 10, W, 2, 'q0')
for x in range(4, W, 24):
    PXL('bg', x, 4, 'r1'); PXL('bg', x + 1, 4, 'r1')
for x in range(68, W - 48, 48):
    R('bg', x, 10, 5, 6, 'm1')
    R('bg', x, 10, 5, 1, 'm0')
    PXL('bg', x + 2, 13, 'm0')

R('bg', 0, 12, W, 20, 'n3')
DI('bg', 0, 24, W, 4, 'n4', 'n3', 1)
DI('bg', 0, 32, W, 8, 'n3', 'n2')
R('bg', 0, 40, W, 56, 'n2')
DI('bg', 0, 96, W, 8, 'n2', 'n1')
R('bg', 0, 104, W, 38, 'n1')
DI('bg', 0, 132, W, 10, 'n1', 'n0')
for x in [96, 192, 288]:
    R('bg', x, 12, 1, 130, 'n1')
R('bg', 0, 142, W, 4, 'ink')
R('bg', 0, 146, W, 2, 'q0')

R('bg', 0, 148, W, 92, 'q1')
R('bg', 0, 148, W, 3, 'q0')
for i, y in enumerate([161, 175, 189, 203, 217, 231]):
    R('bg', 0, y, W, 1, 'm0')
    for x in range(0, W, 16):
        PXL('bg', x + (i * 5) % 16, y + 1, 'm1')
for i, x in enumerate(range(0, W + 32, 32)):
    for j, yy in enumerate([(149, 12), (162, 13), (176, 13), (190, 13), (204, 13), (218, 13), (232, 8)]):
        xo = (x + (16 if j % 2 else 0)) % (W + 32)
        R('bg', xo, yy[0], 1, yy[1], 'q0')
for x, y in [(60,168),(150,183),(250,170),(340,180),(90,194),(230,194),(160,222),(320,226),(50,232)]:
    R('bg', x, y, 3, 1, 'q0')
# スクリーンから出る光の床への映り込み
for rx in range(150, 286, 7):
    R('bg', rx, 149, 1, 5 - (rx // 7) % 3, 'b1')
    R('bg', rx + 1, 149, 1, 2, 'b1')
for bi, (by0, by1) in enumerate([(149,161),(162,175),(176,189),(190,203),(204,217),(218,231)]):
    if bi % 2 == 0:
        for yy5 in range(by0 + 2, by1 - 2):
            for xx5 in range(0, W):
                if (xx5 + yy5 + bi) % 6 == 0:
                    PXL('bg', xx5, yy5, 'q2')
for wx5, wy5 in [(88,171),(132,178),(210,166),(262,181),(150,186),(238,192),(302,188),
                 (180,232),(280,226),(120,224)]:
    PXL('bg', wx5, wy5, 'q0'); PXL('bg', wx5 + 1, wy5, 'q2')
for si, sx5 in enumerate(range(56, W - 48, 24)):
    PXL('bg', sx5, 160, 'm1' if si % 2 else 'cyn1')       # 走行灯はピンクとシアンの交互
    PXL('bg', sx5 + 12, 174, 'm0' if si % 2 else 'cyn0')
DI('bg', 0, 224, W, 6, 'q1', 'q0')
DI('bg', 0, 230, W, 10, 'q0', 'ink')

# ─── シアターの赤絨毯ランナー(スクリーンへ誘う) ───
for yy in range(150, 236):
    t = (yy - 150) / 86.0
    half = int(52 + 30 * t + 0.5)
    x0c, x1c = 205 - half, 205 + half
    for xx in range(x0c, x1c + 1):
        if xx == x0c or xx == x1c:
            c = 'm0'
        elif xx <= x0c + 2 or xx >= x1c - 2:
            c = 'r1'
        else:
            c = 'r1' if (xx * 3 + yy * 7) % 13 == 0 else 'r0'
        if yy >= 226 and (xx + yy) % 2:
            c = 'q0'                                       # 手前は床のビネットと同じく沈める
        PXL('bg', xx, yy, c)

# ─── 側壁(TOPと同じ台形) ───
def side_wall(left):
    for i in range(47):
        xx = i if left else W - 1 - i
        t = i / 46.0
        ytop = int(2 + 12 * t + 0.5)
        ybot = int(234 - 66 * t + 0.5)
        for yy in range(ytop, ybot + 1):
            if yy <= ytop + 1:
                c = 'ink'
            elif yy <= ytop + 3:
                c = 'q1'
            elif yy >= ybot - 1:
                c = 'q0'
            elif yy == ybot - 2:
                c = 'ink'
            elif yy >= ybot - 5:
                c = 'q1'
            else:
                base = 'n1' if t > 0.55 else 'n2'
                c = 'n0' if (xx * 13 + yy * 7) % 37 == 0 else base
            PXL('bg', xx, yy, c)
    cx0 = 46 if left else W - 47
    R('bg', cx0, 13, 1, 156, 'ink')
    R('bg', cx0 + (1 if left else -1), 14, 1, 154, 'n3')
side_wall(True)
side_wall(False)

# ═══════════════ furniture ═══════════════

# ─── 左の壁: スタジオ(TOPの部屋)へ戻る戸口。白色の光がもれる ───
obj('スタジオへの戸口')
for xx in range(10, 39):
    t = (xx - 10) / 28.0
    ytopD = int(58 - 8 * t + 0.5)
    ybotD = int(214 - 46 * t + 0.5)
    for yy in range(ytopD, ybotD):
        rel = (yy - ytopD) / float(ybotD - ytopD)
        if xx <= 11 or xx >= 37:
            c = 'q3'
        elif rel < 0.10:
            c = 'gray0' if (xx + yy) % 2 else 'q4'
        elif rel < 0.34:
            c = 'gray0' if (xx + yy) % 2 else 'gray1'
        elif rel < 0.62:
            c = 'gray1' if (xx + yy) % 2 else 'gray2'
        elif rel < 0.86:
            c = 'gray2'
        else:
            c = 'wht' if (xx + yy) % 2 else 'gray2'
        PXL('furniture', xx, yy, c)
    PXL('furniture', xx, ytopD, 'ink')
    PXL('furniture', xx, ybotD, 'ink')
R('furniture', 9, 58, 1, 157, 'ink')
R('furniture', 39, 50, 1, 119, 'ink')
R('furniture', 8, 58, 1, 157, 'q1')
for k in range(4):
    R('furniture', 14 + k * 6, 62 - k, 1, 140 - k * 10, 'gray2' if k % 2 else 'gray1')

# ─── 左の看板: スタジオ(白の電飾・TOPの看板と同じ台形様式) ───
def bake_sign_img(img_name, x0, x1, ytop_fn, yoff, core):
    m = Image.open(os.path.join(WEB, img_name)).convert('RGBA')
    tw, th = m.size
    ox = x0 + (x1 - x0 + 1 - tw) // 2
    mp = m.load()
    for gy in range(th):
        for gx in range(tw):
            if mp[gx, gy][3] > 0:
                xx = ox + gx
                PXL('furniture', xx, ytop_fn(xx) + yoff + gy, core)

obj('スタジオの看板')
def signS_top(xx):
    return int(21 + 8 * (xx - 4) / 36.0 + 0.5)
for xx in range(4, 41):
    t = (xx - 4) / 36.0
    ytopS = signS_top(xx)
    ybotS = int(45 + 1 * t + 0.5)
    for yy in range(ytopS, ybotS + 1):
        if yy == ytopS or yy == ybotS:
            c = 'ink'
        elif yy == ytopS + 1:
            c = 'q4'
        elif yy == ybotS - 1:
            c = 'q2'
        else:
            c = 'q0'
        PXL('furniture', xx, yy, c)
R('furniture', 3, 21, 1, 25, 'ink'); R('furniture', 41, 29, 1, 18, 'ink')
PXL('furniture', 5, 23, 'wht'); PXL('furniture', 39, 44, 'wht')
bake_sign_img('sign_studio_s.png', 4, 40, signS_top, 5, 'wht')

# ─── 奥壁: 大スクリーン(壁掛け・16:9) ───
obj('大スクリーン')
sx, sy, sw, sh = SCR
O('furniture', sx - 4, sy - 4, sw + 8, sh + 8, 'q1', 'ink')
R('furniture', sx - 2, sy - 2, sw + 4, 1, 'q4')          # ベゼル上ハイライト
R('furniture', sx - 2, sy - 1, sw + 4, sh + 2, 'ink')
R('furniture', sx, sy, sw, sh, 'n0')                     # 消灯した画面
DI('furniture', sx, sy + sh - 4, sw, 4, 'n0', 'n1')      # 画面下のわずかな反射
PXL('furniture', sx + sw - 5, sy + 3, 'n2'); PXL('furniture', sx + sw - 7, sy + 5, 'n1')
PXL('furniture', sx + sw + 2, sy + sh + 2, 'g2')         # 電源LED
# スクリーン背面のシアンLED(アンビエントライト)。ベゼルの外周に点線の光
for xx in range(sx - 5, sx + sw + 5, 2):
    PXL('furniture', xx, sy - 5, 'cyn1')
    PXL('furniture', xx + 1, sy + sh + 4, 'cyn0')
for yy in range(sy - 3, sy + sh + 3, 2):
    PXL('furniture', sx - 5, yy, 'cyn1')
    PXL('furniture', sx + sw + 4, yy, 'cyn0')
PXL('furniture', sx - 5, sy - 5, 'cyn2'); PXL('furniture', sx + sw + 4, sy - 5, 'cyn2')

# ─── 奥壁: カテゴリ名表示パネル(右上) ───
obj('カテゴリ表示')
cx, cy, cw, ch = CATP
O('furniture', cx, cy, cw, ch, 'n0', 'ink')
R('furniture', cx + 1, cy + 1, cw - 2, 1, 'cyn1')
R('furniture', cx + 1, cy + ch - 2, cw - 2, 1, 'cyn0')
PXL('furniture', cx + 2, cy + 2, 'cyn2')

# ─── 奥壁: 数字ボタンパネル(右) ───
obj('数字ボタンパネル')
bx, by, bw, bh = BTNP
O('furniture', bx, by, bw, bh, 'q1', 'ink')
R('furniture', bx + 1, by + 1, bw - 2, 1, 'q4')
R('furniture', bx + 1, by + bh - 2, bw - 2, 1, 'q0')
for i, (bcx, bcy) in enumerate(BTNC):
    EL('furniture', bcx - 9, bcy - 9, bcx + 9, bcy + 9, fill='pnk1', out='ink')
    EL('furniture', bcx - 7, bcy - 7, bcx + 7, bcy + 7, fill='pnk2')
    EL('furniture', bcx - 5, bcy - 6, bcx - 2, bcy - 3, fill='pnkc')
    NTXT('furniture', bcx - 2, bcy - 2, str(i + 1), 'ink')

# ─── 編集卓(壁ぎわのカウンター=ミキサー卓。ボタンいっぱい) ───
obj('編集卓')
R('furniture', 47, DESK_Y, 290, 1, 'mauve')
R('furniture', 47, DESK_Y + 1, 290, 3, 'q4')
R('furniture', 47, DESK_Y + 4, 290, 2, 'q2')
R('furniture', 47, DESK_Y + 6, 290, 20, 'q1')            # 前板
for lx in (47, 104, 162, 220, 278, 336):
    R('furniture', lx, DESK_Y + 6, 1, 20, 'q0')
R('furniture', 47, DESK_Y + 24, 290, 2, 'q0')
R('furniture', 47, DESK_Y + 26, 290, 2, 'ink')
R('furniture', 47, DESK_Y + 7, 290, 1, 'pnk0', 255)      # 前板のほのかな席明かりライン
R('furniture', 49, DESK_Y + 28, 286, 2, 'q0')            # 接地影

# ─── 編集機(デスクの上・チェアの奥のミキサー卓。少し立体) ───
obj('編集機')
EX, EB, EW = EDITC
ET = EB + 6                                # 操作面の上端
MCOLS = ['g1', 'y1', 'cyn1', 'm2', 'b3', 'pnk2']
LEDS = []
# 背面の低いメーターブリッジ
R('furniture', EX + 4, EB, EW - 8, 6, 'q1')
R('furniture', EX + 4, EB, EW - 8, 1, 'q3')
R('furniture', EX + 4, EB + 5, EW - 8, 1, 'q0')
R('furniture', EX + 3, EB, 1, 6, 'ink'); R('furniture', EX + EW - 4, EB, 1, 6, 'ink')
for k, lx in enumerate(range(EX + 8, EX + EW - 8, 7)):   # メーターLED列(キラキラ)
    c = MCOLS[k % len(MCOLS)]
    PXL('furniture', lx, EB + 2, c)
    LEDS.append((lx, EB + 2, c, 1))
# 傾斜した操作面(手前へ少し広がる台形=立体感)
for yy in range(ET, ET + 10):
    t = (yy - ET) / 9.0
    x0e = int(EX + 2 - 2 * t + 0.5)
    x1e = int(EX + EW - 3 + 2 * t + 0.5)
    for xx in range(x0e, x1e + 1):
        if xx == x0e or xx == x1e:
            c = 'ink'
        elif yy == ET:
            c = 'q4'
        elif xx <= x0e + 1:
            c = 'q3'
        else:
            c = 'q2'
        PXL('furniture', xx, yy, c)
# 前面の厚み
R('furniture', EX - 1, ET + 10, EW + 2, 3, 'q0')
R('furniture', EX - 1, ET + 13, EW + 2, 1, 'ink')
# 左翼(チェアに隠れない): フェーダー4本
for i in range(4):
    lx = EX + 6 + i * 7
    R('furniture', lx, ET + 2, 1, 6, 'q0')
    R('furniture', lx - 1, ET + 3 + (i * 2) % 4, 3, 2, 'gray2')
# 右翼: ジョグダイヤル大小 + ボタン
EL('furniture', EX + EW - 22, ET + 1, EX + EW - 12, ET + 9, fill='q3', out='ink')
EL('furniture', EX + EW - 20, ET + 3, EX + EW - 16, ET + 6, fill='q4')
PXL('furniture', EX + EW - 15, ET + 3, 'gray2')
EL('furniture', EX + EW - 34, ET + 3, EX + EW - 28, ET + 8, fill='q3', out='ink')
PXL('furniture', EX + EW - 31, ET + 4, 'gray1')
for i in range(2):
    lx = EX + EW - 10 + i * 4
    c = MCOLS[(i + 3) % len(MCOLS)]
    R('furniture', lx, ET + 7, 2, 2, c)
    LEDS.append((lx, ET + 7, c, 2))

# ─── メニューパネル(デスクに立つ大きなプログラムボード) ───
obj('メニューパネル')
mx, my, mw, mh = MENU
O('furniture', mx, my, mw, mh, 'n0', 'ink')
R('furniture', mx + 1, my + 1, mw - 2, 1, 'pnk2')        # ネオンの上縁
R('furniture', mx + 2, my + 2, mw - 4, 1, 'pnk0')
R('furniture', mx + 1, my + mh - 2, mw - 2, 1, 'pnk0')
R('furniture', mx + 1, my + 2, 1, mh - 4, 'q2')
R('furniture', mx + mw - 2, my + 2, 1, mh - 4, 'q0')
for i in range(1, 5):                                     # 項目の仕切り
    yy = my + 2 + i * 22
    R('furniture', mx + 4, yy, mw - 8, 1, 'q1')
PXL('furniture', mx + 3, my + 3, 'pnkc')
PXL('furniture', mx + mw - 4, my + 3, 'pnkc')
R('furniture', mx + 6, my + mh, 3, 2, 'ink')              # デスクへの接地脚
R('furniture', mx + mw - 9, my + mh, 3, 2, 'ink')

# ─── ゲーミングチェア(編集卓の手前・後ろ姿) ───
obj('ゲーミングチェア')
gx, gy = CHAIR
BR_W, BR_H, RAD = 40, 46, 9
for yy in range(gy, gy + BR_H):
    dy = yy - gy
    if dy < RAD:
        inset = RAD - int(round(math.sqrt(RAD * RAD - (RAD - dy) * (RAD - dy))))
    else:
        inset = 0
    x0c, x1c = gx + inset, gx + BR_W - 1 - inset
    for xx in range(x0c, x1c + 1):
        if xx == x0c or xx == x1c or dy == 0 or (dy < 3 and (xx <= x0c + 1 or xx >= x1c - 1)):
            c = 'ink'
        elif xx <= x0c + 3:
            c = 'q2'
        elif xx >= x1c - 3:
            c = 'q0'
        else:
            c = 'q1'
        PXL('furniture', xx, yy, c)
R('furniture', gx + 7, gy + RAD, 2, BR_H - RAD - 6, 'pnk1')    # ゲーミングの差し色(左)
R('furniture', gx + BR_W - 9, gy + RAD, 2, BR_H - RAD - 6, 'pnk0')  # 右(影側)
R('furniture', gx + 14, gy + 6, 12, 1, 'q0')                   # ヘッドレストの境界
R('furniture', gx + 14, gy + 7, 12, 1, 'ink')
R('furniture', gx + 8, gy + BR_H, 24, 3, 'ink')                # 座面(のぞく部分)
R('furniture', gx + 9, gy + BR_H, 22, 1, 'q2')
R('furniture', gx + 18, gy + BR_H + 3, 4, 10, 'q3')            # 支柱
R('furniture', gx + 18, gy + BR_H + 3, 1, 10, 'q4')
R('furniture', gx + 19, gy + BR_H + 13, 2, 3, 'gray0')         # ガスシリンダー
for ddx, ddy in [(-14, 6), (0, 8), (14, 6)]:                   # 五本脚(見えるのは3本)
    x2, y2 = gx + 20 + ddx, gy + BR_H + 16 + ddy
    D['furniture'].line([gx + 20, gy + BR_H + 16, x2, y2], fill=C('ink'), width=2)
    OD['furniture'].line([gx + 20, gy + BR_H + 16, x2, y2], fill=_oid('furniture'), width=2)
    EL('furniture', x2 - 2, y2 - 1, x2 + 2, y2 + 3, fill='q2', out='ink')

# ─── 戸口の光の床へのこぼれ(白) ───
obj('スタジオへの戸口')
for yy in range(170, 210):
    reach = 30 + int((yy - 170) * 0.9)
    for xx in range(4, 4 + reach):
        if (xx * 2 + yy) % 5 == 0:
            PXL('bg', xx, yy, 'wwht')
        if (xx * 2 + yy) % 9 == 0 and xx < 4 + reach // 2:
            PXL('bg', xx, yy, 'gray1')

obj()
# 編集卓の足元に床影
dpatch('bg', 49, DESK_Y + 28, 286, 6, 'q0', 2)
# スクリーンの光のにじみ(壁)
dpatch('bg', sx - 8, sy - 6, 8, sh + 12, 'n4', 2)
dpatch('bg', sx + sw, sy - 6, 8, sh + 12, 'n4', 2, 1)
dpatch('bg', sx - 4, sy - 8, sw + 8, 6, 'n4', 2)
# スクリーン光の天板へのにじみ(チェアの幅は避ける: チェアより後に打つとチェアを貫通してしまう)
dpatch('furniture', sx + 4, DESK_Y + 1, CHAIR[0] - (sx + 4), 3, 'n4', 3)
dpatch('furniture', CHAIR[0] + 41, DESK_Y + 1, (sx + sw - 4) - (CHAIR[0] + 41), 3, 'n4', 3)

# ═══════════════ relight : プロップ単位の1px陰影 ═══════════════
CHAINS = [
 ['n0','n1','n2','n3','n4'],
 ['q0','q1','q2','q3','q4','q5','mauve'],
 ['m0','m1','m2','m3','m4'],
 ['r0','r1','r2'],
 ['brick','cor','cor2','cream'],
 ['y0','y1','y2'],
 ['g0','g1','g2','g3'],
 ['b0','b1','b2','b3','b4','b5'],
 ['gray0','gray1','gray2'],
 ['cyn0','cyn1','cyn2','cync'],
]
LIGHTER, DARKER = {}, {}
for chain in CHAINS:
    for a, b in zip(chain, chain[1:]):
        LIGHTER[P[a]] = P[b]
        DARKER[P[b]] = P[a]
INK = P['ink']
CRTC = (205, 66)     # 大スクリーンの画面中心

def relight(layer):
    im = L[layer]
    px = im.load()
    orig = [[px[xx, yy] for yy in range(H)] for xx in range(W)]

    def alpha(xx, yy):
        if not (0 <= xx < W and 0 <= yy < H):
            return 0
        return orig[xx][yy][3]

    def probe(xx, yy, dx, dy):
        for k in range(1, 4):
            tx, ty = xx + dx * k, yy + dy * k
            a = alpha(tx, ty)
            if a == 0:
                return True
            if orig[tx][ty][:3] != INK:
                return False
        return False

    for xx in range(W):
        for yy in range(H):
            c = orig[xx][yy]
            if c[3] == 0 or c[:3] == INK:
                continue
            rgb = c[:3]
            dx, dy = xx - CRTC[0], yy - CRTC[1]
            if (dx * dx + dy * dy) ** .5 < 92:
                litd = [((1 if dx < 0 else -1), 0), (0, (1 if dy < 0 else -1))]
                dkd = [((-1 if dx < 0 else 1), 0)]
            else:
                litd = [(0, -1)]
                dkd = [(0, 1), (-1, 0)]
            if any(probe(xx, yy, dx2, dy2) for dx2, dy2 in litd):
                if rgb in LIGHTER:
                    px[xx, yy] = LIGHTER[rgb] + (255,)
            elif any(probe(xx, yy, dx2, dy2) for dx2, dy2 in dkd):
                if rgb in DARKER:
                    px[xx, yy] = DARKER[rgb] + (255,)

for lname in ['furniture', 'props']:
    relight(lname)

# ═══════ 面の陰影 ═══════
def face_shade(layer):
    im = L[layer]
    px = im.load()
    seen = [[False] * H for _ in range(W)]
    for sx0 in range(W):
        for sy0 in range(H):
            if seen[sx0][sy0] or px[sx0, sy0][3] == 0:
                continue
            stack = [(sx0, sy0)]
            comp = []
            seen[sx0][sy0] = True
            while stack:
                cx2, cy2 = stack.pop()
                comp.append((cx2, cy2))
                for nx2, ny2 in ((cx2+1,cy2),(cx2-1,cy2),(cx2,cy2+1),(cx2,cy2-1)):
                    if 0 <= nx2 < W and 0 <= ny2 < H and not seen[nx2][ny2] \
                       and px[nx2, ny2][3] > 0:
                        seen[nx2][ny2] = True
                        stack.append((nx2, ny2))
            ys = [c[1] for c in comp]
            y0c, y1c = min(ys), max(ys)
            hc = y1c - y0c + 1
            if hc < 14:
                continue
            band1 = y1c - max(2, int(hc * 0.30))
            band2 = y1c - max(1, int(hc * 0.10))
            for (cx2, cy2) in comp:
                c = px[cx2, cy2][:3]
                if c == INK:
                    continue
                if cy2 >= band2 and hc >= 26 and c in DARKER:
                    px[cx2, cy2] = DARKER[c] + (255,)
                elif cy2 >= band1 and (cx2 + cy2) % 2 == 0 and c in DARKER:
                    px[cx2, cy2] = DARKER[c] + (255,)

face_shade('furniture')
face_shade('props')

# 壁への落ち影
sil = set()
for lname in ['furniture', 'props']:
    px = L[lname].load()
    for xx in range(W):
        for yy in range(H):
            if px[xx, yy][3] > 0:
                sil.add((xx, yy))
bgp = L['bg'].load()
for (xx, yy) in sil:
    for ox, oy in [(-2, 2), (-3, 3)]:
        tx, ty = xx + ox, yy + oy
        if (tx, ty) in sil or not (0 <= tx < W) or ty >= 146 or ty < 12:
            continue
        if (tx + ty) % 2:
            continue
        c = bgp[tx, ty][:3]
        if c in DARKER:
            bgp[tx, ty] = DARKER[c] + (255,)

# ═══════ 遮蔽AO ═══════
def darken_at(pmap, tx, ty, steps, dither=False):
    if dither and (tx + ty) % 2:
        return
    c = pmap[tx, ty][:3]
    for _ in range(steps):
        c = DARKER.get(c, c)
    pmap[tx, ty] = c + (255,)

for xx in range(W):
    lastY = None
    for yy in range(12, H):
        if (xx, yy) in sil:
            lastY = yy
            continue
        if lastY is None:
            continue
        d = yy - lastY
        if d <= 2:
            darken_at(bgp, xx, yy, 2)
        elif d <= 5:
            darken_at(bgp, xx, yy, 1)
        elif d <= 10:
            darken_at(bgp, xx, yy, 1, dither=True)

# ═══════ global illumination ═══════
DARKER[P['cool2']] = P['cool1']; DARKER[P['cool1']] = P['q2']
DARKER[P['pnkc']] = P['pnk2']; DARKER[P['pnk2']] = P['pnk1']
DARKER[P['pnk1']] = P['q2']; DARKER[P['pnk0']] = P['q1']
DARKER[P['o2']] = P['o1']; DARKER[P['o1']] = P['o0']; DARKER[P['o0']] = P['brick']
DARKER[P['wht']] = P['gray2']; DARKER[P['ivory']] = P['ivory2']
DARKER[P['wwht']] = P['n2']
DARKER[P['cync']] = P['cyn2']

SOURCES = [
    {'pos': (205, 66),  'r': 155, 's': 1.30, 'e': 1.4, 'tint': P['b4'],   'occ': True},   # 大スクリーン
    {'pos': (205, 24),  'r': 60,  's': 0.40, 'e': 1.4, 'tint': P['cyn1'], 'occ': False},  # アンビエントライト上
    {'pos': (24, 118),  'r': 82,  's': 0.95, 'e': 1.3, 'tint': P['gray2'],'occ': False},  # スタジオの白い灯り
    {'pos': (311, 82),  'r': 52,  's': 0.50, 'e': 1.4, 'tint': P['pnk2'], 'occ': False},  # 数字ボタン
    {'pos': (86, 82),   'r': 46,  's': 0.34, 'e': 1.4, 'tint': P['pnk2'], 'occ': False},  # メニューパネル
    {'pos': (205, 128), 'r': 80,  's': 0.42, 'e': 1.3, 'tint': P['m3'],   'occ': False},  # 編集機のLED
    {'pos': (192, 150), 'r': 185, 's': 0.32, 'e': 1.2, 'tint': P['q5'],   'occ': False},  # 室内バウンス
]
AMB = 0.40

GS = 4
gw, gh = W // GS + 1, H // GS + 1
solidg = [[False] * gh for _ in range(gw)]
for (sx3, sy3) in sil:
    solidg[sx3 // GS][sy3 // GS] = True

def ray_occl(cx3, cy3, sx3, sy3):
    dist = math.hypot(cx3 - sx3, cy3 - sy3)
    steps = max(1, int(dist / GS))
    hits = 0
    for k in range(1, steps):
        t = k / steps
        if dist * t < 14:
            continue
        gx3 = int((sx3 + (cx3 - sx3) * t) / GS)
        gy3 = int((sy3 + (cy3 - sy3) * t) / GS)
        if 0 <= gx3 < gw and 0 <= gy3 < gh and solidg[gx3][gy3]:
            hits += 1
            if hits >= 3:
                return 0.22
    return 1.0 if hits == 0 else (0.72 if hits == 1 else 0.45)

ILL = [[AMB] * gh for _ in range(gw)]
TINT = [[(P['q5'], 0.0) for _ in range(gh)] for _ in range(gw)]
for src in SOURCES:
    sx3, sy3 = src['pos']
    for gx3 in range(gw):
        for gy3 in range(gh):
            cx3, cy3 = gx3 * GS + GS // 2, gy3 * GS + GS // 2
            d = math.hypot(cx3 - sx3, cy3 - sy3)
            if d >= src['r']:
                continue
            f = (1 - d / src['r']) ** src['e'] * src['s']
            if src['occ']:
                f *= ray_occl(cx3, cy3, sx3, sy3)
            ILL[gx3][gy3] += f
            if f > TINT[gx3][gy3][1]:
                TINT[gx3][gy3] = (src['tint'], f)

def blend(c1, c2, t):
    return tuple(int(round(c1[i] * (1 - t) + c2[i] * t)) for i in range(3))

def apply_illum(layer):
    im = L[layer]
    px = im.load()
    for xx in range(W):
        for yy in range(H):
            c = px[xx, yy]
            if c[3] == 0 or c[:3] == INK:
                continue
            if layer == 'furniture':
                if c[:3] in (P['cyn0'], P['cyn1'], P['cyn2'], P['cync']):
                    continue    # シアンのアンビエントライトは自ら光る
                if sx <= xx < sx + sw and sy <= yy < sy + sh:
                    continue    # スクリーンは自ら光る(消灯でも保護)
                if 10 <= xx <= 39 and 49 <= yy <= 215:
                    continue    # スタジオの戸口の光
                if 3 <= xx <= 41 and 21 <= yy <= 47:
                    continue    # スタジオの看板
                if bx + 2 <= xx <= bx + bw - 3 and by + 2 <= yy <= by + bh - 3:
                    continue    # 数字ボタンは光る
                if cx + 1 <= xx <= cx + cw - 2 and cy + 1 <= yy <= cy + ch - 2:
                    continue    # カテゴリ表示は発光ディスプレイ
            rgb = c[:3]
            v = ILL[xx // GS][yy // GS] + (((xx * 7 + yy * 13) % 5) - 2) * 0.02
            tint = TINT[xx // GS][yy // GS][0]
            chk = (xx + yy) % 2 == 0
            d1c = DARKER.get(rgb, rgb)
            d2c = DARKER.get(d1c, d1c)
            out = rgb
            WARM = (198, 88, 70)
            if layer == 'bg':
                if v < 0.40:
                    out = d1c
                elif v < 0.55:
                    out = d1c if chk else blend(rgb, WARM, 0.05)
                elif v < 0.94:
                    out = blend(rgb, WARM, 0.09)
                elif v < 1.10:
                    out = blend(LIGHTER.get(rgb, rgb), tint, 0.32) if chk else blend(rgb, WARM, 0.10)
                else:
                    out = blend(LIGHTER.get(rgb, rgb), tint, 0.34)
            else:
                if v < 0.36:
                    out = d2c
                elif v < 0.50:
                    out = d2c if chk else d1c
                elif v < 0.64:
                    out = d1c
                elif v < 0.78:
                    out = d1c if chk else blend(rgb, WARM, 0.06)
                elif v < 0.94:
                    out = blend(rgb, WARM, 0.09)
                elif v < 1.10:
                    out = blend(LIGHTER.get(rgb, rgb), tint, 0.32) if chk else blend(rgb, WARM, 0.10)
                else:
                    out = blend(LIGHTER.get(rgb, rgb), tint, 0.34)
            px[xx, yy] = tuple(out) + (255,)

for lname in ['bg', 'furniture', 'props']:
    apply_illum(lname)

# ═══════ 書き出し ═══════
flat = Image.new("RGBA", (W, H), (0, 0, 0, 255))
for n in names:
    L[n].save(os.path.join(LAY, f"{n}.png"))
    flat.alpha_composite(L[n])
flat.convert("RGB").save(os.path.join(WEB, "room_edit.png"))
print("layers + room_edit.png written")

# ── プロップ切り分け(Aseprite用) ──
OBJ = os.path.join(LAY, "objects")
if os.path.isdir(OBJ):
    for _f in os.listdir(OBJ):
        os.remove(os.path.join(OBJ, _f))
os.makedirs(OBJ, exist_ok=True)
manifest = []
for n in names:
    ids = sorted([(v, k[1]) for k, v in OBJ_ID.items() if k[0] == n])
    layer_alpha = L[n].getchannel("A")
    taken = Image.new("L", (W, H), 0)
    kids = []
    buckets = {oid: bytearray(W * H) for oid, _ in ids}
    for idx, v in enumerate(OWNER[n].getdata()):
        b = buckets.get(v)
        if b is not None:
            b[idx] = 255
    for oid, oname in ids:
        mask = Image.frombytes("L", (W, H), bytes(buckets[oid]))
        cut = ImageChops.multiply(layer_alpha, mask)
        if not cut.getbbox():
            continue
        part = L[n].copy()
        part.putalpha(cut)
        safe = re.sub(r'[\\/:*?"<>|]', "_", oname)
        fn = f"{n}__{oid:03d}_{safe}.png"
        part.save(os.path.join(OBJ, fn))
        taken = ImageChops.lighter(taken, cut)
        kids.append({"name": oname, "file": "objects/" + fn})
    rest = ImageChops.subtract(layer_alpha, taken)
    if rest.getbbox():
        part = L[n].copy()
        part.putalpha(rest)
        fn = f"{n}__999_その他.png"
        part.save(os.path.join(OBJ, fn))
        kids.append({"name": "その他", "file": "objects/" + fn})
    manifest.append({"layer": n, "children": kids})
json.dump(manifest, io.open(os.path.join(LAY, "objects.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("プロップ切り分け:", sum(len(m["children"]) for m in manifest), "枚")

# ── 編集機のキラキラ点滅(3コマ・LEDの明滅) ──
BY0, BBH = 118, 24
blink = Image.new("RGBA", (W * 3, BBH), (0, 0, 0, 0))
bd = ImageDraw.Draw(blink)
BRIGHT = {'y1': 'y2', 'g1': 'g2', 'b3': 'b4', 'm2': 'm3', 'cyn1': 'cyn2', 'pnk2': 'pnkc'}
_mc_oid = OBJ_ID.get(('furniture', '編集機'))
_own = OWNER['furniture'].load()
LEDS = [t for t in LEDS if _own[t[0], t[1]] == _mc_oid]   # チェアに隠れたLEDは光らせない
for f in range(3):
    for i, (lx, ly, c, szb) in enumerate(LEDS):
        if (i + f) % 3 == 0:
            bc = C(BRIGHT.get(c, 'wht'))
            if szb == 2:
                bd.rectangle([f * W + lx, ly - BY0, f * W + lx + 1, ly - BY0 + 1], fill=bc)
            else:
                bd.point((f * W + lx, ly - BY0), fill=bc)
blink.save(os.path.join(WEB, "edit_blink.png"))
print("edit_blink.png", blink.size, "band y", BY0, "h", BBH)
