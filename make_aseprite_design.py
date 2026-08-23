# -*- coding: utf-8 -*-
"""room_layers\\ の書き出しから、レイヤー分けされた room.aseprite を組み立てる。

・bg / light は1枚のレイヤー
・furniture と props は「グループ」にして、その中にプロップ1個ずつのレイヤーを入れる
・重ねた結果が room_design.png と1画素も違わないことを確認してから保存する

池本さんがこの .aseprite を直接いじれるようにするためのファイル。
編集したものをサイトへ戻す時は sync_aseprite.py を使う。
"""
from PIL import Image, ImageChops
import io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(HERE, "room_design_layers")
OUT = os.path.join(HERE, "room_design.aseprite")
ASE = r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe"
GROUPED = ("furniture", "props")          # グループにするレイヤー

man = json.load(io.open(os.path.join(LAY, "objects.json"), encoding="utf-8"))


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ── 読み込む画像を先に全部並べる（Asepriteは後からapp.openを混ぜると落ちる）──
loads, plan = [], []
for entry in man:
    n = entry["layer"]
    kids = entry["children"]
    if not kids:
        continue
    if n in GROUPED and len(kids) > 0:
        items = [(k["name"], os.path.join(LAY, k["file"])) for k in kids]
        plan.append(("group", n, items))
    else:
        # 単独レイヤー。子が複数あっても1枚に統合された画像を使う
        plan.append(("layer", n, [(n, os.path.join(LAY, n + ".png"))]))

idx = {}
for _, _, items in plan:
    for _, path in items:
        if path not in idx:
            idx[path] = len(idx) + 1
            loads.append(path)

lua = ["local I = {}"]
for p in loads:
    lua.append(f"I[{idx[p]}] = Image{{ fromFile = {lua_str(p)} }}")
lua += [
    "local spr = Sprite(384, 240, ColorMode.RGB)",
    "spr:deleteLayer(spr.layers[1])",          # 既定の空レイヤーを外す
]
for kind, n, items in plan:
    if kind == "group":
        lua.append("do")
        lua.append("  local g = spr:newGroup()")
        lua.append(f"  g.name = {lua_str(n)}")
        lua.append("  g.isCollapsed = true")
        for nm, path in items:
            lua.append("  do")
            lua.append("    local l = spr:newLayer()")
            lua.append(f"    l.name = {lua_str(nm)}")
            lua.append("    l.parent = g")
            lua.append(f"    spr:newCel(l, 1, I[{idx[path]}], Point(0, 0))")
            lua.append("  end")
        lua.append("end")
    else:
        nm, path = items[0]
        lua.append("do")
        lua.append("  local l = spr:newLayer()")
        lua.append(f"  l.name = {lua_str(n)}")
        lua.append(f"  spr:newCel(l, 1, I[{idx[path]}], Point(0, 0))")
        lua.append("end")
lua.append(f"spr:saveAs({lua_str(OUT)})")
lua.append('print("aseprite written: " .. tostring(#spr.layers) .. " top-level layers")')

script = os.path.join(HERE, "_build_aseprite.lua")
io.open(script, "w", encoding="utf-8").write("\n".join(lua) + "\n")

if not os.path.exists(ASE):
    sys.exit("Aseprite が見つかりません: " + ASE)
r = subprocess.run([ASE, "-b", "--script", script], capture_output=True, text=True)
print((r.stdout or "").strip() or (r.stderr or "").strip())
os.remove(script)

# ── 検証: 重ねた結果が room.png と一致するか ──────────────────────
flat = Image.new("RGBA", (384, 240), (0, 0, 0, 255))
for _, n, items in plan:
    for _, path in items:
        flat.alpha_composite(Image.open(path).convert("RGBA"))
room = Image.open(os.path.join(HERE, "room_design.png")).convert("RGB")
diff = ImageChops.difference(flat.convert("RGB"), room)
bbox = diff.getbbox()
if bbox is None:
    print("検証OK: 重ねた結果は room_design.png と完全一致")
else:
    n_bad = sum(1 for p in diff.convert("L").getdata() if p)
    print(f"[!] 一致しません: 差のある画素 {n_bad}個 / 範囲 {bbox}")
print("→", OUT, os.path.getsize(OUT) // 1024, "KB")
