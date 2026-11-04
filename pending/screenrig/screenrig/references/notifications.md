# Notifications: chat and pager channels, grouping, glass verdicts

## Slack, Teams, PagerDuty, Telegram

`notifications create` posts to a team's chat or pager the way it emails or
POSTs a signed webhook: the same conditions, hold, `--tag` scope, snooze and
mutes, one notice per outage and screen, and a recovery notice only after that
channel's own first notice went out.

| Flag | Credential the user supplies | Notes |
| --- | --- | --- |
| `--slack URL` | A Slack incoming webhook URL (`hooks.slack.com/services/...`) | Posts a Block Kit card |
| `--teams URL` | The URL of a Teams Workflows webhook (the "When a Teams webhook request is received" trigger) | Posts an Adaptive Card. Office 365 connector URLs are retired and refused |
| `--pagerduty KEY` | An Events API v2 routing key (32 characters) | Triggers one incident per outage and screen and resolves it on recovery; `crashing` triggers an incident a person resolves |
| `--telegram TOKEN --telegram-chat CHAT_ID` | A bot token and the chat id (`-1001234567890`) or `@channelname` | Posts an HTML message |

Each needs `--conditions`. Never put the credential on the command line where
the user's shell history keeps it: use `-` and pipe it in, as in
`printf '%s\n' "$URL" | screenrig notifications create --slack - --conditions screen_offline`.
The credential is sealed and never shown again; `notifications show ID` gives a
masked `destination_hint` (`https://hooks.slack.com/…/x9Zq`, or `…a1b2` for a key
or token) and, for Telegram, `telegram_chat_id`. Replace it with
`notifications update ID --destination -` (and `--telegram-chat ID`). A value of
the wrong shape is `notification_destination_rejected` (exit 8) and nothing is
created.

Prove the path with `notifications test ID`, then `notifications deliveries ID`:
a post is `succeeded` on a 2xx answer, otherwise it is retried for 24 hours and
`last_status` and `last_error` say why. A notification that fails for 72 hours is
disabled; fix the destination, then `notifications update ID --enable`. For
PagerDuty the test triggers an information event and resolves it at once, so no
incident stays open.

A recovered screen's message names the likely cause when it is known by then. A
restart of the device or the Player is; the screen's network or a screenRIG
interruption needs the Player's next health report (up to 15 minutes), so
`screen show` often has it before any message does.
Chat notices are free.

## Grouped notices

Email and the four chat channels say screens that fall together as one notice,
not one per screen: when three or more screens of a project go offline (or hit
the same condition) within five minutes and share a network address, location
name, hardware model, Player version or tag, the notice names what they share
and how many ("8 screens offline · network 203.0.113.7", then the first ten
names). Screens on three or more separate networks that fall together are one
notice that says how many screens on how many networks; it names no cause. A
screen that falls later with the same value joins the open group without a new notice, and
one notice says "All 8 screens on network ... are back online" when the last
one is back. `notifications deliveries ID` shows the grouped screens as
`skipped` with `last_error` `grouped` and a `group_id`; the notice that said the
group carries `group` (`id`, `attribute`, `value`, `count`). A signed webhook
still gets one notice per screen.

## Unsubscribe from email

Every alert and test email has an unsubscribe link for its own recipient, as the
Unsubscribe button of mail apps and as a footer link. Following it stops that
notification's email to that one person, without signing in; the others keep
getting mail, and the person stays in `recipients`. The page it opens has a
Resubscribe button. `notifications show ID` and `notifications list` say who
stopped (`unsubscribed`), and `notifications resubscribe ID --user USER_ID`
mails a person again. When every recipient has unsubscribed, a notice is
skipped as `no_recipients`. Opening the link only shows the page; never press
its button for the user, since that ends their alerts.

## Glass verdicts

screenRIG also checks what a screen shows, from the reports and screenshots it receives and never by asking the Player. A verdict appears in `screen show ID` (`data.glass`), in `alerts` and in `notifications`. Each check prefers missing a problem to raising a false one: no verdict means "fine or not judged", never "proven playing".

A stalled, blank or frozen screen that merely stops being checked (it went
offline, its display went off, a takeover began) closes its alert, but email,
Slack, Teams and Telegram send no recovery for it, because nothing showed it
recovering: its row is `skipped` with `last_error` `no_longer_judged`.
PagerDuty still resolves the incident.

### loop_stalled: the playlist stopped advancing

The screen is online, its display is on, its content is current and its Player reports nothing wrong, yet no image or video start has reached screenRIG for 1.5 times its loop's longest run between media starts (at least a minute) plus three minutes of reporting slack. That points to a hung renderer, a stalled decoder or a Player that stopped advancing. It says what `not_playing` (the Player reports an error), `content_stuck` (the update), `screen_offline` and `display_disconnected` cannot.

- Read it: `screen show ID` prints "Playlist stalled since ..." and `data.glass.playback` has `verdict` `stalled`, `since`, `last_media_start_at` and `threshold_s`. `alerts list` shows it as condition `loop_stalled`; `notifications create ... --conditions loop_stalled` announces it after `--hold` minutes.
- Act on it: look with `screen screenshot ID`, then `screen reload ID`. It clears by itself when the next media start arrives (`verdict` `playing`), or when the screen stops being judged (`unjudged`: it went offline, was archived, or a takeover began). Only the media start is a recovery.
- Late reports: Players report in batches, so a screen that kept playing can look stalled until its reports land. The clearing event carries `late_reports` when the Player's play numbers show it.

It does not judge a screen whose Player sends no play numbers, a loop of one page, a loop with no page that always starts media or with a page of unknown length (adslot break, application-timed page, media chosen when the loop runs), a video wall, a display that is off, standing by or disconnected, a takeover or suspension, an offline screen, an error status, an update that is not current, or anything while no screen at all reported a media start in two minutes. New content (a playlist edit, an update, the end of any state above) restarts the clock.

### glass_blank and glass_frozen: the screenshots show nothing, or nothing moves

Every screenshot of a screen (yours, the dashboard's, or one screenRIG asks for) is reduced to a small brightness grid; no pixels are kept. One flat frame is not a verdict: it can be a transition between pages or a page that is black on purpose, and identical frames can be a two-page loop sampled in step with its period. So a flat frame, or a frame like the one more than the longest page earlier, only makes screenRIG suspicious. It then asks the Player for more screenshots, a little under the shortest page apart, until they span the loop plus its longest page. The verdict is `blank` when all of them were one flat tone and `frozen` when all were the same picture; one frame that disagrees drops the suspicion without a trace.

- Read it: `screen show ID` prints "Blank screen since ..." or "Frozen picture since ..." and `data.glass.picture` has `verdict`, `since` and `judged_at`. `alerts list` shows condition `glass_blank` or `glass_frozen`; `notifications create ... --conditions glass_blank,glass_frozen` announces them after `--hold` minutes.
- `screen screenshot ID` saves the image and reports `data.frame.flat` for that one image, beside the screen's `data.picture` verdict if it has one. A flat image alone is no verdict; the human output says so.
- Act on it: look with `screen screenshot ID`, then `screen reload ID`. A verdict is looked at again every 10 minutes even when nobody is watching, and ends (`verified`) after two screenshots in a row that show a moving picture, or (`unjudged`) when the screen goes offline, is archived or is no longer judged. Only `verified` is a recovery; `unjudged` closes the alert without a recovery message.

It does not judge a screen that is offline, whose display is off, standing by or disconnected, that is under a takeover or suspended, that is a video wall, or whose status is an error or whose update is not current; a loop of one page, with a page that has nothing on it, with no image or card page that is always in it (video, stream, iframe and application captures can come back black), with a page shorter than 6.25 seconds, with a page whose length the playlist does not fix (it plays to the end of its media, an application, an adslot break), or too long to cover with 30 captures; and a capture the Player reported as failed (a privacy frame). A loop whose every page is black on purpose reads as blank, and one whose every page looks alike reads as frozen. There is no "wrong content" verdict: a capture does not say which page was on glass.

## source_failed and source_stale: a data feed breaks

These two conditions are about a data source (`source create`), not a screen.
`source_failed` opens when a refresh of the source fails and clears when one
works; `source_stale` opens when a failing source's last good data is older than
its `stale_after_seconds`, the moment the data expires on every screen and pages
that depend on it fall back, and clears with the next refresh that works.
`notifications create ... --conditions source_failed,source_stale` announces them
after `--hold` minutes (a short hold is right for a feed a room sign depends on).
A notice names the source and links its page; it is never grouped, is not a
screen alert (`alerts list` never shows it), and `--tag` never matches a source, so
leave it off. `source show ID` says why (`status.error`, `status.stale`,
`data_expires_at`); `source refresh ID` retries now.

## card_data_stale: a scheduled write stops

This condition is about a card, not a screen. A card whose data you write with an
expiry (`card data put --ttl`, or `--expires-at`) goes blank on every screen when
the expiry arrives with no write to renew it. `card_data_stale` opens at that
moment, while a screen shows the card, and clears with the next write that lands:
it is how a stopped schedule is noticed ([keep cards
current](sources.md#keep-cards-current)).

- `notifications create --email owner --conditions card_data_stale` announces it
  after `--hold` minutes. The notice names the card (its id and type), says when
  its data expired and to check the agent or job that writes it; `card data get
  crd_ID` shows what was written last.
- It is never a screen alert and never grouped, and `--tag` never matches a card.
  Severity is `warning` by default; `--min-severity`, `--active-hours`, `--hold`
  and snooze apply as for any condition.
- It stays quiet for a data source's cards (`source_stale` covers those), for data
  written with no expiry (a card webhook's data stays until replaced), for a card
  no screen shows, and when the card's data is deleted.

## reach_dropped and group_empty: a campaign silently stops reaching screens

These two conditions are about a campaign (`campaign create`), not a screen. A
tag edit, a folder move, an archived or deleted screen or a new audience can
leave a campaign with fewer screens while nothing fails, and the playlist it
switched in stops showing where it should.

- `reach_dropped` opens when a recount finds the campaign reaching fewer screens
  than when it was last published (created, or updated with a new audience,
  playlist or paused state). It clears when it reaches as many again, or on its
  next publish. `--reach-drop-screens N` and `--reach-drop-percent P` (both
  needed to be met; they require `reach_dropped` in `--conditions`) ignore small
  drops; `update ID --clear-reach-drop` makes any drop notify again.
- `group_empty` opens when a tag or folder the audience names matches no screen,
  one notice per group (`notifications deliveries ID` shows `audience_group`,
  `tag:Lobby` or `folder:sfd_ID`). It clears when the group matches a screen
  again; a publish that drops the group from the audience closes it without a
  recovery message.
- Neither is a screen alert, and `--tag` or `--audience` on the notification never
  limits them. Severity, hours and hold apply as for any condition, default
  `warning`. The notice names the campaign and the numbers and links its calendar.
- Read it: `campaign show ID` has `reach` (`published`, `current`, `at`,
  `empty_groups`), recounted within about 15 seconds of a change. A write that
  causes the drop already says so: `levels.lost` on `screen tag`, `screen move`
  and folder edits names the campaign with `reach_before` and `reach_after`. Tell
  the user before going on, and offer to undo the tag or folder change.
