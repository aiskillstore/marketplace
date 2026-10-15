// ---
// name: omniailab-motion-demo-before-after-slider-scrub
// description: 前后对比拉杆 —— 前后对比拉杆
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 前后对比拉杆 —— 前后对比拉杆
// FakeDashboard 两版叠放：before = 低对比灰蒙版（"处理前"），after = 正常清晰版。
// 竖分割杆带圆手柄：从左端 8% 快甩到 70%（overshoot 至 76% 回弹），
// 再慢速回扫到 40% 停住。杆经过处 after 揭出（clip-path inset 跟随杆 x）。
// 先快甩后慢扫速度对比是节奏关键。f=110 后全静止（40f）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard } from '../../_fixtures/Fixtures';

const CL = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// 时间轴（杆位置以画面宽度百分比表示）
const T0 = 14; // 前 14f 初始静置，杆停在 8%
const FLING = 26; // 快甩：14→26（12f 冲到 76%）
const BOUNCE = 38; // 回弹：26→38 落到 70%
const HOLD = 56; // 停顿看清
const SCRUB = 104; // 慢扫：56→104（48f 回到 40%）——速度约为快甩的 1/5

const posAt = (f: number): number => {
  if (f < FLING)
    return interpolate(f, [T0, FLING], [8, 76], { easing: Easing.out(Easing.cubic), ...CL });
  if (f < BOUNCE)
    return interpolate(f, [FLING, BOUNCE], [76, 70], { easing: Easing.inOut(Easing.cubic), ...CL });
  if (f < HOLD) return 70;
  return interpolate(f, [HOLD, SCRUB], [70, 40], { easing: Easing.inOut(Easing.quad), ...CL });
};

export const BeforeAfterSliderScrub: React.FC = () => {
  const frame = useCurrentFrame();
  const p = posAt(frame); // 杆位置 %
  const x = (p / 100) * 1920;

  // 手柄挤压：速度差分驱动（快甩期手柄微拉伸，静止归 1）
  const v = Math.abs(posAt(frame) - posAt(frame - 1)); // %/frame
  const squish = 1 + Math.min(v / 8, 1) * 0.18;

  return (
    <div style={{ width: 1920, height: 1080, position: 'relative', overflow: 'hidden', background: G.bg }}>
      {/* before：低对比灰蒙版模拟"处理前" */}
      <div style={{ position: 'absolute', inset: 0, filter: 'contrast(0.55) brightness(1.06) grayscale(1)' }}>
        <FakeDashboard variant="A" />
      </div>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(160,160,158,0.35)' }} />

      {/* after：正常清晰版，杆左侧揭出 */}
      <div style={{ position: 'absolute', inset: 0, clipPath: `inset(0 ${1920 - x}px 0 0)` }}>
        <FakeDashboard variant="A" />
      </div>

      {/* 分割杆 + 圆手柄 */}
      <div
        style={{
          position: 'absolute',
          left: x - 3,
          top: 0,
          width: 6,
          height: 1080,
          background: '#ffffff',
          boxShadow: '0 0 14px rgba(0,0,0,0.35)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: x - 44,
          top: 540 - 44,
          width: 88,
          height: 88,
          borderRadius: 44,
          background: '#ffffff',
          border: `3px solid ${G.border}`,
          boxShadow: '0 6px 24px rgba(0,0,0,0.3)',
          transform: `scaleX(${squish})`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
          boxSizing: 'border-box',
        }}
      >
        {/* 左右箭头示意（灰阶三角） */}
        <div style={{ width: 0, height: 0, borderTop: '10px solid transparent', borderBottom: '10px solid transparent', borderRight: `14px solid ${G.mid}` }} />
        <div style={{ width: 0, height: 0, borderTop: '10px solid transparent', borderBottom: '10px solid transparent', borderLeft: `14px solid ${G.mid}` }} />
      </div>

      {/* 角标：BEFORE / AFTER 灰块标签 */}
      <div style={{ position: 'absolute', left: 260, top: 100, padding: '10px 22px', borderRadius: 10, background: 'rgba(47,47,47,0.85)', display: 'flex', gap: 8 }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} style={{ width: 16, height: 20, borderRadius: 4, background: '#e6e6e4' }} />
        ))}
      </div>
      <div style={{ position: 'absolute', right: 60, top: 100, padding: '10px 22px', borderRadius: 10, background: 'rgba(240,240,238,0.9)', border: `2px solid ${G.border}`, display: 'flex', gap: 8 }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} style={{ width: 16, height: 20, borderRadius: 4, background: G.ink }} />
        ))}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

