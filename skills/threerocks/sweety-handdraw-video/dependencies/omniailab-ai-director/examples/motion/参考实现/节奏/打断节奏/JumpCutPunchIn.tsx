// ---
// name: omniailab-motion-demo-jump-cut-punch-in
// description: 三级跳切推近（jump-cut-punch-in）——节奏剪辑｜戈达尔跳切/纪录片 punch-in。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 三级跳切推近（jump-cut-punch-in）——节奏剪辑｜戈达尔跳切/纪录片 punch-in。
// FakeDashboard A 固定构图，transform-origin 钉在第 2 行中间卡中心
// (1070px, 817px)。三次无补间硬切逐级放大：刻意零 interpolate，
// 切换帧一帧到位。每次跳切帧叠 2f 整画面 brightness 0.92 加深脉冲当 tick。
// 关键帧：0–34 scale 1.0 hold → 帧 35 直跳 1.6（35–36 加深脉冲）→ hold →
// 帧 70 直跳 2.6（70–71 加深脉冲）→ 72–134 全静止（63f ≥45f）。
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { G, FakeDashboard, TitleBlock } from '../../_fixtures/Fixtures';

// 目标卡片（3×2 网格第 2 行中间卡）几何：
// 侧栏 220 + 内边距 36；卡宽 (1920-220-72-56)/3 = 524.67，卡高 (1080-72-72-28)/2 = 454
const CARD_L = 220 + 36 + 524.67 + 28; // ≈808.67
const CARD_T = 72 + 36 + 454 + 28; // 590
const CARD_W = 524.67;
const CARD_H = 454;
const ORIGIN_X = CARD_L + CARD_W / 2; // ≈1071
const ORIGIN_Y = CARD_T + CARD_H / 2; // 817

// 三级硬切：零补间，帧 35 / 帧 70 一帧到位
const scaleAt = (f: number): number => (f < 35 ? 1.0 : f < 70 ? 1.6 : 2.6);

// 跳切帧 2f 加深脉冲（整画面 brightness 0.92）
const pulseAt = (f: number): number =>
  (f >= 35 && f <= 36) || (f >= 70 && f <= 71) ? 0.92 : 1;

export const JumpCutPunchIn: React.FC = () => {
  const frame = useCurrentFrame();
  const s = scaleAt(frame);
  const b = pulseAt(frame);

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        position: 'relative',
        overflow: 'hidden',
        filter: `brightness(${b})`,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${s})`,
          transformOrigin: `${ORIGIN_X}px ${ORIGIN_Y}px`,
        }}
      >
        <FakeDashboard variant="A" />
        {/* 目标卡片标记：随构图一起缩放，提示 punch-in 落点 */}
        <div
          style={{
            position: 'absolute',
            left: CARD_L - 10,
            top: CARD_T - 10,
            width: CARD_W + 20,
            height: CARD_H + 20,
            border: `3px dashed ${G.mid}`,
            borderRadius: 20,
            boxSizing: 'border-box',
          }}
        />
      </div>
      {/* 标签不随缩放，固定左上角 */}
      <div style={{ position: 'absolute', left: 260, top: 20 }}>
        <TitleBlock text="JUMP CUT PUNCH-IN" size={54} />
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

