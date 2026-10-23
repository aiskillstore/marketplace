import { sealVisualTrack } from "@hypit/composition";
import type { FrameSpan } from "@hypit/composition";
import type { FontArtifactRef } from "@hypit/media";
import type { Timeline } from "@hypit/timeline";
import { VISUAL_IR_V1 } from "@hypit/composition";

// The caller supplies its projected Window, resolved Frame and selected font faces.
export function renderCard(input: {
  id: string;
  timeline: Timeline;
  span: FrameSpan;
  frame: { x: number; y: number; width: number; height: number };
  text: string;
  fonts: readonly FontArtifactRef[];
  color: string;
  textColor: string;
  size: number;
  padding: number;
  layer: number;
  entranceFrames: number;
}) {
  const root = `${input.id}-box`;
  const length = input.span.endFrameExclusive - input.span.startFrame;
  const entranceEnd = Math.min(input.entranceFrames, length - 1);
  return sealVisualTrack({
    id: input.id,
    timelineId: input.timeline.id,
    visualIr: VISUAL_IR_V1,
    presents: [{
      id: `${input.id}-present`,
      subjectId: input.id,
      span: input.span,
      order: 0,
      z: input.layer,
      elements: [{
        kind: "box", id: root, order: 0,
        style: [
          { name: "position", value: "absolute" },
          { name: "left", value: input.frame.x },
          { name: "top", value: input.frame.y },
          { name: "width", value: input.frame.width },
          { name: "height", value: input.frame.height },
          { name: "background-color", value: input.color },
        ],
        ...(entranceEnd > 0 ? { animation: { keyframes: [
          { atFrame: 0, style: [{ name: "opacity", value: 0 }] },
          { atFrame: entranceEnd, style: [{ name: "opacity", value: 1 }] },
        ] } } : {}),
      }, {
        kind: "text", id: `${input.id}-text`, parent: root, order: 1,
        text: input.text, fonts: input.fonts,
        style: [
          { name: "position", value: "absolute" },
          { name: "left", value: input.padding },
          { name: "top", value: input.padding },
          { name: "width", value: input.frame.width - 2 * input.padding },
          { name: "color", value: input.textColor },
          { name: "font-size", value: input.size },
        ],
      }],
    }],
  });
}
