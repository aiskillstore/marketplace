// ---
// name: omniailab-motion-demo-cube-rotate
// description: 立方体空间翻转（cube-rotate）——cube transition 转场自实现。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 立方体空间翻转（cube-rotate）——cube transition 转场自实现。
// FakeDashboard A / B 各缩放 0.82 居中，当立方体相邻两面：perspective 1400px，
// 面宽 W=1920*0.82，两面各 rotateY(面角) translateZ(W/2)，场景整体先
// translateZ(-W/2) 再 rotateY(θ)（把正面拉回 z=0，保证 hold 时精确 0.82 尺度）。
// 旧面 A 转出画面 brightness 1→0.55 压暗，新面 B 从 +90° 侧转入 0.55→1 亮起；
// 接缝两侧各一条竖向渐变阴影，随角度 sin(pπ) 加深再消失；转动中段叠 blur(1.5px)，
// 落定摘掉（filter 条件挂载，保证收尾逐帧完全相同）。
// 关键帧：0–30 静止展示 A → 30–68 θ 0→-90°（inOut cubic）翻转 → 68–140 B 真静止 72f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard, TitleBlock } from '../../_fixtures/Fixtures';

const S = 0.82;
const W = 1920 * S; // 面宽 = 立方体棱长
const H = 1080 * S;

// 单个立方体面：W×H 视口内放缩放 0.82 的整幅 dashboard
const Face: React.FC<{
  variant: 'A' | 'B';
  rot: number; // 面自身的 rotateY（A=0，B=90）
  brightness: number;
  seam: number; // 接缝阴影不透明度 0–1
  seamSide: 'right' | 'left'; // 阴影贴在哪条竖边（即共享棱一侧）
}> = ({ variant, rot, brightness, seam, seamSide }) => (
  <div
    style={{
      position: 'absolute',
      width: W,
      height: H,
      overflow: 'hidden',
      backfaceVisibility: 'hidden',
      transform: `rotateY(${rot}deg) translateZ(${W / 2}px)`,
      filter: `brightness(${brightness})`,
      background: G.bg,
    }}
  >
    <div style={{ transform: `scale(${S})`, transformOrigin: '0 0' }}>
      <FakeDashboard variant={variant} />
    </div>
    {seam > 0.01 && (
      <div
        style={{
          position: 'absolute',
          top: 0,
          [seamSide]: 0,
          width: 150,
          height: H,
          opacity: seam,
          background:
            seamSide === 'right'
              ? 'linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.55))'
              : 'linear-gradient(to left, rgba(0,0,0,0), rgba(0,0,0,0.55))',
        }}
      />
    )}
  </div>
);

export const CubeRotate: React.FC = () => {
  const frame = useCurrentFrame();
  // 翻转进度：30–68f，inOut cubic；两端 clamp 保证 hold 段逐帧恒定
  const p = interpolate(frame, [30, 68], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const theta = -90 * p;
  const brightA = 1 - 0.45 * p; // 旧面转出压暗 1→0.55
  const brightB = 0.55 + 0.45 * p; // 新面转入亮起 0.55→1
  const mid = Math.sin(p * Math.PI); // 0→1→0，45° 时最深
  const seam = mid * 0.9;
  const blur = mid * 1.5;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      {/* blur 外包一层：>0.02 才挂 filter，落定后收尾帧完全相同 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          filter: blur > 0.02 ? `blur(${blur}px)` : undefined,
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: (1920 - W) / 2,
            top: (1080 - H) / 2,
            width: W,
            height: H,
            perspective: 1400,
          }}
        >
          <div
            style={{
              position: 'absolute',
              inset: 0,
              transformStyle: 'preserve-3d',
              transform: `translateZ(${-W / 2}px) rotateY(${theta}deg)`,
            }}
          >
            {/* 面 A：正面出发，绕左而去；接缝棱在其右边 */}
            <Face variant="A" rot={0} brightness={brightA} seam={seam} seamSide="right" />
            {/* 面 B：从 +90° 侧面转进来；接缝棱在其左边 */}
            <Face variant="B" rot={90} brightness={brightB} seam={seam} seamSide="left" />
          </div>
        </div>
      </div>
      <div style={{ position: 'absolute', left: 120, top: 60 }}>
        <TitleBlock text="CUBE ROTATE" size={54} />
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

