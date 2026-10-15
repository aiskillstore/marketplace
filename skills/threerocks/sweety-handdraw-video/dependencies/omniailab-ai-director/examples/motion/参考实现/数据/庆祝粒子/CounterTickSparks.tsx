// ---
// name: omniailab-motion-demo-counter-tick-sparks
// description: counter-tick-sparks —— 数字跳动溅火
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// counter-tick-sparks —— 数字跳动溅火
// 中央大计数器 0 → 12,847（easeOut 逐位跳动），每逢跳过整千的 tick 帧，
// 数字顶部溅 6–10 颗大火星（初速向上 9–13px/f、重力下坠 14–18f 内坠灭）；
// 终值揭晓那跳翻倍 20 颗 + 数字弹 1.1x 回落。
// 结尾所有火星寿命耗尽条件卸载，真静止 ≥40f。
// 帧确定性：tick 帧从同一 easeOut 曲线预解析（模块级求出），火星 = 纯 age 闭式弹道。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const AMBER = '#b45309';
const TARGET = 12847;
const COUNT_END = 78; // 计数结束帧
const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
const valueAt = (f: number) => Math.round(TARGET * easeOutCubic(Math.min(Math.max(f / COUNT_END, 0), 1)));

const frac = (x: number) => x - Math.floor(x);
const rnd = (i: number, salt: number) => frac(Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453);

// 预解析 tick 帧：跳过整千的那一帧 + 终值揭晓帧
const TICKS: { f: number; big: boolean }[] = (() => {
  const out: { f: number; big: boolean }[] = [];
  let prev = 0;
  for (let f = 1; f <= COUNT_END; f++) {
    const v = valueAt(f);
    if (Math.floor(v / 1000) > Math.floor(prev / 1000)) out.push({ f, big: false });
    prev = v;
  }
  out.push({ f: COUNT_END, big: true }); // 终值揭晓
  return out;
})();

const SPARK_LIFE = 18;
const GRAV = 0.9;

export const CounterTickSparks: React.FC = () => {
  const frame = useCurrentFrame();
  const value = valueAt(frame);

  // 终值揭晓弹 1.1x 回落
  const popScale =
    1 +
    0.1 *
      interpolate(frame, [COUNT_END, COUNT_END + 5, COUNT_END + 16], [0, 1, 0], {
        easing: Easing.out(Easing.quad),
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });

  const TOP_Y = 452; // 数字顶缘（火星发射线）
  const CX = 960;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 110, width: '100%', textAlign: 'center' }}>
        <TitleBlock text="COUNTER TICK SPARKS" size={72} />
      </div>

      {/* 计数卡 */}
      <div style={{
        position: 'absolute', left: 560, top: 400, width: 800, height: 330,
        background: G.card, border: `2px solid ${G.border}`, borderRadius: 16,
        boxSizing: 'border-box', boxShadow: '0 4px 14px rgba(0,0,0,0.08)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20,
      }}>
        <div style={{ height: 14, width: 220, background: G.bar, borderRadius: 7 }} />
        <div style={{
          fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 168,
          color: G.ink, letterSpacing: -3, lineHeight: 1, fontVariantNumeric: 'tabular-nums',
          transform: `scale(${popScale})`,
        }}>
          {value.toLocaleString('en-US')}
        </div>
        <div style={{ height: 10, width: 150, background: G.line, borderRadius: 5 }} />
      </div>

      {/* 火星：每个 tick 一簇，寿命耗尽条件卸载 */}
      {TICKS.map((tick, t) => {
        const age = frame - tick.f;
        if (age <= 0 || age >= SPARK_LIFE) return null;
        const n = tick.big ? 20 : 6 + Math.floor(rnd(t, 21) * 5); // 6–10，终跳 20
        return Array.from({ length: n }).map((_, i) => {
          const salt = t * 31 + i;
          // 初速：向上 9–13px/f，水平 ±4.5px/f 扇形铺开（终跳更宽）
          const vy = -(9 + rnd(salt, 2) * 4);
          const vx = (rnd(salt, 3) - 0.5) * (tick.big ? 13 : 9);
          const x0 = CX + (rnd(salt, 4) - 0.5) * (tick.big ? 560 : 380); // 沿数字顶缘散布
          const x = x0 + vx * age;
          const y = TOP_Y + vy * age + 0.5 * GRAV * age * age;
          const life = 1 - age / SPARK_LIFE;
          const size = (tick.big ? 7 : 5.5) * (0.4 + 0.6 * life);
          return (
            <div key={`${t}-${i}`} style={{
              position: 'absolute', left: x, top: y, width: size, height: size,
              borderRadius: size / 2, background: AMBER, opacity: life,
              boxShadow: `0 0 ${6 * life}px ${AMBER}`,
            }} />
          );
        });
      })}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

