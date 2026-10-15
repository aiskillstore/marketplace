// ---
// name: omniailab-motion-demo-draw-svg-trace
// description: 描边生长圈注（描边生长圈注）——DrawSVG 惯用的入场退场。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 描边生长圈注（描边生长圈注）——DrawSVG 惯用的入场退场。
// 屏心 560×380 卡片位置先空着，一条 G.ink 4px 描边沿圆角矩形轮廓跑一整圈
// 把轮廓"画"出来（rect pathLength=1，dasharray=1，dashoffset 1→0）；
// 线头叠一段 0.045 长的 6px 粗短 dash 当"笔头"跑在最前。闭合瞬间轮廓闪一次
// 加深加粗，卡片内容 8f 淡入，描边淡出换成卡片自身 border；随后标题下划线
// 再来一次短版描边生长（第二用法）。
// 关键帧：0–8 空场 hold → 8–48 轮廓描边生长 40f（inOut cubic）→
// 48–56 闪黑加粗（48–50 上 50–56 回）+ 内容 8f 淡入 →
// 54–64 描边淡出 / 自身 border 淡入 → 68–86 下划线短版生长 → 90–140 真静止 50f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const CW = 560;
const CH = 380;
const CX = (1920 - CW) / 2; // 680
const CY = (1080 - CH) / 2; // 350
const PEN = 0.045; // 笔头 dash 长度（占整圈比例）

export const DrawSvgTrace: React.FC = () => {
  const frame = useCurrentFrame();

  // 轮廓描边进度：8–48，40f，inOut cubic
  const p = interpolate(frame, [8, 48], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // 闭合闪烁：48–50 冲到峰值，50–56 回落。峰值 = 纯黑 + 4→8px 加粗
  const flashUp = interpolate(frame, [48, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const flashDown = interpolate(frame, [50, 56], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });
  const flash = frame < 50 ? flashUp : flashDown;
  const strokeW = 4 + flash * 4;
  const strokeColor = flash > 0.5 ? '#000000' : G.ink;

  // 内容淡入：48–56（8f）
  const contentOp = interpolate(frame, [48, 56], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  // 描边淡出 / 卡片自身 border 淡入：54–64
  const traceOp = interpolate(frame, [54, 64], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const borderOp = 1 - traceOp;

  // 笔头：短 dash 覆盖 [p-PEN, p]，只在描边期可见
  const penOp = p > 0.02 && p < 0.985 ? 1 : 0;

  // 第二用法：标题下划线短版生长 68–86（18f，out cubic）
  const up = interpolate(frame, [68, 86], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const upenOp = up > 0.03 && up < 0.97 ? 1 : 0;
  const UW = 300; // 下划线长度

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', left: 120, top: 96 }}>
        <TitleBlock text="DRAW SVG TRACE" size={54} />
      </div>

      {/* 卡片内容（手写灰阶块：标题条/下划线位/文字行/头像行），闭合后 8f 淡入 */}
      <div
        style={{
          position: 'absolute',
          left: CX,
          top: CY,
          width: CW,
          height: CH,
          borderRadius: 14,
          background: G.card,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          padding: 32,
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          gap: 18,
          opacity: contentOp,
        }}
      >
        <div style={{ height: 24, width: 340, background: G.bar, borderRadius: 10 }} />
        {/* 下划线占位：由下方 SVG 画出，这里留 6px 空隙 */}
        <div style={{ height: 6 }} />
        <div style={{ height: 13, width: '86%', background: G.line, borderRadius: 6 }} />
        <div style={{ height: 13, width: '72%', background: G.line, borderRadius: 6 }} />
        <div style={{ height: 13, width: '60%', background: G.line, borderRadius: 6 }} />
        <div style={{ marginTop: 'auto', display: 'flex', gap: 12, alignItems: 'center' }}>
          <div style={{ width: 34, height: 34, borderRadius: 17, background: G.mid }} />
          <div style={{ height: 12, width: 96, background: G.line, borderRadius: 6 }} />
        </div>
      </div>

      {/* 卡片自身 border：描边淡出时接棒 */}
      <div
        style={{
          position: 'absolute',
          left: CX,
          top: CY,
          width: CW,
          height: CH,
          borderRadius: 14,
          border: `2px solid ${G.border}`,
          boxSizing: 'border-box',
          opacity: borderOp,
        }}
      />

      {/* 描边生长层：主线 4px + 笔头 6px 短 dash */}
      {traceOp > 0.001 && (
        <svg
          width={CW}
          height={CH}
          style={{ position: 'absolute', left: CX, top: CY, overflow: 'visible', opacity: traceOp }}
        >
          <rect
            x={1}
            y={1}
            width={CW - 2}
            height={CH - 2}
            rx={14}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeW}
            pathLength={1}
            strokeDasharray="1"
            strokeDashoffset={1 - p}
            strokeLinecap="round"
          />
          {penOp > 0 && (
            <rect
              x={1}
              y={1}
              width={CW - 2}
              height={CH - 2}
              rx={14}
              fill="none"
              stroke={G.ink}
              strokeWidth={7}
              pathLength={1}
              strokeDasharray={`${PEN} ${1 - PEN}`}
              strokeDashoffset={PEN - p}
              strokeLinecap="round"
            />
          )}
        </svg>
      )}

      {/* 第二用法：标题下划线短版描边生长（画完常驻） */}
      {up > 0.001 && (
        <svg
          width={UW}
          height={8}
          style={{ position: 'absolute', left: CX + 32, top: CY + 32 + 24 + 10, overflow: 'visible' }}
        >
          <line
            x1={0}
            y1={4}
            x2={UW}
            y2={4}
            stroke={G.ink}
            strokeWidth={4}
            pathLength={1}
            strokeDasharray="1"
            strokeDashoffset={1 - up}
            strokeLinecap="round"
          />
          {upenOp > 0 && (
            <line
              x1={0}
              y1={4}
              x2={UW}
              y2={4}
              stroke={G.ink}
              strokeWidth={7}
              pathLength={1}
              strokeDasharray={`${PEN * 2} ${1 - PEN * 2}`}
              strokeDashoffset={PEN * 2 - up}
              strokeLinecap="round"
            />
          )}
        </svg>
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

