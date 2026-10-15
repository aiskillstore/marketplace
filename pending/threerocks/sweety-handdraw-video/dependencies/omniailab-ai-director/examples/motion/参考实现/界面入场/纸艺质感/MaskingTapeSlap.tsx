// ---
// name: omniailab-motion-demo-masking-tape-slap
// description: masking-tape-slap —— 纸胶带拍定
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// masking-tape-slap —— 纸胶带拍定
// 一张 Card 轻飘入位后悬着微晃（±1.5° 正弦 + 5px 上下浮），两条半透明纸胶带
// 先后从画外拍在对角（scale 1.45→1 + rotate 过冲 + 一帧压扁）。第一条拍下晃动减半，
// 第二条拍下同帧卡片停晃、投影瞬间变薄、整卡 2px 下沉——"按死"的一瞬是主角。
// 帧确定性：全部由 frame 派生，无随机。收尾 f86 后真静止 54f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, Card, TitleBlock } from '../../_fixtures/Fixtures';

const CARD_W = 560;
const CARD_H = 350;
const CX = (1920 - CARD_W) / 2;
const CY = (1080 - CARD_H) / 2 + 40;

const FLOAT_START = 12; // 开头 12f 空场静置
const FLOAT_END = 38;
const SLAP1 = 58;
const SLAP2 = 82;
const APPROACH = 6; // 胶带从画外扑向卡面的帧数
const FREEZE = 2; // 拍死后晃动归零帧数

// 悬浮晃动幅度包络：入位后升起 → 第一条胶带拍下后减半 → 第二条拍下冻结（由外层处理）
const amp = (f: number): number => {
  const rise = interpolate(f, [FLOAT_END, FLOAT_END + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const damp = interpolate(f, [SLAP1, SLAP1 + 4], [1, 0.45], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return rise * damp;
};

const rawRot = (f: number): number => amp(f) * 1.5 * Math.sin((f - FLOAT_END) * 0.16);
const rawBob = (f: number): number => amp(f) * 5 * Math.sin((f - FLOAT_END) * 0.11);

// 第二条拍下（SLAP2）同帧起 2f 内把晃动按死到 0
const frozen = (f: number, raw: (x: number) => number): number =>
  f <= SLAP2
    ? raw(f)
    : interpolate(f, [SLAP2, SLAP2 + FREEZE], [raw(SLAP2), 0], {
        extrapolateRight: 'clamp',
      });

const Tape: React.FC<{
  frame: number;
  land: number;
  cx: number; // 胶带中心点（世界坐标）
  cy: number;
  rot: number; // 落定角度
  fromX: number; // 画外来向偏移
  fromY: number;
}> = ({ frame, land, cx, cy, rot, fromX, fromY }) => {
  if (frame < land - APPROACH) return null; // 条件卸载：拍上前真不存在

  const t = interpolate(frame, [land - APPROACH, land], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = interpolate(t, [0, 1], [1.45, 1]);
  const dx = fromX * (1 - t);
  const dy = fromY * (1 - t);
  const opacity = interpolate(frame, [land - APPROACH, land - APPROACH + 2], [0, 0.85], {
    extrapolateRight: 'clamp',
  });
  // rotate 过冲：来时欠 16° → 落帧过 7° → 4f 内回正
  const r = interpolate(frame, [land - APPROACH, land, land + 4], [rot - 16, rot + 7, rot], {
    easing: Easing.out(Easing.quad),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // 一帧压扁：落帧 scaleY 0.72，次帧 0.9，随后复原
  const sy = frame === land ? 0.72 : frame === land + 1 ? 0.9 : 1;

  return (
    <div
      style={{
        position: 'absolute',
        left: cx - 160,
        top: cy - 34,
        width: 320,
        height: 68,
        transform: `translate(${dx}px, ${dy}px) rotate(${r}deg) scale(${scale}) scaleY(${sy})`,
        transformOrigin: '50% 50%',
        opacity,
        background:
          'linear-gradient(90deg, rgba(214,212,206,0.95) 0%, rgba(226,224,218,0.95) 30%, rgba(212,210,204,0.95) 60%, rgba(222,220,214,0.95) 100%)',
        // 撕边：两端锯齿
        clipPath:
          'polygon(0% 8%, 2.5% 0%, 97% 3%, 100% 12%, 98.2% 30%, 100% 52%, 98% 74%, 100% 90%, 96.5% 100%, 3% 97%, 0% 88%, 1.8% 64%, 0% 42%, 2% 22%)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.15)',
      }}
    />
  );
};

export const MaskingTapeSlap: React.FC = () => {
  const frame = useCurrentFrame();

  // 卡片飘入：从上方 -120px 缓落
  const floatY = interpolate(frame, [FLOAT_START, FLOAT_END], [-120, 0], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const floatOp = interpolate(frame, [FLOAT_START, FLOAT_START + 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const rot = frozen(frame, rawRot);
  const bob = frozen(frame, rawBob);

  // 按死：2px 下沉 + 投影瞬间变薄
  const sink = interpolate(frame, [SLAP2, SLAP2 + FREEZE], [0, 2], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shOff = interpolate(frame, [SLAP2, SLAP2 + FREEZE], [16, 3], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shBlur = interpolate(frame, [SLAP2, SLAP2 + FREEZE], [34, 8], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shAlpha = interpolate(frame, [SLAP2, SLAP2 + FREEZE], [0.22, 0.1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 110, width: '100%', textAlign: 'center' }}>
        <TitleBlock text="MASKING TAPE SLAP" size={72} />
      </div>

      <div
        style={{
          position: 'absolute',
          left: CX,
          top: CY,
          transform: `translateY(${floatY + bob + sink}px) rotate(${rot}deg)`,
          transformOrigin: '50% 50%',
          opacity: floatOp,
        }}
      >
        <Card
          w={CARD_W}
          h={CARD_H}
          seed={3}
          style={{ boxShadow: `0 ${shOff}px ${shBlur}px rgba(0,0,0,${shAlpha})` }}
        />
      </div>

      {/* 两条胶带钉在卡片对角（世界坐标，卡片在其下滑动微晃） */}
      <Tape frame={frame} land={SLAP1} cx={CX + 55} cy={CY + 40} rot={-45} fromX={-170} fromY={-130} />
      <Tape frame={frame} land={SLAP2} cx={CX + CARD_W - 55} cy={CY + CARD_H - 40} rot={-45} fromX={170} fromY={130} />
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

