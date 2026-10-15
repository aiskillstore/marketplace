// ---
// name: omniailab-motion-demo-impact-burst-kit
// description: 落点冲击套件（impact-burst-kit）——shockwave-ring + particle-burst 组合变异。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 落点冲击套件（impact-burst-kit）——shockwave-ring + particle-burst 组合变异。
// 主卡砸落的落点帧同时触发：冲击波环扩散 + 14 粒子放射迸发 + 震屏，
// 且冲击波前沿扫到左右邻卡的那一帧（按半径-距离算准=落点后 3f）邻卡被
// 向外推开再 spring 弹回——"波及邻居"即两条词汇焊接成立的证据。
// 关键帧：0–14 两侧卡驻场、主卡 scale1.8/y-120 悬停 → 14–20 主卡 6f 加速砸落 →
// 20 落点帧：环 80→900px(14f out-cubic, op .75→0) + 14 粒子飞散 160–340px(22f)
//   + 4f 震屏 6px 衰减 + 主卡 6f 压扁回弹 → 23 环前沿过邻卡(中心距 460px)：
//   邻卡外推 30px + rotate ±3° 阻尼振荡弹回(40f 内钳到 0) → 63–140 全静止(77f)。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, Card, TitleBlock } from '../../_fixtures/Fixtures';

// 伪随机（帧确定）
const h = (n: number): number => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

const CW = 400;
const CH = 280;
const GAP = 60;
const X_L = (1920 - (CW * 3 + GAP * 2)) / 2; // 300
const Y = (1080 - CH) / 2; // 400
const CX = 960; // 主卡中心
const CY = Y + CH / 2; // 540

const IMPACT = 20; // 落点帧
// 冲击波：80→900px 14f out-cubic。前沿到达邻卡中心距 460px 的帧：
// (460-80)/820=0.463 → 1-(1-p)^3 → p≈0.19 → t≈2.6f → 取落点后 3f = 帧 23
const HIT_NEIGHBOR = IMPACT + 3;

// 14 个粒子：方/圆混合，角度带向上偏置，飞散 160–340px 减速缩小消失
const PARTICLES = Array.from({ length: 14 }).map((_, i) => ({
  angle: -Math.PI / 2 + (h(i + 1) - 0.5) * Math.PI * 1.7, // 上半球为主
  dist: 160 + h(i + 40) * 180,
  size: 8 + h(i + 80) * 10,
  square: i % 2 === 0,
}));

// 邻卡被推开的阻尼振荡包络：t=0 瞬时到 1，之后余弦衰减弹回，40f 后钳 0 保真静止
const pushEnv = (f: number): number => {
  const t = f - HIT_NEIGHBOR;
  if (t < 0 || t >= 40) return 0;
  return Math.cos(t * 0.5) * Math.exp(-t / 8);
};

export const ImpactBurstKit: React.FC = () => {
  const frame = useCurrentFrame();

  // ── 主卡砸落：14–20 帧 scale 1.8→1 / y -120→0，加速进场
  const dropP = interpolate(frame, [14, IMPACT], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const mainScale = interpolate(dropP, [0, 1], [1.8, 1]);
  const mainDy = interpolate(dropP, [0, 1], [-120, 0]);
  // 落点后 6f 压扁回弹（squash & stretch）
  const sq = interpolate(frame, [IMPACT, IMPACT + 3, IMPACT + 6], [0, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });
  const mainSx = mainScale * (1 + 0.07 * sq);
  const mainSy = mainScale * (1 - 0.1 * sq);

  // ── ① 冲击波环：半径 80→900，14f，opacity 0.75→0
  const ringP = interpolate(frame, [IMPACT, IMPACT + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const ringR = interpolate(ringP, [0, 1], [80, 900]);
  const ringOp = frame >= IMPACT && frame < IMPACT + 14 ? 0.75 * (1 - ringP) : 0;

  // ── ② 粒子：落点起 22f，减速飞散 + 缩小 + 淡出
  const pT = interpolate(frame, [IMPACT, IMPACT + 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const particlesAlive = frame >= IMPACT && frame < IMPACT + 22;

  // ── ③ 邻卡外推 30px + rotate ±3°，阻尼弹回
  const env = pushEnv(frame);
  const pushX = 30 * env;
  const pushRot = 3 * env;

  // ── ④ 震屏：落点起 4f，6px 衰减（h 伪随机方向，帧确定）
  let shakeX = 0;
  let shakeY = 0;
  if (frame >= IMPACT && frame < IMPACT + 4) {
    const amp = 6 * (1 - (frame - IMPACT) / 4);
    shakeX = (h(frame * 3.7) - 0.5) * 2 * amp;
    shakeY = (h(frame * 7.1 + 13) - 0.5) * 2 * amp;
  }

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, transform: `translate(${shakeX}px, ${shakeY}px)` }}>
        <div style={{ position: 'absolute', left: 120, top: 96 }}>
          <TitleBlock text="IMPACT BURST KIT" size={54} />
        </div>

        {/* 左邻卡：被冲击波推开再弹回 */}
        <div
          style={{
            position: 'absolute',
            left: X_L,
            top: Y,
            transform: `translateX(${-pushX}px) rotate(${-pushRot}deg)`,
          }}
        >
          <Card w={CW} h={CH} seed={2} />
        </div>

        {/* 右邻卡 */}
        <div
          style={{
            position: 'absolute',
            left: X_L + (CW + GAP) * 2,
            top: Y,
            transform: `translateX(${pushX}px) rotate(${pushRot}deg)`,
          }}
        >
          <Card w={CW} h={CH} seed={4} />
        </div>

        {/* 主卡：砸落 + 落点压扁回弹 */}
        <div
          style={{
            position: 'absolute',
            left: X_L + CW + GAP,
            top: Y + mainDy,
            transform: `scale(${mainSx}, ${mainSy})`,
            transformOrigin: '50% 100%',
          }}
        >
          <Card w={CW} h={CH} seed={7} style={{ boxShadow: '0 6px 18px rgba(0,0,0,0.16)' }} />
        </div>

        {/* ② 粒子迸发（画在卡之上） */}
        {particlesAlive &&
          PARTICLES.map((p, i) => {
            const px = CX + Math.cos(p.angle) * p.dist * pT;
            const py = CY + Math.sin(p.angle) * p.dist * pT;
            const s = p.size * (1 - pT);
            if (s < 0.5) return null;
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: px - s / 2,
                  top: py - s / 2,
                  width: s,
                  height: s,
                  background: G.ink,
                  borderRadius: p.square ? 2 : '50%',
                  opacity: 1 - pT * pT,
                }}
              />
            );
          })}

        {/* ① 冲击波环（最上层扫过邻卡） */}
        {ringOp > 0 && (
          <div
            style={{
              position: 'absolute',
              left: CX - ringR,
              top: CY - ringR,
              width: ringR * 2,
              height: ringR * 2,
              border: `3px solid ${G.ink}`,
              borderRadius: '50%',
              opacity: ringOp,
              boxSizing: 'border-box',
            }}
          />
        )}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

