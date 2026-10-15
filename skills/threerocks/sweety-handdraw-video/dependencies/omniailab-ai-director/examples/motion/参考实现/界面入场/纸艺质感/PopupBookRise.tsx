// ---
// name: omniailab-motion-demo-popup-book-rise
// description: popup-book-rise —— 立体书立起
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// popup-book-rise —— 立体书立起
// FakeDashboard(A) 打平躺下（场景 rotateX 75° 透视俯视），6 张卡片是贴在页上的
// 纸片，沿各自底边从平躺错峰立起（rotateX 90°→-5° 过冲→0° 回弹，即立到 95° 再回 90°），
// 根部投影随立起角度收窄变淡。全部立起后整个场景轻微回正（75°→68°）收尾。
// 卡片用独立网格复刻 dashboard A 区布局（Fixtures 内嵌卡无法单独驱动）。
// 收尾 f108 后真静止 ≥52f。帧确定性：全由 frame 派生。
import React from 'react';
import { useCurrentFrame, interpolate, spring, Easing } from 'remotion';
import { G, Card } from '../../_fixtures/Fixtures';

const FPS = 30;
const HOLD = 14; // 开头静置
const STAGGER = 7;
const RISE_DUR = 34; // spring 视觉收敛帧数
const LAST_START = HOLD + 5 * STAGGER; // 49
const SETTLE = LAST_START + RISE_DUR; // 83：全部立起
const REST = SETTLE + 25; // 108：场景回正完成

// dashboard A 区几何（照抄 FakeDashboard：侧栏 220 + 顶栏 72 + padding 36 + gap 28）
const AREA_X = 220 + 36;
const AREA_Y = 72 + 36;
const AREA_W = 1920 - 220 - 72;
const AREA_H = 1080 - 72 - 72;
const GAP = 28;
const CELL_W = (AREA_W - 2 * GAP) / 3;
const CELL_H = (AREA_H - GAP) / 2;

const PageCard: React.FC<{ i: number; frame: number }> = ({ i, frame }) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  // 远排（row 0）先立，近排后立；同排从左到右
  const order = row === 0 ? col : 3 + col;
  const start = HOLD + order * STAGGER;

  const s = spring({
    frame: frame - start,
    fps: FPS,
    config: { damping: 11, stiffness: 130, mass: 0.9 },
    durationInFrames: RISE_DUR,
    durationRestThreshold: 0.0001,
  });
  // 平躺（贴页面 = local 0°）→ 立起（垂直页面 = local -90°，顶边朝观众翻起），
  // spring 过冲自然冲过 -90° 到约 -95°（纸的韧性）再回弹。
  const rx = interpolate(s, [0, 1], [0, -90]);

  // 根部投影：躺平时长影（卡片盖在页面上），立起后收成窄条
  const lie = 1 - Math.min(Math.abs(rx) / 90, 1); // 1 = 躺平, 0 = 立直
  const shH = 14 + 90 * Math.max(lie, 0);
  const shAlpha = 0.1 + 0.16 * Math.max(lie, 0);

  return (
    <div
      style={{
        position: 'absolute',
        left: AREA_X + col * (CELL_W + GAP),
        top: AREA_Y + row * (CELL_H + GAP),
        width: CELL_W,
        height: CELL_H,
        transformStyle: 'preserve-3d',
      }}
    >
      {/* 根部投影贴在页面上，不随卡片立起 */}
      <div
        style={{
          position: 'absolute',
          left: 6,
          right: 6,
          bottom: -4,
          height: shH,
          background: `rgba(0,0,0,${shAlpha})`,
          borderRadius: 12,
          filter: 'blur(10px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `rotateX(${rx}deg)`,
          transformOrigin: '50% 100%',
          backfaceVisibility: 'hidden',
        }}
      >
        <Card w={0} h={0} seed={i + 1} style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  );
};

export const PopupBookRise: React.FC = () => {
  const frame = useCurrentFrame();

  // 场景（书页）俯视角：全程 75°，全部立起后轻微回正到 68°
  const sceneRx = interpolate(frame, [SETTLE, REST], [75, 68], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ width: 1920, height: 1080, background: '#dddddb', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, perspective: 2600, perspectiveOrigin: '50% 30%' }}>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            transform: `translateY(-40px) rotateX(${sceneRx}deg)`,
            transformOrigin: '50% 62%',
            transformStyle: 'preserve-3d',
          }}
        >
          {/* 书页底板：dashboard 的壳（侧栏+顶栏+空白页面） */}
          <div style={{ position: 'absolute', inset: 0, background: G.bg, boxShadow: '0 40px 80px rgba(0,0,0,0.25)' }}>
            <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 220, background: G.side, padding: '28px 22px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 18 }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: '#777775' }} />
              {Array.from({ length: 7 }).map((_, i) => (
                <div key={i} style={{ height: 12, width: `${60 + ((i * 29) % 35)}%`, background: G.sideBar, borderRadius: 6 }} />
              ))}
            </div>
            <div style={{ position: 'absolute', left: 220, right: 0, top: 0, height: 72, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', padding: '0 32px', gap: 20, boxSizing: 'border-box' }}>
              <div style={{ height: 18, width: 180, background: G.bar, borderRadius: 9 }} />
              <div style={{ marginLeft: 'auto', height: 36, width: 320, background: '#fff', border: `2px solid ${G.line}`, borderRadius: 18, boxSizing: 'border-box' }} />
              <div style={{ width: 36, height: 36, borderRadius: 18, background: G.mid }} />
            </div>
          </div>
          {/* 6 张纸片卡沿底边立起 */}
          {Array.from({ length: 6 }).map((_, i) => (
            <PageCard key={i} i={i} frame={frame} />
          ))}
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

