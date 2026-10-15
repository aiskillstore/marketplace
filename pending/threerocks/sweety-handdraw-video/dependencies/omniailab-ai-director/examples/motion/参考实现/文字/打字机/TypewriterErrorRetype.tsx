// ---
// name: omniailab-motion-demo-typewriter-error-retype
// description: typewriter-error-retype｜打字机误删重打
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// typewriter-error-retype｜打字机误删重打
// 浅底居中大字：f2 起 2f/字符打出 "just a dashboard"(16 字符) → f32–48 停顿
// 16f(光标闪两下=犹豫) → f48 起 1.5f/字符逐字退格删掉 "a dashboard"(11 字符，
// 字符直接消失) → f68 起 1.5f/字符果断打出 "your command center"(19 字符，
// f95 打完) → 光标闪两个周期(10f/周期)后 f110 永久熄灭。节奏三档：打 2f/删
// 1.5f/重打 1.5f 且无停顿。f110 后全静止，160f 总长 → 收尾真静止 50f。
// 等宽感：逐字符固定宽 span，无 letter-spacing 动画。全部帧确定。
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const TEXT1 = 'just a dashboard'; // 16 chars
const KEEP = 5; // "just " 保留
const DEL = TEXT1.length - KEEP; // 11 chars 待删
const TEXT2 = 'your command center'; // 19 chars

const T1 = 2; // 第一遍打字起点，2f/字符
const PAUSE_START = T1 + (TEXT1.length - 1) * 2; // f32 打完
const DS = PAUSE_START + 16; // f48 开删，1.5f/字符
const RS = 68; // 重打起点，1.5f/字符（删完 f64.5 后小顿 3.5f）
const TYPE2_END = RS + (TEXT2.length - 1) * 1.5; // f95 打完
const CURSOR_OFF = 115; // 两个 10f 闪烁周期后熄灭（最后一次视觉变化 f110）

const CHAR_W = 58; // fontSize 96 的等宽感字符宽

// 光标可见性：打字/删除时常亮；停顿段 8f 周期闪两下；打完后 10f 周期闪两下；之后永灭
const cursorOn = (f: number): boolean => {
  if (f >= CURSOR_OFF) return false;
  if (f >= TYPE2_END) {
    // f95 起：on[95,100) off[100,105) on[105,110) off[110,115)
    return Math.floor((f - TYPE2_END) / 5) % 2 === 0;
  }
  if (f >= DS) return true; // 删除 + 重打：常亮（果断）
  if (f >= PAUSE_START) {
    // 犹豫段 f32–48：on[32,36) off[36,40) on[40,44) off[44,48)
    return Math.floor((f - PAUSE_START) / 4) % 2 === 0;
  }
  return true; // 第一遍打字：常亮
};

export const TypewriterErrorRetype: React.FC = () => {
  const f = useCurrentFrame();

  // 第一遍已打出字符数
  const n1 = f < T1 ? 0 : Math.min(TEXT1.length, Math.floor((f - T1) / 2) + 1);
  // 已删除字符数（从尾部删）
  const removed = f < DS ? 0 : Math.min(DEL, Math.floor((f - DS) / 1.5) + 1);
  // 第二遍已打出字符数
  const n2 = f < RS ? 0 : Math.min(TEXT2.length, Math.floor((f - RS) / 1.5) + 1);

  const shown =
    TEXT1.slice(0, Math.max(KEEP, n1 - removed)).slice(0, n1) +
    TEXT2.slice(0, n2);

  const chars = shown.split('');

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        position: 'relative',
      }}
    >
      {/* 左缘锚定：最终句 24 字符×58=1392px，左起 264 恰好整体居中；
          打字过程不横移（真打字机感） */}
      <div
        style={{
          position: 'absolute',
          left: 264,
          top: 490,
          display: 'flex',
          alignItems: 'center',
        }}
      >
        {chars.map((c, i) => (
          <span
            key={i}
            style={{
              display: 'inline-block',
              width: CHAR_W,
              textAlign: 'center',
              fontFamily: '"Courier New", Courier, monospace',
              fontSize: 96,
              fontWeight: 700,
              color: G.ink,
              lineHeight: 1.1,
            }}
          >
            {c === ' ' ? ' ' : c}
          </span>
        ))}
        {/* 光标：竖线，条件挂载而非 opacity 0 */}
        {cursorOn(f) && (
          <span
            style={{
              display: 'inline-block',
              width: 7,
              height: 100,
              marginLeft: 4,
              background: G.ink,
            }}
          />
        )}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

