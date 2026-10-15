// ---
// name: omniailab-motion-demo-card-footage-cadence
// description: card-footage-cadence｜字卡穿插节奏
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// card-footage-cadence｜字卡穿插节奏
// UI 镜头 ↔ 黑底字卡像对话接拍：0–14f UI A 缓推 → 硬切 8f 字卡 SHIP →
// 硬切 12f UI B 1.6x 裁切缓移 → 8f 字卡 FASTER → 10f UI A 2x 裁切 →
// 10f 字卡 TODAY(下划线) → 62f 硬切收尾全景定格。
// UI 段全部带微动（推/移），字卡段除落定微缩(1.05→1, out-cubic)外全静，
// 动↔静对比即手法本体。所有切换零过渡（条件挂载，无 crossfade）。
// 收尾 62–105f 轻推收完，105–150f 真静止 45f ≥ 40f。帧确定，无随机。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard } from '../../_fixtures/Fixtures';

const CLAMP = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// 黑底白字字卡：落定微缩 1.05→1（out-cubic，段内前 5f 完成），其余全静
const TitleCard: React.FC<{ text: string; local: number; underline?: boolean }> = ({
  text,
  local,
  underline = false,
}) => {
  const scale = interpolate(local, [0, 5], [1.05, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill
      style={{ background: '#0d0d0d', alignItems: 'center', justifyContent: 'center' }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 26,
        }}
      >
        <div
          style={{
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 800,
            fontSize: 170,
            color: '#ffffff',
            letterSpacing: 2,
            lineHeight: 1,
          }}
        >
          {text}
        </div>
        {underline && (
          <div style={{ width: 560, height: 14, background: '#ffffff', borderRadius: 7 }} />
        )}
      </div>
    </AbsoluteFill>
  );
};

// UI 镜头：包一层 transform 做缓推/缓移，硬切由外层条件挂载保证
const UiShot: React.FC<{
  variant: 'A' | 'B';
  transform: string;
  origin?: string;
}> = ({ variant, transform, origin = '50% 50%' }) => (
  <AbsoluteFill style={{ overflow: 'hidden', background: '#ececea' }}>
    <div style={{ width: 1920, height: 1080, transform, transformOrigin: origin }}>
      <FakeDashboard variant={variant} />
    </div>
  </AbsoluteFill>
);

export const CardFootageCadence: React.FC = () => {
  const frame = useCurrentFrame();

  // ---- 分段：切点 14 / 22 / 34 / 42 / 52 / 62，总长 150 ----

  // 段1 0–14f：UI A 全景缓推 1.0→1.08
  if (frame < 14) {
    const s = interpolate(frame, [0, 14], [1, 1.08], CLAMP);
    return <UiShot variant="A" transform={`scale(${s})`} />;
  }

  // 段2 14–22f：字卡 SHIP
  if (frame < 22) {
    return <TitleCard text="SHIP" local={frame - 14} />;
  }

  // 段3 22–34f：UI B 1.6x 裁切 + 横向缓移（120px 内容位移，屏上 ~192px）。
  // origin 偏左让列表行图标入画，读得出是 UI（QA 后调：50%→35%）
  if (frame < 34) {
    const tx = interpolate(frame - 22, [0, 12], [60, -60], CLAMP);
    return (
      <UiShot variant="B" transform={`scale(1.6) translateX(${tx}px)`} origin="35% 50%" />
    );
  }

  // 段4 34–42f：字卡 FASTER
  if (frame < 42) {
    return <TitleCard text="FASTER" local={frame - 34} />;
  }

  // 段5 42–52f：UI A 另一处 2x 裁切（左上卡片区）+ 继续缓推 2.0→2.14
  if (frame < 52) {
    const s = interpolate(frame - 42, [0, 10], [2, 2.14], CLAMP);
    return <UiShot variant="A" transform={`scale(${s})`} origin="32% 30%" />;
  }

  // 段6 52–62f：字卡 TODAY + 下划线
  if (frame < 62) {
    return <TitleCard text="TODAY" local={frame - 52} underline />;
  }

  // 段7 62–150f：收尾全景 UI 定格。62–105f 极缓推收完（out-cubic），
  // 105f 后 transform 值恒为 1.02，105–150f 真静止 45f。
  const s = interpolate(frame, [62, 105], [1, 1.02], {
    ...CLAMP,
    easing: Easing.out(Easing.cubic),
  });
  return <UiShot variant="B" transform={`scale(${s})`} />;
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

