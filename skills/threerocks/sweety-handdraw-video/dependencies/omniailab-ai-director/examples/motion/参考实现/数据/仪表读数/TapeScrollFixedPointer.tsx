// ---
// name: omniailab-motion-demo-tape-scroll-fixed-pointer
// description: tape-scroll-fixed-pointer —— 滚带定针
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// tape-scroll-fixed-pointer —— 滚带定针
// 取景窗+琥珀三角指针钉死在画面正中，竖向长刻度带（0–500，每 50 一大格）
// 从窗后滚过："世界动、针不动"。先慢速爬（f12–55 读数 60→140 缓涨），
// 然后一次大跳变：刻度带冲刺 ~23f（峰值 ~50px/f）冲过 420 到 442，
// spring 刹车回摆一次（442→415→420）落定。窗内读数同步。f96 后真静止 44f。
// 帧确定性：value(frame) 纯分段 interpolate 全 clamp，带偏移 = value 线性映射。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const AMBER = '#b45309';

const PXU = 3; // px per unit：500 量程 → 1500px 长带
const CENTER_Y = 590; // 取景窗中线（屏幕坐标）
const TAPE_X = 830; // 刻度带左缘
const TAPE_W = 260;

// 读数时间线：静置→慢爬→冲刺(过冲到442)→回摆(415)→落定420→真静止
const valueAt = (frame: number): number => {
  if (frame <= 12) return 60;
  if (frame <= 55) {
    return interpolate(frame, [12, 55], [60, 140]); // 慢爬 ~5.6px/f
  }
  if (frame <= 78) {
    return interpolate(frame, [55, 78], [140, 442], {
      easing: Easing.inOut(Easing.cubic), // 冲刺段，峰值 ~50px/f
    });
  }
  if (frame <= 88) {
    return interpolate(frame, [78, 88], [442, 415], {
      easing: Easing.out(Easing.cubic), // 刹车回摆：甩过头再拉回
    });
  }
  return interpolate(frame, [88, 96], [415, 420], {
    easing: Easing.out(Easing.cubic),
    extrapolateRight: 'clamp',
  });
};

export const TapeScrollFixedPointer: React.FC = () => {
  const frame = useCurrentFrame();
  const v = valueAt(frame);

  // 刻度带：数值大在上。单位 u 的屏幕 y = CENTER_Y + (v - u) * PXU
  const yOf = (u: number): number => CENTER_Y + (v - u) * PXU;

  const ticks: React.ReactNode[] = [];
  for (let u = 0; u <= 500; u += 10) {
    const y = yOf(u);
    if (y < 180 || y > 1010) continue; // 视野外裁剪
    const major = u % 50 === 0;
    ticks.push(
      <div key={u} style={{
        position: 'absolute', top: y - 2, right: 0,
        width: major ? 92 : 46, height: major ? 5 : 3,
        background: major ? G.ink : G.mid, borderRadius: 2,
      }} />
    );
    if (major) {
      ticks.push(
        <div key={`n${u}`} style={{
          position: 'absolute', top: y - 22, right: 110,
          fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 700,
          fontSize: 38, color: G.mid, textAlign: 'right', width: 90,
        }}>
          {u}
        </div>
      );
    }
  }

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 90, width: '100%', textAlign: 'center' }}>
        <TitleBlock text="TAPE SCROLL · FIXED POINTER" size={68} />
      </div>

      {/* 刻度带容器（世界层：整体在动） */}
      <div style={{
        position: 'absolute', left: TAPE_X, top: 180, width: TAPE_W, height: 830,
        background: G.panel, border: `2px solid ${G.border}`, borderRadius: 12,
        overflow: 'hidden', boxSizing: 'border-box',
      }}>
        <div style={{ position: 'absolute', inset: 0 }}>{
          // 内层坐标 = 屏幕 y - 180
          <div style={{ position: 'absolute', left: 0, right: 14, top: -180, height: 1080 + 400 }}>
            {ticks}
          </div>
        }</div>
      </div>

      {/* 固定层：取景窗 + 琥珀三角指针 + 读数（针不动） */}
      <div style={{
        position: 'absolute', left: TAPE_X - 10, top: CENTER_Y - 46,
        width: TAPE_W + 20, height: 92,
        border: `5px solid ${AMBER}`, borderRadius: 10,
        boxShadow: '0 4px 14px rgba(0,0,0,0.14)', boxSizing: 'border-box',
        background: 'rgba(255,255,255,0.14)',
      }} />
      <svg width={60} height={64} style={{ position: 'absolute', left: TAPE_X - 66, top: CENTER_Y - 32 }}>
        <polygon points="4,4 56,32 4,60" fill={AMBER} />
      </svg>

      {/* 同步读数窗 */}
      <div style={{
        position: 'absolute', left: TAPE_X + TAPE_W + 70, top: CENTER_Y - 84,
        width: 380, height: 168, background: G.card,
        border: `2px solid ${G.border}`, borderRadius: 14,
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        display: 'flex', flexDirection: 'column', justifyContent: 'center',
        padding: '0 36px', boxSizing: 'border-box',
      }}>
        <div style={{ height: 12, width: 150, background: G.line, borderRadius: 6, marginBottom: 12 }} />
        <div style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 96, color: AMBER, letterSpacing: -2, lineHeight: 1 }}>
          {Math.round(v)}
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

