// ---
// name: omniailab-motion-demo-crane-rise-reveal
// description: 升降臂拉升揭示（升降臂拉升揭示）——crane shot。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 升降臂拉升揭示（升降臂拉升揭示）——crane shot。
// 世界 = FakeDashboard(B) 五行列表。相机 transform-origin 左上，联动公式：
// translate = 屏幕中心 - 对准点*scale（对准点始终落在屏幕中心）。
// 帧 0–20 hold 在底行特写（scale 3.2，对准第 5 行图标+长条）；
// 帧 20–120 scale 3.2→1 + 对准点 (520,958)→(960,540)，Easing.out(quad) 减速升起；
// 视野上缘每越过一行顶边，该行深色脉冲一拍（4f 起 18f 落）读作"涌入"；帧 120–150 满幅真静止。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard } from '../../_fixtures/Fixtures';

const HOLD = 20; // 开场特写 hold
const MOVE_END = 120; // 运镜结束，此后真静止
const ease = Easing.out(Easing.quad);

// FakeDashboard(B) 行几何：侧栏 220 + 内容 padding 36，header 72，5 行 gap 20
const ROW_LEFT = 220 + 36;
const ROW_W = 1920 - ROW_LEFT - 36;
const ROW_H = (1080 - 72 - 72 - 4 * 20) / 5; // 171.2
const rowTop = (i: number) => 72 + 36 + i * (ROW_H + 20);

const F0 = { x: 520, y: rowTop(4) + ROW_H / 2 }; // 起点对准最底行（图标+标题条区域）
const F1 = { x: 960, y: 540 }; // 终点对准整页中心
const S0 = 3.2;

const camAt = (frame: number) => {
  const p = Math.min(1, Math.max(0, (frame - HOLD) / (MOVE_END - HOLD)));
  const e = ease(p);
  const s = S0 + (1 - S0) * e;
  const fx = F0.x + (F1.x - F0.x) * e;
  const fy = F0.y + (F1.y - F0.y) * e;
  return { s, tx: 960 - fx * s, ty: 540 - fy * s, visTop: fy - 540 / s };
};

// 每行脉冲触发帧：视野上缘首次越过该行顶边（底行开场已在画内 → 运动一起步即触发）
const triggers = Array.from({ length: 5 }, (_, i) => {
  for (let f = HOLD; f <= MOVE_END; f++) {
    if (camAt(f).visTop <= rowTop(i) + 1) return f;
  }
  return MOVE_END;
});

export const CraneRiseReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { s, tx, ty } = camAt(frame);

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <div
        style={{
          position: 'absolute',
          width: 1920,
          height: 1080,
          transformOrigin: '0 0',
          transform: `translate(${tx}px, ${ty}px) scale(${s})`,
        }}
      >
        <FakeDashboard variant="B" />
        {triggers.map((t, i) => {
          const op = interpolate(frame, [t, t + 4, t + 22], [0, 0.22, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          if (op <= 0.001) return null;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: ROW_LEFT,
                top: rowTop(i),
                width: ROW_W,
                height: ROW_H,
                borderRadius: 14,
                background: G.ink,
                opacity: op,
              }}
            />
          );
        })}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

