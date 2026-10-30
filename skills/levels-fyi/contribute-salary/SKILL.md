---
name: contribute-salary
description: Add the user's own salary or offer to Levels.fyi. Use when the user wants to share, submit or add their pay, including from an offer letter or comp statement, or says yes after you offer to add it.
---

# Add the user's salary to Levels.fyi

Help the user add their own pay or an offer they received, using `add-salary-submission`. No account is needed: a signed-in user's submission is tied to their account, and anyone else gives an email address instead.

This needs the connected Levels.fyi tools. If they aren't available, ask the user to connect Levels.fyi in their app's plugin or connector settings, and don't submit any other way.

## Ground rules

- Only the user's own pay or an offer they received. Never another person's pay, a number you estimated or took from Levels.fyi data, a range from a job posting, a hypothetical, or a test entry.
- Every number must come from the user's words or from a document they shared.
- One submission per job or offer. Never resubmit a confirmed one.

## 1. Gather the details conversationally

If the user shared an offer letter, comp statement or pay stub, take the details from it, list what you read so they can correct it, and ask only for what's missing. Otherwise ask a question or two at a time, starting with the company, role and location. Don't list every field up front.

1. **Company, role and title.** Resolve with `search-companies` and `search-job-families`. Use `companyName` only when `search-companies` finds nothing.
2. **Location: a city.** Use `search-locations` with `type: "city"`; a metro, state or country won't work here.
3. **Offer or current pay?** Offers need the offer date. For current pay, ask how long they have been at the company.
4. **Level.** Use the company's own level name from `get-company-levels` when the company has a ladder.
5. **Base salary,** its currency and period.
6. **Stock.** For an offer: the total grant and the vesting schedule. For current pay: the stock value they receive per year.
7. **Bonus.** For an offer: the target, as an amount or a percent of base. For current pay: the bonus they actually receive per year.
8. **Sign-on and relocation:** offers only. For current pay, put them in `otherDetails`.
9. **Years of experience** and **work arrangement** (remote, hybrid or office).

For stock options, set `stockType` to `option` and send `totalOptionsGranted` (or `avgAnnualOptionsGranted` for current pay), `optionStrikePrice` and `optionPreferredPrice` (the latest price investors paid), with their currency. Don't put a dollar value on the options yourself.

## 2. Turn a vesting description into a schedule

`vestingSchedule` has one entry per year: `percent` of the grant vesting that year, and `occurrences` (how many times it vests that year).

- "4 years, 1-year cliff, then quarterly": `[{percent:25, occurrences:1}, {percent:25, occurrences:4}, {percent:25, occurrences:4}, {percent:25, occurrences:4}]`
- "4 years, vests monthly": four entries of `{percent:25, occurrences:12}`
- "5/15/40/40": `[{percent:5, ...}, {percent:15, ...}, {percent:40, ...}, {percent:40, ...}]`, with occurrences as the user describes

If the user doesn't know, `get-vesting-schedules` shows the company's usual schedule. Confirm it with them before using it.

## 3. Preview, then confirm

1. Generate one UUID as `submissionId` and keep it for this submission.
2. Call `add-salary-submission` with `confirm: false`. Set `source` to `user_document` when the numbers come from an offer letter or pay stub the user shared, otherwise `user_stated`.
3. Show the preview in this form, leaving out lines that don't apply, and ask about anything in `notProvided` that they have:

   > The entry would look like this: [entry, pay in its own currency; [stock per year]; [options granted, strike and preferred price]]. Your name and email never show. [If stock or options: I've entered [stock per year, in its currency / options granted, strike and preferred price]. Fix or drop that if it's off.] [If not signed in: your email only verifies this and is never shown. Levels.fyi may email you for an offer letter or pay stub. That's optional, and it's reviewed either way.] Tell me what to change, or say confirm.
4. If the user isn't signed in, ask for their email and pass it as `email`. Say it's used to verify the entry, not shown with it. Never use an email they gave for anything else.
5. If the user asks for enhanced anonymity, at any point, set `anonymise: true`. It can hide details like company and title on the public entry.
6. Only after a clear yes, call again with the same arguments, the same `submissionId`, and `confirm: true`.

If a call fails, fix what the error names and retry with the same `submissionId`, so a retry can't add the entry twice.

## 4. After submitting

Reply in this form, leaving out the comparison when there's no data for it:

> Added, thank you. Your total pay is [above / in line with / below] the median for [company level / role in city]. [Omit that if there's no data, or if the entry has options.] It gets reviewed before it counts. Nothing else to do.

Share the link the tool returns, then carry on with whatever the user was doing.
