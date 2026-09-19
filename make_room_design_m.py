# -*- coding: utf-8 -*-
"""スマホ(縦画面)用のデザイン室 room_design_m.png を組み立てる。

方針(スマホ版TOP make_room_m.py と同じ作法):
 ・PC版で描いた紙・模造紙・ガーランド・チョーク受けは、光を当てた後の切り出し
   (room_design_layers/objects/*.png)をそのまま等倍で使う。絵の質を落とさない
 ・縦画面に合わせて「奥壁を正面から見る」構図に組み替える。
   左: 壁一面の黒板(紙を2列に貼る) / 右の壁の帯: 縦長の窓(上)・スタジオの看板と戸口(下)
   床: 板張り(二人が立つ)
 ・黒板・壁・床・窓・戸口は縦横比が違うので、このスクリプトで同じパレットで描き直す
 ・置き場所は DEFAULT。配置ツールが保存した layout.json の "design_m" があればそれで上書き。
   無ければ前回の room_design_m.json(いま公開されている配置)を保つ
 ・チョークの矢印は紙の位置から自動で引く(紙を動かしても矢印がついてくる)
 ・置いた物は全部 PLACED に登録して重なりを調べる。既定の配置で重なれば止める。
   池本さんの配置なら注意だけ出して公開は止めない(はみ出しは中へ寄せる)
 出力: room_design_m.png / room_design_m_bare.png / design_garland_m.png
       / props_dm/*.png / room_design_m.json
"""
import glob
import io
import json
import math
import os
import re
import sys

from PIL import Image, ImageDraw

WEB = os.path.dirname(os.path.abspath(__file__))
OBJ = os.path.join(WEB, "room_design_layers", "objects")
PROPS = os.path.join(WEB, "props_dm")
HAVE_LAYERS = os.path.isdir(OBJ) and not os.environ.get("PATTI_NO_LAYERS")
LAYOUT_PATH = os.environ.get("PATTI_LAYOUT") or os.path.join(WEB, "layout.json")
W, H = 216, 480
PCX0 = 84                                   # PC版(幅384)から横216を切り出すときの左端

P = {
    'ink': (4, 2, 26), 'q0': (22, 9, 58), 'q1': (40, 11, 76), 'q3': (74, 21, 78), 'q4': (81, 35, 80),
    'bd0': (12, 26, 24), 'bd1': (22, 40, 36), 'bd2': (34, 56, 50), 'bd3': (52, 78, 70), 'bd4': (78, 106, 96),
    'bdL': (21, 29, 26), 'bdS': (8, 17, 15),                       # 光の当たった黒板 / 紙の落とす影
    'bdW': (60, 66, 54), 'bdW2': (86, 88, 66),                     # 電球の照り返し(黒板の上のほう)
    'pl0': (68, 62, 56), 'pl1': (104, 96, 86), 'pl2': (138, 128, 114),
    'wd0': (70, 42, 26), 'wd1': (112, 70, 42), 'wd2': (156, 106, 64), 'wd3': (200, 150, 98),
    'fl0': (70, 42, 26), 'fl1': (76, 44, 28), 'fl2': (116, 71, 43), 'fl3': (158, 105, 64), 'flD': (48, 28, 18),
    'chk': (226, 240, 230), 'chk2': (146, 176, 164),
    'gray0': (110, 102, 96), 'gray1': (154, 144, 138), 'gray2': (201, 194, 184), 'wht': (255, 255, 255),
    'lav': (236, 234, 252),
    # 窓の外(PC版の窓と同じ色): 夜空 → 夕やけ → 町
    'sk0': (22, 9, 58), 'sk1': (40, 11, 76), 'sk2': (21, 47, 116), 'sk3': (36, 73, 185), 'sk4': (49, 93, 196),
    'sk5': (96, 136, 224), 'sk6': (101, 86, 163), 'sk7': (252, 125, 103), 'sk8': (253, 176, 140),
    'sk9': (250, 220, 202), 'star': (158, 193, 238), 'brick': (145, 49, 61), 'lamp': (255, 214, 140),
}


def C(c):
    return (P[c] if isinstance(c, str) else tuple(c)) + (255,)


class Canvas(object):
    def __init__(self, img):
        self.im = img
        self.d = ImageDraw.Draw(img)
        self.w, self.h = img.size

    def R(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=C(c))

    def PXL(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.d.point((x, y), fill=C(c))

    def DI(self, x, y, w, h, a, b, ph=0):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.PXL(xx, yy, a if (xx + yy + ph) % 2 == 0 else b)

    def get(self, x, y):
        return self.im.getpixel((x, y))[:3]


room = Canvas(Image.new("RGBA", (W, H), (0, 0, 0, 255)))
R, PXL, DI = room.R, room.PXL, room.DI
im = room.im
PLACED = []


# ═══════════ 部品(PC版の切り出し / 無ければ props_dm から) ═══════════
PARTS_JSON = os.path.join(PROPS, "parts.json")
PARTS = {}
if os.path.exists(PARTS_JSON):
    PARTS = json.load(io.open(PARTS_JSON, encoding="utf-8"))


def pc_rects():
    """PC版の紙の位置(design_content.py の定数)。紙の本体の矩形を知るために使う。"""
    src = io.open(os.path.join(WEB, "design_content.py"), encoding="utf-8").read()
    out = {}
    for k in ("PAP_DESIGN", "PAP_SKETCH", "PAP_STORY", "PAP_SPOOKS", "PAP_WORLD", "PAP_TALE",
              "DATA_TITLE", "DATA_PANEL"):
        m = re.search(r"^%s\s*=\s*\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)" % k, src, re.M)
        assert m, k + " が design_content.py に見つからない"
        out[k] = tuple(int(v) for v in m.groups())
    return out


def _layers(name, layers):
    cv = Image.new("RGBA", (384, 240), (0, 0, 0, 0))
    n = 0
    for lay in layers:                               # 奥の層から順に重ねる
        fs = glob.glob(os.path.join(OBJ, "%s__*_%s.png" % (lay, name)))
        for f in fs:
            cv.alpha_composite(Image.open(f).convert("RGBA"))
            n += 1
    assert n, "部品が見つからない: %s %s" % (layers, name)
    return cv


def part(pid, name, layers, pc_rect=None, crop=None):
    """部品を返す: (絵, 紙の本体の矩形の絵の中での位置 (ox, oy, w, h))。"""
    path = os.path.join(PROPS, pid + ".png")
    if HAVE_LAYERS:
        cv = _layers(name, layers)
        bb = crop or cv.getchannel("A").getbbox()
        sp = cv.crop(bb)
        body = [0, 0, sp.size[0], sp.size[1]]
        if pc_rect:
            body = [pc_rect[0] - bb[0], pc_rect[1] - bb[1], pc_rect[2], pc_rect[3]]
        os.makedirs(PROPS, exist_ok=True)
        sp.save(path)
        PARTS[pid] = body
        return sp, tuple(body)
    if not os.path.exists(path) or pid not in PARTS:
        sys.exit("部品がありません: props_dm/%s.png (room_design_layers のある PC で一度ビルドしてください)" % pid)
    return Image.open(path).convert("RGBA"), tuple(PARTS[pid])


PCR = pc_rects() if HAVE_LAYERS else {}
N_DATA = 'キャラクターに関するデータ'
SPR = {}
SPR['story'] = part('story', 'Story is Kingの紙', ['furniture', 'props'], PCR.get('PAP_STORY'))
SPR['design'] = part('design', 'キャラクターデザインと設計の紙', ['furniture', 'props'], PCR.get('PAP_DESIGN'))
SPR['world'] = part('world', '世界観の紙', ['furniture', 'props'], PCR.get('PAP_WORLD'))
SPR['tale'] = part('tale', '物語の紙', ['furniture', 'props'], PCR.get('PAP_TALE'))
SPR['sketch'] = part('sketch', 'おばけのラフ絵', ['furniture', 'props'], PCR.get('PAP_SKETCH'))
SPR['spooks'] = part('spooks', 'Spooks GSの紙', ['furniture'], PCR.get('PAP_SPOOKS'))
SPR['datatitle'] = part('datatitle', N_DATA, ['bg'], PCR.get('DATA_TITLE'))
SPR['datapanel'] = part('datapanel', N_DATA, ['furniture', 'props'], PCR.get('DATA_PANEL'))
# チョーク受け・チョーク・ガーランドは横216(黒板の幅)に切って使う
TRAY = part('tray', 'チョーク受け', ['bg', 'furniture'])[0]
CHALK = part('chalk', 'チョーク', ['props'])[0]
GAR = part('garland', 'ガーランド', ['furniture'], crop=(PCX0, 0, PCX0 + W, 30))[0]
PAPER_IDS = ['story', 'design', 'world', 'tale', 'sketch', 'spooks', 'datatitle', 'datapanel']


# ═══════════ 置き場所 ═══════════
BOARD = (4, 12, 168, 196)                    # 黒板 x4..171 / y12..207
FLOOR_Y = 216                                # 壁と床の見切り(戸口の足元)
MAYU_W, MAYU_H, PATTI_W, PATTI_H = 30, 72, 32, 48
WALK = 0
DEF_PAPER = {                                # 紙の本体の左上(黒板の上)
    'story': (24, 26),
    'design': (10, 46), 'datatitle': (103, 44), 'datapanel': (94, 60),
    'world': (8, 104),
    'tale': (12, 148), 'sketch': (68, 151), 'spooks': (96, 150),
}
DEFAULT = {}
for k in PAPER_IDS:                           # 配置ツールは絵(ピンやテープこみ)の左上で扱う
    ox, oy = SPR[k][1][:2]
    DEFAULT[k] = (DEF_PAPER[k][0] - ox, DEF_PAPER[k][1] - oy)
DEFAULT.update({'window': (180, 20), 'door': (176, 136), 'mayu': (34, 216), 'patti': (136, 240)})
SCALE = {'mayu': 0.75, 'patti': 0.75}
NAMES = {
    'story': 'Story is King', 'design': 'キャラクターデザイン＆設計', 'world': '世界観', 'tale': '物語',
    'sketch': 'おばけのラフ絵', 'spooks': 'Spooks GS', 'datatitle': 'データまとめ(見出し)',
    'datapanel': 'データの模造紙', 'window': 'まど',
    'door': 'スタジオの看板と戸口（横にだけ動きます）', 'mayu': 'マユちゃん', 'patti': 'パッチ',
}
ORDER = PAPER_IDS + ['window', 'door', 'mayu', 'patti']
LOCK_Y = {'door'}
POS = dict(DEFAULT)
SCALE0 = dict(SCALE)


def _read_items(path, key):
    try:
        v = json.load(io.open(path, encoding="utf-8")).get(key)
    except Exception:
        return None
    if v is not None and not isinstance(v, list):
        print('注意: %s の "%s" が配列ではないので無視します' % (os.path.basename(path), key))
        return None
    return v


_lay, SRC = None, "既定"
if not os.environ.get("PATTI_DEFAULT"):
    _lay = _read_items(LAYOUT_PATH, "design_m")
    SRC = 'layout.json の "design_m"'
    if _lay is None:
        _lay = _read_items(os.path.join(WEB, "room_design_m.json"), "tool")
        SRC = "前回の room_design_m.json(いまの配置のまま)"
if _lay:
    for o in _lay:
        try:
            k = o.get("id")
            if k not in POS:
                continue
            x, y = int(round(float(o["x"]))), int(round(float(o["y"])))
            s_ = None
            if k in SCALE and o.get("s") is not None:
                s_ = max(0.4, min(1.6, float(o["s"])))
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            print("注意: 配置の項目 %r が読めないので既定の位置にします (%s)" % (o, e))
            continue
        if k in LOCK_Y:
            y = DEFAULT[k][1]
        POS[k] = (x, y)
        if s_ is not None:
            SCALE[k] = s_
    print("%s を使う(%d 件)" % (SRC, len(_lay)))
CUSTOM = (POS != DEFAULT) or (SCALE != SCALE0)


# ═══════════ 天井・壁 ═══════════
pcroom = Image.open(os.path.join(WEB, "room_design.png")).convert("RGBA")
im.alpha_composite(pcroom.crop((PCX0, 0, PCX0 + W, 11)), (0, 0))     # 天井の板(PC版の光こみ)
R(0, 11, W, 1, 'ink')
# 漆喰の壁(木造校舎)。上ほど明るく、下の腰壁は板張り
for yy in range(12, FLOOR_Y):
    t = (yy - 12) / float(FLOOR_Y - 12)
    R(0, yy, W, 1, 'pl1' if t < 0.3 else 'pl0')
DI(0, 12, W, 6, 'pl2', 'pl1')
DI(0, 60, W, 10, 'pl1', 'pl0')
WAIN_Y = 118                                  # 腰壁の上端
for x in range(0, W):
    for yy in range(WAIN_Y, FLOOR_Y):
        seam = (x % 7 == 0)
        PXL(x, yy, 'wd0' if seam else ('wd1' if (x // 7) % 3 else 'fl2'))
R(0, WAIN_Y - 2, W, 1, 'ink')
R(0, WAIN_Y - 1, W, 2, 'wd2')                 # 腰壁の笠木
R(0, WAIN_Y + 1, W, 1, 'wd0')
for x in range(3, W, 7):                      # 板の節
    PXL(x, WAIN_Y + 20 + (x * 13) % 60, 'wd0')
# 巾木(壁と床の境目はくっきり)
R(0, FLOOR_Y - 4, W, 1, 'ink')
R(0, FLOOR_Y - 3, W, 2, 'wd1')
R(0, FLOOR_Y - 1, W, 1, 'wd0')


# ═══════════ 床(板張り。手前ほど広がる) ═══════════
R(0, FLOOR_Y, W, H - FLOOR_Y, 'fl0')
R(0, FLOOR_Y, W, 2, 'flD')
SEAMS = [224, 234, 246, 260, 276, 294, 314, 336, 360, 386, 414, 444]
for i, y in enumerate(SEAMS):
    R(0, y, W, 1, 'flD')
    R(0, y + 1, W, 1, 'fl2')
VPX, VPY = W / 2.0, 120.0
for k in range(-5, 6):
    xb = VPX + k * 34
    for yy in range(FLOOR_Y + 2, H):
        t = (yy - VPY) / (H - VPY)
        xx = int(VPX + (xb - VPX) * t + 0.5)
        if 0 <= xx < W and yy not in SEAMS and (yy - 1) not in SEAMS:
            PXL(xx, yy, 'flD')
for bi in range(len(SEAMS) - 1):             # 板ごとの色味
    if bi % 2 == 0:
        for yy in range(SEAMS[bi] + 2, SEAMS[bi + 1]):
            for xx in range(W):
                if (xx + yy * 3 + bi) % 5 == 0:
                    PXL(xx, yy, 'fl1')
for yy in range(FLOOR_Y + 2, H):              # 木目
    for xx in range(W):
        if (xx * 5 + yy * 17) % 97 == 0:
            R(xx, yy, 3, 1, 'fl1')
# 窓からの斜めの光の帯(床の上)
for yy in range(FLOOR_Y + 2, 420):
    t = (yy - FLOOR_Y) / 200.0
    x0 = int(150 - t * 150)
    for xx in range(max(0, x0), min(W, x0 + 26 + int(t * 30))):
        if (xx + yy) % 2 == 0 and not any(s <= yy <= s + 1 for s in SEAMS):
            PXL(xx, yy, 'fl2')
DI(0, 470, W, 10, 'fl0', 'ink')
BARE_FLOOR = im.copy()


# ═══════════ 黒板 ═══════════
bx, by, bw, bh = BOARD
for yy in range(by, by + bh):
    t = (yy - by) / float(bh - 1)
    R(bx, yy, bw, 1, 'bd2' if t < 0.10 else ('bdL' if t < 0.62 else 'bd0'))
DI(bx, by + int(bh * 0.60), bw, 6, 'bdL', 'bd0')
for yy in range(by, by + 26):                 # 電球の照り返し(上ほど暖かい)
    step = 2 + (yy - by) // 5
    for xx in range(bx, bx + bw):
        if (xx + yy * 3) % step == 0:
            PXL(xx, yy, 'bdW2' if yy - by < 6 else 'bdW')
for ax, ay, arx, ary in [(50, 70, 36, 16), (128, 120, 34, 18), (60, 170, 38, 14), (140, 40, 30, 12)]:
    for yy in range(max(by, ay - ary), min(by + bh, ay + ary + 1)):
        for xx in range(max(bx, ax - arx), min(bx + bw, ax + arx + 1)):
            e = ((xx - ax) / float(arx)) ** 2 + ((yy - ay) / float(ary)) ** 2
            if 0.58 < e < 1.0 and (xx * 3 + yy * 5) % 4 == 0:
                PXL(xx, yy, 'bd2')
            elif e <= 0.58 and (xx + yy * 2) % 9 == 0:
                PXL(xx, yy, 'bd2')
for yy in range(by + bh - 16, by + bh):       # 下にたまったチョークの粉
    d = (yy - (by + bh - 16)) / 15.0
    step = max(2, int(16 - d * 13))
    for xx in range(bx, bx + bw):
        if (xx * 7 + yy * 11) % step == 0:
            PXL(xx, yy, 'bd3')
for sx, sy, sl in [(140, 204, 8), (96, 42, 6), (6, 186, 7), (120, 186, 9)]:   # 紙や矢印のそばは避ける
    for k in range(sl):
        PXL(sx + k, sy - k // 3, 'bd3')
R(bx, by, bw, 1, 'bd3')                       # 天井との見切り
R(bx - 1, by, 1, bh, 'ink'); R(bx + bw, by, 1, bh, 'ink')
R(bx - 2, by, 1, bh, 'wd0'); R(bx + bw + 1, by, 1, bh, 'wd0')
BOARD_ONLY = im.copy()


# ═══════════ 右の壁: 縦長の窓(夕やけの町) ═══════════
WIN_W, WIN_H = 32, 88


def window_img():
    u = Canvas(Image.new("RGBA", (WIN_W, WIN_H), (0, 0, 0, 0)))
    gx0, gy0, gw, gh = 3, 3, WIN_W - 6, WIN_H - 9          # ガラスの内側
    bands = [('sk0', 0.00), ('sk1', 0.10), ('sk2', 0.20), ('sk3', 0.32), ('sk4', 0.44),
             ('sk5', 0.54), ('sk6', 0.62), ('sk7', 0.70), ('sk8', 0.78), ('sk9', 0.84)]
    for yy in range(gh):
        t = yy / float(gh - 1)
        cur = bands[0][0]
        nxt = None
        for i, (c, t0) in enumerate(bands):
            if t >= t0:
                cur = c
                nxt = bands[i + 1] if i + 1 < len(bands) else None
        for xx in range(gw):
            c = cur
            if nxt and t > nxt[1] - 0.03 and (xx + yy) % 2 == 0:
                c = nxt[0]                                    # 帯の境目はディザでなじませる
            u.PXL(gx0 + xx, gy0 + yy, c)
    for sx, sy in ((6, 6), (19, 4), (24, 12), (10, 16), (4, 24), (22, 22)):
        u.PXL(gx0 + sx, gy0 + sy, 'star')
    # 町のシルエット(明かりのついた窓)
    sky_h = gh
    for xx in range(gw):                                      # 地平線のあかり
        u.PXL(gx0 + xx, gy0 + sky_h - 13, 'sk9')
    tops = [5, 5, 8, 8, 8, 4, 4, 11, 11, 11, 6, 6, 6, 9, 9, 3, 3, 7, 7, 7, 10, 10, 5, 5, 8, 8]
    blk = 0
    for xx in range(gw):
        h9 = tops[xx % len(tops)]
        if xx > 0 and tops[xx % len(tops)] != tops[(xx - 1) % len(tops)]:
            blk += 1
        for yy in range(sky_h - h9, sky_h):
            u.PXL(gx0 + xx, gy0 + yy, 'q0' if blk % 2 else 'ink')
    for cx9, r9 in ((1, 4), (25, 5)):                         # 木のかたまり
        for yy in range(-r9, r9 + 1):
            for xx in range(-r9, r9 + 1):
                if xx * xx + yy * yy <= r9 * r9 and 0 <= cx9 + xx < gw:
                    u.PXL(gx0 + cx9 + xx, gy0 + sky_h - 4 + yy, 'bd0')
    for lx, ly in ((8, 9), (9, 6), (13, 4), (18, 5), (21, 8), (4, 3), (14, 8), (22, 5)):
        if lx < gw:
            u.PXL(gx0 + lx, gy0 + sky_h - ly, 'lamp')
    # 木の窓枠と桟
    u.R(0, 0, WIN_W, 1, 'ink'); u.R(0, WIN_H - 6, WIN_W, 1, 'ink')
    u.R(0, 0, 1, WIN_H - 5, 'ink'); u.R(WIN_W - 1, 0, 1, WIN_H - 5, 'ink')
    u.R(1, 1, WIN_W - 2, 2, 'wd1'); u.R(1, 1, 2, WIN_H - 7, 'wd1')
    u.R(WIN_W - 3, 1, 2, WIN_H - 7, 'wd0'); u.R(1, WIN_H - 8, WIN_W - 2, 2, 'wd0')
    u.R(1, 1, WIN_W - 2, 1, 'wd2')
    cx = WIN_W // 2
    u.R(cx - 1, 1, 2, WIN_H - 7, 'wd1'); u.R(cx, 1, 1, WIN_H - 7, 'wd0')
    for my in (30, 58):
        u.R(1, my, WIN_W - 2, 2, 'wd1'); u.R(1, my + 1, WIN_W - 2, 1, 'wd0')
    u.R(0, WIN_H - 5, WIN_W, 3, 'wd2')                       # 窓台
    u.R(0, WIN_H - 5, WIN_W, 1, 'wd3')
    u.R(0, WIN_H - 2, WIN_W, 1, 'wd0'); u.R(1, WIN_H - 1, WIN_W - 2, 1, 'ink')
    return u.im


# ═══════════ 右の壁: スタジオの看板と戸口(白い光がもれる) ═══════════
DOOR_W, DOOR_H = 40, 80
DOOR_OPEN = (8, 20, 24, 58)                                  # 部品の中での開口


def door_img():
    u = Canvas(Image.new("RGBA", (DOOR_W, DOOR_H), (0, 0, 0, 0)))
    # 看板(TOPの看板と同じ作り。文字は PC 版と同じ sign_studio_s.png)
    sw_, sh_ = 40, 15
    u.R(0, 0, sw_, sh_, 'q0')
    u.R(0, 0, sw_, 1, 'gray2'); u.R(0, 0, 1, sh_, 'gray2')
    u.R(0, sh_ - 1, sw_, 1, 'ink'); u.R(sw_ - 1, 0, 1, sh_, 'ink')
    u.R(1, sh_ - 2, sw_ - 2, 1, 'gray0')
    t = Image.open(os.path.join(WEB, "sign_studio_s.png")).convert("RGBA")
    white = Image.new("RGBA", t.size, (255, 255, 255, 255))
    white.putalpha(t.getchannel("A"))
    u.im.alpha_composite(white, ((sw_ - t.size[0]) // 2, (sh_ - t.size[1]) // 2))
    # 戸口
    x, y, w, h = DOOR_OPEN
    u.R(x - 3, y - 3, w + 6, h + 4, 'wd0')                   # 木の枠
    u.R(x - 2, y - 2, w + 4, h + 2, 'wd1')
    u.R(x - 2, y - 2, w + 4, 1, 'wd2'); u.R(x - 2, y - 2, 1, h + 2, 'wd2')
    u.R(x - 3, y - 4, w + 6, 1, 'ink')
    for yy in range(y, y + h):
        rel = (yy - y) / float(h)
        for xx in range(x, x + w):
            if rel < 0.10:
                c = 'gray0' if (xx + yy) % 2 else 'q4'
            elif rel < 0.34:
                c = 'gray0' if (xx + yy) % 2 else 'gray1'
            elif rel < 0.62:
                c = 'gray1' if (xx + yy) % 2 else 'gray2'
            elif rel < 0.86:
                c = 'gray2'
            else:
                c = 'wht' if (xx + yy) % 2 else 'gray2'
            u.PXL(xx, yy, c)
    for k in range(4):                                        # 奥の廊下の明かりが縦に差す
        u.R(x + 4 + k * 5, y + 4 + k, 1, h - 8 - k * 4, 'gray2' if k % 2 else 'gray1')
    u.R(x - 3, y + h, w + 6, 1, 'wd2')                        # 敷居
    u.R(x - 3, y + h + 1, w + 6, 1, 'ink')
    return u.im


WIN = window_img()
DOOR = door_img()
os.makedirs(PROPS, exist_ok=True)
WIN.save(os.path.join(PROPS, "window.png"))
DOOR.save(os.path.join(PROPS, "door.png"))
SIZES = {k: SPR[k][0].size for k in PAPER_IDS}
SIZES.update({'window': WIN.size, 'door': DOOR.size, 'mayu': (MAYU_W, MAYU_H), 'patti': (PATTI_W, PATTI_H)})
assert DEFAULT['door'][1] + DOOR_OPEN[1] + DOOR_OPEN[3] + 2 == FLOOR_Y, "戸口の敷居が床の見切りに乗っていない"


# ═══════════ はみ出しを中へ寄せる(紙は黒板の中、ほかは画面の中) ═══════════
def paper_rect(k):
    ox, oy, pw, ph = SPR[k][1]
    return (POS[k][0] + ox, POS[k][1] + oy, pw, ph)


for k in ORDER:
    w_, h_ = SIZES[k]
    x_, y_ = POS[k]
    if k in PAPER_IDS:                                        # 紙の本体が黒板の内側に収まるように
        ox, oy, pw, ph = SPR[k][1]
        nx = min(max(x_, bx + 2 - ox), bx + bw - 2 - pw - ox)
        ny = min(max(y_, by + 2 - oy), by + bh - 6 - ph - oy)
    elif k in SCALE:
        s_ = SCALE[k]
        ox, oy = w_ * (1 - s_) / 2.0, h_ * (1 - s_)
        nx = int(min(max(x_, math.ceil(-ox)), math.floor(W - w_ * s_ - ox)))
        ny = int(min(max(y_, math.ceil(-oy)), math.floor(H - h_ * s_ - oy)))
    else:
        nx, ny = min(max(x_, 0), W - w_), min(max(y_, 0), H - h_)
    if k in LOCK_Y:
        ny = y_
    if (nx, ny) != (x_, y_):
        print("注意: %s が%sからはみ出すので (%d,%d) に寄せました"
              % (NAMES[k], "黒板" if k in PAPER_IDS else "画面", nx, ny))
        POS[k] = (nx, ny)

PAPER_RECTS = {k: paper_rect(k) for k in PAPER_IDS}


# ═══════════ 紙の影 → チョーク → 紙 ═══════════
for k in PAPER_IDS:
    if k == 'datatitle':
        continue                                              # 見出しはチョーク書きなので影は無い
    x, y, w, h = PAPER_RECTS[k]
    for yy in range(y + 2, y + h + 2):
        for xx in range(x + 2, x + w + 2):
            if (xx >= x + w or yy >= y + h) and bx <= xx < bx + bw and by <= yy < by + bh:
                PXL(xx, yy, 'bdS')

_cn = [0]


def chalk_free(x, y, pad=4):
    if not (bx + 2 <= x < bx + bw - 2 and by + 2 <= y < by + bh - 2):
        return False
    for (rx, ry, rw, rh) in PAPER_RECTS.values():
        if rx - pad <= x < rx + rw + pad and ry - pad <= y < ry + rh + pad:
            return False
    return True


def CPX(x, y, c, pad=4):
    if chalk_free(x, y, pad):
        PXL(x, y, c)


def chalk_line(pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for k in range(steps + 1):
            t = k / float(steps) if steps else 0.0
            xx = int(round(x0 + (x1 - x0) * t)); yy = int(round(y0 + (y1 - y0) * t))
            _cn[0] += 1
            if _cn[0] % 5 == 4:
                continue
            CPX(xx, yy, 'chk' if _cn[0] % 3 else 'chk2')


def chalk_arrow(a, b):
    """紙 a から紙 b へ、チョークの矢印を引く(紙のすき間だけ。短すぎれば引かない)。
    軸は2本重ねて太く、矢じりは軸と同じ幅の三角形(細いと矢印に見えない)。"""
    ax, ay, aw, ah = PAPER_RECTS[a]
    bx_, by_, bw_, bh_ = PAPER_RECTS[b]
    if by_ >= ay + ah + 12:                                    # b が下
        lo, hi = max(ax, bx_), min(ax + aw, bx_ + bw_)
        x = (lo + hi) // 2 if hi - lo >= 8 else (ax + aw // 2 + bx_ + bw_ // 2) // 2
        y0, tip = ay + ah + 3, by_ - 4
        if tip - y0 < 8:
            return False
        for k in range(y0, tip - 3):
            if (k - y0) % 5 != 4:                             # かすれ
                CPX(x, k, 'chk' if k % 3 else 'chk2', 1); CPX(x + 1, k, 'chk', 1)
        for r in range(4):                                     # 矢じり(下向き)
            for m in range(-r, r + 2):
                CPX(x + m, tip - r, 'chk', 1)
        return True
    if bx_ >= ax + aw + 12:                                    # b が右
        lo, hi = max(ay, by_), min(ay + ah, by_ + bh_)
        y = (lo + hi) // 2 if hi - lo >= 6 else (ay + ah // 2 + by_ + bh_ // 2) // 2
        x0, tip = ax + aw + 3, bx_ - 4
        if tip - x0 < 8:
            return False
        for k in range(x0, tip - 3):
            if (k - x0) % 5 != 4:
                CPX(k, y, 'chk' if k % 3 else 'chk2', 1); CPX(k, y + 1, 'chk', 1)
        for r in range(4):                                     # 矢じり(右向き)
            for m in range(-r, r + 2):
                CPX(tip - r, y + m, 'chk', 1)
        return True
    return False


ARROWS = [('design', 'world'), ('world', 'tale')]
ARROW_OK = {"%s>%s" % ab: chalk_arrow(*ab) for ab in ARROWS}


def chalk_circle(cx9, cy9, r9, dense=3):
    n9 = max(12, int(r9 * 6))
    for k in range(n9):
        if k % dense == 0:
            continue
        a9 = k * 2 * math.pi / n9
        CPX(int(cx9 + math.cos(a9) * r9 + 0.5), int(cy9 + math.sin(a9) * r9 * 0.92 + 0.5), 'chk2')


def chalk_write(x9, y9, rows, wmax):
    for r9 in range(rows):
        yy = y9 + r9 * 4
        ln = wmax - (r9 * 7) % (wmax // 2)
        xx = x9
        while xx < x9 + ln:
            seg = 2 + (xx * 3 + r9) % 4
            for k in range(seg):
                if xx + k < x9 + ln:
                    CPX(xx + k, yy, 'chk2')
            xx += seg + 2


def chalk_ghost(gx9, gy9, r9=5):
    for a9 in range(180, 361, 12):
        CPX(int(gx9 + math.cos(math.radians(a9)) * r9), int(gy9 + math.sin(math.radians(a9)) * r9), 'chk2')
    for dx9 in range(-r9, r9 + 1):
        if (dx9 + r9) % 3 != 1:
            CPX(gx9 + dx9, gy9 + r9 - abs(dx9) % 2, 'chk2')
    CPX(gx9 - 2, gy9 - 1, 'chk'); CPX(gx9 + 2, gy9 - 1, 'chk')


def chalk_star(sx9, sy9):
    for ddx, ddy in ((0, -2), (0, 2), (-2, 0), (2, 0), (0, 0)):
        CPX(sx9 + ddx, sy9 + ddy, 'chk')


# 落書き(紙のない所だけに描かれる。紙を動かしても紙の下にはもぐらない)
chalk_circle(38, 195, 8); chalk_circle(38, 195, 5, 4)
for k in range(-6, 7):
    if k % 3:
        CPX(38 + k, 195, 'chk2'); CPX(38, 195 + k, 'chk2')
chalk_write(60, 190, 3, 40)
chalk_write(112, 192, 2, 44)
chalk_ghost(160, 30)
for sx9, sy9 in ((14, 30), (158, 200)):
    chalk_star(sx9, sy9)

# 紙を貼る
for k in PAPER_IDS:
    sp = SPR[k][0]
    im.alpha_composite(sp, POS[k])
    PLACED.append((k, ) + PAPER_RECTS[k])

# チョーク受けとチョーク(黒板の幅に合わせて切る)
tw = TRAY.size[0]
tray = TRAY.crop(((tw - bw) // 2, 0, (tw - bw) // 2 + bw, TRAY.size[1]))
im.alpha_composite(tray, (bx, by + bh))
im.alpha_composite(CHALK, (bx + 34, by + bh - 2))

# ガーランド(黒板の上にかかる)。またたきのコマも同じ所で切る
im.alpha_composite(GAR, (0, 0))
gb = Image.open(os.path.join(WEB, "design_garland.png")).convert("RGBA")
GB_H = gb.size[1]
gm = Image.new("RGBA", (W * 3, GB_H), (0, 0, 0, 0))
for f in range(3):
    gm.alpha_composite(gb.crop((f * 384 + PCX0, 0, f * 384 + PCX0 + W, GB_H)), (f * W, 0))
gm.save(os.path.join(WEB, "design_garland_m.png"))
GARLAND_Y = 8
BARE = BOARD_ONLY.copy()
BARE.alpha_composite(GAR, (0, 0))

# 窓・戸口
im.alpha_composite(WIN, POS['window'])
PLACED.append(('window', POS['window'][0], POS['window'][1], WIN_W, WIN_H))
dx0, dy0 = POS['door']
im.alpha_composite(DOOR, (dx0, dy0))
PLACED.append(('door:看板', dx0, dy0, 40, 15))
PLACED.append(('door:戸口', dx0 + DOOR_OPEN[0] - 3, dy0 + DOOR_OPEN[1] - 4, DOOR_OPEN[2] + 6, DOOR_OPEN[3] + 6))
DOOR_HOT = (dx0 + DOOR_OPEN[0], dy0 + DOOR_OPEN[1], DOOR_OPEN[2], DOOR_OPEN[3])
# 黒板そのもの(窓と戸口は黒板にかぶってはいけない)
PLACED.append(('黒板', bx - 2, by, bw + 4, bh + 5))

# 戸口の光の床へのこぼれ(白)
for yy in range(FLOOR_Y, FLOOR_Y + 22):
    t = (yy - FLOOR_Y) / 22.0
    half = int(DOOR_OPEN[2] / 2 + t * 14)
    cx = DOOR_HOT[0] + DOOR_HOT[2] // 2
    for xx in range(cx - half, cx + half):
        if 0 <= xx < W and (xx + yy) % (2 if t < 0.5 else 3) == 0 and not any(s <= yy <= s + 1 for s in SEAMS):
            PXL(xx, yy, 'fl3')


# ═══════════ 二人(HTML側が置く)。重なり検査のために登録だけする ═══════════
def chara_box(key, w, h):
    x, y = POS[key]; s = SCALE[key]
    return (x + w * (1 - s) / 2.0, y + h * (1 - s), w * s, h * s)


mb = chara_box('mayu', MAYU_W, MAYU_H)
pb = chara_box('patti', PATTI_W, PATTI_H)
PLACED.append(('mayu', int(mb[0]), int(mb[1]), int(round(mb[2])), int(round(mb[3]))))
PLACED.append(('patti', int(pb[0]), int(pb[1]), int(round(pb[2])), int(round(pb[3]))))
FEET = [POS['mayu'][1] + MAYU_H, POS['patti'][1] + PATTI_H]
GROUND = max(288, max(FEET))


# ═══════════ 重なり検査 ═══════════
def isect(a, b):
    return (min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]), min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2]))


ALLOWED = {frozenset(('door:看板', 'door:戸口'))}
bad = []
for i in range(len(PLACED)):
    for j in range(i + 1, len(PLACED)):
        a, b = PLACED[i], PLACED[j]
        if '黒板' in (a[0], b[0]) and (a[0] in PAPER_IDS or b[0] in PAPER_IDS):
            continue                                          # 紙は黒板の上に貼るもの
        if '黒板' in (a[0], b[0]) and ({a[0], b[0]} & {'mayu', 'patti'}):
            continue                                          # 二人は黒板の手前に立つ
        ow, oh = isect(a, b)
        if ow > 0 and oh > 0 and frozenset((a[0], b[0])) not in ALLOWED:
            bad.append("%s x %s (%dx%d)" % (a[0], b[0], ow, oh))
for k, ok in ARROW_OK.items():
    if not ok:
        bad.append("チョークの矢印 %s が引けない(紙どうしが近すぎるか、並びが上下左右でない)" % k)
if bad:
    if CUSTOM:
        print("注意(池本さんの配置で重なっている所):\n  " + "\n  ".join(bad))
    else:
        raise SystemExit("重なり事故:\n  " + "\n  ".join(bad))


# ═══════════ ビネット ═══════════
def vignette(img):
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            dx = abs(xx - W / 2.0) / (W / 2.0)
            dy = abs(yy - 190.0) / 210.0
            dd = (dx ** 2.3 + dy ** 2.3) ** 0.5
            n = 2 if dd > 1.06 else (1 if dd > 0.93 else (1 if dd > 0.84 and (xx + yy) % 2 == 0 else 0))
            if n:
                r, g_, b, a = px[xx, yy]
                k = 0.88 if n == 1 else 0.76
                px[xx, yy] = (int(r * k), int(g_ * k), int(b * k), a)


vignette(im)
vignette(BARE)
im.convert("RGB").save(os.path.join(WEB, "room_design_m.png"))
# 配置ツール用: 紙・窓・戸口の無い部屋(床と壁は描き込み済み)
bare = BARE_FLOOR.copy()
bare.alpha_composite(BARE.crop((0, 0, W, by + bh)), (0, 0))
bare.alpha_composite(tray, (bx, by + bh))
vignette(bare)
bare.convert("RGB").save(os.path.join(WEB, "room_design_m_bare.png"))
json.dump(PARTS, io.open(PARTS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ═══════════ 書き出し(HTML と配置ツールが読む) ═══════════
IMG = {'mayu': 'mayu_right_shaded.png', 'patti': 'patti_right_shaded.png'}
tool = []
for k in ORDER:
    o = {"id": k, "name": NAMES[k], "x": POS[k][0], "y": POS[k][1],
         "x0": DEFAULT[k][0], "y0": DEFAULT[k][1],
         "w": SIZES[k][0], "h": SIZES[k][1], "img": IMG.get(k, "props_dm/%s.png" % k)}
    if k in SCALE:
        o["chara"] = True; o["s"] = SCALE[k]; o["s0"] = SCALE0[k]
    if k in LOCK_Y:
        o["lockY"] = True
    if k in PAPER_IDS:
        o["inBoard"] = True
    tool.append(o)
meta = {
    "w": W, "h": H, "ground": GROUND, "garland_y": GARLAND_Y, "garland_h": GB_H,
    "board": list(BOARD), "floor": FLOOR_Y,
    "papers": {k: list(v) for k, v in PAPER_RECTS.items()},
    "door": list(DOOR_HOT), "window": [POS['window'][0], POS['window'][1], WIN_W, WIN_H],
    "mayu": [POS['mayu'][0], POS['mayu'][1], SCALE['mayu']],
    "patti": [POS['patti'][0], POS['patti'][1], SCALE['patti']],
    "placed": [list(p) for p in PLACED],
    "custom": CUSTOM, "tool": tool,
}
json.dump(meta, io.open(os.path.join(WEB, "room_design_m.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("room_design_m.png", im.size, "/ room_design_m_bare.png / design_garland_m.png / props_dm / room_design_m.json",
      "(重なり %d 件)" % len(bad))
