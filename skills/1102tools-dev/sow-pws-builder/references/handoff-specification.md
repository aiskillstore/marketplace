# Chat-Only Handoff Specification

Emit both handoffs after the `.docx` is saved and validated. They are internal Government workpapers in the conversation, never files and never document sections or appendices.

## 1. Staffing handoff

Use this heading and notice:

```text
=== STAFFING HANDOFF TABLE: FOR IGCE BUILDER ===
Internal Government workpaper. Not part of the SOW/PWS contract deliverable.
Do not paste this table into the contract file.
```

Fixed columns:

`Labor Category | SOC Code | FTE | Phase | Hours/Yr | Notes`

Rules:

- Include every user-approved labor category.
- Preserve user overrides and derivation basis in Notes.
- Derive continuous coverage from annual coverage hours divided by productive hours.
- Keep at least four decimals in coverage calculations; round presentation only with disclosure.
- Preserve Tier 1 help desk or contact-center SOC 43-4051.
- Identify hybrid CLIN or contract-type routing in Notes.
- Do not include rates, burden, fee, price, or fair-and-reasonable language.

End with: `This approved staffing handoff is ready for the FFP, LH/T&M, or CR pricing skill selected by contract type. The pricing skill should preserve it and ask only for missing pricing inputs.`

## 2. Section B handoff

Use this heading and notice:

```text
=== SECTION B HANDOFF TABLE ===
Contract-administration workpaper. Not part of the SOW/PWS contract deliverable.
Use it to draft Section B of the solicitation shell, not the SOW/PWS body.
```

Base columns:

`Line | Description | Contract Type | Pricing Unit or Basis | Period | Notes`

Build rows from the user's preferred structure: by period, function, deliverable, or hybrid. Add separate travel and ODC lines when in scope.

For T&M/LH, add a second table when the user wants estimated hours for rate evaluation:

`Labor Category | Contractor or Source | Base Estimated Hours | Option Hours | Total Estimated Hours | Fixed Hourly Rate Input`

Also show:

`Overall T&M/LH Ceiling Price Input: <user-confirmed amount or PENDING CO DECISION>`

Do not label estimated hours as a FAR-mandated labor-category ceiling. FAR 16.601 requires fixed hourly rates by labor category and an overall ceiling price; the Contracting Officer owns the final Section B structure.

For CPFF, carry the confirmed Completion or Term form in Notes. For hybrid requirements, make each line's type explicit.

End with: `This is a suggested Section B starting point. The Contracting Officer owns the final line-item structure, estimated hours, rates, and ceiling.`

## Separation audit

The final `.docx` must not contain:

- Either handoff heading or notice
- `IGCE Builder`, `build the IGCE`, or pricing-skill names
- `SOC Code`, FTE values, staffing derivation, or internal workpaper language
- A CLIN or Section B table
- Proposed hourly rates, burden, wraps, fee, or prices

The conversation may contain all of those because the handoffs are explicitly outside the document.
