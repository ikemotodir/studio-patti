# -*- coding: utf-8 -*-
"""スマホ用の軽い画像を作る(原画はそのまま残す)。
・絵本 book_hd/*.jpg      → book_w/*.jpg     (長辺1200・品質82)
・ギャラリー gallery/*.jpg → gallery_w/*.jpg  (長辺1200・品質82)
・絵本の表紙の小さい見本   → thumbs/book.jpg  (400px)
・黒板に貼る Spooks GS の紙 spooks_gs_paper.jpg は 360px 幅まで縮める
book.json / gallery.json に "img_w" / "file_w" / "thumb" を書き足す。
スマホ版のページはこれがあればそちらを読む(無ければ原画を読むので、消しても壊れない)。
    python make_web_images.py
"""
import io, json, os
from PIL import Image

WEB = os.path.dirname(os.path.abspath(__file__))
MAXW = 1200
Q = 82


def shrink(src, dst, maxpx, q=Q):
    """すでに新しければ作り直さない。作ったら True。"""
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return False
    im = Image.open(src)
    im = im.convert("RGB")
    w, h = im.size
    k = min(1.0, float(maxpx) / max(w, h))
    if k < 1.0:
        im = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
    return True


def kb(p):
    return os.path.getsize(p) // 1024


made = 0

# ── 絵本 ──
bp = os.path.join(WEB, "book.json")
if os.path.exists(bp):
    book = json.load(io.open(bp, encoding="utf-8"))
    for pg in book.get("pages", []):
        src = os.path.join(WEB, pg["img"].replace("/", os.sep))
        if not os.path.exists(src):
            continue
        rel = "book_w/" + os.path.basename(pg["img"])
        dst = os.path.join(WEB, rel.replace("/", os.sep))
        made += 1 if shrink(src, dst, MAXW) else 0
        pg["img_w"] = rel
    first = book.get("pages", [{}])[0].get("img")
    if first and os.path.exists(os.path.join(WEB, first.replace("/", os.sep))):
        made += 1 if shrink(os.path.join(WEB, first.replace("/", os.sep)),
                            os.path.join(WEB, "thumbs", "book.jpg"), 400, 78) else 0
        book["thumb"] = "thumbs/book.jpg"
    json.dump(book, io.open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("絵本: %d ページ / 表紙の見本 %dKB" % (len(book.get("pages", [])), kb(os.path.join(WEB, "thumbs", "book.jpg"))))

# ── ギャラリー ──
gp = os.path.join(WEB, "gallery.json")
if os.path.exists(gp):
    gal = json.load(io.open(gp, encoding="utf-8"))
    for it in gal.get("items", []):
        src = os.path.join(WEB, it["file"].replace("/", os.sep))
        if not os.path.exists(src):
            continue
        rel = "gallery_w/" + os.path.basename(it["file"])
        dst = os.path.join(WEB, rel.replace("/", os.sep))
        made += 1 if shrink(src, dst, MAXW) else 0
        it["file_w"] = rel
    json.dump(gal, io.open(gp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ギャラリー: %d 点" % len(gal.get("items", [])))

# ── 黒板に貼る小さい紙(原寸が大きすぎた) ──
sp = os.path.join(WEB, "spooks_gs_paper.jpg")
if os.path.exists(sp):
    im = Image.open(sp)
    if im.size[0] > 380:
        im.convert("RGB").resize((360, max(1, int(im.size[1] * 360.0 / im.size[0]))), Image.LANCZOS) \
          .save(sp, "JPEG", quality=86, optimize=True)
        print("spooks_gs_paper.jpg を 360px に縮めました (%dKB)" % kb(sp))

print("作り直した画像: %d 枚" % made)
