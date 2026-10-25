# Published findings

Every number this skill states, where it came from, and what it does not prove. Read this before defending a threshold to a user, changing one, or quoting one in a report.

## Sourced

### Guo, Kim & Rubin - _How Video Production Affects Student Engagement_ (ACM Learning@Scale 2014)

6,902,358 video-watching sessions across four Fall 2012 edX courses; the largest published study of instructional-video engagement. Every figure below is the paper's own.

| Finding             | The paper's own words or figures                                                                                                                                                                                                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Length              | "Median engagement time is at most 6 minutes, regardless of total video length"; students "often make it less than halfway through videos longer than 9 minutes"                                                                                                                                               |
| Shortest bucket     | 0-3 min had the highest engagement and least variance - 75% of sessions ran past three quarters of the video                                                                                                                                                                                                   |
| Downstream action   | Share of sessions followed by a problem attempt, by length bucket: 56%, 48%, 43%, 41%, 31%                                                                                                                                                                                                                     |
| Planning            | "Invest heavily in pre-production lesson planning to segment videos into chunks shorter than 6 minutes." Producers interviewed believed pre-production had the largest impact of any phase; the planned course beat the spliced-lecture course 55% vs 41% on follow-on problem attempts (one course pair only) |
| Procedural video    | Tutorials were watched 2-3 minutes on average _regardless of length_, re-watched more often, and paused more - and more selectively, at what look like step boundaries                                                                                                                                         |
| Format              | Khan-style continuous drawing held 1.5-2x the normalized engagement of "PowerPoint slide and code screencast tutorials"; 40% vs 31% follow-on problem attempts                                                                                                                                                 |
| Face                | "Videos that intersperse an instructor's talking head with slides are more engaging than slides alone", with a recommendation to edit the head in at opportune times; no benefit found from studio production values                                                                                           |
| Speaking rate       | Corpus range 48-254 wpm (mean 156, sd 31). Within a length range engagement usually rose, up to 2x, with rate. For 6-12 minute videos engagement _dipped_ in the 145-165 wpm quintile                                                                                                                          |
| The authors' caveat | "Speaking rate is merely a surface feature that correlates with enthusiasm… our recommendation is not to force instructors to speak faster"                                                                                                                                                                    |

Limitations the authors state:

- Retrospective log study, not an experiment.
- Four math/science MOOCs.
- Self-selected early-adopter learners.
- Watch time is a proxy for engagement.
- Engagement is not learning.

The widely repeated "100% / 50% / 20% engagement" table is a secondary rendering of their normalized boxplot - prefer the absolute statements above.

### Wistia, 2026 State of Video

Over 13 million hosted videos.

- Videos under one minute average a 52% engagement rate.
- Viewers watch over half of educational and tutorial videos in the 1-5 minute range.
- A further drop appears past 30 minutes.

A business-video corpus rather than a teaching one, which is why it is used here only as a same-direction cross-check.

### Platform retention reporting

The dominant video platform's audience-retention report names four moment types - intro (share still watching **after the first 30 seconds**), dips, spikes, top moments. The 30-second intro window is a measurement boundary defined by the platform, not a stylistic preference. Re-check the current definitions if you can browse the web.

### Platform chapter rules

- First timestamp `00:00`.
- At least three timestamps.
- Each chapter 10 seconds or longer.
- Ascending order.

Platform-documented rules, and the platform revises them - re-check before publishing.

### W3C WAI - media accessibility

WCAG requires captions for prerecorded synchronized media at Level A. W3C recommends **integrated description** for new video: write the visual information into the main narration, then verify the audio alone covers everything relevant. A separate description track is the retrofit for material that already exists.

### Nielsen Norman Group - video usability

Viewers check a video's duration almost immediately, and an introduction beyond roughly five seconds already reads as long. Applies to ceremony, not to substance.

### egghead instructor guide (`howtoegghead.com`)

Published production standard for short technical screencasts:

- "Record in short, high-quality chunks, one thought at a time."
- "Between each, take a pause."
- "Think of your lesson as a series of paragraphs that take 20 seconds to record" - the pause makes the ripple-delete point visible in the waveform.

Audio-first, video-first and all-at-once recording orders are all treated as valid. Capture profile: fullscreen 16:9, 1280x720 HiDPI, large fonts, high-contrast themes.

### John Lindquist, for egghead.io - _Recording a Great Coding Screencast_

Lindquist writes that a screencast is recorded and cut in small pieces rather than filmed as one continuous take: "We strongly encourage recording in small 'takes' rather than trying to record the entire lesson. A take can be as small as a single sentence." Editing happens right after recording, while the mistakes are still fresh: "I strongly recommend editing your lesson immediately after you record so all the mistakes you made are fresh in your mind." On keeping narration tied to the screen: "Your words should reflect what's happening on the screen. Don't talk without showing something and don't show something without talking." On not chasing a clean take: "This is NOT a conference presentation. You do NOT have to be 'perfect' or 'practiced'. You just need to edit out the mistakes. So relax, say stupid stuff, pause, do it again, then edit out the bad stuff later."

### Kevin Blanco, Appsmith - a named video role inside a DevRel team

Blanco's title is Senior DevRel Advocate and Video and Livestream Producer at Appsmith, and he owns the pipeline end to end rather than splitting it across a team. On planning: "I already have a structure that works for me... and then I start planning the different scenes." On editing his own footage: "I also do the post-production, you know, audio level quality, making sure that the levels are good, the video production itself, the lighting, and the coloring, the editing, the animations, the motion graphics, the transitions, all of that I do in DaVinci Resolve." He puts a 20-30 minute video at "four days for everything, you know, writing the script," through shooting, at a stated cadence of "around 2 videos per week or maybe 1 video and live stream." One practitioner's account, not a survey of DevRel org structures, but it shows scripting, recording and editing sitting inside a single named role rather than split across specialists.

### Greg Baugues - _YouTube Based DevRel_ (DevRelCon New York 2025)

Baugues spent nine years on Twilio's developer evangelism team before building an independent YouTube channel: "I had the privilege of joining Twilio's developer evangelism team in 2014," and "I got to serve at Twilio, for nine years." His own pipeline is also one person carrying every stage, and editing is the largest cost in it: "This is probably twelve, thirteen hours of editing into this interview video," weighted toward the opening: "it's really important to invest as much editing in that first minute as possible and make that as sharp and as crisp as possible." His publishing goal slips in practice: "My publishing schedule is my goal is to ship one video a week. Candidly, I don't get there. Typically, I fall more like every ten days."

## This skill's own baselines - not industry standards

These are self-set. They are defensible, they are not measured, and a user may move them.

| Baseline                              | Value                                            | Why it was set here                                                                                                                            |
| ------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Segment ceiling                       | ~6 minutes per segment                           | Mirrors the sourced 6-minute engagement ceiling at the segment level rather than the video level, so a long video still hits it per chapter    |
| Runtime bands per shape               | The Video shapes table                           | Assembled from the sourced length evidence plus what each format has to accomplish; the shapes themselves are this skill's own categories      |
| Production-effort and value orderings | The four axis lines under the Video shapes table | Craft judgement about what each shape costs to make and what it returns, with runtime deliberately not used as the effort proxy                |
| Legibility floors                     | Terminal 24pt, editor 20pt                       | Chosen to survive phone-sized playback; egghead's published standard says "large fonts" rather than point sizes, so these numbers are self-set |
| Seven pass-threshold criteria         | The Pass threshold section                       | An editorial gate written for this skill, and movable once a user has their own retention data                                                 |
| Ceremony budget                       | ~5 seconds                                       | Rounded from the NN/g finding, which reports a perception threshold, not a cutoff                                                              |
| Beat length                           | One thought, ~20 seconds of narration            | Adopted from egghead's recording rule, applied to the script rather than the take                                                              |
| Retention-risk grading                | Three levels                                     | Three bands so a review ranks its fixes instead of listing them; the bands are this skill's own                                                |

## How to talk about these numbers

State the source when you cite a sourced number, and say "this skill's baseline" when you cite one of the others. A user who is told a self-set number is an industry standard will defend it in a review against someone who checks.
