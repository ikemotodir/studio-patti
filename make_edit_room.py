# -*- coding: utf-8 -*-
"""アニメーション制作「編集室」ページの素材を書き出す。

・edit_room.png   … 部屋の背景(384x240)。キャラクターは一切描かない(レイヤー分離)
・edit_glow.png   … 編集機のボタンがキラキラ点滅する4コマ(背景の上に重ねる)
・mayu_stand.png  … 立ち姿のマユちゃん(仮)。40x72 x 4コマ(idle/瞬き)
・edit_room.json  … HTML側が使う矩形(モニタ画面・メニューパネル・編集機など)

パッチくんは既存の patti_shaded.png(本物)をそのまま使うのでここでは作らない。
"""
from PIL import Image, ImageDraw
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 384, 240

P = {
 'ink':  (4, 2, 26),
 'n0': (0, 1, 43),  'n1': (0, 1, 57),  'n2': (1, 32, 68),  'n3': (2, 39, 74),  'n4': (10, 53, 96),
 'q0': (22, 9, 58), 'q1': (40, 11, 76),'q2': (52, 16, 89), 'q3': (74, 21, 78), 'q4': (81, 35, 80),
 'q5': (110, 45, 107),
 'mauve': (168, 96, 139),
 'm0': (128, 36, 93), 'm1': (171, 37, 95), 'm2': (216, 65, 106), 'm3': (240, 106, 148),
 'r0': (92, 10, 44),  'r1': (152, 13, 57), 'r2': (194, 44, 80),
 'cor': (252, 125, 103), 'cream': (253, 227, 209),
 'y0': (184, 122, 14), 'y1': (252, 200, 0), 'y2': (255, 227, 138),
 'g0': (20, 73, 60), 'g1': (58, 168, 138), 'g2': (112, 215, 180),
 'b0': (21, 47, 116), 'b1': (36, 73, 185), 'b2': (49, 93, 196), 'b3': (91, 138, 232),
 'b4': (156, 199, 247), 'b5': (217, 236, 255),
 'gray0': (110, 102, 96), 'gray1': (154, 144, 138), 'gray2': (201, 194, 184),
 'wht': (255, 255, 255),
 'o0': (196, 106, 32), 'o1': (247, 152, 54), 'o2': (255, 214, 140),
 'cool1': (96, 86, 168), 'cool2': (150, 140, 214),
 'chrome': (206, 208, 222), 'chrome2': (150, 152, 172),
}

im = Image.new("RGB", (W, H), P['ink'])
d = ImageDraw.Draw(im)

def C(c):
    return P[c] if isinstance(c, str) else tuple(c)

def R(x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=C(c))

def PX(x, y, c):
    d.point((x, y), fill=C(c))

def O(x, y, w, h, fill, out):
    R(x, y, w, h, out); R(x + 1, y + 1, w - 2, h - 2, fill)

def DIT(x, y, w, h, c, den=2, ph=0):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx + yy + ph) % den == 0:
                PX(xx, yy, c)

# ═══ 壁と天井(トップの部屋と同じ世界観・少し青寄りの作業部屋) ═══
R(0, 0, W, 176, 'q0')
for yy in range(0, 176, 1):                          # 上下のグラデ(上ほど暗い)
    t = yy / 176
    if t < .25: DIT(0, yy, W, 1, 'ink', 2, yy)
    elif t < .5: DIT(0, yy, W, 1, 'ink', 4, yy)
R(0, 0, W, 10, 'ink')                                # 天井の闇
DIT(0, 10, W, 3, 'q0', 2)
for xx in range(0, W, 4):                            # 壁の縦のディザ模様(トップと同じ質感)
    for yy in range(14, 172, 4):
        if (xx // 4 + yy // 4) % 2 == 0:
            PX(xx, yy, 'q1')
# 四隅ビネット
DIT(0, 0, 60, 60, 'ink', 3); DIT(W - 60, 0, 60, 60, 'ink', 3)

# ═══ 幅木と床 ═══
R(0, 168, W, 3, 'q1'); R(0, 170, W, 1, 'ink')
R(0, 171, W, 69, 'q0')
for yy in range(171, 240, 6):                        # 床板
    R(0, yy, W, 1, 'q1')
R(0, 203, W, 1, 'm1')                                # 継ぎ目のマゼンタ発光(トップと同じ流儀)
for xx in range(0, W, 24):
    PX(xx, 203, 'm3')
DIT(0, 208, W, 32, 'ink', 2)                         # 前景の暗い帯
R(0, 236, W, 4, 'ink')

# ═══ 天井のLEDバー(この部屋の常夜灯) ═══
R(96, 8, 196, 2, 'cool1'); R(100, 9, 188, 1, 'cool2')
DIT(96, 10, 196, 4, 'cool1', 3)

# ═══ 大型モニタ(部屋の主役・画面の中身はHTMLが重ねる) ═══
MX, MY, MW, MH = 98, 16, 196, 102                    # ベゼル外形
R(MX - 2, MY + 2, MW + 4, MH + 2, 'ink')             # 背後の影
O(MX, MY, MW, MH, 'q1', 'ink')                       # 筐体
O(MX + 2, MY + 2, MW - 4, MH - 4, 'n0', 'q2')        # 内ベゼル
SX, SY, SW, SH = MX + 6, MY + 6, MW - 12, MH - 16    # 画面(HTMLが重なる)
R(SX - 1, SY - 1, SW + 2, SH + 2, 'ink')
R(SX, SY, SW, SH, 'n0')
DIT(SX, SY, SW, SH, 'n1', 3)                          # 消えている画面のノイズ
R(MX + 4, MY + MH - 8, MW - 8, 1, 'q2')              # ベゼル下端のライン
PX(MX + MW - 8, MY + MH - 5, 'g2')                   # 電源LED
R(MX + 8, MY + MH - 6, 24, 2, 'q2')                  # メーカー銘板風
# スタンド
R(MX + MW // 2 - 14, MY + MH, 6, 8, 'q1'); R(MX + MW // 2 + 8, MY + MH, 6, 8, 'q1')
R(MX + MW // 2 - 24, MY + MH + 8, 48, 3, 'q1'); R(MX + MW // 2 - 24, MY + MH + 8, 48, 1, 'q3')
# 画面の光が壁へこぼれる(2段)
DIT(MX - 5, MY + 8, 5, MH - 16, 'n2', 2)
DIT(MX - 10, MY + 6, 5, MH - 12, 'b0', 3)
DIT(MX + MW, MY + 8, 5, MH - 16, 'n2', 2)
DIT(MX + MW + 5, MY + 6, 5, MH - 12, 'b0', 3)
DIT(MX + 10, MY - 5, MW - 20, 5, 'n2', 3)

# ═══ 左のメニューパネル4枚(クリックでモニタの内容が変わる) ═══
LPX, LPW, LPH = 8, 82, 20
LYS = [22, 46, 70, 94]
for i, py in enumerate(LYS):
    R(LPX + 1, py + 2, LPW, LPH, 'ink')              # 影
    O(LPX, py, LPW, LPH, 'n0', 'ink')
    R(LPX + 1, py + 1, LPW - 2, 1, 'cool2')          # 上端ハイライト
    R(LPX + 1, py + LPH - 2, LPW - 2, 1, 'q1')
    R(LPX + 2, py + 2, 2, LPH - 4, 'cool1')          # 左の色帯
    PX(LPX + LPW - 3, py + 2, 'chrome2'); PX(LPX + LPW - 3, py + LPH - 3, 'chrome2')  # ネジ
# パネル群の見出しプレート
R(LPX, 14, 40, 6, 'q1'); R(LPX, 14, 40, 1, 'q3')

# ═══ 右の作例パネル4枚(クリックでモニタに映像が流れる) ═══
RPX = 294
for i, py in enumerate(LYS):
    R(RPX + 1, py + 2, LPW, LPH, 'ink')
    O(RPX, py, LPW, LPH, 'n0', 'ink')
    R(RPX + 1, py + 1, LPW - 2, 1, 'o2')
    R(RPX + 1, py + LPH - 2, LPW - 2, 1, 'q1')
    R(RPX + 2, py + 2, 2, LPH - 4, 'o0')             # 左の色帯(作例=暖色)
    # 小さな▶(映像の印)
    for k in range(3):
        R(RPX + LPW - 8 + k, py + LPH // 2 - 2 + k, 1, 4 - k * 2 + (1 if k < 2 else 0), 'o1')
    PX(RPX + LPW - 3, py + 2, 'chrome2')
R(RPX + 42, 14, 40, 6, 'q1'); R(RPX + 42, 14, 40, 1, 'q3')

# ═══ デスク(幅いっぱい) ═══
R(0, 128, W, 2, 'q5')                                # 天板の受光エッジ
R(0, 130, W, 6, 'q3')                                # 天板
DIT(0, 130, W, 2, 'q5', 2)
R(0, 136, W, 2, 'ink')
R(0, 138, W, 30, 'q1')                               # 前板
for xx in (48, 128, 256, 336):                       # 前板の継ぎ目
    R(xx, 138, 1, 30, 'q0')
DIT(0, 160, W, 8, 'ink', 2)                          # 前板の下影
# モニタの光が天板へ(画面幅いっぱい・2段)
R(SX, 128, SW, 1, 'n3')
DIT(SX, 129, SW, 3, 'n2', 2)
DIT(SX + 10, 132, SW - 20, 2, 'b0', 3)
# 床への反射(縦のぼんやりした帯)
for k, xx in enumerate(range(SX + 16, SX + SW - 16, 2)):
    ph = (k * 7) % 5
    if k % 2 == 0:
        PX(xx, 172 + ph, 'n2'); PX(xx, 178 + (ph * 3) % 7, 'n1')
    if k % 3 == 0:
        PX(xx, 186 + (ph * 2) % 9, 'n1')

# ═══ 編集機(デスク右・ボタンいっぱい) ═══
EX, EY, EW, EH = 226, 108, 66, 22
R(EX + 1, EY + 3, EW, EH, 'ink')                     # 影
O(EX, EY, EW, EH, 'q2', 'ink')                       # 本体(斜めの操作面)
R(EX + 1, EY + 1, EW - 2, 2, 'chrome2')              # 上端の金属
R(EX + 2, EY + 4, EW - 4, 1, 'q4')
# ボタンの格子(3列x9) — 光る側は edit_glow.png が重なる
for row, by in enumerate((EY + 7, EY + 11, EY + 15)):
    for col in range(9):
        bx = EX + 4 + col * 5
        PX(bx, by, ('q4', 'q1', 'q4')[row]); PX(bx + 1, by, 'ink')
# フェーダー1本
for fx in (EX + 61,):
    R(fx, EY + 6, 1, 12, 'ink'); R(fx - 1, EY + 10, 3, 2, 'chrome')
# ジョグダイヤル
d.ellipse([EX + 48, EY + 6, EX + 58, EY + 16], fill=C('q1'), outline=C('ink'))
d.ellipse([EX + 51, EY + 9, EX + 55, EY + 13], fill=C('chrome2'))
# 編集機からモニタへのケーブル
for k in range(6):
    PX(EX + 30 - k, EY - 1 - (k % 3), 'ink')

# ═══ キーボードとマウス(デスク左) ═══
O(112, 120, 52, 8, 'q2', 'ink')
R(113, 120, 50, 1, 'n4')                              # モニタ光のリム
for kx in range(115, 160, 4):
    R(kx, 122, 2, 1, 'q4'); R(kx, 125, 2, 1, 'q4')
O(172, 122, 9, 6, 'q2', 'ink'); PX(176, 123, 'q4')
# マグカップ(湯気つき)
O(84, 116, 11, 12, 'm2', 'ink')
R(85, 117, 9, 2, 'q1')                                # コーヒーの口
R(85, 123, 9, 1, 'm0')                                # 胴の陰
R(95, 119, 1, 5, 'ink'); PX(96, 120, 'ink'); PX(96, 122, 'ink')   # 取っ手
PX(88, 112, 'cool2'); PX(89, 110, 'cool2'); PX(88, 107, 'cool1')  # 湯気

# ═══ ゲーミングチェア(中央・背面から) ═══
GX = 178                                              # 左端。中心はx197
# チェア用のフロアマット(モニタの光を受ける)
O(156, 176, 84, 22, 'n0', 'q1')
R(157, 177, 82, 1, 'n2')
DIT(160, 180, 76, 14, 'n1', 3)
# 接地影
R(GX - 2, 189, 44, 3, 'ink')
# 星型5本脚(全キャスター接地)
for lx in (-16, -8, 0, 8, 16):
    yb = 184 if abs(lx) > 8 else 186
    R(197 + lx - 1, yb, 3, 188 - yb, 'q2')
    R(197 + lx - 2, 187, 5, 3, 'ink')                 # キャスター(全部 y187-189)
    PX(197 + lx, 188, 'q4')
R(196, 182, 3, 4, 'q2')                               # 脚のハブ
# ガス圧シリンダー(1段明るく)
R(195, 170, 5, 12, 'q2'); R(195, 170, 1, 12, 'chrome2'); R(199, 170, 1, 12, 'ink')
# 座面
O(180, 162, 34, 10, 'q1', 'ink'); R(181, 163, 32, 2, 'q3')
# 背もたれ(小ぶりに・サイドサポートで面を割る)
O(180, 124, 34, 40, 'q1', 'ink')
R(182, 126, 3, 36, 'q2'); R(209, 126, 3, 36, 'q2')    # サイドの盛り上がり
R(185, 126, 2, 36, 'm1'); R(207, 126, 2, 36, 'm1')    # 赤ステッチ
PX(185, 126, 'm2'); PX(208, 126, 'm2')
R(190, 128, 14, 34, 'q0')                             # 背面の凹み
DIT(191, 130, 12, 30, 'q2', 3)
R(194, 132, 6, 3, 'm1')                               # ロゴ刺繍
# ヘッドレスト(上辺にモニタの寒色リム)
O(186, 114, 22, 12, 'q1', 'ink'); R(188, 116, 18, 2, 'q2')
R(190, 118, 14, 3, 'm1'); R(191, 119, 12, 1, 'm2')
R(188, 114, 18, 1, 'n4')                              # 寒色リムライト
# アームレスト
R(174, 144, 8, 4, 'ink'); R(175, 145, 6, 2, 'q2')
R(212, 144, 8, 4, 'ink'); R(213, 145, 6, 2, 'q2')

# ═══ かたわらのテーブル(右) ═══
R(334, 186, 40, 3, 'ink')                             # 接地影
O(332, 150, 44, 6, 'q3', 'ink'); R(333, 151, 42, 1, 'q5')    # 丸天板
R(350, 156, 6, 28, 'q1'); R(350, 156, 2, 28, 'q2')    # 支柱
R(342, 184, 22, 3, 'q1')                              # 台座
# 天板の上: タブレットとペン(天板に接地)
O(336, 144, 16, 7, 'n0', 'ink'); R(338, 146, 12, 3, 'b0')
R(356, 148, 10, 2, 'y0'); PX(366, 148, 'cream')
# 支柱に立てかけたフィルムリール(床に接地)
d.ellipse([336, 166, 352, 182], fill=C('q3'), outline=C('ink'))
d.ellipse([342, 172, 346, 176], fill=C('q0'))
for hx, hy in ((339, 169), (349, 169), (339, 179), (349, 179)):
    PX(hx, hy, 'q1')
R(337, 182, 14, 1, 'ink')                             # 接地ライン


# ═══ デスク左: テープ/HDDの山・ヘッドホンスタンド ═══
# 積まれたメディア(色はトップページのアクセント色・パネルに被らない高さ)
O(8, 122, 26, 6, 'cor', 'ink'); R(10, 124, 8, 2, 'y1')
O(10, 116, 24, 6, 'b2', 'ink'); R(12, 118, 6, 2, 'wht')
# 机のふちに掛けたヘッドホン
d.arc([44, 130, 62, 146], 160, 20, fill=C('m2'), width=2)
R(42, 136, 5, 9, 'm1'); R(59, 136, 5, 9, 'm1')
R(43, 137, 1, 7, 'm3'); R(60, 137, 1, 7, 'm3')
PX(52, 130, 'chrome2')
# ═══ デスク前板: 引き出しとステッカー ═══
for dx in (10, 52):
    O(dx, 142, 34, 22, 'q2', 'q0')
    R(dx + 12, 150, 10, 2, 'chrome2'); R(dx + 12, 150, 10, 1, 'chrome')
PX(20, 158, 'y1'); PX(28, 160, 'g2'); PX(60, 157, 'cor'); PX(70, 159, 'b3')  # ステッカー
for dx in (322, 356):
    O(dx, 142, 26, 22, 'q2', 'q0')
    R(dx + 8, 150, 10, 2, 'chrome2')
# 垂れるケーブル(デスク左端から床へ)
for k in range(30):
    PX(100 + (k % 3), 138 + k, 'ink')
PX(101, 148, 'n4'); PX(100, 160, 'n4')
for xx in range(102, 156, 2):
    PX(xx, 168 + ((xx // 2) % 3), 'ink')
# ═══ 右の壁: カチンコ(パネルと机のあいだに掛ける) ═══
O(336, 117, 34, 10, 'q1', 'ink')
for k, xx in enumerate(range(337, 369, 4)):           # 白黒のしま
    R(xx, 118, 2, 2, 'gray2' if k % 2 == 0 else 'ink')
R(338, 121, 30, 1, 'q0')
R(340, 123, 16, 1, 'gray1'); R(340, 125, 10, 1, 'gray1')
# ═══ 床の小物 ═══
# 散らばった絵コンテ
O(118, 198, 12, 7, 'cream', 'ink'); R(120, 200, 8, 1, 'q1'); R(120, 202, 6, 1, 'q1')
O(132, 201, 11, 6, 'cream', 'ink'); R(134, 203, 6, 1, 'q1')
# マスキングテープのロール
d.ellipse([258, 198, 266, 206], fill=C('gray2'), outline=C('ink'))
d.ellipse([260, 200, 264, 204], fill=C('q0'))
# 電源タップとコード(右)
O(282, 202, 22, 5, 'q2', 'ink'); PX(285, 204, 'g2'); PX(290, 204, 'o1')
for xx in range(304, 332, 2):
    PX(xx, 204 + ((xx // 2) % 2), 'ink')
# ═══ 前景の帯(トップページの転がる絵本と同じ言語で) ═══
# 左: フィルム缶の山
O(10, 224, 30, 8, 'q2', 'ink'); R(12, 226, 8, 2, 'm2')
O(14, 216, 26, 8, 'q3', 'ink'); R(16, 218, 8, 2, 'b2')
O(18, 208, 22, 8, 'q2', 'ink'); R(20, 210, 6, 2, 'g1')
# 右: ポスター筒(トップページの筒と同族)
R(338, 212, 34, 10, 'q2'); R(338, 212, 34, 2, 'q4'); R(338, 220, 34, 2, 'q0')
d.ellipse([368, 212, 376, 222], fill=C('q4'), outline=C('ink'))
d.ellipse([370, 214, 374, 220], fill=C('m1'))
R(300, 226, 44, 8, 'q1'); R(302, 228, 8, 4, 'cor')    # 平置きの台本ケース
# 床へのモニタ光の映り込み
for k, xx in enumerate(range(MX + 30, MX + MW - 30, 3)):
    if k % 2 == 0:
        PX(xx, 174 + (k % 5), 'n2')
        PX(xx, 180 + (k % 7), 'n1')

im.save(os.path.join(HERE, "edit_room.png"))
print("edit_room.png written", im.size)

# ═══ 編集機のキラキラ(4コマ・背景の同じ位置に重ねる) ═══
GW, GH = EW, EH + 4
glow = Image.new("RGBA", (GW * 4, GH), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
CYC = [P['o1'], P['m3'], P['g2'], P['b4'], P['y1'], P['cool2']]
for f in range(4):
    ox = f * GW
    for row, by in enumerate((7, 11, 15)):
        for col in range(9):
            if (col + row + f) % 3 == 0:              # 1/3ずつ順番に点灯
                c = CYC[(col * 2 + row * 3 + f) % len(CYC)]
                gd.point((ox + 4 + col * 5, by), fill=c + (255,))
                gd.point((ox + 4 + col * 5, by - 1), fill=c + (90,))
    # ジョグダイヤルの回転きらり
    jx, jy = ox + 53, 11
    pos = [(0, -4), (4, 0), (0, 4), (-4, 0)][f]
    gd.point((jx + pos[0], jy + pos[1]), fill=P['wht'] + (200,))
    # フェーダーのLED
    gd.point((ox + 61, 6 + f * 3), fill=P['g2'] + (220,))
glow.save(os.path.join(HERE, "edit_glow.png"))
print("edit_glow.png written", glow.size)

# ═══ 立ち姿のマユちゃん(仮) 40x72 x 4コマ ═══
MC = {
 'hair': (10, 8, 14), 'hair2': (36, 32, 46),
 'skin': (246, 210, 168), 'skin2': (216, 176, 134),
 'shirt': (212, 217, 235), 'shirt2': (168, 172, 198),
 'pants': (34, 27, 180), 'pants2': (26, 21, 162),
 'shoe': (150, 30, 30), 'shoe2': (110, 16, 16),
 'blush': (240, 150, 170), 'ink': (4, 2, 26),
}
FW2, FH2 = 40, 72
sheet = Image.new("RGBA", (FW2 * 4, FH2), (0, 0, 0, 0))

def draw_mayu(frame, ox, blink=False, bob=0):
    md = ImageDraw.Draw(sheet)
    def r2(x, y, w, h, c):
        if w > 0 and h > 0:
            md.rectangle([ox + x, y, ox + x + w - 1, y + h - 1], fill=MC[c])
    def p2(x, y, c):
        md.point((ox + x, y), fill=MC[c])
    yo = bob                                   # 上半身だけ1px沈む(足は接地のまま)
    # 脚(パンツ) — 接地固定
    r2(12, 50 + yo, 16, 8, 'pants')            # 腰
    r2(12, 58, 7, 8, 'pants'); r2(21, 58, 7, 8, 'pants')
    r2(12, 58, 2, 8, 'pants2'); r2(21, 58, 2, 8, 'pants2')
    # 靴(赤いスリッポン)
    r2(10, 66, 9, 5, 'shoe'); r2(20, 66, 9, 5, 'shoe')
    r2(10, 69, 9, 2, 'shoe2'); r2(20, 69, 9, 2, 'shoe2')
    p2(17, 67, 'blush'); p2(27, 67, 'blush')   # 靴のワンポイント
    # 胴(シャツ)
    r2(10, 30 + yo, 20, 21, 'shirt')
    r2(10, 30 + yo, 3, 21, 'shirt2')           # 左(奥)の陰
    r2(28, 32 + yo, 4, 14, 'shirt')            # 右腕
    r2(28, 46 + yo, 4, 3, 'skin')              # 右手
    r2(8, 33 + yo, 3, 12, 'shirt2')            # 左腕(奥)
    # 顔(前髪の下)
    r2(12, 16 + yo, 20, 14, 'skin')
    r2(12, 16 + yo, 3, 14, 'skin2')
    # 髪(大きなおかっぱ)
    r2(8, 2 + yo, 26, 14, 'hair')              # 頭頂〜前髪
    r2(6, 6 + yo, 4, 22, 'hair')               # 左のサイド(長め)
    r2(32, 6 + yo, 4, 18, 'hair')              # 右のサイド
    p2(14, 16 + yo, 'hair'); p2(15, 16 + yo, 'hair')   # 前髪の毛先(ぎざぎざ)
    p2(20, 16 + yo, 'hair'); p2(21, 16 + yo, 'hair')
    p2(27, 16 + yo, 'hair'); p2(28, 16 + yo, 'hair')
    r2(9, 3 + yo, 24, 2, 'hair2')              # 髪のツヤ
    p2(20, 0 + yo, 'hair'); p2(21, 1 + yo, 'hair'); p2(19, 1 + yo, 'hair')  # アホ毛
    # 目と口(右向き)
    if blink:
        r2(25, 22 + yo, 4, 1, 'ink')
    else:
        r2(25, 19 + yo, 3, 4, 'ink')
        p2(26, 20 + yo, 'wht2') if False else None
    p2(30, 26 + yo, 'ink')                     # 口
    r2(22, 25 + yo, 2, 2, 'blush')             # ほっぺ
    # 輪郭(シルエットの外周に1pxのink) — 透明に接する画素を縁取る
    px = sheet.load()
    for yy in range(FH2):
        for xx in range(FW2):
            c = px[ox + xx, yy]
            if c[3] == 0:
                continue
            edge = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = xx + dx, yy + dy
                if not (0 <= nx < FW2 and 0 <= ny < FH2) or px[ox + nx, ny][3] == 0:
                    edge = True
                    break
            if edge and c[:3] != MC['ink']:
                px[ox + xx, yy] = MC['ink'] + (255,)

for f, (blink, bob) in enumerate([(False, 0), (False, 1), (False, 0), (True, 0)]):
    draw_mayu(f, f * FW2, blink=blink, bob=bob)
sheet.save(os.path.join(HERE, "mayu_stand.png"))
print("mayu_stand.png written", sheet.size)

# ═══ HTMLが使う矩形 ═══
rects = {
 "screen": [SX, SY, SW, SH],
 "menuL": [[LPX, y, LPW, LPH] for y in LYS],
 "menuR": [[RPX, y, LPW, LPH] for y in LYS],
 "console": [EX, EY - 2, GW, GH],
 "mayu": [30, 128, FW2, FH2],
 "patti": [318, 154, 36, 48],
}
json.dump(rects, io.open(os.path.join(HERE, "edit_room.json"), "w", encoding="utf-8"))
print("edit_room.json written")
