# -*- coding: utf-8 -*-
"""サイトの決まりごと検査。直したバグが戻っていないかを機械で見張る。
    python qa_site.py           … web/ を検査して結果を出す(NGがあれば終了コード1)
GitHub の反映ワークフローからも呼べるように、外部ライブラリは使わない。"""
import io, json, os, re, sys

WEB = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "m.html", "design.html", "design_m.html", "contents.html", "contents_m.html", "layout.html"]
PHONE = ["m.html", "design_m.html", "contents_m.html"]
ng = []
ok = 0


def check(name, cond, detail=""):
    global ok
    if cond:
        ok += 1
    else:
        ng.append(name + (("  " + detail) if detail else ""))


def read(p):
    return io.open(os.path.join(WEB, p), encoding="utf-8", newline="").read()


# ── 1) 参照しているファイルが本当にあるか(GitHub は大文字小文字を区別する) ──
REF = re.compile(r'(?:src|href)="([^"#?:]+?)(?:\?[^"]*)?"|url\((?!data:)([^)\'"]+?)(?:\?[^)]*)?\)')
SKIP = ("http://", "https://", "//", "mailto:", "javascript:", "#")
listing = {}


def exists_exact(rel):
    """大文字小文字までぴったり合う物があるか(GitHub Pages と同じ判定)。"""
    rel = rel.replace("\\", "/").split("?")[0]
    d, n = os.path.split(rel)
    key = d
    if key not in listing:
        full = os.path.join(WEB, d) if d else WEB
        listing[key] = set(os.listdir(full)) if os.path.isdir(full) else set()
    return n in listing[key]


for page in PAGES:
    s = read(page)
    for m in REF.finditer(s):
        rel = (m.group(1) or m.group(2) or "").strip()
        if not rel or rel.startswith(SKIP) or "$" in rel or "'" in rel or "+" in rel:
            continue                                   # JS で組み立てるURLは対象外
        check("%s が参照する %s が無い" % (page, rel), exists_exact(rel))

# データの中の画像も見る
for j, keys in (("book.json", ("pages", "img")), ("gallery.json", ("items", "img")), ("metaverse.json", None)):
    p = os.path.join(WEB, j)
    if not os.path.exists(p):
        continue
    d = json.load(io.open(p, encoding="utf-8"))
    files = []
    if j == "metaverse.json":
        for g in d:
            files += list(g.get("files", []))
    else:
        for it in d.get(keys[0], []):
            if it.get(keys[1]):
                files.append(it[keys[1]])
    for f in files:
        check("%s が指す %s が無い" % (j, f), exists_exact(f))

# 編集室が使う動画サムネ
cont = read("contents.html")
for t, vid in re.findall(r"\{t:'(v|y)',id:'([^']+)'\}", cont):
    check("thumbs/%s%s.jpg が無い" % (t, vid), exists_exact("thumbs/%s%s.jpg" % (t, vid)))

# ── 2) 社内向けの下書き文が公開ページに出ていないか ──
NGWORD = ["仮です", "仮のボード", "清書します", "フォルダに入れてビルド", "TODO", "FIXME", "ここに書く"]
for page in PAGES + ["design_data.js"]:
    s = read(page)
    for w in NGWORD:
        check("%s に社内向けの文言『%s』が残っている" % (page, w), w not in s)

# ── 3) 旧ページ(anime.html)へ飛ぶ導線が残っていないか ──
for page in PAGES:
    check("%s から anime.html へ飛ぶ所が残っている" % page, "anime.html" not in read(page))

# ── 4) スマホ版3ページの決まりごと ──
for page, room, roomjson in (("m.html", "room_m.png", "room_m.json"),
                             ("design_m.html", "room_design_m.png", "room_design_m.json"),
                             ("contents_m.html", "room_edit_m.png", "room_edit_m.json")):
    s = read(page)
    # 置き場所が決まるまで小物を出さない(開いた瞬間の謎グラフィック防止)
    check("%s に「置き場所が決まるまで小物を隠す」指定が無い" % page,
          "#stage > :not(#room) { visibility: hidden; }" in s)
    # 部屋の絵は HTML に版つきで直書き(開いた瞬間に出す)
    m = re.search(r'<img id="room" src="%s\?v=([0-9a-f]+)"' % re.escape(room), s)
    check("%s の部屋の絵に版が書かれていない" % page, bool(m))
    if m:
        v = json.load(io.open(os.path.join(WEB, roomjson), encoding="utf-8")).get("v")
        check("%s の版が %s と食い違う" % (page, roomjson), m.group(1) == v, "%s vs %s" % (m.group(1), v))
    # 戻るで帰ってきたときに動かなくなる one-shot フラグを戻しているか
    check("%s に「戻るで帰ってきたとき」の戻し処理が無い" % page, "pageshow" in s)

check("index.html に「戻るで帰ってきたとき」の戻し処理が無い", "pageshow" in read("index.html"))

# ── 5) PC版とスマホ版の行き来 ──
for pc, ph in (("index.html", "m.html"), ("design.html", "design_m.html"), ("contents.html", "contents_m.html")):
    s = read(pc)
    check("%s にスマホ版への振り分けが無い" % pc, "location.replace('%s'" % ph in s)
    check("%s が ?pc=1 を覚えない(押すたびスマホ版に戻される)" % pc, "sessionStorage.setItem('patti-pc'" in s)
    check("%s から %s へ戻るリンクが無い" % (ph, pc), pc in read(ph))

# ── 6) 部屋の数字(json)とページの食い違い ──
for roomjson in ("room_m.json", "room_design_m.json", "room_edit_m.json"):
    d = json.load(io.open(os.path.join(WEB, roomjson), encoding="utf-8"))
    check("%s に絵の版(v)が無い" % roomjson, bool(d.get("v")))
    if "F_ref" in d:
        check("%s の いちばん短い画面の足元が 290 を超える" % roomjson,
              d["F_min"] + d["depth_min"] <= 290, "%d+%d" % (d["F_min"], d["depth_min"]))

# ── 7) 重い素材を出していないか ──
for page in ("m.html", "index.html"):
    t = read(page)
    check("%s がまだ非圧縮の曲(.wav)を読んでいる" % page, "music/" not in t or ".wav" not in t)
bj = json.load(io.open(os.path.join(WEB, "book.json"), encoding="utf-8"))
check("book.json にスマホ用の軽い絵(img_w)が無い", all("img_w" in p_ for p_ in bj.get("pages", [])))
check("book.json に表紙の小さい見本(thumb)が無い", bool(bj.get("thumb")))
gj = json.load(io.open(os.path.join(WEB, "gallery.json"), encoding="utf-8"))
check("gallery.json にスマホ用の軽い絵(file_w)が無い", all("file_w" in i_ for i_ in gj.get("items", [])))
mm = read("m.html")
check("m.html がスマホ用の軽い絵を使っていない", "img_w" in mm and "file_w" in mm)

print("OK %d 件 / NG %d 件" % (ok, len(ng)))
for x in ng:
    print("  NG " + x)
sys.exit(1 if ng else 0)
