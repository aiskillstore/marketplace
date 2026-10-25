# Installation / نصب

## Native skill hosts

1. Download or clone the full repository into a directory named `write-natural`.
2. Register that directory using the host's supported skill installation flow.
3. Preserve relative paths. Copying only `SKILL.md` loses the genre and language guidance.
4. Confirm that the host can read a linked reference and invoke `write-natural`.
5. Ask for a small edit with a protected number and qualifier; check the output yourself.

For hosts configured to discover `~/.codex/skills`, the complete folder can live at `~/.codex/skills/write-natural`. This is a conditional directory example, not a compatibility claim for all products. Restart or refresh skill discovery if the host requires it. No paid account, Python package or network service is required by the writing instructions themselves; the host can have its own requirements.

## Manual use

If your assistant cannot install skills, provide the core and relevant linked modules in its context. Avoid pasting the entire research archive. Confirm that needed references are actually available; merely naming an absent file does not load it.

## Optional diagnostics

Use Python 3.9+ from the repository root. No `pip install` step is required. See `references/local-tools.md` for arguments, exit codes, protected spans and known limitations. The original runtime test environment is disclosed in `references/validation.md`; cross-platform execution is not assumed.

## فارسی

پوشهٔ کامل با نام `write-natural` را از روش پشتیبانی‌شدهٔ میزبان ثبت کنید. فقط کپی کردن هسته کافی نیست. مسیرهای نسبی را حفظ کنید و با یک ویرایش کوتاه بررسی کنید که مرجع فارسی واقعاً خوانده می‌شود و عدد و قید احتمال تغییر نمی‌کنند. نصب ZIP و محل پوشه به میزبان بستگی دارد. برای استفادهٔ دستی، هسته و مرجع‌های لازم را در اختیار مدل بگذارید؛ صرف نام بردن یک فایل، محتوای آن را بارگذاری نمی‌کند.
