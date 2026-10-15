// ---
// name: omniailab-motion-demo-beat-cut-accelerando
// description: 参考实现——参考实现/节奏/硬切节拍/BeatCutAccelerando.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

// beat-cut-accelerando：六个不同构图按 16→12→8→6→4 帧递减间隔全屏硬切，
// 加速逼近，最后一切戛然定格回主画面并 1→1.06 慢推收住。
// 真硬切：frame 落在哪个区间就渲染哪个视图，无任何过渡。

// 一个视图 = FakeDashboard 变体 + 缩放 + 对焦点（画面上要被推到屏幕中心的点）
type View = { variant: 'A' | 'B'; scale: number; cx: number; cy: number };

const VIEWS: View[] = [
  { variant: 'A', scale: 1, cx: 960, cy: 540 },    // v0 全景（建立）
  { variant: 'A', scale: 1.8, cx: 1070, cy: 576 }, // v1 卡片区
  { variant: 'A', scale: 2.6, cx: 600, cy: 340 },  // v2 单卡特写
  { variant: 'B', scale: 1, cx: 960, cy: 540 },    // v3 列表页全景
  { variant: 'B', scale: 1.9, cx: 1070, cy: 500 }, // v4 列表行区
  { variant: 'B', scale: 2.8, cx: 1070, cy: 290 }, // v5 单行特写
];

// 每段起始帧：建立 49f，然后间隔 16→12→8→6→4，末段（回主画面）hold 35f
// 0–48 v0 | 49–64 v1 | 65–76 v2 | 77–84 v3 | 85–90 v4 | 91–94 v5 | 95–129 定格
const CUTS = [0, 49, 65, 77, 85, 91, 95];
const FINAL = 95; // 最后一切：戛然定格回主画面

const ViewShot: React.FC<{ view: View; extraScale?: number }> = ({ view, extraScale = 1 }) => {
  const s = view.scale * extraScale;
  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        transformOrigin: `${view.cx}px ${view.cy}px`,
        transform: `translate(${960 - view.cx}px, ${540 - view.cy}px) scale(${s})`,
      }}
    >
      <FakeDashboard variant={view.variant} />
    </div>
  );
};

export const BeatCutAccelerando: React.FC = () => {
  const frame = useCurrentFrame();

  // 当前落在哪个区间（末段 = 主画面 v0）
  let seg = 0;
  for (let i = 0; i < CUTS.length; i++) {
    if (frame >= CUTS[i]) seg = i;
  }
  const isFinal = seg === CUTS.length - 1;
  const view = isFinal ? VIEWS[0] : VIEWS[seg];

  // 末段慢推：scale 1 → 1.06，ease-out，推 22f 后静止（结尾静止 ≥15f）
  const push = isFinal
    ? interpolate(frame, [FINAL, FINAL + 20], [1, 1.06], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
        easing: Easing.out(Easing.cubic),
      })
    : 1;

  // 每次硬切的 1f 亮度跳变（约 +5%）模拟快门
  const isCutFrame = CUTS.some((c, i) => i > 0 && frame === c);
  const flash = isCutFrame ? 1.05 : 1;

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, filter: `brightness(${flash})` }}>
        <ViewShot view={view} extraScale={push} />
      </div>
      {/* 切帧再叠一层极薄白闪，保证肉眼可感 */}
      {isCutFrame && (
        <AbsoluteFill style={{ background: '#ffffff', opacity: 0.06 }} />
      )}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

