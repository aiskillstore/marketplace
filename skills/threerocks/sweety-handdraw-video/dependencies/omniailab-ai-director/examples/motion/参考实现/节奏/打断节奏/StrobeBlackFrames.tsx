// ---
// name: omniailab-motion-demo-strobe-black-frames
// description: 频闪黑帧（strobe-black-frames）——节奏剪辑｜VJ strobe / 剪映闪黑。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 频闪黑帧（strobe-black-frames）——节奏剪辑｜VJ strobe / 剪映闪黑。
// FakeDashboard A 全程缓慢推近蓄张力（scale 1.0→1.05，Easing.in(quad)，
// 越到后段越快）。40–80f 频闪窗：全屏纯黑 #0c0c0c 按写死帧号表闪现，
// 每次持续 2f，间隔从 8f 收敛到 3f，窒息感逐渐逼近。最后一闪盖住 79–80，
// 帧 81 掀开时构图已硬切到 scale 1.35 对准第 2 行中间卡（零补间一帧到位），
// 叠 2f brightness 0.88 加深脉冲当落锤。
// 关键帧：0–78 推近 1.0→~1.05 → 黑闪 [40,48,55,61,66,70,73,76,79]（各 2f）→
// 79–80 全黑 → 帧 81 硬切 scale 1.35（81–82 加深脉冲）→ 83–134 全静止（52f ≥50f）。
// 光敏警示：实战建议配乐渐强使用。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard, TitleBlock } from '../../_fixtures/Fixtures';

// punch-in 落点：3×2 网格第 2 行中间卡中心（同 JumpCutPunchIn 几何）
// 侧栏 220 + 内边距 36；卡宽 (1920-220-72-56)/3 ≈ 524.67，卡高 (1080-72-72-28)/2 = 454
const CARD_L = 220 + 36 + 524.67 + 28; // ≈808.67
const CARD_T = 72 + 36 + 454 + 28; // 590
const CARD_W = 524.67;
const CARD_H = 454;
const ORIGIN_X = CARD_L + CARD_W / 2; // ≈1071
const ORIGIN_Y = CARD_T + CARD_H / 2; // 817

// 黑闪帧号表（写死）：间隔 8→7→6→5→4→3→3→3，每次持续 2f（f0 与 f0+1）
const FLASHES = [40, 48, 55, 61, 66, 70, 73, 76, 79];

const isBlack = (f: number): boolean =>
  FLASHES.some((f0) => f >= f0 && f <= f0 + 1);

// 帧 81 前缓慢推近（Easing.in 蓄力），81 起零补间硬切 1.35 定住
const scaleAt = (f: number): number =>
  f < 81
    ? interpolate(f, [0, 80], [1.0, 1.05], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
        easing: Easing.in(Easing.quad),
      })
    : 1.35;

// 落锤：81–82 两帧整画面加深脉冲
const pulseAt = (f: number): number => (f >= 81 && f <= 82 ? 0.88 : 1);

export const StrobeBlackFrames: React.FC = () => {
  const frame = useCurrentFrame();
  const s = scaleAt(frame);
  const b = pulseAt(frame);
  const black = isBlack(frame);

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.bg,
        position: 'relative',
        overflow: 'hidden',
        filter: `brightness(${b})`,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${s})`,
          transformOrigin: `${ORIGIN_X}px ${ORIGIN_Y}px`,
        }}
      >
        <FakeDashboard variant="A" />
        {/* 落点卡片标记：随构图一起缩放，提示硬切对准的核心卡 */}
        <div
          style={{
            position: 'absolute',
            left: CARD_L - 10,
            top: CARD_T - 10,
            width: CARD_W + 20,
            height: CARD_H + 20,
            border: `3px dashed ${G.mid}`,
            borderRadius: 20,
            boxSizing: 'border-box',
          }}
        />
      </div>
      {/* 标签不随缩放，固定顶栏位置 */}
      <div style={{ position: 'absolute', left: 260, top: 20 }}>
        <TitleBlock text="STROBE BLACK FRAMES" size={54} />
      </div>
      {/* 全屏黑闪层：盖住一切（含标签），每次 2f */}
      {black && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: '#0c0c0c',
            zIndex: 10,
          }}
        />
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

