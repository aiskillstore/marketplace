// ---
// name: omniailab-motion-demo-barn-door-split
// description: 对开门裂幕（barn-door-split-reveal）——剪映"开门式"转场。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 对开门裂幕（barn-door-split-reveal）——剪映"开门式"转场。
// FakeDashboard A 从画面正中垂直裂成左右两半：两个 960×1080 overflow:hidden
// 容器各装一份完整 A（右半内层 translateX(-960) 对位拼合），同时向外加速滑
// 出画外，露出底层 FakeDashboard B 从 scale 1.06 轻推到 1.0 迎上来。
// 裂缝各自内边缘 2px G.ink 亮线 + 8px 投影强调"撕开"。
// 关键帧：0–30 静止展示 A（18–22 / 25–29 中缝细线两次闪现预告裂点）→
// 30–50 两半各 translateX ∓980（Easing.in cubic 加速滑出）→
// 30–55 底层 B scale 1.06→1.0（out cubic）→ 55–130 全静止（75f）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard, TitleBlock } from '../../_fixtures/Fixtures';

export const BarnDoorSplit: React.FC = () => {
  const frame = useCurrentFrame();

  // 两半外滑位移：30–50f，0 → 980px，加速离场
  const slide = interpolate(frame, [30, 50], [0, 980], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });

  // 底层 B：30–55f 从 1.06 轻推到 1.0 迎上来
  const bScale = interpolate(frame, [30, 55], [1.06, 1.0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // 裂前预告：中缝细线两次闪现（帧确定的开关，无随机）
  const crackFlash =
    (frame >= 18 && frame < 22) || (frame >= 25 && frame < 29);
  // 裂开后内边缘亮线 + 阴影常驻（随门一起滑出画外）
  const tornEdge = frame >= 30;

  const edgeLine = (side: 'left' | 'right'): React.CSSProperties => ({
    position: 'absolute',
    top: 0,
    [side]: 0,
    width: 3,
    height: 1080,
    background: G.ink,
    boxShadow:
      side === 'right'
        ? '-8px 0 14px rgba(0,0,0,0.4)'
        : '8px 0 14px rgba(0,0,0,0.4)',
  });

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* 底层 FakeDashboard B：scale 1.06 → 1.0 迎上来 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 1920,
          height: 1080,
          transform: `scale(${bScale})`,
          transformOrigin: '50% 50%',
        }}
      >
        <FakeDashboard variant="B" />
      </div>

      {/* 左门：960×1080 视口，装完整 A 的左半 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 960,
          height: 1080,
          overflow: 'hidden',
          transform: `translateX(${-slide}px)`,
        }}
      >
        <div style={{ position: 'absolute', left: 0, top: 0, width: 1920, height: 1080 }}>
          <FakeDashboard variant="A" />
        </div>
        {tornEdge && <div style={edgeLine('right')} />}
      </div>

      {/* 右门：960×1080 视口，内层 translateX(-960) 对位拼合 */}
      <div
        style={{
          position: 'absolute',
          left: 960,
          top: 0,
          width: 960,
          height: 1080,
          overflow: 'hidden',
          transform: `translateX(${slide}px)`,
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: 1920,
            height: 1080,
            transform: 'translateX(-960px)',
          }}
        >
          <FakeDashboard variant="A" />
        </div>
        {tornEdge && <div style={edgeLine('left')} />}
      </div>

      {/* 裂点预告：中缝 2px 细线闪现两次 */}
      {crackFlash && (
        <div
          style={{
            position: 'absolute',
            left: 959,
            top: 0,
            width: 2,
            height: 1080,
            background: G.ink,
          }}
        />
      )}

      <div style={{ position: 'absolute', left: 120, top: 96 }}>
        <TitleBlock text="BARN DOOR SPLIT" size={54} />
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

