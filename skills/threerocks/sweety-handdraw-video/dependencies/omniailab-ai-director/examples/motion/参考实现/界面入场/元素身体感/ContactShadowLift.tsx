// ---
// name: omniailab-motion-demo-contact-shadow-lift
// description: contact-shadow-lift｜接触阴影离面抬升
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// contact-shadow-lift｜接触阴影离面抬升
// 浅底上一排 3 张卡，逐张被"点名"抬起：卡 translateY(-28px)+scale(1.08)，
// 其正下方独立椭圆阴影同步放大变淡——纸片离桌感；落回时阴影收紧变实，
// 落地 2f 卡壳 scale 0.99 微压。三张依次各来一遍。收尾真静止 ≥35f。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, Card } from '../../_fixtures/Fixtures';

const outCubic = Easing.out(Easing.cubic);
const inCubic = Easing.in(Easing.cubic);

// 每张卡的局部时间轴（局部帧 t）：
// [0,10)   抬起  out-cubic
// [10,28)  悬停 18f
// [28,36)  落回  in-cubic
// [36,38)  落地卡壳 scale 0.99
// [38,43)  回弹 0.99→1.0 out-cubic
// t<0 或 t>=43 完全静止（rest 态）
const LIFT_Y = -28; // 原案 -8 → 加码 -20 → QA 保险再到 -28
const LIFT_S = 1.08;

const cardMotion = (t: number) => {
  const y = interpolate(t, [0, 10], [0, LIFT_Y], {
    easing: outCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }) + interpolate(t, [28, 36], [0, -LIFT_Y], {
    easing: inCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  let s: number;
  if (t < 28) {
    s = interpolate(t, [0, 10], [1, LIFT_S], {
      easing: outCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
  } else if (t < 38) {
    s = interpolate(t, [28, 36], [LIFT_S, 0.99], {
      easing: inCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
  } else {
    s = interpolate(t, [38, 43], [0.99, 1], {
      easing: outCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
  }

  // 抬升进度 0（贴桌）→1（悬空），驱动阴影
  const lift = interpolate(t, [0, 10], [0, 1], {
    easing: outCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }) - interpolate(t, [28, 36], [0, 1], {
    easing: inCubic, extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return { y, s, lift };
};

const CARD_W = 360;
const CARD_H = 220;
const GAP = 120;
const STARTS = [2, 42, 82]; // 三张卡依次点名，间隔 40f；末次动画止于 f125，留 35f 真静止

export const ContactShadowLift: React.FC = () => {
  const frame = useCurrentFrame();
  const rowW = CARD_W * 3 + GAP * 2;
  const left0 = (1920 - rowW) / 2;
  const top = (1080 - CARD_H) / 2 - 20;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      {/* 假 dashboard 式顶栏，给浅底一点场景感 */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 84, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', padding: '0 48px', gap: 24, boxSizing: 'border-box' }}>
        <div style={{ width: 40, height: 40, borderRadius: 10, background: G.side }} />
        <div style={{ height: 18, width: 220, background: G.bar, borderRadius: 9 }} />
        <div style={{ marginLeft: 'auto', width: 36, height: 36, borderRadius: 18, background: G.mid }} />
      </div>

      {[0, 1, 2].map((i) => {
        const t = frame - STARTS[i];
        const { y, s, lift } = cardMotion(t);
        const x = left0 + i * (CARD_W + GAP);

        // 独立接触阴影（不是 box-shadow）：卡正下方椭圆径向渐变
        const shScale = 1 + 0.72 * lift;     // 1.0 → 1.72（对比再拉大）
        const shOpacity = 0.55 - 0.37 * lift; // 0.55 → 0.18
        const shW = CARD_W * 0.88;
        const shH = 44;

        return (
          <React.Fragment key={i}>
            <div
              style={{
                position: 'absolute',
                left: x + (CARD_W - shW) / 2,
                top: top + CARD_H - shH / 2 - 4,
                width: shW,
                height: shH,
                borderRadius: '50%',
                background: 'radial-gradient(ellipse at center, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.45) 42%, rgba(0,0,0,0) 72%)',
                transform: `scale(${shScale})`,
                opacity: shOpacity,
              }}
            />
            <Card
              w={CARD_W}
              h={CARD_H}
              seed={i + 2}
              style={{
                position: 'absolute',
                left: x,
                top,
                boxShadow: 'none',
                transform: `translateY(${y}px) scale(${s})`,
              }}
            />
          </React.Fragment>
        );
      })}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

