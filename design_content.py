# -*- coding: utf-8 -*-
"""make_room_design.py の中身(座標〜描画)。組み立てスクリプトが挟み込む。"""
CONTENT = r'''
# ═══════════════ 主要座標(ここだけ見れば配置が分かる) ═══════════════
BOARD  = (47, 12, 290, 150)     # 壁一面が黒板(赤線指示どおり下まで) x47..336 / y12..161

RAIL_Y = 161                    # チョーク受け(黒板の下端・床のすぐ上)
GAR_SPANS = [(50, 192, 13, 4, 8), (192, 334, 13, 4, 8)]   # 電球ガーランド(浅く吊って標語と重ねない)
DOORX0, DOORX1 = 345, 373       # スタジオへ戻る戸口(右の壁)
# 黒板に貼ってある紙 (x, y, w, h)
PAP_DESIGN = (57, 47, 73, 40)   # 黄: キャラクターデザイン＆設計(左上)
PAP_SKETCH = (222, 110, 24, 27) # おばけのラフ絵(物語の右)
PAP_STORY = (128, 25, 128, 14) # 白: Story is King(電球の下・黒板上部センター)
PAP_SPOOKS = (66, 110, 70, 28)  # Spooks GS(指示画像の赤枠を実尺で測った位置)
PAP_WORLD = (162, 73, 80, 25)  # 桃: 世界観(黄の右)
PAP_TALE = (161, 118, 52, 32) # 赤: 物語(指示画像の赤枠を実尺で測った位置)
DATA_TITLE = (265, 46, 56, 12)  # 見出し「データまとめ」(模造紙と同心)
DATA_PANEL = (256, 62, 74, 80)  # 模造紙(上下左右に余白を取った大きさ)

# ═══════════════ bg : 天井・奥壁・床 ═══════════════
obj()
R('bg', 0, 0, W, H, 'pl1')
# 天井(木造校舎の竿縁天井。古い杉板に細い桟が渡る)
R('bg', 0, 0, W, 12, 'wd0')
DITH('bg', 0, 2, W, 8, None, 'wd1', 'hline')              # 板目
R('bg', 0, 0, W, 2, 'ink')                                # 奥は暗く沈む
for x in range(6, W, 22):                                  # 竿縁(細い桟)
    R('bg', x, 2, 1, 9, 'ink')
    R('bg', x + 1, 2, 1, 9, 'wd1')
R('bg', 0, 10, W, 1, 'wd2')                                # 手前の縁が電球の光を拾う
R('bg', 0, 11, W, 1, 'wd0')

# 奥壁(黒板がのる下地。漆喰)
R('bg', 0, 12, W, 134, 'pl1')
DI('bg', 0, 12, W, 8, 'pl2', 'pl1')
DI('bg', 0, 128, W, 10, 'pl0', 'pl1')
R('bg', 0, 142, W, 4, 'ink')
R('bg', 0, 146, W, 2, 'wd0')

# 床(古い木造校舎の板張り)
# 遠近は部屋そのものに合わせる。側壁の足元線(i=0でy234 / i=46でy168)を
# 左右で延長した交点が、この部屋の消失点。床の目地もそこへ向ける。
VPX = (W - 1) / 2.0
VPY = 234.0 - (66.0 / 46.0) * VPX
FL_Y0 = 148
PLANK = 30.0                                                # 画面下端での板幅

def _floor_x(xb, yy):
    """画面下端で xb を通り消失点へ向かう線の、高さ yy での x。"""
    return VPX + (xb - VPX) * (yy - VPY) / (H - VPY)

# 面: 板の中はほぼ平坦。目地とその脇の受光だけで板を見せる
# (この解像度では細かい点描はノイズになり、遠近が読めなくなる)
PLANK_TONE = (0, 1, 0, -1, 0, 1, -1, 0, 1, 0, -1, 1)        # 板ごとのわずかな色味の差
for yy in range(FL_Y0, H):
    depth = (H - VPY) / (yy - VPY)
    for xx in range(W):
        u = ((xx - VPX) * depth) / PLANK                     # 板の中の位置(0..1)
        k = int(math.floor(u))
        f = u - k
        if f < 0.07:
            c = 'wd0'                                        # 目地
        elif f < 0.15:
            c = 'wd2'                                        # 目地の脇が光を拾う
        elif f > 0.93:
            c = 'wd0'                                        # 反対側の縁も落ちる
        else:
            tone = PLANK_TONE[k % len(PLANK_TONE)]
            c = 'wd1'
            if tone > 0 and (xx * 3 + yy * 7) % 13 == 0:
                c = 'wd2'
            elif tone < 0 and (xx * 5 + yy * 3) % 13 == 0:
                c = 'wd0'
        PXL('bg', xx, yy, c)

_inv0, _inv1 = 1.0 / (H - VPY), 1.0 / (FL_Y0 - VPY)
for n in range(1, 7):                                        # 板の継ぎ手(奥ほど詰まる)
    yy = int(1.0 / (_inv0 + (_inv1 - _inv0) * n / 6.0) + VPY + 0.5)
    for k in range(-9, 9):
        if (k + n) % 3:                                      # 互い違いに継ぐ(格子に見せない)
            continue
        x0 = int(_floor_x(VPX + k * PLANK, yy) + 0.5)
        x1 = int(_floor_x(VPX + (k + 1) * PLANK, yy) + 0.5)
        for xx in range(max(0, x0), min(W, x1)):
            PXL('bg', xx, yy, 'wd0')

for yy in range(FL_Y0, H):                                   # 人が通って擦れた艶
    t = (yy - FL_Y0) / float(H - FL_Y0)
    half = int(26 + 52 * t)
    for xx in range(max(0, int(VPX) - half), min(W, int(VPX) + half)):
        if (xx * 3 + yy * 5) % 23 == 0:
            PXL('bg', xx, yy, 'wd3')
for si, sx5 in enumerate(range(56, W - 48, 24)):             # 電球の映り込み
    PXL('bg', sx5, 176, 'y0' if si % 2 else 'o0')
    PXL('bg', sx5 + 12, 198, 'o0' if si % 2 else 'y0')
DI('bg', 0, 222, W, 10, 'wd1', 'wd0')                        # 手前はゆるやかに沈む
DI('bg', 0, 232, W, 8, 'wd0', 'ink')

# ── 壁を床側へ延長(黒板は下まで)。境目は木の巾木でくっきり ──
R('bg', 0, 148, W, 14, 'pl1')
R('bg', 0, 162, W, 3, 'wd1')                                # 巾木
R('bg', 0, 162, W, 1, 'wd2')
R('bg', 0, 165, W, 2, 'ink')                                # 床との見切りの影

# ─── 側壁(木造校舎: 上が漆喰・下が板張りの腰壁) ───
WAINSCOT_SEAMS = (0, 10, 19, 27, 34, 39, 43, 46)   # 奥ほど詰まる板の継ぎ目
def side_wall(left):
    for i in range(47):
        xx = i if left else W - 1 - i
        t = i / 46.0
        ytop = int(2 + 12 * t + 0.5)
        ybot = int(234 - 66 * t + 0.5)
        rail = int(ytop + (ybot - ytop) * 0.54 + 0.5)       # 腰壁の見切り桟
        for yy in range(ytop, ybot + 1):
            if yy <= ytop + 1:
                c = 'ink'                                    # 回り縁(天井との見切り)
            elif yy <= ytop + 3:
                c = 'wd0'
            elif yy < rail - 2:
                # 漆喰: 塗りムラを粗いディザで。ドット柄に見えないよう不規則に
                base = 'pl1' if t > 0.5 else 'pl2'
                if (xx * 5 + yy * 3) % 7 == 0:
                    base = 'pl0' if t > 0.5 else 'pl1'
                c = 'pl0' if (xx * 29 + yy * 17) % 53 < 2 else base
            elif yy == rail - 2:
                c = 'ink'                                    # 見切り桟の落ち影
            elif yy == rail - 1:
                c = 'wd3'                                    # 桟の天面(光を拾う)
            elif yy <= rail + 1:
                c = 'wd1'                                    # 桟の見付け
            elif yy == rail + 2:
                c = 'wd0'                                    # 桟の下の影
            elif yy >= ybot - 1:
                c = 'ink'                                    # 巾木の下の影
            elif yy >= ybot - 4:
                c = 'wd1'                                    # 巾木
            elif yy == ybot - 5:
                c = 'wd2'                                    # 巾木の天面
            else:
                c = 'wd1' if (xx * 7 + yy * 3) % 31 else 'wd0'   # 板張りの腰壁
            PXL('bg', xx, yy, c)
        if i in WAINSCOT_SEAMS:                              # 腰壁の板の継ぎ目(実目地)
            for yy in range(rail + 3, ybot - 5):
                PXL('bg', xx, yy, 'ink')
                nx = xx + (1 if left else -1)
                if 0 <= nx < W:
                    PXL('bg', nx, yy, 'wd2')                 # 目地の片側が光を拾う
    cx0 = 46 if left else W - 47
    R('bg', cx0, 13, 1, 156, 'ink')
    R('bg', cx0 + (1 if left else -1), 14, 1, 154, 'wd1')
side_wall(True)
side_wall(False)

# ─── 左の壁: 木造校舎の窓(木の格子・夜の月あかり) ───
obj('教室の窓')
WI0, WI1 = 0, 43                       # 窓が入る壁の範囲(i が大きいほど奥・画面の端まで続く)
MULL_I = (13, 22, 31, 38)              # 縦の桟(奥ほど詰まる)
# 窓の外の家並み: 列ごとの屋根の高さ。切妻と陸屋根が混じる低い町
TREE = (3, 6, 9, 9, 9, 9, 5, 2, 2, 7, 11, 13, 13, 13, 9, 4, 2, 5, 8, 8, 8, 8, 4, 2)
# 明かりの漏れる窓(列オフセット, 稜線からの深さ)
HOMEWIN = ((3, 4), (4, 7), (10, 4), (12, 8), (13, 4), (18, 5), (19, 8), (20, 4))

def _wall_band(i):
    t = i / 46.0
    ytop = int(2 + 12 * t + 0.5)
    ybot = int(234 - 66 * t + 0.5)
    return ytop, int(ytop + (ybot - ytop) * 0.54 + 0.5)

for i in range(WI0, WI1 + 1):
    ytop, rail = _wall_band(i)
    wy0, wy1 = ytop + 14, rail - 2                           # 窓の上下(少し下へ)
    hh = max(1, wy1 - wy0)
    mid = wy0 + int(hh * 0.46)                               # 上下の障子の分かれ目
    horizon = wy0 + int(hh * 0.76)                           # 遠くの稜線
    tree_top = horizon - TREE[i % len(TREE)]                 # 木立の高さ
    frame_col = i <= WI0 + 1 or i >= WI1 - 1
    for yy in range(wy0, wy1 + 1):
        if frame_col or yy <= wy0 + 1 or yy >= wy1 - 1:
            c = 'wd1'                                        # 窓枠
        elif i in MULL_I or mid <= yy <= mid + 1:
            c = 'wd0'                                        # 格子の桟
        else:
            # 空は夕暮れ。上が藍、地平に近づくほど暖色になる
            g = (yy - wy0) / float(hh)
            if yy >= tree_top:                               # 家並みのシルエット
                c = 'ink' if yy > horizon + 4 else 'bd0'
                if yy == tree_top:
                    c = 'bd1'                                # 屋根の稜線がわずかに残る
                for hw, hd in HOMEWIN:                       # 明かりの漏れる窓(2px角)
                    if i % len(TREE) in (hw, hw + 1) and tree_top + hd <= yy <= tree_top + hd + 1:
                        c = 'y2' if yy == tree_top + hd else 'o1'
            elif g < 0.20:
                c = 'cool1'
            elif g < 0.38:
                c = 'b3'
            elif g < 0.54:
                c = 'b4'
            elif g < 0.64:
                c = 'cream'
            else:
                c = 'cor2' if g < 0.70 else 'o1'             # 稜線ぎわが一番あかるい
            if g < 0.36 and (i * 7 + yy * 3) % 31 == 0:
                c = 'wht'                                    # 一番星
        PXL('bg', i, yy, c)
    PXL('bg', i, wy0, 'wd2')                                 # 上枠の天面が光を拾う
    R('bg', i, wy1 + 1, 1, 2, 'wd2')                         # 窓台
    PXL('bg', i, wy1 + 3, 'ink')                             # 窓台の下の影

# 夕日が腰壁と床へこぼれる
for i in range(WI0, WI1 + 1):
    _, rail = _wall_band(i)
    for k in range(9):
        yy = rail + 4 + k
        if (i + yy) % (2 + k // 2) == 0:
            PXL('bg', i, yy, 'wd3' if k < 5 else 'wd2')
for yy in range(168, 226):
    for xx in range(0, 86):
        if xx <= 46 and yy <= 234 - (66.0 / 46.0) * xx:
            continue                                         # まだ壁の中
        d = xx / 86.0 + (yy - 168) / 70.0
        if d < 1.0 and (xx * 5 + yy * 3) % (3 + int(d * 11)) == 0:
            PXL('bg', xx, yy, 'wd3' if d < 0.5 else 'wd2')


# ═══════════════ 壁一面の黒板 ═══════════════
obj('黒板')
bx, by, bw, bh = BOARD

# ── スレート面: 上ほど明るい3階調。ベタで置いてからムラを重ねる ──
for yy in range(by, by + bh):
    t = (yy - by) / float(bh - 1)
    R('bg', bx, yy, bw, 1, 'bd2' if t < 0.12 else ('bd1' if t < 0.68 else 'bd0'))
DITH('bg', bx, by, bw, 22, None, 'bd2', 'sparse')            # 天井からの照り返し
R('bg', bx, by, bw, 1, 'bd3')                                # 天井との見切り
R('bg', bx, by + 1, bw, 1, 'bd2')
# 拭き跡の弧(消しゴムの往復)
for ax, ay, arx, ary in [(100, 104, 50, 22), (206, 130, 40, 20), (276, 40, 38, 17),
                         (90, 60, 34, 14), (172, 50, 42, 16), (300, 148, 34, 12),
                         (250, 100, 30, 14)]:
    for yy in range(max(by, ay - ary), min(by + bh, ay + ary + 1)):
        for xx in range(max(bx, ax - arx), min(bx + bw, ax + arx + 1)):
            e = ((xx - ax) / float(arx)) ** 2 + ((yy - ay) / float(ary)) ** 2
            if 0.58 < e < 1.0 and (xx * 3 + yy * 5) % 4 == 0:
                PXL('bg', xx, yy, 'bd2')
            elif e <= 0.58 and (xx + yy * 2) % 9 == 0:
                PXL('bg', xx, yy, 'bd2')
# 下に溜まったチョークの粉
for yy in range(by + bh - 16, by + bh):
    d = (yy - (by + bh - 16)) / 15.0
    step = max(2, int(16 - d * 13))
    for xx in range(bx, bx + bw):
        if (xx * 7 + yy * 11) % step == 0:
            PXL('bg', xx, yy, 'bd3')
for sx, sy, sl in [(88, 44, 9), (152, 78, 6), (240, 116, 11), (306, 66, 7), (62, 96, 5)]:
    for k in range(sl):                                       # 細かい傷
        PXL('bg', sx + k, sy - k // 3, 'bd3')

# ─── チョークの線(かすれた点線)と矢印 ───
_cn = [0]
# 紙が貼ってあるところにチョークを引くと、紙で半分隠れて汚く見える。
# 紙の矩形+余白の中には引かない。
PAPER_RECTS = [PAP_DESIGN, PAP_SKETCH, PAP_STORY, PAP_SPOOKS, PAP_WORLD, PAP_TALE,
               DATA_TITLE, DATA_PANEL]

def chalk_free(x, y, pad=4):
    for (rx9, ry9, rw9, rh9) in PAPER_RECTS:
        if rx9 - pad <= x < rx9 + rw9 + pad and ry9 - pad <= y < ry9 + rh9 + pad:
            return False
    return True

def CPX(x, y, c):
    if chalk_free(x, y):
        PXL('bg', x, y, c)

def chalk_line(pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for k in range(steps + 1):
            t = k / float(steps) if steps else 0.0
            xx = int(round(x0 + (x1 - x0) * t)); yy = int(round(y0 + (y1 - y0) * t))
            _cn[0] += 1
            if _cn[0] % 5 == 4:
                continue                                   # かすれ
            CPX(xx, yy, 'chk' if _cn[0] % 3 else 'chk2')

def chalk_head(x, y, dx, dy):
    """矢じり(進む向きに開く)"""
    for k in range(1, 5):
        CPX(x - dx * k - dy * (k // 2), y - dy * k + dx * (k // 2), 'chk')
        CPX(x - dx * k + dy * (k // 2), y - dy * k - dx * (k // 2), 'chk')
    CPX(x, y, 'chk')

def chalk_circle(cx9, cy9, r9, dense=3):
    """チョークで描いた円(あたり)。かすれさせる。"""
    n9 = max(12, int(r9 * 6))
    for k in range(n9):
        a9 = k * 2 * math.pi / n9
        if k % dense == 0:
            continue
        CPX(int(cx9 + math.cos(a9) * r9 + 0.5),
                  int(cy9 + math.sin(a9) * r9 * 0.92 + 0.5), 'chk2')

def chalk_write(x9, y9, rows, wmax):
    """手書きの走り書き(読めなくてよい)。行ごとに長さを変える。"""
    for r9 in range(rows):
        yy = y9 + r9 * 4
        ln = wmax - (r9 * 7) % (wmax // 2)
        xx = x9
        while xx < x9 + ln:
            seg = 2 + (xx * 3 + r9) % 4
            for k in range(seg):
                if (xx + k) < x9 + ln:
                    CPX(xx + k, yy, 'chk2')
            xx += seg + 2

obj('チョークの矢印')
# 設計の紙 → 世界観 (下へ回り込む)
def chalk_arrow(pts, hx, hy, dx, dy):
    """矢印。線は2本重ねて太くし、矢じりは三角形で描く(細い線だと矢印に見えない)。"""
    chalk_line(pts)
    chalk_line([(x, y + 1) for x, y in pts])
    for k in range(6):                                   # 矢じり(三角)
        for m in range(-k, k + 1):
            CPX(hx + dx * (-k) + (m if dy else 0),
                      hy + dy * (-k) + (0 if dy else m), 'chk')
    CPX(hx, hy, 'chk')

# 黄 → 世界観 (右へ)。矢じりは紙の4px手前で止める
chalk_arrow([(134, 58), (142, 62), (149, 66)], 154, 69, 1, 0)
# 世界観 → 物語 (下へ)
chalk_arrow([(186, 102), (186, 106)], 186, 112, 0, 1)

obj('チョークの書き込み')
# キャラのあたり(円+十字)。黄と物語のあいだの空きへ
chalk_circle(148, 106, 10); chalk_circle(148, 106, 7, 4)
for k in range(-8, 9):
    if k % 3: CPX( 148 + k, 106, 'chk2')
for k in range(-8, 9):
    if k % 3: CPX( 148, 106 + k, 'chk2')
# 身長比較のあたり線(縦の目盛り)。物語とラフ絵のあいだ
for yy in range(104, 150, 2):
    CPX( 204, yy, 'chk2')
for k, yy in enumerate((106, 118, 132, 148)):
    for dx9 in range(4):
        CPX( 204 + dx9, yy, 'chk' if k == 1 else 'chk2')
# 走り書き
chalk_write(62, 98, 3, 44)
chalk_write(208, 152, 2, 38)
chalk_write(136, 156, 2, 56)
# 小さなおばけの落書き
for k, (gx9, gy9) in enumerate(((134, 100), (322, 30))):
    r9 = 5
    for a9 in range(180, 361, 12):
        CPX( int(gx9 + math.cos(math.radians(a9)) * r9),
                  int(gy9 + math.sin(math.radians(a9)) * r9), 'chk2')
    for dx9 in range(-r9, r9 + 1):
        if (dx9 + r9) % 3 != 1:
            CPX( gx9 + dx9, gy9 + r9 - abs(dx9) % 2, 'chk2')
    CPX( gx9 - 2, gy9 - 1, 'chk'); CPX( gx9 + 2, gy9 - 1, 'chk')
# きらめき(★)
for sx9, sy9 in ((200, 60), (140, 46), (86, 26)):
    CPX( sx9, sy9 - 2, 'chk'); CPX( sx9, sy9 + 2, 'chk')
    CPX( sx9 - 2, sy9, 'chk'); CPX( sx9 + 2, sy9, 'chk')
    CPX( sx9, sy9, 'chk')

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
                CPX( xx, yy, 'bd0')
        for yy in range(y + d, y + h + d):
            xx = x + w - 1 + d
            if onboard(xx, yy) and (xx + yy) % dens == 0:
                CPX( xx, yy, 'bd0')
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
                CPX( xx, yy, 'bd0')

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

obj('Spooks GSの紙')
paper(*PAP_SPOOKS, base='ivory2', hi='ivory', shade='gray0', curl=2)
# 実画像(spooks_gs_paper.jpg)はHTML側で紙の内側に重ねる(ピクセル化しない指示)

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

photo(259, 66, 30, 23, 'b0')                                   # 上段: 写真2枚
EL('furniture', 267, 71, 279, 82, fill='b2', out='b1')         # 写真の中のおばけらしき影
PXL('furniture', 271, 75, 'b5'); PXL('furniture', 275, 75, 'b5')
photo(293, 66, 26, 20, 'q1')
EL('furniture', 299, 70, 310, 79, fill='q4', out='q2')
sticky(259, 93, 17, 14, 'y2', 'ivory', 'y0')                   # 中段: 付箋2枚+写真
sticky(279, 94, 15, 12, 'm4', 'pnkc', 'm2')
photo(297, 92, 24, 21, 'r0')
EL('furniture', 303, 96, 314, 106, fill='r1', out='r2')
for k in range(6):                                             # 下段: 手書きの行
    R('furniture', 259, 118 + k * 3, 32 - (k % 3) * 6, 1, 'gray1')
for k in range(5):                                             # 小さなグラフ
    hgt = (k * 3 + 4) % 11
    R('furniture', 298 + k * 5, 136 - hgt, 3, hgt, 'b3')
    R('furniture', 298 + k * 5, 136 - hgt, 3, 1, 'b4')
R('furniture', 297, 137, 27, 1, 'gray0')
R('furniture', 254, 59, 4, 6, 'gray2')                         # ゼムクリップ
R('furniture', 254, 59, 4, 1, 'wht'); PXL('furniture', 255, 64, 'gray0')

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
# 壁の下端に付く棚。天板(受光)+リップ+前面+壁への落ち影
R('furniture', 47, RAIL_Y, 290, 1, 'wd3')
DITH('furniture', 47, RAIL_Y + 1, 290, 2, 'wd2', 'wd1', 'hline')
R('furniture', 47, RAIL_Y + 3, 290, 1, 'wd0')
R('furniture', 47, RAIL_Y + 4, 290, 1, 'ink')
DITH('bg', 47, RAIL_Y + 5, 290, 2, None, 'q0', 'check')
for kx in range(49, 336, 3):
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
'''
