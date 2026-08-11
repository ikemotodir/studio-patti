# -*- coding: utf-8 -*-
"""サイト用画像\\ の重い素材を、Web公開に耐える軽さへ落として web\\ へ置く。
・animation_1.mp4 → tv_video.mp4（部屋のブラウン管は44x34でしか映さないので小さくてよい）
・sekkeizu.jpg    → 長辺1400pxへ縮小
原本（サイト用画像\\）には一切触らない。ffmpegが無い場合は動画だけ飛ばす。
"""
from PIL import Image
import os, shutil, subprocess, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "..", "サイト用画像")
SRC = os.path.abspath(SRC)


def find_ffmpeg():
    p = shutil.which("ffmpeg")
    if p:
        return p
    pat = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                       "Packages", "Gyan.FFmpeg*", "ffmpeg*", "bin", "ffmpeg.exe")
    hits = glob.glob(pat)
    return hits[0] if hits else None


def kb(path):
    return os.path.getsize(path) // 1024


# ── ブラウン管の映像 ────────────────────────────────
mp4_src = os.path.join(SRC, "animation_1.mp4")
mp4_dst = os.path.join(HERE, "tv_video.mp4")
ff = find_ffmpeg()
if not os.path.exists(mp4_src):
    print("[ ] animation_1.mp4 が見つからないので動画はそのまま")
elif not ff:
    print("[ ] ffmpeg が見つからないので動画はそのまま（今の tv_video.mp4 を使います）")
else:
    subprocess.run([ff, "-y", "-i", mp4_src, "-an",          # 音は使わないので捨てる
                    "-vf", "scale=320:-2", "-r", "24",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "30",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4_dst],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"tv_video.mp4  320x180 無音  {kb(mp4_dst)}KB")

# ── 設計図の写真 ───────────────────────────────────
jpg_src = os.path.join(SRC, "sekkeizu.jpg")
jpg_dst = os.path.join(HERE, "sekkeizu.jpg")
if os.path.exists(jpg_src):
    im = Image.open(jpg_src)
    im.thumbnail((1400, 1400), Image.LANCZOS)
    im.convert("RGB").save(jpg_dst, quality=86, optimize=True)
    print(f"sekkeizu.jpg  {im.size[0]}x{im.size[1]}  {kb(jpg_dst)}KB")
else:
    print("[ ] sekkeizu.jpg の原本が見つからないのでそのまま")
