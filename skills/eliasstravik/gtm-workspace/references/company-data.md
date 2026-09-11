# Company-data research contract

Use this contract for the default company data in every newly created `ORG.md` and `ICP.md`, and whenever research refreshes either artifact. `ORG.md` records sourced facts about the organization. `ICP.md` records desired or accepted account criteria. Numeric and monetary ICP values may be target ranges, and ICP lists contain accepted values.

Research every field when safe sources are available. Preserve uncertainty and source limits. Keep every field visible in the rendered Markdown and write `Unknown` when a value cannot be resolved. Never invent a value or infer an ICP criterion from organization facts.

Use `## Company data` followed by these 13 top-level fields in this order. Optional structural metadata and free-form notes may follow the company data, but they are not default research targets.

1. **Business types**
   - A controlled list describing how the company serves its market.
   - Examples include `B2B`, `B2C`, and `Nonprofit`.
   - Record every applicable value.
2. **Industries**
   - A controlled list.
   - Examples include `Software` and `Financial Services`.
3. **Subindustries**
   - A controlled list.
   - Examples include `Sales Enablement` and `Payment Processing`.
4. **Revenue streams**
   - A controlled list.
   - Examples include `Professional Services`, `Financial Services`, `Subscriptions/Recurring`, `Product Sales`, `Transaction Fees`, `Rental/Leasing`, and `Project/Contract Work`.
   - Record every applicable value.
5. **Annual revenue**
   - A monetary amount or range with its currency.
   - Nest the amount or range and its estimated status under this field. Record estimated status when known.
6. **Company size**
   - An employee-count range, such as `51-200`.
   - Record lower and upper bounds when useful.
7. **Company type**
   - One controlled value.
   - Examples include `Privately held`, `Public company`, `Partnership`, `Self-employed`, `Nonprofit`, `Educational`, and `Self-owned`.
8. **Description**
   - A concise free-text description of what the company does.
9. **Domain**
   - A normalized hostname such as `example.com`.
   - Remove the protocol, path, and `www` prefix.
10. **Employees**
    - A non-negative integer employee count.
    - Use the label `Employees`. Nest the count and its estimated status under this field, and record estimated status when known.
11. **Location**
    - One or more structured locations.
    - Each location supports city, country, country code, headquarters status, postal code, region, and state or province.
12. **Products and services**
    - A free-form list of offering concepts, not a copy of the description.
    - Examples include `B2B SaaS`, `Revenue intelligence`, and `Implementation services`.
13. **Tech stack**
    - Three structured lists named `Categories`, `Products`, and `Vendors`.
    - Example categories include `CRM` and `Marketing automation`.
    - Example products include `Salesforce Sales Cloud` and `HubSpot Marketing Hub`.
    - Example vendors include `Salesforce` and `HubSpot`.
