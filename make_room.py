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
for x in range(20, W, 48):                          # 赤い吊りタブ(sankou流)
    R('bg', x, 10, 5, 6, 'm1')
    R('bg', x, 10, 5, 1, 'm0')
    PXL('bg', x + 2, 13, 'm0')

R('bg', 0, 12, W, 20, 'n3')                          # 壁: 多段グラデーション
DI('bg', 0, 24, W, 4, 'n4', 'n3', 1)
DI('bg', 0, 32, W, 8, 'n3', 'n2')
R('bg', 0, 40, W, 56, 'n2')
DI('bg', 0, 96, W, 8, 'n2', 'n1')
R('bg', 0, 104, W, 38, 'n1')
DI('bg', 0, 132, W, 10, 'n1', 'n0')
DI('bg', 0, 12, 6, 130, 'n0', 'n1')                  # 四隅ビネット
DI('bg', 6, 12, 6, 130, 'n1', 'n2', 1)
DI('bg', W - 6, 12, 6, 130, 'n0', 'n1')
DI('bg', W - 12, 12, 6, 130, 'n1', 'n2', 1)
for x in [96, 192, 288]:
    R('bg', x, 12, 1, 130, 'n1')
for gx, gy in [(150, 100, ), (30, 60), (350, 120)][:0]:
    pass
R('bg', 0, 142, W, 4, 'ink')
R('bg', 0, 146, W, 2, 'q0')

R('bg', 0, 148, W, 92, 'q1')
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
for rx in range(136, 178, 7):
    R('bg', rx, 149, 1, 5 - (rx // 7) % 3, 'g0')
    R('bg', rx + 1, 149, 1, 2, 'g0')
for rx in range(300, 344, 8):
    R('bg', rx, 149, 1, 4 - (rx // 8) % 2, 'n4')
    PXL('bg', rx + 1, 149, 'n4')
# 床板ごとのトーン差と摩耗(1pxのこだわりゾーン)
for bi, (by0, by1) in enumerate([(149,161),(162,175),(176,189),(190,203),(204,217),(218,231)]):
    if bi % 2 == 0:
        for yy5 in range(by0 + 2, by1 - 2):
            for xx5 in range(0, W):
                if (xx5 + yy5 + bi) % 6 == 0:
                    PXL('bg', xx5, yy5, 'q2')
for wx5, wy5 in [(24,157),(88,171),(132,178),(210,166),(262,181),(322,158),(356,178),
                 (44,196),(150,186),(238,192),(302,188),(70,224),(180,232),(280,226),(330,234)]:
    PXL('bg', wx5, wy5, 'q0'); PXL('bg', wx5 + 1, wy5, 'q2')
for sx5 in range(8, W, 24):
    PXL('bg', sx5, 160, 'm1'); PXL('bg', sx5 + 12, 174, 'm0')
DI('bg', 0, 224, W, 6, 'q1', 'q0')
DI('bg', 0, 230, W, 10, 'q0', 'ink')

# ═══════════════ window : 楕円窓(上へ移動) ═══════════════
WX, WY, WRX, WRY = 312, 44, 42, 30
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
for sx, sy in [(284,30),(300,24),(330,20),(344,34),(292,44),(340,52),(300,60),(322,62),(286,56),(314,26)]:
    PXL('window', sx, sy, 'b5' if (sx+sy)%3 else 'wht')
PXL('window', 300, 23, 'b3'); PXL('window', 300, 25, 'b3'); PXL('window', 299, 24, 'b3'); PXL('window', 301, 24, 'b3')
# 月はBonbon(月のおばけ)がその位置に入るためアート削除。ハローは残す
for cx5, cy5, cw5 in [(286, 28, 16), (330, 52, 12)]:  # 夜雲のシルエット
    R('window', cx5, cy5, cw5, 3, 'n1')
    R('window', cx5 + 2, cy5 - 2, cw5 - 5, 2, 'n1')
    R('window', cx5 + 1, cy5 + 3, cw5 - 2, 1, 'b0')
# ※窓のおばけはSpeop.asepriteのアニメに置き換え(Web/GIFで窓の向こうを飛ぶ)
R('window', WX-1, WY-WRY+1, 3, 2*WRY-2, 'q3')
R('window', WX-WRX+1, WY-1, 2*WRX-2, 3, 'q3')
R('window', WX-1, WY-WRY+1, 1, 2*WRY-2, 'q5')
R('window', WX-WRX+1, WY-1, 2*WRX-2, 1, 'q5')
EL('window', WX-WRX-1, WY-WRY-1, WX+WRX+1, WY+WRY+1, out='q4', ow=2)
EL('window', WX-WRX-4, WY-WRY-4, WX+WRX+4, WY+WRY+4, out='ink', ow=2)
PXL('window', WX-WRX+7, WY-WRY+10, 'q5')

# ═══════════════ furniture ═══════════════
def counter(x, w):
    R('furniture', x, 106, w, 1, 'mauve')
    R('furniture', x, 107, w, 3, 'q4')
    R('furniture', x, 110, w, 2, 'q2')
    R('furniture', x, 112, w, 1, 'q0')
obj('カウンター')
counter(84, 212)
counter(300, 84)
for lx in [88, 180, 284, 304, 372]:
    R('furniture', lx, 112, 5, 34, 'q2')
    R('furniture', lx, 112, 1, 34, 'q4')
    R('furniture', lx + 4, 112, 1, 34, 'q0')
R('furniture', 92, 130, 88, 2, 'q2')
R('furniture', 92, 132, 88, 1, 'q0')

# 本棚
obj('本棚')
O('furniture', 6, 22, 66, 124, 'q0', 'ink')
R('furniture', 8, 24, 62, 2, 'q4')
for sy in [46, 74, 102, 130]:
    R('furniture', 9, sy, 60, 3, 'q3')
    R('furniture', 9, sy, 60, 1, 'q5')
R('furniture', 6, 22, 2, 124, 'q3'); R('furniture', 70, 22, 2, 124, 'q3')
C_shade = {'m2':'m0','cor':'brick','g2':'g0','b3':'b0','m1':'m0','cream':'cor2','b2':'b0','m3':'m1','g1':'g0','r2':'r0'}
def bookrow(y, specs):
    bx = 11
    for bw, bh, c in specs:
        R('furniture', bx, y - bh, bw, bh, c)
        R('furniture', bx, y - bh, bw, 2, 'ink')
        R('furniture', bx, y - bh, 1, bh, C_shade.get(c, 'ink'))
        PXL('furniture', bx + bw - 1, y - bh + 3, 'cream')
        bx += bw + 1
bookrow(45, [(4,17,'m2'),(5,15,'cor'),(4,18,'g2'),(5,16,'b3'),(4,14,'m1'),(5,17,'cream'),(4,15,'b2'),(5,18,'m3'),(4,13,'g1'),(5,16,'r2'),(4,17,'b3')])
bookrow(73, [(5,18,'b2'),(4,15,'m3'),(5,17,'cream'),(4,16,'g1'),(5,14,'cor'),(4,18,'m1'),(5,15,'b3'),(4,17,'r2'),(5,16,'g2'),(4,13,'m2')])
bookrow(129, [(5,16,'cor'),(4,18,'b3'),(5,14,'m2'),(4,17,'g2'),(5,15,'m1'),(4,16,'cream'),(5,18,'b2'),(4,14,'r2')])
obj('緑の図鑑')
R('furniture', 12, 88, 22, 14, 'ink')
R('furniture', 13, 89, 20, 12, 'g1')                   # 緑の図鑑
R('furniture', 13, 89, 20, 2, 'g2')
R('furniture', 14, 92, 18, 3, 'cream')                 # タイトル帯
R('furniture', 16, 93, 6, 1, 'g0'); R('furniture', 24, 93, 4, 1, 'g0')
PXL('furniture', 22, 98, 'y1'); PXL('furniture', 23, 99, 'y1')  # 菱形の箔
PXL('furniture', 22, 100, 'y1'); PXL('furniture', 21, 99, 'y1')
obj('地球儀')
EL('furniture', 42, 80, 60, 98, fill='b2', out='ink')     # 地球儀
for xx, yy, w2, h2 in [(45,84,6,4),(52,82,5,3),(48,90,7,4),(55,92,4,3)]:
    R('furniture', xx, yy, w2, h2, 'g1')
    PXL('furniture', xx, yy, 'g2')
R('furniture', 58, 78, 2, 4, 'y0')
R('furniture', 48, 98, 8, 3, 'q3')
R('furniture', 50, 101, 4, 1, 'ink')
PXL('furniture', 46, 83, 'b4'); PXL('furniture', 47, 84, 'b4')

# ブラウン管テレビ
obj('ブラウン管テレビ')
tvx, tvy = 122, 50
O('furniture', tvx, tvy, 66, 56, 'q3', 'ink')
R('furniture', tvx + 2, tvy + 2, 62, 2, 'q5')
R('furniture', tvx + 2, tvy + 52, 62, 2, 'q1')
O('furniture', tvx + 5, tvy + 7, 48, 40, 'n0', 'ink')
R('furniture', tvx + 7, tvy + 9, 44, 34, 'n0')
R('furniture', tvx + 55, tvy + 8, 8, 38, 'q1')
EL('furniture', tvx+56, tvy+10, tvx+61, tvy+15, fill='q5', out='ink')
EL('furniture', tvx+56, tvy+18, tvx+61, tvy+23, fill='q5', out='ink')
R('furniture', tvx + 56, tvy + 28, 6, 2, 'm2')
R('furniture', tvx + 56, tvy + 32, 6, 2, 'g1')
PXL('furniture', tvx + 57, tvy + 40, 'y1')
for i in range(4):
    R('furniture', tvx + 8 + i * 12, tvy + 50, 8, 1, 'q0')
R('furniture', tvx + 14, tvy - 12, 2, 12, 'gray1')
R('furniture', tvx + 40, tvy - 10, 2, 10, 'gray1')
R('furniture', tvx + 8, tvy - 14, 10, 3, 'gray1'); R('furniture', tvx + 8, tvy - 14, 10, 1, 'gray2')
R('furniture', tvx + 38, tvy - 12, 10, 3, 'gray1'); R('furniture', tvx + 38, tvy - 12, 10, 1, 'gray2')
R('furniture', tvx + 10, 106, 8, 2, 'ink'); R('furniture', tvx + 48, 106, 8, 2, 'ink')

# デスクトップPC(窓の下)
obj('PCモニタ')
mx, my = 300, 74
O('furniture', mx, my, 48, 28, 'n0', 'ink')
R('furniture', mx + 1, my + 1, 46, 1, 'q5')
R('furniture', mx + 3, my + 3, 42, 22, 'q1')          # シンセウェーブの空
DI('furniture', mx + 3, my + 8, 42, 3, 'q1', 'm0')
EL('furniture', mx + 17, my + 4, mx + 31, my + 16, fill='m3')  # ネオンの太陽
R('furniture', mx + 17, my + 9, 15, 1, 'q1'); R('furniture', mx + 17, my + 12, 15, 1, 'q1')
R('furniture', mx + 3, my + 12, 10, 2, 'ink'); R('furniture', mx + 34, my + 11, 11, 3, 'ink')  # 山影
R('furniture', mx + 3, my + 14, 42, 1, 'm2')          # 地平線ネオン
R('furniture', mx + 3, my + 15, 42, 10, 'n0')         # グリッドの床
for gy7 in (17, 20, 23):
    R('furniture', mx + 3, my + gy7, 42, 1, 'g1')
for gx7 in (10, 20, 28, 38):
    R('furniture', mx + gx7, my + 15, 1, 10, 'g0')
R('furniture', mx + 22, my + 15, 1, 10, 'm1')         # 中央グリッド
R('furniture', mx + 20, my + 16, 4, 5, 'wht')          # 走るミニパッチ
PXL('furniture', mx + 21, my + 17, 'ink')
R('furniture', mx + 21, my + 20, 2, 1, 'y1')
R('furniture', mx + 4, my + 4, 2, 2, 'm2'); R('furniture', mx + 7, my + 4, 2, 2, 'm2')  # HUD
R('furniture', mx + 38, my + 4, 4, 1, 'g2'); R('furniture', mx + 38, my + 6, 3, 1, 'g2')
PXL('furniture', mx + 12, my + 5, 'g2'); PXL('furniture', mx + 36, my + 8, 'b4')  # 星
PXL('furniture', mx + 42, my + 5, 'b5'); PXL('furniture', mx + 41, my + 6, 'b5')
R('furniture', mx + 20, my + 28, 8, 2, 'q2')
R('furniture', mx + 14, my + 30, 20, 2, 'q0')
obj('キーボード')
R('furniture', mx + 4, 102, 30, 4, 'q2')
for kx in range(mx + 5, mx + 32, 3): PXL('furniture', kx, 103, 'q4')
obj('PCタワー')
R('furniture', 351, 102, 1, 10, 'ink')               # モニタ→タワーのケーブル
O('furniture', 340, 112, 22, 34, 'q1', 'ink')        # PCタワー
R('furniture', 342, 114, 18, 1, 'q4')
PXL('furniture', 344, 118, 'g2'); PXL('furniture', 344, 121, 'm2')
R('furniture', 343, 126, 16, 2, 'q0')
R('furniture', 343, 130, 16, 2, 'q0')
R('furniture', 350, 138, 6, 1, 'b3')

# カウンター下(左)
obj('赤い収納ケース')
O('furniture', 96, 124, 26, 22, 'r1', 'ink')
R('furniture', 98, 126, 22, 2, 'r2')
R('furniture', 104, 132, 10, 3, 'q0')
obj('紫の収納ケース')
O('furniture', 126, 128, 30, 18, 'q2', 'ink')
R('furniture', 128, 130, 26, 1, 'q4')
R('furniture', 136, 136, 10, 2, 'mauve')
obj('グレーの収納箱')
R('furniture', 162, 138, 20, 8, 'gray1')
R('furniture', 162, 138, 20, 2, 'gray2')
R('furniture', 168, 140, 8, 3, 'ink')
obj('カウンター下の小箱')
R('furniture', 186, 140, 8, 6, 'cor'); R('furniture', 186, 140, 8, 2, 'cor2')
R('furniture', 196, 142, 8, 4, 'g1')
# カウンター下(中央) 段ボール・スピーカー・ゴミ箱
obj('段ボール箱')
O('furniture', 208, 124, 26, 22, 'y0', 'ink')
R('furniture', 210, 126, 22, 2, 'y2')
R('furniture', 214, 124, 6, 4, 'cor2'); R('furniture', 222, 124, 6, 4, 'cor2')
EL('furniture', 216, 132, 226, 140, out='ink')
PXL('furniture', 219, 135, 'ink'); PXL('furniture', 223, 135, 'ink')
obj('スピーカー')
O('furniture', 240, 118, 26, 28, 'q2', 'ink')
EL('furniture', 245, 122, 261, 138, fill='q0', out='q4')
EL('furniture', 249, 126, 257, 134, fill='g0')
PXL('furniture', 252, 129, 'g1')
obj('ゴミ箱')
R('furniture', 270, 128, 12, 18, 'gray1')
R('furniture', 270, 128, 12, 2, 'gray2')
R('furniture', 272, 124, 3, 4, 'cream'); R('furniture', 277, 125, 3, 3, 'gray2')

# ═══════════════ props ═══════════════
GAR_SPANS = [(6, 196, 12, 9, 7), (196, 378, 12, 9, 7)]
def garland_positions():
    out = []
    for x0, x1, y0, sag, nb in GAR_SPANS:
        for i in range(nb):
            t = (i + 0.5) / nb
            out.append((int(x0 + t * (x1 - x0)),
                        y0 + int(sag * (1 - (2 * t - 1) ** 2))))
    return out

def draw_garland(layer_draw_px, core_of, off=(0, 0)):
    """wire + オレンジ電球。core_of(i)でコアの色を変える(チラつきアニメ用)"""
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

obj('スタジオ看板')
O('props', 84, 26, 44, 24, 'q0', 'ink')              # STUDIO PATTI サイン
R('props', 86, 28, 40, 1, 'q2')
TXT('props', 89, 31, "STUDIO", 'm3')
TXT('props', 93, 39, "PATTI", 'cor')
R('props', 89, 46, 34, 1, 'm0')

obj('キャラクター設計図')
bx0, by0 = 196, 24                                   # ブループリント
O('props', bx0, by0, 72, 52, 'b0', 'ink')
R('props', bx0 + 1, by0 + 1, 70, 1, 'q5')
for gx2 in range(bx0 + 4, bx0 + 70, 8):
    for gy2 in range(by0 + 4, by0 + 50, 8):
        PXL('props', gx2, gy2, 'b1')
# キャラクターの3面図(正面・側面・背面)。文字なし、図面の記法だけで語る
V_Y = by0 + 12                                                 # 各ビューの頭の上端
def bp_view(vx, kind):
    O('props', vx, V_Y, 14, 11, 'b0', 'cream')                 # 頭
    R('props', vx + 6, V_Y - 3, 2, 3, 'cream')                 # アンテナ
    PXL('props', vx + 6, V_Y - 4, 'y1')
    O('props', vx - 1, V_Y + 13, 16, 13, 'b0', 'cream')        # 胴体
    R('props', vx + 1, V_Y + 27, 4, 4, 'cream')                # 脚
    R('props', vx + 9, V_Y + 27, 4, 4, 'cream')
    if kind == 'front':
        O('props', vx + 2, V_Y + 3, 4, 4, 'b0', 'cream')       # 両目
        O('props', vx + 8, V_Y + 3, 4, 4, 'b0', 'cream')
        R('props', vx + 4, V_Y + 8, 6, 1, 'cream')             # 口
        O('props', vx + 3, V_Y + 16, 8, 6, 'b0', 'b3')         # 胸パネル
    elif kind == 'side':
        O('props', vx + 8, V_Y + 3, 4, 4, 'b0', 'cream')       # 片目(横顔)
        R('props', vx - 1, V_Y + 16, 4, 8, 'b3')               # 背中のユニット
        R('props', vx + 6, V_Y + 15, 2, 8, 'cream')            # 腕のライン
    else:                                                       # back
        R('props', vx + 2, V_Y + 3, 10, 1, 'b3')               # 後頭部の継ぎ目
        R('props', vx + 3, V_Y + 16, 8, 1, 'b3')               # 背面パネル
        R('props', vx + 3, V_Y + 20, 8, 1, 'b3')
bp_view(bx0 + 8, 'front')
bp_view(bx0 + 30, 'side')
bp_view(bx0 + 52, 'back')
for gx6 in range(bx0 + 4, bx0 + 68, 3):                        # 投影線(頭頂・あご・足元)
    PXL('props', gx6, V_Y - 1, 'b1')
    PXL('props', gx6 + 1, V_Y + 12, 'b1')
    PXL('props', gx6, V_Y + 31, 'b1')
for vx6 in (bx0 + 15, bx0 + 37, bx0 + 59):                     # 各ビューの中心線(一点鎖線)
    for dy6 in range(V_Y - 6, V_Y + 36, 4):
        PXL('props', vx6, dy6, 'b3')
R('props', bx0 + 6, V_Y + 36, 26, 1, 'b3')                     # 寸法線(正面ビュー下)
PXL('props', bx0 + 6, V_Y + 35, 'b3'); PXL('props', bx0 + 6, V_Y + 37, 'b3')
PXL('props', bx0 + 31, V_Y + 35, 'b3'); PXL('props', bx0 + 31, V_Y + 37, 'b3')
R('props', bx0 + 66, V_Y, 1, 31, 'b3')                         # 高さの寸法線(右端)
PXL('props', bx0 + 65, V_Y, 'b3'); PXL('props', bx0 + 67, V_Y, 'b3')
PXL('props', bx0 + 65, V_Y + 30, 'b3'); PXL('props', bx0 + 67, V_Y + 30, 'b3')

def frame(x, y, w, h, matc, edge='q4'):
    O('props', x, y, w, h, matc, 'ink')
    R('props', x + 1, y + 1, w - 2, 1, edge)
# ギャラリー: 大きな額縁(右の空きスペースまで広げる)と、その中央に来る傘ライト
obj('傘ライト')
R('props', 97, 56, 2, 2, 'q4')                        # ライトのアーム
R('props', 90, 52, 16, 4, 'q3')                       # 傘シェード
R('props', 91, 51, 14, 1, 'mauve')
R('props', 91, 55, 14, 1, 'y0')                       # 内側(未点灯の金)
obj('額縁(ギャラリー)')
frame(76, 58, 44, 24, 'cream')                        # 額縁(44x24)
R('props', 78, 60, 40, 20, 'ink')                     # 落とし込み
R('props', 79, 61, 38, 18, 'n1')                      # 夜空
for sx0, sy0 in [(83,64),(91,63),(104,65),(112,68),(86,72),(99,74),(110,62),(95,69)]:
    PXL('props', sx0, sy0, 'b5')
EL('props', 105, 63, 112, 70, fill='b4')              # 月
EL('props', 103, 62, 109, 68, fill='n1')
R('props', 88, 66, 7, 7, 'wht')                       # 飛ぶパッチ
R('props', 87, 67, 1, 4, 'wht'); R('props', 95, 67, 1, 4, 'wht')
PXL('props', 90, 68, 'ink'); PXL('props', 93, 68, 'ink')
R('props', 89, 71, 5, 1, 'y1')                        # 蝶ネクタイ
PXL('props', 88, 74, 'wht'); PXL('props', 91, 75, 'wht'); PXL('props', 94, 74, 'wht')
for tx0 in range(80, 116, 4):                          # 額の内側の面取り
    PXL('props', tx0, 59, 'mauve')
# (ミント額はTVと被るため撤去。ギャラリー入口はクリーム額に一本化)
obj('額縁(抽象画)')
frame(148, 14, 22, 18, 'q4')
R('props', 150, 18, 8, 10, 'wht')
R('props', 160, 16, 7, 12, 'brick')
R('props', 161, 21, 5, 6, 'm2')
obj('額縁(青)')
frame(174, 18, 16, 14, 'b3')
DI('props', 176, 20, 12, 10, 'b2', 'b0')

obj('デジタル時計')
O('props', 356, 26, 26, 14, 'n0', 'ink')                 # デジタル時計(表示はWeb側)
R('props', 357, 27, 24, 1, 'q4')
R('props', 358, 28, 22, 10, 'n0')
PXL('props', 368, 31, 'g0'); PXL('props', 368, 34, 'g0')   # 消灯時のコロン

obj('カレンダー')
O('props', 268, 82, 18, 22, 'cream', 'ink')           # カレンダー 8.8
R('props', 270, 84, 14, 5, 'm2')
TXT('props', 273, 92, "8.8", 'ink')
R('props', 274, 80, 2, 3, 'gray1')

obj('コルクボード')
O('props', 84, 84, 44, 20, 'y0', 'ink')               # コルクボード
R('props', 86, 86, 40, 1, 'y2')
for nx, ny, c in [(88,88,'cream'),(100,89,'g2'),(112,87,'m3'),(94,95,'b4'),(107,96,'cor')]:
    R('props', nx, ny, 9, 7, c)
    PXL('props', nx + 4, ny - 1, 'r2')

# (ペナントはTVと被るため撤去)

# フィギュア棚(ブループリント下)
obj('フィギュア棚')
R('props', 232, 90, 34, 3, 'q4'); R('props', 232, 90, 34, 1, 'mauve')
R('props', 234, 93, 2, 3, 'q1'); R('props', 262, 93, 2, 3, 'q1')
EL('props', 234, 78, 242, 89, fill='wht', out='ink')
PXL('props', 236, 82, 'ink'); PXL('props', 239, 82, 'ink')
R('props', 236, 86, 4, 2, 'y1')
R('props', 246, 80, 8, 4, 'brick'); PXL('props', 250, 78, 'brick')
R('props', 247, 84, 6, 3, 'cream'); R('props', 247, 87, 6, 3, 'm2')
EL('props', 257, 80, 264, 88, fill='g2', out='g0')
PXL('props', 259, 83, 'ink'); PXL('props', 262, 83, 'ink')

obj('カメラ')
cx2, cy2 = 208, 92                                    # 一眼カメラ
O('props', cx2, cy2, 24, 14, 'q0', 'ink')
R('props', cx2 + 2, cy2 + 1, 20, 2, 'q2')
R('props', cx2 + 6, cy2 - 3, 8, 4, 'q0')
EL('props', cx2 + 8, cy2 + 3, cx2 + 17, cy2 + 12, fill='q2', out='ink')
EL('props', cx2 + 10, cy2 + 5, cx2 + 15, cy2 + 10, fill='b1')
PXL('props', cx2 + 11, cy2 + 6, 'b4')
PXL('props', cx2 + 20, cy2 + 2, 'm2')
R('props', cx2 - 3, cy2 + 3, 3, 1, 'q3'); R('props', cx2 + 24, cy2 + 3, 3, 1, 'q3')

obj('マグカップ')
R('props', 196, 98, 8, 8, 'g1'); R('props', 197, 97, 6, 2, 'g2')   # マグ
R('props', 204, 100, 2, 3, 'g1')
obj('ラジオ')
R('props', 240, 96, 14, 10, 'q2'); R('props', 241, 95, 12, 2, 'q4')  # ラジオ
PXL('props', 243, 99, 'y1'); R('props', 246, 99, 5, 3, 'n0')
obj('小さな本')
R('props', 258, 100, 10, 6, 'cor'); R('props', 258, 100, 10, 2, 'cor2')  # 本
obj('観葉植物')
R('props', 90, 96, 12, 10, 'm1'); R('props', 90, 96, 12, 3, 'm2')   # 植物
for dx, dy, hh in [(2,-7,8),(5,-11,12),(8,-6,7),(0,-4,5),(10,-3,4)]:
    R('props', 90 + dx, 96 + dy, 2, hh, 'g0')
    R('props', 90 + dx - 1, 96 + dy - 2, 4, 3, 'g1')
    PXL('props', 90 + dx, 96 + dy - 2, 'g2')

obj('換気口')
R('props', 8, 16, 10, 6, 'gray0'); R('props', 9, 17, 8, 4, 'ink')   # 換気口
R('props', 9, 18, 8, 1, 'gray0'); R('props', 9, 20, 8, 1, 'gray0')
obj('レコード')
EL('props', 356, 84, 370, 98, fill='m0', out='ink')                 # レコード
EL('props', 360, 88, 366, 94, fill='q0')
PXL('props', 358, 87, 'm3')
obj('ポスター筒')
R('props', 366, 128, 12, 26, 'q2'); R('props', 366, 128, 12, 2, 'q4')  # ポスター筒
R('props', 368, 132, 2, 18, 'm2'); R('props', 372, 132, 2, 18, 'g1')
obj('電気スイッチ')
R('props', 76, 96, 5, 7, 'gray2'); R('props', 77, 98, 3, 3, 'ink')  # スイッチ
# 小さな換気口と床の点はジュークボックスの定位置と重なるので廃止
obj()
for xx in range(58, 118, 2): PXL('props', xx, 156 + (xx // 2) % 2, 'ink')  # ジュークボックスの右端から

def bookstack(x, y):                                  # 絵本の山
    for i, (w2, c, c2) in enumerate([(26,'b2','b3'),(24,'cor','cor2'),(28,'m2','m3'),(22,'g1','g2')]):
        yy = y - i * 5
        R('props', x + (28 - w2)//2, yy, w2, 5, c)
        R('props', x + (28 - w2)//2, yy, w2, 1, c2)
        R('props', x + (28 - w2)//2, yy, 2, 5, 'ink')
# (本の山はジュークボックスの場所と重なるため撤去。前景に十分ある)
obj('青い星の本')
O('props', 44, 196, 18, 24, 'b2', 'ink')               # 青い星の本(前景へ移動)
R('props', 45, 197, 16, 3, 'b4')
R('props', 47, 202, 12, 2, 'cream')
PXL('props', 52, 209, 'y1'); PXL('props', 51, 210, 'y1'); PXL('props', 53, 210, 'y1')
PXL('props', 52, 211, 'y1'); PXL('props', 50, 211, 'y1'); PXL('props', 54, 211, 'y1')
PXL('props', 52, 212, 'y1')
R('props', 48, 215, 10, 1, 'b0')
R('props', 43, 219, 20, 2, 'q0')

def rug(x, y, w, h):
    O('props', x, y, w, h, 'r1', 'r0')
    R('props', x + 3, y + 3, w - 6, h - 6, 'm0')
    R('props', x + 6, y + 6, w - 12, h - 12, 'r1')
    for i in range(6):
        R('props', x + 10 + i * (w - 20) // 5, y + h // 2 - 1, 4, 2, 'm2')
    for fx2 in range(x + 2, x + w - 2, 3):
        PXL('props', fx2, y - 1, 'mauve'); PXL('props', fx2, y + h, 'mauve')
obj('ラグ')
rug(122, 148, 140, 24)

# ═══ 前景ゾーン(y208〜): 転がる絵本たち + 絵本『おばけのパッチ』表紙 ═══
def flatbook(x, y, w, c, ct):
    R('props', x, y, w, 7, 'ink')
    R('props', x + 1, y + 1, w - 2, 5, c)
    R('props', x + 1, y + 1, w - 2, 1, ct)
    R('props', x + 2, y + 5, w - 4, 1, 'cream')      # ページの小口
obj('転がる絵本')
flatbook(42, 226, 32, 'm2', 'm3')
flatbook(46, 219, 28, 'b2', 'b3')
flatbook(104, 227, 22, 'g1', 'g2')
obj('開いた絵本')
R('props', 12, 218, 26, 11, 'ink')                    # 開いた絵本
R('props', 13, 219, 11, 9, 'cream')
R('props', 25, 219, 12, 9, 'cream')
R('props', 24, 218, 1, 11, 'q3')
for ly in (221, 223, 225):
    R('props', 15, ly, 7, 1, 'gray1')
    R('props', 27, ly, 8, 1, 'gray1')
R('props', 15, 227, 5, 1, 'cor')                      # 挿絵のつもりの色チップ
# 『おばけのパッチ』表紙(実物の装丁を再現: 白地に大きな円、円の中にパッチの後ろ姿)
# 床に開いて置かれた絵本(ホバーで「この本自体」がパラパラめくれる)
# frame0 を部屋に焼き、同じ絵の6コマを bookflip.png に書き出して完全に重ねる
def draw_openbook(px_fn, ox, oy, frame):
    """36x22。床に寝かせたパース付きの開き本。frame0=静止"""
    TOPL, TOPR, TY = 9, 27, 6                   # 上辺(奥・狭い)
    BOTL, BOTR, BY = 1, 34, 19                  # 下辺(手前・広い)
    for r8 in range(TY, BY + 1):
        t8 = (r8 - TY) / (BY - TY)
        lx8 = round(TOPL + (BOTL - TOPL) * t8)
        rx8 = round(TOPR + (BOTR - TOPR) * t8)
        for xx in range(lx8, rx8 + 1):
            if r8 in (TY, BY) or xx in (lx8, rx8):
                px_fn(ox + xx, oy + r8, 'ink')          # 輪郭
            elif 17 <= xx <= 18:
                px_fn(ox + xx, oy + r8, 'q3')           # のど
            else:
                px_fn(ox + xx, oy + r8, 'cream')
    for xx in range(2, 34):
        px_fn(ox + xx, oy + BY + 1, 'ink')              # 本の厚み
    for xx in range(3, 33):
        px_fn(ox + xx, oy + BY + 2, 'q0')               # 接地影
    for (xx, yy) in [(8,10),(9,9),(10,9),(11,10),(7,11),(12,11),(8,13),(11,13),(9,14),(10,14)]:
        px_fn(ox + xx, oy + yy, 'ink')                  # 左: パッチの挿絵
    px_fn(ox + 9, oy + 11, 'ink'); px_fn(ox + 11, oy + 11, 'ink')
    for ly8, lw8 in ((9, 7), (12, 8), (15, 9)):
        for xx in range(21, 21 + lw8):
            px_fn(ox + xx, oy + ly8, 'gray1')           # 右: 文章の線
    if frame > 0:
        # めくれるページは「手前(下)ののど」を軸に、右から左へ弧を描いて起き上がる
        tips = {1: (31, 12), 2: (28, 3), 3: (17, 0), 4: (6, 3), 5: (3, 12)}
        tipx, tipy = tips[frame]
        x0_, y0_ = 18, BY - 1
        steps8 = max(abs(tipx - x0_), abs(tipy - y0_), 1)
        pts8 = []
        for k8 in range(steps8 + 1):
            t9 = k8 / steps8
            xx = round(x0_ + (tipx - x0_) * t9)
            yy = round(y0_ + (tipy - y0_) * t9 - 2.6 * (t9 - t9 * t9) * 4)  # 反り
            pts8.append((xx, yy))
        for (xx, yy) in pts8:                         # ページの面(厚みをもって見せる)
            px_fn(ox + xx, oy + yy, 'ink')
            px_fn(ox + xx, oy + yy + 1, 'wht')
            px_fn(ox + xx, oy + yy + 2, 'cream')
        px_fn(ox + tipx, oy + tipy, 'ink')

# ═══ ジュークボックス(バブラー型・左下) 42x74 @ (14,104) ═══
JX, JY = 14, 104
P['chrome'] = (206, 208, 222); P['chrome2'] = (150, 152, 172)
P['ivory'] = (247, 238, 216); P['ivory2'] = (206, 194, 172)
P['wood'] = (126, 78, 46); P['wood2'] = (92, 54, 32)
P['tuber'] = (214, 46, 62)

def _jb(x, y, w, h, c):
    R('furniture', JX + x, JY + y, w, h, c)

def draw_jukebox():
    # 本体シルエット(アーチ天面+胴体) 42x74
    EL('furniture', JX + 1, JY, JX + 40, JY + 36, fill='ivory', out='ink')
    _jb(1, 18, 40, 48, 'ivory')
    R('furniture', JX, JY + 18, 1, 48, 'ink'); R('furniture', JX + 41, JY + 18, 1, 48, 'ink')
    _jb(1, 65, 40, 1, 'ink')
    # 中央の木目パネル(アーチの内側)
    EL('furniture', JX + 8, JY + 4, JX + 33, JY + 34, fill='wood', out='ink')
    _jb(8, 18, 26, 44, 'wood')
    _jb(8, 18, 26, 1, 'wood2'); _jb(8, 40, 26, 1, 'wood2')
    # 上部の表示窓(レコードが見える)
    _jb(10, 7, 22, 11, 'ink')
    _jb(11, 8, 20, 9, 'n0')
    EL('furniture', JX + 16, JY + 9, JX + 25, JY + 16, fill='q4', out='chrome2')
    EL('furniture', JX + 19, JY + 11, JX + 22, JY + 14, fill='y2')
    PXL('furniture', JX + 13, JY + 10, 'chrome')
    # 左右のカラーチューブ(バブラー管)
    for tx in (3, 36):
        _jb(tx, 8, 3, 54, 'ivory')
        R('furniture', JX + tx, JY + 8, 1, 54, 'ivory2')
        for ty in (11, 26, 41, 54):
            _jb(tx, ty, 3, 4, 'tuber')
    # クロームの飾り金具(上・中・下)
    for cy in (5, 28, 50):
        _jb(1, cy, 5, 5, 'chrome'); _jb(1, cy, 5, 1, 'wht')
        _jb(36, cy, 5, 5, 'chrome'); _jb(36, cy, 5, 1, 'wht')
    _jb(16, 0, 10, 4, 'chrome'); _jb(17, 0, 8, 1, 'wht')
    _jb(19, 1, 4, 2, 'tuber')
    # 選曲パネル(ボタン格子)
    _jb(9, 20, 24, 11, 'ink')
    _jb(10, 21, 22, 9, 'chrome2')
    for by in (23, 27):
        for bx in range(12, 32, 4):
            PXL('furniture', JX + bx, JY + by, 'tuber' if (bx // 4) % 2 else 'y2')
            PXL('furniture', JX + bx + 1, JY + by, 'ink')
    _jb(11, 25, 20, 1, 'ink')
    # グリル(菱形の網)
    _jb(10, 33, 22, 20, 'ink')
    _jb(11, 34, 20, 18, 'q0')
    for gy in range(34, 52, 3):
        for gx in range(11, 31, 3):
            PXL('furniture', JX + gx + ((gy // 3) % 2), JY + gy, 'chrome2')
            PXL('furniture', JX + gx + 1 + ((gy // 3) % 2), JY + gy + 1, 'chrome2')
    # 中央の星のエンブレム
    for (sx, sy) in [(20,41),(21,40),(22,41),(21,42),(19,42),(23,42),(20,43),(22,43),(21,44)]:
        PXL('furniture', JX + sx, JY + sy, 'y1')
    PXL('furniture', JX + 21, JY + 41, 'y2')
    EL('furniture', JX + 17, JY + 38, JX + 25, JY + 46, out='chrome')
    # 下部キャビネットと脚
    _jb(5, 54, 32, 10, 'wood')
    _jb(5, 54, 32, 1, 'wood2')
    _jb(16, 57, 10, 4, 'chrome2')
    _jb(2, 64, 9, 9, 'ink'); _jb(31, 64, 9, 9, 'ink')
    _jb(3, 64, 7, 1, 'q2'); _jb(32, 64, 7, 1, 'q2')
    R('furniture', JX + 1, JY + 73, 40, 2, 'q0')

obj('ジュークボックス')
draw_jukebox()

def _room_px(xx, yy, c):
    PXL('props', xx, yy, c)
obj('おばけのパッチの絵本')
draw_openbook(_room_px, 136, 148, 0)                    # 床(ラグの上)に開いて置く
patti_cover = None                                      # 旧カバーは廃止
obj()
for sx4, sy4, sw4 in [(42, 233, 32), (12, 229, 26), (104, 234, 22)]:
    R('props', sx4, sy4, sw4, 2, 'q0')                # 接地影

# 光の中のホコリ(チリ)と暗闇で光る星シール
for dx4, dy4, dc in [(285, 62, 'b4'), (297, 74, 'b4'), (341, 80, 'b4'),
                     (58, 30, 'o2'), (162, 27, 'o2'), (252, 29, 'o2'),
                     (146, 46, 'g2'), (176, 100, 'g2')]:
    PXL('props', dx4, dy4, dc)
for dx4, dy4 in [(150, 132), (168, 128), (186, 133)]:
    PXL('props', dx4, dy4, 'g1')                      # 蓄光星シール(カウンター下)
obj('クッション')
R('props', 356, 170, 26, 12, 'b1')                    # クッション
R('props', 356, 170, 26, 3, 'b2')
R('props', 356, 180, 26, 2, 'b0')
PXL('props', 368, 175, 'b3')

# ═══════════════ mayu : 本物のMayu.asepriteが完成したのでレイヤーは空のまま残す ═══════════════
DRAW_MAYU_PLACEHOLDER = False
mxx, myy = 72, 156
obj()
EL('mayu', mxx + 1, myy, mxx + 31, myy + 24, fill='brick', out='ink')   # マッシュルームボブ
R('mayu', mxx + 5, myy + 2, 22, 3, 'r2')
R('mayu', mxx + 11, myy + 1, 9, 1, 'cor2')
R('mayu', mxx + 3, myy + 22, 28, 4, 'brick')
R('mayu', mxx + 3, myy + 25, 28, 1, 'r0')
PXL('mayu', mxx + 15, myy - 3, 'brick'); PXL('mayu', mxx + 16, myy - 2, 'brick')
PXL('mayu', mxx + 17, myy - 4, 'brick'); PXL('mayu', mxx + 18, myy - 3, 'brick')
R('mayu', mxx + 9, myy + 12, 14, 10, 'cream')                            # 顔
R('mayu', mxx + 8, myy + 14, 1, 6, 'cream'); R('mayu', mxx + 23, myy + 14, 1, 6, 'cream')
R('mayu', mxx + 11, myy + 15, 1, 3, 'ink'); R('mayu', mxx + 12, myy + 17, 1, 1, 'ink')  # 伏し目(左)
R('mayu', mxx + 20, myy + 15, 1, 3, 'ink'); R('mayu', mxx + 19, myy + 17, 1, 1, 'ink')  # 伏し目(右)
PXL('mayu', mxx + 9, myy + 19, 'm3'); PXL('mayu', mxx + 22, myy + 19, 'm3')
R('mayu', mxx + 15, myy + 20, 2, 1, 'm2')                                # 口
R('mayu', mxx + 7, myy + 26, 18, 12, 'm2')                               # ワンピース
R('mayu', mxx + 7, myy + 26, 18, 2, 'm3')
R('mayu', mxx + 7, myy + 35, 18, 3, 'm0')
R('mayu', mxx + 9, myy + 27, 2, 2, 'cream')                              # 襟
R('mayu', mxx + 21, myy + 27, 2, 2, 'cream')
R('mayu', mxx + 1, myy + 33, 10, 7, 'm2')                                # あぐらの膝
R('mayu', mxx + 21, myy + 33, 10, 7, 'm2')
R('mayu', mxx + 1, myy + 33, 10, 2, 'm3'); R('mayu', mxx + 21, myy + 33, 10, 2, 'm3')
R('mayu', mxx + 2, myy + 39, 8, 3, 'cream')                              # 足
R('mayu', mxx + 22, myy + 39, 8, 3, 'cream')
R('mayu', mxx + 4, myy + 41, 6, 2, 'brick'); R('mayu', mxx + 22, myy + 41, 6, 2, 'brick')
R('mayu', mxx + 5, myy + 28, 10, 8, 'cream')                             # 絵本(開き)
R('mayu', mxx + 17, myy + 28, 10, 8, 'cream')
R('mayu', mxx + 15, myy + 27, 2, 10, 'q3')
R('mayu', mxx + 6, myy + 30, 7, 1, 'gray1'); R('mayu', mxx + 6, myy + 32, 6, 1, 'gray1')
R('mayu', mxx + 19, myy + 30, 7, 1, 'gray1'); R('mayu', mxx + 19, myy + 32, 6, 1, 'gray1')
R('mayu', mxx + 3, myy + 29, 3, 5, 'cream')                              # 手
R('mayu', mxx + 26, myy + 29, 3, 5, 'cream')
D['mayu'].ellipse([mxx + 1, myy + 42, mxx + 31, myy + 48], fill=C('q0', 190))
D['mayu'].ellipse([mxx + 5, myy + 43, mxx + 27, myy + 47], fill=C('ink', 120))
if not DRAW_MAYU_PLACEHOLDER:
    L['mayu'] = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    D['mayu'] = ImageDraw.Draw(L['mayu'])

obj()
# ═══════════════ post : ライティングを焼き込む(批評反映) ═══════════════
P['wwarm'] = (52, 48, 88)     # 電球の暖色が当たる壁(紺に馴染む暖紫)
P['wneon'] = (42, 36, 80)     # ネオンのマゼンタが当たる壁
P['spill'] = (62, 122, 106)   # ブラウン管の緑がこぼれる机
P['bulbc'] = (255, 246, 200)  # 電球コア
P['bulbh'] = (176, 138, 74)   # 電球ハロー

def dpatch(l, x, y, w, h, c, den=2, ph=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx + yy + ph) % den == 0:
                PXL(l, xx, yy, c)

obj('ガーランド')
# 1) ガーランド: オレンジ統一。ハローと壁の暖色だまり(コアのチラつきはWeb/GIF側)
for bxg, byg in garland_positions():
    for hx, hy in [(-3, 5), (3, 5), (0, 1), (0, 9), (-2, 8), (2, 8), (-3, 3), (3, 3)]:
        PXL('garland', bxg + hx, byg + hy, 'bulbh')
    dpatch('bg', bxg - 4, byg + 10, 9, 5, 'wwarm', 2)
    dpatch('bg', bxg - 2, byg + 15, 5, 3, 'wwarm', 2, 1)

obj('ブラウン管テレビ')
# 2) ブラウン管: 画面のフチ + 壁の明るみ + 机への緑スピル + 隣接物のリム
R('furniture', tvx + 6, tvy + 8, 46, 1, 'g1')
R('furniture', tvx + 6, tvy + 45, 46, 1, 'g0')
R('furniture', tvx + 6, tvy + 8, 1, 38, 'g0'); R('furniture', tvx + 51, tvy + 8, 1, 38, 'g0')
dpatch('bg', 108, 46, 14, 62, 'n4', 2)
dpatch('bg', 188, 46, 14, 62, 'n4', 2, 1)
dpatch('bg', 118, 38, 74, 12, 'n4', 2)
dpatch('furniture', tvx + 8, 107, 46, 5, 'spill', 2)
PXL('props', 100, 82, 'g2'); PXL('props', 96, 87, 'g2'); PXL('props', 102, 89, 'g2')
R('props', cx2 + 2, cy2, 6, 1, 'g2')
R('props', 197, 97, 3, 1, 'g3')

obj('ネオンサイン')
# 3) ネオンサイン: 明るいコア + 壁のマゼンタ
TXT('props', 90, 32, "STUDIO", 'm0')
TXT('props', 89, 31, "STUDIO", 'm4')
TXT('props', 94, 40, "PATTI", 'm0')
TXT('props', 93, 39, "PATTI", 'cor2')
R('props', 89, 46, 34, 1, 'm2')
dpatch('bg', 80, 20, 52, 6, 'wneon', 2)
dpatch('bg', 78, 26, 6, 26, 'wneon', 2, 1)
dpatch('bg', 128, 26, 6, 26, 'wneon', 2)
dpatch('bg', 80, 50, 52, 6, 'wneon', 2, 1)

obj('楕円窓')
# 4) 窓: 月のハロー + 壁の冷たいスピル + 下の物への青リム
mcx, mcy = 333, 33
for yy in range(14, 60):
    for xx in range(306, 360):
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
dpatch('bg', 288, 76, 74, 16, 'n4', 2)
R('furniture', mx + 1, my, 46, 1, 'b4')
PXL('props', 360, 84, 'b4'); PXL('props', 364, 83, 'b4')

obj()
# 5) 接地影(床の物すべて)
# (本の山の影も撤去)
# (面出し本の影は移動先で描画)
R('props', 354, 182, 30, 2, 'q0')

# 6) 天井から吊るす(占有と重なり)
obj('おばけの風鈴')
R('props', 29, 10, 1, 4, 'ink')                       # おばけの風鈴(本棚上に重なる)
EL('props', 25, 14, 34, 23, fill='wht', out='ink')
R('props', 25, 19, 10, 3, 'wht')
PXL('props', 26, 22, 'wht'); PXL('props', 29, 22, 'wht'); PXL('props', 32, 22, 'wht')
PXL('props', 28, 17, 'ink'); PXL('props', 31, 17, 'ink')
obj('星のモビール')
R('props', 362, 10, 1, 5, 'ink')                      # 星のモビール(窓のリングに重なる)
R('props', 359, 15, 7, 7, 'y1'); PXL('props', 362, 13, 'y1')
PXL('props', 360, 17, 'y2'); PXL('props', 358, 18, 'y1'); PXL('props', 366, 18, 'y1')

# 7) 右下の固まり(空白つぶし+画面端の見切れ)
obj('木箱')
O('props', 326, 166, 30, 22, 'y0', 'ink')             # 木箱(タワー下端に重なる)
R('props', 328, 168, 26, 2, 'y2')
R('props', 330, 174, 8, 2, 'q0'); R('props', 342, 174, 8, 2, 'q0')
O('props', 332, 154, 18, 12, 'cor', 'ink')
R('props', 334, 156, 14, 2, 'cor2')
obj('赤いポスト')
# 赤いポスト(問い合わせ入口・クリック対象)
EL('props', 295, 134, 320, 152, fill='r1', out='ink')
R('props', 296, 144, 24, 30, 'r1')
R('props', 296, 144, 1, 30, 'ink'); R('props', 319, 144, 1, 30, 'ink')
R('props', 298, 145, 2, 26, 'r0')                     # 左の陰
R('props', 315, 145, 2, 26, 'r2')                     # 右の月光側
R('props', 294, 140, 28, 3, 'r0')                     # 笠
R('props', 294, 140, 28, 1, 'ink')
R('props', 300, 148, 16, 4, 'ink')                    # 投函口
R('props', 300, 153, 16, 1, 'r0')
R('props', 304, 159, 8, 1, 'cream')                   # 〒マーク
R('props', 304, 162, 8, 1, 'cream')
R('props', 307, 163, 2, 4, 'cream')
O('props', 297, 174, 22, 6, 'q2', 'ink')              # 台座
R('props', 295, 178, 26, 2, 'q0')                     # 接地影
obj('サボテン')
R('props', 284, 168, 9, 9, 'm1'); R('props', 284, 168, 9, 2, 'm2')   # サボテン
R('props', 287, 162, 3, 6, 'g1'); PXL('props', 286, 164, 'g1'); PXL('props', 290, 163, 'g1')
PXL('props', 288, 161, 'g2')
obj('コントローラー')
R('props', 358, 167, 12, 6, 'gray1')                  # クッションの上のコントローラー
R('props', 358, 167, 12, 2, 'gray2')
PXL('props', 361, 170, 'm2'); PXL('props', 366, 170, 'g1')
obj('木箱')
R('props', 326, 186, 32, 2, 'q0')                     # 接地影
obj('実験メモ')
# 実験メモ(CHARA CHARA LABへの扉・クリック対象) ※TVと被らない壁の空きへ
O('props', 288, 84, 15, 20, 'q3', 'ink')
R('props', 290, 86, 11, 16, 'cream')
R('props', 290, 86, 11, 2, 'm2')                      # 表題バー
R('props', 291, 90, 8, 1, 'g1'); R('props', 291, 93, 9, 1, 'g1')
R('props', 291, 96, 7, 1, 'g1')
R('props', 292, 99, 3, 2, 'g2'); PXL('props', 296, 100, 'g1')   # フラスコ落書き
PXL('props', 295, 83, 'r2'); PXL('props', 295, 82, 'r2')        # ピン

# 8) 机下の重なり(孤島解消)
obj('ボール')
EL('props', 118, 134, 128, 144, fill='m2', out='ink') # 赤箱に寄りかかるボール
PXL('props', 121, 137, 'm4')
obj('ケーブル束')
EL('props', 232, 134, 246, 144, fill=None, out='q4')  # スピーカー前のケーブル束
EL('props', 235, 137, 243, 141, fill=None, out='q4')
obj('雑誌')
for i2 in range(3):                                   # 段ボールに立てかけた雑誌
    R('props', 200 + i2 * 2, 130 - i2, 3, 16, ['b3', 'cream', 'm3'][i2])
    R('props', 200 + i2 * 2, 130 - i2, 3, 2, 'ink')

# 9,10) 旧ブループリント補正とペナントは撤去(v13で描き直し済み)

obj()
# 11) 床の平面を明確に(家具の足元に影)
dpatch('bg', 84, 160, 216, 10, 'q0', 2)
dpatch('bg', 300, 160, 84, 8, 'q0', 2, 1)

obj()
# ═══════ 月光の当たり(窓に近い面へ青のディザ) ═══════
dpatch('furniture', 300, 106, 84, 2, 'b3', 3)         # 右カウンター天板(モニタの青と同源)
dpatch('furniture', tvx + 38, tvy + 1, 26, 2, 'cool2', 3, 1)   # テレビ天面の右側
dpatch('furniture', 340, 118, 22, 2, 'cool2', 3)      # PCタワー上面
dpatch('props', 326, 176, 30, 2, 'cool2', 3, 1)       # 右下の木箱の上面

# ═══════════════ light : (空レイヤー・自由記入用) ═══════════════

def _global_illum_pass():
    pass  # 実体は書き出し直前に移動(DARKER等の定義後に実行する必要がある)

_GI_MARKER = """
DARKER[P['cool2']] = P['cool1']; DARKER[P['cool1']] = P['q2']
DARKER[P['o2']] = P['o1']; DARKER[P['o1']] = P['o0']; DARKER[P['o0']] = P['brick']
DARKER[P['bulbc']] = P['o2']; DARKER[P['bulbh']] = P['y0']
DARKER[P['wwarm']] = P['n2']; DARKER[P['wneon']] = P['q1']; DARKER[P['spill']] = P['g0']
DARKER[P['wht']] = P['gray2']

SOURCES = [
    {'pos': (312, 44),  'r': 150, 's': 1.46, 'e': 1.4, 'tint': P['b3'],  'occ': True},   # 窓/月
    {'pos': (151, 76),  'r': 115, 's': 1.34, 'e': 1.4, 'tint': P['g2'],  'occ': True},   # ブラウン管
    {'pos': (324, 88),  'r': 62,  's': 0.62, 'e': 1.5, 'tint': P['b3'],  'occ': True},   # モニタ
    {'pos': (112, 38),  'r': 64,  's': 0.85, 'e': 1.5, 'tint': P['m3'],  'occ': True},   # ネオン
    {'pos': (190, 150), 'r': 185, 's': 0.34, 'e': 1.2, 'tint': P['q5'],  'occ': False},  # 室内バウンス
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
                if tvx + 5 <= xx <= tvx + 53 and tvy + 7 <= yy <= tvy + 47:
                    continue
                if mx + 2 <= xx <= mx + 46 and my + 2 <= yy <= my + 27:
                    continue
            if layer == 'props' and 88 <= xx <= 126 and 30 <= yy <= 46:
                continue
            if layer == 'props' and 197 <= xx <= 267 and 25 <= yy <= 75:
                continue    # キャラ設計図の中身は見せ場なので基準明度を守る
            if layer == 'furniture' and 12 <= xx <= 58 and 102 <= yy <= 180:
                continue    # ジュークボックスは光る箱なので基準明度を守る
            if layer == 'props' and 134 <= xx <= 172 and 146 <= yy <= 172:
                continue    # 絵本『おばけのパッチ』表紙はクリック対象なので目立たせる
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

# 発光体まわりの再ブースト(ネオン文字のコアを白熱させる)
TXT('props', 89, 31, "STUDIO", 'm4')
TXT('props', 93, 39, "PATTI", 'cor2')
for xx, yy in [(91, 33), (95, 31), (103, 33), (107, 31), (115, 33), (119, 31),
               (97, 41), (101, 39), (109, 41), (113, 39)]:
    PXL('props', xx, yy, 'wht')
R('props', 89, 46, 34, 1, 'm3')

# 影ゾーンにある派手なプロップを沈める(視線ドロボー対策)
for (zx, zy, zw, zh, layn) in [(208, 124, 28, 22, 'furniture'),
                               (198, 126, 10, 21, 'props'),
                               (330, 152, 22, 16, 'props'),
                               (330, 162, 22, 16, 'props')]:   # 右下クレートは2段沈める
    pxz = L[layn].load()
    for xx in range(zx, zx + zw):
        for yy in range(zy, zy + zh):
            c = pxz[xx, yy]
            if c[3] == 0 or c[:3] == INK:
                continue
            pxz[xx, yy] = DARKER.get(c[:3], c[:3]) + (255,)

# 画面の光だまりを机とカウンターに(ブラウン管とモニタは主役の光)
dpatch('furniture', 120, 107, 62, 6, 'spill', 2)
dpatch('bg', 118, 113, 66, 8, 'spill', 3)
dpatch('bg', 112, 113, 6, 8, 'spill', 4)              # プールの縁は密度を下げて減衰
dpatch('bg', 184, 113, 6, 8, 'spill', 4, 1)
dpatch('bg', 118, 121, 66, 3, 'spill', 4)
dpatch('furniture', 300, 107, 50, 6, 'n4', 2, 1)
dpatch('bg', 296, 66, 8, 34, 'n4', 3)
dpatch('bg', 350, 66, 10, 34, 'n4', 3, 1)
"""
# ↑ グローバル照明はコードを文字列として保持し、全パスの定義後(書き出し直前)にexecする

# ═══════════════ asset bake : 池本の実素材をはめ込む ═══════════════
ASSETS = os.path.abspath(os.path.join(WEB, "..", "..", "サイト用画像"))

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

# ═══════════════ こまごま第2弾 + 棚と床の微細陰影 ═══════════════
obj('ペン立て')
R('props', 186, 96, 8, 10, 'q2'); R('props', 186, 96, 8, 2, 'q4')     # ペン立て
R('props', 188, 92, 1, 5, 'm2'); R('props', 190, 91, 1, 6, 'g1')
R('props', 192, 93, 1, 4, 'b3')
obj('サイコロ')
R('props', 240, 100, 4, 4, 'wht'); PXL('props', 241, 101, 'ink')      # サイコロ
R('props', 245, 101, 3, 3, 'gray2'); PXL('props', 246, 102, 'ink')
obj('壁の付箋')
R('props', 190, 64, 5, 5, 'y2'); PXL('props', 191, 66, 'q3')          # 壁の付箋たち
R('props', 190, 71, 5, 4, 'm3')
R('props', 191, 77, 4, 4, 'g2')
obj('テープ')
EL('props', 272, 99, 279, 106, fill='gray1', out='ink')               # テープ
PXL('props', 275, 102, 'q0')
obj('鍵フック')
R('props', 74, 80, 1, 3, 'gray1')                                     # 鍵フック
PXL('props', 73, 84, 'y1'); PXL('props', 74, 85, 'y1'); PXL('props', 75, 84, 'y1')
obj('床の紙きれ')
R('props', 300, 222, 10, 6, 'cream')                                   # 床の紙きれ
R('props', 302, 224, 6, 1, 'gray1'); R('props', 302, 226, 5, 1, 'gray1')
R('props', 308, 225, 10, 6, 'gray2'); R('props', 310, 227, 6, 1, 'gray0')
obj('えんぴつ')
R('props', 340, 228, 7, 2, 'y1'); PXL('props', 347, 228, 'ink')          # えんぴつ
PXL('props', 339, 229, 'cor')
R('furniture', 62, 62, 2, 11, 'q4'); R('furniture', 62, 71, 5, 2, 'q4')  # ブックエンド
obj('鉢植え')
R('props', 26, 15, 7, 7, 'brick')                                     # 本棚の上の鉢植え
PXL('props', 28, 12, 'g1'); PXL('props', 30, 11, 'g2'); PXL('props', 31, 13, 'g1')
PXL('props', 27, 13, 'g0'); PXL('props', 29, 14, 'g1')
obj('カセットテープ')
R('props', 112, 232, 9, 6, 'q2'); R('props', 113, 233, 7, 2, 'm2')    # 床のカセット
obj('モニタ縁の付箋')
R('furniture', 300, 80, 3, 4, 'y2'); R('furniture', 300, 86, 3, 3, 'g2')  # モニタ縁の付箋
obj('ミニパッチ人形')
EL('props', 345, 96, 351, 105, fill='wht', out='ink')                 # ミニパッチ人形(右机)
PXL('props', 347, 99, 'ink'); PXL('props', 349, 99, 'ink')
R('props', 347, 102, 3, 1, 'y1')
obj('本棚')
# 本棚: 棚ごとの暗部と木目
for sy5 in [46, 74, 102, 130]:
    R('furniture', 9, sy5 + 3, 60, 1, 'ink')
    dpatch('furniture', 10, sy5 - 26, 58, 3, 'ink', 3)
for gy5 in range(26, 144, 5):
    PXL('furniture', 7, gy5, 'q1'); PXL('furniture', 71, (gy5 + 2) if gy5 + 2 < 146 else 144, 'q1')

# ═══════════════ detail shading : プロップの多段陰影 ═══════════════
obj('ブラウン管テレビ')
# ブラウン管を背景から立たせる(上端リム+右端光+背後の暗がり)
R('furniture', tvx + 1, tvy + 1, 64, 1, 'mauve')
R('furniture', tvx + 62, tvy + 3, 2, 50, 'q5')
R('furniture', tvx + 6, tvy + 8, 46, 1, 'g2')
obj()
dpatch('bg', 112, 30, 10, 78, 'n0', 2)
dpatch('bg', 188, 30, 8, 78, 'n0', 2, 1)
dpatch('bg', 118, 28, 72, 8, 'n0', 2)
obj('ブラウン管テレビ')
# ブラウン管: 筐体の丸みをディザで
DI('furniture', tvx + 3, tvy + 8, 3, 42, 'q2', 'q3')
DI('furniture', tvx + 60, tvy + 6, 3, 44, 'q4', 'q3', 1)
DI('furniture', tvx + 4, tvy + 44, 50, 4, 'q2', 'q3')
obj()
# 箱もの: 三面(上=明・前=中・横=暗)
DI('furniture', 98, 138, 22, 6, 'r1', 'r0')
R('furniture', 97, 126, 1, 19, 'r0')
DI('furniture', 128, 140, 26, 4, 'q2', 'q1')
R('furniture', 127, 130, 1, 15, 'q1')
obj('段ボール箱')
DI('furniture', 210, 138, 22, 6, 'y0', 'brick')
R('furniture', 209, 126, 1, 19, 'brick')
obj('スピーカー')
DI('furniture', 242, 138, 22, 6, 'q2', 'q1', 1)
obj('本棚')
# 本棚: 棚板の下の奥を暗く(3D遮蔽の手描き分)
for sy in [46, 74, 102, 130]:
    DI('furniture', 9, sy + 3, 60, 3, 'q0', 'ink')
DI('furniture', 8, 24, 3, 132, 'q0', 'q1')
obj('PCモニタ')
# モニタ: ガラスの斜めツヤ
for k in range(12):
    if k % 2 == 0:
        PXL('furniture', mx + 38 - k, my + 4 + k, 'b4')
    if k % 3 == 0:
        PXL('furniture', mx + 33 - k, my + 4 + k, 'b3')
obj('地球儀')
# 地球儀: 下側の回り込み陰
for xx, yy in [(45,92),(46,94),(47,95),(49,96),(51,96),(44,90),(53,95)]:
    PXL('furniture', xx, yy, 'b0')
obj('PCタワー')
# PCタワー: 前面下部
DI('furniture', 342, 138, 18, 7, 'q1', 'q0')
obj()
# ラグ: 内側の落ち影
DI('props', 126, 202, 132, 3, 'r0', 'm0')
obj('木箱')
# 木箱(右下)三面
R('props', 327, 167, 1, 20, 'y0')
DI('props', 328, 183, 26, 4, 'y0', 'brick', 1)

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
CRTC = (151, 76)     # ブラウン管の画面中心
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
            if xx >= 170:                      # 月光ゾーン(拡大): 右上から冷たい光
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

FWt, FHt = 44, 34
tv = Image.new("RGBA", (FWt * 2, FHt), (0, 0, 0, 0))
td3 = ImageDraw.Draw(tv)
for i in range(2):
    ox = i * FWt
    td3.rectangle([ox, 0, ox + FWt - 1, FHt - 1], fill=C('n0'))
    td3.rectangle([ox + 2, 2, ox + FWt - 3, FHt - 3], fill=C('g1'))     # 白熱した画面
    td3.rectangle([ox + 2, 2, ox + FWt - 3, 12], fill=C('g2'))
    py2 = 10 + (2 if i else 0)
    td3.ellipse([ox + 16, py2, ox + 27, py2 + 13], fill=C('wht'))
    td3.point((ox + 20, py2 + 5), fill=C('ink')); td3.point((ox + 23, py2 + 5), fill=C('ink'))
    td3.rectangle([ox + 20, py2 + 9, ox + 23, py2 + 10], fill=C('y1'))
    td3.rectangle([ox + 4, FHt - 8, ox + FWt - 5, FHt - 6], fill=C('g3'))
    for y3 in range(2, FHt - 2, 3):
        td3.line([(ox + 2, y3), (ox + FWt - 3, y3)], fill=C('g0', 120))
    td3.point((ox + FWt - 7, 4), fill=C('g3'))
    td3.rectangle([ox + 30, 16, ox + 39, 22], fill=C('g3'))             # 明るいUI窓
tv.save(os.path.join(WEB, "tv.png"))
print("tv.png", tv.size)

# ガーランドのチラつきアニメ(3コマ) — コアの色が波打つ
GY0, GBH = 10, 26
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

# 絵本ホバー用: 部屋に置いた開き本と同一絵の6コマ(34x26)
bf = Image.new("RGBA", (36 * 6, 22), (0, 0, 0, 0))
bfd_px = bf.load()
for f6 in range(6):
    def _strip_px(xx, yy, c, _o=f6 * 36):
        if 0 <= yy - 148 < 22:
            bfd_px[_o + (xx - 136), yy - 148] = C(c)
    draw_openbook(_strip_px, 136, 148, f6)
bf.save(os.path.join(WEB, "bookflip.png"))

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
print("bookflip.png / globe_spin.png written")
json.dump(["#%02X%02X%02X" % P[k] for k in P], open(os.path.join(LAY, "palette.json"), "w"))

_shaded = os.path.join(WEB, "patti_shaded.png")
sheet = Image.open(_shaded if os.path.exists(_shaded)
                   else os.path.join(WEB, "patti.png")).convert("RGBA")
prev = flat.copy()
prev.alpha_composite(tv.crop((0, 0, FWt, FHt)), (129, 59))
pd2 = ImageDraw.Draw(prev)
pd2.ellipse([213, 185, 243, 191], fill=(64, 24, 108, 140))
prev.alpha_composite(sheet.crop((0, 0, 36, 48)), (210, 190 - 48))
prev.convert("RGB").resize((W * 2, H * 2), Image.NEAREST).save(SP + "room3_preview.png")
print("preview written")
