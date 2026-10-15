// ---
// name: omniailab-motion-demo-split-text-stagger
// description: 逐字遮罩裂升（split-text-stagger）——GSAP SplitText 惯用入场。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 逐字遮罩裂升（split-text-stagger）——GSAP SplitText 惯用入场。
// 标题 "MOTION SYSTEM" 按字符拆 span，每字外包 overflow:hidden 的行高盒，
// 内层从 translateY(115%) 升到 0，各 14f Easing.out(cubic)，带 10% 过冲
// 再 6f 回落（原案 6% 过冲，按可感性红线加码到 10%）。delay = 字符索引×2f。
// 底部基线细线（G.bar 2px）在首字起跳同帧从左向右生长，暗示裁切线存在。
// 关键帧：0–12 空场 hold → 12 首字起跳 + 基线开始生长 → 每字 12+i*2 起跳，
// 14f 升至 -10% 过冲 → 再 6f 回落归 0 → 末字(索引12)于 56f 落定 →
// 56–130 全静止（74f ≥ 40f，无逐帧噪声层）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const TEXT = 'MOTION SYSTEM';
const START = 12; // 首字起跳帧
const RISE = 14; // 升起时长
const SETTLE = 6; // 过冲回落时长
const OVERSHOOT = -10; // 过冲到 -10%（原案 6%，加码）
const FONT = 120;

// 单字符纵向位移（%）：115 → -10（out cubic）→ 0（out quad），帧确定
const charY = (f: number, idx: number): number => {
  const t0 = START + idx * 2;
  if (f < t0 + RISE) {
    return interpolate(f, [t0, t0 + RISE], [115, OVERSHOOT], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
  }
  return interpolate(f, [t0 + RISE, t0 + RISE + SETTLE], [OVERSHOOT, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });
};

export const SplitTextStagger: React.FC = () => {
  const frame = useCurrentFrame();
  const chars = TEXT.split('');
  // 基线：首字起跳同帧开始，从左向右生长到 100%
  const lineW = interpolate(frame, [START, START + 26], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', left: 120, top: 96 }}>
        <TitleBlock text="SPLIT TEXT STAGGER" size={54} />
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
        }}
      >
        <div style={{ display: 'flex' }}>
          {chars.map((c, i) => (
            <div
              key={i}
              style={{
                // 遮罩盒：上方留 0.3em 头部空间容纳过冲，底边即裁切线
                overflow: 'hidden',
                height: FONT * 1.35,
                display: 'flex',
                alignItems: 'flex-end',
              }}
            >
              <span
                style={{
                  display: 'inline-block',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 800,
                  fontSize: FONT,
                  lineHeight: 1.05,
                  color: G.ink,
                  letterSpacing: 2,
                  transform: `translateY(${charY(frame, i)}%)`,
                }}
              >
                {c === ' ' ? ' ' : c}
              </span>
            </div>
          ))}
        </div>
        {/* 基线细线：宽度从 0 生长到全文宽 */}
        <div style={{ width: 920, marginTop: 10, display: 'flex', justifyContent: 'flex-start' }}>
          <div style={{ height: 2, width: `${lineW}%`, background: G.bar }} />
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

