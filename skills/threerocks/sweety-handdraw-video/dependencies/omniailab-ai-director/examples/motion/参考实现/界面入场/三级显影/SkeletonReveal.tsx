// ---
// name: omniailab-motion-demo-skeleton-reveal
// description: 三级显影 —— slack-promo 4–15s 合并
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 三级显影 —— slack-promo 4–15s 合并
// 三级显影：全屏手绘粗笔触涂鸦占位（圆头 blob 线稿，煮沸抖动）→ 一拍内被
// 灰条骨架 UI 窗口替换 → 骨架消息列表滚入，镜头推近时灰条逐行"显影"成
// 头像+文字内容（最后一行末词晚半拍到）。
import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from 'remotion';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const INK = '#2f2f2f';
const PAPER = '#f2f0ea';

// ——— 手绘涂鸦工具：把折线/圆加种子抖动，画粗圆头 stroke ———
const wobbleLine = (
  x1: number, y1: number, x2: number, y2: number,
  seed: number, amp = 7, segs = 8,
) => {
  const rnd = mulberry32(seed);
  const pts: string[] = [];
  for (let i = 0; i <= segs; i++) {
    const t = i / segs;
    const jx = (rnd() - 0.5) * amp * 2;
    const jy = (rnd() - 0.5) * amp * 2;
    pts.push(`${i === 0 ? 'M' : 'L'} ${x1 + (x2 - x1) * t + jx} ${y1 + (y2 - y1) * t + jy}`);
  }
  return pts.join(' ');
};

const wobbleBlobRect = (
  x: number, y: number, w: number, h: number,
  seed: number, amp = 10, r = 70,
) => {
  // 圆头 blob 矩形：四条边中段抖动，四角大圆弧
  const rnd = mulberry32(seed);
  const j = () => (rnd() - 0.5) * amp * 2;
  return [
    `M ${x + r + j()} ${y + j()}`,
    `L ${x + w / 2 + j()} ${y + j()}`, `L ${x + w - r + j()} ${y + j()}`,
    `Q ${x + w + j()} ${y + j()} ${x + w + j()} ${y + r + j()}`,
    `L ${x + w + j()} ${y + h / 2 + j()}`, `L ${x + w + j()} ${y + h - r + j()}`,
    `Q ${x + w + j()} ${y + h + j()} ${x + w - r + j()} ${y + h + j()}`,
    `L ${x + w / 2 + j()} ${y + h + j()}`, `L ${x + r + j()} ${y + h + j()}`,
    `Q ${x + j()} ${y + h + j()} ${x + j()} ${y + h - r + j()}`,
    `L ${x + j()} ${y + h / 2 + j()}`, `L ${x + j()} ${y + r + j()}`,
    `Q ${x + j()} ${y + j()} ${x + r + j()} ${y + j()}`,
  ].join(' ');
};

const wobbleCircle = (cx: number, cy: number, r: number, seed: number, amp = 6) => {
  const rnd = mulberry32(seed);
  const n = 14;
  const pts: string[] = [];
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * Math.PI * 2;
    const rr = r + (rnd() - 0.5) * amp * 2;
    pts.push(`${i === 0 ? 'M' : 'L'} ${cx + Math.cos(a) * rr} ${cy + Math.sin(a) * rr}`);
  }
  return pts.join(' ') + ' Z';
};

const Doodle: React.FC<{ boil: number }> = ({ boil }) => {
  const S = boil * 977; // 每次煮沸换一套抖动种子
  const stroke = {
    fill: 'none' as const,
    stroke: INK,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  };
  return (
    <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
      {/* 窗口大 blob */}
      <path d={wobbleBlobRect(250, 140, 1420, 800, S + 1)} {...stroke} strokeWidth={14} />
      {/* 侧栏分隔 */}
      <path d={wobbleLine(600, 160, 600, 920, S + 2)} {...stroke} strokeWidth={12} />
      {/* 侧栏 logo blob + 短线 */}
      <path d={wobbleCircle(420, 260, 52, S + 3)} {...stroke} strokeWidth={12} />
      {Array.from({ length: 6 }).map((_, i) => (
        <path
          key={`sb${i}`}
          d={wobbleLine(330, 400 + i * 82, 470 + ((i * 53) % 70), 400 + i * 82, S + 10 + i)}
          {...stroke}
          strokeWidth={11}
        />
      ))}
      {/* 主区消息行：圆头像 blob + 波浪文字线 */}
      {Array.from({ length: 4 }).map((_, i) => {
        const y = 320 + i * 160;
        return (
          <g key={`row${i}`}>
            <path d={wobbleCircle(720, y, 44, S + 30 + i)} {...stroke} strokeWidth={12} />
            <path d={wobbleLine(810, y - 28, 1180 + ((i * 97) % 220), y - 28, S + 40 + i)} {...stroke} strokeWidth={11} />
            <path d={wobbleLine(810, y + 24, 1420 - ((i * 71) % 260), y + 24, S + 50 + i)} {...stroke} strokeWidth={11} />
          </g>
        );
      })}
    </svg>
  );
};

// ——— 骨架/内容消息行 ———
const NAMES = ['Ana', 'Ben', 'Kai', 'Mia'];
const AVA = ['#5a5a58', '#7a7a78', '#4a4a48', '#8f8f8d'];
const MSGS = [
  'Morning! Kicking off the rebrand today',
  'Logo drafts are ready for review',
  'Nice — shipping the deck this afternoon',
  'Love it. Can we make it pink?',
];

const Row: React.FC<{ i: number; dev: number; wordAt: (w: number, n: number) => number }> = ({
  i, dev, wordAt,
}) => {
  const words = MSGS[i].split(' ');
  return (
    <div style={{ position: 'relative', height: 96 }}>
      {/* 骨架层 */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', gap: 22, opacity: 1 - dev }}>
        <div style={{ width: 72, height: 72, borderRadius: 16, background: '#d5d5d3' }} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 14, paddingTop: 6 }}>
          <div style={{ height: 18, width: 180 + ((i * 67) % 90), background: '#d5d5d3', borderRadius: 9 }} />
          <div style={{ height: 16, width: `${58 + ((i * 31) % 30)}%`, background: '#e2e2e0', borderRadius: 8 }} />
        </div>
      </div>
      {/* 内容层（逐词显影） */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', gap: 22, opacity: dev > 0.02 ? 1 : 0 }}>
        <div
          style={{
            width: 72, height: 72, borderRadius: 16, background: AVA[i],
            color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 32, fontWeight: 800, opacity: dev,
            transform: `scale(${0.7 + 0.3 * dev})`,
          }}
        >
          {NAMES[i][0]}
        </div>
        <div style={{ flex: 1, paddingTop: 2 }}>
          <div style={{ fontSize: 26, fontWeight: 800, color: INK, opacity: dev }}>
            {NAMES[i]}
            <span style={{ fontWeight: 400, fontSize: 19, color: '#9a9a98', marginLeft: 12 }}>9:0{i + 1} AM</span>
          </div>
          <div style={{ fontSize: 27, color: '#3c3c3a', marginTop: 8 }}>
            {words.map((w, wi) => {
              const p = wordAt(wi, words.length);
              return (
                <span
                  key={wi}
                  style={{
                    display: 'inline-block',
                    marginRight: 9,
                    opacity: p,
                    transform: `translateY(${(1 - p) * 14}px)`,
                  }}
                >
                  {w}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export const SkeletonReveal: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();

  const SWAP = 32; // 涂鸦 → 骨架的那一拍

  // 涂鸦：煮沸抖动 + 一拍内被拉回替换（快速缩退 + 淡出，加速离场）
  const boil = Math.floor(f / 5);
  const doodleOut = interpolate(f, [SWAP, SWAP + 8], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const doodleVisible = f < SWAP + 9;

  // 骨架窗口：swap 时弹入
  const winIn = spring({ frame: f - SWAP, fps, config: { damping: 16, stiffness: 160, mass: 0.7 } });

  // 骨架列表滚入（第二拍）
  const rowSlide = (i: number) =>
    interpolate(f, [SWAP + 12 + i * 6, SWAP + 34 + i * 6], [520, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });

  // 镜头推近
  const zoom = interpolate(f, [66, 142], [1, 1.34], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // 逐行显影
  const devAt = (i: number) =>
    interpolate(f, [80 + i * 13, 92 + i * 13], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: Easing.out(Easing.quad),
    });

  // 逐词进场；最后一行最后一个词晚半拍（+14 帧）
  const wordAt = (row: number) => (w: number, n: number) => {
    const isLastWordOfLastRow = row === 3 && w === n - 1;
    const start = 82 + row * 13 + w * 2.5 + (isLastWordOfLastRow ? 14 : 0);
    return interpolate(f, [start, start + 9], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
  };

  return (
    <AbsoluteFill style={{ background: PAPER, fontFamily: 'Helvetica, Arial, sans-serif', overflow: 'hidden' }}>
      {/* 第三/二拍：骨架 UI 窗口 */}
      {f >= SWAP && (
        <AbsoluteFill
          style={{
            transform: `scale(${zoom})`,
            transformOrigin: '58% 46%',
          }}
        >
          <div
            style={{
              position: 'absolute', left: 250, top: 140, width: 1420, height: 800,
              background: '#ffffff', border: '2px solid #d8d8d6', borderRadius: 22,
              overflow: 'hidden', display: 'flex',
              boxShadow: '0 12px 40px rgba(0,0,0,0.10)',
              opacity: Math.min(1, winIn * 2),
              transform: `scale(${interpolate(winIn, [0, 1], [1.08, 1])})`,
            }}
          >
            {/* 侧栏 */}
            <div style={{ width: 300, background: '#3a3a3a', padding: '30px 26px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 22 }}>
              <div style={{ width: 46, height: 46, borderRadius: 12, background: '#777775' }} />
              {Array.from({ length: 7 }).map((_, i) => (
                <div key={i} style={{ height: 13, width: `${55 + ((i * 37) % 40)}%`, background: '#5a5a58', borderRadius: 7 }} />
              ))}
            </div>
            {/* 主区 */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <div style={{ height: 72, borderBottom: '2px solid #e4e4e2', display: 'flex', alignItems: 'center', padding: '0 34px' }}>
                <div style={{ height: 18, width: 230, background: '#d5d5d3', borderRadius: 9 }} />
              </div>
              <div style={{ flex: 1, padding: '30px 40px', display: 'flex', flexDirection: 'column', gap: 32, overflow: 'hidden' }}>
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} style={{ transform: `translateY(${rowSlide(i)}px)`, opacity: rowSlide(i) > 500 ? 0 : 1 }}>
                    <Row i={i} dev={devAt(i)} wordAt={wordAt(i)} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* 第一拍：手绘涂鸦占位（在骨架之上，一拍内缩退让位） */}
      {doodleVisible && (
        <AbsoluteFill
          style={{
            background: PAPER,
            opacity: 1 - doodleOut,
            transform: `scale(${1 - doodleOut * 0.14})`,
            transformOrigin: '50% 50%',
          }}
        >
          <Doodle boil={boil} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

