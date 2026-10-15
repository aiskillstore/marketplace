// ---
// name: omniailab-motion-demo-brand-frame-snap
// description: 品牌画框吸附 —— figma-devmode 0:28–0:32 (品牌画框吸附) + 0:43–0:47 (frame-color-flip)
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 品牌画框吸附 —— figma-devmode 0:28–0:32 (品牌画框吸附) + 0:43–0:47 (frame-color-flip)
// 一圈粗品牌色画框先于内容出现包住全屏 → 灰阶"录屏窗口"在框内落位 →
// 停一拍 → 画框整圈蓝→绿同帧硬翻色，窗口内容同帧换布局。
// 一个 borderColor 完成章节导航/状态提示/品牌露出。
import React from 'react';
import { useCurrentFrame, spring, interpolate } from 'remotion';
import { G, FakeDashboard } from '../../_fixtures/Fixtures';

const FPS = 30;
const FIGMA_BLUE = '#3E7BFA';
const DEV_GREEN = '#1BC47D';
const FLIP_FRAME = 78; // 同帧硬翻色时刻

const clamp01 = (t: number) => Math.min(1, Math.max(0, t));
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

export const BrandFrameSnap: React.FC = () => {
  const f = useCurrentFrame();
  const mode: 'design' | 'dev' = f < FLIP_FRAME ? 'design' : 'dev';
  const frameColor = mode === 'design' ? FIGMA_BLUE : DEV_GREEN;

  // 1) 画框先登场：厚度从 0 长到 44px（ease-out，前 18 帧）
  const frameGrow = easeOut(clamp01(f / 18));
  const frameW = 44 * frameGrow;

  // 2) 窗口在框内落位：从下方 + 略缩，弹簧弹入（帧 14 起）
  const drop = spring({ frame: f - 14, fps: FPS, config: { damping: 16, stiffness: 110, mass: 1 } });
  const winY = interpolate(drop, [0, 1], [560, 0]);
  const winS = interpolate(drop, [0, 1], [0.82, 1]);
  const winO = interpolate(drop, [0, 0.25], [0, 1], { extrapolateRight: 'clamp' });

  // 3) 翻色瞬间给 2 帧白闪脉冲 + 画框轻微厚度弹跳，强化"换挡"
  const sinceFlip = f - FLIP_FRAME;
  const flash = sinceFlip >= 0 && sinceFlip < 3 ? 0.55 - sinceFlip * 0.18 : 0;
  const snapPulse = sinceFlip >= 0 ? Math.exp(-sinceFlip * 0.22) * Math.cos(sinceFlip * 0.9) * 10 : 0;

  // 模式标签
  const label = mode === 'design' ? 'DESIGN' : 'DEV MODE';

  return (
    <div style={{ width: 1920, height: 1080, background: '#161618', position: 'relative', overflow: 'hidden' }}>
      {/* 框内内容区 */}
      <div style={{
        position: 'absolute', inset: frameW + snapPulse, background: G.bg,
        overflow: 'hidden', borderRadius: 8,
      }}>
        {/* 录屏窗口（带标题栏的窗口卡）落位 */}
        <div style={{
          position: 'absolute', left: '50%', top: '50%',
          width: 1560, height: 830,
          transform: `translate(-50%, -50%) translateY(${winY}px) scale(${winS})`,
          opacity: winO,
          borderRadius: 16, overflow: 'hidden',
          boxShadow: '0 24px 70px rgba(0,0,0,0.28)',
          border: `2px solid ${G.border}`, background: G.panel,
        }}>
          {/* 窗口标题栏 */}
          <div style={{
            height: 52, background: '#e9e9e7', borderBottom: `2px solid ${G.line}`,
            display: 'flex', alignItems: 'center', gap: 10, padding: '0 22px', boxSizing: 'border-box',
          }}>
            {[0, 1, 2].map((i) => (
              <div key={i} style={{ width: 16, height: 16, borderRadius: 8, background: G.bar }} />
            ))}
            <div style={{ marginLeft: 18, height: 12, width: 260, background: G.line, borderRadius: 6 }} />
            {/* 模式徽标：随画框同帧换色换字 */}
            <div style={{
              marginLeft: 'auto', background: frameColor, color: '#fff',
              fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 15,
              letterSpacing: 1.5, padding: '6px 16px', borderRadius: 8,
              opacity: winO,
            }}>
              {label}
            </div>
          </div>
          {/* 窗口内容：翻色同帧换布局 A→B */}
          <div style={{ transform: 'scale(0.81)', transformOrigin: '0 0', width: 1920, height: 1080 }}>
            <FakeDashboard variant={mode === 'design' ? 'A' : 'B'} />
          </div>
        </div>
      </div>

      {/* 品牌色画框：用 4 条实体边而非 border，翻色是纯 background 同帧硬切 */}
      {([
        { left: 0, top: 0, right: 0, height: frameW + snapPulse },
        { left: 0, bottom: 0, right: 0, height: frameW + snapPulse },
        { left: 0, top: 0, bottom: 0, width: frameW + snapPulse },
        { right: 0, top: 0, bottom: 0, width: frameW + snapPulse },
      ] as React.CSSProperties[]).map((pos, i) => (
        <div key={i} style={{ position: 'absolute', background: frameColor, ...pos }} />
      ))}

      {/* 画框上的模式角标（左上，嵌在框带里） */}
      <div style={{
        position: 'absolute', left: 70, top: 0, height: frameW + snapPulse,
        display: 'flex', alignItems: 'center',
        fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
        fontSize: 22, letterSpacing: 3, color: '#ffffff',
        opacity: frameGrow,
      }}>
        {label}
      </div>

      {/* 翻色白闪脉冲 */}
      {flash > 0 && (
        <div style={{ position: 'absolute', inset: 0, background: '#ffffff', opacity: flash }} />
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

