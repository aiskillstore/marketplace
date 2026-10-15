// ---
// name: omniailab-motion-demo-segmented-thumb-hero
// description: 分段控件特写 —— 分段控件 thumb 位移当叙事主角拍特写
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 分段控件特写 —— 分段控件 thumb 位移当叙事主角拍特写
// 源：perplexity-promo 2.3–5s。胶囊分段控件（Ask/Computer）带阴影浮入，
// 超大描边箭头光标滑入点击，白 thumb 左→右 ~8f ease-out 滑动，
// 到位瞬间新选项前弹出小图标、旧图标收起。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing, spring, useVideoConfig } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const FONT = 'Helvetica, Arial, sans-serif';

// 超大描边箭头光标
const ArrowCursor: React.FC<{ x: number; y: number; press: number }> = ({ x, y, press }) => (
  <svg
    width={130}
    height={150}
    viewBox="0 0 26 30"
    style={{
      position: 'absolute',
      left: x,
      top: y,
      transform: `scale(${1 - press * 0.14})`,
      transformOrigin: '15% 10%',
      filter: 'drop-shadow(0 8px 16px rgba(0,0,0,0.25))',
    }}
  >
    <path
      d="M4 2 L4 24 L9.5 18.5 L13 27 L16.8 25.4 L13.3 17 L21 17 Z"
      fill="#fff"
      stroke={G.ink}
      strokeWidth={1.8}
      strokeLinejoin="round"
    />
  </svg>
);

const SmileLaptop: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <rect x={7} y={7} width={26} height={19} rx={3} fill="none" stroke={G.ink} strokeWidth={3} />
    <circle cx={15.5} cy={14.5} r={1.9} fill={G.ink} />
    <circle cx={24.5} cy={14.5} r={1.9} fill={G.ink} />
    <path d="M14.5 19 Q20 23.5 25.5 19" stroke={G.ink} strokeWidth={2.6} fill="none" strokeLinecap="round" />
    <path d="M4 31 L36 31" stroke={G.ink} strokeWidth={3.4} strokeLinecap="round" />
  </svg>
);

const AskIcon: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <circle cx={20} cy={20} r={13} fill="none" stroke={G.ink} strokeWidth={3} />
    <path d="M16 17 q0-5 4.5-5 q4.5 0 4.5 4.2 q0 3-3.4 4.4 q-1.6 0.7-1.6 2.6" stroke={G.ink} strokeWidth={2.8} fill="none" strokeLinecap="round" />
    <circle cx={20} cy={28} r={1.8} fill={G.ink} />
  </svg>
);

export const SegmentedThumbHero: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ---- 时间轴 ----
  const FLOAT_IN = 0; // 控件浮入 0–18
  const CURSOR_IN = 20; // 光标滑入 20–44
  const CLICK = 48; // 按下
  const SLIDE = 52; // thumb 开始滑 52–60 (~8f)
  const SLIDE_END = 60;

  // 控件浮入：从下 160px 带阴影弹簧浮入
  const floatT = spring({ frame: frame - FLOAT_IN, fps, config: { damping: 14, stiffness: 120, mass: 0.9 } });
  const ctrlY = interpolate(floatT, [0, 1], [200, 0]);

  // 控件几何（特写尺寸）
  const CW = 1080; // 控件宽
  const CH = 220;
  const PAD = 16;
  const SEGW = (CW - PAD * 2) / 2;

  // 光标滑入：ease-out 从右下画外飘到 Computer 段上
  const curT = interpolate(frame, [CURSOR_IN, CURSOR_IN + 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const curX = interpolate(curT, [0, 1], [1780, 1210]);
  const curY = interpolate(curT, [0, 1], [1020, 620]);
  // 按下动作
  const press = interpolate(frame, [CLICK, CLICK + 3, CLICK + 7], [0, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // thumb 位移：~8f ease-out
  const thumbT = interpolate(frame, [SLIDE, SLIDE_END], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const thumbX = PAD + thumbT * SEGW;

  // 到位瞬间：Computer 图标弹出（过冲），Ask 图标收起
  const iconIn = spring({ frame: frame - SLIDE_END, fps, config: { damping: 10, stiffness: 220, mass: 0.6 } });
  const laptopScale = frame >= SLIDE_END ? iconIn : 0;
  const askScale = interpolate(frame, [SLIDE, SLIDE + 6], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });

  // 点击涟漪
  const rippleT = interpolate(frame, [CLICK, CLICK + 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  const labelStyle = (active: boolean): React.CSSProperties => ({
    fontFamily: FONT,
    fontWeight: 700,
    fontSize: 72,
    color: active ? G.ink : G.mid,
    transition: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 22,
    width: SEGW,
    height: CH - PAD * 2,
    position: 'relative',
    zIndex: 2,
  });

  const askActive = thumbT < 0.5;

  return (
    <AbsoluteFill style={{ background: G.bg, alignItems: 'center', justifyContent: 'center' }}>
      {/* 分段控件 */}
      <div
        style={{
          width: CW,
          height: CH,
          borderRadius: CH / 2,
          background: '#e4e4e2',
          border: `3px solid ${G.border}`,
          boxShadow: `0 ${24 - floatT * 12}px ${70 - floatT * 20}px rgba(0,0,0,0.22)`,
          transform: `translateY(${ctrlY}px)`,
          opacity: Math.min(1, floatT * 1.5),
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          padding: PAD,
          boxSizing: 'border-box',
        }}
      >
        {/* 白色 thumb */}
        <div
          style={{
            position: 'absolute',
            left: thumbX,
            top: PAD,
            width: SEGW,
            height: CH - PAD * 2,
            borderRadius: (CH - PAD * 2) / 2,
            background: '#fff',
            boxShadow: '0 6px 20px rgba(0,0,0,0.18)',
            zIndex: 1,
          }}
        />
        {/* 点击涟漪 */}
        {rippleT > 0 && rippleT < 1 && (
          <div
            style={{
              position: 'absolute',
              left: PAD + SEGW + SEGW / 2 - 130 * rippleT,
              top: CH / 2 - PAD - 130 * rippleT + (CH - PAD * 2) / 2 - (CH / 2 - PAD),
              width: 260 * rippleT,
              height: 260 * rippleT,
              borderRadius: '50%',
              border: `4px solid ${G.mid}`,
              opacity: 1 - rippleT,
              zIndex: 3,
            }}
          />
        )}
        {/* Ask 段 */}
        <div style={labelStyle(askActive)}>
          <span
            style={{
              display: 'inline-flex',
              transform: `scale(${askScale})`,
              width: askScale < 0.05 ? 0 : 78,
              overflow: 'visible',
            }}
          >
            <AskIcon size={78} />
          </span>
          Ask
        </div>
        {/* Computer 段 */}
        <div style={labelStyle(!askActive)}>
          <span
            style={{
              display: 'inline-flex',
              transform: `scale(${laptopScale})`,
              width: laptopScale < 0.05 ? 0 : 78,
              overflow: 'visible',
            }}
          >
            <SmileLaptop size={78} />
          </span>
          Computer
        </div>
      </div>
      <ArrowCursor x={curX} y={curY} press={press} />
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

