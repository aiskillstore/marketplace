// ---
// name: omniailab-motion-demo-riso-misregistration-hit
// description: 套印错位冲击帧（riso-misregistration-hit）——标题撞停瞬间裂成两份单色"印版"
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 套印错位冲击帧（riso-misregistration-hit）——标题撞停瞬间裂成两份单色"印版"
// （浅灰琥珀版 G.mid + 深墨版 G.ink，mix-blend-mode: multiply 叠加），像 riso 印刷
// 没对准版；两版反向错位（x 为主 y 少量）做衰减震荡 offset = A*cos(ωt)*exp(-t/τ)
// 抖两下，帧 72 啪地硬切回单一正体（套准合一），带 4f scale 1.03→1 脉冲收束。
// 结构：0–19f 空场 hold（只有底部装饰线）；20–28f 标题从右画外 Easing.in(cubic)
// 撞入屏心（帧 28 命中）；28–71f 双版错位震荡；72–75f 套准脉冲；76–119f 真静止 44f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const HIT = 28; // 撞停命中帧
const SNAP = 72; // 套准合一帧
const AX = 16; // 单版 x 错位振幅（两版反向 → 总分离 ~32px，肉眼明显）
const AY = 7; // 单版 y 错位振幅（少量，更像没对准版）
const OMEGA = (2 * Math.PI) / 18; // 震荡周期 18f，44f 内抖两下半
const TAU = 60; // 缓衰减：帧 72 前仍余 ~14px 总分离，被"啪地"硬切归零

// 与 TitleBlock 同字形的可调色标题（错位印版需要单色副本）
const Plate: React.FC<{ color: string; dx: number; dy: number }> = ({ color, dx, dy }) => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transform: `translate(${dx}px, ${dy}px)`,
      mixBlendMode: 'multiply',
    }}
  >
    <div
      style={{
        fontFamily: 'Helvetica, Arial, sans-serif',
        fontWeight: 800,
        fontSize: 200,
        color,
        letterSpacing: -1,
        whiteSpace: 'nowrap',
      }}
    >
      IMPACT
    </div>
  </div>
);

export const RisoMisregistrationHit: React.FC = () => {
  const frame = useCurrentFrame();

  // 阶段判定
  const entering = frame >= 20 && frame < HIT; // 撞入
  const split = frame >= HIT && frame < SNAP; // 双版错位震荡
  const showSingle = frame < HIT || frame >= SNAP; // 正体（画外/撞入/套准后）

  // 撞入位移：右画外 1400px → 0，8f Easing.in(cubic)（加速撞停）
  const slideX = interpolate(frame, [20, HIT], [1400, 0], {
    easing: Easing.in(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 错位震荡包络：t 自命中起，衰减余弦（帧 72 前仍有可见残余，硬切归零成"啪"）
  const t = frame - HIT;
  const m = split ? Math.cos(OMEGA * t) * Math.exp(-t / TAU) : 0;
  const dx = AX * m;
  const dy = AY * m;

  // 套准合一脉冲：帧 72 起 4f scale 1.03 → 1，之后精确 1（保证结尾真静止）
  const pulse =
    frame >= SNAP && frame < SNAP + 4 ? 1 + 0.03 * (1 - (frame - SNAP) / 4) : 1;

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
      {/* 底部装饰线：全程静止的布景锚点 */}
      <div
        style={{
          position: 'absolute',
          left: 510,
          top: 740,
          width: 900,
          height: 6,
          borderRadius: 3,
          background: G.bar,
        }}
      />

      {/* 正体：画外等待 / 撞入 / 套准后（撞入前 frame<20 时在画外，视觉等同空场） */}
      {showSingle && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `translateX(${entering || frame < 20 ? slideX : 0}px) scale(${pulse})`,
            transformOrigin: 'center center',
          }}
        >
          <TitleBlock text="IMPACT" size={200} />
        </div>
      )}

      {/* 双版错位：浅灰版与深墨版反向偏移，multiply 叠加出"重影套印" */}
      {split && (
        <>
          <Plate color={G.mid} dx={-dx} dy={dy} />
          <Plate color={G.ink} dx={dx} dy={-dy} />
        </>
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

