// ---
// name: omniailab-motion-template-main
// description: 成片工程模板——工程/src/demo/Main.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { SceneOpen } from './live/SceneOpen';
import { SceneFlyIn } from './live/SceneFlyIn';
import { SceneDetail } from './live/SceneDetail';
import { ScenePapers } from './live/ScenePapers';
import { SceneWbr } from './live/SceneWbr';
import { PaperTitleCard } from './PaperTitleCard';
import { SceneOutroLive } from './live/SceneOutroLive';
import { FlashCut } from './FlashCut';
import { Caption } from './Caption';

// ~36.2s @ 30fps — paper-and-ink morning reading room (10 shots). Both wordmark
// moments (brand open, outro sign-off) hold a full second once fully on.
export const AIFL_SHOTS = {
  morning: { from: 0, duration: 220 },  // 0–7.3s  brand ~46f + 30f hold + 138f macro
  card1: { from: 220, duration: 55 },   // 7.3–9.2s "All your team's research, one place to go."
  table: { from: 275, duration: 190 },  // 9.2–15.5s pile close-up → deal → scroll → search → filter → click
  macro: { from: 465, duration: 100 },  // 15.5–18.8s macro card detail, rows reveal
  card2: { from: 565, duration: 55 },   // 18.8–20.7s "Paper Radar, tailored for your morning reading."
  chart: { from: 620, duration: 105 },  // 20.7–24.2s papers stack radar
  cardWbr: { from: 725, duration: 50 }, // 24.2–25.8s "Every project, linked to your weekly report."
  wbr: { from: 775, duration: 110 },    // 25.8–29.5s weekly report / collaborative write
  card3: { from: 885, duration: 55 },   // 29.5–31.3s "The whole team, on the same page."
  outro: { from: 940, duration: 145 },  // 31.3–36.2s defocus + letterpress sign-off (+1s hold)
} as const; // sum = 1085

export const AIFL_TOTAL = 1085;

// bottom-strip narration over the live shots (absolute frames; outro stays clean)
const CAPTIONS = [
  { from: 90, duration: 40, text: 'TEN LIVE PROJECTS · FOUR RESEARCHERS' },
  // (the hero-card hover annotation lives inside SceneOpen as a 3D floating note)
  { from: 318, duration: 44, text: 'NEW WORK LANDS ALL WEEK' },
  { from: 395, duration: 55, text: 'SEARCH · FILTER · OPEN' },
  { from: 477, duration: 68, text: 'EVERY QUESTION, TRACKED TO ITS EXPERIMENTS' },
  { from: 633, duration: 72, text: 'THE DAILY PAPER RADAR' },
  { from: 789, duration: 78, text: 'FOUR VOICES, ONE WEEKLY BRIEF' },
] as const;

// sound design pinned to animation beats (absolute frames, Mixkit license).
// Classic product-promo vocabulary: whooshes on camera moves, cinematic
// impacts on landings, a riser into the finale, sparkle on the reveal.
const SFX: { from: number; src: string; volume: number }[] = [
  // brand open: soft transition as the lockup lands, whoosh into the console
  // hero card: whoosh up on the pop, sparkle on the beam scan, impact reseat
  { from: 127, src: 'whoosh-big.mp3', volume: 0.5 },
  { from: 141, src: 'sparkle.mp3', volume: 0.35 },
  // title cards ride a quick swoosh
  // deck shot: soft transition into the pile close-up, whoosh as the orbit
  // pulls back and dealing starts, fast whooshes as the deal accelerates,
  // then the scroll rest → big whoosh back up to the search bar
  { from: 308, src: 'whoosh-big.mp3', volume: 0.5 }, // pull-back + first deals
  { from: 388, src: 'whoosh-big.mp3', volume: 0.5 }, // swoosh back to header
  // typing (slower now, 3f/char) + a breath + filter + click
  { from: 401, src: 'keyboard.mp3', volume: 0.4 }, // trimmed by sequence length
  // detail rows embed with one cinematic transition sweep
  // papers stack: soft transition, camera-click as the counter settles
  // wbr: the page "writes itself" over live keyboard typing, then past weeks
  // pop into the left rail one by one (a pop per landing)
  { from: 781, src: 'keyboard.mp3', volume: 0.34 }, // trimmed to the writing reveals
  { from: 840, src: 'pop.mp3', volume: 0.4 },
  { from: 845, src: 'pop.mp3', volume: 0.37 },
  { from: 850, src: 'pop.mp3', volume: 0.34 },
  { from: 855, src: 'pop.mp3', volume: 0.31 },
  { from: 860, src: 'pop.mp3', volume: 0.28 },
  { from: 865, src: 'pop.mp3', volume: 0.25 },
  // outro: riser under the assembly, big impact when the wordmark stamps
  { from: 945, src: 'riser-cine.mp3', volume: 0.5 },
  { from: 980, src: 'impact-cine.mp3', volume: 0.55 },
  { from: 1005, src: 'sparkle.mp3', volume: 0.3 }, // rule + tagline glint
];

export const AiflMain: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#f2eee6' }}>
      {/* beat-pinned promo sound effects (no music bed — SFX only) */}
      {SFX.map((s, i) => (
        <Sequence
          key={`sfx-${i}`}
          from={s.from}
          // keyboard: 24f for the short search-box typing, 44f under the wbr
          // writing reveals; everything else plays out (≤3s assets)
          durationInFrames={s.src === 'keyboard.mp3' ? (s.from > 700 ? 44 : 24) : 90}
        >
          <Audio src={staticFile(`audio/${s.src}`)} volume={s.volume} />
        </Sequence>
      ))}
      <Sequence from={AIFL_SHOTS.morning.from} durationInFrames={AIFL_SHOTS.morning.duration}>
        <SceneOpen />
      </Sequence>
      <Sequence from={AIFL_SHOTS.card1.from} durationInFrames={AIFL_SHOTS.card1.duration}>
        <PaperTitleCard
          duration={AIFL_SHOTS.card1.duration}
          words={[{ text: 'All' }, { text: 'your' }, { text: 'team’s' }, { text: 'research,' }, { text: 'one', accent: true }, { text: 'place' }, { text: 'to' }, { text: 'go.' }]}
        />
      </Sequence>
      <Sequence from={AIFL_SHOTS.table.from} durationInFrames={AIFL_SHOTS.table.duration}>
        <SceneFlyIn />
      </Sequence>
      <Sequence from={AIFL_SHOTS.macro.from} durationInFrames={AIFL_SHOTS.macro.duration}>
        <SceneDetail />
      </Sequence>
      <Sequence from={AIFL_SHOTS.card2.from} durationInFrames={AIFL_SHOTS.card2.duration}>
        <PaperTitleCard
          duration={AIFL_SHOTS.card2.duration}
          words={[{ text: 'Paper' }, { text: 'Radar,', accent: true }, { text: 'tailored' }, { text: 'for' }, { text: 'your' }, { text: 'morning' }, { text: 'reading.' }]}
          sub="of 31 fetched today"
          subDigits="5"
        />
      </Sequence>
      <Sequence from={AIFL_SHOTS.chart.from} durationInFrames={AIFL_SHOTS.chart.duration}>
        <ScenePapers />
      </Sequence>
      <Sequence from={AIFL_SHOTS.cardWbr.from} durationInFrames={AIFL_SHOTS.cardWbr.duration}>
        <PaperTitleCard
          duration={AIFL_SHOTS.cardWbr.duration}
          words={[{ text: 'Every' }, { text: 'project,' }, { text: 'linked', accent: true }, { text: 'to' }, { text: 'your' }, { text: 'weekly' }, { text: 'report.' }]}
        />
      </Sequence>
      <Sequence from={AIFL_SHOTS.wbr.from} durationInFrames={AIFL_SHOTS.wbr.duration}>
        <SceneWbr />
      </Sequence>
      <Sequence from={AIFL_SHOTS.card3.from} durationInFrames={AIFL_SHOTS.card3.duration}>
        <PaperTitleCard
          duration={AIFL_SHOTS.card3.duration}
          words={[{ text: 'The' }, { text: 'whole' }, { text: 'team,' }, { text: 'on' }, { text: 'the' }, { text: 'same', accent: true }, { text: 'page.' }]}
        />
      </Sequence>
      <Sequence from={AIFL_SHOTS.outro.from} durationInFrames={AIFL_SHOTS.outro.duration}>
        <SceneOutroLive />
      </Sequence>
      {/* narration captions over the live shots (under the flash cuts) */}
      {CAPTIONS.map((c) => (
        <Sequence key={c.from} from={c.from} durationInFrames={c.duration}>
          <Caption text={c.text} duration={c.duration} />
        </Sequence>
      ))}
      {/* warm flash cuts straddling scene changes */}
      {[AIFL_SHOTS.table.from, AIFL_SHOTS.macro.from, AIFL_SHOTS.chart.from, AIFL_SHOTS.wbr.from].map((cut) => (
        <Sequence key={cut} from={cut - 5} durationInFrames={10}>
          <FlashCut duration={10} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

