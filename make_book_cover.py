# -*- coding: utf-8 -*-
"""絵本にカーソルを合わせたときに出る「表紙」の画像 ehon_cover.png を作る。

 ・もとは本物の表紙 book_hd/00_Front.jpg(1800x1800)
 ・部屋の中の絵本は 24x24 ドットの正方形。画面では最大 8 倍まで大きくなるので、
   8 倍の密度(192x192)で書き出す。これ以上細かくしても見た目は変わらない
 ・まわりの 1 ドットぶん(8px)は部屋と同じ黒フチにして、ふだんの札と同じ座りにする
 ・線画が細いので、少しだけ濃くしてから縮める
 出力: ehon_cover.png
"""
import io
import os

from PIL import Image, ImageEnhance

WEB = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(WEB, "book_hd", "00_Front.jpg")
DENS = 8                                   # 1ドット = 8px
SIDE = 24 * DENS                           # 192
PAD = 1 * DENS                             # 黒フチ(部屋の枠と同じ1ドット)
INK = (4, 2, 26)

src = Image.open(SRC).convert("RGB")
w, h = src.size
side = min(w, h)                           # 念のため正方形に切る
src = src.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))

art = ImageEnhance.Contrast(src).enhance(1.35)          # 細い線を残す
art = art.resize((SIDE - PAD * 2, SIDE - PAD * 2), Image.LANCZOS)

im = Image.new("RGB", (SIDE, SIDE), INK)
im.paste(art, (PAD, PAD))
im.save(os.path.join(WEB, "ehon_cover.png"))
print("ehon_cover.png", im.size, "(1ドット = %dpx)" % DENS)
