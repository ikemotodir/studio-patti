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
scene.alpha_composite(mayu.crop((0, 0, 76, 58)), (66, 112))
scene.alpha_composite(patti.crop((0, 0, 36, 48)), (196, 122))
big = scene.resize((384 * 3, 240 * 3), Image.NEAREST)      # 1152x720
ogp = Image.new("RGBA", (1200, 630), (5, 3, 15, 255))
ogp.alpha_composite(big.crop((0, 45, 1152, 675)), (24, 0))  # 上下を45pxずつ落として630に
ogp.convert("RGB").save(os.path.join(HERE, "ogp.png"))
print("ogp.png written", (1200, 630))

# ── タブに出るアイコン ────────────────────────────────
fav = Image.new("RGBA", (36, 36), (11, 8, 32, 255))
fav.alpha_composite(patti.crop((0, 0, 36, 36)), (0, 0))
fav.resize((72, 72), Image.NEAREST).save(os.path.join(HERE, "favicon.png"))
print("favicon.png written (72, 72)")
