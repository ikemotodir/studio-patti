# -*- coding: utf-8 -*-
"""文字が「枠のセンターに来ているか」を、実際に描かれた画素で検査する。

CSSの数字を目で追うのではなく、スクリーンショットから
 ・枠(刷り面)の矩形
 ・その中で光っている文字の画素の外形
を取り、中心のズレを px で出す。0.5px を超えたら失敗として印を付ける。

使い方:  python check_center.py [URL]
"""
import io, json, os, subprocess, sys

SP = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/contents.html?v=cc"
SHOT = os.path.join(SP, "center_check.png")

# 枠(刷り面)の位置。make_room_edit.py の MENU / MARQ から決まる
MENU = (40, 24, 58, 114)
MARQ = (288, 18, 53, 24)
BEDS = [("見出し 制作事例", MENU[0] + 5, MENU[1] + 6 + 0 * 22 + 5, MENU[2] - 11, 10)]
for i, nm in enumerate(("アニメーション", "絵本", "メタバース", "実写映像"), start=1):
    BEDS.append(("メニュー " + nm, MENU[0] + 5, MENU[1] + 6 + i * 22 + 5, MENU[2] - 11, 10))
# 枠の縁(明るい見切り)を入れると文字と区別できないので、塗った刷り面だけを見る
BEDS.append(("電飾マーキー", MARQ[0] + 5, MARQ[1] + 7, MARQ[2] - 10, MARQ[3] - 14))

env = dict(os.environ, SHOT_URL=URL, SHOT_WAIT="3200")
js = ('(() => { const r = document.getElementById("stage").getBoundingClientRect();'
      ' return JSON.stringify({x:r.left, y:r.top, w:r.width, h:r.height}); })()')
out = subprocess.run([sys.executable, os.path.join(SP, "shot2.py"), SHOT, js],
                     capture_output=True, text=True, env=env, cwd=SP)
line = [l for l in out.stdout.splitlines() if l.startswith("JS:")]
if not line:
    print(out.stdout, out.stderr)
    sys.exit("スクリーンショットに失敗")
rect = json.loads(json.loads(line[0][3:].strip()))
sc = rect["w"] / 384.0

from PIL import Image
im = Image.open(SHOT).convert("RGB")
px = im.load()
IW, IH = im.size

def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

ng = 0
for name, bx, by, bw, bh in BEDS:
    # 両端は ▶カーソル(メニュー)と シアンLED(見出し)があるので外して見る
    x0 = int(rect["x"] + (bx + 5) * sc)
    x1 = int(rect["x"] + (bx + bw - 3) * sc)
    y0 = int(rect["y"] + (by - 3) * sc)          # 字面が枠から出ていても拾う
    y1 = int(rect["y"] + (by + bh + 3) * sc)
    x0, x1 = max(0, x0), min(IW, x1)
    y0, y1 = max(0, y0), min(IH, y1)
    thr = 95                                     # 下地より明らかに明るい画素=文字
    rows = [y for y in range(y0, y1) if any(lum(px[x, y]) > thr for x in range(x0, x1))]
    cols = [x for x in range(x0, x1) if any(lum(px[x, y]) > thr for y in range(y0, y1))]
    if not rows or not cols:
        print("  %-22s 文字が見つからない(選択されていない項目かも)" % name)
        continue
    # 刷り面そのものの中心と比べる(走査範囲の中心ではない)
    dy = (rows[0] + rows[-1]) / 2.0 / sc - rect["y"] / sc - (by + (bh - 1) / 2.0)
    dx = (cols[0] + cols[-1]) / 2.0 / sc - rect["x"] / sc - (bx + (bw - 1) / 2.0)
    mark = "OK " if abs(dy) <= 0.5 else "NG "
    if abs(dy) > 0.5:
        ng += 1
    print("  %s%-22s 縦ズレ %+5.2fpx / 横ズレ %+5.2fpx" % (mark, name, dy, dx))

print("NG %d 件" % ng)
sys.exit(1 if ng else 0)
