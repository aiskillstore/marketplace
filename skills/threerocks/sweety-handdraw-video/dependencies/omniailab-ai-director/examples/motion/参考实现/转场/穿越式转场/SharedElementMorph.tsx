// ---
// name: omniailab-motion-demo-shared-element-morph
// description: 参考实现——参考实现/转场/穿越式转场/SharedElementMorph.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, Card, G } from '../../_fixtures/Fixtures';

// shared-element-morph〔转场〕：全屏特写面板收缩、位移、长出圆角，
// 严丝合缝飞落进 dashboard 网格里它所属的卡片槽位，落座带 3% 过冲。
// 观众感觉是同一个物体被镜头送回原位（FLIP 共享元素转场）。
//
// 目标槽位 = FakeDashboard A 中列第二行那格（seed 5），按 fixtures 布局精确推算：
//   侧栏 220 + 网格 padding 36 → 列宽 (1920-220-72-56)/3 = 524
//   头部 72 + padding 36     → 行高 (1008-72-28)/2   = 454
//   中列 x = 220+36+524+28 = 808；第二行 y = 72+36+454+28 = 590
const SLOT = { x: 808, y: 590, w: 524, h: 454, r: 14, seed: 5 };
const FULL = { x: 0, y: 0, w: 1920, h: 1080, r: 0 };

// 节拍：0–35 全屏特写 hold ｜ 35–60 morph 25f（bezier 0.4,0,0.2,1 → 1.03）
//       60–70 过冲回弹落座 ｜ 70–130 静止收尾
const MORPH_START = 35;
const MORPH_END = 60;
const SETTLE_END = 70;

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const SharedElementMorph: React.FC = () => {
  const frame = useCurrentFrame();

  // 位置/尺寸/圆角共用同一条进度曲线：25f 冲到 1.03，再 10f 弹回 1
  const drive = interpolate(frame, [MORPH_START, MORPH_END], [0, 1.03], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });
  const settle = interpolate(frame, [MORPH_END, SETTLE_END], [1.03, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const p = frame <= MORPH_END ? drive : settle;

  const x = lerp(FULL.x, SLOT.x, p);
  const y = lerp(FULL.y, SLOT.y, p);
  const w = lerp(FULL.w, SLOT.w, p);
  const h = lerp(FULL.h, SLOT.h, p);
  const r = lerp(FULL.r, SLOT.r, p);

  // 内容是同一张卡：按目标尺寸渲染，等比放大铺满全屏（全屏 = 这张卡的特写），
  // 收缩过程中内容随容器一起缩小，强化"同一个物体"的感知
  const contentScale = w / SLOT.w;

  // 投影随尺寸缩小：悬空时大而深，落座后收敛到 fixtures 卡片原生投影量级
  const ps = Math.min(Math.max(p, 0), 1);
  const shadowY = lerp(36, 2, ps);
  const shadowBlur = lerp(110, 8, ps);
  const shadowAlpha = lerp(0.32, 0.06, ps);

  // 背景 dashboard 先 0.9 透明度待命，落座瞬间提到 1
  const bgOpacity = interpolate(frame, [MORPH_END - 2, MORPH_END + 3], [0.9, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      <div style={{ opacity: bgOpacity }}>
        <FakeDashboard variant="A" />
      </div>
      {/* 共享元素：全屏特写 → 精确飞落进槽位 */}
      <div
        style={{
          position: 'absolute',
          left: x,
          top: y,
          width: w,
          height: h,
          borderRadius: r,
          overflow: 'hidden',
          background: G.card,
          boxShadow: `0 ${shadowY}px ${shadowBlur}px rgba(0,0,0,${shadowAlpha})`,
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            transform: `scale(${contentScale})`,
            transformOrigin: 'top left',
          }}
        >
          <Card
            w={SLOT.w}
            h={SLOT.h}
            seed={SLOT.seed}
            style={{ boxShadow: 'none', borderRadius: r / Math.max(contentScale, 0.0001) }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

