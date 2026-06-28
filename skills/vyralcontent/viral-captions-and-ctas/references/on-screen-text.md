# On-screen text

Roughly 85% of social video is watched on mute. If the on-screen text
doesn't carry the story, the video doesn't exist for most of the feed.
Burned-in captions also outperform on completion: captioned videos tend
to see substantially higher watch-through than uncaptioned, and a real
slice of mute viewers turn the sound on because the captions pulled
them in.

This is the in-video text layer. For the written caption that sits
beside the video, see `caption-craft.md`.

## Burn it in. Do not trust auto-captions

Burned-in captions are hardcoded into the video file. Platform
auto-captions are an overlay that only shows when the viewer has them
toggled on. Default to burned-in for three reasons:

- They survive reposts, screenshots, downloads, and re-uploads.
- You control font, weight, color, size, position, timing.
- They show by default, on mute, to everyone.

Auto-captions have their place as an accessibility fallback for viewers
who toggled them on. They are not the main surface. TikTok's native
auto-caption runs in the high-80s for accuracy and gives you no
styling control.

## The headline + body pattern

The dominant high-performing layout:

- One **large, static text block** at the top: the hook line or the
  topic claim. This is the line the OCR reads first and the line the
  muted viewer reads in the first frame.
- **Body captions** built up word-by-word at the bottom or center as
  the voiceover speaks. These carry the spoken transcript.

The headline does the SEO and the scroll-stop. The body keeps the muted
viewer following the argument.

## The karaoke pattern

Caption text appears word-by-word or phrase-by-phrase **in sync with
the audio**, not as a static block of the whole sentence. Words
highlight, scale up, or change color as they're spoken.

- Karaoke tends to be the highest-engagement subtitle style on TikTok.
- Reels skews slightly more polished: bold centered blocks, boxed
  panels, less aggressive pop.
- Shorts splits the difference and tolerates either.

Karaoke is also a pacing tool. Words appearing on beat keep the eye
hooked the same way the cuts do.

## Safe zones

The area the platform UI does **not** cover. Critical text outside
these zones gets eaten by buttons, captions, music tickers, and
profile pictures.

### TikTok (9:16, 1080x1920)

- Top: leave about 130px clear for the Following / For You tabs and
  the search affordance.
- Bottom: leave 440 to 484px clear for the caption, username, and
  music ticker.
- Left: 60px margin.
- Right: 120px for the action rail (like, comment, share, profile).
- The vertical center is the only universally safe zone for hook text.

### Instagram Reels

- Same UI footprint as TikTok in practice.
- Keep critical text out of the bottom roughly 600px and the right
  roughly 150px.

### YouTube Shorts

- Keep critical text out of the bottom roughly 30% of the frame: title,
  description preview, like/dislike, comments rail all live there.

## Font, color, contrast

- **Weight:** bold (700+) is meaningfully more readable on mobile than
  thin weights. Default to bold for body captions, heavier for
  headlines.
- **Color:** white with a black outline (or the inverse) is the default
  that works across roughly 90% of content. High contrast against the
  background beats clever color choices.
- **Family:** sans-serif geometric fonts dominate. Montserrat Bold,
  TikTok Sans, Futura Bold, Archivo Black are common picks. TikTok Sans
  is open-source and matches the app's native UI if you want the
  in-app feel.
- **Size:** body captions in the 22 to 28pt range with high contrast
  against the background is the readability sweet spot. Headlines
  larger.
- **Avoid:** thin weights, low-contrast pastels, decorative scripts,
  tight letterspacing. They look fine on a desktop preview and
  disappear on a phone.

## Pace the text the way you'd pace the cuts

- A new word or phrase on screen every beat keeps the eye engaged the
  same way a shot change does.
- If the voiceover pauses for emphasis, the text can hold for a beat
  longer, then resume.
- Avoid dumping a long sentence on screen all at once. The viewer
  reads it faster than the voiceover finishes, then looks away.

## Practical defaults

- Headline at top, 5 to 8 words, large bold sans-serif, in the safe
  zone.
- Body captions karaoke-built, white with black outline, 22 to 28pt,
  centered or bottom-center but above the platform caption.
- Same topic words as the spoken hook and the written caption (the
  three-surface SEO play; see `caption-craft.md`).
- Do not repeat the headline as the first line of body captions. The
  body picks up where the headline left off.
