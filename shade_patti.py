# patti.png(書き出し直後のスプライトシート)に陰影を乗せて patti_shaded.png を作る。
# 原本の Patti.aseprite には一切触らない。build.bat から自動で呼ばれる。
# 光源設定: 右上(窓)からの光 → 左と下に影、輪郭の内側1〜2pxをラベンダーで落とす。
from PIL import Image
import os, json

d = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(d, "patti.png")).convert("RGBA")
px = im.load()
Wp, Hp = im.size
FW = 36                                  # 1コマの幅

WHITE = (255, 255, 255, 255)
# 部屋は暗いので、真っ白のままだと光源より目立ってしまう。
# 環境光(夜の部屋)に馴染むトーンへ全体を落とす。
AMB_BODY = (213, 217, 236, 255)          # 白 → 夜のクールホワイト
S1 = (172, 164, 205, 255)                # 影1段目(ラベンダー)
S2 = (194, 192, 222, 255)                # 影2段目(淡)
BOW = (252, 200, 0, 255)
BOWN = (228, 182, 22, 255)               # 蝶ネクタイも半段落とす
BOWD = (188, 144, 8, 255)                # 蝶ネクタイの影

orig = [[px[x, y] for y in range(Hp)] for x in range(Wp)]

def cell(x, y, fi):
    if not (0 <= x < Wp and 0 <= y < Hp) or x // FW != fi:
        return (0, 0, 0, 0)
    return orig[x][y]

def probe(x, y, dx, dy, fi):
    """輪郭の外(透明)に抜けたらTrue。白に当たったら内部ディテールなのでFalse。"""
    for k in range(1, 4):
        c = cell(x + dx * k, y + dy * k, fi)
        if c[3] == 0:
            return True
        if c == WHITE or c == BOW:
            return False
    return False

band1 = set()
for x in range(Wp):
    fi = x // FW
    for y in range(Hp):
        c = orig[x][y]
        if c == WHITE:
            if probe(x, y, 0, 1, fi) or probe(x, y, -1, 1, fi) or probe(x, y, -1, 0, fi):
                band1.add((x, y))
        elif c == BOW:
            if probe(x, y, 0, 1, fi) or probe(x, y, -1, 0, fi):
                px[x, y] = BOWD

band2 = set()
for (x, y) in band1:
    fi = x // FW
    for dx, dy in [(0, -1), (1, 0), (1, -1)]:
        t = (x + dx, y + dy)
        if t not in band1 and cell(t[0], t[1], fi) == WHITE:
            band2.add(t)

for x in range(Wp):
    for y in range(Hp):
        if orig[x][y] == WHITE and (x, y) not in band1 and (x, y) not in band2:
            px[x, y] = AMB_BODY
        elif orig[x][y] == BOW and px[x, y] == BOW:
            px[x, y] = BOWN
for (x, y) in band1:
    px[x, y] = S1
for (x, y) in band2:
    px[x, y] = S2

im.save(os.path.join(d, "patti_shaded.png"))
print("patti_shaded.png written", im.size)

