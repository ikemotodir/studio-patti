# -*- coding: utf-8 -*-
"""make_room_edit.py の照明パイプラインを土台に make_room_design.py を組み立てる。
中身(部屋のデザイン)は design_content.py の CONTENT で全面入れ替え。"""
import ast, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_content import CONTENT

WEB = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(WEB, "make_room_edit.py"), encoding="utf-8").read()

M1 = "# ═══════════════ 主要座標(ここだけ見れば配置が分かる) ═══════════════"
M2 = "# ═══════════════ relight : プロップ単位の1px陰影 ═══════════════"
M3 = "# ═══════ global illumination ═══════"
M4 = "# ═══════ 書き出し ═══════"
head = src[:src.index(M1)]
pipe = src[src.index(M2):src.index(M3)]
gi   = src[src.index(M3):src.index(M4)]

def rep(txt, a, b, what):
    """置換が起きなかったら止める(黙って古い定義が残るのを防ぐ)。"""
    assert txt.count(a) == 1, "組み立て失敗: " + what
    return txt.replace(a, b)

# ─── head: 説明・出力先・パレット追加 ───
head = head.replace(
    '"""編集室(CONTENTS CREATIVE)の部屋 - 池本さんスケッチ準拠。',
    '"""デザイン室(CHARACTER DESIGN)の部屋 - 池本さんスケッチ準拠。')
head = head.replace(
    """レイアウト: 左壁=スタジオへ戻る戸口(白光)+スタジオ看板 / 奥壁=メニューパネル+大スクリーン+
カテゴリ表示+数字ボタンパネル / 手前=編集卓(ボタンいっぱい)+ゲーミングチェア。""",
    """レイアウト: 壁面いっぱいの黒板(木枠+チョーク受け)に紙を貼り、チョークの矢印でつなぐ。
右壁=スタジオへ戻る戸口(白光)+スタジオ看板 / 右=模造紙「キャラクターに関するデータ」/
天井=電球のガーランド(この部屋のあかり)。""")
head = head.replace('LAY = os.path.join(WEB, "room_edit_layers")',
                    'LAY = os.path.join(WEB, "room_design_layers")')
head = head.replace(
    " 'cyn0': (16, 84, 104), 'cyn1': (44, 164, 186), 'cyn2': (126, 224, 235), 'cync': (214, 250, 252),\n}",
    """ 'cyn0': (16, 84, 104), 'cyn1': (44, 164, 186), 'cyn2': (126, 224, 235), 'cync': (214, 250, 252),
 # ── デザイン室で足した色 ──
 'bd0': (12, 26, 24), 'bd1': (22, 40, 36), 'bd2': (34, 56, 50), 'bd3': (52, 78, 70),
 'pl0': (68, 62, 56), 'pl1': (104, 96, 86), 'pl2': (138, 128, 114),  # 漆喰(木造校舎の壁)
 'bd4': (78, 106, 96),                                                                 # 黒板
 'chk2': (146, 176, 164), 'chk': (226, 240, 230),                                       # チョーク
 'wd0': (70, 42, 26), 'wd1': (112, 70, 42), 'wd2': (156, 106, 64), 'wd3': (200, 150, 98),  # 木枠
 'pap_r0': (150, 32, 40), 'pap_r': (214, 58, 62),                                       # 赤い紙
 'bulbc': (255, 246, 200),                                                              # 電球のあかり
}""")

# ─── pipeline: 光の向きの基準をガーランドへ ───
pipe = pipe.replace(" ['cyn0','cyn1','cyn2','cync'],",
                    """ ['cyn0','cyn1','cyn2','cync'],
 ['bd0','bd1','bd2','bd3','bd4'],
 ['wd0','wd1','wd2','wd3'],
 ['pap_r0','pap_r'],
 ['chk2','chk'],
 ['o2','bulbc'],""")
pipe = pipe.replace("CRTC = (205, 66)     # 大スクリーンの画面中心",
                    "CRTC = (192, 12)     # 天井のガーランド(この部屋の主光源)")
pipe = pipe.replace("if (dx * dx + dy * dy) ** .5 < 92:",
                    "if (dx * dx + dy * dy) ** .5 < 30:")

# ─── GI: 光源とプロテクト ───
gi = gi.replace("""DARKER[P['cync']] = P['cyn2']""",
                """DARKER[P['cync']] = P['cyn2']
DARKER[P['chk']] = P['chk2']; DARKER[P['bulbc']] = P['o2']
DARKER[P['pap_r']] = P['pap_r0']""")
_i0 = gi.index("SOURCES = [")
_i1 = gi.index("AMB = ")
_i2 = gi.index(chr(10), _i1)
gi = gi[:_i0] + """SOURCES = [
    {'pos': (360, 118), 'r': 86,  's': 0.98, 'e': 1.3, 'tint': P['gray2'], 'occ': False},  # スタジオの白い灯り
    {'pos': (287, 92),  'r': 58,  's': 0.26, 'e': 1.4, 'tint': P['ivory'], 'occ': False},  # 模造紙の照り返し
    {'pos': (192, 120), 'r': 200, 's': 0.24, 'e': 1.3, 'tint': P['o1'],    'occ': False},  # 室内バウンス(暖色)
]
for _gx, _gy in GAR_BULBS:
    SOURCES.append({'pos': (_gx, _gy + 5), 'r': 46, 's': 0.30, 'e': 1.5,
                    'tint': P['o2'], 'occ': False})        # 電球ひとつずつが光源
AMB = 0.38""" + gi[_i2:]

gi = gi.replace("""            if layer == 'furniture':
                if c[:3] in (P['cyn0'], P['cyn1'], P['cyn2'], P['cync']):
                    continue    # シアンのアンビエントライトは自ら光る
                if sx <= xx < sx + sw and sy <= yy < sy + sh:
                    continue    # スクリーンは自ら光る(消灯でも保護)
                if 10 <= xx <= 39 and 49 <= yy <= 215:
                    continue    # スタジオの戸口の光
                if 3 <= xx <= 41 and 21 <= yy <= 47:
                    continue    # スタジオの看板
                if bx + 2 <= xx <= bx + bw - 3 and by + 2 <= yy <= by + bh - 3:
                    continue    # 数字ボタンは光る
                if cx <= xx <= cx + cw - 1 and cy <= yy <= cy + ch - 1:
                    continue    # 電飾マーキーは自ら光る""",
"""            if layer == 'bg':
                if c[:3] in (P['chk'], P['chk2']):
                    continue    # チョークの線は白のまま読ませる
            if layer == 'furniture':
                if DOORX0 <= xx <= DOORX1 and 49 <= yy <= 215:
                    continue    # スタジオの戸口の光
                if 342 <= xx <= 380 and 21 <= yy <= 47:
                    continue    # スタジオの看板
                if yy <= 26 and c[:3] in (P['o2'], P['bulbc'], P['y0']):
                    continue    # ガーランドの電球は自ら光る""")

# ─── 書き出し(出力名 + ガーランドのまたたき) ───
export = '''# ═══════ 書き出し ═══════
flat = Image.new("RGBA", (W, H), (0, 0, 0, 255))
for n in names:
    L[n].save(os.path.join(LAY, f"{n}.png"))
    flat.alpha_composite(L[n])
flat.convert("RGB").save(os.path.join(WEB, "room_design.png"))
print("layers + room_design.png written")

# ── プロップ切り分け(Aseprite用) ──
OBJ = os.path.join(LAY, "objects")
if os.path.isdir(OBJ):
    for _f in os.listdir(OBJ):
        os.remove(os.path.join(OBJ, _f))
os.makedirs(OBJ, exist_ok=True)
manifest = []
for n in names:
    ids = sorted([(v, k[1]) for k, v in OBJ_ID.items() if k[0] == n])
    layer_alpha = L[n].getchannel("A")
    taken = Image.new("L", (W, H), 0)
    kids = []
    buckets = {oid: bytearray(W * H) for oid, _ in ids}
    for idx, v in enumerate(OWNER[n].getdata()):
        b = buckets.get(v)
        if b is not None:
            b[idx] = 255
    for oid, oname in ids:
        mask = Image.frombytes("L", (W, H), bytes(buckets[oid]))
        cut = ImageChops.multiply(layer_alpha, mask)
        if not cut.getbbox():
            continue
        part = L[n].copy()
        part.putalpha(cut)
        safe = re.sub(r'[\\\\/:*?"<>|]', "_", oname)
        fn = f"{n}__{oid:03d}_{safe}.png"
        part.save(os.path.join(OBJ, fn))
        taken = ImageChops.lighter(taken, cut)
        kids.append({"name": oname, "file": "objects/" + fn})
    rest = ImageChops.subtract(layer_alpha, taken)
    if rest.getbbox():
        part = L[n].copy()
        part.putalpha(rest)
        fn = f"{n}__999_その他.png"
        part.save(os.path.join(OBJ, fn))
        kids.append({"name": "その他", "file": "objects/" + fn})
    manifest.append({"layer": n, "children": kids})
json.dump(manifest, io.open(os.path.join(LAY, "objects.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("プロップ切り分け:", sum(len(m["children"]) for m in manifest), "枚")

# ── ガーランドのまたたき(3コマ) ──
GY0, GBH = 8, 20
gar = Image.new("RGBA", (W * 3, GBH), (0, 0, 0, 0))
gard = ImageDraw.Draw(gar)
for f in range(3):
    for i, (gbx, gby) in enumerate(GAR_BULBS):
        if (i + f) % 3 == 0:
            gard.ellipse([f * W + gbx - 1, gby + 3 - GY0, f * W + gbx + 1, gby + 5 - GY0],
                         fill=C('bulbc'))
            gard.point((f * W + gbx, gby + 2 - GY0), fill=C('o2'))
gar.save(os.path.join(WEB, "design_garland.png"))
print("design_garland.png", gar.size, "band y", GY0, "h", GBH, "電球", len(GAR_BULBS), "個")
'''

out = head + CONTENT.strip("\n") + "\n\n" + pipe + gi + export
ast.parse(out)
io.open(os.path.join(WEB, "make_room_design.py"), "w", encoding="utf-8").write(out)
print("make_room_design.py 生成 / 構文OK  行数:", out.count("\n"))
