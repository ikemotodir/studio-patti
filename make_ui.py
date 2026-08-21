# -*- coding: utf-8 -*-
"""サイトのUI用の画像を書き出す。
・rotate_phone.png … スマホが縦→横にくるっと回る10コマ（48x48）
  角度ごとに矩形の頂点を計算して多角形で塗るので、拡大しても輪郭が濁らない。
・ogp.png … SNSやLINEに貼ったときのサムネイル（1200x630）
・favicon.png … ブラウザのタブに出るパッチくんの顔
"""
from PIL import Image, ImageDraw
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
S = 48                                   # 1コマの大きさ
ANGLES = [0, 0, 0, 15, 30, 45, 60, 75, 90, 90]

INK = (14, 10, 34)
BODY = (232, 228, 244)
BODY2 = (176, 170, 208)
SCREEN = (58, 46, 130)
SCREEN2 = (120, 190, 255)
ACCENT = (252, 200, 0)

BW, BH = 17, 31                          # 本体の幅と高さ(縦持ち)


def corners(w, h, deg, cx, cy):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return pts


sheet = Image.new("RGBA", (S * len(ANGLES), S), (0, 0, 0, 0))
for i, deg in enumerate(ANGLES):
    fr = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(fr)
    cx = cy = S / 2 - .5
    d.polygon(corners(BW + 2, BH + 2, deg, cx, cy), fill=INK)          # 縁取り
    d.polygon(corners(BW, BH, deg, cx, cy), fill=BODY)                 # 本体
    d.polygon(corners(BW - 4, BH - 9, deg, cx, cy), fill=INK)          # 画面の枠
    lit = i >= len(ANGLES) - 2                                         # 横向きになったら画面が点く
    d.polygon(corners(BW - 6, BH - 11, deg, cx, cy),
              fill=SCREEN2 if lit else SCREEN)
    # スピーカーとホームボタン(短辺の中央にくるよう回転させて置く)
    a = math.radians(deg)
    for off, col, ln in ((-BH / 2 + 2.5, BODY2, 5), (BH / 2 - 2.5, BODY2, 3)):
        px = cx - off * math.sin(a)
        py = cy + off * math.cos(a)
        d.line([(px - ln / 2 * math.cos(a), py - ln / 2 * math.sin(a)),
                (px + ln / 2 * math.cos(a), py + ln / 2 * math.sin(a))], fill=col)
    if lit:                                                            # 点いた画面にきらり
        d.point((int(cx + 4), int(cy - 3)), fill=ACCENT)
    sheet.alpha_composite(fr, (i * S, 0))

sheet.save(os.path.join(HERE, "rotate_phone.png"))
print("rotate_phone.png written", sheet.size, len(ANGLES), "コマ")


# ── SNS共有用のサムネイル(OGP) ────────────────────────
# 部屋を整数倍(3倍)で拡大してから上下を切る。半端な拡大率にしないのがコツ。
room = Image.open(os.path.join(HERE, "room.png")).convert("RGBA")
mayu = Image.open(os.path.join(HERE, "mayu_shaded.png")).convert("RGBA")
patti = Image.open(os.path.join(HERE, "patti_shaded.png")).convert("RGBA")
scene = room.copy()
scene.alpha_composite(mayu.crop((0, 0, 76, 58)).resize((57, 44), Image.NEAREST), (105, 140))
scene.alpha_composite(patti.crop((0, 0, 36, 48)).resize((27, 36), Image.NEAREST), (205, 148))
big = scene.resize((384 * 3, 240 * 3), Image.NEAREST)      # 1152x720
ogp = Image.new("RGBA", (1200, 630), (5, 3, 15, 255))
ogp.alpha_composite(big.crop((0, 45, 1152, 675)), (24, 0))  # 上下を45pxずつ落として630に
ogp.convert("RGB").save(os.path.join(HERE, "ogp.png"))
print("ogp.png written", (1200, 630))

# ── ナビのロゴ: 池本の正式ロゴ「PIXEL STUDIO PATTI【White】」を論理ドットに落とす ──
_lg = Image.open(os.path.join(HERE, "..", "..", "..", "ロゴ", "PIXEL STUDIO PATTI【White】.png")).convert("RGBA")
_alpha = _lg.getchannel("A")
_bbx = _alpha.getbbox()
_lg = _lg.crop(_bbx)
# ドットの格子サイズを推定(アルファの縦エッジ間隔の最頻値)
_ap = _lg.getchannel("A").load()
_w9, _h9 = _lg.size
_runs = {}
for _yy in range(0, _h9, max(1, _h9 // 8)):
    _last, _run = None, 0
    for _xx in range(_w9):
        _on = _ap[_xx, _yy] > 128
        if _on == _last:
            _run += 1
        else:
            if _last is not None and 3 <= _run <= 80:
                _runs[_run] = _runs.get(_run, 0) + 1
            _last, _run = _on, 1
_grid = min(_runs, key=lambda k: (-_runs[k], k)) if _runs else 17
_lw, _lh = max(1, round(_w9 / _grid)), max(1, round(_h9 / _grid))
_logo = _lg.resize((_lw, _lh), Image.NEAREST)
if _lh != 10:                                        # ナビでは高さ10pxで使う
    _logo = _logo.resize((max(1, round(_lw * 10 / _lh)), 10), Image.NEAREST)
_logo.save(os.path.join(HERE, "nav_logo.png"))
print("nav_logo.png written", _logo.size, "grid=", _grid)

# ── タブに出るアイコン ────────────────────────────────
fav = Image.new("RGBA", (36, 36), (11, 8, 32, 255))
fav.alpha_composite(patti.crop((0, 0, 36, 36)), (0, 0))
fav.resize((72, 72), Image.NEAREST).save(os.path.join(HERE, "favicon.png"))
print("favicon.png written (72, 72)")
