// ---
// name: omniailab-motion-demo-pop-burst-confirm
// description: 爆花确认（pop-burst-confirm）——确认时刻的三连爆
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 爆花确认（pop-burst-confirm）——确认时刻的三连爆
// 半屏大对勾 icon（圆底+勾）：先缩 0.6x 蓄力 3f → 弹 1.35x 过冲 → 落回 1x，
// 释放帧同帧中心射出 10 根短线粒子（径向飞出后消失）+ 一圈描边圆环从
// icon 边缘扩到 2.5 倍直径淡出；随后 "Deployed" 小标签弹出。
// 节拍：0–20 静置（空心圆待确认）→ 20–23 缩 0.6x → 23–27 蓄力 3f →
// 27 释放（勾画出+粒子+圆环）→ 27–44 过冲落回 → 40–50 标签弹出 → 55 后真静止 65f。
// 帧确定，无随机源（粒子角度抖动用 sin 散列）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const AMBER = '#b45309';
const POP = 27; // 释放帧
const DUR = 120;

export const PopBurstConfirm: React.FC = () => {
  const f = useCurrentFrame();

  // icon 缩放：蓄力→过冲→落回
  const scale = (() => {
    if (f <= 20) return 1;
    if (f <= 23)
      return interpolate(f, [20, 23], [1, 0.6], { easing: Easing.in(Easing.quad) });
    if (f <= POP) return 0.6;
    if (f <= 33)
      return interpolate(f, [POP, 33], [0.6, 1.35], { easing: Easing.out(Easing.cubic) });
    return interpolate(f, [33, 44], [1.35, 1], {
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.back(2)),
    });
  })();

  // 对勾：释放帧起 8f 内画出（dashoffset 滑窗）
  const checkT = interpolate(f, [POP, POP + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // 粒子：释放帧起 14f 径向飞出（幅度加码到 190px 保半屏可感）
  const pt = interpolate(f, [POP, POP + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const pDist = 210 + 190 * Easing.out(Easing.cubic)(pt);
  const pLen = 46 * (1 - pt);

  // 圆环：释放帧起 20f 从 icon 边缘扩到 2.5 倍直径淡出
  const rt = interpolate(f, [POP, POP + 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ringR = 200 + 300 * Easing.out(Easing.cubic)(rt);
  const ringO = 0.85 * (1 - rt);
  const ringW = 16 - 12 * rt;

  // 标签：40f 弹出（back 超调）
  const tagT = interpolate(f, [40, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.back(2.6)),
  });

  const CX = 960;
  const CY = 470;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      {/* 扩散圆环（不随 icon 缩放） */}
      {rt > 0 && rt < 1 && (
        <svg
          width={1400}
          height={1400}
          style={{ position: 'absolute', left: CX - 700, top: CY - 700 }}
        >
          <circle cx={700} cy={700} r={ringR} fill="none" stroke={AMBER} strokeWidth={ringW} opacity={ringO} />
        </svg>
      )}

      {/* 粒子：10 根短线径向飞出，角度带 sin 散列微抖 */}
      {pt > 0 && pt < 1 && (
        <svg
          width={1400}
          height={1400}
          style={{ position: 'absolute', left: CX - 700, top: CY - 700 }}
        >
          {Array.from({ length: 10 }).map((_, i) => {
            const ang = ((i * 36 + 9 * Math.sin(i * 7.31)) * Math.PI) / 180;
            const x1 = 700 + Math.cos(ang) * pDist;
            const y1 = 700 + Math.sin(ang) * pDist;
            const x2 = 700 + Math.cos(ang) * (pDist + pLen);
            const y2 = 700 + Math.sin(ang) * (pDist + pLen);
            return (
              <line
                key={i}
                x1={x1} y1={y1} x2={x2} y2={y2}
                stroke={i % 5 < 2 ? AMBER : G.ink}
                strokeWidth={12}
                strokeLinecap="round"
                opacity={1 - pt}
              />
            );
          })}
        </svg>
      )}

      {/* 主体 icon：圆底 + 对勾（半屏特写 ~480px） */}
      <svg
        width={480}
        height={480}
        viewBox="0 0 480 480"
        style={{
          position: 'absolute',
          left: CX - 240,
          top: CY - 240,
          transform: `scale(${scale})`,
          transformOrigin: '50% 50%',
        }}
      >
        <circle cx={240} cy={240} r={190} fill={G.card} stroke={G.ink} strokeWidth={22} />
        {checkT > 0 && (
          <path
            d="M 150 245 L 215 310 L 340 175"
            fill="none"
            stroke={AMBER}
            strokeWidth={34}
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - checkT}
          />
        )}
      </svg>

      {/* Deployed 小标签 */}
      {tagT > 0 && (
        <div
          style={{
            position: 'absolute',
            left: CX - 130,
            top: CY + 300,
            width: 260,
            transform: `scale(${tagT})`,
            transformOrigin: '50% 0%',
            padding: '16px 0',
            borderRadius: 40,
            background: G.ink,
            color: '#ffffff',
            textAlign: 'center',
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 800,
            fontSize: 40,
            letterSpacing: 1,
          }}
        >
          Deployed
        </div>
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

