// ---
// name: omniailab-motion-demo-drone-dive-landing
// description: 参考实现——参考实现/运镜/空间分解运镜/DroneDiveLanding.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { CameraMotionBlur } from '@remotion/motion-blur';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

// drone-dive-landing：上帝视角俯视整页平躺的 dashboard（近垂直俯角、缩小居中），
// 相机猛扎下来——俯角抬平、页面放大立正，最后一段气垫式长尾减速，
// 稳稳停在 hero 卡正前方特写。FPV 无人机俯冲降落的运镜翻译。
//
// hero 卡 = FakeDashboard A 网格左上格：
// 侧栏 220 + padding 36 = x 256 起，列宽 (1628-56)/3 = 524；
// 顶栏 72 + padding 36 = y 108 起，行高 (936-28)/2 = 454。
// 卡中心 (256+262, 108+227) = (518, 335)，全程 transform-origin 钉在这里。
const HERO = { cx: 518, cy: 335 };
const DIVE_START = 20; // 开头 hold 20f：上帝视角建立
const DIVE_END = 45;   // 主俯冲段 25f，ease-in(cubic) 越冲越快
const LAND_END = 65;   // 气垫段 20f，ease-out(quint) 长尾减速，之后真静止
const DIVE_SHARE = 0.82; // 俯冲段吃掉 82% 行程，剩 18% 留给气垫

const Scene: React.FC = () => {
  const frame = useCurrentFrame();

  // 两段速度曲线拼一条行程 p∈[0,1]：先猛加速扎下，切换帧速度骤降 = 气垫顶住的体感
  const pDive = interpolate(frame, [DIVE_START, DIVE_END], [0, DIVE_SHARE], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const pLand = interpolate(frame, [DIVE_END, LAND_END], [0, 1 - DIVE_SHARE], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.poly(5)),
  });
  const p = frame < DIVE_END ? pDive : DIVE_SHARE + pLand;

  // 三轴联动，全部由同一条 p 驱动（同一台"相机"的一次连续机动）
  const rotX = interpolate(p, [0, 1], [72, 0]);      // 俯角抬平
  const scale = interpolate(p, [0, 1], [0.42, 1.35]); // 缩小全景 → hero 特写
  // 平移：起点让整页平躺在画面中央偏上；终点 hero 卡中心正对画面中心
  const tx = interpolate(p, [0, 1], [256, 960 - HERO.cx]);
  const ty = interpolate(p, [0, 1], [150, 540 - HERO.cy]);

  // 地面投影：俯视时页面悬空、下方拖一团椭圆软影；落地立正后影子收干
  const shadowOp = interpolate(p, [0, 0.8], [0.32, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shadowW = 1300 * (0.6 + scale * 0.4);

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 地面软影（高度感线索） */}
      <div
        style={{
          position: 'absolute',
          left: 960 - shadowW / 2,
          top: 620,
          width: shadowW,
          height: 320,
          borderRadius: '50%',
          background: 'radial-gradient(ellipse at center, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 68%)',
          opacity: shadowOp,
          filter: 'blur(18px)',
        }}
      />
      {/* 相机 = perspective 容器；页面绕 hero 卡中心做 rotateX + scale + translate */}
      <AbsoluteFill style={{ perspective: 1400 }}>
        <div
          style={{
            position: 'absolute',
            width: 1920,
            height: 1080,
            transformOrigin: `${HERO.cx}px ${HERO.cy}px`,
            transform: `translate(${tx}px, ${ty}px) rotateX(${rotX}deg) scale(${scale})`,
            boxShadow: `0 ${6 + (1 - p) * 30}px ${20 + (1 - p) * 60}px rgba(0,0,0,${0.1 + (1 - p) * 0.14})`,
            borderRadius: 6,
            overflow: 'hidden',
          }}
        >
          <FakeDashboard variant="A" />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const DroneDiveLanding: React.FC = () => (
  <CameraMotionBlur shutterAngle={220} samples={9}>
    <Scene />
  </CameraMotionBlur>
);
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

