# -*- coding: utf-8 -*-
"""配置ツール(layout.html)が保存した layout.json を、部屋の絵とページに反映する。

 使い方:  python apply_layout.py [layout.json のパス]
 パスを省いたら、ダウンロードフォルダの一番新しい layout*.json を拾う。

 ここで扱うのは「位置と大きさ」だけ。数値から決まるもの(HTMLの当たり判定・
 文字の枠・ボタンの位置など)も、この中で一緒に書き換える。
 置換に1つでも失敗したら、何も保存せずに止める(黙って壊れるのを防ぐ)。
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

WEB = os.path.dirname(os.path.abspath(__file__))
SCRATCH = WEB          # 部屋の作り方一式はリポジトリの中に置いてある


def newest_layout():
    cands = []
    for d in (os.path.join(os.path.expanduser("~"), "Downloads"), WEB, os.getcwd()):
        cands += glob.glob(os.path.join(d, "layout*.json"))
    if not cands:
        sys.exit("layout.json が見つかりません。配置ツールで「配置ファイルを保存」を押してください。")
    return max(cands, key=os.path.getmtime)


class Patch(object):
    """まとめて書き換えて、全部そろってから保存する。"""

    def __init__(self):
        self.files = {}

    def load(self, path):
        if path not in self.files:
            self.files[path] = io.open(path, encoding="utf-8").read()
        return self.files[path]

    def sub(self, path, pat, new, why):
        s = self.load(path)
        n = len(re.findall(pat, s, re.M))
        if n != 1:
            sys.exit("止めました: %s の「%s」が %d 件でした" % (os.path.basename(path), why, n))
        self.files[path] = re.sub(pat, new, s, count=1, flags=re.M)

    def save(self):
        for path, s in self.files.items():
            io.open(path, "w", encoding="utf-8").write(s)
            print("  書き換え:", os.path.basename(path))


def apply_design(P, it):
    dc = os.path.join(SCRATCH, "design_content.py")
    dh = os.path.join(WEB, "design.html")
    HOT = {'PAP_DESIGN': 'ppdesign', 'PAP_SPOOKS': 'ppspooks', 'PAP_WORLD': 'ppworld',
           'PAP_TALE': 'pptale', 'PAP_SKETCH': 'ppsketch', 'PAP_STORY': 'ppstory',
           'DATA_TITLE': 'ppdatatitle', 'DATA_PANEL': 'ppdata'}
    for k, o in it.items():
        if k not in HOT:
            continue
        P.sub(dc, r"^%s\s*=\s*\([^)]*\)" % k,
              "%s = (%d, %d, %d, %d)" % (k, o['x'], o['y'], o['w'], o['h']), k)
        if k == 'PAP_STORY':               # これだけ CSS 側で位置を持っている
            P.sub(dh,
                  r"#ppstory \{(\s+)position: absolute; left: \d+px; top: \d+px;"
                  r" width: \d+px; height: \d+px;",
                  "#ppstory {\\1position: absolute; left: %dpx; top: %dpx;"
                  " width: %dpx; height: %dpx;" % (o['x'], o['y'], o['w'], o['h']),
                  "ppstory")
            continue
        P.sub(dh, r'id="%s" style="left:\d+px;top:\d+px;width:\d+px;height:\d+px' % HOT[k],
              'id="%s" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx'
              % (HOT[k], o['x'], o['y'], o['w'], o['h']), HOT[k])
    apply_chara(P, dh, it)


def apply_edit(P, it):
    me = os.path.join(WEB, "make_room_edit.py")
    ch = os.path.join(WEB, "contents.html")
    for k in ('MENU', 'SCR', 'MARQ', 'BTNP'):
        if k not in it:
            continue
        o = it[k]
        P.sub(me, r"^%s\s*=\s*\([^)]*\)" % k,
              "%-4s = (%d, %d, %d, %d)" % (k, o['x'], o['y'], o['w'], o['h']), k)
    if 'MENU' in it:                       # メニュー枠から決まるもの
        m = it['MENU']
        P.sub(ch, r"\.mi \{(\s+)position: absolute; left: \d+px; width: \d+px;",
              ".mi {\\1position: absolute; left: %dpx; width: %dpx;" % (m['x'] + 3, m['w'] - 6),
              ".mi の枠")
        P.sub(ch, r"#mihdr \{(\s+)position: absolute; left: \d+px; width: \d+px;",
              "#mihdr {\\1position: absolute; left: %dpx; width: %dpx;" % (m['x'] + 3, m['w'] - 6),
              "#mihdr の枠")
        P.sub(ch, r"const MENU_TOP = [\d.]+", "const MENU_TOP = %.2f" % (m['y'] + 5.42), "MENU_TOP")
    if 'SCR' in it:                        # モニターから決まるもの
        s = it['SCR']
        P.sub(ch, r"position: absolute; left: \d+px; top: \d+px;(\s+)width: \d+px; height: \d+px; overflow: hidden;",
              "position: absolute; left: %dpx; top: %dpx;\\1width: %dpx; height: %dpx; overflow: hidden;"
              % (s['x'], s['y'], s['w'], s['h']), "#screenbox")
        P.sub(ch, r"position: absolute; left: \d+px; top: 10px; width: \d+px; height: \d+px;",
              "position: absolute; left: %dpx; top: 10px; width: %dpx; height: %dpx;"
              % (s['x'] - 1, s['w'] + 18, s['h'] + 20), "#screenglow")
        P.sub(ch, r'<canvas id="wstars" width="\d+" height="\d+"',
              '<canvas id="wstars" width="%d" height="%d"' % (s['w'], s['h']), "待機画面のcanvas")
        P.sub(ch, r"const SW = \d+, SH = \d+;", "const SW = %d, SH = %d;" % (s['w'], s['h']), "SW/SH")
    if 'MARQ' in it:                       # 電飾の表示板から決まるもの
        q = it['MARQ']
        P.sub(ch, r"position: absolute; left: \d+px; top: [\d.]+px; width: \d+px; height: \d+px;(\s+)display: flex; align-items: center; justify-content: center;\s+font-family: 'DotGothic16', 'MS Gothic', monospace;\s+color: #fff6e0",
              "position: absolute; left: %dpx; top: %.2fpx; width: %dpx; height: %dpx;\\1display: flex; align-items: center; justify-content: center;\\1font-family: 'DotGothic16', 'MS Gothic', monospace;\\1color: #fff6e0"
              % (q['x'] + 4, q['y'] + 6.15, q['w'] - 8, q['h'] - 12), "#catname")
        P.sub(ch, r"position: absolute; left: 0; top: \d+px;(\s+)width: 384px; height: \d+px; pointer-events: none;\s+background-image: url\(marquee_blink.png\);\s+background-size: 1536px \d+px;",
              "position: absolute; left: 0; top: %dpx;\\1width: 384px; height: %dpx; pointer-events: none;\\1background-image: url(marquee_blink.png);\\1background-size: 1536px %dpx;"
              % (q['y'], q['h'], q['h']), "#marqblink")
    if 'BTNP' in it:                       # 数字ボタンの枠から決まるもの
        b = it['BTNP']
        cx = int(b['x'] + (b['w'] - 1) / 2.0)
        L, R = cx - 12, cx + 12
        r1, r2 = b['y'] + 27, b['y'] + 54
        P.sub(os.path.join(WEB, "make_room_edit.py"), r"^BTNC = \[[^\]]*\]",
              "BTNC = [(%d, %d), (%d, %d), (%d, %d), (%d, %d)]" % (L, r1, R, r1, L, r2, R, r2), "BTNC")
        P.sub(ch, r"const BTN_POS = \[\[[^\]]*\], \[[^\]]*\], \[[^\]]*\], \[[^\]]*\]\]",
              "const BTN_POS = [[%d, %d], [%d, %d], [%d, %d], [%d, %d]]"
              % (L - 10, r1 - 10, R - 10, r1 - 10, L - 10, r2 - 10, R - 10, r2 - 10), "BTN_POS")
    apply_chara(P, ch, it)


def apply_chara(P, page, it):
    for key, sel, sh, w, h in (('mayu', '#mayu', '#mshadow', 30, 72),
                               ('patti', '#pattifloat', '#pshadow', 32, 48)):
        if key not in it:
            continue
        o = it[key]
        sc = float(o.get('s', 0.9))
        P.sub(page, r"%s \{(\s+)position: absolute; left: \d+px; top: \d+px;" % re.escape(sel),
              "%s {\\1position: absolute; left: %dpx; top: %dpx;" % (sel, o['x'], o['y']), sel)
        P.sub(page, r"%s \{(\s+)position: absolute; left: \d+px; top: \d+px;\s+width: \d+px; height: 5px;" % re.escape(sh),
              "%s {\\1position: absolute; left: %dpx; top: %dpx;\\1width: %dpx; height: 5px;"
              % (sh, int(round(o['x'] + w * (1 - sc) / 2.0 + 2)), o['y'] + h - 2,
                 int(round(w * sc - 4))), sh)
        tag = 'mayuchar' if key == 'mayu' else 'pattichar'
        P.sub(page, r"transform: scale\([\d.]+\)( scaleX\(-1\))?; transform-origin: 50%% 100%%;(\s+)animation: %s" % tag,
              "transform: scale(%.2f)\\1; transform-origin: 50%% 100%%;\\2animation: %s" % (sc, tag),
              sel + " の大きさ")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else newest_layout()
    print("読み込み:", path)
    data = json.load(io.open(path, encoding="utf-8"))
    os.environ["PATTI_LAYOUT"] = os.path.abspath(path)   # make_room_m.py が同じ layout.json を読む
    P = Patch()
    for room, items in data.items():
        if not isinstance(items, list):
            print("[%s] 配列ではないので飛ばします" % room)
            continue
        it = dict((o['id'], o) for o in items if isinstance(o, dict) and 'id' in o)
        print("[%s] %d 件" % (room, len(it)))
        if room == 'design':
            apply_design(P, it)
        elif room == 'edit':
            apply_edit(P, it)
        elif room == 'mobile':
            print("  (スマホ版は make_room_m.py が layout.json を直接読む)")
    P.save()

    print("絵を描き直しています…")
    # aseprite の書き出しは Aseprite 本体が要るので、無ければ飛ばす
    # (GitHub 上では本体が無い。池本さんが編集する .aseprite は手元で作り直す)
    for script, need_aseprite in (("build_design.py", False),
                                  ("make_room_edit.py", False),
                                  ("make_room_design.py", False),
                                  ("make_room_m.py", False),
                                  ("make_aseprite_edit.py", True),
                                  ("make_aseprite_design.py", True)):
        r = subprocess.run([sys.executable, script], cwd=WEB, capture_output=True)
        out = r.stdout.decode("utf-8", "replace")
        if r.returncode != 0:
            msg = (out + r.stderr.decode("utf-8", "replace"))[-800:]
            if need_aseprite:
                print("  とばした", script, "(Aseprite が無い環境)")
                continue
            sys.exit("失敗: %s\n%s" % (script, msg))
        print("  OK", script)
        if "注意" in out:                      # 池本さんの配置での重なり・はみ出しは記録に残す
            note = out[out.index("注意"):].rstrip()
            for line in note.splitlines():
                print("    " + line)
            if os.environ.get("GITHUB_ACTIONS"):
                print("::warning title=%s::%s" % (script, note.replace("\n", "%0A")))
    print("反映おわり。")


if __name__ == "__main__":
    main()
