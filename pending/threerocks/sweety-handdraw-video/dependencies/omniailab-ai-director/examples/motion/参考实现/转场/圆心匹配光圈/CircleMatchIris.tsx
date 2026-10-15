// ---
// name: omniailab-motion-demo-circle-match-iris
// description: 圆心匹配光圈切(match-cut × iris-reveal 组合):
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 圆心匹配光圈切(match-cut × iris-reveal 组合):
// 帧 0–30:景 A(列表面板)hold,第 2 行 44px 圆形头像做两次脉冲 + 扩散光环提示"看这里";
// 帧 30–75:景 B 以 clip-path: circle(r at CX CY) 从 22px 炸开到 2100px(Easing.inOut(cubic)),
//   景 B 是深色圆环图表页,圆环半径同步从 22px 长到 170px——在光圈吃满全屏前就"接住"头像的圆;
// 帧 45–100:圆环描边 sweep 到 78%,中央大数字随之浮现计数;帧 100–140 全属性静止收尾(≥35f)。
// 命门:两景的圆严格同心——CX/CY 写死为 FakeDashboard B 第 2 行头像的屏幕坐标常量。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

// FakeDashboard variant B 第 2 行左侧 44px 头像的圆心(手算自 fixture 布局)
const CX = 308;
const CY = 384.8;

export const CircleMatchIris: React.FC = () => {
  const f = useCurrentFrame();

  // ---- 景 A:头像脉冲(帧 0–30,两次呼吸) ----
  const pulseT = Math.min(f, 30) / 30;
  const scale = f < 30 ? 1 + 0.45 * Math.abs(Math.sin(pulseT * Math.PI * 2)) : 1;
  // 两道扩散光环
  const waves = [0, 14].map((start) => {
    const p = interpolate(f, [start, start + 16], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    return { r: 22 + p * 40, o: f < start + 16 ? 0.85 * (1 - p) : 0 };
  });

  // ---- 光圈:景 B 从同一圆心炸开 ----
  const irisR = interpolate(f, [30, 75], [22, 2100], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // ---- 景 B 圆环:半径从 22 长到 170,"接住"头像的圆 ----
  const ringR = interpolate(f, [30, 70], [22, 170], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const ringW = interpolate(f, [30, 70], [12, 40], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  // 描边 sweep 到 78%
  const sweep = interpolate(f, [45, 100], [0, 0.78], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const circ = 2 * Math.PI * ringR;
  const num = Math.round(sweep * 100);
  const numOpacity = interpolate(f, [68, 88], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const furnitureOpacity = interpolate(f, [60, 85], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <div style={{ width: 1920, height: 1080, position: 'relative', overflow: 'hidden', background: G.bg }}>
      {/* ===== 景 A:列表面板 ===== */}
      <FakeDashboard variant="B" />
      {/* 白色补丁盖住 fixture 自带的圆角方块,再叠真正的圆形头像 */}
      <div style={{ position: 'absolute', left: CX - 23, top: CY - 23, width: 46, height: 46, background: G.card }} />
      <div style={{
        position: 'absolute', left: CX - 22, top: CY - 22, width: 44, height: 44,
        borderRadius: 22, background: G.mid, border: `3px solid ${G.ink}`,
        boxSizing: 'border-box', transform: `scale(${scale})`,
      }} />
      {/* 脉冲扩散光环 */}
      <svg width={1920} height={1080} style={{ position: 'absolute', left: 0, top: 0 }}>
        {waves.map((w, i) => (
          <circle key={i} cx={CX} cy={CY} r={w.r} fill="none" stroke={G.ink} strokeWidth={4} opacity={w.o} />
        ))}
      </svg>

      {/* ===== 景 B:深色圆环图表页,从同一圆心以光圈长出 ===== */}
      {f >= 30 && (
        <div style={{
          position: 'absolute', left: 0, top: 0, width: 1920, height: 1080,
          background: G.ink,
          clipPath: `circle(${irisR}px at ${CX}px ${CY}px)`,
        }}>
          {/* 圆环 donut:圆心与头像严格同点 */}
          <svg width={1920} height={1080} style={{ position: 'absolute', left: 0, top: 0 }}>
            {/* 底轨 */}
            <circle cx={CX} cy={CY} r={ringR} fill="none" stroke="#5a5a58" strokeWidth={ringW} />
            {/* sweep 弧,从正上方起 */}
            <circle
              cx={CX} cy={CY} r={ringR} fill="none" stroke="#ececea"
              strokeWidth={ringW} strokeLinecap="round"
              strokeDasharray={`${sweep * circ} ${circ}`}
              transform={`rotate(-90 ${CX} ${CY})`}
            />
          </svg>
          {/* 中央大数字 */}
          <div style={{
            position: 'absolute', left: CX - 150, top: CY - 80, width: 300, height: 160,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            opacity: numOpacity,
          }}>
            <div style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 96, color: '#f2f2f0', letterSpacing: -2 }}>
              {num}%
            </div>
            <div style={{ marginTop: 6, height: 12, width: 130, background: '#6a6a68', borderRadius: 6 }} />
          </div>
          {/* 右侧页面家具:标题 + 统计条,证明这是一整页 */}
          <div style={{ position: 'absolute', left: 680, top: 260, opacity: furnitureOpacity, display: 'flex', flexDirection: 'column', gap: 30 }}>
            <div style={{ height: 34, width: 520, background: '#c2c2c0', borderRadius: 10 }} />
            <div style={{ height: 16, width: 780, background: '#5a5a58', borderRadius: 8 }} />
            <div style={{ height: 16, width: 640, background: '#5a5a58', borderRadius: 8 }} />
            <div style={{ height: 16, width: 700, background: '#5a5a58', borderRadius: 8 }} />
            <div style={{ display: 'flex', gap: 28, marginTop: 24 }}>
              {[0, 1, 2].map((i) => (
                <div key={i} style={{ width: 240, height: 150, background: '#454543', border: '2px solid #5a5a58', borderRadius: 14, padding: 20, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <div style={{ height: 12, width: `${55 + i * 12}%`, background: '#8f8f8d', borderRadius: 6 }} />
                  <div style={{ height: 30, width: '45%', background: '#c2c2c0', borderRadius: 8, marginTop: 'auto' }} />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

