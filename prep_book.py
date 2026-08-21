# -*- coding: utf-8 -*-
"""絵本の高画質スキャン(【PB】*.jpg)を絵本ビューア用に取り込む。
・Front / Page2-3 ... Page40 を順番に並べる(裏表紙Backは載せない)
・見開きスキャン(Page2-3など)は spread=true で見開き全面表示
・文章は既存 book.json(ブログ原文の改行)の該当ページから引き継ぐ
"""
from PIL import Image
import os, glob, json, io, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "..", "サイト用画像", "gallery"))
DST = os.path.join(HERE, "book_hd")
os.makedirs(DST, exist_ok=True)
MAX = 1800

def sort_key(path):
    n = os.path.splitext(os.path.basename(path))[0].replace("【PB】", "")
    if n.lower() == "front":
        return (0, 0)
    if n.lower() == "back":
        return (99, 0)
    m = re.match(r"Page(\d+)", n)
    return (1, int(m.group(1))) if m else (50, 0)

files = sorted(glob.glob(os.path.join(SRC, "【PB】*")), key=sort_key)
files = [f for f in files                       # 裏表紙は展示しない(池本指示)
         if os.path.splitext(os.path.basename(f))[0].replace("【PB】", "").lower() != "back"]
# 文章の引き継ぎ元は必ずブログ原文のバックアップ。
# book.json 自身から読むと、再ビルドのたびに本文が1ページずつズレて消える。
BASE = os.path.join(HERE, "book_blog_backup.json")
if not os.path.exists(BASE):
    raise SystemExit("book_blog_backup.json が見つかりません(本文の引き継ぎ元)")
old = json.load(io.open(BASE, encoding="utf-8"))
old_pages = old["pages"]

pages = []
for i, p in enumerate(files):
    name = os.path.splitext(os.path.basename(p))[0].replace("【PB】", "")
    im = Image.open(p)
    im.thumbnail((MAX, MAX), Image.LANCZOS)
    out = f"{i:02d}_{name}.jpg".replace(" ", "_")
    im.convert("RGB").save(os.path.join(DST, out), quality=88, optimize=True)
    # 元データから文章を引き継ぐ(表紙・裏表紙・扉は文章なし)
    src_i = i - 1                      # Frontぶんズレる
    jp, en = [], []
    if 0 <= src_i < len(old_pages):
        jp = old_pages[src_i].get("jp", [])
        en = old_pages[src_i].get("en", [])
    is_cover = name.lower() in ("front", "back")
    pages.append({
        "img": "book_hd/" + out,
        "jp": [] if is_cover else jp,
        "en": [] if is_cover else en,
        "spread": True if is_cover else (len(jp) == 0),
        "label": name,
    })
    print(f"{out}  {im.size[0]}x{im.size[1]}  {'見開き' if pages[-1]['spread'] else '文章あり'}")

json.dump({"title": old["title"], "dedication": old.get("dedication"),
           "source": old.get("source"), "pages": pages},
          io.open(os.path.join(HERE, "book.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("book.json:", len(pages), "pages (高画質スキャン版)")
