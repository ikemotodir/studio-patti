// キャラクターに関するデータ(PC版 design.html とスマホ版 design_m.html で共用)
// ─── キャラクターに関するデータ(仮。池本さんが選んだものを本掲載にする) ───
const DATA_SECTIONS = [
  { h: '若い人は、キャラクターとアニメの中で暮らしている', items: [
    { fig: '87.4%', rec: false,
      say: '高校生がアニメを観ている割合。大学生も85.6%。好きな作品にお金を使った経験も7割を超える。',
      src: 'TesTee Lab「学生のアニメに関する調査【2024年版】」(テスティー)',
      url: 'https://lab.testee.co/anime_student2024/' },
    { fig: '約4人に3人', rec: true,
      say: '15〜19歳に「好きなキャラクターがいる」割合(男72.9%／女75.1%)。全年代で最も高い。',
      src: '矢野経済研究所「キャラクターに関する消費者アンケート調査(2025年)」',
      url: 'https://www.yano.co.jp/press-release/show/press_id/4012' },
    { fig: '約1.5倍', rec: false,
      say: '「推し活」主要16分野の市場規模が2020→2024年度で約50%拡大。国の広報誌が若年層主導の成長消費と位置づけている。',
      src: '財務省広報誌『ファイナンス』経済トレンド「推し活」(2025年)',
      url: 'https://www.mof.go.jp/public_relations/finance/2025011/202511f.pdf' },
  ]},
  { h: '会社の話は、もうテレビでは届かない', items: [
    { fig: '95.7%', rec: true,
      say: '10代のYouTube利用率(20代97.2%)。TikTokも10代65.7%と、全年代で最も高い。',
      src: '総務省 情報通信政策研究所「令和6年度 情報通信メディアの利用時間と情報行動に関する調査」',
      url: 'https://www.soumu.go.jp/main_content/001017240.pdf' },
    { fig: '1日165分', rec: true,
      say: '10代が平日1日にネット動画を見ている時間。テレビ(リアルタイム)は40分で、その差は約4倍。',
      src: '総務省 情報通信政策研究所(同上・令和6年度)',
      url: 'https://www.soumu.go.jp/main_content/001017240.pdf' },
    { fig: '75.0%', rec: false,
      say: '10代のInstagram利用率(20代は78.0%)。絵とキャラクターで語れる素材を持つほど、若年層への発信で有利になる。',
      src: '総務省 情報通信政策研究所(同上・令和6年度)',
      url: 'https://www.soumu.go.jp/main_content/001017240.pdf' },
  ]},
  { h: 'だから、採用に効く', items: [
    { fig: '86.6%', rec: true,
      say: 'Z世代の就活生が企業選びで採用動画を参考にした割合。観たあとに志望度が上がった人は77.0%。',
      src: 'moovy「Z世代就活生の採用動画に関する調査」(2022年)',
      url: 'https://prtimes.jp/main/html/rd/p/000000009.000062343.html' },
    { fig: '8割超', rec: false,
      say: '2026年卒の学生が、就活準備・インターンの情報収集に「動画を活用したい」と答えた割合。',
      src: '学情「就職活動準備における動画活用」調査(2024年・26卒対象)',
      url: 'https://prtimes.jp/main/html/rd/p/000001237.000013485.html' },
    { fig: '57.1%', rec: false,
      say: '20代がTikTokで就職活動の情報を集めた経験。動画で発信している企業には約88%が好印象を持つ。',
      src: 'TORIHADA「Z世代の就職活動におけるTikTok活用調査」(2024年)',
      url: 'https://prtimes.jp/main/html/rd/p/000000160.000030350.html' },
  ]},
  { h: 'キャラクターは、すでに社会のインフラ', items: [
    { fig: '2兆8,492億円', rec: true,
      say: '国内キャラクタービジネスの市場規模(2025年度予測)。前年度比102.6%で拡大が続いている。',
      src: '矢野経済研究所「キャラクタービジネスに関する調査(2025年)」',
      url: 'https://www.yano.co.jp/press-release/show/press_id/4012' },
    { fig: '1,553体', rec: false,
      say: '自治体の公式ご当地キャラクターの数(2021年度)。10年で倍増し、市区町村の約8割が持っている。',
      src: '日本経済新聞「目指せくまモン 全国1500超、ゆるキャラに託す発信力」(2022年)',
      url: 'https://www.nikkei.com/article/DGXZQOCC0429G0U2A200C2000000/' },
    { fig: '42%', rec: false,
      say: '「キャラクターを使っている企業は記憶に残る」と答えた生活者の割合。商品理解に役立つは約46%。',
      src: 'Minto「企業によるキャラクター利用効果の調査」',
      url: 'https://prtimes.jp/main/html/rd/p/000000059.000029274.html' },
  ]},
];
function designDataHTML() {
  const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  let h = '<h2>キャラクターに関するデータ</h2>'
        + '<p class="lead">企業や自治体が、若い人材に届き、選ばれるために。'
        + 'キャラクターとアニメーションが「あった方がいいもの」ではなく「必要なもの」である理由を、公的統計と調査データで。</p>'
        + '<p class="note">★はスタジオパッチが特に注目している数字です。'
        + 'それぞれの「出典先」から、元の調査資料を確認できます。</p>';
  DATA_SECTIONS.forEach(sec => {
    h += '<h3>' + esc(sec.h) + '</h3><ul>';
    sec.items.forEach(it => {
      h += '<li><div class="fig"><span>' + esc(it.fig) + '</span>'
         + (it.rec ? '<span class="rec">★</span>' : '') + '</div>'
         + '<div class="body"><div class="say">' + esc(it.say) + '</div>'
         + '<div class="src">' + esc(it.src) + ' '
         + '<a href="' + it.url + '" target="_blank" rel="noopener">出典先</a>'
         + '</div></div></li>';
    });
    h += '</ul>';
  });
  return h;
}
