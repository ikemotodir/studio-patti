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
MENU = (40, 24, 86, 114)        # メニューパネル外形(最長ラベル72pxが枠内に収まる幅)
SCR  = (133, 21, 154, 87)       # スクリーン画面(16:9・面積1.32倍。センター209=チェアと同心)
MARQ = (293, 18, 50, 36)        # 電飾マーキー(コンテンツクリエイティブの掲示板)
BTNP = (293, 58, 50, 52)        # 数字ボタンパネル
BTNC = [(306, 71), (330, 71), (306, 95), (330, 95)]   # 丸ボタン中心(19px)
DESK_Y = 138                    # 編集卓の天板
CHAIR = (189, 120)              # ゲーミングチェア左上(センター209)
EDITC = (136, 112, 145)         # 編集機 x,幅の基準 (センター209)

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
    for i in range(40):          # 側壁を浅くして奥壁を広げ、その分をスクリーンに回す
        xx = i if left else W - 1 - i
        t = i / 39.0
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
    cx0 = 39 if left else W - 40
    R('bg', cx0, 13, 1, 156, 'ink')
    R('bg', cx0 + (1 if left else -1), 14, 1, 154, 'n3')
side_wall(True)
side_wall(False)

# ═══════════════ furniture ═══════════════

# ─── 左の壁: スタジオ(TOPの部屋)へ戻る戸口。白色の光がもれる ───
obj('スタジオへの戸口')
for xx in range(8, 37):
    t = (xx - 8) / 28.0
    ytopD = int(58 - 8 * t + 0.5)
    ybotD = int(214 - 46 * t + 0.5)
    for yy in range(ytopD, ybotD):
        rel = (yy - ytopD) / float(ybotD - ytopD)
        if xx <= 9 or xx >= 35:
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
R('furniture', 7, 58, 1, 157, 'ink')
R('furniture', 37, 50, 1, 119, 'ink')
R('furniture', 6, 58, 1, 157, 'q1')
for k in range(4):
    R('furniture', 12 + k * 6, 62 - k, 1, 140 - k * 10, 'gray2' if k % 2 else 'gray1')

# ─── 左の看板: スタジオ(白の電飾・TOPの看板と同じ台形様式) ───
def bake_sign_img(img_name, x0, x1, ytop_fn, ybot_fn, core):
    """プレート(台形)に文字が「描いてある」ように焼く。
    列ごとにプレートの中心線へ縦センタリングするので、パースの傾きに自然に沿う。
    文字を縦に縮小するパースも試したが、9pxの字が6pxまで潰れて
    「ジ」の濁点と「オ」が崩れるため、字高は一定にしている。"""
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
    return int(21 + 8 * (xx - 2) / 36.0 + 0.5)
def signS_bot(xx):
    return int(45 + 1 * (xx - 2) / 36.0 + 0.5)
for xx in range(2, 39):
    ytopS = signS_top(xx)
    ybotS = signS_bot(xx)
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
R('furniture', 1, 21, 1, 25, 'ink'); R('furniture', 39, 29, 1, 18, 'ink')
PXL('furniture', 3, 23, 'wht'); PXL('furniture', 37, 44, 'wht')
bake_sign_img('sign_studio_s.png', 2, 38, signS_top, signS_bot, 'wht')

# ─── 奥壁: 大スクリーン(壁掛け・16:9) ───
obj('大スクリーン')
sx, sy, sw, sh = SCR
# ベゼル: 外枠→面取り→内枠の3層。上面が受光し、下面は影。
R('furniture', sx - 5, sy - 5, sw + 10, sh + 10, 'q2')          # 外枠の面
R('furniture', sx - 5, sy - 5, sw + 10, 1, 'q4')                # 天面の稜線
R('furniture', sx - 5, sy - 5, 1, sh + 10, 'q3')
R('furniture', sx + sw + 4, sy - 5, 1, sh + 10, 'q0')
R('furniture', sx - 5, sy + sh + 4, sw + 10, 1, 'q0')
R('furniture', sx - 4, sy - 4, sw + 8, 1, 'q1')                 # 面取りの谷
R('furniture', sx - 3, sy - 3, sw + 6, sh + 6, 'q1')            # 内枠
R('furniture', sx - 3, sy - 3, sw + 6, 1, 'q0')                 # 内枠の上は暗い(奥まる)
R('furniture', sx - 1, sy - 1, sw + 2, sh + 2, 'ink')           # 画面の縁
R('furniture', sx, sy, sw, sh, 'n0')                            # 消灯した画面
for k in range(4):                                               # ベゼルのネジ
    SCREW('furniture', sx - 4 + (sw + 6) * (k % 2), sy - 4 + (sh + 6) * (k // 2), 'q3', 'q0')
R('furniture', sx + sw // 2 - 8, sy + sh + 1, 16, 2, 'q0')      # ブランドプレート
R('furniture', sx + sw // 2 - 8, sy + sh + 1, 16, 1, 'q3')
for k in range(5):
    PXL('furniture', sx + sw // 2 - 5 + k * 3, sy + sh + 2, 'q4')
for k in range(10):                                              # 通気スリット(凹み)
    R('furniture', sx - 2 + k * 15, sy - 4, 8, 1, 'q0')
PXL('furniture', sx + sw + 2, sy + sh + 2, 'g2')                # 電源LED
PXL('furniture', sx + sw + 2, sy + sh + 3, 'g1')
# 背面のシアンLED(アンビエントライト)は壁に光をこぼす
for xx in range(sx - 7, sx + sw + 7, 2):
    PXL('furniture', xx, sy - 7, 'cyn1')
    PXL('furniture', xx + 1, sy + sh + 6, 'cyn0')
for yy in range(sy - 5, sy + sh + 5, 2):
    PXL('furniture', sx - 7, yy, 'cyn1')
    PXL('furniture', sx + sw + 6, yy, 'cyn0')
PXL('furniture', sx - 7, sy - 7, 'cyn2'); PXL('furniture', sx + sw + 6, sy - 7, 'cyn2')
DITH('bg', sx - 12, sy - 12, sw + 24, 6, None, 'n4', 'sparse')  # 壁への光のこぼれ

# ─── 奥壁: 電飾マーキー(この部屋の看板。小さな電球がぐるりと並ぶ) ───
obj('電飾マーキー')
cx, cy, cw, ch = MARQ
BEVEL('furniture', cx, cy, cw, ch, 'q2', 'q4', 'q0')     # 枠(電球の台座)
INSET('furniture', cx + 4, cy + 4, cw - 8, ch - 8, 'n0', 'q1', 'ink')   # 文字が入る凹み
DITH('bg', cx + 2, cy + ch, cw - 2, 2, None, 'q0', 'check')             # 壁への落ち影

# 電球: 枠のふちを2px内側でぐるりと1周し、4pxおきに並べる
_bl, _bt = cx + 2, cy + 2
_br, _bb = cx + cw - 3, cy + ch - 3
_path = ([(x, _bt) for x in range(_bl, _br + 1)] +
         [(_br, y) for y in range(_bt + 1, _bb + 1)] +
         [(x, _bb) for x in range(_br - 1, _bl - 1, -1)] +
         [(_bl, y) for y in range(_bb - 1, _bt, -1)])
MARQ_BULBS = [_path[i] for i in range(0, len(_path), 4)]
for (bxb, byb) in MARQ_BULBS:
    PXL('furniture', bxb, byb, 'ivory2')

# ─── 奥壁: 数字ボタンパネル(右) ───
obj('数字ボタンパネル')
bx, by, bw, bh = BTNP
BEVEL('furniture', bx, by, bw, bh, 'q2', 'q4', 'q0')
DITH('furniture', bx + 2, by + 2, bw - 4, bh - 4, 'q1', 'q2', 'sparse')  # パネル面
DITH('bg', bx + 2, by + bh, bw - 2, 2, None, 'q0', 'check')              # 壁への落ち影
for i, (bcx, bcy) in enumerate(BTNC):
    EL('furniture', bcx - 9, bcy - 8, bcx + 9, bcy + 10, fill='q0', out='q0')  # 座ぐりの影
    EL('furniture', bcx - 9, bcy - 9, bcx + 9, bcy + 9, fill='pnk1', out='pnk0')
    EL('furniture', bcx - 7, bcy - 7, bcx + 7, bcy + 7, fill='pnk2')
    EL('furniture', bcx - 5, bcy - 6, bcx - 1, bcy - 2, fill='pnkc')           # 樹脂ドームの映り込み
    PXL('furniture', bcx + 5, bcy + 4, 'pnkc')                                 # 反対側の反射光
    NTXT('furniture', bcx - 1, bcy - 2, str(i + 1), 'ink')   # 字形3x5なので中心-1,-2 が真ん中

# ─── 編集卓(壁ぎわのカウンター。天板の小口→膝板→接地影の3層) ───
obj('編集卓')
R('furniture', 40, DESK_Y - 1, 304, 1, 'q5')             # 天板前縁の稜線(全通し)
R('furniture', 40, DESK_Y, 304, 3, 'q3')                 # 天板の小口(厚み)
R('furniture', 40, DESK_Y + 3, 304, 1, 'q1')
R('furniture', 40, DESK_Y + 4, 304, 22, 'q1')            # 膝板
DITH('furniture', 40, DESK_Y + 13, 304, 13, None, 'q0', 'sparse')
for lx in (104, 162, 220, 278):                          # 板の継ぎ目(途中で切る)
    R('furniture', lx, DESK_Y + 5, 1, 16, 'q0')
    R('furniture', lx + 1, DESK_Y + 5, 1, 12, 'q2')
R('furniture', 40, DESK_Y + 26, 304, 2, 'q0')
R('furniture', 42, DESK_Y + 28, 300, 1, 'ink')           # 接地影(最深部)
DITH('bg', 40, DESK_Y + 29, 304, 2, None, 'q0', 'check')

# ─── 編集機(ミキシングコンソール) ───
obj('編集機')
CX0, CX1 = 136, 280
BR0, BR1 = 112, 118                                      # メーターブリッジ面
TP0, TP1 = 120, 131                                      # 操作天板
ARM = 133                                                # アームレスト
LEDS = []

# ── 3面: 面ごとに基準値を変える ──
R('furniture', CX0, BR0, CX1 - CX0 + 1, BR1 - BR0 + 1, 'q1')    # ブリッジ面(中・ディザ禁止)
R('furniture', CX0, BR0, CX1 - CX0 + 1, 1, 'q3')                # 上の稜線
R('furniture', CX0, BR1 + 1, CX1 - CX0 + 1, 1, 'q0')            # ブリッジ下のAO
R('furniture', CX0 - 1, TP0, CX1 - CX0 + 3, TP1 - TP0 + 1, 'q2')# 天板(最も光を拾う)
R('furniture', CX0 - 1, TP0, CX1 - CX0 + 3, 1, 'q4')
R('furniture', CX0 - 1, TP1 + 1, CX1 - CX0 + 3, 1, 'q1')        # 前縁ベベル
BEVEL('furniture', CX0 - 2, ARM, CX1 - CX0 + 5, 3, 'q3', 'q5', 'q0')
R('furniture', CX0 - 2, ARM, CX1 - CX0 + 5, 1, 'mauve')         # 唯一の全通しハイライト
R('furniture', CX0 - 2, ARM + 3, CX1 - CX0 + 5, 1, 'q0')        # アームレスト下のコアシャドウ

# ── サイドチーク(木口。くさび断面の厚みを見せる唯一の部品) ──
for sxc, inw in ((CX0 - 3, 1), (CX1 + 1, -1)):
    for k in range(3):
        R('furniture', sxc + k * inw, BR0 + 1 + k, 1, ARM + 3 - BR0 - k, 'q4' if k else 'q5')
    PXL('furniture', sxc, ARM + 3, 'q0')

# ── パッチベイ(ブリッジ左。凹み+2段のジャック列) ──
INSET('furniture', CX0 + 3, BR0 + 2, 26, 5, 'q0', 'q2', 'ink')
for jy in (BR0 + 3, BR0 + 5):
    for k in range(12):
        PXL('furniture', CX0 + 5 + k * 2, jy, 'ink')
        PXL('furniture', CX0 + 5 + k * 2, jy - 1, 'q3')
for cxp, cyp in ((CX0 + 9, BR0 + 3), (CX0 + 17, BR0 + 5)):   # 挿さったコード
    for k in range(4):
        PXL('furniture', cxp + k // 2, cyp + 2 + k, 'm0')

# ── メーター(点灯/消灯が同時に見える。最明色はここだけ) ──
METER_LV = [4, 5, 3, 5, 2, 4, 6, 3, 5, 4, 2, 5, 3]
METERS = []       # (x, 一番下のy, 段数) 書き出しでコマごとに高さを変える
for i in range(13):
    mxm = CX0 + 34 + i * 4
    if mxm > CX1 - 24:
        break
    for pair in (0, 2):
        lit = max(1, METER_LV[(i * 3 + pair) % len(METER_LV)] - (pair and 1))
        for k in range(6):
            yy = BR1 - 1 - k
            if k < lit:
                c = 'cync' if k == lit - 1 else 'cyn2'
                PXL('furniture', mxm + pair, yy, c)
            else:
                PXL('furniture', mxm + pair, yy, 'q2')       # 消灯も物として描く
        METERS.append((mxm + pair, BR1 - 1, 6))
DITH('furniture', CX0 + 34, BR1 + 2, 52, 2, None, 'q3', 'sparse')   # メーターの照り返し

# ── チャンネルストリップ(ピッチ4px・8本ごとにモジュールの継ぎ目) ──
FADER_LV = [1, 0, 2, 1, 3, 2, 0, 1, 2, 3, 1, 2]
NSTRIP = 30
for i in range(NSTRIP):
    sxs = CX0 + 4 + i * 4
    if sxs > CX1 - 26:
        break
    for r in range(2):                                        # ノブ2段
        ky = TP0 + 1 + r * 3
        R('furniture', sxs, ky, 2, 2, 'q4')
        PXL('furniture', sxs + (i % 3 == 0), ky, 'q5')        # 指標の向きを列ごとに振る
        PXL('furniture', sxs + 2, ky + 1, 'q1')               # 1pxの接地影
    R('furniture', sxs + 1, TP0 + 8, 1, 5, 'q0')              # フェーダー溝
    PXL('furniture', sxs + 2, TP0 + 8, 'q3')                  # 凹みの受光側
    cy = TP0 + 8 + FADER_LV[(i // 3) % len(FADER_LV)]
    R('furniture', sxs, cy, 3, 2, 'gray1')                    # キャップ
    R('furniture', sxs, cy, 3, 1, 'gray2')
    PXL('furniture', sxs + 3, cy + 1, 'q0')                   # キャップの落ち影
for m in range(1, 4):                                          # モジュールの継ぎ目
    mx2 = CX0 + 4 + m * 8 * 4 - 2
    if mx2 < CX1 - 26:
        R('furniture', mx2, TP0 + 1, 1, 10, 'q0')
        R('furniture', mx2 + 1, TP0 + 1, 1, 7, 'q3')

# ── スクリブルストリップ(暗い卓で唯一の水平の明るい線) ──
R('furniture', CX0 + 3, TP0 + 6, CX1 - CX0 - 28, 1, 'q1')     # 差し込み溝
R('furniture', CX0 + 3, TP0 + 7, CX1 - CX0 - 28, 1, 'ivory2')
for i in range(NSTRIP):
    sxs = CX0 + 4 + i * 4
    if sxs > CX1 - 28:
        break
    if (i * 7) % 5 < 3:                                        # 空きチャンネルは無地
        R('furniture', sxs, TP0 + 7, 2 + (i % 2), 1, 'gray0')

# ── マスター/モニター区画(右寄り。対称を壊す) ──
MSX = CX1 - 24
R('furniture', MSX - 2, TP0 + 1, 1, 10, 'q0')                 # 区画の継ぎ目
KNOB('furniture', MSX + 4, TP0 + 4, 3, 'q3', 'q4', 'q5', 'q0')# 大きなモニターノブ
PXL('furniture', MSX + 7, TP0 + 7, 'q0')
for r in range(2):
    for k in range(5):
        bx2, by2 = MSX + 10 + k * 2, TP0 + 2 + r * 2
        on = (k + r) % 4 == 1
        PXL('furniture', bx2, by2, 'm3' if on else 'q1')
        if on:
            LEDS.append((bx2, by2, 'm2', 1))
R('furniture', MSX + 11, TP0 + 8, 1, 4, 'q0')                 # マスターフェーダー(短い)
R('furniture', MSX + 10, TP0 + 9, 3, 2, 'gray1')
R('furniture', MSX + 10, TP0 + 9, 3, 1, 'gray2')

# ── ジョグ/シャトルホイール(卓上で唯一の円。4層) ──
JX, JY = CX1 - 8, TP0 + 6
EL('furniture', JX - 6, JY - 5, JX + 6, JY + 5, fill='q3', out='q0')
for k in range(-5, 6, 2):
    PXL('furniture', JX + k, JY - 5, 'q4')                    # ローレット(刻み)
EL('furniture', JX - 4, JY - 3, JX + 4, JY + 3, fill='q1')    # ディッシュ(皿は上が暗い)
R('furniture', JX - 3, JY - 3, 7, 1, 'q0')
R('furniture', JX - 3, JY + 2, 7, 1, 'q2')                    # 皿の底が受光
R('furniture', JX - 1, JY - 1, 2, 2, 'q4')                    # ハブ
PXL('furniture', JX - 1, JY - 1, 'q5')
PXL('furniture', JX + 2, JY, 'q0')                            # 指かけの窪み
PXL('furniture', JX + 3, JY, 'q3')
for k in range(9):                                            # 弧を描く落ち影
    PXL('furniture', JX - 4 + k, JY + 6 + (0 if 2 < k < 6 else 1), 'q0')

# ─── メニューパネル(デスクに立つ大きなプログラムボード) ───
obj('メニューパネル')
mx, my, mw, mh = MENU
# 枠: 外→面取り→内の3層。上面が受光し、下面は影(角丸矩形にしない)
R('furniture', mx, my, mw, mh, 'q2')
R('furniture', mx, my, mw, 1, 'q4')                       # 天面の稜線
R('furniture', mx, my, 1, mh, 'q3')
R('furniture', mx + mw - 1, my, 1, mh, 'q0')
R('furniture', mx, my + mh - 1, mw, 1, 'q0')
INSET('furniture', mx + 2, my + 2, mw - 4, mh - 4, 'n0', 'q1', 'ink')   # カードが入る凹み
R('furniture', mx + 4, my + 4, mw - 8, 1, 'pnk0')         # 内側のネオン(上辺)
for i in range(5):                                         # 差し込みカード5枚
    cy2 = my + 6 + i * 22
    R('furniture', mx + 3, cy2, mw - 6, 19, 'q1')         # カードの面
    R('furniture', mx + 3, cy2, mw - 6, 1, 'q3')          # カードの上辺(受光)
    R('furniture', mx + 3, cy2 + 18, mw - 6, 1, 'q0')     # 下辺の影
    R('furniture', mx + 3, cy2 + 19, mw - 6, 1, 'n0')     # レールの隙間
    R('furniture', mx + mw - 4, cy2 + 2, 1, 15, 'q0')     # 差し込みレール(右)
    R('furniture', mx + 3, cy2 + 2, 1, 15, 'q2')          # レール(左)
for k in range(2):                                         # 上部のクリップ
    R('furniture', mx + 8 + k * (mw - 22), my + 1, 6, 3, 'gray0')
    R('furniture', mx + 8 + k * (mw - 22), my + 1, 6, 1, 'gray2')
SCREW('furniture', mx + 2, my + mh - 4, 'q3', 'q0')
SCREW('furniture', mx + mw - 4, my + mh - 4, 'q3', 'q0')
R('furniture', mx + 6, my + mh, 3, 3, 'q0')               # デスクへの接地脚
R('furniture', mx + mw - 9, my + mh, 3, 3, 'q0')
DITH('furniture', mx + 4, my + mh + 3, mw - 8, 2, None, 'q0', 'check')   # 接地影

# ─── ゲーミングチェア(編集卓の手前・後ろ姿。背後の大スクリーンで逆光) ───
obj('ゲーミングチェア')
gx, gy = CHAIR
CXC = gx + 20                                   # 中心線
BK0 = gy + 9                                    # 背もたれ上端
BK_H = 35

def _half(dy):
    """背もたれの半幅(砂時計)。"""
    if dy < 12:  return 14                      # 肩: ウイングが張る
    if dy < 22:  return 14 - (dy - 12) * 2 // 5 # 絞り
    if dy < 30:  return 10                      # 腰
    return 10 + (dy - 30) // 2                  # 根元でわずかに広がる

# ── ヘッドレスト(別部品。背もたれより手前に浮く) ──
for dy in range(8):
    hw = 8 if 1 <= dy <= 6 else 7
    for xx in range(CXC - hw, CXC + hw + 1):
        d = min(xx - (CXC - hw), (CXC + hw) - xx)
        if dy == 0:
            c = 'mauve'                          # 天面は逆光を最も受ける
        elif d == 0:
            c = 'pnk1'
        elif dy >= 6:
            c = 'q0'
        else:
            c = 'q1' if d < 3 else 'q2'
        PXL('furniture', xx, gy + dy, c)
R('furniture', CXC - 7, gy + 8, 15, 1, 'ink')    # 枕と背もたれの隙間の影(別部品の証拠)
for sxh in (CXC - 6, CXC + 5):                   # ストラップを通すスリット
    R('furniture', sxh, gy + 2, 1, 3, 'q0')
R('furniture', CXC - 6, gy + 3, 12, 1, 'q0')     # 背面を横切るストラップ
R('furniture', CXC - 6, gy + 3, 12, 1, 'q2')

# ── 背もたれ: 樹脂シェル(中央・フラット)+張り地(外周・階調) ──
for dy in range(BK_H):
    yy = BK0 + dy
    hw = _half(dy)
    x0c, x1c = CXC - hw, CXC + hw
    for xx in range(x0c, x1c + 1):
        d = min(xx - x0c, x1c - xx)
        if d == 0:
            c = 'pnk1' if dy < 24 else 'q2'      # 逆光を受けるふち
        elif d == 1:
            c = 'q2' if dy < 24 else 'q1'
        elif d < 5:
            c = 'q1'                              # 張り地のウイング
        else:
            c = 'q1' if dy < 3 else 'q0'          # 樹脂シェル(ディザを入れずフラットに保つ)
        PXL('furniture', xx, yy, c)
R('furniture', CXC - 9, BK0, 19, 1, 'q2')         # 上端の張り地の縁(パイピング)
for dy in range(2, BK_H - 4):                     # パネルの継ぎ目(溝)。光源側だけ明るく
    yy = BK0 + dy
    off = 6 - (dy > 22)
    for sgn in (-1, 1):
        PXL('furniture', CXC + sgn * off, yy, 'q0')
        PXL('furniture', CXC + sgn * off - 1, yy, 'q1')
for dy in range(3, 20, 3):                        # ステッチ(光の当たる上半分だけ)
    PXL('furniture', CXC - 7, BK0 + dy, 'mauve')
    PXL('furniture', CXC + 7, BK0 + dy, 'mauve')
R('furniture', CXC - 8, BK0 + 27, 17, 1, 'q0')    # ランバーのストラップ
R('furniture', CXC - 8, BK0 + 27, 17, 1, 'q2')
PXL('furniture', CXC - 9, BK0 + 27, 'q1'); PXL('furniture', CXC + 9, BK0 + 27, 'q1')
for kx in (CXC - 5, CXC + 4):                     # 締め付けによる引きつれ
    PXL('furniture', kx, BK0 + 26, 'q2'); PXL('furniture', kx + 1, BK0 + 28, 'q0')

# ── 座面・ガスシリンダー・5本脚 ──
SY = BK0 + BK_H
R('furniture', CXC - 13, SY, 27, 3, 'q1')         # 座面の後ろ側がのぞく
R('furniture', CXC - 13, SY, 27, 1, 'q3')
R('furniture', CXC - 13, SY + 3, 27, 1, 'ink')
R('furniture', CXC - 2, SY + 4, 4, 6, 'q2')       # 支柱
R('furniture', CXC - 2, SY + 4, 1, 6, 'q4')
R('furniture', CXC + 1, SY + 4, 1, 6, 'q0')
R('furniture', CXC - 3, SY + 10, 6, 3, 'gray0')   # ガスシリンダーのカバー
R('furniture', CXC - 3, SY + 10, 6, 1, 'gray1')
for ddx, ddy, wlen in ((-15, 7, 2), (-8, 9, 2), (8, 9, 2), (15, 7, 2)):
    x2, y2 = CXC + ddx, SY + 13 + ddy
    D['furniture'].line([CXC, SY + 13, x2, y2], fill=C('q1'), width=wlen)
    OD['furniture'].line([CXC, SY + 13, x2, y2], fill=_oid('furniture'), width=wlen)
    D['furniture'].line([CXC, SY + 12, x2, y2 - 1], fill=C('q3'), width=1)
    EL('furniture', x2 - 2, y2 - 1, x2 + 2, y2 + 3, fill='q2', out='q0')   # キャスター
    PXL('furniture', x2 - 1, y2, 'q4')
DITH('bg', CXC - 20, SY + 22, 40, 3, None, 'q0', 'check')                  # 床の接地影

# ─── 戸口の光の床へのこぼれ(白) ───
obj('スタジオへの戸口')
for yy in range(170, 210):
    reach = 30 + int((yy - 170) * 0.9)
    for xx in range(3, 3 + reach):
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
    {'pos': (309, 84),  'r': 52,  's': 0.50, 'e': 1.4, 'tint': P['pnk2'], 'occ': False},  # 数字ボタン
    {'pos': (309, 36),  'r': 62,  's': 0.62, 'e': 1.3, 'tint': P['ivory'], 'occ': False},  # 電飾マーキー
    {'pos': (86, 82),   'r': 46,  's': 0.34, 'e': 1.4, 'tint': P['pnk2'], 'occ': False},  # メニューパネル
    {'pos': (205, 120), 'r': 96,  's': 0.62, 'e': 1.3, 'tint': P['cyn1'], 'occ': False},  # 編集機のメーター
    {'pos': (192, 150), 'r': 200, 's': 0.46, 'e': 1.2, 'tint': P['q5'],   'occ': False},  # 室内バウンス
]
AMB = 0.52

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
                if cx <= xx <= cx + cw - 1 and cy <= yy <= cy + ch - 1:
                    continue    # 電飾マーキーは自ら光る
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

# ═══════ 空気感: ふちを落として視線を中央へ集める(ビネット) ═══════
# 部屋ごとに VIG_C(中心) と VIG_S(強さ) を変えられる
try:
    VIG_C
except NameError:
    VIG_C, VIG_S = (W * 0.5, H * 0.46), 1.0
for _ln in ('bg', 'furniture', 'props'):
    _px = L[_ln].load()
    for yy in range(H):
        _dy = abs(yy - VIG_C[1]) / (H * 0.5)
        for xx in range(W):
            _dx = abs(xx - VIG_C[0]) / (W * 0.5)
            _d = (_dx ** 2.3 + _dy ** 2.3) ** 0.5 * VIG_S
            if _d < 0.80:
                continue
            c = _px[xx, yy]
            if c[3] == 0 or c[:3] == INK:
                continue
            n = 2 if _d > 1.06 else (1 if _d > 0.93 else (1 if (xx + yy) % 2 == 0 else 0))
            out = c[:3]
            for _ in range(n):
                out = DARKER.get(out, out)
            _px[xx, yy] = tuple(out) + (255,)

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
BY0, BBH = 106, 34
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
# メーターは「レベルが踊る」。コマごとに点灯段数を変え、消灯部も必ず描く
_mtr = [t for t in METERS if _own[t[0], t[1]] == _mc_oid]
for f in range(3):
    for i, (lx, lyb, seg) in enumerate(_mtr):
        lv = 2 + int(abs(math.sin(i * 1.7 + f * 2.1)) * (seg - 2) + 0.5)
        for k in range(seg):
            yy = lyb - k
            if k < lv:
                col = 'cync' if k == lv - 1 else 'cyn2'
            else:
                col = 'q2'
            bd.point((f * W + lx, yy - BY0), fill=C(col))
blink.save(os.path.join(WEB, "edit_blink.png"))
print("edit_blink.png", blink.size, "band y", BY0, "h", BBH)

# ── マーキーの電球の流れ(4コマ・ぐるりと回るチェイス) ──
MY0, MBH = MARQ[1], MARQ[3]
mq = Image.new("RGBA", (W * 4, MBH), (0, 0, 0, 0))
mqd = ImageDraw.Draw(mq)
for f in range(4):
    for i, (bxb, byb) in enumerate(MARQ_BULBS):
        if (i + f) % 4 == 0:
            mqd.point((f * W + bxb, byb - MY0), fill=C('wht'))
        elif (i + f) % 4 == 1:
            mqd.point((f * W + bxb, byb - MY0), fill=C('ivory'))
mq.save(os.path.join(WEB, "marquee_blink.png"))
print("marquee_blink.png", mq.size, "band y", MY0, "h", MBH, "電球", len(MARQ_BULBS), "個")
