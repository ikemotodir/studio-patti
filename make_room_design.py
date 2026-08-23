# -*- coding: utf-8 -*-
"""デザイン室(CHARACTER DESIGN)の部屋 - 池本さんスケッチ準拠。
TOPの部屋(make_room.py)と同じ描法・同じパレット・同じ照明パイプライン。
レイアウト: 壁面いっぱいの黒板(木枠+チョーク受け)に紙を貼り、チョークの矢印でつなぐ。
右壁=スタジオへ戻る戸口(白光)+スタジオ看板 / 右=模造紙「キャラクターに関するデータ」/
天井=電球のガーランド(この部屋のあかり)。
Layers: bg / furniture / props / light
"""
from PIL import Image, ImageDraw, ImageChops
import os, json, math, io, re

WEB = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(WEB, "room_design_layers")
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
 # ── デザイン室で足した色 ──
 'bd0': (12, 26, 24), 'bd1': (22, 40, 36), 'bd2': (34, 56, 50), 'bd3': (52, 78, 70),
 'bd4': (78, 106, 96),                                                                 # 黒板
 'chk2': (146, 176, 164), 'chk': (226, 240, 230),                                       # チョーク
 'wd0': (70, 42, 26), 'wd1': (112, 70, 42), 'wd2': (156, 106, 64), 'wd3': (200, 150, 98),  # 木枠
 'pap_r0': (150, 32, 40), 'pap_r': (214, 58, 62),                                       # 赤い紙
 'bulbc': (255, 246, 200),                                                              # 電球のあかり
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

# ═══════════════ 作り込み用の描画キット ═══════════════
# 方針: 一律の黒枠で囲まない / 面を分けて立体を作る / ディザは階調でなく素材を表す

def DITH(l, x, y, w, h, cA, cB, kind='check', ph=0):
    """素材別のディザ。cA=地、cB=混ぜる色。"""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            u, v = xx + ph, yy
            if kind == 'check':    m = (u + v) % 2 == 0
            elif kind == 'sparse': m = (u * 2 + v) % 4 == 0
            elif kind == 'dense':  m = (u + v) % 4 != 0
            elif kind == 'grain':  m = (u * 7 + v * 13 + (u * v) % 5) % 9 < 2   # 紙・コンクリのざらつき
            elif kind == 'weave':  m = (u % 3 == 0) != (v % 3 == 0)             # 布・メッシュ
            elif kind == 'brush':  m = (u + v * 3) % 7 == 0                     # 刷毛目・拭き跡
            elif kind == 'hline':  m = v % 2 == 0
            elif kind == 'vline':  m = u % 2 == 0
            else:                  m = False
            if m:
                PXL(l, xx, yy, cB)
            elif cA is not None:
                PXL(l, xx, yy, cA)

def BEVEL(l, x, y, w, h, base, hi, sh):
    """面取りした箱。上と左に1pxの明、下と右に1pxの暗。黒枠で囲まない。"""
    R(l, x, y, w, h, base)
    R(l, x, y, w, 1, hi); R(l, x, y, 1, h, hi)
    R(l, x + w - 1, y, 1, h, sh); R(l, x, y + h - 1, w, 1, sh)

def INSET(l, x, y, w, h, base, hi, sh):
    """へこんだ面(スリット・くぼみ)。明暗がBEVELと逆。"""
    R(l, x, y, w, h, base)
    R(l, x, y, w, 1, sh); R(l, x, y, 1, h, sh)
    R(l, x + w - 1, y, 1, h, hi); R(l, x, y + h - 1, w, 1, hi)

def CYL(l, x, y, w, h, ramp, lit=0.30):
    """円柱。ハイライト→コアシャドウ→端に反射光。rampは暗い順のリスト。"""
    n = len(ramp)
    for i in range(w):
        t = i / float(w - 1) if w > 1 else 0.0
        k = int(abs(t - lit) * (n - 1) * 1.55)
        if t > 0.88:
            k = max(0, k - 1)                       # 反射光
        R(l, x + i, y, 1, h, ramp[min(n - 1, k)])

def SCREW(l, x, y, body, slot):
    R(l, x, y, 2, 2, body)
    PXL(l, x, y + 1, slot); PXL(l, x + 1, y, slot)

def KNOB(l, cx, cy, r, skirt, cap, hi, sh, ang=-1.2):
    """ロータリーノブ。スカート+キャップ+指標+ハイライト。"""
    EL(l, cx - r, cy - r, cx + r, cy + r, fill=skirt, out=sh)
    EL(l, cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 2, fill=cap)
    PXL(l, cx - r + 2, cy - r + 2, hi)
    PXL(l, cx + int(round(math.cos(ang) * (r - 1))),
           cy + int(round(math.sin(ang) * (r - 1))), hi)

def FADER(l, x, y, h, pos, slot, cap, hi, sh):
    """フェーダー。溝(へこみ)+つまみ(面取り)。posは0(下)〜1(上)。"""
    INSET(l, x + 1, y, 2, h, slot, sh, slot)
    ky = y + int((1 - pos) * (h - 5))
    BEVEL(l, x, ky, 4, 4, cap, hi, sh)
    R(l, x, ky + 2, 4, 1, sh)

def CAST(l, x, y, w, h, c, soft=True):
    """落ち影。物の右下へ、外へ行くほど薄く。"""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if not soft or (xx + yy) % 2 == 0:
                PXL(l, xx, yy, c)

# 数字(5x5) - 数字ボタン用
NFONT = {
 '1': "010 110 010 010 111", '2': "110 001 010 100 111",
 '3': "110 001 011 001 110", '4': "101 101 111 001 001",
}
def NTXT(l, x, y, ch, c):
    rows = NFONT[ch].split()
    for ry, row in enumerate(rows):
        for rx, bit in enumerate(row):
            if bit == '1': PXL(l, x + rx, y + ry, c)

# ═══════════════ 主要座標(ここだけ見れば配置が分かる) ═══════════════
FRAME  = (47, 14, 290, 124)     # 黒板の木枠 x47..336 / y14..137
BOARD  = (51, 18, 282, 116)     # 黒板の面   x51..332 / y18..133
RAIL_Y = 138                    # チョーク受け(黒板の下)
GAR_SPANS = [(50, 192, 16, 6, 8), (192, 334, 16, 6, 8)]   # 電球ガーランド(2連・16球)
DOORX0, DOORX1 = 345, 373       # スタジオへ戻る戸口(右の壁)
# 黒板に貼ってある紙 (x, y, w, h)
PAP_DESIGN = (58, 32, 59, 35)   # 黄: キャラクターデザイン＆設計
PAP_SKETCH = (128, 42, 21, 23)  # おばけのラフ絵
PAP_STORY  = (160, 30, 53, 27)  # 白: Story is King
PAP_SPOOKS = (78, 70, 53, 21)   # Spooks Gs
PAP_WORLD  = (106, 98, 49, 19)  # 桃: 世界観
PAP_TALE   = (182, 74, 33, 19)  # 赤: 物語
DATA_TITLE = (244, 36, 87, 13)  # キャラクターに関するデータ(見出し)
DATA_PANEL = (244, 52, 87, 78)  # 模造紙

# ═══════════════ bg : 天井・奥壁・床 ═══════════════
obj()
R('bg', 0, 0, W, H, 'q2')
# 天井(TOP・編集室と同じ建物)
R('bg', 0, 0, W, 10, 'ink')
R('bg', 0, 6, W, 1, 'q1')
R('bg', 0, 10, W, 2, 'q0')
for x in range(4, W, 24):
    PXL('bg', x, 4, 'wd1'); PXL('bg', x + 1, 4, 'wd1')

# 奥壁(黒板がのる下地)
R('bg', 0, 12, W, 134, 'q2')
DI('bg', 0, 12, W, 8, 'q3', 'q2')
DI('bg', 0, 128, W, 10, 'q1', 'q2')
R('bg', 0, 142, W, 4, 'ink')
R('bg', 0, 146, W, 2, 'q0')

# 床(TOP・編集室と同じ間取り。継ぎ目のきらめきは暖色)
R('bg', 0, 148, W, 92, 'q1')
R('bg', 0, 148, W, 3, 'q0')
for i, y in enumerate([161, 175, 189, 203, 217, 231]):
    R('bg', 0, y, W, 1, 'q0')
    for x in range(0, W, 16):
        PXL('bg', x + (i * 5) % 16, y + 1, 'q2')
for i, x in enumerate(range(0, W + 32, 32)):
    for j, yy in enumerate([(149, 12), (162, 13), (176, 13), (190, 13), (204, 13), (218, 13), (232, 8)]):
        xo = (x + (16 if j % 2 else 0)) % (W + 32)
        R('bg', xo, yy[0], 1, yy[1], 'q0')
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
    PXL('bg', sx5, 160, 'y0' if si % 2 else 'o0')          # 床のきらめきは電球とおなじ暖色
    PXL('bg', sx5 + 12, 174, 'o0' if si % 2 else 'y0')
DI('bg', 0, 224, W, 6, 'q1', 'q0')
DI('bg', 0, 230, W, 10, 'q0', 'ink')

# ─── 側壁(TOP・編集室と同じ台形) ───
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
                base = 'q1' if t > 0.55 else 'q2'
                c = 'q0' if (xx * 13 + yy * 7) % 37 == 0 else base
            PXL('bg', xx, yy, c)
    cx0 = 46 if left else W - 47
    R('bg', cx0, 13, 1, 156, 'ink')
    R('bg', cx0 + (1 if left else -1), 14, 1, 154, 'q3')
side_wall(True)
side_wall(False)

# ═══════════════ 黒板(壁いっぱい) ═══════════════
obj('黒板')
fx, fy, fw, fh = FRAME
bx, by, bw, bh = BOARD

# ── 木枠(4px厚): 上面は光を受け、下面は影。四隅は留め(トメ)。──
R('bg', fx, fy, fw, fh, 'wd1')
DITH('bg', fx, fy, fw, 4, 'wd1', 'wd2', 'hline')          # 上の桟(木目は横)
R('bg', fx, fy, fw, 1, 'wd2')
R('bg', fx, fy + 3, fw, 1, 'wd0')                          # 板に落ちる枠の影
DITH('bg', fx, fy + fh - 4, fw, 4, 'wd0', 'wd1', 'hline')  # 下の桟
R('bg', fx, fy + fh - 1, fw, 1, 'ink')
DITH('bg', fx, fy, 4, fh, 'wd1', 'wd2', 'vline')           # 左の桟(木目は縦)
R('bg', fx, fy, 1, fh, 'wd2')
R('bg', fx + 3, fy, 1, fh, 'wd0')
DITH('bg', fx + fw - 4, fy, 4, fh, 'wd0', 'wd1', 'vline')  # 右の桟
R('bg', fx + fw - 1, fy, 1, fh, 'ink')
for k in range(4):                                          # 留めの継ぎ目(45度)
    PXL('bg', fx + k, fy + k, 'wd0')
    PXL('bg', fx + fw - 1 - k, fy + k, 'wd0')
    PXL('bg', fx + k, fy + fh - 1 - k, 'wd0')
    PXL('bg', fx + fw - 1 - k, fy + fh - 1 - k, 'wd0')
for kx, ky in [(104, fy + 1), (226, fy + 2), (168, fy + fh - 3), (292, fy + fh - 2)]:
    PXL('bg', kx, ky, 'wd0'); PXL('bg', kx + 1, ky, 'wd0')  # 節(ふし)

# ── スレート面: 上ほど明るい。拭き跡の弧と、下に溜まるチョークの粉。──
for yy in range(by, by + bh):
    t = (yy - by) / float(bh - 1)
    R('bg', bx, yy, bw, 1, 'bd2' if t < 0.14 else ('bd1' if t < 0.70 else 'bd0'))
DITH('bg', bx, by, bw, 26, None, 'bd2', 'sparse')          # 天面の照り返し
for ax, ay, arx, ary in [(112, 62, 48, 23), (206, 96, 56, 21), (274, 46, 36, 16),
                         (78, 106, 32, 13), (170, 40, 40, 15)]:
    for yy in range(max(by, ay - ary), min(by + bh, ay + ary + 1)):
        for xx in range(max(bx, ax - arx), min(bx + bw, ax + arx + 1)):
            e = ((xx - ax) / float(arx)) ** 2 + ((yy - ay) / float(ary)) ** 2
            if 0.58 < e < 1.0 and (xx * 3 + yy * 5) % 4 == 0:
                PXL('bg', xx, yy, 'bd2')                    # 消しゴムの弧のふち
            elif e <= 0.58 and (xx + yy * 2) % 9 == 0:
                PXL('bg', xx, yy, 'bd2')                    # 弧の内側は薄く
for yy in range(by + bh - 15, by + bh):                     # 下に溜まった粉
    d = (yy - (by + bh - 15)) / 14.0
    step = max(2, int(15 - d * 12))
    for xx in range(bx, bx + bw):
        if (xx * 7 + yy * 11) % step == 0:
            PXL('bg', xx, yy, 'bd3')
for sx, sy, sl in [(88, 44, 9), (152, 78, 6), (240, 112, 11), (300, 64, 7), (66, 94, 5)]:
    for k in range(sl):                                     # 細かい傷
        PXL('bg', sx + k, sy - k // 3, 'bd3')

# ─── チョークの線(かすれた点線)と矢印 ───
_cn = [0]
def chalk_line(pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for k in range(steps + 1):
            t = k / float(steps) if steps else 0.0
            xx = int(round(x0 + (x1 - x0) * t)); yy = int(round(y0 + (y1 - y0) * t))
            _cn[0] += 1
            if _cn[0] % 5 == 4:
                continue                                   # かすれ
            PXL('bg', xx, yy, 'chk' if _cn[0] % 3 else 'chk2')

def chalk_head(x, y, dx, dy):
    """矢じり(進む向きに開く)"""
    for k in range(1, 5):
        PXL('bg', x - dx * k - dy * (k // 2), y - dy * k + dx * (k // 2), 'chk')
        PXL('bg', x - dx * k + dy * (k // 2), y - dy * k - dx * (k // 2), 'chk')
    PXL('bg', x, y, 'chk')

obj('チョークの矢印')
# 設計の紙 → 世界観 (下へ回り込む)
chalk_line([(66, 70), (62, 82), (66, 95), (80, 103), (100, 106)])
chalk_head(103, 106, 1, 0)
# 世界観 → 物語 (右上へ)
chalk_line([(157, 102), (168, 96), (176, 88)])
chalk_head(179, 85, 1, -1)

# ═══════════════ furniture : 貼り紙・模造紙・戸口・ガーランド ═══════════════
def paper(x, y, w, h, base, hi, shade, curl=5, rule=0, grid=False, torn=0):
    """黒板に貼った紙。上が明るいグラデ・ごく薄い紙目・罫線・めくれた角まで描く。
    質感は「気配」程度に抑える(上に6pxの文字が乗るため)。"""
    B0, B1, B2, B3 = BOARD
    def onboard(xx, yy):
        return B0 <= xx < B0 + B2 and B1 <= yy < B1 + B3
    # ── 落ち影: 右と下へ。近いほど濃く ──
    for d, dens in ((1, 1), (2, 2), (3, 3)):
        for xx in range(x + d, x + w + d):
            yy = y + h - 1 + d
            if onboard(xx, yy) and (xx + yy) % dens == 0:
                PXL('bg', xx, yy, 'bd0')
        for yy in range(y + d, y + h + d):
            xx = x + w - 1 + d
            if onboard(xx, yy) and (xx + yy) % dens == 0:
                PXL('bg', xx, yy, 'bd0')
    # ── 面: 上が明るく下が落ちる ──
    R('furniture', x, y, w, h, base)
    band = max(2, h // 4)
    DITH('furniture', x, y + 1, w, band, None, hi, 'sparse')
    DITH('furniture', x, y + h - band, w, band, None, shade, 'sparse')
    for yy in range(y + 1, y + h - 1):                        # 紙目(4%だけ)
        for xx in range(x + 1, x + w - 1):
            if (xx * 13 + yy * 7) % 23 == 0:
                PXL('furniture', xx, yy, hi)
    R('furniture', x, y, w, 1, hi); R('furniture', x, y, 1, h, hi)
    R('furniture', x + w - 1, y, 1, h, shade); R('furniture', x, y + h - 1, w, 1, shade)
    # ── 罫線・方眼(破線にして薄く) ──
    for k in range(rule):
        yy = y + 9 + k * 5
        for xx in range(x + 4, x + w - 5):
            if xx % 2 == 0:
                PXL('furniture', xx, yy, shade)
    if grid:
        for gx in range(x + 5, x + w - 4, 6):
            for gy in range(y + 4, y + h - 4):
                if gy % 2 == 0: PXL('furniture', gx, gy, shade)
        for gy in range(y + 5, y + h - 4, 6):
            for gx in range(x + 4, x + w - 4):
                if gx % 2 == 0: PXL('furniture', gx, gy, shade)
    # ── ちぎれたふち(上端) ──
    for k in range(torn):
        tx = x + 3 + k * 4
        if tx < x + w - 3:
            PXL('furniture', tx, y, 'bd1'); PXL('furniture', tx + 1, y, 'bd1')
            PXL('furniture', tx, y + 1, hi)
    # ── めくれた角(右下): 裏面が見える + 折り目 + 下にできる濃い影 ──
    if curl:
        n = curl
        for i in range(n):                                    # まず角を黒板に戻す(紙が浮いている)
            yy = y + h - 1 - i
            for j in range(n - 1 - i):
                PXL('furniture', x + w - 1 - j, yy, 'bd1' if onboard(x + w - 1 - j, yy) else base)
        for i in range(n):                                    # 折り返した裏面(手前ほど明るい)
            yy = y + h - 1 - i
            for j in range(n - i):
                xx = x + w - n + i + (n - i - 1 - j)
                if j == 0:
                    PXL('furniture', xx, yy, shade)           # 折り目
                else:
                    PXL('furniture', xx, yy, 'wht' if j > 1 else hi)
        for i in range(n - 2):                                # めくれの影
            yy, xx = y + h - i, x + w - 1 - i
            if onboard(xx, yy):
                PXL('bg', xx, yy, 'bd0')

def pin(x, y, c, c2):
    """画鋲。頭のドーム+ハイライト+紙に落ちる1pxの影。"""
    PXL('furniture', x + 2, y + 2, 'bd1')
    EL('props', x - 1, y - 1, x + 1, y + 1, fill=c, out=c2)
    PXL('props', x - 1, y - 1, 'wht')

def tape(x, y, w):
    """マスキングテープ。半透明で下が透け、両端がちぎれている。"""
    R('props', x, y, w, 3, 'ivory2', 120)
    R('props', x, y, w, 1, 'ivory', 150)
    for k in range(3):
        if k % 2 == 0:
            PXL('props', x, y + k, 'ivory', 80)
            PXL('props', x + w - 1, y + k, 'ivory', 80)

obj('キャラクターデザインと設計の紙')
paper(*PAP_DESIGN, base='y2', hi='ivory', shade='y1', curl=6)
pin(PAP_DESIGN[0] + PAP_DESIGN[2] // 2, PAP_DESIGN[1] + 2, 'm2', 'm0')

obj('おばけのラフ絵')
px7, py7, pw7, ph7 = PAP_SKETCH
paper(px7, py7, pw7, ph7, base='ivory', hi='wht', shade='ivory2', curl=0)
# 一つ目のおばけ(鉛筆のラフ線。#=線 / O=目)
GHOST = [
    "....#####....",
    "..##.....##..",
    ".#.........#.",
    "#...........#",
    "#....OOO....#",
    "#...OOOOO...#",
    "#...OOOOO...#",
    "#....OOO....#",
    "#...........#",
    "#...........#",
    "#...........#",
    "#...........#",
    "#..#..#..#..#",
    ".##..##..##..",
]
for gy9, row9 in enumerate(GHOST):
    for gx9, ch9 in enumerate(row9):
        if ch9 == '#':
            PXL('furniture', px7 + 4 + gx9, py7 + 3 + gy9, 'gray0')
        elif ch9 == 'O':
            PXL('furniture', px7 + 4 + gx9, py7 + 3 + gy9, 'ink')
PXL('furniture', px7 + 9, py7 + 8, 'wht')                 # 目のハイライト
for k in range(3):                                        # 鉛筆のあたり線
    PXL('furniture', px7 + 6 + k, py7 + 15 + k, 'gray1')
    PXL('furniture', px7 + 13 + k, py7 + 13 + k, 'gray1')
R('furniture', px7 + 4, py7 + 19, 13, 1, 'gray1')         # 下に一本メモ線
tape(px7 + pw7 // 2 - 3, py7 - 1, 7)

obj('Story is Kingの紙')
paper(*PAP_STORY, base='ivory', hi='wht', shade='ivory2', curl=4, torn=6)
tape(PAP_STORY[0] - 2, PAP_STORY[1] - 1, 8)
tape(PAP_STORY[0] + PAP_STORY[2] - 6, PAP_STORY[1] - 1, 8)

obj('Spooks Gsの紙')
paper(*PAP_SPOOKS, base='ivory2', hi='ivory', shade='gray0', curl=4)
pin(PAP_SPOOKS[0] + 4, PAP_SPOOKS[1] + 2, 'b3', 'b0')
pin(PAP_SPOOKS[0] + PAP_SPOOKS[2] - 5, PAP_SPOOKS[1] + 2, 'b3', 'b0')

obj('世界観の紙')
paper(*PAP_WORLD, base='m4', hi='pnkc', shade='m2', curl=4)
pin(PAP_WORLD[0] + PAP_WORLD[2] // 2, PAP_WORLD[1] + 2, 'y1', 'y0')

obj('物語の紙')
paper(*PAP_TALE, base='pap_r', hi='cor', shade='pap_r0', curl=4)
pin(PAP_TALE[0] + PAP_TALE[2] // 2, PAP_TALE[1] + 2, 'y1', 'y0')

# ─── 模造紙(キャラクターに関するデータ) ───
obj('キャラクターに関するデータ')
tx8, ty8, tw8, th8 = DATA_TITLE
# 見出しはチョークで囲って黒板に直接書いてある
for k in range(tw8):
    PXL('bg', tx8 + k, ty8, 'chk' if k % 5 else 'chk2')
    PXL('bg', tx8 + k, ty8 + th8 - 1, 'chk' if (k + 2) % 5 else 'chk2')
for k in range(th8):
    PXL('bg', tx8, ty8 + k, 'chk' if k % 4 else 'chk2')
    PXL('bg', tx8 + tw8 - 1, ty8 + k, 'chk' if (k + 1) % 4 else 'chk2')
dx8, dy8, dw8, dh8 = DATA_PANEL
paper(dx8, dy8, dw8, dh8, base='ivory', hi='wht', shade='ivory2', curl=0)
for k in range(4):                                        # 四隅のテープ
    tape(dx8 + (0 if k % 2 == 0 else dw8 - 8), dy8 + (0 if k < 2 else dh8 - 3), 8)
# 貼ってある写真・付箋・手書き(内容は読めなくてOK)
def photo(x, y, w, h, tone, tilt=0):
    """ポラロイド。白フチ+下の余白+わずかな影。中身は読めなくてよい。"""
    for k in range(2):                                        # 落ち影
        for xx in range(x + 1 + k, x + w + 1 + k):
            PXL('furniture', xx, y + h + k, 'ivory2')
    R('furniture', x, y, w, h, 'wht')                         # 白フチ
    R('furniture', x + w - 1, y, 1, h, 'ivory2')
    R('furniture', x, y + h - 1, w, 1, 'ivory2')
    INSET('furniture', x + 2, y + 2, w - 4, h - 8, tone, 'gray0', 'ink')   # 画面(凹み)
    for yy in range(y + 3, y + h - 7):                        # 中身は抽象的な陰影
        for xx in range(x + 3, x + w - 3):
            if (xx * 5 + yy * 3) % 9 == 0:
                PXL('furniture', xx, yy, 'gray0')
    R('furniture', x + 3, y + h - 5, w - 8, 1, 'gray1')       # 下の余白に手書き
    R('furniture', x + 3, y + h - 3, w - 12, 1, 'gray1')

def sticky(x, y, w, h, base, hi, sh):
    """付箋。下端がめくれ上がり、その下に影ができる。"""
    R('furniture', x, y, w, h, base)
    R('furniture', x, y, w, 1, hi)
    R('furniture', x + w - 1, y, 1, h, sh)
    for k in range(3):                                        # めくれた下端
        R('furniture', x + k, y + h - 1 - k, w - k * 2, 1, hi if k else sh)
    for k in range(3):
        R('furniture', x + 2, y + 3 + k * 3, w - 5 - k, 1, sh)

photo(249, 57, 32, 25, 'b0')
EL('furniture', 258, 62, 270, 73, fill='b2', out='b1')        # 写真の中のおばけらしき影
PXL('furniture', 262, 66, 'b5'); PXL('furniture', 266, 66, 'b5')
photo(287, 57, 26, 22, 'q1')
EL('furniture', 294, 61, 305, 71, fill='q4', out='q2')
photo(293, 86, 27, 24, 'r0')
EL('furniture', 300, 90, 312, 101, fill='r1', out='r2')
sticky(249, 88, 18, 15, 'y2', 'ivory', 'y0')
sticky(271, 90, 16, 13, 'm4', 'pnkc', 'm2')
for k in range(6):                                             # 手書きの行
    R('furniture', 249, 112 + k * 3, 36 - (k % 3) * 7, 1, 'gray1')
for k in range(5):                                             # 小さなグラフ
    hgt = (k * 3 + 4) % 13
    R('furniture', 292 + k * 5, 127 - hgt, 3, hgt, 'b3')
    R('furniture', 292 + k * 5, 127 - hgt, 3, 1, 'b4')
R('furniture', 291, 128, 27, 1, 'gray0')
R('furniture', 246, 55, 4, 6, 'gray2')                         # ゼムクリップ
R('furniture', 246, 55, 4, 1, 'wht'); PXL('furniture', 247, 60, 'gray0')

# ─── 右の壁: スタジオ(TOPの部屋)へ戻る戸口。白色の光がもれる ───
obj('スタジオへの戸口')
for xx in range(DOORX0, DOORX1 + 1):
    t = (DOORX1 - xx) / 28.0
    ytopD = int(58 - 8 * t + 0.5)
    ybotD = int(214 - 46 * t + 0.5)
    for yy in range(ytopD, ybotD):
        rel = (yy - ytopD) / float(ybotD - ytopD)
        if xx >= DOORX1 - 1 or xx <= DOORX0 + 1:
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
R('furniture', DOORX1 + 1, 58, 1, 157, 'ink')
R('furniture', DOORX0 - 1, 50, 1, 119, 'ink')
R('furniture', DOORX1 + 2, 58, 1, 157, 'q1')
for k in range(4):
    R('furniture', DOORX1 - 4 - k * 6, 62 - k, 1, 140 - k * 10, 'gray2' if k % 2 else 'gray1')

# ─── 右の看板: スタジオ(白の電飾・TOPと同じ台形様式) ───
def bake_sign_img(img_name, x0, x1, ytop_fn, ybot_fn, core):
    """プレート(台形)に文字が「描いてある」ように焼く。
    列ごとにプレートの中心線へ縦センタリングするので、パースの傾きに自然に沿う。"""
    m = Image.open(os.path.join(WEB, img_name)).convert('RGBA')
    tw, th = m.size
    ox = x0 + (x1 - x0 + 1 - tw) // 2
    mp = m.load()
    for gy in range(th):
        for gx in range(tw):
            if mp[gx, gy][3] > 0:
                xx = ox + gx
                cy_ = (ytop_fn(xx) + ybot_fn(xx)) / 2.0
                PXL('furniture', xx, int(cy_ - th / 2.0 + 0.5) + gy, core)

obj('スタジオの看板')
def signS_top(xx):
    return int(21 + 8 * (379 - xx) / 36.0 + 0.5)
def signS_bot(xx):
    return int(45 + 1 * (379 - xx) / 36.0 + 0.5)
for xx in range(343, 380):
    ytopS = signS_top(xx)
    ybotS = signS_bot(xx)
    for yy in range(ytopS, ybotS + 1):
        if yy == ytopS or yy == ybotS:
            c = 'ink'
        elif yy == ytopS + 1:
            c = 'gray2'
        elif yy == ybotS - 1:
            c = 'gray0'
        else:
            c = 'q0'
        PXL('furniture', xx, yy, c)
R('furniture', 380, 21, 1, 25, 'ink'); R('furniture', 342, 29, 1, 18, 'ink')
PXL('furniture', 378, 23, 'wht'); PXL('furniture', 344, 44, 'wht')
bake_sign_img('sign_studio_s.png', 343, 379, signS_top, signS_bot, 'wht')

# ─── 天井の電球ガーランド(この部屋のあかり) ───
obj('ガーランド')
def garland_positions():
    out = []
    for x0, x1, y0, sag, nb in GAR_SPANS:
        for i in range(nb):
            t = (i + 0.5) / nb
            out.append((int(x0 + t * (x1 - x0)), y0 + int(sag * (1 - (2 * t - 1) ** 2) + 0.5)))
    return out

def wire_y(x):
    for x0, x1, y0, sag, nb in GAR_SPANS:
        if x0 <= x <= x1:
            t = (x - x0) / float(x1 - x0)
            return y0 + int(sag * (1 - (2 * t - 1) ** 2) + 0.5)
    return None

for xx in range(GAR_SPANS[0][0], GAR_SPANS[-1][1] + 1):
    wy = wire_y(xx)
    if wy is not None:
        PXL('furniture', xx, wy, 'ink')
        PXL('furniture', xx, wy + 1, 'q1')
GAR_BULBS = garland_positions()
for (gbx, gby) in GAR_BULBS:
    R('furniture', gbx, gby + 1, 1, 1, 'gray0')                     # 吊り線
    R('furniture', gbx - 1, gby + 2, 3, 1, 'gray1')                 # ソケット(口金)
    PXL('furniture', gbx - 1, gby + 2, 'gray2')
    EL('furniture', gbx - 2, gby + 3, gbx + 2, gby + 7, fill='o2', out='y0')  # ガラス球
    PXL('furniture', gbx, gby + 5, 'bulbc')                         # フィラメント
    PXL('furniture', gbx - 1, gby + 4, 'bulbc')
    PXL('furniture', gbx + 2, gby + 6, 'o1')                        # 球の縁の陰り
    PXL('furniture', gbx - 2, gby + 6, 'o1')

# ─── チョーク受け(黒板の下のふち)とチョーク ───
obj('チョーク受け')
# 受け: 天板(光を受ける)+リップ+前面+下の落ち影。粉が天板に溜まる。
R('furniture', FRAME[0] - 1, RAIL_Y, FRAME[2] + 2, 1, 'wd3')      # 天板のふち(明)
DITH('furniture', FRAME[0] - 1, RAIL_Y + 1, FRAME[2] + 2, 2, 'wd2', 'wd1', 'hline')
R('furniture', FRAME[0] - 1, RAIL_Y + 3, FRAME[2] + 2, 1, 'wd0')  # 前面の下
R('furniture', FRAME[0] - 1, RAIL_Y + 4, FRAME[2] + 2, 1, 'ink')  # 下端
DITH('bg', FRAME[0], RAIL_Y + 5, FRAME[2], 2, None, 'q0', 'check') # 壁への落ち影
for kx in range(FRAME[0] + 2, FRAME[0] + FRAME[2], 3):            # 天板のチョーク粉
    if (kx * 5) % 7 < 3:
        PXL('furniture', kx, RAIL_Y, 'ivory2')
obj('チョーク')
# マユ(x92..114)とパッチ(x266..290)の立ち位置を避けて置く
R('props', 148, RAIL_Y - 1, 9, 2, 'wht'); PXL('props', 148, RAIL_Y - 1, 'gray2')
R('props', 162, RAIL_Y - 1, 7, 2, 'y2'); PXL('props', 162, RAIL_Y - 1, 'y1')
R('props', 212, RAIL_Y - 2, 13, 3, 'wd0')
R('props', 212, RAIL_Y - 2, 13, 1, 'gray1')

# ─── 戸口の光の床へのこぼれ(白) ───
obj('戸口のあかり')
for yy in range(170, 212):
    reach = 30 + int((yy - 170) * 0.9)
    for xx in range(W - 4 - reach, W - 4):
        if (xx * 2 + yy) % 5 == 0:
            PXL('bg', xx, yy, 'q3')
        if (xx * 2 + yy) % 9 == 0 and xx > W - 4 - reach // 2:
            PXL('bg', xx, yy, 'gray0')

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
 ['bd0','bd1','bd2','bd3','bd4'],
 ['wd0','wd1','wd2','wd3'],
 ['pap_r0','pap_r'],
 ['chk2','chk'],
 ['o2','bulbc'],
]
LIGHTER, DARKER = {}, {}
for chain in CHAINS:
    for a, b in zip(chain, chain[1:]):
        LIGHTER[P[a]] = P[b]
        DARKER[P[b]] = P[a]
INK = P['ink']
CRTC = (192, 12)     # 天井のガーランド(この部屋の主光源)

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
            if (dx * dx + dy * dy) ** .5 < 30:
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
DARKER[P['chk']] = P['chk2']; DARKER[P['bulbc']] = P['o2']
DARKER[P['pap_r']] = P['pap_r0']

SOURCES = [
    {'pos': (360, 118), 'r': 86,  's': 0.98, 'e': 1.3, 'tint': P['gray2'], 'occ': False},  # スタジオの白い灯り
    {'pos': (287, 92),  'r': 58,  's': 0.26, 'e': 1.4, 'tint': P['ivory'], 'occ': False},  # 模造紙の照り返し
    {'pos': (192, 120), 'r': 200, 's': 0.24, 'e': 1.3, 'tint': P['o1'],    'occ': False},  # 室内バウンス(暖色)
]
for _gx, _gy in GAR_BULBS:
    SOURCES.append({'pos': (_gx, _gy + 5), 'r': 46, 's': 0.30, 'e': 1.5,
                    'tint': P['o2'], 'occ': False})        # 電球ひとつずつが光源
AMB = 0.38

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
            if layer == 'bg':
                if c[:3] in (P['chk'], P['chk2']):
                    continue    # チョークの線は白のまま読ませる
            if layer == 'furniture':
                if DOORX0 <= xx <= DOORX1 and 49 <= yy <= 215:
                    continue    # スタジオの戸口の光
                if 342 <= xx <= 380 and 21 <= yy <= 47:
                    continue    # スタジオの看板
                if yy <= 26 and c[:3] in (P['o2'], P['bulbc'], P['y0']):
                    continue    # ガーランドの電球は自ら光る
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
flat.convert("RGB").save(os.path.join(WEB, "room_design.png"))
print("layers + room_design.png written")

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

# ── ガーランドのまたたき(3コマ) ──
GY0, GBH = 8, 20
gar = Image.new("RGBA", (W * 3, GBH), (0, 0, 0, 0))
gard = ImageDraw.Draw(gar)
for f in range(3):
    for i, (gbx, gby) in enumerate(GAR_BULBS):
        if (i + f) % 3 == 0:
            gard.ellipse([f * W + gbx - 1, gby + 3 - GY0, f * W + gbx + 1, gby + 5 - GY0],
                         fill=C('bulbc'))
            gard.point((f * W + gbx, gby + 2 - GY0), fill=C('o2'))
gar.save(os.path.join(WEB, "design_garland.png"))
print("design_garland.png", gar.size, "band y", GY0, "h", GBH, "電球", len(GAR_BULBS), "個")
