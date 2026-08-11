# -*- coding: utf-8 -*-
"""ファミコン風8bit BGMを生成する(権利クリア)。
・著作権消滅のクラシック(パブリックドメイン)を8bit編曲
・オリジナル曲(スタジオパッチのためにこちらで作曲)
出力: web/music/*.wav（ブラウザで直接再生できる）
"""
import math, os, struct, wave

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
os.makedirs(OUT, exist_ok=True)
SR = 22050

NOTES = {}
for octv in range(1, 8):
    for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']):
        NOTES[f"{n}{octv}"] = 440.0 * (2 ** ((octv - 4) + (i - 9) / 12.0))
NOTES['R'] = 0.0


def pulse(f, t, duty=0.5):
    if f <= 0:
        return 0.0
    return 1.0 if (t * f) % 1.0 < duty else -1.0


def tri(f, t):
    if f <= 0:
        return 0.0
    x = (t * f) % 1.0
    return (4 * x - 1) if x < 0.5 else (3 - 4 * x)


def render(track, bpm, duty=0.5, vol=0.22, wave_fn=pulse, vib=0.0):
    """track: [(note, beats), ...] → floatサンプル列"""
    spb = 60.0 / bpm
    buf = []
    for note, beats in track:
        f = NOTES.get(note, 0.0)
        n = int(SR * spb * beats)
        for i in range(n):
            t = i / SR
            env = 1.0
            if f > 0:
                a = min(1.0, i / (SR * 0.006))                    # アタック
                d = max(0.0, 1.0 - (i / max(1, n)) ** 2 * 0.55)   # 減衰
                env = a * d
                if i > n - SR * 0.012:                             # 音の切れ目
                    env *= max(0.0, (n - i) / (SR * 0.012))
            ff = f * (1 + vib * math.sin(2 * math.pi * 5.5 * t)) if vib else f
            v = wave_fn(ff, t, duty) if wave_fn is pulse else wave_fn(ff, t)
            buf.append(v * env * vol)
    return buf


def noise_drums(pattern, bpm, beats_total, vol=0.10):
    spb = 60.0 / bpm
    total = int(SR * spb * beats_total)
    buf = [0.0] * total
    seed = 12345
    for hit_beat, kind in pattern:
        start = int(SR * spb * hit_beat)
        length = int(SR * (0.05 if kind == 'h' else 0.11))
        for i in range(length):
            if start + i >= total:
                break
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            r = (seed / 0x7FFFFFFF) * 2 - 1
            env = (1 - i / length) ** (3 if kind == 'h' else 2)
            f = 1.0 if kind == 'h' else 0.55
            buf[start + i] += r * env * vol * f
    return buf


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return out


def save(name, samples):
    path = os.path.join(OUT, name)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        frames = b''.join(struct.pack('<h', int(max(-1, min(1, s)) * 32000)) for s in samples)
        w.writeframes(frames)
    print(name, round(len(samples) / SR, 1), "sec")


# ── 1. パッチのおへや(オリジナル・ゆったり) ──
mel1 = [('C5',1),('E5',1),('G5',1),('E5',1), ('F5',1),('A5',1),('C6',2),
        ('B5',1),('G5',1),('A5',1),('F5',1), ('G5',2),('E5',2),
        ('C5',1),('E5',1),('G5',1),('C6',1), ('B5',1),('A5',1),('G5',2),
        ('F5',1),('E5',1),('D5',1),('E5',1), ('C5',4)]
bass1 = [('C3',2),('G3',2), ('F3',2),('C4',2), ('G3',2),('E3',2), ('C3',2),('G3',2),
         ('C3',2),('E3',2), ('A3',2),('G3',2), ('F3',2),('G3',2), ('C3',4)]
d1 = [(b, 'h') for b in range(0, 32, 1)] + [(b, 'k') for b in range(0, 32, 2)]
save("01_pattis_room.wav",
     mix(render(mel1, 108, duty=0.5, vol=0.20),
         render(bass1, 108, vol=0.16, wave_fn=tri),
         noise_drums(d1, 108, 32)))

# ── 2. よるのさんぽ(オリジナル・軽快) ──
mel2 = [('G4',.5),('A4',.5),('B4',1),('D5',1),('B4',1),
        ('C5',.5),('D5',.5),('E5',1),('G5',1),('E5',1),
        ('D5',.5),('C5',.5),('B4',1),('A4',1),('G4',1),
        ('A4',.5),('B4',.5),('C5',1),('D5',2),
        ('E5',.5),('D5',.5),('C5',1),('B4',1),('G4',1),
        ('A4',1),('B4',1),('D5',2)]
bass2 = [('G2',1),('D3',1)] * 8
d2 = [(b * .5, 'h') for b in range(0, 32)] + [(b, 'k') for b in range(0, 16, 1)]
save("02_night_walk.wav",
     mix(render(mel2, 132, duty=0.25, vol=0.19),
         render(bass2, 132, vol=0.15, wave_fn=tri),
         noise_drums(d2, 132, 16)))

# ── 3. きらきら星(トゥインクル/モーツァルト変奏・パブリックドメイン) ──
mel3 = [('C5',1),('C5',1),('G5',1),('G5',1),('A5',1),('A5',1),('G5',2),
        ('F5',1),('F5',1),('E5',1),('E5',1),('D5',1),('D5',1),('C5',2),
        ('G5',1),('G5',1),('F5',1),('F5',1),('E5',1),('E5',1),('D5',2),
        ('G5',1),('G5',1),('F5',1),('F5',1),('E5',1),('E5',1),('D5',2),
        ('C5',1),('C5',1),('G5',1),('G5',1),('A5',1),('A5',1),('G5',2),
        ('F5',1),('F5',1),('E5',1),('E5',1),('D5',1),('D5',1),('C5',2)]
bass3 = [('C3',2),('C3',2),('F3',2),('C3',2), ('F3',2),('C3',2),('G3',2),('C3',2),
         ('C3',2),('G3',2),('C3',2),('G3',2), ('C3',2),('G3',2),('C3',2),('G3',2),
         ('C3',2),('C3',2),('F3',2),('C3',2), ('F3',2),('C3',2),('G3',2),('C3',2)]
save("03_twinkle_star.wav",
     mix(render(mel3, 120, duty=0.5, vol=0.20),
         render(bass3, 120, vol=0.15, wave_fn=tri),
         noise_drums([(b, 'k') for b in range(0, 48, 2)], 120, 48)))

# ── 4. エリーゼのために(ベートーヴェン・パブリックドメイン) ──
mel4 = [('E5',.5),('D#5',.5),('E5',.5),('D#5',.5),('E5',.5),('B4',.5),('D5',.5),('C5',.5),
        ('A4',1),('R',.5),('C4',.5),('E4',.5),('A4',.5),
        ('B4',1),('R',.5),('E4',.5),('G#4',.5),('B4',.5),
        ('C5',1),('R',.5),('E4',.5),
        ('E5',.5),('D#5',.5),('E5',.5),('D#5',.5),('E5',.5),('B4',.5),('D5',.5),('C5',.5),
        ('A4',1),('R',.5),('C4',.5),('E4',.5),('A4',.5),
        ('B4',1),('R',.5),('E4',.5),('C5',.5),('B4',.5),('A4',2)]
bass4 = [('A2',2),('E3',2),('A2',2),('E3',2),('A2',2),('E3',2),
         ('A2',2),('E3',2),('A2',2),('E3',2),('A2',2),('E3',2)]
save("04_fur_elise.wav",
     mix(render(mel4, 112, duty=0.5, vol=0.20),
         render(bass4, 112, vol=0.14, wave_fn=tri)))

# ── 5. おばけのマーチ(オリジナル・ちょっと不気味で楽しい) ──
mel5 = [('A4',.5),('C5',.5),('E5',.5),('A5',.5),('G#5',1),('E5',1),
        ('F5',.5),('A5',.5),('C6',1),('B5',1),('A5',1),
        ('E5',.5),('F5',.5),('G5',.5),('A5',.5),('B5',1),('C6',1),
        ('B5',.5),('A5',.5),('G#5',.5),('A5',.5),('E5',2),
        ('D5',.5),('E5',.5),('F5',1),('E5',1),('D5',1),
        ('C5',.5),('D5',.5),('E5',1),('A4',2)]
bass5 = [('A2',1),('E3',1)] * 10
d5 = [(b * .5, 'h') for b in range(0, 40)] + [(b, 'k') for b in range(0, 20)]
save("05_spook_march.wav",
     mix(render(mel5, 126, duty=0.125, vol=0.19, vib=0.004),
         render(bass5, 126, vol=0.16, wave_fn=tri),
         noise_drums(d5, 126, 20)))

print("all tracks written to", OUT)
