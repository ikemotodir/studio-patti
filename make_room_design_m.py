# -*- coding: utf-8 -*-
"""スマホ(縦画面)用のデザイン室を組み立てる。画面の高さに合わせて伸び縮みする作り。

方針(スマホ版TOP make_room_m.py と同じ作法 + 伸び縮み):
 ・PC版で描いた紙・模造紙・ガーランド・チョーク受けは、光を当てた後の切り出し
   (room_design_layers/objects/*.png)をそのまま等倍で使う。絵の質を落とさない
 ・基準は「背の高い画面」(池本さんの指示の絵): 黒板は上から床の線 F=312 まで。データまとめは黒板の下1/3、
   ほかの紙は上2/3。二人とトビラは黒板の下の床
 ・画面が短いときは床の線 F が上がる。床・トビラ・二人・データまとめ・黒板の下の方は「下のかたまり」
   (design_m_lower.png)としていっしょに上がり、上の紙は間隔が詰まる(詰めた位置 yc はここで計算)。
   どの高さでも横いっぱいで、二人はテキストボックスに被らない(計算はページ側 design_m.html)
 ・チョークの矢印は紙の位置からページ側で引く(紙が動いても矢印がついてくる)
 ・置き場所は DEFAULT。配置ツールが保存した layout.json の "design_m" があればそれで上書き。
   無ければ前回の room_design_m.json(いま公開されている配置)を保つ
 ・重なりは「背の高い画面」と「いちばん短い画面」の両方で調べる。既定の配置で重なれば止める。
   池本さんの配置なら注意だけ出して公開は止めない(はみ出しは中へ寄せる)
 出力: room_design_m.png(壁・黒板・窓) / design_m_lower.png(下のかたまり) / room_design_m_bare.png(配置ツール用)
       / design_garland_m.png / props_dm/*.png / room_design_m.json
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


# ═══════════ 置き場所(基準 = 背の高い画面。池本さんの指示の絵) ═══════════
# 画面が短いときは、床の線 F が上がる(床・トビラ・二人・データまとめ・黒板の下の方がいっしょに上がる)。
# 上の紙は「詰めた位置」と「基準の位置」の間を、F に合わせて補間する(ページ側で計算)。
BOARD_X, BOARD_W, BOARD_TOP = 4, 168, 12      # 黒板の石板 x4..171 / y12..(F-8)
F_REF = 312                                   # 基準の床の線(黒板の下のふち・トビラの足元)
TRAY_H = 8                                    # チョーク受け(F-8..F-1)
MAYU_W, MAYU_H, PATTI_W, PATTI_H = 30, 72, 32, 48
TOP_PAPERS = ['story', 'sketch', 'design', 'spooks', 'world', 'tale']   # 上の2/3(画面に合わせて間隔が伸び縮み)
FLOOR_PAPERS = ['datatitle', 'datapanel']                                 # 下の1/3(床といっしょに上下)
UP_LIMIT = 26                                 # 上の紙はこれより上へは寄せない(電球の下)
ARROWS = [('design', 'world'), ('world', 'tale')]
DEF_PAPER = {                                 # 紙の本体の左上(基準)
    'story': (12, 26), 'sketch': (146, 26),
    'design': (6, 66), 'spooks': (96, 74),
    'world': (6, 150), 'tale': (104, 146),
    'datatitle': (60, F_REF - 106), 'datapanel': (51, F_REF - 91),
}
DOOR_W, DOOR_H = 40, 92
DOOR_OPEN = (6, 20, 28, 70)                   # 部品の中での開口(看板の下)
DEFAULT = {}
for k in PAPER_IDS:                           # 配置ツールは絵(ピンやテープこみ)の左上で扱う
    ox, oy = SPR[k][1][:2]
    DEFAULT[k] = (DEF_PAPER[k][0] - ox, DEF_PAPER[k][1] - oy)
DEFAULT.update({'window': (180, 20), 'door': (176, F_REF - DOOR_H),
                'mayu': (39, F_REF + 60 - MAYU_H), 'patti': (134, F_REF + 60 - PATTI_H)})
SCALE = {'mayu': 0.75, 'patti': 0.75}
NAMES = {
    'story': 'Story is King', 'design': 'キャラクターデザイン＆設計', 'world': '世界観', 'tale': '物語',
    'sketch': 'おばけのラフ絵', 'spooks': 'Spooks GS', 'datatitle': 'データまとめ(見出し)',
    'datapanel': 'データの模造紙', 'window': 'まど',
    'door': 'スタジオの看板とトビラ（横にだけ動きます）', 'mayu': 'マユちゃん', 'patti': 'パッチ',
}
ORDER = PAPER_IDS + ['window', 'door', 'mayu', 'patti']
LOCK_Y = {'door'}
FLOOR_ANCHOR = set(FLOOR_PAPERS) | {'door', 'mayu', 'patti'}
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
        try:                                  # 作りを変える前の古い一覧は使わない(基準の高さが違う)
            if json.load(io.open(os.path.join(WEB, "room_design_m.json"), encoding="utf-8")).get("F_ref") != F_REF:
                _lay, SRC = None, "既定(前回の配置は作りが古いので使わない)"
        except Exception:
            pass
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
print("%s を使う" % SRC)
CUSTOM = (POS != DEFAULT) or (SCALE != SCALE0)


# ═══════════ 部品の絵(窓・トビラ) ═══════════
WIN_W, WIN_H = 32, 88


def window_img():
    u = Canvas(Image.new("RGBA", (WIN_W, WIN_H), (0, 0, 0, 0)))
    gx0, gy0, gw, gh = 3, 3, WIN_W - 6, WIN_H - 9          # ガラスの内側
    bands = [('sk0', 0.00), ('sk1', 0.10), ('sk2', 0.20), ('sk3', 0.32), ('sk4', 0.44),
             ('sk5', 0.54), ('sk6', 0.62), ('sk7', 0.70), ('sk8', 0.78), ('sk9', 0.84)]
    for yy in range(gh):
        t = yy / float(gh - 1)
        cur, nxt = bands[0][0], None
        for i, (c, t0) in enumerate(bands):
            if t >= t0:
                cur = c
                nxt = bands[i + 1] if i + 1 < len(bands) else None
        for xx in range(gw):
            c = cur
            if nxt and t > nxt[1] - 0.03 and (xx + yy) % 2 == 0:
                c = nxt[0]
            u.PXL(gx0 + xx, gy0 + yy, c)
    for sx, sy in ((6, 6), (19, 4), (24, 12), (10, 16), (4, 24), (22, 22)):
        u.PXL(gx0 + sx, gy0 + sy, 'star')
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
    u.R(0, 0, WIN_W, 1, 'ink'); u.R(0, WIN_H - 6, WIN_W, 1, 'ink')
    u.R(0, 0, 1, WIN_H - 5, 'ink'); u.R(WIN_W - 1, 0, 1, WIN_H - 5, 'ink')
    u.R(1, 1, WIN_W - 2, 2, 'wd1'); u.R(1, 1, 2, WIN_H - 7, 'wd1')
    u.R(WIN_W - 3, 1, 2, WIN_H - 7, 'wd0'); u.R(1, WIN_H - 8, WIN_W - 2, 2, 'wd0')
    u.R(1, 1, WIN_W - 2, 1, 'wd2')
    cx = WIN_W // 2
    u.R(cx - 1, 1, 2, WIN_H - 7, 'wd1'); u.R(cx, 1, 1, WIN_H - 7, 'wd0')
    for my in (30, 58):
        u.R(1, my, WIN_W - 2, 2, 'wd1'); u.R(1, my + 1, WIN_W - 2, 1, 'wd0')
    u.R(0, WIN_H - 5, WIN_W, 3, 'wd2')
    u.R(0, WIN_H - 5, WIN_W, 1, 'wd3')
    u.R(0, WIN_H - 2, WIN_W, 1, 'wd0'); u.R(1, WIN_H - 1, WIN_W - 2, 1, 'ink')
    return u.im


def door_img():
    """看板(上)とトビラ(下)を1つの部品に。トビラの足元が部品の下端=床の線。"""
    u = Canvas(Image.new("RGBA", (DOOR_W, DOOR_H), (0, 0, 0, 0)))
    sw_, sh_ = 40, 15
    u.R(0, 0, sw_, sh_, 'q0')
    u.R(0, 0, sw_, 1, 'gray2'); u.R(0, 0, 1, sh_, 'gray2')
    u.R(0, sh_ - 1, sw_, 1, 'ink'); u.R(sw_ - 1, 0, 1, sh_, 'ink')
    u.R(1, sh_ - 2, sw_ - 2, 1, 'gray0')
    t = Image.open(os.path.join(WEB, "sign_studio_s.png")).convert("RGBA")
    white = Image.new("RGBA", t.size, (255, 255, 255, 255))
    white.putalpha(t.getchannel("A"))
    u.im.alpha_composite(white, ((sw_ - t.size[0]) // 2, (sh_ - t.size[1]) // 2))
    x, y, w, h = DOOR_OPEN
    u.R(x - 3, y - 3, w + 6, h + 3, 'wd0')                   # 木の枠
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
    for k in range(5):                                        # 奥の廊下の明かりが縦に差す
        u.R(x + 3 + k * 5, y + 4 + k, 1, h - 8 - k * 4, 'gray2' if k % 2 else 'gray1')
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


# ═══════════ はみ出しを中へ寄せる(紙は黒板の中、ほかは画面の中。いずれも基準の高さで) ═══════════
def body(k, pos=None):
    ox, oy, pw, ph = SPR[k][1]
    x, y = pos or POS[k]
    return (x + ox, y + oy, pw, ph)


for k in ORDER:
    w_, h_ = SIZES[k]
    x_, y_ = POS[k]
    if k in PAPER_IDS:
        ox, oy, pw, ph = SPR[k][1]
        nx = min(max(x_, BOARD_X + 2 - ox), BOARD_X + BOARD_W - 2 - pw - ox)
        ny = min(max(y_, BOARD_TOP + 2 - oy), F_REF - TRAY_H - 3 - ph - oy)
    elif k in SCALE:
        s_ = SCALE[k]
        ox, oy = w_ * (1 - s_) / 2.0, h_ * (1 - s_)
        nx = int(min(max(x_, math.ceil(-ox)), math.floor(W - w_ * s_ - ox)))
        ny = int(min(max(y_, F_REF + 2 - h_), math.floor(H - h_ * s_ - oy)))   # 足元は床の上
    else:
        nx, ny = min(max(x_, 0), W - w_), min(max(y_, 0), H - h_)
    if k in LOCK_Y:
        ny = y_
    if (nx, ny) != (x_, y_):
        print("注意: %s が%sからはみ出すので (%d,%d) に寄せました"
              % (NAMES[k], "黒板" if k in PAPER_IDS else "画面", nx, ny))
        POS[k] = (nx, ny)


# ═══════════ 画面が短いときの「詰めた位置」(上の紙を上へ寄せる) ═══════════
def xover(a, b, m=2):
    return a[0] < b[0] + b[2] + m and b[0] < a[0] + a[2] + m


REF_B = {k: body(k) for k in PAPER_IDS}
order = sorted(TOP_PAPERS, key=lambda k: (REF_B[k][1], REF_B[k][0]))
CMP_Y = {}
for k in order:
    bx_, by_, bw_, bh_ = REF_B[k]
    y = min(by_, UP_LIMIT) if by_ >= UP_LIMIT else by_
    for a in CMP_Y:
        if REF_B[a][1] < by_ and xover(REF_B[a], REF_B[k]):
            gap = 15 if (a, k) in ARROWS else 4
            y = max(y, CMP_Y[a] + REF_B[a][3] + gap)
    CMP_Y[k] = min(y, by_)
for a, b in ARROWS:                               # 横の矢印の2枚は、上下が6以上重なるように(矢印が引ける)
    ra, rb = REF_B[a], REF_B[b]
    if rb[0] >= ra[0] + ra[2]:
        need = min(6, min(ra[3], rb[3]))
        ov = min(CMP_Y[a] + ra[3], CMP_Y[b] + rb[3]) - max(CMP_Y[a], CMP_Y[b])
        if ov < need:                                 # 上にある方を、足りない分だけ下げる
            if CMP_Y[a] < CMP_Y[b]:
                CMP_Y[a] = min(ra[1], CMP_Y[a] + (need - ov))
            else:
                CMP_Y[b] = min(rb[1], CMP_Y[b] + (need - ov))
CMP_END = max(CMP_Y[k] + REF_B[k][3] for k in TOP_PAPERS)

# 下のかたまり(黒板の下の方〜床)の上端は、床側の紙の一番上より少し上
FLOOR_TOP_REF = min(REF_B[k][1] for k in FLOOR_PAPERS)
LB_OFF = F_REF - (FLOOR_TOP_REF - 2)              # 下のかたまりの上端 = F - LB_OFF
# いちばん短い画面の F: 上の紙(詰めた位置)の下に、床側の紙が重ならない高さ
F_MIN = CMP_END + 3 + (F_REF - FLOOR_TOP_REF)
F_MIN = min(F_MIN, F_REF)
# 二人: 奥行き(床の線から足元まで)。短い画面では頭が床の線に届くまで詰められる
def chara_box(key, pos=None):
    x, y = pos or POS[key]; s = SCALE[key]
    w, h = (MAYU_W, MAYU_H) if key == 'mayu' else (PATTI_W, PATTI_H)
    return (x + w * (1 - s) / 2.0, y + h * (1 - s), w * s, h * s)


FEET = max(POS['mayu'][1] + MAYU_H, POS['patti'][1] + PATTI_H)
DEPTH_REF = FEET - F_REF
HEAD_GAP = min(chara_box('mayu')[1], chara_box('patti')[1]) - F_REF
DEPTH_MIN = int(math.ceil(DEPTH_REF - max(0, HEAD_GAP)))
print("基準: 床の線 %d / 足元 %d   いちばん短い画面: 床の線 %d / 奥行き %d (上の紙の下端 %d)"
      % (F_REF, FEET, F_MIN, DEPTH_MIN, CMP_END))
if F_MIN + DEPTH_MIN > 290:                        # iPhone の Safari(ツールバーあり)で横いっぱいに入る目安
    print("注意: この配置だと、背の低いスマホでは部屋が少し縮みます(足元 %d > 290)" % (F_MIN + DEPTH_MIN))


# ═══════════ 壁・天井・黒板(うごかない絵) ═══════════
bx, by, bw = BOARD_X, BOARD_TOP, BOARD_W
pcroom = Image.open(os.path.join(WEB, "room_design.png")).convert("RGBA")
im.alpha_composite(pcroom.crop((PCX0, 0, PCX0 + W, 11)), (0, 0))     # 天井の板(PC版の光こみ)
R(0, 11, W, 1, 'ink')
for yy in range(12, H):                           # 漆喰の壁。下のほうは平らな色(下のかたまりとの継ぎ目を消す)
    R(0, yy, W, 1, 'pl1' if yy < 60 else 'pl0')
DI(0, 12, W, 6, 'pl2', 'pl1')
DI(0, 56, W, 8, 'pl1', 'pl0')
TEX_END = int(F_MIN - LB_OFF - 4)                  # ここより下の石板は、いつでも継ぎ目が出ないよう平らに
R(bx, by, bw, H - by, 'bdL')
for yy in range(by, by + 8):
    R(bx, yy, bw, 1, 'bd2')
DI(bx, by + 8, bw, 6, 'bd2', 'bdL')
for yy in range(by, by + 26):                     # 電球の照り返し
    step = 2 + (yy - by) // 5
    for xx in range(bx, bx + bw):
        if (xx + yy * 3) % step == 0:
            PXL(xx, yy, 'bdW2' if yy - by < 6 else 'bdW')
for ax, ay, arx, ary in [(48, 70, 36, 16), (132, 64, 30, 14), (70, 108, 30, 10)]:   # 拭き跡
    for yy in range(max(by, ay - ary), min(TEX_END, ay + ary + 1)):
        for xx in range(max(bx, ax - arx), min(bx + bw, ax + arx + 1)):
            e = ((xx - ax) / float(arx)) ** 2 + ((yy - ay) / float(ary)) ** 2
            if 0.58 < e < 1.0 and (xx * 3 + yy * 5) % 4 == 0:
                PXL(xx, yy, 'bd2')
            elif e <= 0.58 and (xx + yy * 2) % 9 == 0:
                PXL(xx, yy, 'bd2')
R(bx, by, bw, 1, 'bd3')                           # 天井との見切り
R(bx - 1, by, 1, H - by, 'ink'); R(bx + bw, by, 1, H - by, 'ink')
R(bx - 2, by, 1, H - by, 'wd0'); R(bx + bw + 1, by, 1, H - by, 'wd0')
im.alpha_composite(GAR, (0, 0))                   # ガーランド(黒板の上にかかる)
gb = Image.open(os.path.join(WEB, "design_garland.png")).convert("RGBA")
GB_H = gb.size[1]
gm = Image.new("RGBA", (W * 3, GB_H), (0, 0, 0, 0))
for f in range(3):
    gm.alpha_composite(gb.crop((f * 384 + PCX0, 0, f * 384 + PCX0 + W, GB_H)), (f * W, 0))
gm.save(os.path.join(WEB, "design_garland_m.png"))
GARLAND_Y = 8
BG_BARE = im.copy()                               # 配置ツール用(窓なし)
im.alpha_composite(WIN, POS['window'])


# ═══════════ 下のかたまり(黒板の下の方・データまとめ・チョーク受け・床・腰壁・トビラ) ═══════════
# 基準の座標で描いて、上端 LB_TOP_REF から切り出す。ページは F に合わせて上下させる
LB_TOP_REF = F_REF - LB_OFF
LB_H = H - (F_MIN - LB_OFF)                       # いちばん上がったときにも画面の下まで届く高さ
F = F_REF
lb = Canvas(Image.new("RGBA", (W, LB_TOP_REF + LB_H), (0, 0, 0, 0)))
LR, LP, LD = lb.R, lb.PXL, lb.DI
SLATE_END = F - TRAY_H                            # 石板の下端
# 左右の壁(平らな漆喰)と、右の腰壁
LR(0, LB_TOP_REF, W, F - LB_TOP_REF, 'pl0')
WAIN_TOP = F - 46
for x in range(bx + bw + 2, W):
    for yy in range(WAIN_TOP, F - 4):
        LP(x, yy, 'wd0' if x % 7 == 0 else ('wd1' if (x // 7) % 3 else 'fl2'))
LR(bx + bw + 2, WAIN_TOP - 2, W - bx - bw - 2, 1, 'ink')
LR(bx + bw + 2, WAIN_TOP - 1, W - bx - bw - 2, 2, 'wd2')
LR(bx + bw + 2, WAIN_TOP + 1, W - bx - bw - 2, 1, 'wd0')
LR(0, WAIN_TOP, 2, F - 4 - WAIN_TOP, 'wd1')       # 左の細い壁も腰壁
# 石板: 上端は平ら(継ぎ目)、下へ暗く、チョークの粉がたまる
LR(bx, LB_TOP_REF, bw, SLATE_END - LB_TOP_REF, 'bdL')
dark0 = SLATE_END - 40
for yy in range(dark0, SLATE_END):
    t = (yy - dark0) / 40.0
    for xx in range(bx, bx + bw):
        if t > 0.55 or (xx + yy) % 2 == 0 and t > 0.2:
            LP(xx, yy, 'bd0')
for yy in range(SLATE_END - 16, SLATE_END):
    d = (yy - (SLATE_END - 16)) / 15.0
    step = max(2, int(16 - d * 13))
    for xx in range(bx, bx + bw):
        if (xx * 7 + yy * 11) % step == 0:
            LP(xx, yy, 'bd3')
LR(bx - 1, LB_TOP_REF, 1, SLATE_END - LB_TOP_REF, 'ink'); LR(bx + bw, LB_TOP_REF, 1, SLATE_END - LB_TOP_REF, 'ink')
LR(bx - 2, LB_TOP_REF, 1, SLATE_END - LB_TOP_REF, 'wd0'); LR(bx + bw + 1, LB_TOP_REF, 1, SLATE_END - LB_TOP_REF, 'wd0')
# 巾木(黒板の外)
for x0, x1 in ((0, bx - 2), (bx + bw + 2, W)):
    LR(x0, F - 4, x1 - x0, 1, 'ink'); LR(x0, F - 3, x1 - x0, 2, 'wd1'); LR(x0, F - 1, x1 - x0, 1, 'wd0')
# 床(板張り。消失点は床の線の上 96px。基準の見え方と同じ遠近)
FLOOR_BOT = LB_TOP_REF + LB_H
LR(0, F, W, FLOOR_BOT - F, 'fl0')
LR(0, F, W, 2, 'flD')
SEAM_OFF = [8, 18, 30, 44, 60, 78, 98, 120, 144, 170, 198, 228, 260]
SEAMS = [F + o for o in SEAM_OFF]
for y in SEAMS:
    LR(0, y, W, 1, 'flD'); LR(0, y + 1, W, 1, 'fl2')
VPX, VPY = W / 2.0, F - 96.0
for k in range(-5, 6):
    xb = VPX + k * 34
    for yy in range(F + 2, FLOOR_BOT):
        t = (yy - VPY) / (F + 264 - VPY)
        xx = int(VPX + (xb - VPX) * t + 0.5)
        if 0 <= xx < W and yy not in SEAMS and (yy - 1) not in SEAMS:
            LP(xx, yy, 'flD')
for bi in range(len(SEAMS) - 1):
    if bi % 2 == 0:
        for yy in range(SEAMS[bi] + 2, SEAMS[bi + 1]):
            for xx in range(W):
                if (xx + yy * 3 + bi) % 5 == 0:
                    LP(xx, yy, 'fl1')
for yy in range(F + 2, FLOOR_BOT):
    for xx in range(W):
        if (xx * 5 + yy * 17) % 97 == 0:
            LR(xx, yy, 3, 1, 'fl1')
for yy in range(F + 2, F + 200):                  # 窓からの斜めの光の帯
    t = (yy - F) / 200.0
    x0 = int(150 - t * 150)
    for xx in range(max(0, x0), min(W, x0 + 26 + int(t * 30))):
        if (xx + yy) % 2 == 0 and not any(s <= yy <= s + 1 for s in SEAMS):
            LP(xx, yy, 'fl2')
LB_BARE_NOCHALK = lb.im.copy()


# ── チョーク(下のかたまりの落書き。データまとめのわきだけ) ──
FLOOR_RECTS = {k: REF_B[k] for k in FLOOR_PAPERS}


def free_lb(x, y, pad=4):
    if not (bx + 2 <= x < bx + bw - 2 and FLOOR_TOP_REF <= y < SLATE_END - 3):
        return False
    for (rx, ry, rw, rh) in FLOOR_RECTS.values():
        if rx - pad <= x < rx + rw + pad and ry - pad <= y < ry + rh + pad:
            return False
    return True


def LCPX(x, y, c):
    if free_lb(x, y):
        LP(x, y, c)


def lb_circle(cx9, cy9, r9, dense=3):
    n9 = max(12, int(r9 * 6))
    for k in range(n9):
        if k % dense:
            a9 = k * 2 * math.pi / n9
            LCPX(int(cx9 + math.cos(a9) * r9 + 0.5), int(cy9 + math.sin(a9) * r9 * 0.92 + 0.5), 'chk2')


def lb_write(x9, y9, rows, wmax):
    for r9 in range(rows):
        yy = y9 + r9 * 4
        ln = wmax - (r9 * 7) % max(1, wmax // 2)
        xx = x9
        while xx < x9 + ln:
            seg = 2 + (xx * 3 + r9) % 4
            for k in range(seg):
                if xx + k < x9 + ln:
                    LCPX(xx + k, yy, 'chk2')
            xx += seg + 2


def lb_ghost(gx9, gy9, r9=5):
    for a9 in range(180, 361, 12):
        LCPX(int(gx9 + math.cos(math.radians(a9)) * r9), int(gy9 + math.sin(math.radians(a9)) * r9), 'chk2')
    for dx9 in range(-r9, r9 + 1):
        if (dx9 + r9) % 3 != 1:
            LCPX(gx9 + dx9, gy9 + r9 - abs(dx9) % 2, 'chk2')
    LCPX(gx9 - 2, gy9 - 1, 'chk'); LCPX(gx9 + 2, gy9 - 1, 'chk')


def lb_star(sx9, sy9):
    for ddx, ddy in ((0, -2), (0, 2), (-2, 0), (2, 0), (0, 0)):
        LCPX(sx9 + ddx, sy9 + ddy, 'chk')


pr = REF_B['datapanel']
lx0, lx1 = bx + 4, pr[0] - 6                       # データまとめの左の空き
rx0, rx1 = pr[0] + pr[2] + 6, bx + bw - 4          # 右の空き
ymid = pr[1] + pr[3] // 2
if lx1 - lx0 >= 20:
    lb_circle((lx0 + lx1) // 2, ymid - 14, 8); lb_circle((lx0 + lx1) // 2, ymid - 14, 5, 4)
    for k in range(-6, 7):
        if k % 3:
            LCPX((lx0 + lx1) // 2 + k, ymid - 14, 'chk2'); LCPX((lx0 + lx1) // 2, ymid - 14 + k, 'chk2')
    lb_write(lx0, ymid + 8, 3, lx1 - lx0)
if rx1 - rx0 >= 20:
    lb_ghost((rx0 + rx1) // 2, ymid - 18)
    lb_write(rx0, ymid + 4, 3, rx1 - rx0)
    lb_star(rx1 - 4, ymid + 22)
LB_BARE = lb.im.copy()                              # 配置ツール用(データまとめ・トビラなし)

# データまとめ(床側の紙)とチョーク受け
for k in FLOOR_PAPERS:
    x, y, pw, ph = REF_B[k]
    if k != 'datatitle':                            # 紙の影
        for yy in range(y + 2, y + ph + 2):
            for xx in range(x + 2, x + pw + 2):
                if (xx >= x + pw or yy >= y + ph) and bx <= xx < bx + bw and yy < SLATE_END:
                    LP(xx, yy, 'bdS')
    lb.im.alpha_composite(SPR[k][0], POS[k])
tw = TRAY.size[0]
tray = TRAY.crop(((tw - bw) // 2, 0, (tw - bw) // 2 + bw, TRAY.size[1]))
for img_ in (lb.im, LB_BARE):
    img_.alpha_composite(tray, (bx, SLATE_END))
lb.im.alpha_composite(CHALK, (bx + 34, SLATE_END - 2))
LB_BARE.alpha_composite(CHALK, (bx + 34, SLATE_END - 2))
# トビラ(床に立つ)と、床にこぼれる白い光
dx0, dy0 = POS['door']
lb.im.alpha_composite(DOOR, (dx0, dy0))
DOOR_HOT = (dx0 + DOOR_OPEN[0], dy0 + DOOR_OPEN[1], DOOR_OPEN[2], DOOR_OPEN[3])
for yy in range(F, F + 26):
    t = (yy - F) / 26.0
    half = int(DOOR_OPEN[2] / 2 + t * 14)
    cx = DOOR_HOT[0] + DOOR_HOT[2] // 2
    for xx in range(cx - half, cx + half):
        if 0 <= xx < W and (xx + yy) % (2 if t < 0.5 else 3) == 0 and not any(s <= yy <= s + 1 for s in SEAMS):
            LP(xx, yy, 'fl3')


# ═══════════ 重なり検査(基準の高さと、いちばん短い画面の両方で) ═══════════
def placed_at(t):
    """t=1 基準 / t=0 いちばん短い画面 のときの配置(名前, x, y, w, h)。"""
    dF = (F_MIN - F_REF) * (1 - t)
    out = []
    for k in PAPER_IDS:
        x, y, pw, ph = REF_B[k]
        if k in TOP_PAPERS:
            y = CMP_Y[k] + (REF_B[k][1] - CMP_Y[k]) * t
        else:
            y = y + dF
        out.append((k, x, y, pw, ph))
    out.append(('window', POS['window'][0], POS['window'][1], WIN_W, WIN_H))
    out.append(('door:看板', dx0, dy0 + dF, 40, 15))
    out.append(('door:トビラ', dx0 + DOOR_OPEN[0] - 3, dy0 + DOOR_OPEN[1] - 4 + dF, DOOR_OPEN[2] + 6, DOOR_OPEN[3] + 6))
    dd = (DEPTH_MIN - DEPTH_REF) * (1 - t)
    for c in ('mayu', 'patti'):
        b = chara_box(c)
        out.append((c, b[0], b[1] + dF + dd, b[2], b[3]))
    out.append(('黒板', bx - 2, by, bw + 4, (F_REF + dF) - by))
    return out


def isect(a, b):
    return (min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]), min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2]))


ALLOWED = {frozenset(('door:看板', 'door:トビラ'))}
bad = []
for tt, label in ((1, "背の高い画面"), (0, "いちばん短い画面")):
    pl = placed_at(tt)
    for i in range(len(pl)):
        for j in range(i + 1, len(pl)):
            a, b = pl[i], pl[j]
            if '黒板' in (a[0], b[0]) and ((a[0] in PAPER_IDS or b[0] in PAPER_IDS) or ({a[0], b[0]} & {'mayu', 'patti'})):
                continue
            ow, oh = isect(a, b)
            if ow > 0.5 and oh > 0.5 and frozenset((a[0], b[0])) not in ALLOWED:
                bad.append("%s: %s x %s (%dx%d)" % (label, a[0], b[0], ow, oh))


def arrow_ok(rects, a, b):
    ax, ay, aw, ah = rects[a]; bx_, by_, bw_, bh_ = rects[b]
    if by_ >= ay + ah + 15:
        return True
    if bx_ >= ax + aw + 15:
        lo, hi = max(ay, by_), min(ay + ah, by_ + bh_)
        return hi - lo >= 6
    return False


for tt in (1, 0):
    rects = {p[0]: p[1:] for p in placed_at(tt)}
    for a, b in ARROWS:
        if not arrow_ok(rects, a, b):
            bad.append("チョークの矢印 %s→%s が引けない(紙どうしが近すぎるか、並びが上下左右でない)" % (a, b))
if bad:
    if CUSTOM:
        print("注意(池本さんの配置で重なっている所):\n  " + "\n  ".join(bad))
    else:
        raise SystemExit("重なり事故:\n  " + "\n  ".join(bad))


# ═══════════ 書き出し ═══════════
def side_vignette(img, y0=0):
    """左右のふちを沈める(上下に動く絵にも使えるよう、横方向だけ)。"""
    px = img.load()
    w_, h_ = img.size
    for yy in range(h_):
        for xx in list(range(0, 10)) + list(range(w_ - 10, w_)):
            d = min(xx, w_ - 1 - xx)
            k = 0.76 if d < 3 else (0.88 if d < 8 else 1.0)          # ディザにしない(上下に動いても継ぎ目が出ない)
            r, g_, b, a = px[xx, yy]
            if a and k < 1:
                px[xx, yy] = (int(r * k), int(g_ * k), int(b * k), a)


def top_vignette(img):
    px = img.load()
    for yy in range(12, 40):
        k = 0.82 + 0.18 * (yy - 12) / 28.0
        for xx in range(W):
            if (yy > 30 and (xx + yy) % 2) or k >= 0.99:
                continue
            r, g_, b, a = px[xx, yy]
            px[xx, yy] = (int(r * k), int(g_ * k), int(b * k), a)


for img_ in (im, BG_BARE):
    side_vignette(img_); top_vignette(img_)
lower = lb.im.crop((0, LB_TOP_REF, W, LB_TOP_REF + LB_H))
lower_bare = LB_BARE.crop((0, LB_TOP_REF, W, LB_TOP_REF + LB_H))
for img_ in (lower, lower_bare):
    side_vignette(img_, LB_TOP_REF)
im.convert("RGB").save(os.path.join(WEB, "room_design_m.png"))
lower.save(os.path.join(WEB, "design_m_lower.png"))
bare = BG_BARE.copy()
bare.alpha_composite(lower_bare.crop((0, 0, W, H - LB_TOP_REF)), (0, LB_TOP_REF))
bare.convert("RGB").save(os.path.join(WEB, "room_design_m_bare.png"))
json.dump(PARTS, io.open(PARTS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

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
    if k in FLOOR_ANCHOR:
        o["floor"] = True
    tool.append(o)
papers = {}
for k in PAPER_IDS:
    ox, oy, pw, ph = SPR[k][1]
    p = {"img": "props_dm/%s.png" % k, "x": POS[k][0], "y": POS[k][1], "w": SIZES[k][0], "h": SIZES[k][1],
         "body": [ox, oy, pw, ph], "anchor": "floor" if k in FLOOR_PAPERS else "top"}
    if k in TOP_PAPERS:
        p["yc"] = CMP_Y[k] - oy                      # 詰めた位置(絵の左上)
    papers[k] = p
meta = {
    "w": W, "h": H, "F_ref": F_REF, "F_min": F_MIN, "depth_ref": DEPTH_REF, "depth_min": DEPTH_MIN,
    "board": [bx, by, bw], "tray_h": TRAY_H,
    "lower": {"img": "design_m_lower.png", "top_ref": LB_TOP_REF, "h": LB_H},
    "garland_y": GARLAND_Y, "garland_h": GB_H,
    "papers": papers, "arrows": [list(a) for a in ARROWS],
    "door": list(DOOR_HOT), "window": [POS['window'][0], POS['window'][1], WIN_W, WIN_H],
    "mayu": [POS['mayu'][0], POS['mayu'][1], SCALE['mayu']],
    "patti": [POS['patti'][0], POS['patti'][1], SCALE['patti']],
    "custom": CUSTOM, "tool": tool,
}
json.dump(meta, io.open(os.path.join(WEB, "room_design_m.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("room_design_m.png / design_m_lower.png(高さ %d) / room_design_m_bare.png / room_design_m.json  (重なり %d 件)"
      % (LB_H, len(bad)))
