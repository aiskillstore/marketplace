# استفاده و نمونهٔ درخواست / Invocation examples

## فارسی

در محیطی که اسکیل‌ها را می‌خواند، پوشهٔ `write-natural` باید همراه با `SKILL.md`، پوشه‌های `references`، `scripts`، `assets` و `agents` در دسترس باشد. پشتیبانی از نصب ZIP و محل پوشه در میزبان‌های مختلف فرق می‌کند؛ یک قالب نصب واحد را برای همهٔ ابزارها فرض نکنید. این بسته سرویس آنلاین یا افزونهٔ تشخیص نویسنده نیست.

پس از بارگذاری اسکیل، نوع متن، مخاطب، اطلاعات واقعی و محدودیت‌های مهم را در درخواست بنویسید. اگر پیش‌نویس یا نمونهٔ لحن دارید، همان را هم ارائه کنید. لازم نیست همهٔ مرجع‌ها را دستی به هر درخواست بچسبانید؛ هسته مسیر مربوط را انتخاب می‌کند.

نمونه‌های قابل‌استفاده:

- «از $write-natural استفاده کن. این بند را برای پایان‌نامه ویرایش کن؛ عددها، قیدهای احتمال و استنادها حفظ شوند.»
- «با $write-natural برای این محصول یک متن فارسی بنویس. فقط از مشخصات زیر استفاده کن و ادعای صرفه‌جویی یا ضمانت نساز.»
- «با $write-natural این مقاله را از نظر اسلپ و پرش استدلال نقد کن؛ ابتدا مهم‌ترین ایرادهای واقعی را نشان بده.»
- «با $write-natural این متن انگلیسی را به فارسی طبیعی ترجمه کن. لحن رسمی بماند و نقل‌قول‌ها دقیق حفظ شوند.»
- «با $write-natural این پیش‌نویس را طبیعی‌تر کن. نتیجهٔ آزمایش تشخیص در اختیار نداریم؛ ادعای عبور از ابزار نکن.»
- «با $write-natural فقط تیتر را عوض کن و به بقیهٔ متن دست نزن.»

برای کنترل محلی، به `local-tools.md` مراجعه کنید. ابزارها هشدار و محل بررسی می‌دهند؛ هیچ امتیاز واقعیِ AI بودن یا گواهی صحت تولید نمی‌کنند. نتیجهٔ یک هشدار می‌تواند «نگه‌داشتن عبارت با دلیل» باشد.

## English

Make the complete `write-natural` directory available to a host that supports Markdown skills. Keep its relative resource paths intact. ZIP import behavior and installation paths vary by host; do not claim universal compatibility without a host-specific test.

Examples:

- “Use $write-natural to revise this paper abstract. Preserve every number, citation, comparison and uncertainty qualifier.”
- “Use $write-natural to write product copy from the attached facts. Do not invent testimonials, guarantees or performance results.”
- “Use $write-natural for a detector-aware edit. Improve actual writing quality and retain my voice; do not claim an unmeasured detector result.”
- “Use $write-natural to compare these revisions for changed claims, then explain the most consequential differences.”
- “Use $write-natural to produce three distinct newsletter angles from the supplied facts, with no fabricated anecdotes.”

Python tools are optional and require only Python 3.9+. Ordinary writing can run without Python or internet access. Research tasks need source access when the required evidence is not supplied; missing access remains a documented limitation.
