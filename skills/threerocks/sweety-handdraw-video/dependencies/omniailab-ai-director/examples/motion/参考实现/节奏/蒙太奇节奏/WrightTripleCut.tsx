// ---
// name: omniailab-motion-demo-wright-triple-cut
// description: 三连咔哒特写（wright-triple-cut）——Edgar Wright《僵尸肖恩》流程三连快切:
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 三连咔哒特写（wright-triple-cut）——Edgar Wright《僵尸肖恩》流程三连快切:
// 帧 0–24 全景 hold(FakeDashboard A);随后三个 10f 特写硬切连打,每个特写
// 前 4f 静止、中 3f 动作、后 3f 静止:①25–34 光标按下按钮(圆点缩一圈+按钮变深)
// ②35–44 开关左拨右(圆钮 3f 滑动+轨道 G.mid→G.ink) ③45–54 大数字 rotateX 翻牌 0→1;
// 帧 55 甩回全景:6f whip translateX 滑入,高速段 3 层错帧副本模拟运动模糊,
// 中上卡片提亮泛光+大 "1" 标记结果;帧 ~68 起全静止到 130(真静止 ≥60f)。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

const HOLD_END = 25; // 全景 hold 结束
const C1 = 25; // 特写一:光标按下
const C2 = 35; // 特写二:开关
const C3 = 45; // 特写三:翻牌
const WHIP = 55; // 甩回全景

// 特写统一舞台:G.panel 底 + 居中大白卡,主体屏心、同倍率感
const CloseupStage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ width: 1920, height: 1080, background: G.panel, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{
      width: 1400, height: 800, background: G.card, border: `4px solid ${G.border}`,
      borderRadius: 28, boxShadow: '0 6px 24px rgba(0,0,0,0.08)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      {children}
    </div>
  </div>
);

// 结果卡片(3×2 网格中上格)的几何:sidebar 220 + padding 36,列宽 524,行高 454
const RESULT = { left: 808, top: 108, w: 524, h: 454 };

export const WrightTripleCut: React.FC = () => {
  const f = useCurrentFrame();

  // ===== 帧 0–24:全景 hold =====
  if (f < HOLD_END) {
    return <FakeDashboard variant="A" />;
  }

  // ===== 特写一(25–34):光标从悬停到按下,按钮变深 =====
  if (f < C2) {
    const t = f - C1; // 局部 0–9;动作窗 4–6
    const p = interpolate(t, [4, 7], [0, 1], {
      easing: Easing.out(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    const cursorScale = 1 - 0.3 * p; // 1 → 0.7 缩一圈
    const btnBg = p < 0.5 ? G.bar : '#5c5c5a'; // 按下瞬间变深
    const btnY = 8 * p; // 按钮被压下 8px
    return (
      <CloseupStage>
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{
            width: 620, height: 190, borderRadius: 40, background: btnBg,
            border: `5px solid ${G.mid}`, boxSizing: 'border-box',
            transform: `translateY(${btnY}px)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14,
          }}>
            <div style={{ width: 260, height: 30, borderRadius: 15, background: p < 0.5 ? G.card : G.line }} />
          </div>
          {/* 圆形光标点:悬停在按钮中心,按下缩一圈 */}
          <div style={{
            position: 'absolute', left: '50%', top: '50%',
            width: 96, height: 96, marginLeft: -48, marginTop: -48 + btnY,
            borderRadius: 48, background: G.ink, border: '8px solid #ffffff',
            boxSizing: 'border-box', transform: `scale(${cursorScale})`,
            boxShadow: '0 4px 14px rgba(0,0,0,0.3)',
          }} />
        </div>
      </CloseupStage>
    );
  }

  // ===== 特写二(35–44):开关从左拨到右 =====
  if (f < C3) {
    const t = f - C2;
    const p = interpolate(t, [4, 7], [0, 1], {
      easing: Easing.out(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    const trackW = 560; const trackH = 240; const knob = 192; const pad = 24;
    const knobX = pad + p * (trackW - knob - pad * 2); // 左 → 右
    const trackBg = p < 0.5 ? G.mid : G.ink;
    return (
      <CloseupStage>
        <div style={{
          position: 'relative', width: trackW, height: trackH, borderRadius: trackH / 2,
          background: trackBg, boxSizing: 'border-box',
        }}>
          <div style={{
            position: 'absolute', top: pad, left: knobX,
            width: knob, height: knob, borderRadius: knob / 2, background: G.card,
            boxShadow: '0 6px 18px rgba(0,0,0,0.35)',
          }} />
        </div>
      </CloseupStage>
    );
  }

  // ===== 特写三(45–54):大数字翻牌 0 → 1(rotateX) =====
  if (f < WHIP) {
    const t = f - C3;
    const p = interpolate(t, [4, 7], [0, 1], {
      easing: Easing.inOut(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    const showOne = p >= 0.5;
    const angle = showOne ? (1 - p) * 2 * 90 : -p * 2 * 90; // 0→-90 折走,90→0 翻入
    const digit = showOne ? '1' : '0';
    return (
      <CloseupStage>
        <div style={{ perspective: 1200 }}>
          <div style={{
            width: 440, height: 560, borderRadius: 32, background: G.ink,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transform: `rotateX(${angle}deg)`, backfaceVisibility: 'hidden',
            boxShadow: '0 8px 28px rgba(0,0,0,0.25)',
          }}>
            <div style={{
              fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
              fontSize: 420, color: '#ffffff', lineHeight: 1,
            }}>
              {digit}
            </div>
          </div>
        </div>
      </CloseupStage>
    );
  }

  // ===== 帧 55 起:甩回全景 + 结果卡片亮起 =====
  const t = f - WHIP;
  // whip:6f 从右侧 900px 高速滑入,poly(5) out 急减速;t≥6 恒为 0(真静止)
  const whipX = t >= 6 ? 0 : interpolate(t, [0, 6], [900, 0], {
    easing: Easing.out(Easing.poly(5)), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const speeding = t < 4; // 高速段:3 层错帧副本模拟模糊感

  // 结果卡片:泛光 57–84 缓升后恒定(帧 84 起真静止);弹一下 57–64 后恒为 1
  const glow = interpolate(f, [57, 84], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const pop = f >= 64 ? 1 : interpolate(f, [57, 60, 64], [1, 1.07, 1], {
    easing: Easing.out(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const dash = (x: number, opacity: number, key: string) => (
    <div key={key} style={{ position: 'absolute', left: 0, top: 0, transform: `translateX(${x}px)`, opacity }}>
      <FakeDashboard variant="A" />
    </div>
  );

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, overflow: 'hidden', position: 'relative' }}>
      {speeding && dash(whipX + 220, 0.18, 'echo2')}
      {speeding && dash(whipX + 110, 0.35, 'echo1')}
      {dash(whipX, 1, 'main')}
      {/* 结果卡片提亮泛光 */}
      <div style={{
        position: 'absolute',
        left: RESULT.left, top: RESULT.top, width: RESULT.w, height: RESULT.h,
        transform: `translateX(${whipX}px) scale(${pop})`,
        borderRadius: 14, boxSizing: 'border-box',
        background: `rgba(255,255,255,${0.72 * glow})`,
        border: `5px solid rgba(47,47,47,${glow})`,
        boxShadow: `0 0 ${70 * glow}px rgba(255,255,255,${0.95 * glow}), 0 0 ${26 * glow}px rgba(47,47,47,${0.28 * glow})`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        opacity: glow,
      }}>
        <div style={{
          fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
          fontSize: 260, color: G.ink, lineHeight: 1,
        }}>
          1
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

