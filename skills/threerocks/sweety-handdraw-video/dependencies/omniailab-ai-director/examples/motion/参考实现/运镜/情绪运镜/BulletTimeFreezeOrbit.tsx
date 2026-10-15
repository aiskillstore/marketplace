// ---
// name: omniailab-motion-demo-bullet-time-freeze-orbit
// description: 子弹时间冻结环绕(bullet-time-freeze-orbit)——The Matrix bullet time。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 子弹时间冻结环绕(bullet-time-freeze-orbit)——The Matrix bullet time。
// 中央 900×560 面板内 5 根柱状图错峰生长(动画时钟 effFrame 驱动)。
// 关键帧:0–20 hold 读布景;20–45 柱子正常生长;45–105 时钟咬死(柱子完全静止),
// 相机 perspective(1600px) 下 rotateY 0→55°(45–72)→顶点悬停(72–82)→回 0(82–105),
// 同步 scale 1→1.12→1 + translateX 摆动增强绕行感;105–120 时钟恢复柱子长完;
// 118–128 数字标签浮现;128–150 全静止收尾。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const h = (n: number) => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

const PANEL_W = 900;
const PANEL_H = 560;
const BAR_COUNT = 5;

export const BulletTimeFreezeOrbit: React.FC = () => {
  const frame = useCurrentFrame();

  // ── 子弹时间时钟:0–45 正常走,45–105 冻结,105 起恢复 ──
  const effFrame =
    frame < 45 ? frame : frame < 105 ? 45 : 45 + (frame - 105);

  // ── 冻结区间的相机环绕(用真实 frame 驱动) ──
  const rotY =
    frame < 72
      ? interpolate(frame, [45, 72], [0, 55], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        })
      : frame < 82
        ? 55 // 顶点悬停 10f
        : interpolate(frame, [82, 105], [55, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: Easing.inOut(Easing.cubic),
          });
  const orbitT = rotY / 55; // 0→1→0,复用做 scale / translateX
  const scale = 1 + 0.12 * orbitT;
  const tx = -170 * Math.sin(orbitT * Math.PI * 0.5) - 60 * orbitT; // 绕行横摆
  const ty = -24 * orbitT;

  // ── 柱子:错峰生长,全部由 effFrame 驱动(冻结即静止) ──
  const chartW = PANEL_W - 140;
  const chartH = PANEL_H - 190;
  const barW = 92;
  const gap = (chartW - BAR_COUNT * barW) / (BAR_COUNT - 1);
  const bars = Array.from({ length: BAR_COUNT }).map((_, i) => {
    const full = chartH * (0.42 + h(i + 1) * 0.55); // 目标高度
    const start = 20 + i * 4;
    const end = 48 + i * 3; // 20–60f 区间内错峰
    const p = interpolate(effFrame, [start, end], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
    const value = Math.round((full / chartH) * 100); // 标签与柱高一致

    return { hNow: full * p, full, value, done: p >= 1 };
  });

  // ── 恢复段:数字标签浮现(118–128),之后全静止 ──
  const labelOp = interpolate(frame, [118, 128], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 冻结提示条:冻结期间显示 FREEZE 徽标,帮助读出手法
  const freezeOp = interpolate(frame, [45, 52, 98, 105], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: 'Helvetica, Arial, sans-serif',
      }}
    >
      <div style={{ position: 'absolute', top: 56, left: 72 }}>
        <TitleBlock text="BULLET TIME" size={44} />
      </div>

      {/* 冻结徽标 */}
      <div
        style={{
          position: 'absolute',
          top: 62,
          right: 84,
          opacity: freezeOp,
          background: G.ink,
          color: G.card,
          fontWeight: 800,
          fontSize: 30,
          letterSpacing: 4,
          padding: '12px 26px',
          borderRadius: 10,
        }}
      >
        FREEZE
      </div>

      {/* 3D 舞台 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          perspective: 1600,
        }}
      >
        <div
          style={{
            width: PANEL_W,
            height: PANEL_H,
            background: G.card,
            border: `2px solid ${G.border}`,
            borderRadius: 18,
            boxShadow: '0 16px 48px rgba(0,0,0,0.14)',
            boxSizing: 'border-box',
            padding: '44px 70px',
            transform: `translateX(${tx}px) translateY(${ty}px) rotateY(${rotY}deg) scale(${scale})`,
            transformStyle: 'preserve-3d',
          }}
        >
          {/* 面板标题条 */}
          <div
            style={{
              height: 20,
              width: 260,
              background: G.bar,
              borderRadius: 10,
              marginBottom: 14,
            }}
          />
          <div
            style={{
              height: 12,
              width: 170,
              background: G.line,
              borderRadius: 6,
              marginBottom: 30,
            }}
          />

          {/* 图表区:横向刻度线 + 柱子 */}
          <div style={{ position: 'relative', width: chartW, height: chartH }}>
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: 0,
                  right: 0,
                  top: (chartH / 4) * i,
                  height: 2,
                  background: G.line,
                }}
              />
            ))}
            {/* 基线 */}
            <div
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                bottom: 0,
                height: 3,
                background: G.mid,
              }}
            />
            {bars.map((b, i) => (
              <div key={i}>
                <div
                  style={{
                    position: 'absolute',
                    left: i * (barW + gap),
                    bottom: 3,
                    width: barW,
                    height: b.hNow,
                    background: i % 2 === 0 ? G.bar : G.mid,
                    borderRadius: '8px 8px 0 0',
                  }}
                />
                {/* 数字标签:恢复段浮现 */}
                <div
                  style={{
                    position: 'absolute',
                    left: i * (barW + gap),
                    bottom: 3 + b.full + 14 - 10 * (1 - labelOp),
                    width: barW,
                    textAlign: 'center',
                    fontWeight: 800,
                    fontSize: 28,
                    color: G.ink,
                    opacity: labelOp,
                  }}
                >
                  {b.value}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

