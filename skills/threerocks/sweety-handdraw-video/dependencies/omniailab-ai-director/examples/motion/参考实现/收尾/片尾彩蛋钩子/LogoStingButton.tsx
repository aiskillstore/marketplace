// ---
// name: omniailab-motion-demo-logo-sting-button
// description: logo-sting-button —— 收尾按钮镜头（button ending）
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// logo-sting-button —— 收尾按钮镜头（button ending）
// 上一镜收黑 → 黑场 → LOGO 入场定住（观众以为结束）→ 12f UI 特写彩蛋硬切 →
// 硬切回黑底 LOGO 定格。节奏是全部：彩蛋段短促像眨眼。收尾真静止 ≥40f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard } from '../../_fixtures/Fixtures';

// 时间轴（30fps，共 142f）
const T = {
  shotAEnd: 24,     // 0–24f 上一镜（B），f14–24 压暗到纯黑
  darkenStart: 14,
  blackEnd: 30,     // 24–30f 黑场 6f
  logoInEnd: 40,    // 30–40f LOGO 入场 10f
  holdEnd: 70,      // 40–70f 定住 30f（观众以为结束）
  eggEnd: 82,       // 70–82f 彩蛋硬切 12f
  total: 142,       // 82–142f 黑底 LOGO 真静止 60f
};

const LogoLockup: React.FC<{ opacity: number; scale: number }> = ({ opacity, scale }) => (
  <div style={{
    width: 1920, height: 1080, background: '#000',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  }}>
    <div style={{
      display: 'flex', alignItems: 'center', gap: 44,
      opacity, transform: `scale(${scale})`,
    }}>
      <div style={{
        width: 120, height: 120, borderRadius: 28, background: '#fff',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {/* 方块内一个黑色小标记，避免纯白块太空 */}
        <div style={{ width: 44, height: 44, borderRadius: 12, background: '#000' }} />
      </div>
      <div style={{
        fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
        fontSize: 90, color: '#fff', letterSpacing: 2,
      }}>
        ACME
      </div>
    </div>
  </div>
);

export const LogoStingButton: React.FC = () => {
  const frame = useCurrentFrame();

  // —— 段 1：上一镜（FakeDashboard B）压暗收黑 ——
  if (frame < T.shotAEnd) {
    const dark = interpolate(frame, [T.darkenStart, T.shotAEnd - 1], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: Easing.in(Easing.cubic),
    });
    return (
      <div style={{ width: 1920, height: 1080, background: '#000', position: 'relative', overflow: 'hidden' }}>
        <FakeDashboard variant="B" />
        <div style={{ position: 'absolute', inset: 0, background: '#000', opacity: dark }} />
      </div>
    );
  }

  // —— 段 2：黑场 6f ——
  if (frame < T.blackEnd) {
    return <div style={{ width: 1920, height: 1080, background: '#000' }} />;
  }

  // —— 段 4：彩蛋硬切 12f（variant A 按钮区 2.4x 裁切 + 角落小圆点 tick 闪 2f）——
  if (frame >= T.holdEnd && frame < T.eggEnd) {
    const egg = frame - T.holdEnd; // 0..11
    // tick 圆点：第 4–5f 亮 2f，像眨眼
    const tickOn = egg >= 4 && egg < 6;
    return (
      <div style={{ width: 1920, height: 1080, background: '#ececea', position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute', inset: 0,
          // 2.4x 放大：把第 1 张卡片底部"按钮行"（头像圆+文字条）平移到画面中心
          // 原坐标 (839, 531)（第 2 列卡片底部头像圆+文字条）→ 屏幕中心 (960, 540)
          // 选中列卡片可把左侧深色 sidebar 完全推出画面，特写更纯粹
          transform: 'translate(-1054px, -734px) scale(2.4)', transformOrigin: '0 0',
        }}>
          <FakeDashboard variant="A" />
        </div>
        {tickOn && (
          <div style={{
            position: 'absolute', right: 90, bottom: 80,
            width: 56, height: 56, borderRadius: 28, background: '#2f2f2f',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{ width: 20, height: 20, borderRadius: 10, background: '#fff' }} />
          </div>
        )}
      </div>
    );
  }

  // —— 段 3 + 段 5：黑底 LOGO（入场 → 定住 → 彩蛋后定格收尾，真静止）——
  const opacity = interpolate(frame, [T.blackEnd, T.logoInEnd], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const scale = interpolate(frame, [T.blackEnd, T.logoInEnd], [0.96, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <LogoLockup opacity={opacity} scale={scale} />;
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

