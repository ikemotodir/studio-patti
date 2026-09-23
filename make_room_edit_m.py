# -*- coding: utf-8 -*-
"""スマホ(縦画面)用の編集室を組み立てる。デザイン室(make_room_design_m.py)と同じ「画面の高さで伸び縮み」の作り。

方針:
 ・PC版で描いた 大スクリーン・電飾の表示板・数字ボタンパネル は、光を当てた後の切り出し
   (room_edit_layers/objects/*.png)をそのまま等倍で使う
 ・メニューパネルは縦に5段だと縦画面に入らないので、同じ色と作りで「見出し+2列×2段」に組み直す
 ・基準(背の高い画面): 天井から電飾の表示板を吊り、その下に大スクリーン。床に メニュー・数字ボタン・
   スタジオへのトビラ(左)。二人は床の手前。ゲーミングチェアと編集卓は縦では入らないので置かない
 ・画面が短いときは床の線 F が上がり、床側(メニュー・数字ボタン・トビラ・二人・床)はいっしょに上がる。
   表示板とスクリーンは間隔が詰まる(詰めた位置 yc はここで計算、補間はページ側 contents_m.html)
 ・壁は縦じまの吸音パネル(上下に同じ模様)なので、上下に動く床側の絵との継ぎ目は出ない
 ・置き場所は DEFAULT。配置ツールが保存した layout.json の "edit_m" があればそれで上書き。
   無ければ前回の room_edit_m.json(いま公開されている配置)を保つ
 出力: room_edit_m.png(壁・天井) / edit_m_lower.png(床側) / room_edit_m_bare.png(配置ツール用)
       / marquee_blink_m.png / props_em/*.png / room_edit_m.json
"""
import glob, hashlib
import io
import json
import math
import os
import re
import sys

from PIL import Image, ImageDraw

WEB = os.path.dirname(os.path.abspath(__file__))
OBJ = os.path.join(WEB, "room_edit_layers", "objects")
PROPS = os.path.join(WEB, "props_em")
HAVE_LAYERS = os.path.isdir(OBJ) and not os.environ.get("PATTI_NO_LAYERS")
LAYOUT_PATH = os.environ.get("PATTI_LAYOUT") or os.path.join(WEB, "layout.json")
W, H = 216, 480

P = {
    'ink': (4, 2, 26), 'n0': (0, 1, 43), 'n1': (0, 1, 57), 'n2': (1, 32, 68),
    'q0': (22, 9, 58), 'q1': (40, 11, 76), 'q2': (52, 16, 89), 'q3': (74, 21, 78), 'q4': (81, 35, 80),
    'q5': (110, 45, 107),
    'cyn0': (16, 84, 104), 'cyn1': (44, 164, 186), 'cyn2': (126, 224, 235),
    'mb': (54, 18, 75), 'mb2': (56, 19, 75), 'md': (38, 16, 59), 'md2': (18, 9, 45),     # メニュー箱(PC版の色)
    'ml': (103, 77, 121), 'ml2': (117, 80, 114), 'mp': (111, 58, 121),
    'fl0': (54, 18, 75), 'fl1': (38, 16, 59), 'fl2': (65, 22, 87), 'flS': (134, 41, 91), 'flL': (118, 86, 142),  # 床
    'cp0': (102, 17, 46), 'cp1': (156, 20, 58), 'cp2': (139, 23, 73),                     # 赤いじゅうたん
    'gray0': (110, 102, 96), 'gray1': (154, 144, 138), 'gray2': (201, 194, 184), 'wht': (255, 255, 255),
}


def C(c):
    return (P[c] if isinstance(c, str) else tuple(c)) + (255,)


class Canvas(object):
    def __init__(self, img):
        self.im = img
        self.d = ImageDraw.Draw(img)
        self.w, self.h = img.size

    def R(self, x, y, w, h, c):
        if w > 0 and h > 0:
            self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=C(c))

    def PXL(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.d.point((x, y), fill=C(c))


# ═══════════ 部品(PC版の切り出し / 無ければ props_em から) ═══════════
def part(pid, name, layers=('bg', 'furniture', 'props'), fix=None):
    path = os.path.join(PROPS, pid + ".png")
    if HAVE_LAYERS:
        cv = Image.new("RGBA", (384, 240), (0, 0, 0, 0))
        n = 0
        for lay in layers:
            for f in sorted(glob.glob(os.path.join(OBJ, "%s__*_%s.png" % (lay, name)))):
                cv.alpha_composite(Image.open(f).convert("RGBA"))
                n += 1
        assert n, "部品が見つからない: " + name
        bb = cv.getchannel("A").getbbox()
        sp = cv.crop(bb)
        if fix:                                           # 手直し(上を cut 行落としたら位置もずらす)
            sp, cut = fix(sp)
            bb = (bb[0], bb[1] + cut, bb[2], bb[3])
        os.makedirs(PROPS, exist_ok=True)
        sp.save(path)
        return sp, bb
    if not os.path.exists(path):
        sys.exit("部品がありません: props_em/%s.png (room_edit_layers のある PC で一度ビルドしてください)" % pid)
    return Image.open(path).convert("RGBA"), None


def fix_screen(sp):
    """PC版では下の縁が編集卓に隠れていた。下の縁・影・LEDを上と同じ作りで描き足し、
    上の光のにじみ(0〜4行目。縦の画面ではスクリーンより横に長い帯に見える)を落とす。"""
    px = sp.load()
    w, h = sp.size
    base = {h - 6: (54, 18, 75), h - 5: (54, 18, 75), h - 4: (65, 22, 87), h - 3: (38, 16, 59)}
    for x in range(11, w - 11):
        r_ = px[x, h - 7]                                 # 画面の下の影
        if r_[3] == 0 or r_[:3] == (0, 0, 0):
            px[x, h - 7] = (4, 2, 26, 255)
        for y, c in base.items():                         # 枠の下辺(PC版の角と同じ色。ところどころ傷)
            r_ = px[x, y]
            if r_[3] == 0 or r_[:3] == (0, 0, 0):
                px[x, y] = ((22, 9, 58) if (x + y * 2) % 29 == 0 else c) + (255,)
    for x in range(6, w - 5, 2):                          # 下のLED(角に残っている粒と同じ間隔・同じ色)
        if px[x, h - 1][3] == 0:
            px[x, h - 1] = (44, 164, 186, 255)
    CUT = 5
    return sp.crop((0, CUT, w, h)), CUT


SCREEN, SCR_BB = part('screen', '大スクリーン', fix=fix_screen)
MARQ, MARQ_BB = part('marquee_body', '電飾マーキー')
NUMP, NUMP_BB = part('number', '数字ボタンパネル')
# PC版での中身の位置(部品の左上からの距離)。切り出しが無い環境では前回の値を使う
PARTS_JSON = os.path.join(PROPS, "parts.json")
if HAVE_LAYERS:
    PARTS = {
        'screen_inner': [106 - SCR_BB[0], 22 - SCR_BB[1], 172, 93],
        'marquee_text': [292 - MARQ_BB[0], 24.15 - MARQ_BB[1], 45, 12],
        'marquee_blink_x': MARQ_BB[0], 'marquee_blink_dy': 18 - MARQ_BB[1],
        'buttons': [[x - NUMP_BB[0], y - NUMP_BB[1], 21, 21] for x, y in ((292, 69), (316, 69), (292, 96), (316, 96))],
    }
    os.makedirs(PROPS, exist_ok=True)
    json.dump(PARTS, io.open(PARTS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    PARTS = json.load(io.open(PARTS_JSON, encoding="utf-8"))

# 電飾の表示板は天井から吊る(ひもを部品に含める。表示板が下がるとひもが伸びて見える)
CORD = 44
marquee = Image.new("RGBA", (MARQ.size[0], MARQ.size[1] + CORD), (0, 0, 0, 0))
mc = Canvas(marquee)
for cx in (7, MARQ.size[0] - 8):
    mc.R(cx, 0, 1, CORD + 2, 'gray0'); mc.R(cx + 1, 0, 1, CORD + 2, 'ink')
marquee.alpha_composite(MARQ, (0, CORD))
marquee.save(os.path.join(PROPS, "marquee.png"))
# 電飾のまたたき(PC版の4コマから表示板の所だけ切る)
mb = Image.open(os.path.join(WEB, "marquee_blink.png")).convert("RGBA")
MBH = mb.size[1]
mbm = Image.new("RGBA", (MARQ.size[0] * 4, MBH), (0, 0, 0, 0))
bx0 = int(PARTS['marquee_blink_x'])
for f in range(4):
    mbm.alpha_composite(mb.crop((f * 384 + bx0, 0, f * 384 + bx0 + MARQ.size[0], MBH)), (f * MARQ.size[0], 0))
mbm.save(os.path.join(WEB, "marquee_blink_m.png"))


# ── メニュー(見出し+2列×2段)。PC版のメニューパネルと同じ色・同じ作り ──
MENU_W, MENU_H = 120, 62
MENU_SLOTS = {'hdr': [4, 4, 112, 14],
              0: [4, 22, 54, 16], 1: [62, 22, 54, 16], 2: [4, 42, 54, 16], 3: [62, 42, 54, 16]}


def menu_img():
    u = Canvas(Image.new("RGBA", (MENU_W, MENU_H), (0, 0, 0, 0)))
    u.R(0, 0, MENU_W, MENU_H, 'ink')
    u.R(1, 1, MENU_W - 2, MENU_H - 2, 'mb')
    for yy in range(1, MENU_H - 1):                      # ななめの照り(PC版の箱と同じ見え方)
        for xx in range(1, MENU_W - 1):
            k = (xx + yy * 2) % 23
            if k < 3 and (xx + yy) % 2 == 0:
                u.PXL(xx, yy, 'mp' if k == 0 else 'mb2')
    u.R(1, 1, MENU_W - 2, 1, 'ml'); u.R(1, 1, 1, MENU_H - 2, 'ml2')
    u.R(1, MENU_H - 2, MENU_W - 2, 1, 'md'); u.R(MENU_W - 2, 1, 1, MENU_H - 2, 'md')
    for key, (x, y, w, h) in MENU_SLOTS.items():
        u.R(x - 1, y - 1, w + 2, h + 2, 'md2')           # くぼみ
        u.R(x, y, w, h, 'n0')
        u.R(x, y, w, 1, 'n1')
        u.R(x - 1, y + h, w + 2, 1, 'ml'); u.R(x + w, y - 1, 1, h + 2, 'ml2')
        if key == 'hdr':                                  # 見出しはシアンの線とLED
            u.R(x + 3, y + 2, w - 6, 1, 'cyn1'); u.R(x + 3, y + h - 3, w - 6, 1, 'cyn1')
            for ex in (x + 1, x + w - 2):
                u.R(ex, y + 4, 1, h - 8, 'cyn2')
    return u.im


MENU = menu_img()
MENU.save(os.path.join(PROPS, "menu.png"))


# ── スタジオへのトビラ(看板つき。白い光がもれる) ──
DOOR_W = 40
DOOR_OPEN = (7, 20, 26, 62)
DOOR_H = DOOR_OPEN[1] + DOOR_OPEN[3] + 2


def door_img():
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
    u.R(x - 3, y - 3, w + 6, h + 3, 'q3')
    u.R(x - 2, y - 2, w + 4, h + 2, 'q4')
    u.R(x - 2, y - 2, w + 4, 1, 'q5'); u.R(x - 2, y - 2, 1, h + 2, 'q5')
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
    for k in range(5):
        u.R(x + 3 + k * 5, y + 4 + k, 1, h - 8 - k * 4, 'gray2' if k % 2 else 'gray1')
    u.R(x - 3, y + h, w + 6, 1, 'q5')
    u.R(x - 3, y + h + 1, w + 6, 1, 'ink')
    return u.im


DOOR = door_img()
DOOR.save(os.path.join(PROPS, "door.png"))


# ═══════════ 置き場所(基準 = 背の高い画面) ═══════════
F_REF = 290
MAYU_W, MAYU_H, PATTI_W, PATTI_H = 30, 72, 32, 48
TOP_ITEMS = ['marquee', 'screen']                     # 画面に合わせて間隔が伸び縮み
FLOOR_ITEMS = ['menu', 'number', 'door', 'mayu', 'patti']
SIZES = {'marquee': marquee.size, 'screen': SCREEN.size, 'menu': MENU.size, 'number': NUMP.size,
         'door': DOOR.size, 'mayu': (MAYU_W, MAYU_H), 'patti': (PATTI_W, PATTI_H)}
DEFAULT = {
    'marquee': ((W - MARQ.size[0]) // 2, 24 - CORD),      # 表示板の上端 y=24(ひもはその上)
    'screen': ((W - SCREEN.size[0]) // 2, 63),
    'door': (0, F_REF - DOOR_H),
    'menu': (42, F_REF - MENU_H),
    'number': (W - NUMP.size[0], F_REF - NUMP.size[1]),
    'mayu': (46, F_REF + 60 - MAYU_H), 'patti': (150, F_REF + 60 - PATTI_H),
}
SCALE = {'mayu': 0.75, 'patti': 0.75}
NAMES = {'marquee': '電飾の表示板', 'screen': '大スクリーン', 'menu': 'メニュー（制作事例）',
         'number': '数字ボタン', 'door': 'スタジオの看板とトビラ（横にだけ動きます）',
         'mayu': 'マユちゃん', 'patti': 'パッチ'}
ORDER = TOP_ITEMS + ['menu', 'number', 'door', 'mayu', 'patti']
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
    _lay = _read_items(LAYOUT_PATH, "edit_m")
    SRC = 'layout.json の "edit_m"'
    if _lay is None:
        _lay = _read_items(os.path.join(WEB, "room_edit_m.json"), "tool")
        SRC = "前回の room_edit_m.json(いまの配置のまま)"
        try:                                  # 作りを変える前の古い一覧は使わない(基準の高さが違う)
            if json.load(io.open(os.path.join(WEB, "room_edit_m.json"), encoding="utf-8")).get("F_ref") != F_REF:
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

# はみ出しは中へ寄せる(基準の高さで)
for k in ORDER:
    w_, h_ = SIZES[k]
    x_, y_ = POS[k]
    if k in SCALE:
        s_ = SCALE[k]
        ox, oy = w_ * (1 - s_) / 2.0, h_ * (1 - s_)
        nx = int(min(max(x_, math.ceil(-ox)), math.floor(W - w_ * s_ - ox)))
        ny = int(min(max(y_, F_REF + 2 - h_), math.floor(H - h_ * s_ - oy)))
    elif k == 'marquee':
        nx, ny = min(max(x_, 0), W - w_), min(max(y_, -CORD + 12), F_REF - h_)
    else:
        nx, ny = min(max(x_, 0), W - w_), min(max(y_, 12), F_REF - h_)
    if k in LOCK_Y:
        ny = y_
    if (nx, ny) != (x_, y_):
        print("注意: %s が画面からはみ出すので (%d,%d) に寄せました" % (NAMES[k], nx, ny))
        POS[k] = (nx, ny)


# ═══════════ 画面が短いときの「詰めた位置」 ═══════════
def vis(k, pos=None):
    """目に見える矩形(表示板はひもを除く)。"""
    x, y = pos or POS[k]
    w, h = SIZES[k]
    if k == 'marquee':
        return (x, y + CORD, w, h - CORD)
    return (x, y, w, h)


def xover(a, b, m=2):
    return a[0] < b[0] + b[2] + m and b[0] < a[0] + a[2] + m


UP = {'marquee': 6, 'screen': 12}                     # これより上へは寄せない
REF_V = {k: vis(k) for k in TOP_ITEMS}
CMP = {}
for k in sorted(TOP_ITEMS, key=lambda k: REF_V[k][1]):
    y = min(REF_V[k][1], UP[k])
    for a in CMP:
        if REF_V[a][1] < REF_V[k][1] and xover(REF_V[a], REF_V[k]):
            y = max(y, CMP[a] + REF_V[a][3] + 4)
    CMP[k] = min(y, REF_V[k][1])
CMP_END = max(CMP[k] + REF_V[k][3] for k in TOP_ITEMS)
FLOOR_TOP_REF = min(POS[k][1] for k in ('menu', 'number', 'door'))
LB_OFF = F_REF - (FLOOR_TOP_REF - 4)                 # 下の絵(床側)の上端 = F - LB_OFF
F_MIN = min(F_REF, CMP_END + 4 + (F_REF - FLOOR_TOP_REF))


def chara_box(key, pos=None):
    x, y = pos or POS[key]; s = SCALE[key]
    w, h = (MAYU_W, MAYU_H) if key == 'mayu' else (PATTI_W, PATTI_H)
    return (x + w * (1 - s) / 2.0, y + h * (1 - s), w * s, h * s)


FEET = max(POS['mayu'][1] + MAYU_H, POS['patti'][1] + PATTI_H)
DEPTH_REF = FEET - F_REF
HEAD_GAP = min(chara_box('mayu')[1], chara_box('patti')[1]) - F_REF
DEPTH_MIN = int(math.ceil(DEPTH_REF - max(0, HEAD_GAP)))
print("基準: 床の線 %d / 足元 %d   いちばん短い画面: 床の線 %d / 奥行き %d (スクリーンの下端 %d)"
      % (F_REF, FEET, F_MIN, DEPTH_MIN, CMP_END))
if F_MIN + DEPTH_MIN > 290:
    print("注意: この配置だと、背の低いスマホでは部屋が少し縮みます(足元 %d > 290)" % (F_MIN + DEPTH_MIN))


# ═══════════ 壁(縦じまの吸音パネル。上下に同じ模様なので継ぎ目が出ない) ═══════════
def wall(cv, y0, y1):
    for x in range(W):
        k = x % 18
        c = 'ink' if k == 0 else ('q1' if k == 1 else ('q0' if k < 16 else 'md2'))
        cv.R(x, y0, 1, y1 - y0, c)
    for x in (5, W - 6):                              # 縦のシアンのLED
        for yy in range(y0, y1):
            if yy % 3 == 0:
                cv.PXL(x, yy, 'cyn2' if yy % 9 == 0 else 'cyn1')


bg = Canvas(Image.new("RGBA", (W, H), (0, 0, 0, 255)))
wall(bg, 0, H)
bg.R(0, 0, W, 9, 'ink')                               # 天井
bg.R(0, 9, W, 1, 'q2'); bg.R(0, 10, W, 1, 'cyn0')
for x in range(3, W, 6):
    bg.PXL(x, 4, 'cyn1' if (x // 6) % 2 else 'cyn0')
BG_BARE = bg.im.copy()


# ═══════════ 床側(基準の座標で描いて、上端 LB_TOP_REF から切り出す) ═══════════
F = F_REF
LB_TOP_REF = F - LB_OFF
LB_H = H - (F_MIN - LB_OFF)
lb = Canvas(Image.new("RGBA", (W, LB_TOP_REF + LB_H), (0, 0, 0, 0)))
# 壁は描かない(透明のまま)。後ろの背景の壁がそのまま見えるので、上下に動かしても継ぎ目が出ない
lb.R(0, F - 4, W, 1, 'ink'); lb.R(0, F - 3, W, 2, 'q3'); lb.R(0, F - 1, W, 1, 'ink')   # 巾木
FLOOR_BOT = LB_TOP_REF + LB_H
lb.R(0, F, W, FLOOR_BOT - F, 'fl0')
SEAM_OFF = [8, 18, 30, 44, 60, 78, 98, 120, 144, 170, 198, 228, 260]
SEAMS = [F + o for o in SEAM_OFF]
for y in SEAMS:
    lb.R(0, y, W, 1, 'fl1'); lb.R(0, y + 1, W, 1, 'fl2')
VPX, VPY = W / 2.0, F - 96.0
for k in range(-5, 6):
    xb = VPX + k * 34
    for yy in range(F + 2, FLOOR_BOT):
        t = (yy - VPY) / (F + 264 - VPY)
        xx = int(VPX + (xb - VPX) * t + 0.5)
        if 0 <= xx < W and yy not in SEAMS and (yy - 1) not in SEAMS:
            lb.PXL(xx, yy, 'fl1')
for yy in range(F + 1, FLOOR_BOT):                     # 赤いじゅうたん(スクリーンの前から手前へ、細く)
    t = (yy - F) / 180.0
    half = int(14 + t * 22)
    cx = W // 2
    for xx in range(max(0, cx - half), min(W, cx + half)):
        edge = xx in (cx - half, cx + half - 1)
        if edge:
            lb.PXL(xx, yy, 'cp2')
        elif (xx + yy) % 2 == 0:
            lb.PXL(xx, yy, 'cp0')
        elif (xx * 3 + yy * 5) % 7 == 0:
            lb.PXL(xx, yy, 'cp2')
for yy in range(F + 2, FLOOR_BOT):                     # 木目のかすれ
    for xx in range(W):
        if (xx * 5 + yy * 17) % 97 == 0:
            lb.R(xx, yy, 3, 1, 'fl2')
LB_BARE = lb.im.copy()

# 床に置く物(トビラ・メニュー・数字ボタン)
lb.im.alpha_composite(MENU, POS['menu'])
lb.im.alpha_composite(NUMP, POS['number'])
lb.im.alpha_composite(DOOR, POS['door'])
dx0, dy0 = POS['door']
DOOR_HOT = [dx0 + DOOR_OPEN[0], dy0 + DOOR_OPEN[1], DOOR_OPEN[2], DOOR_OPEN[3]]
for yy in range(F, F + 24):                            # 床にこぼれる白い光
    t = (yy - F) / 24.0
    half = int(DOOR_OPEN[2] / 2 + t * 12)
    cx = DOOR_HOT[0] + DOOR_HOT[2] // 2
    for xx in range(cx - half, cx + half):
        if 0 <= xx < W and (xx + yy) % (2 if t < 0.5 else 3) == 0 and not any(s <= yy <= s + 1 for s in SEAMS):
            lb.PXL(xx, yy, 'flL')                      # 床の色を明るくした色(デザイン室と同じ作り)


# ═══════════ 重なり検査(背の高い画面と、いちばん短い画面) ═══════════
def placed_at(t):
    dF = (F_MIN - F_REF) * (1 - t)
    out = []
    for k in TOP_ITEMS:
        v = REF_V[k]
        out.append((k, v[0], CMP[k] + (v[1] - CMP[k]) * t, v[2], v[3]))
    for k in ('menu', 'number', 'door'):
        x, y = POS[k]; w, h = SIZES[k]
        out.append((k, x, y + dF, w, h))
    dd = (DEPTH_MIN - DEPTH_REF) * (1 - t)
    for c in ('mayu', 'patti'):
        b = chara_box(c)
        out.append((c, b[0], b[1] + dF + dd, b[2], b[3]))
    return out


bad = []
for tt, label in ((1, "背の高い画面"), (0, "いちばん短い画面")):
    pl = placed_at(tt)
    for i in range(len(pl)):
        for j in range(i + 1, len(pl)):
            a, b = pl[i], pl[j]
            ow = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
            oh = min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2])
            if ow > 0.5 and oh > 0.5:
                bad.append("%s: %s x %s (%dx%d)" % (label, a[0], b[0], ow, oh))
if bad:
    if CUSTOM:
        print("注意(池本さんの配置で重なっている所):\n  " + "\n  ".join(bad))
    else:
        raise SystemExit("重なり事故:\n  " + "\n  ".join(bad))


# ═══════════ 書き出し ═══════════
def side_vignette(img):
    px = img.load()
    w_, h_ = img.size
    for yy in range(h_):
        for xx in list(range(0, 10)) + list(range(w_ - 10, w_)):
            d = min(xx, w_ - 1 - xx)
            k = 0.76 if d < 3 else (0.88 if d < 8 else 1.0)
            r, g_, b, a = px[xx, yy]
            if a and k < 1:
                px[xx, yy] = (int(r * k), int(g_ * k), int(b * k), a)


for img_ in (bg.im, BG_BARE):
    side_vignette(img_)
lower = lb.im.crop((0, LB_TOP_REF, W, LB_TOP_REF + LB_H))
lower_bare = LB_BARE.crop((0, LB_TOP_REF, W, LB_TOP_REF + LB_H))
for img_ in (lower, lower_bare):
    side_vignette(img_)
bg.im.convert("RGB").save(os.path.join(WEB, "room_edit_m.png"))
lower.save(os.path.join(WEB, "edit_m_lower.png"))
bare = BG_BARE.copy()
bare.alpha_composite(lower_bare.crop((0, 0, W, H - LB_TOP_REF)), (0, LB_TOP_REF))
bare.convert("RGB").save(os.path.join(WEB, "room_edit_m_bare.png"))

IMG = {'mayu': 'mayu_frontright_shaded.png', 'patti': 'patti_front_shaded.png',
       'marquee': 'props_em/marquee.png', 'screen': 'props_em/screen.png', 'menu': 'props_em/menu.png',
       'number': 'props_em/number.png', 'door': 'props_em/door.png'}
tool = []
for k in ORDER:
    o = {"id": k, "name": NAMES[k], "x": POS[k][0], "y": POS[k][1],
         "x0": DEFAULT[k][0], "y0": DEFAULT[k][1],
         "w": SIZES[k][0], "h": SIZES[k][1], "img": IMG[k]}
    if k in SCALE:
        o["chara"] = True; o["s"] = SCALE[k]; o["s0"] = SCALE0[k]
    if k in LOCK_Y:
        o["lockY"] = True
    if k == 'marquee':
        o["cord"] = CORD                                  # 上の CORD ドットはひも(画面の上にはみ出してよい)
    if k in FLOOR_ITEMS:
        o["floor"] = True
    tool.append(o)
top = {}
for k in TOP_ITEMS:
    top[k] = {"img": IMG[k], "x": POS[k][0], "y": POS[k][1], "w": SIZES[k][0], "h": SIZES[k][1],
              "yc": CMP[k] - (REF_V[k][1] - POS[k][1])}
mx, my = POS['menu']
nx_, ny_ = POS['number']
meta = {
    "w": W, "h": H, "F_ref": F_REF, "F_min": F_MIN, "depth_ref": DEPTH_REF, "depth_min": DEPTH_MIN,
    "lower": {"img": "edit_m_lower.png", "top_ref": LB_TOP_REF, "h": LB_H},
    "top": top,
    "screen_inner": PARTS['screen_inner'], "marquee_text": [PARTS['marquee_text'][0], PARTS['marquee_text'][1] + CORD,
                                                            PARTS['marquee_text'][2], PARTS['marquee_text'][3]],
    "marquee_blink": {"img": "marquee_blink_m.png", "dy": PARTS['marquee_blink_dy'] + CORD, "w": MARQ.size[0], "h": MBH},
    "menu": {"hdr": [mx + MENU_SLOTS['hdr'][0], my + MENU_SLOTS['hdr'][1], MENU_SLOTS['hdr'][2], MENU_SLOTS['hdr'][3]],
             "items": [[mx + MENU_SLOTS[i][0], my + MENU_SLOTS[i][1], MENU_SLOTS[i][2], MENU_SLOTS[i][3]] for i in range(4)]},
    "buttons": [[nx_ + b[0], ny_ + b[1], b[2], b[3]] for b in PARTS['buttons']],
    "door": DOOR_HOT,
    "mayu": [POS['mayu'][0], POS['mayu'][1], SCALE['mayu']],
    "patti": [POS['patti'][0], POS['patti'][1], SCALE['patti']],
    "custom": CUSTOM, "tool": tool,
}
# 絵の版(絵が変わったら変わる)。ページは画像に ?v= を付けて、配置を変えた直後も古い絵を出さない
_h = hashlib.md5()
for f in ("room_edit_m.png", "edit_m_lower.png", "marquee_blink_m.png") + tuple(IMG[k] for k in TOP_ITEMS):
    _h.update(open(os.path.join(WEB, f), "rb").read())
meta["v"] = _h.hexdigest()[:10]

def stamp_page(page, names, ver):
    """ページの <img id="room"> などに ?v= を書き込む(開いた瞬間に部屋の絵が出るように)。
    JSON にも同じ版が入っているので、ページが古くてもJS側で直る。"""
    path = os.path.join(WEB, page)
    try:
        raw = io.open(path, encoding="utf-8", newline="").read()
    except IOError:
        return
    out = raw
    for n in names:
        out = re.sub(r'src="%s(\?v=[0-9a-f]+)?"' % re.escape(n), 'src="%s?v=%s"' % (n, ver), out)
    if out != raw:
        io.open(path, "w", encoding="utf-8", newline="").write(out)
        print("  %s に絵の版を書きました" % page)


stamp_page("contents_m.html", ("room_edit_m.png",), meta["v"])
json.dump(meta, io.open(os.path.join(WEB, "room_edit_m.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("room_edit_m.png / edit_m_lower.png(高さ %d) / room_edit_m_bare.png / room_edit_m.json  (重なり %d 件)"
      % (LB_H, len(bad)))
