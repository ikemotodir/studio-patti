# -*- coding: utf-8 -*-
"""room.aseprite で手直しした内容を、サイトへ反映する。

・room.aseprite の各レイヤー(グループは中身を合成)を書き出す
・生成された room_layers\\*.png と見比べて、変わっているものだけ
  overrides\\<レイヤー名>.full.png として保存する
・make_room.py はこの .full.png があれば、そのレイヤーを丸ごと差し替える
  → 次に build.bat を流しても、手直しが消えない

つまり池本さんの作業は「room.aseprite を編集して保存 → これを実行」だけ。
"""
from PIL import Image, ImageChops
import io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(HERE, "room_layers")
OVR = os.path.join(HERE, "overrides")
ASE_FILE = os.path.join(HERE, "room.aseprite")
ASE = r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe"
TMP = os.path.join(HERE, "_sync_tmp")

if not os.path.exists(ASE_FILE):
    sys.exit("room.aseprite がありません。先に make_aseprite.py を実行してください。")
os.makedirs(OVR, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ── Aseprite に「トップレベルのレイヤー/グループ」ごとの合成画像を出させる ──
lua = f'''
local spr = app.open([[{ASE_FILE}]])
local out = [[{TMP}]]
local top = {{}}
for i, l in ipairs(spr.layers) do top[#top + 1] = l end
for _, target in ipairs(top) do
  for _, l in ipairs(top) do l.isVisible = (l == target) end
  local img = Image(spr.width, spr.height, ColorMode.RGB)
  img:drawSprite(spr, 1)
  img:saveAs(out .. [[\\]] .. target.name .. [[.png]])
end
for _, l in ipairs(top) do l.isVisible = true end
print("exported " .. #top .. " top-level layers")
'''
script = os.path.join(HERE, "_sync.lua")
io.open(script, "w", encoding="utf-8").write(lua)
r = subprocess.run([ASE, "-b", "--script", script], capture_output=True, text=True)
print((r.stdout or "").strip() or (r.stderr or "").strip())
os.remove(script)

# ── 生成物と見比べて、変わったレイヤーだけ override にする ──────────
changed, same = [], []
for fn in sorted(os.listdir(TMP)):
    if not fn.endswith(".png"):
        continue
    name = fn[:-4]
    edited = Image.open(os.path.join(TMP, fn)).convert("RGBA")
    src = os.path.join(LAY, name + ".png")
    if os.path.exists(src):
        base = Image.open(src).convert("RGBA")
        if ImageChops.difference(edited, base).getbbox() is None:
            same.append(name)
            continue
    edited.save(os.path.join(OVR, name + ".full.png"))
    changed.append(name)

for fn in os.listdir(TMP):
    os.remove(os.path.join(TMP, fn))
os.rmdir(TMP)

if changed:
    print("手直しを取り込んだレイヤー:", "、".join(changed))
else:
    print("変更はありませんでした（room.aseprite は生成物と同じ内容です）")
if same:
    print("変更なし:", "、".join(same))

# ── 部屋を作り直して、サイトに反映する ──────────────────────────
print()
subprocess.run([sys.executable, os.path.join(HERE, "make_room.py")], check=True)
print()
print("反映しました。start.bat で確認してください。")
