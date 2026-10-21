// AI事業の入口: 映写機の上で回る「AI」のホログラム(PC版TOP・スマホ版TOPで共用)
// 部屋の絵と同じ1ドット単位の canvas に、立体の文字を回して描く。光り方は CSS で付ける。
//   mountAIHolo(stage, lensX, lensY) … lensX/lensY = 映写機のレンズ(上向き)の位置(部屋のドット座標)
(function () {
  const CW = 44, CH = 46;                // canvas の大きさ(ドット)
  const LX = 22, LY = CH - 1;            // canvas の中のレンズの位置
  const U = 3, DEPTH = 3;                // 文字の1マス=3ドット / 奥行きは前後に3ドットずつ
  // 7段の文字(A と I)。1=ブロック
  const GLYPH = [
    '.###..###',
    '#...#..#.',
    '#...#..#.',
    '#####..#.',
    '#...#..#.',
    '#...#..#.',
    '#...#.###',
  ];
  const ROWS = GLYPH.length, COLS = GLYPH[0].length;
  const on = (c, r) => r >= 0 && r < ROWS && c >= 0 && c < COLS && GLYPH[r][c] === '#';
  // 会社概要と同じ 青(#004AAD)→紫(#CB6CE6)の仲間。光る物なので明るくして、時間で流れるように色を変える
  const PAL = [[110, 232, 255], [80, 140, 255], [176, 112, 255], [236, 120, 236]];   // 水色→青→紫→桃→(水色へ戻る)
  const palette = (u) => {
    u = ((u % 1) + 1) % 1 * PAL.length;
    const i = Math.floor(u), f = u - i, a = PAL[i], b = PAL[(i + 1) % PAL.length];
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
  };

  // 文字の面を点の集まりにしておく(毎フレーム回して描くだけにする)
  const PTS = [];
  const face = (x0, y0, z0, ax, ay, nx, ny, nz) => {      // ax/ay: 面を張る2方向
    for (let a = 0; a <= U; a += 0.5) {
      for (let b = 0; b <= (ay === 'z' ? DEPTH * 2 : U); b += 0.5) {
        const p = { x: x0, y: y0, z: z0, nx, ny, nz };
        if (ax === 'x') p.x += a; else if (ax === 'y') p.y += a; else p.z += a;
        if (ay === 'x') p.x += b; else if (ay === 'y') p.y += b; else p.z += b;
        PTS.push(p);
      }
    }
  };
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (!on(c, r)) continue;
      const x0 = (c - COLS / 2) * U, y0 = (r - ROWS / 2) * U;
      face(x0, y0, DEPTH, 'x', 'y', 0, 0, 1);              // 前
      face(x0, y0, -DEPTH, 'x', 'y', 0, 0, -1);            // 後ろ
      if (!on(c - 1, r)) face(x0, y0, -DEPTH, 'y', 'z', -1, 0, 0);
      if (!on(c + 1, r)) face(x0 + U, y0, -DEPTH, 'y', 'z', 1, 0, 0);
      if (!on(c, r - 1)) face(x0, y0, -DEPTH, 'x', 'z', 0, -1, 0);
      if (!on(c, r + 1)) face(x0, y0 + U, -DEPTH, 'x', 'z', 0, 1, 0);
    }
  }

  function draw(g, t) {
    const img = g.createImageData(CW, CH), px = img.data;
    const put = (x, y, r, gg, b, a) => {
      if (x < 0 || y < 0 || x >= CW || y >= CH) return;
      const i = (y * CW + x) * 4;
      if (px[i + 3] >= a) return;
      px[i] = r; px[i + 1] = gg; px[i + 2] = b; px[i + 3] = a;
    };
    // 映写機の光(レンズから上へ広がる)
    const top = 8;                                        // 光の上端(窓にかからない高さ)
    for (let y = top; y < LY; y++) {
      const k = (LY - y) / (LY - top);                     // 0=レンズ 1=上
      const half = Math.round(2 + k * 13);
      for (let x = LX - half; x <= LX + half; x++) {
        const edge = Math.abs(x - LX) >= half - 1;
        const a = edge ? 95 * (1 - k * 0.6) : (16 + 30 * (1 - k)) * (((x + y) & 1) ? 1 : 0.5);   // 文字が目立つよう光は控えめ
        const col = edge ? [150, 190, 255] : [90, 140, 255];
        put(x, y, col[0], col[1], col[2], Math.round(a));
      }
    }
    // 光の中をのぼる粒
    for (let i = 0; i < 6; i++) {
      const ph = ((t * 0.35 + i / 6) % 1);
      const y = Math.round(LY - 2 - ph * (LY - top - 4));
      const x = Math.round(LX + Math.sin(i * 2.1 + t) * (2 + ph * 9));
      put(x, y, 230, 220, 255, Math.round(220 * (1 - ph)));
    }
    // 回る「AI」
    // 1周 約5秒。正面(「AI」と読める向き)ではゆっくり、裏側はすばやく回す
    const ph = (t / 5) % 1;
    const ang = 2 * Math.PI * ph - 0.62 * Math.sin(2 * Math.PI * ph);
    const ca = Math.cos(ang), sa = Math.sin(ang), F = 70;
    const cy = 21 + Math.round(Math.sin(t * 2.2));         // ふわっと上下(窓にかからない高さ)
    const zb = new Float32Array(CW * CH).fill(1e9), cb = new Uint8ClampedArray(CW * CH * 4);
    for (const p of PTS) {
      const xr = p.x * ca + p.z * sa, zr = -p.x * sa + p.z * ca;
      const nzr = -p.nx * sa + p.nz * ca;
      if (nzr > 0.05) continue;                            // 向こうを向いた面は描かない
      const s = F / (F + zr);
      const X = Math.round(LX + xr * s), Y = Math.round(cy + p.y * s);
      if (X < 0 || Y < 0 || X >= CW || Y >= CH) continue;
      const j = Y * CW + X;
      if (zr >= zb[j]) continue;
      zb[j] = zr;
      const lit = 0.5 + 0.5 * Math.min(1, -nzr + (p.ny < 0 ? 0.35 : 0));
      // 色は ななめに流れるグラデーション(時間で 水色→青→紫→桃 と移っていく)
      const col = palette((p.y / (ROWS * U)) * 0.55 + (p.x / (COLS * U)) * 0.3 - t * 0.2);
      const scan = ((Y + Math.floor(t * 8)) % 3 === 0) ? 0.8 : 1;              // 走査線
      const b = (0.58 + 0.42 * lit) * scan;
      cb[j * 4] = col[0] * b; cb[j * 4 + 1] = col[1] * b; cb[j * 4 + 2] = col[2] * b;
      cb[j * 4 + 3] = 255;
    }
    for (let j = 0; j < CW * CH; j++) {
      if (!cb[j * 4 + 3]) continue;
      const i = j * 4, x = j % CW, y = (j / CW) | 0;
      // 文字のふち(となりが空いている点)は白っぽく光らせて、壁の色に埋もれないようにする
      const rim = x === 0 || y === 0 || x === CW - 1 || y === CH - 1
        || !cb[i - 4 + 3] || !cb[i + 4 + 3] || !cb[i - CW * 4 + 3] || !cb[i + CW * 4 + 3];
      const w = rim ? 0.45 : 0;
      px[i] = cb[i] + (255 - cb[i]) * w; px[i + 1] = cb[i + 1] + (255 - cb[i + 1]) * w; px[i + 2] = cb[i + 2] + (255 - cb[i + 2]) * w;
      px[i + 3] = (Math.random() < 0.04) ? 170 : 245;      // ときどきチラつく
    }
    // 文字の下の光の輪
    const ry = cy + 13;
    for (let i = 0; i < 28; i++) {
      const a = i / 28 * Math.PI * 2 + t * 2;
      const x = Math.round(LX + Math.cos(a) * 12), y = Math.round(ry + Math.sin(a) * 2);
      if (i % 3 !== 0) put(x, y, 160, 200, 255, Math.sin(a) > 0 ? 200 : 110);
    }
    g.putImageData(img, 0, 0);
  }

  window.mountAIHolo = function (stage, lensX, lensY) {
    let cv = document.getElementById('aiholo');
    if (!cv) {
      cv = document.createElement('canvas');
      cv.id = 'aiholo';
      cv.width = CW; cv.height = CH;
      cv.setAttribute('aria-hidden', 'true');
      stage.appendChild(cv);
    }
    cv.style.left = (lensX - LX) + 'px';
    cv.style.top = (lensY - LY) + 'px';
    const g = cv.getContext('2d');
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      draw(g, 0.3);                                       // 動きを減らす設定: 少し斜めを向いた1枚だけ
      return cv;
    }
    if (cv._running) return cv;
    cv._running = true;
    let prev = 0;
    const tick = (ms) => {
      requestAnimationFrame(tick);
      if (document.hidden || ms - prev < 1000 / 15) return;   // 15コマ/秒(ドット絵らしく・電池にやさしく)
      if (window.AI_HOLO_PAUSED) return;                       // 詳細パネルを開いている間は止める
      prev = ms;
      draw(g, ms / 1000);
    };
    requestAnimationFrame(tick);
    return cv;
  };
})();
