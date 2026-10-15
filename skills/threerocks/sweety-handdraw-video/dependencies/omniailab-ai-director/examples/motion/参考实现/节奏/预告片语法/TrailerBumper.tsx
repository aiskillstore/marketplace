// ---
// name: omniailab-motion-demo-trailer-bumper
// description: trailer-bumper｜前置速剪预告
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// trailer-bumper｜前置速剪预告
// 结构即全部：三连 9f 速剪（A 整页 / B 整页 / A 2.2x 怼脸特写）→ 6f 纯黑喘息
// → 正式开场大标题淡入+微升 16f 定格。每个速剪镜头内部带 1→1.04 轻推近。
// 收尾真静止：49f 后所有动画结束，静止 91f（>40f）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard } from '../../_fixtures/Fixtures';

// 时间轴（帧）
const CUT_1 = 0;   // 镜头1：variant A 整页
const CUT_2 = 9;   // 镜头2：variant B 整页
const CUT_3 = 18;  // 镜头3：variant A 2.2x 怼脸特写
const BLACK = 27;  // 纯黑静默
const TITLE = 33;  // 正式开场
const TITLE_IN = 16; // 标题淡入+微升时长

// 速剪镜头内部轻推近：镜头内 local 0→9f，scale 1→1.04（线性，活镜头感）
const push = (frame: number, start: number) =>
  interpolate(frame, [start, start + 9], [1, 1.04], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const TrailerBumper: React.FC = () => {
  const frame = useCurrentFrame();

  // —— 段落 1–3：三连速剪 ——
  if (frame < BLACK) {
    let inner: React.ReactNode;
    if (frame < CUT_2) {
      // 镜头1：A 整页 + 轻推近
      inner = (
        <div style={{ width: 1920, height: 1080, transform: `scale(${push(frame, CUT_1)})`, transformOrigin: '50% 50%' }}>
          <FakeDashboard variant="A" />
        </div>
      );
    } else if (frame < CUT_3) {
      // 镜头2：B 整页 + 轻推近
      inner = (
        <div style={{ width: 1920, height: 1080, transform: `scale(${push(frame, CUT_2)})`, transformOrigin: '50% 50%' }}>
          <FakeDashboard variant="B" />
        </div>
      );
    } else {
      // 镜头3：A 的 2.2x 放大裁切怼脸特写（对准中列卡片），叠加同样的轻推近
      const s = 2.2 * push(frame, CUT_3);
      inner = (
        <div style={{ width: 1920, height: 1080, transform: `scale(${s})`, transformOrigin: '58% 40%' }}>
          <FakeDashboard variant="A" />
        </div>
      );
    }
    return (
      <div style={{ width: 1920, height: 1080, overflow: 'hidden', background: G.bg }}>
        {inner}
      </div>
    );
  }

  // —— 段落 4：纯黑静默 6f，必须纯黑无物 ——
  if (frame < TITLE) {
    return <div style={{ width: 1920, height: 1080, background: '#000000' }} />;
  }

  // —— 段落 5：正式开场——浅底大标题淡入+微升 16f 后定格 ——
  const opacity = interpolate(frame, [TITLE, TITLE + TITLE_IN], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const rise = interpolate(frame, [TITLE, TITLE + TITLE_IN], [44, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${rise}px)`,
          fontFamily: 'Helvetica, Arial, sans-serif',
          fontWeight: 800,
          fontSize: 168,
          color: G.ink,
          letterSpacing: -2,
          textAlign: 'center',
        }}
      >
        THE LAUNCH
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

