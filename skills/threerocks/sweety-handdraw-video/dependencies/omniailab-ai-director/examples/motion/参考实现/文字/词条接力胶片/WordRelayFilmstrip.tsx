// ---
// name: omniailab-motion-demo-word-relay-filmstrip
// description: 词条接力胶片 v3 —— 批次 12 单点微调：右侧大词块（Computer+动词）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 词条接力胶片 v3 —— 批次 12 单点微调：右侧大词块（Computer+动词）
// 的垂直中心与左列当前页面卡的垂直中点（y=540）对齐（top 462→402）。
// 其余沿用 v2：对照用户截图重做（perplexity-promo01，7 张）：
// ① 左列页面卡黑白相间、每张等高（940x530，间距 105）；
// ② 左列平时静止，只在右侧切词的窗口内滚动一格（滚动与切词同步）；
// ③ 尺寸/字号/位置按截图量取：卡 x=106 宽 940，词右对齐至 x≈1710，
//    Didot 系衬线 116px，"Computer" 固定第一行，动词第二行原位灰化淡出换词。
import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const CARD_W = 940;
const CARD_H = 530;
const GAP = 105;
const STEP = CARD_H + GAP;

// —— 页面卡集合：黑白相间（奇偶强制交替），内容各异 ——
const DarkArticle: React.FC<{ seed: number }> = ({ seed }) => {
  const rand = mulberry32(seed);
  return (
    <div style={{ position: 'absolute', inset: 0, background: '#101318', padding: '38px 46px' }}>
      <div style={{ display: 'flex', gap: 26, alignItems: 'center', marginBottom: 34 }}>
        <div style={{ width: 90, height: 13, background: '#d8b25a', borderRadius: 3, opacity: 0.9 }} />
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 18 }}>
          {[0, 1, 2, 3].map((i) => <div key={i} style={{ width: 54, height: 9, background: '#3a3f48', borderRadius: 3 }} />)}
        </div>
      </div>
      <div style={{ width: 150, height: 9, background: '#a8452e', borderRadius: 3, marginBottom: 20 }} />
      <div style={{ width: '62%', height: 30, background: '#e8e6df', borderRadius: 5, marginBottom: 14 }} />
      <div style={{ width: '44%', height: 30, background: '#e8e6df', borderRadius: 5, marginBottom: 30 }} />
      <div style={{ display: 'flex', gap: 30 }}>
        <div style={{ flex: 1.3 }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} style={{ height: 9, width: `${62 + rand() * 34}%`, background: '#41454e', borderRadius: 3, marginBottom: 13 }} />
          ))}
        </div>
        <div style={{ flex: 1, border: '1px solid #2c313a', borderRadius: 8, background: '#151a22', padding: 20 }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 15 }}>
              <div style={{ width: 58, height: 12, background: '#6d5423', borderRadius: 3 }} />
              <div style={{ width: `${34 + rand() * 30}%`, height: 9, background: '#4a4f58', borderRadius: 3 }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const LightMedal: React.FC<{ seed: number }> = ({ seed }) => {
  const rand = mulberry32(seed);
  return (
    <div style={{ position: 'absolute', inset: 0, background: '#ffffff', padding: '36px 44px' }}>
      <div style={{ width: 120, height: 9, background: '#b9bcc2', borderRadius: 3, marginBottom: 14 }} />
      <div style={{ display: 'flex', gap: 14, marginBottom: 24 }}>
        <div style={{ width: 150, height: 32, background: '#17181a', borderRadius: 5 }} />
        <div style={{ width: 170, height: 32, background: '#2f6fd6', borderRadius: 5, opacity: 0.85 }} />
      </div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 22 }}>
        {[64, 96, 78, 110, 70, 88, 92].map((w, i) => (
          <div key={i} style={{ width: w, height: 24, borderRadius: 12, background: i === 0 ? '#2f6fd6' : '#f2f3f5', border: i === 0 ? 'none' : '1px solid #dfe1e5' }} />
        ))}
      </div>
      <div style={{ height: 34, borderRadius: 6, border: '1px solid #dfe1e5', marginBottom: 26 }} />
      <div style={{ display: 'flex', gap: 16 }}>
        {[0, 1, 2].map((c) => (
          <div key={c} style={{ flex: 1, border: '1px solid #e4e6ea', borderRadius: 8, padding: 18 }}>
            <div style={{ width: 74, height: 8, background: '#9aa0aa', borderRadius: 3, marginBottom: 12 }} />
            <div style={{ width: `${52 + rand() * 30}%`, height: 13, background: '#1c1d20', borderRadius: 4, marginBottom: 10 }} />
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <div style={{ width: 20, height: 13, background: c === 0 ? '#c8342f' : c === 1 ? '#2c8a4b' : '#c8342f', borderRadius: 2 }} />
              <div style={{ width: 60, height: 8, background: '#c3c7cd', borderRadius: 3 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const DarkStats: React.FC<{ seed: number }> = ({ seed }) => {
  const rand = mulberry32(seed);
  return (
    <div style={{ position: 'absolute', inset: 0, background: '#0e0d12', padding: '44px 52px' }}>
      <div style={{ borderLeft: '3px solid #6a2430', paddingLeft: 34 }}>
        {[
          { n: 92, accent: false }, { n: 74, accent: false }, { n: 58, accent: false }, { n: 118, accent: true },
        ].map((row, i) => (
          <div key={i} style={{ display: 'flex', gap: 20, alignItems: 'center', marginBottom: 26 }}>
            <div style={{ width: row.n, height: row.accent ? 30 : 20, background: row.accent ? '#c33b2e' : '#d6d3cc', borderRadius: 4, opacity: row.accent ? 0.95 : 0.85 }} />
            <div style={{ width: 130, height: 11, background: row.accent ? '#7a3328' : '#4c4a52', borderRadius: 3 }} />
            <div style={{ width: `${20 + rand() * 26}%`, height: 8, background: '#33323a', borderRadius: 3 }} />
          </div>
        ))}
      </div>
      <div style={{ marginTop: 30, background: '#1c1216', borderRadius: 8, padding: '22px 30px', display: 'flex', gap: 60 }}>
        {[0, 1, 2].map((i) => (
          <div key={i}>
            <div style={{ width: 96, height: 16, background: '#c3564a', borderRadius: 3, marginBottom: 10, opacity: 0.9 }} />
            <div style={{ width: 76, height: 8, background: '#5a4448', borderRadius: 3 }} />
          </div>
        ))}
      </div>
    </div>
  );
};

const LightTable: React.FC<{ seed: number }> = ({ seed }) => {
  const rand = mulberry32(seed);
  return (
    <div style={{ position: 'absolute', inset: 0, background: '#ffffff', padding: '34px 44px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 26 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div style={{ width: 34, height: 22, background: '#1d4f9e', borderRadius: 4 }} />
          <div style={{ width: 130, height: 11, background: '#2a2b2e', borderRadius: 3 }} />
        </div>
        <div style={{ display: 'flex', gap: 16 }}>
          <div style={{ width: 84, height: 10, background: '#c6c9cf', borderRadius: 3 }} />
          <div style={{ width: 70, height: 10, background: '#c6c9cf', borderRadius: 3 }} />
        </div>
      </div>
      {Array.from({ length: 7 }).map((_, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 20, padding: '13px 0', borderBottom: '1px solid #eceef1' }}>
          <div style={{ width: 22, height: 10, background: '#9aa0aa', borderRadius: 3 }} />
          <div style={{ width: 26, height: 16, background: ['#b23a3a', '#2c62b8', '#caa53c', '#3a8a52'][i % 4], borderRadius: 2, opacity: 0.85 }} />
          <div style={{ width: 90 + rand() * 60, height: 10, background: '#3a3c40', borderRadius: 3 }} />
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 46 }}>
            <div style={{ width: 16, height: 16, background: i % 3 === 1 ? '#8d8f94' : '#eceef1', borderRadius: 3 }} />
            <div style={{ width: 16, height: 16, background: i % 3 === 2 ? '#a5772e' : '#eceef1', borderRadius: 3 }} />
            <div style={{ width: 14, height: 10, background: '#5a5c60', borderRadius: 3 }} />
          </div>
        </div>
      ))}
    </div>
  );
};

const DarkMri: React.FC = () => (
  <div style={{ position: 'absolute', inset: 0, background: '#08090b', padding: 0 }}>
    <div style={{ height: 44, borderBottom: '1px solid #1c1e22', display: 'flex', alignItems: 'center', gap: 16, padding: '0 26px' }}>
      <div style={{ width: 100, height: 10, background: '#cfd2d6', borderRadius: 3, opacity: 0.8 }} />
      <div style={{ marginLeft: 'auto', width: 60, height: 8, background: '#2c2f34', borderRadius: 3 }} />
    </div>
    <div style={{ display: 'flex', height: CARD_H - 44 }}>
      <div style={{ width: 190, borderRight: '1px solid #17191d', padding: 20 }}>
        <div style={{ width: 110, height: 10, background: '#b8a24e', borderRadius: 3, marginBottom: 14 }} />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} style={{ height: 7, width: `${58 + (i * 13) % 36}%`, background: '#2e3138', borderRadius: 3, marginBottom: 10 }} />
        ))}
        <div style={{ marginTop: 24, width: 44, height: 130, margin: '24px auto 0', border: '1px solid #4a4330', borderRadius: 6 }} />
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{
          width: 300, height: 360, borderRadius: 16,
          background: 'radial-gradient(ellipse 46% 40% at 50% 42%, #b9bcc0 0%, #6c7076 34%, #33363c 62%, #101216 100%)',
          position: 'relative',
        }}>
          {[[120, 100], [200, 150], [96, 210]].map(([x, y], i) => (
            <div key={i} style={{ position: 'absolute', left: x, top: y, width: 12, height: 12, borderRadius: 6, border: '2px solid #d8b25a' }} />
          ))}
        </div>
      </div>
      <div style={{ width: 170, borderLeft: '1px solid #17191d', padding: 18 }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} style={{ height: 7, width: `${50 + (i * 17) % 44}%`, background: '#26292f', borderRadius: 3, marginBottom: 11 }} />
        ))}
      </div>
    </div>
  </div>
);

const LightPortfolio: React.FC = () => (
  <div style={{ position: 'absolute', inset: 0, background: '#f7f7f8', padding: '40px 60px', textAlign: 'center' }}>
    <div style={{ width: 340, height: 26, background: '#242528', borderRadius: 5, margin: '10px auto 18px' }} />
    {[420, 470, 300].map((w, i) => (
      <div key={i} style={{ width: w, height: 9, background: '#b6b9bf', borderRadius: 3, margin: '0 auto 11px' }} />
    ))}
    <div style={{ display: 'flex', gap: 18, marginTop: 36 }}>
      {[0, 1, 2, 3].map((i) => (
        <div key={i} style={{ flex: 1, height: 150, background: '#ffffff', border: '1px solid #e2e4e8', borderRadius: 10, padding: 16, textAlign: 'left' }}>
          <div style={{ width: '54%', height: 12, background: '#2c2d30', borderRadius: 3, marginBottom: 12 }} />
          <div style={{ width: '80%', height: 8, background: '#d3d6db', borderRadius: 3, marginBottom: 8 }} />
          <div style={{ width: '66%', height: 8, background: '#d3d6db', borderRadius: 3 }} />
        </div>
      ))}
    </div>
  </div>
);

// 黑白相间的固定顺序（奇偶交替）
const CARDS: React.FC<{ seed: number }>[] = [
  ({ seed }) => <DarkArticle seed={seed} />,
  ({ seed }) => <LightMedal seed={seed} />,
  () => <DarkMri />,
  ({ seed }) => <LightTable seed={seed} />,
  ({ seed }) => <DarkStats seed={seed} />,
  () => <LightPortfolio />,
];

const WORDS = ['researches', 'builds', 'codes'];
// 切词窗口：第一个词入场 f14–30；换词 f62–78、f108–124
const SWITCHES = [14, 62, 108];
const SW_DUR = 16;
const SERIF = '"Didot", "Bodoni 72", "Playfair Display", Georgia, serif';

export const WordRelayFilmstrip: React.FC = () => {
  const frame = useCurrentFrame();

  // —— 滚动步进：平时静止，仅在切词窗口内滚一格（ease-in-out）——
  let stepF = 0;
  SWITCHES.forEach((s) => {
    const p = interpolate(frame, [s, s + SW_DUR], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    // easeInOutCubic
    stepF += p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
  });
  const scroll = stepF * STEP;

  // 卡片布局：中心卡顶 y=275，向两侧铺开；黑白相间
  const total = CARDS.length * STEP;
  const cards: React.ReactNode[] = [];
  for (let rep = -1; rep < 2; rep++) {
    CARDS.forEach((C, i) => {
      const y = 275 + i * STEP + rep * total - scroll;
      if (y > 1200 || y < -CARD_H - 120) return;
      cards.push(
        <div key={`${rep}-${i}`} style={{
          position: 'absolute', top: y, left: 106, width: CARD_W, height: CARD_H,
          borderRadius: 12, overflow: 'hidden',
          boxShadow: '0 12px 40px rgba(30,26,20,0.14)',
          border: '1px solid rgba(0,0,0,0.06)', background: '#fff',
        }}>
          <C seed={(i + 1) * 733} />
        </div>,
      );
    });
  }

  // —— 右侧词接力：原位交叉淡（旧词灰化淡出，新词淡入，不位移）——
  const wordStyle: React.CSSProperties = {
    fontFamily: SERIF, fontWeight: 400, fontSize: 116, lineHeight: 1.18,
    letterSpacing: '0.002em', textAlign: 'right', whiteSpace: 'nowrap',
  };
  // 每个词的生命周期：入场淡入（黑）→ 常驻黑 → 下个切点前 14 帧灰化
  //（截图 4/6 捕捉到的就是"旧词已灰、新词未现"的状态）→ 切点起淡出。
  const smooth = (x: number) => x * x * (3 - 2 * x);
  const wordNodes = WORDS.map((w, i) => {
    const sIn = SWITCHES[i];
    const sOut = i + 1 < SWITCHES.length ? SWITCHES[i + 1] : null;
    // 新词后半窗口淡入（避免与旧词叠影）
    const pIn = interpolate(frame, [sIn + 7, sIn + SW_DUR], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    if (i === 0 ? frame < sIn : pIn <= 0) return null;
    const pInEff = i === 0 ? interpolate(frame, [sIn, sIn + 12], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    }) : pIn;
    // 灰化：切点前 14 帧开始，切点时已全灰
    const grey = sOut ? interpolate(frame, [sOut - 14, sOut - 2], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    }) : 0;
    // 淡出：切点起前半窗口内出完
    const pOut = sOut ? interpolate(frame, [sOut, sOut + 8], [1, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    }) : 1;
    const op = smooth(pInEff) * smooth(pOut);
    if (op <= 0) return null;
    const mix = smooth(grey);
    const ch = Math.round(0x19 + (0x9d - 0x19) * mix);
    return (
      <div key={w} style={{
        ...wordStyle, position: 'absolute', right: 0, top: 0,
        color: `rgb(${ch},${Math.round(0x19 + (0x98 - 0x19) * mix)},${Math.round(0x19 + (0x8e - 0x19) * mix)})`,
        opacity: op,
      }}>
        {w}
      </div>
    );
  });

  return (
    <AbsoluteFill style={{ background: '#faf8f3' }}>
      <div style={{ position: 'absolute', inset: 0 }}>{cards}</div>
      {/* 右侧词组：Computer 固定第一行，动词第二行原位换词。
          v3：块总高≈137(Computer 行)+140(词行容器)=277，垂直中心须对齐
          当前页面卡中点 y=540（卡顶 275 + 卡高 530/2）→ top=540-277/2≈402 */}
      <div style={{ position: 'absolute', right: 210, top: 402 }}>
        <div style={{ ...wordStyle, color: '#191919' }}>Computer</div>
        <div style={{ position: 'relative', height: 140 }}>{wordNodes}</div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

