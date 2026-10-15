// ---
// name: omniailab-motion-demo-split-flap-flip
// description: 参考实现——参考实现/文字/翻牌屏标题/SplitFlapFlip.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

// split-flap-flip：机场翻牌字。每字符一个深底翻牌格（上下两半），
// 逐格翻过 3 个乱码中间态后咔哒停在目标字，左→右 4f 级联成波。
// 节拍：0–21 建立（整排乱码静止）→ 22 起级联翻牌 → 78 全部停定 → 静止到 140。

const TEXT = 'SHIP FASTER';
const CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&';
const START = 22; // 级联起始帧
const STAGGER = 4; // 字符间级联延迟
const FLIP = 5; // 单次翻牌时长
const NFLIP = 3; // 每字符翻 3 次（2 个乱码中间态 + 1 次落到目标字）
const CELL_W = 118;
const CELL_H = 156;

// seed 正弦哈希（禁 Math.random）
const rnd = (a: number) => {
  const x = Math.sin(a * 127.3) * 43758.5453;
  return x - Math.floor(x);
};
const garble = (i: number, k: number) =>
  CHARSET[Math.floor(rnd(i * 7.13 + k * 3.71 + 1) * CHARSET.length)];

const FLAP_BG = '#262624';
const FLAP_INK = '#f4f4f2';

// 半格：上/下半各自 overflow hidden，内部整字定位错半格露出对应一半
const Half: React.FC<{ ch: string; part: 'top' | 'bottom' }> = ({ ch, part }) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      top: part === 'top' ? 0 : CELL_H / 2,
      width: CELL_W,
      height: CELL_H / 2,
      overflow: 'hidden',
      background: FLAP_BG,
      borderRadius: part === 'top' ? '10px 10px 0 0' : '0 0 10px 10px',
    }}
  >
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: part === 'top' ? 0 : -CELL_H / 2,
        width: CELL_W,
        height: CELL_H,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Helvetica, Arial, sans-serif',
        fontWeight: 800,
        fontSize: 100,
        color: FLAP_INK,
      }}
    >
      {ch}
    </div>
  </div>
);

const FlapCell: React.FC<{ target: string; i: number; frame: number }> = ({
  target,
  i,
  frame,
}) => {
  // 该格的字符序列：2 个乱码 → 1 个乱码 → 目标字（首态也是乱码，建立段可见）
  const seq = [garble(i, 0), garble(i, 1), garble(i, 2), target];
  const local = frame - (START + i * STAGGER);
  const done = local >= NFLIP * FLIP;

  // 停定咔哒：整格下沉回弹（1px 肉眼无感，放大到 6px 才有"咔哒"）
  const clickY = done
    ? interpolate(local, [15, 17, 19, 22], [0, 6, -1.5, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
        easing: Easing.out(Easing.quad),
      })
    : 0;

  let topCh = seq[0];
  let bottomCh = seq[0];
  let flap: React.ReactNode = null;

  if (done) {
    topCh = target;
    bottomCh = target;
  } else if (local > 0) {
    const k = Math.min(NFLIP - 1, Math.floor(local / FLIP));
    const from = seq[k];
    const to = seq[k + 1];
    const p = Easing.in(Easing.quad)((local - k * FLIP) / FLIP); // 重力感：越掉越快
    topCh = to; // 上半静态：翻开后露出下一字符的上半
    bottomCh = from; // 下半静态：保持旧字符直到活动叶盖下来
    if (p < 0.5) {
      // 前半程：旧字符上半叶 0→-90 掉下
      const deg = p * 2 * 90;
      flap = (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            transform: `rotateX(${-deg}deg)`,
            transformOrigin: `center ${CELL_H / 2}px`,
            backfaceVisibility: 'hidden',
            filter: `brightness(${1 - p * 2 * 0.45})`,
            zIndex: 2,
          }}
        >
          <Half ch={from} part="top" />
        </div>
      );
    } else {
      // 后半程：新字符下半叶 90→0 拍下盖住旧下半
      const deg = 90 - (p - 0.5) * 2 * 90;
      flap = (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            transform: `rotateX(${deg}deg)`,
            transformOrigin: `center ${CELL_H / 2}px`,
            backfaceVisibility: 'hidden',
            filter: `brightness(${0.55 + (p - 0.5) * 2 * 0.45})`,
            zIndex: 2,
          }}
        >
          <Half ch={to} part="bottom" />
        </div>
      );
    }
  }

  return (
    <div
      style={{
        position: 'relative',
        width: CELL_W,
        height: CELL_H,
        transform: `translateY(${clickY}px)`,
        perspective: 420,
        borderRadius: 10,
        boxShadow: '0 6px 18px rgba(0,0,0,0.3)',
      }}
    >
      <Half ch={topCh} part="top" />
      <Half ch={bottomCh} part="bottom" />
      {flap}
      {/* 中缝铰链线 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: CELL_H / 2 - 2,
          width: CELL_W,
          height: 4,
          background: '#141412',
          zIndex: 3,
        }}
      />
    </div>
  );
};

export const SplitFlapFlip: React.FC = () => {
  const frame = useCurrentFrame();
  let letterIdx = 0;
  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 背景假页面压暗，突出翻牌板 */}
      <div style={{ position: 'absolute', inset: 0, opacity: 0.3, filter: 'saturate(0.8)' }}>
        <FakeDashboard variant="A" />
      </div>
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          {TEXT.split('').map((ch, idx) => {
            if (ch === ' ') {
              return <div key={idx} style={{ width: 52 }} />;
            }
            const i = letterIdx++;
            return <FlapCell key={idx} target={ch} i={i} frame={frame} />;
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

