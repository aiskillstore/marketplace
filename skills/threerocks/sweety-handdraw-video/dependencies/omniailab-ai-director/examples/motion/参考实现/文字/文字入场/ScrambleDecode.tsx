// ---
// name: omniailab-motion-demo-scramble-decode
// description: 乱码解码字（scramble-decode）——终端黑客感文字入场。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 乱码解码字（scramble-decode）——终端黑客感文字入场。
// 标题 "DECODE SPEED" 每字符先高速跳随机字母/数字（每 2f 换一个，seed hash 取字符），
// 从左到右逐个锁定：第 i 个字符在帧 20+i*6 锁定为真字符，锁定瞬间该字符反色闪
// （G.ink 色块白字 2f）随即恢复。跳动期字符 G.mid，锁定后 G.ink。
// 关键帧：0–20f 全员乱跳 → 20–86f 从左到右逐个锁定 → 87–130f 完全静止收尾。
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const TEXT = 'DECODE SPEED';
const CHARSET = 'ABCDEF0123456789#$%&';
const LOCK_START = 20; // 第 0 个字符锁定帧
const LOCK_STEP = 6; // 相邻字符锁定间隔
const FLASH_LEN = 2; // 锁定反色闪持续帧数

// 帧确定伪随机
const h = (n: number) => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

export const ScrambleDecode: React.FC = () => {
  const frame = useCurrentFrame();
  const chars = TEXT.split('');
  const lockedCount = chars.filter((c, i) => c === ' ' || frame >= LOCK_START + i * LOCK_STEP).length;
  const allLocked = lockedCount === chars.length;

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 48,
      }}
    >
      <div
        style={{
          fontFamily: 'ui-monospace, Menlo, Monaco, monospace',
          fontWeight: 800,
          fontSize: 120,
          letterSpacing: 2,
          display: 'flex',
        }}
      >
        {chars.map((ch, i) => {
          if (ch === ' ') {
            return <span key={i} style={{ display: 'inline-block', width: '0.7em' }} />;
          }
          const lockFrame = LOCK_START + i * LOCK_STEP;
          const locked = frame >= lockFrame;
          const flashing = locked && frame < lockFrame + FLASH_LEN;
          // 跳动期：每 2 帧换一个伪随机字符
          const tick = Math.floor(frame / 2);
          const 乱码锁定Char = CHARSET[Math.floor(h(i * 101 + tick * 7 + 13) * CHARSET.length)];
          const shown = locked ? ch : 乱码锁定Char;
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                width: '1ch',
                textAlign: 'center',
                color: flashing ? G.card : locked ? G.ink : G.mid,
                background: flashing ? G.ink : 'transparent',
              }}
            >
              {shown}
            </span>
          );
        })}
      </div>
      {/* 底部进度提示条：已锁定字符数比例，帮助读出"从左到右扫过"的推进感 */}
      <div style={{ width: 900, height: 10, background: G.line, borderRadius: 5, overflow: 'hidden' }}>
        <div
          style={{
            width: `${(lockedCount / chars.length) * 100}%`,
            height: '100%',
            background: allLocked ? G.ink : G.mid,
            borderRadius: 5,
          }}
        />
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

