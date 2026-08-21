# -*- coding: utf-8 -*-
"""サイト用画像\\gallery の原画をWeb用に最適化して web\\gallery へ入れ、gallery.json を作る。
・【数字】が付いた画像だけを、その番号順に展示する（番号なし・【PB】は対象外）
・表示名は【数字】を取り除いたもの
・長辺1600pxへ縮小、JPEG品質88（透過PNGはPNGのまま）
・購入リンクは gallery_links.json。キーは【番号】が正（例 "7"）。作品名やファイル名でも引ける
"""
from PIL import Image
import os, glob, json, io, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "..", "サイト用画像", "gallery"))
DST = os.path.join(HERE, "gallery")
os.makedirs(DST, exist_ok=True)
MAX = 1600
NUM = re.compile(r"^【(\d+)】\s*(.+)$")

links = {}
lp = os.path.join(HERE, "gallery_links.json")
if os.path.exists(lp):
    links = json.load(io.open(lp, encoding="utf-8"))

found, skipped = [], []
for p in glob.glob(os.path.join(SRC, "*")):
    ext = os.path.splitext(p)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        continue
    stem = os.path.splitext(os.path.basename(p))[0]
    m = NUM.match(stem)
    if not m:
        skipped.append(stem)
        continue
    found.append((int(m.group(1)), m.group(2).strip(), p))

found.sort(key=lambda t: t[0])
items = []
for no, disp, p in found:
    im = Image.open(p)
    im.thumbnail((MAX, MAX), Image.LANCZOS)
    safe = re.sub(r'[\\/:*?"<>|]', "_", disp)
    if not safe.isascii():          # 日本語のファイル名は公開URLで化けやすいので英数字に寄せる
        safe = "artwork"
    has_alpha = im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 255
    out = f"{no:02d}_{safe}" + (".png" if has_alpha else ".jpg")
    if has_alpha:
        im.convert("RGBA").save(os.path.join(DST, out), optimize=True)
    else:
        im.convert("RGB").save(os.path.join(DST, out), quality=88, optimize=True)
    ent = links.get(str(no), links.get(disp, links.get(stem, "")))   # 番号を最優先で引く
    if isinstance(ent, dict):
        title = ent.get("title") or disp
        url = ent.get("url", "")
    else:
        title, url = disp, ent
    items.append({"file": "gallery/" + out, "title": title, "url": url, "no": no})
    kb = os.path.getsize(os.path.join(DST, out)) // 1024
    print(f"[{no:2d}] {title}  {im.size[0]}x{im.size[1]}  {kb}KB" + ("  購入リンクあり" if url else ""))

json.dump({"items": items}, io.open(os.path.join(HERE, "gallery.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("gallery.json:", len(items), "items")
if skipped:
    print(f"(番号なしの画像 {len(skipped)}枚 は展示対象外)")

keys = {str(i["no"]) for i in items} | {i["title"] for i in items}
for k in links:
    if k.startswith("_"):
        continue
    if k not in keys:
        print(f"[!] リンクのキーがどの作品にも一致しません → 「{k}」")
for i in items:
    if not i["url"]:
        print(f'[ ] 購入リンク未設定: "{i["title"]}"')
