// ---
// name: omniailab-motion-demo-hit-counter
// description: 参考实现——参考实现/特效/命中反馈/HitCounter.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, Card, TitleBlock, G } from '../../_fixtures/Fixtures';

// hit-counter 连招计数：三张功能卡接连砸入槽位，每次命中 = 全局顿帧 2f
// + 落点伤害数字上浮渐隐 + 右上角 ×N 计数跳字（脉冲/倾斜逐次加码）。
// 组合：hitstop + damage-number-pop + combo-counter。

// —— 时间结构（动画时间 t 空间）——
// 0–19 建立 hold；卡 i 于 t = HIT-10 → HIT ease-in 砸落；HIT = 30/60/90；
// 每命中后真实帧多出 2f 顿帧，末卡效果收完后静止 hold 到 150。
const HITS_T = [30, 60, 90]; // 命中时刻（重映射后的动画时间）
const STOP = 2; // 每次顿帧帧数
// 真实命中帧 = 动画命中时刻 + 前面累计的顿帧
const HITS_REAL = HITS_T.map((h, i) => h + i * STOP);

const SLOT_W = 420;
const SLOT_H = 300;
const SLOT_Y = 430;
const SLOT_XS = [390, 890, 1390].map((cx) => cx - SLOT_W / 2);

const DMG_TEXT = ['+1.2k', '+2.4k', '+4.8k'];
const PULSE = [1.3, 1.45, 1.6]; // 计数器脉冲峰值，逐次递增
const TILT = [-2, -4, -6]; // 计数器倾斜，逐次递增并保持

export const HitCounter: React.FC = () => {
  const frame = useCurrentFrame();

  // —— 全局帧 remap：每个真实命中帧起冻结 2f（全画面顿帧）——
  let t = frame;
  for (const h of HITS_REAL) {
    t -= Math.min(Math.max(frame - h, 0), STOP);
  }

  const count = HITS_T.filter((h) => t >= h).length; // 当前连击数

  // —— 计数器（右上角 ×N）——
  let counterScale = 1;
  let counterRot = 0;
  let counterSize = 84;
  if (count > 0) {
    const i = count - 1;
    const since = t - HITS_T[i];
    counterScale = 1 + (PULSE[i] - 1) * Math.exp(-since / 2.4); // 脉冲后指数回落
    counterRot = TILT[i]; // 倾斜保持，越打越斜
    counterSize = 84 + i * 14; // 字号逐次加大
  }

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 背景 dashboard 压暗，突出前景连招 */}
      <div style={{ filter: 'saturate(0.9)', opacity: 0.4 }}>
        <FakeDashboard variant="B" />
      </div>

      {/* 三个槽位虚线框（全程可见，建立期先立预期） */}
      {SLOT_XS.map((x, i) => (
        <div
          key={`slot-${i}`}
          style={{
            position: 'absolute', left: x, top: SLOT_Y,
            width: SLOT_W, height: SLOT_H,
            border: `3px dashed ${G.bar}`, borderRadius: 16,
            boxSizing: 'border-box',
          }}
        />
      ))}

      {/* 三张功能卡：各隔 30f，命中前 10f ease-in 加速砸落 */}
      {HITS_T.map((hit, i) => {
        const y = interpolate(t, [hit - 10, hit], [-520, SLOT_Y], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.in(Easing.quad),
        });
        if (t < hit - 10) return null;
        // 触地 3f 内轻微压扁，衬托命中
        const since = t - hit;
        const squash = since >= 0 ? 1 - 0.06 * Math.exp(-since / 1.5) : 1;
        return (
          <div
            key={`card-${i}`}
            style={{
              position: 'absolute', left: SLOT_XS[i], top: y,
              transform: `scaleY(${squash})`, transformOrigin: 'bottom center',
            }}
          >
            <Card w={SLOT_W} h={SLOT_H} seed={i + 2} style={{ boxShadow: '0 16px 48px rgba(0,0,0,0.25)' }} />
          </div>
        );
      })}

      {/* 伤害数字：命中帧起 scale 1.4→1、上浮 60px、12f 渐隐 */}
      {HITS_T.map((hit, i) => {
        const s = t - hit;
        if (s < 0 || s > 14) return null;
        const scale = interpolate(s, [0, 5], [1.4, 1], {
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.quad),
        });
        const rise = interpolate(s, [0, 12], [0, -60], {
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.quad),
        });
        const opacity = interpolate(s, [0, 4, 12], [1, 1, 0], {
          extrapolateRight: 'clamp',
        });
        return (
          <div
            key={`dmg-${i}`}
            style={{
              position: 'absolute',
              left: SLOT_XS[i] + SLOT_W / 2, top: SLOT_Y - 40 + rise,
              transform: `translateX(-50%) scale(${scale})`,
              transformOrigin: 'center bottom',
              opacity,
            }}
          >
            <TitleBlock text={DMG_TEXT[i]} size={72} />
          </div>
        );
      })}

      {/* 右上角连击计数器：跳字 + 递增脉冲 + 递增倾斜 */}
      <div
        style={{
          position: 'absolute', right: 70, top: 50,
          transform: `scale(${counterScale}) rotate(${counterRot}deg)`,
          transformOrigin: 'center center',
          opacity: count === 0 ? 0.25 : 1,
        }}
      >
        <div
          style={{
            background: G.ink, color: '#fff', borderRadius: 18,
            padding: '10px 34px 16px',
            fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
            fontSize: counterSize, letterSpacing: -2, lineHeight: 1.1,
            boxShadow: '0 8px 28px rgba(0,0,0,0.3)',
          }}
        >
          {`×${count}`}
        </div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

