// ---
// name: omniailab-motion-demo-score-slam
// description: 比分砸落入场（score-slam）——ESPN 比分弹窗 slam。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 比分砸落入场（score-slam）——ESPN 比分弹窗 slam。
// KPI 卡从 scale 2.5 / rotate 5° / y-80 高空加速砸落屏心，落点帧同时触发
// 三件套：冲击波描边圆环扩散消散、8 个尘点小方块 seeded 抛物线飞散、
// 整画面震屏指数衰减。砸落带 3% 压缩过冲回弹落定。
// 关键帧：0–8 环境 hold → 8–14 砸落（Easing.in(quad)，scale 2.5→0.97，
// rotate 5→0，y -80→0）→ 14 落点帧触发环/尘/震 → 14–22 过冲回弹 0.97→1 →
// 14–28 圆环 60→720px 直径 op 0.7→0 → 14–30 尘点飞散 → 14–19 震屏 18px 衰减
// → 30–135 全静止（≥45f，无逐帧噪声层）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard, TitleBlock } from '../../_fixtures/Fixtures';

// 库规伪随机
const h = (n: number) => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

const IMPACT = 14; // 落点帧
const CX = 960;
const CY = 540;
const CARD_W = 460;
const CARD_H = 260;

export const ScoreSlam: React.FC = () => {
  const frame = useCurrentFrame();

  // —— 卡片砸落：8–14 加速下砸到 0.97（压缩过冲），14–22 回弹到 1 ——
  const slamScale =
    frame < IMPACT
      ? interpolate(frame, [8, IMPACT], [2.5, 0.97], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.in(Easing.quad),
        })
      : interpolate(frame, [IMPACT, 22], [0.97, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.cubic),
        });
  const slamRot = interpolate(frame, [8, IMPACT], [5, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.quad),
  });
  const slamY = interpolate(frame, [8, IMPACT], [-80, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.quad),
  });
  const cardOp = interpolate(frame, [8, 11], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // —— 震屏：落点帧起 5f，18px 指数衰减，seeded 方向，19f 后严格归零 ——
  let shakeX = 0;
  let shakeY = 0;
  if (frame >= IMPACT && frame < IMPACT + 5) {
    const t = frame - IMPACT;
    const amp = 18 * Math.exp(-t * 0.9);
    shakeX = amp * (h(frame * 7 + 1) * 2 - 1);
    shakeY = amp * (h(frame * 13 + 2) * 2 - 1);
  }

  // —— 冲击波圆环：14f 内直径 60→720，opacity 0.7→0 ——
  const ringT = interpolate(frame, [IMPACT, IMPACT + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const ringD = interpolate(ringT, [0, 1], [60, 860]);
  // 不透明度走线性帧时间（与扩散的 out-cubic 解耦），扩到最大前都保持可见
  const ringTLin = interpolate(frame, [IMPACT, IMPACT + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ringOp = interpolate(ringTLin, [0, 0.65, 1], [0.75, 0.55, 0]);
  const ringOn = frame >= IMPACT && frame < IMPACT + 14;

  // —— 8 个尘点：seeded 角度抛物线飞散 120–260px，16f 减速缩小消失 ——
  const dustT = interpolate(frame, [IMPACT, IMPACT + 16], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const dustTLin = interpolate(frame, [IMPACT, IMPACT + 16], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const dustOn = frame >= IMPACT && frame < IMPACT + 16;

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
      {/* 震屏容器：整画面一起抖 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translate(${shakeX}px, ${shakeY}px)`,
        }}
      >
        {/* 虚化 dashboard 环境底 */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            filter: 'blur(6px)',
            transform: 'scale(1.05)',
            transformOrigin: '50% 50%',
          }}
        >
          <FakeDashboard variant="B" />
        </div>

        <div style={{ position: 'absolute', left: 120, top: 96 }}>
          <TitleBlock text="SCORE SLAM" size={54} />
        </div>

        {/* ② 尘点飞散 */}
        {dustOn &&
          Array.from({ length: 8 }).map((_, i) => {
            const ang = (i / 8) * Math.PI * 2 + (h(i + 3) - 0.5) * 0.7;
            const dist = 160 + h(i + 11) * 160; // 160–320px
            const size = 18 + h(i + 23) * 12; // 18–30px
            const dx = Math.cos(ang) * dist * dustT;
            // 抛物线：先随角度飞出，再叠加重力下坠
            const dy = Math.sin(ang) * dist * dustT + 90 * dustT * dustT;
            const s = size * (1 - 0.75 * dustTLin);
            const op = interpolate(dustTLin, [0, 0.75, 1], [0.9, 0.7, 0]);
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: CX + dx - s / 2,
                  top: CY + CARD_H / 2 - 20 + dy - s / 2,
                  width: s,
                  height: s,
                  background: G.ink,
                  opacity: op,
                  borderRadius: 2,
                }}
              />
            );
          })}

        {/* ① 冲击波圆环 */}
        {ringOn && (
          <div
            style={{
              position: 'absolute',
              left: CX - ringD / 2,
              top: CY - ringD / 2,
              width: ringD,
              height: ringD,
              borderRadius: '50%',
              border: `6px solid ${G.ink}`,
              opacity: ringOp,
              boxSizing: 'border-box',
            }}
          />
        )}

        {/* KPI 卡本体 */}
        {frame >= 8 && (
          <div
            style={{
              position: 'absolute',
              left: CX - CARD_W / 2,
              top: CY - CARD_H / 2,
              width: CARD_W,
              height: CARD_H,
              background: G.card,
              border: `3px solid ${G.border}`,
              borderRadius: 18,
              boxShadow: '0 10px 30px rgba(0,0,0,0.18)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              opacity: cardOp,
              transform: `translateY(${slamY}px) rotate(${slamRot}deg) scale(${slamScale})`,
              transformOrigin: '50% 50%',
            }}
          >
            <div
              style={{
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 800,
                fontSize: 110,
                color: G.ink,
                letterSpacing: -3,
                lineHeight: 1,
              }}
            >
              +247%
            </div>
            <div
              style={{
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 600,
                fontSize: 26,
                color: G.mid,
                letterSpacing: 4,
              }}
            >
              QUARTERLY GROWTH
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

