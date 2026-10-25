# Persian writing: native register and precise meaning

Use for Persian and mixed Persian/English output. Treat editorial heuristics as contextual guidance, not evidence of authorship. A10–A11 inform native register and script review; R04 motivates examining cultural homogenization without transferring its measured effects to Iran. Current primary guidance Q01–Q03 overrides unsupported SEO folklore in style guides.

## Choose register from the deliverable

Read destination and audience before matching the user's chat style.

| Destination | Default register | Preserve |
|---|---|---|
| Paper, thesis, scholarly report | Written academic Persian; measured claims | Qualifications, discipline terms, statistical notation |
| Proposal, business email, professional report | Formal, direct, courteous | Clear obligations and required conventions |
| Administrative letter | Formal with appropriate salutation and close | Addressee/title, subject, specific request, signature |
| Blog, tutorial, newsletter | Written, accessible, engaged | Author's legitimate perspective and needed depth |
| Product/service page | Real audience and brand's register | Accurate offer, conditions, currency, evidence |
| Explicitly casual social copy or personal chat | Consistent colloquial writing | Natural particles, speaker voice, correct هکسره |
| Fiction, poetry, quoted speech | Voice defined by the work | Deliberate rhythm, character, imagery, quotation |

Use full written forms such as «می‌شود» in formal prose. Use colloquial forms such as «میشه» only when appropriate and consistent. Do not make every brand casual, every academic sentence passive, or every formal letter bureaucratic.

Distinguish warmth from slang. A clear sentence, a real detail, and a courteous request can sound human without chatty idioms. Explain mechanisms impersonally, address reader actions directly, and use «ما» for actions genuinely attributable to the author or organization. Avoid needless repetition of «شما» when the verb carries it.

## Edit weak Persian by function

Review clusters, rather than treating one phrase as a verdict:

- Ceremonial announcement: «لازم به ذکر است»، «شایان ذکر است»، «همان‌طور که می‌دانید». State the information unless the framing has a real function.
- Inflated significance: «نقش بسزایی»، «از اهمیت ویژه‌ای برخوردار»، «گامی شگرف». Explain the effect, evidence, or mechanism.
- Empty promotion: «بی‌نظیر»، «بی‌رقیب»، «تجربه‌ای متفاوت». Use a supportable distinction or remove the claim.
- Formulaic setup and close: «در دنیای امروز»، «با گسترش روزافزون»، «در نهایت می‌توان گفت». Begin at the point; stop when the reader's need is met.
- Unwarranted interpretation: «که نشان‌دهندهٔ تعهد ماست». A change does not by itself establish motive or significance.
- Translationese: identify English idioms that distort intended meaning. «در پایان روز» is correct literally; otherwise express the actual intended conclusion.
- Bureaucratic verb chains: use a direct verb where meaning permits. «درخواست را ثبت کنید» can replace «اقدام به ثبت درخواست نمایید». Preserve exact legal or approved wording when required.

Keep «احتمالاً»، «تقریباً»، «عمدتاً»، «ممکن است»، «تا»، «حداقل» and «معنادار» when they constrain a claim. Do not delete «زیرا»، «اگر»، «اما» or «بنابراین» when they encode real logic. Do not force three factual items into two to avoid a perceived AI tell.

## Preserve technical and source meaning

Keep one chosen term per concept. Introduce the English equivalent when useful, then remain consistent. Do not alternate «سامانه»، «پلتفرم» and «ابزار» if that introduces ambiguity.

In source-based paraphrase preserve qualifiers, quantities, comparison direction, denominator, uncertainty and scope. Separate findings from the author's synthesis. Do not supply missing methods, causes, citations or results from what is typical.

Keep statistical symbols, units and exact values. A non-significant difference does not establish equivalence. Use appropriate LTR formatting for notation and equations.

## Apply orthography without corrupting data

- Use Persian ی and ک in authored Persian prose. Preserve exact quotations, proper names, Arabic passages, identifiers and source data where fidelity requires it.
- Use normal نیم‌فاصله U+200C where appropriate: «می‌شود»، «نمی‌توان»، «کتاب‌ها»، «خانه‌ام»، «حرفه‌ای». Do not insert it globally into unknown compounds or machine-readable content.
- Distinguish ezafe from colloquial «ـه»: «این کتابه» can mean «این کتاب است»; «کتابه من» incorrectly substitutes «ه» for ezafe. Judge in context, not by a suffix regex alone.
- Prefer Persian punctuation in Persian prose: «،»، «؛»، «؟» and «گیومه». Keep one house style for ezafe after ه. Preserve punctuation inside protected material.
- Use Persian digits in ordinary Persian prose if the destination allows them. Preserve Latin digits in URLs, DOI, code, identifiers, version strings, source keys and notation. Follow explicit journal style when it differs.
- Name currency and scale: تومان, ریال, هزار, میلیون. Never infer or convert the unit silently. Specify calendar and time zone when consequential.
- Keep ordinary word/punctuation spacing consistent; preserve intentional formatting in code, tables and poetry.

## Handle direction in the output format

In plain Markdown, lead a mixed paragraph with a natural Persian word where possible: «کتابخانهٔ React…». Keep Latin runs whole. Do not sprinkle invisible control characters as a generic repair.

For HTML use `lang="fa"`, `dir="rtl"`, and direction isolation for Latin fragments. For Word, slides and sheets use their native bidi properties through the format skill. A text file cannot guarantee a platform's shaping; inspect the rendered artifact when layout matters.

## Original calibration examples

### Formal service copy

Weak: «خدمات ما تجربه‌ای بی‌نظیر و تحول‌آفرین برای شما رقم می‌زند.»

If the only verified fact is consolidation of three spreadsheets: «داده‌های سه فایل را در یک گزارش می‌بینید.» Do not add time saved or automatic updates without evidence.

### Academic paraphrase

Given: «در نمونهٔ بررسی‌شده، کاهش اندکی مشاهده شد؛ علت آن مشخص نیست.»

Faithful: «در نمونهٔ این مطالعه کاهش اندکی دیده شد، اما علت آن روشن نیست.»

Reject: «این روش باعث کاهش شد.» It adds cause and removes scope.

### Casual and formal counterparts

Given: the author cannot attend tomorrow and will send the file tonight.

Casual: «فردا نمی‌تونم بیام؛ فایل رو امشب می‌فرستم.»

Formal: «فردا امکان حضور ندارم؛ فایل را امشب ارسال می‌کنم.»

Choose from the audience and destination, not an assumption that casual prose is more human.

## Final review

Read aloud for translated rhythm and mismatched register. Check هکسره, ی/ک, نیم‌فاصله, point of view, stable terms, punctuation and mixed direction. Compare the facts again. Passing orthography does not establish substance, accuracy or natural authorship.
