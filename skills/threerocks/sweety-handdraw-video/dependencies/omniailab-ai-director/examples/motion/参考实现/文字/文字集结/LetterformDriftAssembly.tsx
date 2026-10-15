// ---
// name: omniailab-motion-demo-letterform-drift-assembly
// description: 字形漂移合拢（letterform-drift-assembly）——Stranger Things 片头式入场。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 字形漂移合拢（letterform-drift-assembly）——Stranger Things 片头式入场。
// 标题 "ASSEMBLE" 拆 9 字符：各自从不同方向（h(i) seeded 随机向量，
// 幅度 ±260–360px）带 blur 8px + opacity 0.35 缓慢漂入，错峰归位
// （delay i×3f，45f 行程，Easing.out(cubic)）。每字锁定瞬间给一次
// "加深脉冲"：字色 G.ink→#000→G.ink + 描边 0→3px→0（8f）——白底上
// 不用发光用加深（库判例）。全部合体后整词 scale 1→1.04→1 收束呼吸
// （判例：1.02 太弱，加码到 1.04）。
// 关键帧：0–24 各字错峰启程 → i 字 [i*3, i*3+45] 漂入归位 →
// 锁定帧 i*3+45 起 8f 加深脉冲（最后一字 69–77）→ 80–104 整词呼吸 →
// 104–150 全静止（46f，无逐帧滤镜）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const h = (n: number) => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

const WORD = 'ASSEMBLE';
const TRAVEL = 45; // 每字漂入行程帧数
const STAG = 3; // 错峰间隔

export const LetterformDriftAssembly: React.FC = () => {
  const frame = useCurrentFrame();
  const chars = WORD.split('');
  const lastLock = (chars.length - 1) * STAG + TRAVEL; // 69

  // 整词收束呼吸：80–92 放大到 1.04，92–104 回落，之后恒 1 → 帧确定
  const breath =
    frame < 92
      ? interpolate(frame, [80, 92], [1, 1.04], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        })
      : interpolate(frame, [92, 104], [1.04, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.inOut(Easing.cubic),
        });

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', left: 120, top: 96 }}>
        <TitleBlock text="LETTERFORM DRIFT ASSEMBLY" size={54} />
      </div>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${breath})`,
        }}
      >
        {chars.map((c, i) => {
          const start = i * STAG;
          const lock = start + TRAVEL;
          // 漂入进度
          const p = interpolate(frame, [start, lock], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: Easing.out(Easing.cubic),
          });
          // seeded 起始向量：方向 h(i)，幅度 260–360px
          const ang = h(i + 1) * Math.PI * 2;
          const mag = 260 + h(i + 101) * 100;
          const dx = Math.cos(ang) * mag * (1 - p);
          const dy = Math.sin(ang) * mag * (1 - p);
          const blur = 8 * (1 - p);
          const op = interpolate(p, [0, 1], [0.35, 1]);
          // 锁定加深脉冲：lock→lock+8，三角波 0→1→0
          const pulse =
            frame <= lock || frame >= lock + 8
              ? 0
              : frame < lock + 4
                ? (frame - lock) / 4
                : (lock + 8 - frame) / 4;
          const shade = Math.round(47 * (1 - pulse)); // #2f(47)→#00
          const color = `rgb(${shade},${shade},${shade})`;
          const strokeW = 3 * pulse;
          return (
            <span
              key={i}
              style={{
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 800,
                fontSize: 140,
                letterSpacing: 8,
                color,
                display: 'inline-block',
                transform: `translate(${dx}px, ${dy}px)`,
                opacity: op,
                filter: blur > 0.01 ? `blur(${blur}px)` : undefined,
                WebkitTextStroke: strokeW > 0.01 ? `${strokeW}px #000` : undefined,
              }}
            >
              {c}
            </span>
          );
        })}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

