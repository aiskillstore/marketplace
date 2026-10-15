// ---
// name: omniailab-motion-demo-karaoke-fill-sync
// description: 卡拉OK填色随读（karaoke-fill-sync）——旁白读到哪个词，哪个词就被深色从左到右
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 卡拉OK填色随读（karaoke-fill-sync）——旁白读到哪个词，哪个词就被深色从左到右
// 点亮。两行标语 "SHIP FASTER / BREAK NOTHING"，每个词双层同文本叠放：底层 G.line
// 浅灰字，上层 G.ink 深字用 clip-path: inset(0 X% 0 0) 按词内进度线性填充（逐词独立
// 叠层，clip 百分比即词内进度，无需量测词在整行的像素占比）。词级时间表模拟语速：
// SHIP 20–38、FASTER 42–75（长词慢读）、BREAK 85–103、NOTHING 107–130，词间停顿。
// 正在填的词底下有 8px 深色下划线跟随填充右缘作读指。0–19f hold；130–149f 真静止。
import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

type Word = { text: string; start: number; end: number };

const LINES: Word[][] = [
  [
    { text: 'SHIP', start: 20, end: 38 },
    { text: 'FASTER', start: 42, end: 75 },
  ],
  [
    { text: 'BREAK', start: 85, end: 103 },
    { text: 'NOTHING', start: 107, end: 130 },
  ],
];

const KaraokeWord: React.FC<{ word: Word; frame: number }> = ({ word, frame }) => {
  // 词内 linear 填充进度，clamp 保证读完保持
  const p = interpolate(frame, [word.start, word.end], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const active = frame >= word.start && frame < word.end; // 正在读这个词
  return (
    <span style={{ position: 'relative', display: 'inline-block' }}>
      {/* 底层：浅灰未读字 */}
      <span style={{ color: G.line }}>{word.text}</span>
      {/* 上层：深字按进度从左到右揭开 */}
      <span
        style={{
          position: 'absolute',
          inset: 0,
          color: G.ink,
          clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`,
        }}
      >
        {word.text}
      </span>
      {/* 读指下划线：只在正在填的词下出现，右缘跟随填充进度 */}
      {active && (
        <span
          style={{
            position: 'absolute',
            left: 0,
            bottom: -14,
            width: `${p * 100}%`,
            height: 8,
            background: G.ink,
          }}
        />
      )}
    </span>
  );
};

export const KaraokeFillSync: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        paddingLeft: 240,
        boxSizing: 'border-box',
        fontFamily: 'Helvetica, Arial, sans-serif',
        fontSize: 130,
        fontWeight: 800,
        letterSpacing: 2,
        lineHeight: 1.45,
      }}
    >
      {LINES.map((words, li) => (
        <div key={li} style={{ display: 'flex', gap: 48 }}>
          {words.map((w) => (
            <KaraokeWord key={w.text} word={w} frame={frame} />
          ))}
        </div>
      ))}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

