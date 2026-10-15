// ---
// name: omniailab-motion-demo-line-carry-transition
// description: 线条接力转场｜线条接力横移转场（Catch Me If You Can 图形接力）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 线条接力转场｜线条接力横移转场（Catch Me If You Can 图形接力）
// 世界宽 3840（A 左半 / B 右半）。0–24f 卡 A 底部 6px ink 进度条走满；
// 24–34f 进度条末端延伸成横线冲出卡右缘；34–94f 镜头整体左移 1920px
// （Easing.inOut(cubic)，60f），线与镜头同速延伸，笔头始终在画面偏右；
// 94–112f 线拐直角围出 560×330 卡框（一条 path 全程 evolve，dashoffset 生长）；
// 112–124f 框闭合后 B 卡内容淡入 12f。124–160f 真静止 36f ≥ 35f。
// 帧确定，无随机；笔头墨点 118f 起条件卸载（摘罩判例）。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, Card, TitleBlock } from '../../_fixtures/Fixtures';

// ---- 世界几何（一条折线：进度条 + 横线 + 直角 + 矩形框）----
// M 400,705 → 2600,705（进度 560 + 冲出 1640）→ 上 2600,375 → 右 3160,375
// → 下 3160,705 → 左回 2600,705 闭合。总长 2200+330+560+330+560 = 3980。
const PATH = 'M 400 705 L 2600 705 L 2600 375 L 3160 375 L 3160 705 L 2600 705';
const SEGS: Array<[number, number, number, number, number]> = [
  [400, 705, 2600, 705, 2200],
  [2600, 705, 2600, 375, 330],
  [2600, 375, 3160, 375, 560],
  [3160, 375, 3160, 705, 330],
  [3160, 705, 2600, 705, 560],
];
const TOTAL = 3980;

// 笔头坐标：按已画长度沿折线取点
const tipAt = (drawn: number): [number, number] => {
  let d = Math.max(0, Math.min(drawn, TOTAL));
  for (const [x1, y1, x2, y2, len] of SEGS) {
    if (d <= len) {
      const t = d / len;
      return [x1 + (x2 - x1) * t, y1 + (y2 - y1) * t];
    }
    d -= len;
  }
  return [2600, 705];
};

export const LineCarryTransition: React.FC = () => {
  const frame = useCurrentFrame();

  // 镜头：34–94f 左移 1920px，inOut cubic
  const cam = interpolate(frame, [34, 94], [0, 1920], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 已画长度：三段接力（进度条 → 冲出 → 与镜头同速 → 收框）
  let drawn: number;
  if (frame < 24) {
    drawn = interpolate(frame, [0, 24], [0, 560], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  } else if (frame < 34) {
    drawn = interpolate(frame, [24, 34], [560, 1100], {
      extrapolateRight: 'clamp',
    });
  } else if (frame < 94) {
    drawn = 1100 + cam; // 与镜头同速延伸，笔头稳在画面偏右
  } else {
    drawn = interpolate(frame, [94, 112], [3020, TOTAL], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }

  // B 卡内容：框闭合(112f)后淡入 12f
  const contentOpacity = interpolate(frame, [112, 124], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 笔头墨点：全程随笔走，112–118f 线性消散，118f 起条件卸载
  const tipMounted = frame < 118;
  const tipOpacity = interpolate(frame, [112, 118], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const [tx, ty] = tipAt(drawn);

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 世界容器：3840 宽，整体横移 = 镜头跟线走 */}
      <div
        style={{
          position: 'absolute',
          width: 3840,
          height: 1080,
          transform: `translateX(${-cam}px)`,
        }}
      >
        {/* B 半世界底色略浅，卖出"新世界" */}
        <div style={{ position: 'absolute', left: 1920, top: 0, width: 1920, height: 1080, background: G.panel }} />

        {/* 场景 A：标题 + 卡 + 进度条轨道（ink 填充即 path 本体） */}
        <div style={{ position: 'absolute', left: 400, top: 250 }}>
          <TitleBlock text="Scene A" size={56} />
        </div>
        <Card w={560} h={330} seed={2} style={{ position: 'absolute', left: 400, top: 350 }} />
        <div style={{ position: 'absolute', left: 400, top: 702, width: 560, height: 6, borderRadius: 3, background: G.line }} />

        {/* 一条线全程 evolve：dasharray/dashoffset 生长 */}
        <svg width={3840} height={1080} style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          <path
            d={PATH}
            fill="none"
            stroke={G.ink}
            strokeWidth={6}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={TOTAL}
            strokeDashoffset={TOTAL - drawn}
          />
          {tipMounted && <circle cx={tx} cy={ty} r={11} fill={G.ink} opacity={tipOpacity} />}
        </svg>

        {/* 场景 B：框(2600,375–3160,705)由线画成，内容淡入 */}
        <div
          style={{
            position: 'absolute',
            left: 2600,
            top: 375,
            width: 560,
            height: 330,
            boxSizing: 'border-box',
            padding: 26,
            display: 'flex',
            flexDirection: 'column',
            gap: 14,
            opacity: contentOpacity,
          }}
        >
          <div style={{ height: 18, width: '58%', background: G.bar, borderRadius: 9 }} />
          <div style={{ height: 11, width: '86%', background: G.line, borderRadius: 5 }} />
          <div style={{ height: 11, width: '72%', background: G.line, borderRadius: 5 }} />
          <div style={{ height: 11, width: '64%', background: G.line, borderRadius: 5 }} />
          <div style={{ marginTop: 'auto', display: 'flex', gap: 10, alignItems: 'center' }}>
            <div style={{ width: 30, height: 30, borderRadius: 15, background: G.mid }} />
            <div style={{ height: 11, width: 90, background: G.line, borderRadius: 5 }} />
          </div>
        </div>
        <div style={{ position: 'absolute', left: 2600, top: 275, opacity: contentOpacity }}>
          <TitleBlock text="Scene B" size={56} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

