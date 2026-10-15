// ---
// name: omniailab-motion-component-caption
// description: origin: 工程/src/demo/Caption.tsx（模板片同源组件）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// origin: 工程/src/demo/Caption.tsx（模板片同源组件）
import { interpolate, useCurrentFrame } from 'remotion';

const MONO = 'ui-monospace, SFMono-Regular, Menlo, monospace';
const AMBER = 'oklch(52% 0.115 65)';

/** Screen-space narration caption: a mono UI info-strip at the bottom of the
 * frame, led by a small amber square. Fades/rises in over 8 frames and fades
 * out over the last 8 of its window.
 *
 * 注意：22px 属"信息条"风格（大字距全大写作补偿），低于审美准则 Q11 的
 * 字幕线（≥56px）。作为叙事主字幕使用时应提到 56–60px 档或改用大字幕组件；
 * 沿用 22px 信息条风格属于 Q11 允许的有意识违反，需在项目说明中注明。 */
export const Caption: React.FC<{ text: string; duration: number; bottom?: number }> = ({
  text,
  duration,
  bottom = 72,
}) => {
  const frame = useCurrentFrame();
  const inT = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const outT = interpolate(frame, [duration - 8, duration], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'baseline',
        gap: 14,
        fontFamily: MONO,
        fontSize: 22,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        color: 'oklch(45% 0.006 82)',
        opacity: inT * outT,
        transform: `translateY(${(1 - inT) * 8}px)`,
        pointerEvents: 'none',
      }}
    >
      <span style={{ width: 6, height: 6, background: AMBER, display: 'inline-block' }} />
      <span>{text}</span>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

