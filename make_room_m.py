# -*- coding: utf-8 -*-
"""スマホ(縦画面)用の TOP の部屋 room_m.png を組み立てる。

方針:
 ・PC版の部屋(room.png)で描いた家具や小物は、プロップ単位の切り出し
   (room_layers/objects/*.png・陰影込み)をそのまま等倍で使う。絵の質を落とさない
 ・縦画面に合わせて「奥壁を正面から見る」構図に組み替える。
   上から: ガーランド / ギャラリー+楕円窓 / 時計・Spookの額・本棚(絵本・本・鉢植え) /
   看板(戸口のすぐ上) / デザイン室・編集室の戸口+カウンター(COMPANYモニタ) /
   床(ジュークボックス・ポスト・二人)
 ・壁と床はこのスクリプトで同じパレットで描き直す(縦横比が違うので流用できない)
 ・置き場所は DEFAULT にあり、配置ツール(layout.html)が保存した layout.json の
   "mobile" があればそれで上書きする(GitHub 上でも同じように動く)
 ・切り出した部品は props_m/ に保存する。room_layers が無い環境(GitHub)では
   props_m/ から読む。配置ツールも props_m/ の絵を使う
 ・置いた物は全部 PLACED に登録し、重なりを報告する。既定の配置で意図しない
   重なりがあればビルドを失敗させる(池本さんが置いた配置は警告だけ)
 出力: room_m.png / room_m_bare.png / garland_m.png / winbars_m.png / globe_spin_m.png
       / props_m/*.png / room_m.json
"""
import glob
import io
import json
import math
import os
import sys

from PIL import Image, ImageDraw

WEB = os.path.dirname(os.path.abspath(__file__))
OBJ = os.path.join(WEB, "room_layers", "objects")
PROPS = os.path.join(WEB, "props_m")
HAVE_LAYERS = os.path.isdir(OBJ) and not os.environ.get("PATTI_NO_LAYERS")   # 検証用: GitHub と同じ条件で回す
LAYOUT_PATH = os.environ.get("PATTI_LAYOUT") or os.path.join(WEB, "layout.json")
W, H = 216, 480

P = {
 'ink':  (4, 2, 26),
 'n0': (0, 1, 43),  'n1': (0, 1, 57),  'n2': (1, 32, 68),  'n3': (2, 39, 74),  'n4': (10, 53, 96),
 'q0': (22, 9, 58), 'q1': (40, 11, 76), 'q2': (52, 16, 89), 'q3': (74, 21, 78), 'q4': (81, 35, 80),
 'q5': (110, 45, 107),
 'm0': (128, 36, 93), 'm1': (171, 37, 95), 'm2': (216, 65, 106), 'm3': (240, 106, 148), 'm4': (255, 159, 190),
 'r0': (92, 10, 44),  'r1': (152, 13, 57),
 'cor2': (253, 176, 140),
 'y1': (252, 200, 0), 'y2': (255, 227, 138),
 'b1': (36, 73, 185),
 'o0': (196, 106, 32), 'o1': (247, 152, 54), 'o2': (255, 214, 140),
}


def C(c):
    return P[c] + (255,)


class Canvas(object):
    """ドット絵を描く先。部屋そのものにも、部品(戸口+看板)にも使う。"""

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


room = Canvas(Image.new("RGBA", (W, H), (0, 0, 0, 255)))
R, PXL, DI = room.R, room.PXL, room.DI
im = room.im
PLACED = []                      # (名前, x, y, w, h) — 重なり検査用


# ═══════════ 部品の読み込み(room_layers から切り出す / 無ければ props_m から) ═══════════
def _cut(prefix):
    fs = glob.glob(os.path.join(OBJ, prefix + "*.png"))
    assert len(fs) == 1, prefix + " が1つに決まらない: %r" % fs
    s = Image.open(fs[0]).convert("RGBA")
    return s.crop(s.getchannel("A").getbbox())


def part(pid, prefix, fix=None):
    """部品を返す。room_layers があれば切り出して props_m/ に保存、無ければ props_m/ を読む。"""
    path = os.path.join(PROPS, pid + ".png")
    if HAVE_LAYERS:
        s = _cut(prefix)
        if fix:
            s = fix(s)
        os.makedirs(PROPS, exist_ok=True)
        s.save(path)
        return s
    if not os.path.exists(path):
        sys.exit("部品がありません: " + path + " (room_layers のある PC で一度ビルドしてください)")
    return Image.open(path).convert("RGBA")


def save_unit(pid, img):
    os.makedirs(PROPS, exist_ok=True)
    img.save(os.path.join(PROPS, pid + ".png"))


def put(name, sp, x, y):
    """部品を置いて、位置を登録する。"""
    im.alpha_composite(sp, (x, y))
    PLACED.append((name, x, y, sp.size[0], sp.size[1]))
    return (x, y, sp.size[0], sp.size[1])


def mark(name, x, y, w, h):
    PLACED.append((name, x, y, w, h))
    return (x, y, w, h)


# ═══════════ 置き場所(既定)。配置ツールの layout.json "mobile" で上書きできる ═══════════
DEFAULT = {
    'gallery': (8, 24),   'window': (116, 24), 'clock': (6, 88),    'spook': (46, 94),
    'shelf': (112, 98),   'doorL': (0, 129),   'doorR': (170, 129),
    'counter': (42, 200), 'globe': (42, 176),  'monitor': (63, 158), 'keyboard': (100, 201),
    'pen': (165, 185),    'jukebox': (0, 213), 'post': (176, 216),
    'mayu': (60, 230),    'patti': (126, 240),
}
SCALE = {'mayu': 0.75, 'patti': 0.75}
WALK = 10                                            # パッチは置いた所から右へこれだけ歩く
MAYU_W, MAYU_H, PATTI_W, PATTI_H = 76, 58, 36, 48    # 二人のコマの大きさ(等倍)
NAMES = {
    'gallery': 'ギャラリーのかべ', 'window': 'まど', 'clock': 'かけ時計', 'spook': 'Patti the Spookの額',
    'shelf': '本棚（絵本・本・鉢植え）', 'doorL': 'デザイン室の戸口（横にだけ動きます）',
    'doorR': '編集室の戸口（横にだけ動きます）', 'counter': 'カウンター', 'globe': '地球儀',
    'monitor': 'COMPANYのパソコン', 'keyboard': 'キーボード', 'pen': 'ペン立て',
    'jukebox': 'ジュークボックス', 'post': 'ポスト', 'mayu': 'マユちゃん',
    'patti': 'パッチ（ここから右へ%dドット歩きます）' % WALK,
}
ORDER = ['gallery', 'window', 'clock', 'spook', 'shelf', 'doorL', 'doorR', 'counter', 'globe',
         'monitor', 'keyboard', 'pen', 'jukebox', 'post', 'mayu', 'patti']
LOCK_Y = {'doorL', 'doorR'}                          # 戸口は床に立つので縦には動かさない

POS = dict(DEFAULT)
SCALE0 = dict(SCALE)


def _read_items(path, key):
    """配置の配列を読む。無ければ None。壊れていても落とさない。"""
    try:
        v = json.load(io.open(path, encoding="utf-8")).get(key)
    except Exception:
        return None
    if v is not None and not isinstance(v, list):
        print('注意: %s の "%s" が配列ではないので無視します' % (os.path.basename(path), key))
        return None
    return v


# 置き場所の出どころ: layout.json の "mobile" → 無ければ前回の room_m.json(いま公開されている配置のまま)
# → それも無ければ DEFAULT。PATTI_DEFAULT=1 なら必ず DEFAULT(検証用)
_lay, SRC = None, "既定"
if not os.environ.get("PATTI_DEFAULT"):
    _lay = _read_items(LAYOUT_PATH, "mobile")
    SRC = 'layout.json の "mobile"'
    if _lay is None:
        _lay = _read_items(os.path.join(WEB, "room_m.json"), "tool")
        SRC = "前回の room_m.json(いまの配置のまま)"
if _lay:
    for o in _lay:
        try:                                      # 全部そろって読めた項目だけ採用する
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
CUSTOM = (POS != DEFAULT) or (SCALE != SCALE0)   # 池本さんの配置かどうか(重なりは警告だけにする)


# ═══════════ 壁と床(PC版と同じパレット・同じ作法) ═══════════
WALL0, WALL1 = 10, 214                              # 奥壁の範囲(下端で床と見切る)
R(0, 0, W, H, 'n2')
# 天井
R(0, 0, W, 8, 'ink')
R(0, 5, W, 1, 'q1')
R(0, 8, W, 2, 'q0')
for x in range(4, W, 24):
    PXL(x, 3, 'r1'); PXL(x + 1, 3, 'r1')
# 奥壁: 上が明るく、下へ多段で落ちる
R(0, WALL0, W, 30, 'n3')
DI(0, 26, W, 6, 'n4', 'n3', 1)
DI(0, 40, W, 12, 'n3', 'n2')
R(0, 52, W, 84, 'n2')
DI(0, 136, W, 12, 'n2', 'n1')
R(0, 148, W, WALL1 - 148, 'n1')
DI(0, 200, W, WALL1 - 200, 'n1', 'n0')
R(0, WALL1, W, 4, 'ink')                             # 壁と床の見切り
R(0, WALL1 + 4, W, 2, 'q0')

# 床: 手前ほど広がる板。継ぎ目はマゼンタに光る(PC版と同じ流儀)
FL0 = WALL1 + 6
R(0, FL0, W, H - FL0, 'q1')
R(0, FL0, W, 3, 'q0')
SEAMS = [232, 248, 266, 286, 308, 332, 358, 386, 416, 448]
for i, y in enumerate(SEAMS):
    R(0, y, W, 1, 'm0')
    for x in range(0, W, 16):
        PXL(x + (i * 5) % 16, y + 1, 'm1')
VPX, VPY = W / 2.0, 140.0                            # 消失点(奥壁の中ほど)
for k in range(-4, 5):                               # 縦の継ぎ目は消失点へ向かう
    xb = VPX + k * 44
    for yy in range(FL0, H):
        t = (yy - VPY) / (H - VPY)
        xx = int(VPX + (xb - VPX) * t + 0.5)
        if 0 <= xx < W and yy not in SEAMS:
            PXL(xx, yy, 'q0')
for bi in range(len(SEAMS) - 1):                     # 板ごとのトーン差
    if bi % 2 == 0:
        for yy in range(SEAMS[bi] + 2, SEAMS[bi + 1] - 2):
            for xx in range(W):
                if (xx + yy + bi) % 6 == 0:
                    PXL(xx, yy, 'q2')
for x, y in [(30, 240), (150, 256), (90, 276), (180, 296), (60, 318), (140, 344), (40, 372), (170, 402), (100, 434)]:
    R(x, y, 3, 1, 'q0')
for sx in range(24, W - 16, 24):
    PXL(sx, 244, 'm1'); PXL(sx + 12, 262, 'm0')
DI(0, 462, W, 8, 'q1', 'q0')
DI(0, 470, W, 10, 'q0', 'ink')

# 配置ツール用: 何も置いていない部屋
BARE = im.copy()


# ═══════════ 戸口+看板(1つの部品として描く。看板は戸口のすぐ上、まぐさに直に乗る) ═══════════
SIGN_W, SIGN_H = 45, 16
DOOR_W, DOOR_H = 30, 62
DOOR_DX = 7                                          # 部品の左端から戸口の開口まで
DOOR_DY = SIGN_H + 4                                 # 看板の下 = まぐさ(2px)+枠(2px)
UNIT_H = DOOR_DY + DOOR_H + 3                        # 敷居とインク線まで


def door_unit(warm, textfile):
    u = Canvas(Image.new("RGBA", (SIGN_W, UNIT_H), (0, 0, 0, 0)))
    x, y, w, h = DOOR_DX, DOOR_DY, DOOR_W, DOOR_H
    u.R(x - 2, y - 2, w + 4, h + 3, 'q3')            # 枠
    u.R(x - 2, y - 2, w + 4, 1, 'q4')
    u.R(x - 2, y - 2, 1, h + 3, 'q5')
    u.R(x, y, w, h, 'ink')                           # 開口
    a, b, c = ('r0', 'o0', 'o1') if warm else ('m0', 'm2', 'm3')
    u.DI(x + 1, y + 1, w - 2, h // 3, 'q0', a)       # 奥は暗い
    u.DI(x + 1, y + 1 + h // 3, w - 2, h // 3, a, b)  # 中ほどから明るい
    u.DI(x + 1, y + 1 + 2 * (h // 3), w - 2, h - 2 * (h // 3) - 1, b, c)
    u.R(x + 1, y + h - 5, w - 2, 4, c)               # 足元は光でいっぱい
    for yy in range(y + 1 + h // 3, y + h - 5):      # 奥の廊下の明かりが縦に差す
        if (yy - y) % 2 == 0:
            u.PXL(x + w // 2, yy, c); u.PXL(x + w // 2 - 1, yy, c)
    u.R(x - 2, y - 4, w + 4, 2, 'q4')                # まぐさ(上枠)
    u.R(x - 2, y - 4, w + 4, 1, 'q5')
    u.R(x, y + h, w, 2, 'q3')                        # 敷居
    u.R(x, y + h + 2, w, 1, 'ink')
    # 看板(札)。戸口(枠込み)の中心に合わせる: 枠 x-2..x+w+2 の中心 = 22, 札の中心 = 22.5
    u.R(0, 0, SIGN_W, SIGN_H, 'q0')
    u.R(0, 0, SIGN_W, 1, 'q4'); u.R(0, 0, 1, SIGN_H, 'q4')
    u.R(0, SIGN_H - 1, SIGN_W, 1, 'ink'); u.R(SIGN_W - 1, 0, 1, SIGN_H, 'ink')
    t = Image.open(os.path.join(WEB, textfile)).convert("RGBA")
    u.im.alpha_composite(t, ((SIGN_W - t.size[0]) // 2, (SIGN_H - t.size[1]) // 2))
    return u.im


HOT = {}
DOOR_Y = DEFAULT['doorL'][1] + DOOR_DY               # = 149。敷居の下端が壁と床の見切りに乗る
assert DOOR_Y + DOOR_H + 3 == WALL1, "戸口の足元が見切りに乗っていない"
SIGN = {}
DOOR_UNITS = {}
for key, warm, tf in (('doorL', True, "sign_design_s.png"), ('doorR', False, "sign_hensyu_s.png")):
    DOOR_UNITS[key] = door_unit(warm, tf)
    save_unit(key, DOOR_UNITS[key])

# ═══════════ 部品(PC版の切り出しを等倍で) ═══════════
if not HAVE_LAYERS:                                  # 足りない部品は最初に全部並べて止める
    _need = ['gallery', 'window', 'clock', 'spook', 'globe', 'monitor', 'keyboard', 'pen', 'jukebox', 'post',
             'shelf_raw', 'books', 'ehon', 'plant', 'counter_raw']
    _miss = [p for p in _need if not os.path.exists(os.path.join(PROPS, p + ".png"))]
    if _miss:
        sys.exit("部品がありません: props_m/{%s}.png (room_layers のある PC で一度ビルドしてコミットしてください)"
                 % ",".join(_miss))
# ガーランド(3コマ)。room には1コマ目、動くぶんは garland_m.png へ
g = Image.open(os.path.join(WEB, "garland.png")).convert("RGBA")
GX0, GW = 84, W
gm = Image.new("RGBA", (GW * 3, 26), (0, 0, 0, 0))
for f in range(3):
    gm.alpha_composite(g.crop((f * 384 + GX0, 0, f * 384 + GX0 + GW, 26)), (f * GW, 0))
gm.save(os.path.join(WEB, "garland_m.png"))
GARLAND_Y = 4
im.alpha_composite(gm.crop((0, 0, GW, 26)), (0, GARLAND_Y))
BARE.alpha_composite(gm.crop((0, 0, GW, 26)), (0, GARLAND_Y))


def clean_window(win):
    """窓ガラスの中の「暗い雲」はスマホでは欠けに見えるので、まわりの空のディザで埋める。"""
    wp = win.load()
    for yy in range(6, 34):
        for xx in range(8, 46):
            r_, g_, b_, a_ = wp[xx, yy]
            if a_ and r_ + g_ + b_ < 60 and (r_, g_, b_) != P['ink']:
                for dx in range(1, 40):              # 同じ行・同じ市松位相の空の色を借りる
                    for sx in (xx - 2 * dx, xx + 2 * dx):
                        if 8 <= sx < 46 and sum(wp[sx, yy][:3]) >= 60 and wp[sx, yy][3]:
                            wp[xx, yy] = wp[sx, yy]; break
                    else:
                        continue
                    break
    return win


SPR = {
    'gallery': part('gallery', "props__016_"),
    'window': part('window', "window__001_", clean_window),
    'clock': part('clock', "furniture__009_"),
    'spook': part('spook', "props__017_"),
    'globe': part('globe', "furniture__011_"),
    'monitor': part('monitor', "furniture__013_"),
    'keyboard': part('keyboard', "furniture__014_"),
    'pen': part('pen', "props__026_"),
    'jukebox': part('jukebox', "furniture__019_"),
    'post': part('post', "props__018_"),
}
shelf_raw = part('shelf_raw', "furniture__006_")     # 二段の壁棚(板の行だけ使う)
books = part('books', "furniture__007_")
ehon = part('ehon', "furniture__008_")
plant = part('plant', "furniture__012_")
counter_raw = part('counter_raw', "furniture__010_")  # 290px。両端を残して真ん中を詰める

# 本棚: 長い板(棚板の行を伸ばす)に 絵本・本・鉢植え を並べる
PLANK_H = 4
SHELF_W, SHELF_H = 102, ehon.size[1] + PLANK_H
shelf = Image.new("RGBA", (SHELF_W, SHELF_H), (0, 0, 0, 0))
plank_src = shelf_raw.crop((0, 0, shelf_raw.size[0], PLANK_H))
plank = Image.new("RGBA", (SHELF_W, PLANK_H), (0, 0, 0, 0))
plank.alpha_composite(plank_src.crop((0, 0, 4, PLANK_H)), (0, 0))
xx = 4
while xx < SHELF_W - 4:
    seg = plank_src.crop((8, 0, min(8 + (SHELF_W - 4 - xx), 64), PLANK_H))
    plank.alpha_composite(seg, (xx, 0))
    xx += seg.size[0]
plank.alpha_composite(plank_src.crop((plank_src.size[0] - 4, 0, plank_src.size[0], PLANK_H)), (SHELF_W - 4, 0))
SHELF_PARTS = {                                     # 部品内の位置(板の上にそろえる)
    'ehon': (2, SHELF_H - PLANK_H - ehon.size[1]),
    'books': (28, SHELF_H - PLANK_H - books.size[1]),
    'plant': (SHELF_W - 1 - plant.size[0], SHELF_H - PLANK_H - plant.size[1]),
    'plank': (0, SHELF_H - PLANK_H),
}
shelf.alpha_composite(ehon, SHELF_PARTS['ehon'])
shelf.alpha_composite(books, SHELF_PARTS['books'])
shelf.alpha_composite(plant, SHELF_PARTS['plant'])
shelf.alpha_composite(plank, SHELF_PARTS['plank'])
save_unit('shelf', shelf)

# カウンター: 両端の66pxを残して真ん中を詰める(端の造作を切らない)
END = 66
counter = Image.new("RGBA", (END * 2, counter_raw.size[1]), (0, 0, 0, 0))
counter.alpha_composite(counter_raw.crop((0, 0, END, counter_raw.size[1])), (0, 0))
counter.alpha_composite(counter_raw.crop((counter_raw.size[0] - END, 0, counter_raw.size[0], counter_raw.size[1])), (END, 0))
save_unit('counter', counter)

# 大きさの一覧(配置ツール用・はみ出し判定用)
SIZES = {k: SPR[k].size for k in SPR}
SIZES.update({'shelf': shelf.size, 'counter': counter.size,
              'doorL': (SIGN_W, UNIT_H), 'doorR': (SIGN_W, UNIT_H),
              'mayu': (MAYU_W, MAYU_H), 'patti': (PATTI_W, PATTI_H)})
# 画面の外に出た物は中へ寄せる(池本さんの配置でも公開を止めない)
for k in ORDER:
    w_, h_ = SIZES[k]
    x_, y_ = POS[k]
    if k in SCALE:                                   # 二人は縮めた見た目の箱(中央寄せ・足元ぞろえ)
        s_ = SCALE[k]
        ox, oy = w_ * (1 - s_) / 2.0, h_ * (1 - s_)
        bw = w_ * s_ + (WALK if k == 'patti' else 0)
        nx = int(min(max(x_, math.ceil(-ox)), math.floor(W - bw - ox)))
        ny = int(min(max(y_, math.ceil(-oy)), math.floor(H - h_ * s_ - oy)))
    else:
        nx, ny = min(max(x_, 0), W - w_), min(max(y_, 0), H - h_)
    if k in LOCK_Y:
        ny = y_
    if (nx, ny) != (x_, y_):
        print("注意: %s が画面からはみ出すので (%d,%d) に寄せました" % (NAMES[k], nx, ny))
        POS[k] = (nx, ny)

# ═══════════ 置く(奥から手前の順。壁の物 → 戸口+看板 → カウンターまわり → 床の物) ═══════════
HOT['gallery'] = put('gallery', SPR['gallery'], *POS['gallery'])
HOT['window'] = put('window', SPR['window'], *POS['window'])
HOT['clock'] = put('clock', SPR['clock'], *POS['clock'])
HOT['spook'] = put('spook', SPR['spook'], *POS['spook'])
sx, sy = POS['shelf']
im.alpha_composite(shelf, (sx, sy))
for pid, spimg in (('ehon', ehon), ('books', books), ('plant', plant), ('plank', plank)):
    ox, oy = SHELF_PARTS[pid]
    mark('本棚:' + pid, sx + ox, sy + oy, spimg.size[0], spimg.size[1])
# 絵本の当たり判定は指で押せる大きさに(棚板と隙間ぶん広げる。絵は変えない)
HOT['book'] = (sx - 2, sy + SHELF_PARTS['ehon'][1] - 5, SHELF_PARTS['books'][0] + 2, SHELF_H + 5)
# 戸口+看板(壁の物より手前、カウンターより奥。配置ツールの並び順と同じ)
for key in ('doorL', 'doorR'):
    ux, uy = POS[key]
    im.alpha_composite(DOOR_UNITS[key], (ux, uy))
    SIGN[key] = mark(key + ':看板', ux, uy, SIGN_W, SIGN_H)
    mark(key + ':戸口', ux + DOOR_DX - 2, uy + DOOR_DY - 4, DOOR_W + 4, DOOR_H + 7)
    HOT[key] = (ux + DOOR_DX, uy + DOOR_DY, DOOR_W, DOOR_H)
cx, cy = POS['counter']
put('counter', counter, cx, cy)
put('globe', SPR['globe'], *POS['globe'])
GLOBE = (POS['globe'][0], POS['globe'][1], SPR['globe'].size[0], SPR['globe'].size[1])
MON = put('monitor', SPR['monitor'], *POS['monitor'])
HOT['company'] = MON
SCREEN = [MON[0] + 4, MON[1] + 4, 92, 28]            # 画面の内側
put('keyboard', SPR['keyboard'], *POS['keyboard'])
put('pen', SPR['pen'], *POS['pen'])
HOT['jukebox'] = put('jukebox', SPR['jukebox'], *POS['jukebox'])
HOT['post'] = put('post', SPR['post'], *POS['post'])

# 二人(HTML側が room_m.json を読んで置く)。重なり検査のために登録だけする
def chara_box(key, w, h):
    x, y = POS[key]; s = SCALE[key]
    return (x + w * (1 - s) / 2.0, y + h * (1 - s), w * s, h * s)
mb = chara_box('mayu', MAYU_W, MAYU_H)
pb = chara_box('patti', PATTI_W, PATTI_H)
mark('mayu', int(mb[0]), int(mb[1]), int(round(mb[2])), int(round(mb[3])))
mark('patti(walk)', int(pb[0]), int(pb[1]), int(round(pb[2])) + WALK, int(round(pb[3])))
FEET = [POS['jukebox'][1] + SPR['jukebox'].size[1], POS['post'][1] + SPR['post'].size[1],
        POS['mayu'][1] + MAYU_H, POS['patti'][1] + PATTI_H]
GROUND = max(288, max(FEET))                         # テキストボックスはこれより下

# 窓の桟(おばけが桟の向こうを飛ぶ用)。PC版の桟から窓の範囲だけ切り出す
win = SPR['window']
if HAVE_LAYERS:
    bars = Image.open(os.path.join(WEB, "window_bars.png")).convert("RGBA")
    bars.crop((244, 10, 244 + win.size[0], 10 + win.size[1])).save(os.path.join(WEB, "winbars_m.png"))

# 地球儀の回転アニメ: PC版のコマ(背景つき)から、地球儀の形だけを抜く
glb = SPR['globe']
gs = Image.open(os.path.join(WEB, "globe_spin.png")).convert("RGBA")
gmask = glb.getchannel("A")
gsm = Image.new("RGBA", (glb.size[0] * 6, glb.size[1]), (0, 0, 0, 0))
for f in range(6):
    fr = gs.crop((f * 24 + 2, 2, f * 24 + 2 + glb.size[0], 2 + glb.size[1]))
    fr.putalpha(gmask)
    gsm.paste(fr, (f * glb.size[0], 0))
gsm.save(os.path.join(WEB, "globe_spin_m.png"))

# ═══════════ 重なり検査 ═══════════
ALLOWED = {
    frozenset(('monitor', 'counter')),               # モニタの台はカウンターに乗る
    frozenset(('keyboard', 'counter')),
    frozenset(('keyboard', 'monitor')),              # PC版と同じくキーボードは台の手前
}
def isect(a, b):
    ax0, ay0, ax1, ay1 = a[1], a[2], a[1] + a[3], a[2] + a[4]
    bx0, by0, bx1, by1 = b[1], b[2], b[1] + b[3], b[2] + b[4]
    return min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0)
bad = []
for i in range(len(PLACED)):
    for j in range(i + 1, len(PLACED)):
        a, b = PLACED[i], PLACED[j]
        ow, oh = isect(a, b)
        if ow > 0 and oh > 0:
            key = frozenset((a[0], b[0]))
            if a[0].startswith('本棚:') and b[0].startswith('本棚:'):
                continue
            if oh <= 1 and (a[0].endswith(':戸口') or b[0].endswith(':戸口')):
                continue                             # 敷居の下のインク線(1行)に床の物が乗るのは許す
            if key not in ALLOWED:
                bad.append("%s x %s (%dx%d)" % (a[0], b[0], ow, oh))
for nm, x, y, w, h in PLACED:
    if x < 0 or y < 0 or x + w > W or y + h > H:
        bad.append("%s が画面からはみ出す (%d,%d,%d,%d)" % (nm, x, y, w, h))
if bad:
    if CUSTOM:
        print("注意(池本さんの配置で重なっている所):\n  " + "\n  ".join(bad))
    else:
        raise SystemExit("重なり事故:\n  " + "\n  ".join(bad))

# ═══════════ ビネット(四隅を沈める。PC版の空気感に合わせる) ═══════════
def vignette(img):
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            dx = abs(xx - W / 2.0) / (W / 2.0)
            dy = abs(yy - 180.0) / 200.0
            dd = (dx ** 2.3 + dy ** 2.3) ** 0.5
            n = 2 if dd > 1.06 else (1 if dd > 0.93 else (1 if dd > 0.84 and (xx + yy) % 2 == 0 else 0))
            if n:
                r, g_, b, a = px[xx, yy]
                k = 0.88 if n == 1 else 0.76
                px[xx, yy] = (int(r * k), int(g_ * k), int(b * k), a)


vignette(im)
vignette(BARE)
im.convert("RGB").save(os.path.join(WEB, "room_m.png"))
BARE.convert("RGB").save(os.path.join(WEB, "room_m_bare.png"))

# 配置ツール用の一覧: いまの置き場所(=公開される配置)と、「最初にもどす」用の既定(x0,y0,s0)
IMG = {'mayu': 'mayu_shaded.png', 'patti': 'patti_shaded.png'}
tool = []
for k in ORDER:
    o = {"id": k, "name": NAMES[k], "x": POS[k][0], "y": POS[k][1],
         "x0": DEFAULT[k][0], "y0": DEFAULT[k][1],
         "w": SIZES[k][0], "h": SIZES[k][1], "img": IMG.get(k, "props_m/%s.png" % k)}
    if k in SCALE:
        o["chara"] = True; o["s"] = SCALE[k]; o["s0"] = SCALE0[k]
    if k in LOCK_Y:
        o["lockY"] = True
    if k == 'patti':
        o["walk"] = WALK
    tool.append(o)

meta = {
    "w": W, "h": H, "ground": GROUND, "garland_y": GARLAND_Y,
    "screen": SCREEN,                            # COMPANYモニタの画面の内側
    "globe": list(GLOBE[:2]), "globe_size": list(GLOBE[2:]),
    "clock": list(HOT['clock'][:2]), "window": list(HOT['window'][:2]),
    "signs": {"L": list(SIGN['doorL']), "R": list(SIGN['doorR'])},
    "mayu": [POS['mayu'][0], POS['mayu'][1], SCALE['mayu']],
    "patti": [POS['patti'][0], POS['patti'][1], SCALE['patti']],
    "walk": WALK,
    "hot": {k: list(v) for k, v in HOT.items()},
    "placed": [list(p) for p in PLACED],
    "custom": CUSTOM,
    "tool": tool,
}
json.dump(meta, io.open(os.path.join(WEB, "room_m.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("room_m.png", im.size, "/ room_m_bare.png / garland_m.png / winbars_m.png / globe_spin_m.png / props_m / room_m.json",
      "(重なり %d 件)" % len(bad))
