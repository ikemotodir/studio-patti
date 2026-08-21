"""STUDIO PATCH room v3.1 - Pixel Jeff quality pass.
Layers: bg / window / furniture / props / mayu / light
Canvas 384x216. Fixes: window/monitor overlap, figure shelf, Mayu redraw, more clutter.
"""
from PIL import Image, ImageDraw, ImageChops
import os, json, math, io, re

WEB = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(WEB, "room_layers")
SP = ("C:\\Users\\studi\\AppData\\Local\\Temp\\claude\\"
      "C--Users-studi-Desktop-Claude-apps\\3485a72e-2b4a-48a5-8091-a6345c07fe32\\scratchpad\\")
os.makedirs(LAY, exist_ok=True)
W, H = 384, 240      # 下に24px拡張: 転がる絵本とテキストボックスの前景ゾーン

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
}

names = ["bg", "window", "furniture", "props", "garland", "mayu", "light"]
L = {n: Image.new("RGBA", (W, H), (0, 0, 0, 0)) for n in names}
D = {n: ImageDraw.Draw(L[n]) for n in names}

def C(c, a=255):
    return (P[c] + (a,)) if isinstance(c, str) else (tuple(c) + (a,))

# ── オブジェクト単位の切り分け(Aseprite のレイヤー分け用) ──────────────
# 描いた瞬間に「その画素はどのプロップのものか」を所有マップへ記録しておく。
# 後段の陰影パスは既にある画素を塗り替えるだけなので、完成した部屋の画素を
# この所有マップで切り抜けば、陰影込みのプロップ画像がそのまま取り出せる。
OWNER = {n: Image.new("I", (W, H), 0) for n in names}
OD = {n: ImageDraw.Draw(OWNER[n]) for n in names}
OBJ_ID, _OSEQ, _OCUR = {}, [0], [None]

def obj(name=None):
    """これ以降の描画が属するプロップ名を決める(引数なしで解除)。"""
    _OCUR[0] = name

def _oid(l):
    """いま開いているプロップの、そのレイヤーでの通し番号"""
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
        if fill:                      # 塗りがある時だけ内側まで自分のものにする
            OD[l].ellipse([x0, y0, x1, y1], fill=i)
        else:
            OD[l].ellipse([x0, y0, x1, y1], outline=i, width=ow)

FONT = {
 'A': "010 101 111 101 101", 'C': "011 100 100 100 011", 'D': "110 101 101 101 110",
 'H': "101 101 111 101 101", 'I': "111 010 010 010 111", 'O': "010 101 101 101 010",
 'P': "110 101 110 100 100", 'S': "011 100 010 001 110", 'T': "111 010 010 010 010",
 'U': "101 101 101 101 111", '8': "111 101 111 101 111", '.': "000 000 000 000 010",
 'R': "110 101 110 110 101", 'B': "110 101 110 101 110",
 ' ': "000 000 000 000 000",
}
def TXT(l, x, y, s, c):
    cx = x
    for ch in s:
        rows = FONT.get(ch, FONT[' ']).split()
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '1': PXL(l, cx + rx, y + ry, c)
        cx += 4

# ═══════════════ bg ═══════════════
obj()
R('bg', 0, 0, W, H, 'n2')
R('bg', 0, 0, W, 10, 'ink')
R('bg', 0, 6, W, 1, 'q1')
R('bg', 0, 10, W, 2, 'q0')
for x in range(4, W, 24):
    PXL('bg', x, 4, 'r1'); PXL('bg', x + 1, 4, 'r1')
for x in range(68, W - 48, 48):                     # 赤い吊りタブ(sankou流)
    R('bg', x, 10, 5, 6, 'm1')
    R('bg', x, 10, 5, 1, 'm0')
    PXL('bg', x + 2, 13, 'm0')

R('bg', 0, 12, W, 20, 'n3')                          # 奥壁: 多段グラデーション
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

R('bg', 0, 148, W, 92, 'q1')                         # 床
R('bg', 0, 148, W, 3, 'q0')
for i, y in enumerate([161, 175, 189, 203, 217, 231]):    # 床の継ぎ目はマゼンタに光る(sankou流)
    R('bg', 0, y, W, 1, 'm0')
    for x in range(0, W, 16):
        PXL('bg', x + (i * 5) % 16, y + 1, 'm1')
for i, x in enumerate(range(0, W + 32, 32)):
    for j, yy in enumerate([(149, 12), (162, 13), (176, 13), (190, 13), (204, 13), (218, 13), (232, 8)]):
        xo = (x + (16 if j % 2 else 0)) % (W + 32)
        R('bg', xo, yy[0], 1, yy[1], 'q0')
for x, y in [(60,168),(150,183),(250,170),(340,180),(90,194),(230,194),(160,222),(320,226),(50,232)]:
    R('bg', x, y, 3, 1, 'q0')
# 画面から出る光の床への映り込み(濡れた床のゲーム表現)
for rx in range(160, 240, 7):
    R('bg', rx, 149, 1, 5 - (rx // 7) % 3, 'b1')
    R('bg', rx + 1, 149, 1, 2, 'b1')
for rx in range(254, 300, 8):
    R('bg', rx, 149, 1, 4 - (rx // 8) % 2, 'n4')
    PXL('bg', rx + 1, 149, 'n4')
# 床板ごとのトーン差と摩耗(1pxのこだわりゾーン)
for bi, (by0, by1) in enumerate([(149,161),(162,175),(176,189),(190,203),(204,217),(218,231)]):
    if bi % 2 == 0:
        for yy5 in range(by0 + 2, by1 - 2):
            for xx5 in range(0, W):
                if (xx5 + yy5 + bi) % 6 == 0:
                    PXL('bg', xx5, yy5, 'q2')
for wx5, wy5 in [(88,171),(132,178),(210,166),(262,181),(150,186),(238,192),(302,188),
                 (180,232),(280,226),(120,224)]:
    PXL('bg', wx5, wy5, 'q0'); PXL('bg', wx5 + 1, wy5, 'q2')
for sx5 in range(56, W - 48, 24):
    PXL('bg', sx5, 160, 'm1'); PXL('bg', sx5 + 12, 174, 'm0')
DI('bg', 0, 224, W, 6, 'q1', 'q0')
DI('bg', 0, 230, W, 10, 'q0', 'ink')

# ─── 側壁: 左=デザイン室 / 右=編集室 へつづく(奥に向かって狭まる) ───
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
    R('bg', cx0, 13, 1, 156, 'ink')                  # 奥の縦の角
    R('bg', cx0 + (1 if left else -1), 14, 1, 154, 'n3')
side_wall(True)
side_wall(False)

# ═══════════════ window : 楕円窓(右上・編集室側) ═══════════════
WX, WY, WRX, WRY = 290, 44, 42, 30
obj('楕円窓')
EL('window', WX-WRX-4, WY-WRY-4, WX+WRX+4, WY+WRY+4, fill='ink')
EL('window', WX-WRX-1, WY-WRY-1, WX+WRX+1, WY+WRY+1, fill='q3')
sky = Image.new("RGBA", (W, H), (0,0,0,0))
sd = ImageDraw.Draw(sky)
sd.ellipse([WX-WRX+2, WY-WRY+2, WX+WRX-2, WY+WRY-2], fill=(255,255,255,255))
mask = sky.split()[3]
tmp = Image.new("RGBA", (W, H), (0,0,0,0))
td = ImageDraw.Draw(tmp)
td.rectangle([WX-WRX, WY-WRY, WX+WRX, WY+WRY], fill=C('b0'))
for yy in range(WY+6, WY+WRY):
    for xx in range(WX-WRX, WX+WRX):
        if (xx+yy) % 2 == 0: td.point((xx, yy), fill=C('n1'))
td.rectangle([WX-WRX, WY-WRY, WX+WRX, WY-14], fill=C('b1'))
for yy in range(WY-14, WY-4):
    for xx in range(WX-WRX, WX+WRX):
        if (xx+yy) % 2 == 0: td.point((xx, yy), fill=C('b1'))
td.rectangle([WX-WRX, WY-WRY, WX+WRX, WY-24], fill=C('b2'))
for yy in range(WY-24, WY-16):
    for xx in range(WX-WRX, WX+WRX):
        if (xx+yy) % 2 == 0: td.point((xx, yy), fill=C('b2'))
L['window'].paste(Image.composite(tmp, L['window'], mask), (0,0))
for i in range(-WRX + 8, WRX - 8):
    hh = int(5 + 3 * math.sin(i * 0.11))
    R('window', WX + i, WY + WRY - 8 - hh, 1, hh, 'n1')
for sx, sy in [(262,30),(278,24),(308,20),(322,34),(270,44),(318,52),(278,60),(300,62),(264,56),(292,26)]:
    PXL('window', sx, sy, 'b5' if (sx+sy)%3 else 'wht')
PXL('window', 278, 23, 'b3'); PXL('window', 278, 25, 'b3'); PXL('window', 277, 24, 'b3'); PXL('window', 279, 24, 'b3')
# 月はBonbon(月のおばけ)がその位置に入るためアート削除。ハローは残す
for cx5, cy5, cw5 in [(264, 28, 16), (308, 52, 12)]:  # 夜雲のシルエット
    R('window', cx5, cy5, cw5, 3, 'n1')
    R('window', cx5 + 2, cy5 - 2, cw5 - 5, 2, 'n1')
    R('window', cx5 + 1, cy5 + 3, cw5 - 2, 1, 'b0')
R('window', WX-1, WY-WRY+1, 3, 2*WRY-2, 'q3')
R('window', WX-WRX+1, WY-1, 2*WRX-2, 3, 'q3')
R('window', WX-1, WY-WRY+1, 1, 2*WRY-2, 'q5')
R('window', WX-WRX+1, WY-1, 2*WRX-2, 1, 'q5')
EL('window', WX-WRX-1, WY-WRY-1, WX+WRX+1, WY+WRY+1, out='q4', ow=2)
EL('window', WX-WRX-4, WY-WRY-4, WX+WRX+4, WY+WRY+4, out='ink', ow=2)
PXL('window', WX-WRX+7, WY-WRY+10, 'q5')

# ═══════════════ furniture ═══════════════
P['chrome'] = (206, 208, 222); P['chrome2'] = (150, 152, 172)
P['ivory'] = (247, 238, 216); P['ivory2'] = (206, 194, 172)
P['wood'] = (126, 78, 46); P['wood2'] = (92, 54, 32)
P['tuber'] = (214, 46, 62)
P['wwarm'] = (52, 48, 88)
P['wneon'] = (42, 36, 80)
P['spill'] = (62, 122, 106)
P['bulbc'] = (255, 246, 200)
P['pnk0'] = (132, 54, 96); P['pnk1'] = (186, 88, 140)
P['pnk2'] = (236, 148, 190); P['pnkc'] = (255, 212, 232)
P['bulbh'] = (176, 138, 74)

FONT.update({
 'M': "101 111 101 101 101", 'N': "110 101 101 101 101",
 'Y': "101 101 010 010 010", 'E': "111 100 110 100 111",
 'K': "101 110 100 110 101", 'L': "100 100 100 100 111",
 'G': "011 100 101 101 011", 'W': "101 101 101 111 101",
})
def TXT2(l, x, y, s, c):
    cx = x
    for ch in s:
        rows = FONT.get(ch, FONT[' ']).split()
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '1': R(l, cx + rx * 2, y + ry * 2, 2, 2, c)
        cx += 8

def dpatch(l, x, y, w, h, c, den=2, ph=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx + yy + ph) % den == 0:
                PXL(l, xx, yy, c)

# ─── 左の壁: デザイン室の戸口(あたたかい黄色の光がもれる) ───
obj('デザイン室の入口')
for xx in range(10, 39):
    t = (xx - 10) / 28.0
    ytopD = int(58 - 8 * t + 0.5)
    ybotD = int(214 - 46 * t + 0.5)
    for yy in range(ytopD, ybotD):
        rel = (yy - ytopD) / float(ybotD - ytopD)
        if xx <= 11 or xx >= 37:
            c = 'q3'
        elif rel < 0.10:
            c = 'brick' if (xx + yy) % 2 else 'o0'
        elif rel < 0.34:
            c = 'o0' if (xx + yy) % 2 else 'o1'
        elif rel < 0.62:
            c = 'o1' if (xx + yy) % 2 else 'o2'
        elif rel < 0.86:
            c = 'o2'
        else:
            c = 'bulbc' if (xx + yy) % 2 else 'o2'
        PXL('furniture', xx, yy, c)
    PXL('furniture', xx, ytopD, 'ink')
    PXL('furniture', xx, ybotD, 'ink')
R('furniture', 9, 58, 1, 157, 'ink')
R('furniture', 39, 50, 1, 119, 'ink')
R('furniture', 8, 58, 1, 157, 'q1')
for k in range(4):
    R('furniture', 14 + k * 6, 62 - k, 1, 140 - k * 10, 'o2' if k % 2 else 'o1')

# ─── 吊り看板: 池本さん制作のドット文字(1ドット=1px)を1画素も変えずに載せる ───
# 文字の実寸(デザイン室78px/編集室47px)が側壁の台形パネル(最大43px)より大きいため、
# 天井から吊るした電飾看板として前面に出す。板の厚みと吊り棒で立体感を出す。
def hang_sign(img_name, x0, y0, core, edge_hi, edge_lo, spark, rods):
    m = Image.open(os.path.join(WEB, img_name)).convert('RGBA')
    tw, th = m.size
    bw, bh = tw + 4, th + 5
    x1, y1 = x0 + bw - 1, y0 + bh - 1
    for rx in rods:                                    # 吊り棒(天井側はナビの裏に隠れる)
        for yy in range(2, y0):
            PXL('furniture', rx, yy, 'q3' if yy % 3 else 'q4')
    R('furniture', x0, y0, bw, 1, 'ink')
    R('furniture', x0, y1, bw, 1, 'ink')
    R('furniture', x0, y0, 1, bh, 'ink'); R('furniture', x1, y0, 1, bh, 'ink')
    R('furniture', x0 + 1, y0 + 1, bw - 2, 1, edge_hi)   # 上縁の灯り
    R('furniture', x0 + 1, y0 + 2, bw - 2, bh - 4, 'q0') # 面
    R('furniture', x0 + 1, y1 - 1, bw - 2, 1, edge_lo)   # 下縁の陰
    PXL('furniture', x0 + 2, y0 + 2, spark)
    R('furniture', x0 + 1, y1 + 1, bw - 2, 1, 'q1')      # 板の厚み
    mp = m.load()
    for gy in range(th):
        for gx in range(tw):
            if mp[gx, gy][3] > 0:
                PXL('furniture', x0 + 2 + gx, y0 + 3 + gy, core)

obj('デザイン室の看板')
hang_sign('sign_design.png', 2, 28, 'bulbc', 'o1', 'o0', 'o2', rods=(6, 79))

# ─── 右の壁: 編集室の戸口(淡いピンクの光がもれる) ───
obj('編集室の入口')
for xx in range(346, 375):
    t = (374 - xx) / 28.0
    ytopD = int(58 - 8 * t + 0.5)
    ybotD = int(214 - 46 * t + 0.5)
    for yy in range(ytopD, ybotD):
        rel = (yy - ytopD) / float(ybotD - ytopD)
        if xx <= 347 or xx >= 373:
            c = 'q3'
        elif rel < 0.10:
            c = 'q1' if (xx + yy) % 2 else 'pnk1'
        elif rel < 0.34:
            c = 'pnk1' if (xx + yy) % 2 else 'q2'
        elif rel < 0.62:
            c = 'pnk1' if (xx + yy) % 2 else 'pnk2'
        elif rel < 0.86:
            c = 'pnk2'
        else:
            c = 'pnkc' if (xx + yy) % 2 else 'pnk2'
        PXL('furniture', xx, yy, c)
    PXL('furniture', xx, ytopD, 'ink')
    PXL('furniture', xx, ybotD, 'ink')
R('furniture', 374, 58, 1, 157, 'ink')
R('furniture', 345, 50, 1, 119, 'ink')
R('furniture', 375, 58, 1, 157, 'q1')
for k in range(4):
    R('furniture', 368 - k * 6, 62 - k, 1, 140 - k * 10, 'pnk2' if k % 2 else 'pnk1')

# 右の吊り看板: 編集室(テーマカラー=ピンク。文字は池本さんデータをピンクで焼く)
obj('編集室の看板')
hang_sign('sign_hensyu.png', 332, 28, 'pnkc', 'pnk1', 'pnk0', 'pnk2', rods=(336, 378))

# ─── 壁かけの棚(板+ブラケット)と本たち ───
C_shade = {'m2':'m0','cor':'brick','g2':'g0','b3':'b0','m1':'m0','cream':'cor2','b2':'b0','m3':'m1','g1':'g0','r2':'r0'}
def bookrow(y, specs, bx):
    for bw, bh, c in specs:
        R('furniture', bx, y - bh, bw, bh, c)
        R('furniture', bx, y - bh, bw, 2, 'ink')
        R('furniture', bx, y - bh, 1, bh, C_shade.get(c, 'ink'))
        PXL('furniture', bx + bw - 1, y - bh + 3, 'cream')
        bx += bw + 1

obj('壁かけの棚')
for py in (76, 108):
    R('furniture', 50, py, 72, 3, 'q3')
    R('furniture', 50, py, 72, 1, 'q5')
    R('furniture', 50, py + 3, 72, 1, 'ink')
    for bx in (56, 112):
        R('furniture', bx, py + 4, 3, 6, 'q2')
        R('furniture', bx, py + 4, 1, 6, 'q1')
        PXL('furniture', bx + 1, py + 9, 'q0')
obj('本たち')
bookrow(76, [(4,15,'m2'),(5,13,'cor'),(4,16,'g2'),(5,14,'b3'),(4,12,'m1'),(5,15,'cream'),
             (4,13,'b2'),(5,16,'m3'),(4,11,'g1'),(5,14,'r2'),(4,15,'b3'),(5,12,'cor')], 52)
# 2段目の左: 絵本『おばけのパッチ』の表紙を面出し(クリックで絵本ビューア)
obj('おばけのパッチの絵本')
# 実際の装丁と同じ正方形の表紙(白地に大きな円、円の中にパッチの後ろ姿)。棚の中央に置く
O('furniture', 74, 84, 24, 24, 'wht', 'ink')
R('furniture', 75, 85, 22, 1, 'ivory2')
R('furniture', 75, 86, 22, 3, 'b2')                    # タイトル帯
EL('furniture', 78, 91, 93, 104, out='b2')             # 大きな円
EL('furniture', 82, 93, 89, 101, fill='wht', out='ink')# パッチの後ろ姿
R('furniture', 83, 102, 2, 1, 'ink'); R('furniture', 87, 102, 2, 1, 'ink')
R('furniture', 77, 105, 18, 1, 'gray1')

# ─── 掛け時計(棚の右上。針はWeb側でリアルタイム描画) ───
obj('掛け時計')
EL('furniture', 108, 32, 140, 64, fill='ivory', out='ink')
EL('furniture', 110, 34, 138, 62, out='q4')
for i in range(12):
    ang = i * math.pi / 6
    tx = int(round(124 + math.sin(ang) * 13))
    ty = int(round(48 - math.cos(ang) * 13))
    if i % 3 == 0:
        R('furniture', tx - 1, ty - 1, 2, 2, 'ink')
    else:
        PXL('furniture', tx, ty, 'gray1')
R('furniture', 123, 47, 2, 2, 'ink')
PXL('furniture', 114, 38, 'wht')

# ─── 壁ぎわのカウンター(部屋の隅から隅まで) ───
obj('カウンター')
R('furniture', 47, 138, 290, 1, 'mauve')
R('furniture', 47, 139, 290, 3, 'q4')
R('furniture', 47, 142, 290, 2, 'q2')
R('furniture', 47, 144, 290, 20, 'q1')                 # 前板
for lx in (47, 104, 162, 220, 278, 336):
    R('furniture', lx, 144, 1, 20, 'q0')
R('furniture', 47, 162, 290, 2, 'q0')
R('furniture', 47, 164, 290, 2, 'ink')
R('furniture', 49, 166, 286, 2, 'q0')                  # 接地影

# ─── カウンターの上: 地球儀・小物 ───
obj('地球儀')
EL('furniture', 94, 117, 112, 135, fill='b2', out='ink')
for xx, yy, w2, h2 in [(97,121,6,4),(104,119,5,3),(100,127,7,4),(107,129,4,3)]:
    R('furniture', xx, yy, w2, h2, 'g1'); PXL('furniture', xx, yy, 'g2')
R('furniture', 110, 115, 2, 4, 'y0')
R('furniture', 100, 135, 8, 3, 'q3')
R('furniture', 102, 138, 4, 1, 'ink')
PXL('furniture', 98, 120, 'b4'); PXL('furniture', 99, 121, 'b4')
obj('鉢植え')
R('furniture', 322, 131, 7, 8, 'brick')
PXL('furniture', 324, 128, 'g1'); PXL('furniture', 326, 127, 'g2'); PXL('furniture', 327, 129, 'g1')
PXL('furniture', 323, 129, 'g0')

# ─── COMPANYモニタ(横長の大型・この部屋の主役の光) ───
obj('COMPANYモニタ')
O('furniture', 146, 96, 100, 34, 'q1', 'ink')
R('furniture', 148, 98, 96, 1, 'q4')
R('furniture', 149, 99, 94, 30, 'ink')
R('furniture', 150, 100, 92, 28, 'n0')
DI('furniture', 150, 124, 92, 4, 'n0', 'n1')
TXT2('furniture', 169, 106, "COMPANY", 'b4')
R('furniture', 169, 119, 54, 1, 'b1')
PXL('furniture', 238, 102, 'b4'); PXL('furniture', 236, 104, 'b3')
R('furniture', 193, 130, 6, 7, 'q2'); R('furniture', 193, 130, 1, 7, 'q4')   # 中央の支柱
R('furniture', 180, 137, 32, 1, 'mauve')                                     # 土台
R('furniture', 180, 138, 32, 2, 'q4')
R('furniture', 182, 139, 28, 1, 'q1')
PXL('furniture', 243, 126, 'g2')                       # 電源LED
obj('キーボード')
R('furniture', 186, 139, 26, 3, 'q2')
for kx in range(187, 210, 3): PXL('furniture', kx, 140, 'q4')

# ═══════════════ props ═══════════════
GAR_SPANS = [(46, 192, 14, 8, 6), (192, 338, 14, 8, 6)]
def garland_positions():
    out = []
    for x0, x1, y0, sag, nb in GAR_SPANS:
        for i in range(nb):
            t = (i + 0.5) / nb
            out.append((int(x0 + t * (x1 - x0)),
                        y0 + int(sag * (1 - (2 * t - 1) ** 2))))
    return out

def draw_garland(layer_draw_px, core_of, off=(0, 0)):
    ox, oy = off
    for x0, x1, y0, sag, nb in GAR_SPANS:
        for xx in range(x0, x1):
            t = (xx - x0) / (x1 - x0)
            yy = y0 + int(sag * (1 - (2 * t - 1) ** 2))
            layer_draw_px(xx + ox, yy + oy, 'ink')
    for i, (bx, by) in enumerate(garland_positions()):
        for dx3 in range(3):
            layer_draw_px(bx - 1 + dx3 + ox, by + 1 + oy, 'gray0')
            layer_draw_px(bx - 1 + dx3 + ox, by + 2 + oy, 'gray0')
        for dy3 in range(5):
            for dx3 in range(5):
                layer_draw_px(bx - 2 + dx3 + ox, by + 3 + dy3 + oy, 'o1')
        for dx3 in range(5):
            layer_draw_px(bx - 2 + dx3 + ox, by + 3 + oy, 'o2')
        cc = core_of(i)
        for dy3 in range(3):
            for dx3 in range(3):
                layer_draw_px(bx - 1 + dx3 + ox, by + 4 + dy3 + oy, cc)

obj('ガーランド')
draw_garland(lambda x, y, c: PXL('garland', x, y, c), lambda i: 'o2')

# ─── ギャラリー: 黒い額 × モノクロの絵 ×11枚(スケッチの枚数) ───
obj('額縁の壁(ギャラリー)')
def frameM(x, y, w, h):
    O('props', x, y, w, h, 'q1', 'ink')
    R('props', x + 1, y + 1, w - 2, 1, 'q2')
    R('props', x + 2, y + 2, w - 4, h - 4, 'n1')
# ─ 1段目(3枚) ─
frameM(150, 34, 24, 16)                              # 丘と月
R('props', 152, 44, 20, 4, 'gray0')
EL('props', 164, 37, 169, 42, fill='wht')
frameM(180, 32, 16, 20)                              # パッチの肖像
R('props', 184, 38, 8, 9, 'wht')
PXL('props', 186, 41, 'ink'); PXL('props', 189, 41, 'ink')
R('props', 186, 45, 4, 1, 'gray2')
frameM(202, 34, 26, 14)                              # 波
for wx in range(204, 226, 4):
    PXL('props', wx, 40 + (wx // 4) % 2, 'gray2'); PXL('props', wx + 2, 42, 'gray1')
# ─ 2段目(4枚) ─
frameM(146, 56, 18, 18)                              # 星空
for sx, sy in [(151,60),(158,63),(154,67),(160,60)]:
    PXL('props', sx, sy, 'wht')
PXL('props', 155, 62, 'gray2')
frameM(168, 54, 26, 20)                              # 渦巻き
EL('props', 172, 58, 189, 69, out='gray2')
EL('props', 176, 61, 185, 66, out='gray1')
frameM(198, 56, 20, 16)                              # 山なみ
for k in range(7):
    R('props', 201 + k, 66 - k, 1, k + 2, 'gray1')
    R('props', 212 - k // 2, 67 - k, 1, k + 2, 'gray0')
frameM(222, 54, 26, 18)                              # 夜の街
for bx, bh in [(225,7),(229,10),(234,6),(238,9),(242,5)]:
    R('props', bx, 69 - bh, 3, bh, 'gray0')
    PXL('props', bx + 1, 69 - bh + 2, 'wht')
# ─ 3段目(4枚) ─
frameM(150, 78, 20, 14)                              # りんご
EL('props', 156, 82, 162, 88, fill='gray2')
PXL('props', 159, 81, 'gray1')
frameM(174, 76, 24, 16)                              # ボトルの静物
R('props', 182, 80, 3, 9, 'gray2'); R('props', 183, 78, 1, 3, 'gray1')
R('props', 189, 82, 3, 7, 'gray1')
frameM(202, 78, 18, 14)                              # 市松の抽象
DI('props', 205, 81, 12, 8, 'gray1', 'n1')
frameM(224, 76, 24, 16)                              # 三日月と鳥
EL('props', 236, 79, 244, 87, fill='wht')
EL('props', 234, 78, 241, 85, fill='n1')
PXL('props', 229, 82, 'gray2'); PXL('props', 231, 81, 'gray2')

# ─── Patti the Spook の大きな額(ここだけ色をもつ=世界観の入口) ───
obj('Patti the Spookの額')
O('props', 256, 84, 64, 52, 'q3', 'ink')
R('props', 258, 86, 60, 1, 'q5'); R('props', 258, 133, 60, 1, 'q1')
O('props', 259, 87, 58, 46, 'y0', 'q1')
R('props', 261, 89, 54, 42, 'n0')
TXT('props', 262, 92, "PATTI", 'y2')                   # タイトルは上側
TXT('props', 283, 92, "THE", 'y2')
TXT('props', 296, 92, "SPOOK", 'y2')
EL('props', 296, 100, 312, 116, fill='b4')             # 大きな月
EL('props', 292, 97, 306, 111, fill='n0')              # 三日月に欠けさせる
for sx, sy in [(265,101),(271,97),(279,94),(268,112),(287,116),(308,94),(265,120)]:
    PXL('props', sx, sy, 'b5')
R('props', 261, 122, 54, 9, 'n1')                      # 丘
R('props', 261, 122, 54, 1, 'cool1')
R('props', 268, 104, 11, 11, 'wht')                    # 飛ぶパッチ
R('props', 267, 106, 1, 7, 'wht'); R('props', 279, 106, 1, 7, 'wht')
R('props', 269, 103, 9, 1, 'wht')
for ox9, oy9 in [(267,105),(266,108),(266,111),(280,105),(281,108),(281,111),(270,102),(276,102)]:
    PXL('props', ox9, oy9, 'n2')
PXL('props', 271, 108, 'ink'); PXL('props', 275, 108, 'ink')
R('props', 272, 111, 3, 1, 'ink')
R('props', 271, 113, 5, 2, 'y1')
PXL('props', 268, 115, 'wht'); PXL('props', 270, 116, 'wht')
PXL('props', 273, 115, 'wht'); PXL('props', 276, 116, 'wht'); PXL('props', 278, 115, 'wht')

# ─── 赤いポスト(お問い合わせ・日本の円柱ポスト) ───
obj('赤いポスト')
EL('props', 322, 116, 347, 132, fill='r1', out='ink')      # 丸屋根
R('props', 320, 128, 29, 3, 'r0')                          # つば
R('props', 320, 128, 29, 1, 'ink')
R('props', 323, 131, 24, 47, 'r1')                         # 円柱の胴体
R('props', 323, 131, 1, 47, 'ink'); R('props', 346, 131, 1, 47, 'ink')
R('props', 325, 132, 2, 45, 'r0')                          # 左の陰
R('props', 342, 132, 2, 45, 'r2')                          # 右の月光
R('props', 327, 135, 17, 9, 'cream')                       # 白票
R('props', 331, 136, 9, 1, 'r0')                           # 〒の赤(略式)
TXT('props', 329, 138, "POST", 'r0')
R('props', 326, 147, 18, 1, 'r0')                          # 胴のリング
R('props', 327, 151, 16, 4, 'ink')                         # 投函口
R('props', 327, 156, 16, 1, 'r0')
R('props', 326, 160, 18, 9, 'r0')                          # 取出口の扉
R('props', 327, 161, 16, 7, 'r1')
PXL('props', 341, 164, 'y1')                               # 鍵穴
R('props', 331, 171, 8, 1, 'cream')                        # 〒マーク
R('props', 331, 173, 8, 1, 'cream')
R('props', 334, 174, 2, 3, 'cream')
R('props', 324, 178, 22, 3, 'q2')                          # 首の台
O('props', 322, 181, 26, 5, 'gray1', 'ink')                # コンクリの土台
R('props', 320, 186, 30, 2, 'q0')                          # 接地影

obj()
# ホコリ(光のチリ)
for dx4, dy4, dc in [(263, 62, 'b4'), (275, 74, 'b4'), (319, 78, 'b4'),
                     (100, 30, 'o2'), (180, 27, 'o2'), (258, 29, 'o2'),
                     (132, 58, 'g2')]:
    PXL('props', dx4, dy4, dc)

# ═══ ジュークボックス(バブラー型・カウンターの手前) 42x74 @ (50,110) ═══
JX, JY = 50, 110

def _jb(x, y, w, h, c):
    R('furniture', JX + x, JY + y, w, h, c)

def draw_jukebox():
    EL('furniture', JX + 1, JY, JX + 40, JY + 36, fill='ivory', out='ink')
    _jb(1, 18, 40, 48, 'ivory')
    R('furniture', JX, JY + 18, 1, 48, 'ink'); R('furniture', JX + 41, JY + 18, 1, 48, 'ink')
    _jb(1, 65, 40, 1, 'ink')
    EL('furniture', JX + 8, JY + 4, JX + 33, JY + 34, fill='wood', out='ink')
    _jb(8, 18, 26, 44, 'wood')
    _jb(8, 18, 26, 1, 'wood2'); _jb(8, 40, 26, 1, 'wood2')
    _jb(10, 7, 22, 11, 'ink')
    _jb(11, 8, 20, 9, 'n0')
    EL('furniture', JX + 16, JY + 9, JX + 25, JY + 16, fill='q4', out='chrome2')
    EL('furniture', JX + 19, JY + 11, JX + 22, JY + 14, fill='y2')
    PXL('furniture', JX + 13, JY + 10, 'chrome')
    for tx in (3, 36):
        _jb(tx, 8, 3, 54, 'ivory')
        R('furniture', JX + tx, JY + 8, 1, 54, 'ivory2')
        for ty in (11, 26, 41, 54):
            _jb(tx, ty, 3, 4, 'tuber')
    for cy in (5, 28, 50):
        _jb(1, cy, 5, 5, 'chrome'); _jb(1, cy, 5, 1, 'wht')
        _jb(36, cy, 5, 5, 'chrome'); _jb(36, cy, 5, 1, 'wht')
    _jb(16, 0, 10, 4, 'chrome'); _jb(17, 0, 8, 1, 'wht')
    _jb(19, 1, 4, 2, 'tuber')
    _jb(9, 20, 24, 11, 'ink')
    _jb(10, 21, 22, 9, 'chrome2')
    for by in (23, 27):
        for bx in range(12, 32, 4):
            PXL('furniture', JX + bx, JY + by, 'tuber' if (bx // 4) % 2 else 'y2')
            PXL('furniture', JX + bx + 1, JY + by, 'ink')
    _jb(11, 25, 20, 1, 'ink')
    _jb(10, 33, 22, 20, 'ink')
    _jb(11, 34, 20, 18, 'q0')
    for gy in range(34, 52, 3):
        for gx in range(11, 31, 3):
            PXL('furniture', JX + gx + ((gy // 3) % 2), JY + gy, 'chrome2')
            PXL('furniture', JX + gx + 1 + ((gy // 3) % 2), JY + gy + 1, 'chrome2')
    for (sx, sy) in [(20,41),(21,40),(22,41),(21,42),(19,42),(23,42),(20,43),(22,43),(21,44)]:
        PXL('furniture', JX + sx, JY + sy, 'y1')
    PXL('furniture', JX + 21, JY + 41, 'y2')
    EL('furniture', JX + 17, JY + 38, JX + 25, JY + 46, out='chrome')
    _jb(5, 54, 32, 10, 'wood')
    _jb(5, 54, 32, 1, 'wood2')
    _jb(16, 57, 10, 4, 'chrome2')
    _jb(2, 64, 9, 9, 'ink'); _jb(31, 64, 9, 9, 'ink')
    _jb(3, 64, 7, 1, 'q2'); _jb(32, 64, 7, 1, 'q2')
    R('furniture', JX + 1, JY + 73, 40, 2, 'q0')

obj('ジュークボックス')
draw_jukebox()

# ═══════════════ mayu : 本物のMayu.asepriteをWebで重ねるため空 ═══════════════
obj()

# ═══════════════ ライティングの焼き込み ═══════════════
obj('ガーランド')
for bxg, byg in garland_positions():
    for hx, hy in [(-3, 5), (3, 5), (0, 1), (0, 9), (-2, 8), (2, 8), (-3, 3), (3, 3)]:
        PXL('garland', bxg + hx, byg + hy, 'bulbh')
    dpatch('bg', bxg - 4, byg + 10, 9, 5, 'wwarm', 2)
    dpatch('bg', bxg - 2, byg + 15, 5, 3, 'wwarm', 2, 1)

obj('COMPANYモニタ')
R('furniture', 150, 100, 92, 1, 'b1')
R('furniture', 150, 127, 92, 1, 'b0')
R('furniture', 150, 100, 1, 28, 'b0'); R('furniture', 241, 100, 1, 28, 'b0')
dpatch('bg', 136, 88, 10, 46, 'n4', 2)
dpatch('bg', 246, 88, 10, 46, 'n4', 2, 1)
dpatch('bg', 144, 90, 104, 8, 'n4', 2)
dpatch('furniture', 150, 139, 92, 4, 'n4', 2)

obj('楕円窓')
mcx, mcy = 311, 33
for yy in range(14, 60):
    for xx in range(284, 338):
        dxm, dym = xx - mcx, yy - mcy
        rr = math.sqrt(dxm * dxm + dym * dym)
        if abs(yy - WY) <= 2 or abs(xx - WX) <= 1:
            continue
        ex = ((xx - WX) / (WRX - 3)) ** 2 + ((yy - WY) / (WRY - 3)) ** 2
        if ex >= 1:
            continue
        if 13 <= rr < 16 and (xx + yy) % 2 == 0:
            PXL('window', xx, yy, 'b3')
        elif 16 <= rr < 20 and (xx + yy) % 3 == 0:
            PXL('window', xx, yy, 'b2')
dpatch('bg', 266, 76, 70, 8, 'n4', 2)
dpatch('props', 258, 85, 60, 1, 'cool2', 2)

obj('デザイン室の入口')
for yy in range(170, 210):
    reach = 30 + int((yy - 170) * 0.9)
    for xx in range(4, 4 + reach):
        if (xx * 2 + yy) % 5 == 0:
            PXL('bg', xx, yy, 'wwarm')
        if (xx * 2 + yy) % 9 == 0 and xx < 4 + reach // 2:
            PXL('bg', xx, yy, 'o0')

obj('編集室の入口')
for yy in range(170, 210):
    reach = 30 + int((yy - 170) * 0.9)
    for xx in range(W - 4 - reach, W - 4):
        if (xx * 2 + yy) % 5 == 0:
            PXL('bg', xx, yy, 'wneon')
        if (xx * 2 + yy) % 9 == 0 and xx > W - 4 - reach // 2:
            PXL('bg', xx, yy, 'cool1')

obj()
# カウンターの足元に床影
dpatch('bg', 49, 166, 286, 6, 'q0', 2)
# 月光の当たり(窓に近い上面へ青のディザ)
dpatch('props', 320, 128, 29, 1, 'cool2', 2)

# ═══════════════ light : (空レイヤー・自由記入用) ═══════════════

def _global_illum_pass():
    pass  # 実体は書き出し直前に移動(DARKER等の定義後に実行する必要がある)

_GI_MARKER = """
DARKER[P['cool2']] = P['cool1']; DARKER[P['cool1']] = P['q2']
DARKER[P['pnkc']] = P['pnk2']; DARKER[P['pnk2']] = P['pnk1']
DARKER[P['pnk1']] = P['q2']; DARKER[P['pnk0']] = P['q1']
DARKER[P['o2']] = P['o1']; DARKER[P['o1']] = P['o0']; DARKER[P['o0']] = P['brick']
DARKER[P['bulbc']] = P['o2']; DARKER[P['bulbh']] = P['y0']
DARKER[P['wwarm']] = P['n2']; DARKER[P['wneon']] = P['q1']; DARKER[P['spill']] = P['g0']
DARKER[P['wht']] = P['gray2']

SOURCES = [
    {'pos': (290, 44),  'r': 150, 's': 1.46, 'e': 1.4, 'tint': P['b3'],  'occ': True},   # 窓/月
    {'pos': (196, 113), 'r': 105, 's': 1.05, 'e': 1.4, 'tint': P['b4'],  'occ': True},   # COMPANYモニタ
    {'pos': (24, 118),  'r': 78,  's': 0.85, 'e': 1.3, 'tint': P['o2'],  'occ': False},  # デザイン室の灯り
    {'pos': (360, 118), 'r': 78,  's': 0.80, 'e': 1.3, 'tint': P['pnk2'], 'occ': False},  # 編集室の灯り(ピンク)
    {'pos': (192, 150), 'r': 185, 's': 0.34, 'e': 1.2, 'tint': P['q5'],  'occ': False},  # 室内バウンス
]
for _bx, _by in garland_positions():
    SOURCES.append({'pos': (_bx, _by + 5), 'r': 36, 's': 0.52, 'e': 1.5,
                    'tint': P['mauve'], 'occ': False})   # 紺壁に乗る暖色は紫寄りが自然
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
            continue            # 光源自身の筐体(画面の枠など)による自己遮蔽を防ぐ
        gx3 = int((sx3 + (cx3 - sx3) * t) / GS)
        gy3 = int((sy3 + (cy3 - sy3) * t) / GS)
        if 0 <= gx3 < gw and 0 <= gy3 < gh and solidg[gx3][gy3]:
            hits += 1
            if hits >= 3:
                return 0.22
    return 1.0 if hits == 0 else (0.72 if hits == 1 else 0.45)

ILL = [[AMB] * gh for _ in range(gw)]
TINT = [[(P['q5'], 0.0)] * gh for _ in range(gw)]
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
            # 発光体は暗くしない(窓の空・月 / TV画面 / モニタ画面 / ネオン文字)
            if layer == 'window':
                ex = ((xx - WX) / (WRX - 3)) ** 2 + ((yy - WY) / (WRY - 3)) ** 2
                if ex < 1:
                    continue
            if layer == 'furniture':
                if 150 <= xx <= 242 and 100 <= yy <= 128:
                    continue    # COMPANYの画面は自ら光る
                if 74 <= xx <= 98 and 84 <= yy <= 108:
                    continue    # 絵本の表紙はクリック対象なので目立たせる
                if 48 <= xx <= 94 and 108 <= yy <= 186:
                    continue    # ジュークボックスは光る箱
                if 10 <= xx <= 39 and 49 <= yy <= 215:
                    continue    # デザイン室の戸口の光
                if 345 <= xx <= 375 and 49 <= yy <= 215:
                    continue    # 編集室の戸口の光
                if (2 <= xx <= 83 and 28 <= yy <= 48) or (332 <= xx <= 382 and 28 <= yy <= 48):
                    continue    # 吊り看板は読ませる
            rgb = c[:3]
            v = ILL[xx // GS][yy // GS] + (((xx * 7 + yy * 13) % 5) - 2) * 0.02
            tint = TINT[xx // GS][yy // GS][0]
            chk = (xx + yy) % 2 == 0
            d1c = DARKER.get(rgb, rgb)
            d2c = DARKER.get(d1c, d1c)
            out = rgb
            WARM = (198, 88, 70)              # 灯りの赤み(sankouの温かさ)
            if layer == 'bg':
                # 壁・床のベース色はすでに「暗い部屋」。落とすのは遮蔽と隅だけ。
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

for lname in ['bg', 'window', 'furniture', 'props', 'mayu']:
    apply_illum(lname)

# 発光体まわりの再ブースト(COMPANYの文字とPOSTの票をくっきり戻す)
TXT2('furniture', 169, 106, "COMPANY", 'b4')
TXT('props', 329, 138, "POST", 'r0')

# 影ゾーンにある派手なプロップを沈める(視線ドロボー対策)
for (zx, zy, zw, zh, layn) in []:   # いまは沈める対象なし
    pxz = L[layn].load()
    for xx in range(zx, zx + zw):
        for yy in range(zy, zy + zh):
            c = pxz[xx, yy]
            if c[3] == 0 or c[:3] == INK:
                continue
            pxz[xx, yy] = DARKER.get(c[:3], c[:3]) + (255,)

# 画面の光だまり(COMPANYモニタが主役の光)
dpatch('furniture', 152, 139, 88, 4, 'n4', 2, 1)
dpatch('bg', 150, 166, 92, 6, 'n4', 3)
"""
# ↑ グローバル照明はコードを文字列として保持し、全パスの定義後(書き出し直前)にexecする

# ═══════════════ asset bake : 池本の実素材をはめ込む ═══════════════
ASSETS = os.path.abspath(os.path.join(WEB, "..", "..", "..", "サイト用画像"))

def bake_mono(path, layer, x0, y0, w, h, paper, mid, dark,
              crop_sq=False, t_dark=120, t_mid=195):
    """ペン画をドット化: 紙→paper、淡い線→mid、濃い線→dark"""
    src = Image.open(path).convert("L")
    if crop_sq:
        sw2, sh2 = src.size
        side = min(sw2, sh2)
        src = src.crop(((sw2 - side) // 2, (sh2 - side) // 2,
                        (sw2 + side) // 2, (sh2 + side) // 2))
    src = src.resize((w, h), Image.LANCZOS)
    pxs = src.load()
    for yy in range(h):
        for xx in range(w):
            v = pxs[xx, yy]
            c = dark if v < t_dark else (mid if v < t_mid else paper)
            PXL(layer, x0 + xx, y0 + yy, c)

def bake_color(path, layer, x0, y0, w, h):
    src = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    pxs = src.load()
    tgt = L[layer]
    for yy in range(h):
        for xx in range(w):
            tgt.putpixel((x0 + xx, y0 + yy), pxs[xx, yy] + (255,))

# ※実画像のベイクは縮小で判読不能になったため撤去(2026-08-09 池本判断)。
#   額縁・設計図・モニタは手描きドット版を使う。TVの動画だけWeb側で再生する。

# ═══════════════ こまごま第2弾 + 棚の微細陰影 ═══════════════
obj('ペン立て')
R('props', 264, 128, 8, 10, 'q2'); R('props', 264, 128, 8, 2, 'q4')
R('props', 266, 124, 1, 5, 'm2'); R('props', 268, 123, 1, 6, 'g1')
R('props', 270, 125, 1, 4, 'b3')
obj('壁かけの棚')
for py in (76, 108):
    dpatch('bg', 52, py + 4, 68, 3, 'q0', 2)          # 棚板の下の壁影

# ═══════════════ detail shading : プロップの多段陰影 ═══════════════
obj('COMPANYモニタ')
for k in range(10):
    if k % 2 == 0:
        PXL('furniture', 238 - k, 101 + k, 'n2')
obj('地球儀')
for xx, yy in [(97,129),(98,131),(99,132),(101,133),(103,133),(96,127),(105,132)]:
    PXL('furniture', xx, yy, 'b0')
obj('カウンター')
DI('furniture', 49, 144, 288, 2, 'q1', 'q0')

obj()
# ═══════════════ relight : プロップ単位の1px陰影と投影 ═══════════════
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
]
LIGHTER, DARKER = {}, {}
for chain in CHAINS:
    for a, b in zip(chain, chain[1:]):
        LIGHTER[P[a]] = P[b]
        DARKER[P[b]] = P[a]
INK = P['ink']
CRTC = (196, 113)    # COMPANYモニタの画面中心
# 月光(窓側)のリムは同系の明色ではなく「青みがかった明色」へ色相シフト
COOL = {}
for k in ['n0','n1','n2','q0','q1','q2','m0','r0','r1','b0','g0']:
    COOL[P[k]] = P['cool1']
for k in ['n3','n4','q3','q4','q5','m1','m2','brick','b1','b2','gray0']:
    COOL[P[k]] = P['cool2']

def relight(layer):
    im = L[layer]
    px = im.load()
    orig = [[px[xx, yy] for yy in range(H)] for xx in range(W)]

    def alpha(xx, yy):
        if not (0 <= xx < W and 0 <= yy < H):
            return 0
        return orig[xx][yy][3]

    def probe(xx, yy, dx, dy):
        """輪郭の外(透明)に出るならTrue、同プロップの別色に当たるならFalse"""
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
            if xx >= 246:                      # 月光ゾーン: 窓の右上から冷たい光
                litd = [(1, 0), (0, -1)]
                dkd = [(-1, 0), (0, 1)]
            else:
                dx, dy = xx - CRTC[0], yy - CRTC[1]
                if (dx * dx + dy * dy) ** .5 < 74 and layer != 'mayu':
                    litd = [((1 if dx < 0 else -1), 0), (0, (1 if dy < 0 else -1))]
                    dkd = [((-1 if dx < 0 else 1), 0)]
                else:                          # それ以外はガーランドの上面光
                    litd = [(0, -1)]
                    dkd = [(0, 1), (-1, 0)]
            if any(probe(xx, yy, dx2, dy2) for dx2, dy2 in litd):
                if xx >= 170 and rgb in COOL:
                    px[xx, yy] = COOL[rgb] + (255,)      # 月光 → 青みの明色
                elif rgb in LIGHTER:
                    px[xx, yy] = LIGHTER[rgb] + (255,)
            elif any(probe(xx, yy, dx2, dy2) for dx2, dy2 in dkd):
                if rgb in DARKER:
                    px[xx, yy] = DARKER[rgb] + (255,)

for lname in ['furniture', 'props', 'mayu']:
    relight(lname)

# ═══════ オブジェクト単位の面の陰影(見える側の面に光の設計を入れる) ═══════
def face_shade(layer):
    """連結成分=1つの物として、下部30%をディザで暗く、
    背の高い物は最下部を追加で暗く。上に机がある物は後段のゾーン減光も受ける。"""
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
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for nx2, ny2 in ((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
                    if 0 <= nx2 < W and 0 <= ny2 < H and not seen[nx2][ny2] \
                       and px[nx2, ny2][3] > 0:
                        seen[nx2][ny2] = True
                        stack.append((nx2, ny2))
            ys = [c[1] for c in comp]
            y0c, y1c = min(ys), max(ys)
            hc = y1c - y0c + 1
            if hc < 14:
                continue        # 小物はディザ陰影にするとノイズになるので除外
            band1 = y1c - max(2, int(hc * 0.30))
            band2 = y1c - max(1, int(hc * 0.10))
            for (cx, cy) in comp:
                c = px[cx, cy][:3]
                if c == INK:
                    continue
                if cy >= band2 and hc >= 26 and c in DARKER:
                    px[cx, cy] = DARKER[c] + (255,)
                elif cy >= band1 and (cx + cy) % 2 == 0 and c in DARKER:
                    px[cx, cy] = DARKER[c] + (255,)

face_shade('furniture')
face_shade('props')

# (旧・机の下ゾーン減光はグローバル照明+遮蔽に統合したため削除)

# 壁への落ち影(光=右上 → 影は左下へ、50%ディザ)
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

# ═══════════════ occlusion : 3D遮蔽AO ═══════════════
def darken_at(pmap, tx, ty, steps, dither=False):
    if dither and (tx + ty) % 2:
        return
    c = pmap[tx, ty][:3]
    for _ in range(steps):
        c = DARKER.get(c, c)
    pmap[tx, ty] = c + (255,)

# 上に物がある壁・床は、その物に光を遮られて暗い(棚下の影)
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

obj()
# 右に物がある壁は、窓の光を遮られて暗い(左向きのソフトシャドウ)
for yy in range(12, 142):
    nxt = None
    for xx in range(W - 1, -1, -1):
        if (xx, yy) in sil:
            nxt = xx
            continue
        if nxt is None:
            continue
        d = nxt - xx
        if d <= 3:
            darken_at(bgp, xx, yy, 1)
        elif d <= 7:
            darken_at(bgp, xx, yy, 1, dither=True)

# カウンター上の小物 → 天板への接地影
propsil = set()
ppx2 = L['props'].load()
for xx in range(W):
    for yy in range(H):
        if ppx2[xx, yy][3] > 0:
            propsil.add((xx, yy))
fpx = L['furniture'].load()
for xx in range(W):
    lastY = None
    for yy in range(12, H):
        if (xx, yy) in propsil:
            lastY = yy
            continue
        if lastY is None or fpx[xx, yy][3] == 0:
            continue
        d = yy - lastY
        if d <= 2:
            darken_at(fpx, xx, yy, 1)
        elif d <= 4:
            darken_at(fpx, xx, yy, 1, dither=True)

obj('ジュークボックス')
# ジュークボックスは本棚より手前。あとの描き込みで欠けないよう最後にもう一度描く
draw_jukebox()

obj()
# ═══════════════ global illumination 実行(全パスの最後) ═══════════════
exec(_GI_MARKER)

# ═══════════════ 手編集オーバーライド(池本のaseprite直接編集を最優先で残す) ═══════════════
OVRD = os.path.join(WEB, "overrides")
if os.path.isdir(OVRD):
    for n in names:
        # <名前>.full.png … room.aseprite で手直しした版。そのレイヤーを丸ごと置き換える。
        # 足すだけでなく「消した」も反映されるので、こちらを優先する。
        full = os.path.join(OVRD, f"{n}.full.png")
        if os.path.exists(full):
            ov = Image.open(full).convert("RGBA")
            if ov.size == (W, H):
                L[n] = ov
                D[n] = ImageDraw.Draw(L[n])
                print("手直しで差し替え:", n)
                continue
        opth = os.path.join(OVRD, f"{n}.png")
        if os.path.exists(opth):
            ov = Image.open(opth).convert("RGBA")
            if ov.size == (W, H):
                L[n].alpha_composite(ov)
                print("override applied:", n)

# 窓の桟オーバーレイ(おばけが桟の向こうを飛ぶためのWeb/GIF用パーツ)
bars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd2 = ImageDraw.Draw(bars)
bd2.rectangle([WX - 1, WY - WRY + 1, WX + 1, WY + WRY - 1], fill=C('q3'))
bd2.rectangle([WX - WRX + 1, WY - 1, WX + WRX - 1, WY + 1], fill=C('q3'))
bd2.rectangle([WX - 1, WY - WRY + 1, WX - 1, WY + WRY - 1], fill=C('q5'))
bd2.rectangle([WX - WRX + 1, WY - 1, WX + WRX - 1, WY - 1], fill=C('q5'))
bd2.ellipse([WX - WRX - 1, WY - WRY - 1, WX + WRX + 1, WY + WRY + 1], outline=C('q4'), width=2)
bd2.rectangle([332, 27, 383, 49], fill=(0, 0, 0, 0))   # 吊り看板(編集室)は窓枠より手前
bars.save(os.path.join(WEB, "window_bars.png"))
print("window_bars.png written")

# ═══════════════ 書き出し ═══════════════
flat = Image.new("RGBA", (W, H), (0, 0, 0, 255))
for n in names:
    L[n].save(os.path.join(LAY, f"{n}.png"))
    flat.alpha_composite(L[n])
flat.convert("RGB").save(os.path.join(WEB, "room.png"))
print("layers + room.png written")

# ── プロップ1個ずつのPNGへ切り分け(Aseprite のレイヤー分け用) ──────────
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
    # 所有マップを1回だけ走査して、プロップごとの白黒マスクを一気に作る
    # (I画像の point() は線形関数しか扱えないので使えない)
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
    rest = ImageChops.subtract(layer_alpha, taken)      # 誰のものでもない画素
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



# ガーランドのチラつきアニメ(3コマ) — コアの色が波打つ
GY0, GBH = 14, 26
gar = Image.new("RGBA", (W * 3, GBH), (0, 0, 0, 0))
gd = ImageDraw.Draw(gar)
CORE_CYCLE = ['o2', 'o1', 'o0']
for f in range(3):
    def put_px(x, y, c, _f=f):
        if 0 <= y - GY0 < GBH:
            gd.point((_f * W + x, y - GY0), fill=C(c))
    draw_garland(put_px, lambda i, _f=f: CORE_CYCLE[(i + _f) % 3])
    for i, (bx, by) in enumerate(garland_positions()):
        if (i + f) % 3 == 0:
            for hx, hy in [(-3, 5), (3, 5), (0, 1), (0, 9)]:
                put_px(bx + hx, by + hy, 'bulbh')
gar.save(os.path.join(WEB, "garland.png"))
print("garland.png", gar.size, "band y", GY0, "h", GBH)



# 地球儀の回転6コマ: 池本が塗った実物ピクセルを行ごとにロールさせる
_usrF = Image.open(os.path.join(WEB, "user_layers", "furniture.png")).convert("RGBA")
_gl = _usrF.crop((40, 76, 64, 104))
gs = Image.new("RGBA", (24 * 6, 28), (0, 0, 0, 0))
GCX, GCY, GR = 11.0, 13.0, 9.6                 # クロップ内の球の中心と半径
_ink3 = P['ink']
for f7 in range(6):
    fr7 = _gl.copy()
    fp7 = fr7.load()
    op7 = _gl.load()
    for yy in range(28):
        xs = [xx for xx in range(24)
              if ((xx - GCX) ** 2 + (yy - GCY) ** 2) <= (GR - 1.1) ** 2
              and op7[xx, yy][3] > 0 and op7[xx, yy][:3] != _ink3]
        if len(xs) < 3:
            continue
        vals = [op7[xx, yy] for xx in xs]
        sh7 = (f7 * len(xs)) // 6
        rolled = vals[sh7:] + vals[:sh7]
        for xx, vv in zip(xs, rolled):
            fp7[xx, yy] = vv
    gs.paste(fr7, (f7 * 24, 0))
# ジュークボックスの発光アニメ(4コマ・チューブと星がピカピカ)
JBW, JBH = 42, 74
jbg = Image.new("RGBA", (JBW * 4, JBH), (0, 0, 0, 0))
jd = ImageDraw.Draw(jbg)
CYC = [P['tuber'], (255, 150, 60), P['y1'], (255, 110, 170)]
STAR8 = [(20,41),(21,40),(22,41),(21,42),(19,42),(23,42),(20,43),(22,43),(21,44)]
for f8 in range(4):
    ox8 = f8 * JBW
    for i8, tx8 in enumerate((3, 36)):            # 左右のチューブが順に光る
        for k8, ty8 in enumerate((11, 26, 41, 54)):
            c8 = CYC[(f8 + k8 + i8) % 4]
            jd.rectangle([ox8 + tx8, ty8, ox8 + tx8 + 2, ty8 + 3], fill=c8 + (255,))
            jd.rectangle([ox8 + tx8, ty8 - 1, ox8 + tx8 + 2, ty8 - 1], fill=c8 + (110,))
            jd.rectangle([ox8 + tx8, ty8 + 4, ox8 + tx8 + 2, ty8 + 4], fill=c8 + (110,))
    jd.rectangle([ox8 + 11, 8, ox8 + 30, 16], fill=C('b3', 44 + f8 * 12))   # 表示窓の明滅
    st8 = CYC[f8 % 4]
    for (sx8, sy8) in STAR8:
        jd.point((ox8 + sx8, sy8), fill=st8 + (255,))
    jd.point((ox8 + 21, 41), fill=(255, 255, 255, 255))
    jd.ellipse([ox8 + 17, 38, ox8 + 25, 46], outline=st8 + (70,))
    for bx8 in range(12, 32, 4):                   # 選曲ボタンも点滅
        jd.point((ox8 + bx8, 23 if f8 % 2 else 27), fill=(255, 240, 200, 255))
jbg.save(os.path.join(WEB, "jukebox_glow.png"))

print("jukebox_glow.png written", jbg.size)
gs.save(os.path.join(WEB, "globe_spin.png"))
print("globe_spin.png written")
json.dump(["#%02X%02X%02X" % P[k] for k in P], open(os.path.join(LAY, "palette.json"), "w"))

_shaded = os.path.join(WEB, "patti_shaded.png")
sheet = Image.open(_shaded if os.path.exists(_shaded)
                   else os.path.join(WEB, "patti.png")).convert("RGBA")
prev = flat.copy()
pd2 = ImageDraw.Draw(prev)
pd2.ellipse([203, 179, 233, 185], fill=(64, 24, 108, 140))
prev.alpha_composite(sheet.crop((0, 0, 36, 48)), (200, 182 - 48))
prev.convert("RGB").resize((W * 2, H * 2), Image.NEAREST).save(SP + "room3_preview.png")
print("preview written")
