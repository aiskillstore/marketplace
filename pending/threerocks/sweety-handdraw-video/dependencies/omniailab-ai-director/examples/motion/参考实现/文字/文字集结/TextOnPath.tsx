// ---
// name: omniailab-motion-demo-text-on-path
// description: 文字沿曲线流入（text-on-path）——字符沿一条上升贝塞尔曲线（像图表增长线）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 文字沿曲线流入（text-on-path）——字符沿一条上升贝塞尔曲线（像图表增长线）
// 鱼贯滑入，行进中按切线角旋转；到达各自终点后再从"贴线姿态"lerp 到水平基线位
// 拼成正常标题。曲线本身随字符前进同步 evolve（dashoffset 生长）。
// 关键帧：字符 i 于 i*2 起跑、45f 沿线到达 t_i（out cubic）→ 到达后停 8f →
// 12f 摆正到水平基线（y 拉平、rotate→0）→ 全部落定约 f103 → 103–150 真静止。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

// 上升贝塞尔：左下 → 右上，先缓后陡（增长线形状）
const P0 = { x: 200, y: 820 };
const P1 = { x: 760, y: 810 };
const P2 = { x: 1240, y: 660 };
const P3 = { x: 1500, y: 320 };

const bez = (t: number) => {
  const u = 1 - t;
  return {
    x: u * u * u * P0.x + 3 * u * u * t * P1.x + 3 * u * t * t * P2.x + t * t * t * P3.x,
    y: u * u * u * P0.y + 3 * u * u * t * P1.y + 3 * u * t * t * P2.y + t * t * t * P3.y,
  };
};
// 切线角（度）
const tangent = (t: number) => {
  const u = 1 - t;
  const dx = 3 * u * u * (P1.x - P0.x) + 6 * u * t * (P2.x - P1.x) + 3 * t * t * (P3.x - P2.x);
  const dy = 3 * u * u * (P1.y - P0.y) + 6 * u * t * (P2.y - P1.y) + 3 * t * t * (P3.y - P2.y);
  return (Math.atan2(dy, dx) * 180) / Math.PI;
};

const TEXT = 'GROWTH ALL THE WAY';
const N = TEXT.length;
const CHAR_W = 46; // 64px fontWeight 800 的近似字宽
const FINAL_Y = 300; // 水平基线（标题最终落位）
const FINAL_X0 = 960 - (N * CHAR_W) / 2;

export const TextOnPath: React.FC = () => {
  const frame = useCurrentFrame();
  // 曲线 evolve：随最前字符推进同步生长
  const evolve = interpolate(frame, [0, 82], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', left: 120, top: 96 }}>
        <TitleBlock text="TEXT ON PATH" size={54} />
      </div>
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        <path
          d={`M ${P0.x} ${P0.y} C ${P1.x} ${P1.y}, ${P2.x} ${P2.y}, ${P3.x} ${P3.y}`}
          fill="none" stroke={G.bar} strokeWidth={3}
          pathLength={1} strokeDasharray={1} strokeDashoffset={1 - evolve}
        />
      </svg>
      {TEXT.split('').map((ch, i) => {
        if (ch === ' ') return null;
        const tEnd = 0.12 + 0.82 * (i / (N - 1)); // 各字符沿线终点
        const start = i * 2;
        // 沿线推进：start 起 45f 到达 tEnd
        const t = interpolate(frame, [start, start + 45], [0, tEnd], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          easing: Easing.out(Easing.cubic),
        });
        const pOnCurve = bez(t);
        const angOnCurve = tangent(t);
        // 到达后停 8f，再 12f 摆正到水平基线
        const settle = interpolate(frame, [start + 53, start + 65], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        });
        const x = pOnCurve.x + (FINAL_X0 + i * CHAR_W - pOnCurve.x) * settle;
        const y = pOnCurve.y + (FINAL_Y - pOnCurve.y) * settle;
        const ang = angOnCurve * (1 - settle);
        const op = interpolate(frame, [start, start + 8], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        });
        return (
          <div key={i} style={{
            position: 'absolute', left: x, top: y, opacity: op,
            transform: `translate(-50%, -50%) rotate(${ang}deg)`,
            fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
            fontSize: 64, color: G.ink,
          }}>
            {ch}
          </div>
        );
      })}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

