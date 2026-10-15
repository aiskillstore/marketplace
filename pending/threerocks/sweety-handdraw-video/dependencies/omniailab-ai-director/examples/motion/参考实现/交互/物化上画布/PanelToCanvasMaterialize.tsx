// ---
// name: omniailab-motion-demo-panel-to-canvas-materialize
// description: panel-to-canvas-materialize —— miro-promo 84–92s
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// panel-to-canvas-materialize —— miro-promo 84–92s
// 侧面板表格行复选框自动逐个打勾 → 按钮按下 → 三行内容飞出面板、
// 物化成画布上三张独立卡片落位（行→卡跨容器形态迁移，尺寸/形状插值）。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const PANEL_X = 1210;
const PANEL_Y = 90;
const PANEL_W = 620;
const ROW_H = 92;
const ROWS_TOP = 210; // 面板内第一行的画面 y

// 行 → 卡的目标位（画布左侧区域）
const TARGETS = [
  { x: 150, y: 150, rot: -2 },
  { x: 480, y: 420, rot: 1.5 },
  { x: 180, y: 660, rot: 2 },
];
const CARD_W = 480;
const CARD_H = 240;

const CHECK_FRAMES = [12, 22, 32]; // 三个复选框打勾时刻
const BUTTON_FRAME = 46; // 按钮按下
const FLY_START = [54, 60, 66]; // 三行错峰起飞

export const PanelToCanvasMaterialize: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const btnPress = interpolate(frame, [BUTTON_FRAME, BUTTON_FRAME + 3, BUTTON_FRAME + 9], [0, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 画布点阵底 */}
      <AbsoluteFill
        style={{
          backgroundImage: `radial-gradient(${G.line} 3px, transparent 3px)`,
          backgroundSize: '52px 52px',
        }}
      />

      {/* 侧面板 */}
      <div
        style={{
          position: 'absolute',
          left: PANEL_X,
          top: PANEL_Y,
          width: PANEL_W,
          height: 900,
          background: G.panel,
          border: `2px solid ${G.border}`,
          borderRadius: 20,
          boxShadow: '0 8px 32px rgba(0,0,0,0.10)',
          boxSizing: 'border-box',
          padding: 28,
        }}
      >
        {/* 面板标题 */}
        <div style={{ height: 20, width: 260, background: G.bar, borderRadius: 10, marginBottom: 14 }} />
        <div style={{ height: 12, width: 380, background: G.line, borderRadius: 6, marginBottom: 26 }} />
        {/* 表头 */}
        <div style={{ height: 34, background: G.line, borderRadius: 8, marginBottom: 12, opacity: 0.6 }} />
        {/* 行槽位（行飞走后留白） */}
        {[0, 1, 2].map((i) => (
          <RowSlot key={i} idx={i} frame={frame} fps={fps} />
        ))}
        {/* 面板底部按钮 */}
        <div
          style={{
            position: 'absolute',
            left: 28,
            bottom: 28,
            right: 28,
            height: 64,
            borderRadius: 14,
            background: btnPress > 0 ? G.ink : G.side,
            transform: `scale(${1 - btnPress * 0.06})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 700, fontSize: 22, color: '#f2f2f0', letterSpacing: 0.5 }}>
            Add all to canvas
          </div>
        </div>
      </div>

      {/* 飞行中/落位的三张卡（行→卡形态插值） */}
      {[0, 1, 2].map((i) => (
        <FlyingCard key={i} idx={i} frame={frame} fps={fps} />
      ))}

      {/* 光标 */}
      <Cursor frame={frame} />
    </AbsoluteFill>
  );
};

// 面板内的一行：复选框自动打勾；起飞后槽位塌陷成虚线留白
const RowSlot: React.FC<{ idx: number; frame: number; fps: number }> = ({ idx, frame, fps }) => {
  const checkF = CHECK_FRAMES[idx];
  const flyF = FLY_START[idx];
  const checked = frame >= checkF;
  const checkPop = spring({ frame: frame - checkF, fps, config: { damping: 10, stiffness: 260 } });
  const flown = frame >= flyF;

  return (
    <div
      style={{
        height: ROW_H - 12,
        marginBottom: 12,
        borderRadius: 10,
        border: flown ? `2px dashed ${G.line}` : `2px solid ${G.border}`,
        background: flown ? 'transparent' : G.card,
        boxSizing: 'border-box',
        display: 'flex',
        alignItems: 'center',
        gap: 18,
        padding: '0 20px',
        opacity: flown ? 0.7 : 1,
      }}
    >
      {!flown && (
        <>
          {/* 复选框 */}
          <div
            style={{
              width: 30,
              height: 30,
              borderRadius: 8,
              border: `3px solid ${checked ? G.ink : G.bar}`,
              background: checked ? G.ink : 'transparent',
              boxSizing: 'border-box',
              transform: checked ? `scale(${0.8 + 0.2 * checkPop})` : 'scale(1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {checked && (
              <svg width="18" height="18" viewBox="0 0 18 18">
                <path d="M3 9.5 L7.2 13.5 L15 4.5" stroke="#fff" strokeWidth="3.2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </div>
          <div style={{ height: 14, width: 180 + idx * 40, background: G.bar, borderRadius: 7 }} />
          <div style={{ marginLeft: 'auto', height: 12, width: 90, background: G.line, borderRadius: 6 }} />
        </>
      )}
    </div>
  );
};

// 行→卡：位置沿贝塞尔弧线飞、尺寸/圆角/内容布局同步插值
const FlyingCard: React.FC<{ idx: number; frame: number; fps: number }> = ({ idx, frame, fps }) => {
  const flyF = FLY_START[idx];
  if (frame < flyF) return null;

  const t = spring({ frame: frame - flyF, fps, config: { damping: 16, stiffness: 60 }, durationInFrames: 34 });

  // 起点：面板内该行的屏幕位置/尺寸
  const sx = PANEL_X + 30;
  const sy = ROWS_TOP + idx * ROW_H;
  const sw = PANEL_W - 60;
  const sh = ROW_H - 12;
  const tgt = TARGETS[idx];

  // 弧线：中点向上抬，像被"倒"出来
  const mx = (sx + tgt.x) / 2;
  const my = Math.min(sy, tgt.y) - 170;
  const u = t;
  const x = (1 - u) * (1 - u) * sx + 2 * (1 - u) * u * mx + u * u * tgt.x;
  const y = (1 - u) * (1 - u) * sy + 2 * (1 - u) * u * my + u * u * tgt.y;

  const w = sw + (CARD_W - sw) * u;
  const h = sh + (CARD_H - sh) * u;
  const rot = tgt.rot * u;
  const radius = 10 + 8 * u;
  const shadow = interpolate(u, [0, 1], [0.08, 0.16]);
  // 行内容(单行水平) → 卡内容(标题+行+footer) 交叉淡化
  const rowOp = Math.max(0, 1 - u * 2.2);
  const cardOp = Math.max(0, (u - 0.45) / 0.55);

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        background: G.card,
        border: `2px solid ${G.border}`,
        borderRadius: radius,
        boxShadow: `0 ${10 + 14 * u}px ${24 + 20 * u}px rgba(0,0,0,${shadow})`,
        transform: `rotate(${rot}deg)`,
        boxSizing: 'border-box',
        overflow: 'hidden',
        zIndex: 10 + idx,
      }}
    >
      {/* 行形态内容 */}
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', gap: 18, padding: '0 20px', opacity: rowOp }}>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: G.ink }} />
        <div style={{ height: 14, width: 180 + idx * 40, background: G.bar, borderRadius: 7 }} />
      </div>
      {/* 卡形态内容 */}
      <div style={{ position: 'absolute', inset: 0, padding: 24, display: 'flex', flexDirection: 'column', gap: 12, opacity: cardOp, boxSizing: 'border-box' }}>
        <div style={{ height: 18, width: `${52 + idx * 12}%`, background: G.bar, borderRadius: 9 }} />
        <div style={{ height: 11, width: '84%', background: G.line, borderRadius: 5 }} />
        <div style={{ height: 11, width: '66%', background: G.line, borderRadius: 5 }} />
        <div style={{ marginTop: 'auto', display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ width: 28, height: 28, borderRadius: 14, background: G.mid }} />
          <div style={{ height: 11, width: 70, background: G.line, borderRadius: 5 }} />
        </div>
      </div>
    </div>
  );
};

const Cursor: React.FC<{ frame: number }> = ({ frame }) => {
  // 光标：从画面中部移到按钮上并停留按下
  const bx = PANEL_X + PANEL_W / 2;
  const by = PANEL_Y + 900 - 60;
  const x = interpolate(frame, [8, BUTTON_FRAME - 4], [900, bx], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });
  const y = interpolate(frame, [8, BUTTON_FRAME - 4], [560, by], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });
  const press = interpolate(frame, [BUTTON_FRAME, BUTTON_FRAME + 3, BUTTON_FRAME + 8], [1, 0.78, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <svg
      width={40}
      height={44}
      viewBox="0 0 20 22"
      style={{ position: 'absolute', left: x, top: y, transform: `scale(${press})`, zIndex: 40 }}
    >
      <path d="M2 1 L2 17 L6.5 13.2 L9.4 20 L12.4 18.7 L9.5 12 L15 11.6 Z" fill={G.ink} stroke="#fff" strokeWidth="1.4" />
    </svg>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

