// ---
// name: omniailab-motion-demo-glitch-displace
// description: glitch-displace｜噪声置换撕裂
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// glitch-displace｜噪声置换撕裂
// FakeDashboard A 播到 45f，45–62f 撕裂转场：页面切 16 条水平条带
// （外层 overflow hidden + 内层整页反向 translateY 对位），每条 translateX
// 由 h(条号*31+f*7) 驱动 ±70px 抖动，幅度包络 0→峰值→0（起势 out-cubic、
// 消散线性，冲击判例）。同时叠 2 份整页明暗错位重影（+12px 暗 / -12px 亮反相，
// opacity ≤0.35，灰阶版代替 RGB 分离）。58f 抖动衰减中硬切 variant="B"，
// 再抖 4f 至 62f 归位。62f 起摘罩直出 B（条带/重影全部条件卸载），
// 62–135f 真静止 73f ≥ 40f。帧确定：h() 伪随机，无 Math.random。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

const STRIPS = 16;
const H = 1080;
const STRIP_H = H / STRIPS; // 67.5
const AMP = 70; // 峰值条带错位（spec 备选加码值，QA 要一眼看到撕裂）

// 库内标准伪随机
const h = (n: number) => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

export const GlitchDisplace: React.FC = () => {
  const frame = useCurrentFrame();

  const tearing = frame >= 45 && frame < 62;
  const variant: 'A' | 'B' = frame >= 58 ? 'B' : 'A';

  if (!tearing) {
    // 45f 前 A 静置；62f 起 B 摘罩真静止（无 transform / filter / 重影）
    return (
      <AbsoluteFill style={{ background: G.bg }}>
        <FakeDashboard variant={variant} />
      </AbsoluteFill>
    );
  }

  // 幅度包络：45–48f out-cubic 冲起 → 平台 → 56–62f 线性消散（帧驱动，确定性）
  const rise = interpolate(frame, [45, 48], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const decay = interpolate(frame, [56, 62], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const env = Math.min(rise, decay);

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 底垫一份完整页，防条带间横移露底色缝 */}
      <AbsoluteFill>
        <FakeDashboard variant={variant} />
      </AbsoluteFill>

      {/* 明暗错位重影（灰阶版 RGB 分离）：+12px 压暗 / -12px 反相提亮 */}
      <AbsoluteFill
        style={{
          transform: 'translateX(12px)',
          opacity: 0.35 * env,
          filter: 'brightness(0.45)',
        }}
      >
        <FakeDashboard variant={variant} />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          transform: 'translateX(-12px)',
          opacity: 0.28 * env,
          filter: 'invert(1)',
        }}
      >
        <FakeDashboard variant={variant} />
      </AbsoluteFill>

      {/* 16 条水平条带：外层裁切，内层整页反向 translateY 对位 + 逐帧横向抖动 */}
      {Array.from({ length: STRIPS }).map((_, i) => {
        const dx = (h(i * 31 + frame * 7) * 2 - 1) * AMP * env;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: i * STRIP_H,
              left: 0,
              width: 1920,
              height: STRIP_H,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: 1920,
                height: H,
                transform: `translate(${dx.toFixed(2)}px, ${-i * STRIP_H}px)`,
              }}
            >
              <FakeDashboard variant={variant} />
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

