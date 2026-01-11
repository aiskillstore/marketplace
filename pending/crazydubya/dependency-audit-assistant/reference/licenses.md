# License Compatibility Matrix

## License Categories

### Permissive Licenses (Most Compatible)

**MIT License**
- ✓ Commercial use allowed
- ✓ Modification allowed
- ✓ Distribution allowed
- ✓ Private use allowed
- Requirement: Include license and copyright notice
- Compatible with: Everything

**Apache License 2.0**
- ✓ Commercial use allowed
- ✓ Modification allowed
- ✓ Distribution allowed
- ✓ Patent grant included
- Requirement: Include license, copyright, and state changes
- Compatible with: Most licenses (including GPL-3.0+)

**BSD Licenses (2-Clause, 3-Clause)**
- ✓ Commercial use allowed
- ✓ Modification allowed
- ✓ Distribution allowed
- Requirement: Include license and copyright notice
- Compatible with: Everything

**ISC License**
- ✓ Functionally equivalent to MIT
- ✓ Simpler wording
- Compatible with: Everything

**Unlicense / 0BSD**
- ✓ Public domain equivalent
- ✓ No restrictions
- Compatible with: Everything

### Weak Copyleft (Moderate Restrictions)

**LGPL (Lesser GPL)**
- ✓ Can be used in proprietary software
- Requirement: Changes to LGPL code must be released
- ⚠️ Dynamic linking usually okay, static linking may require release
- Use case: Libraries that can be used in commercial apps
- Compatible with: Proprietary code (with conditions)

**MPL (Mozilla Public License)**
- ✓ File-level copyleft
- ✓ Can combine with proprietary code
- Requirement: Changes to MPL files must be released
- Compatible with: Proprietary code (file-scoped)

**EPL (Eclipse Public License)**
- Similar to MPL
- ✓ Can combine with proprietary code
- Requirement: Changes to EPL code must be released

### Strong Copyleft (Significant Restrictions)

**GPL-2.0**
- ✗ Any derivative work must be GPL
- ✗ Cannot combine with proprietary code in many cases
- Requirement: Entire combined work must be GPL
- Use case: Open source projects only
- Incompatible with: Apache-2.0, proprietary code

**GPL-3.0**
- ✗ Any derivative work must be GPL
- ✗ Cannot combine with proprietary code
- ✓ Compatible with Apache-2.0
- Additional: Anti-tivoization, patent grants
- Use case: Strong open source projects

**AGPL (Affero GPL)**
- ✗ Network use = distribution (must release)
- ✗ SaaS products must release source
- Most restrictive copyleft license
- Use case: Prevent SaaS loopholes

### Problematic / Unknown

**UNLICENSED**
- ✗ No license = no rights to use
- ✗ Legally risky
- Action: Contact author for license

**UNKNOWN**
- ✗ Cannot determine license
- ✗ May be proprietary
- Action: Investigate package source

**Custom Licenses**
- ⚠️ Requires legal review
- May contain unusual restrictions
- Action: Read license carefully

## Compatibility Chart

| Your License | Can include MIT? | Can include Apache-2.0? | Can include GPL-2.0? | Can include GPL-3.0? | Can include AGPL? |
|--------------|------------------|-------------------------|----------------------|----------------------|-------------------|
| Proprietary  | ✓ Yes            | ✓ Yes                   | ✗ No                 | ✗ No                 | ✗ No              |
| MIT          | ✓ Yes            | ✓ Yes                   | ✓ Yes*               | ✓ Yes*               | ✓ Yes*            |
| Apache-2.0   | ✓ Yes            | ✓ Yes                   | ✗ No                 | ✓ Yes                | ✓ Yes*            |
| GPL-2.0      | ✓ Yes            | ✗ No                    | ✓ Yes                | ⚠️ Maybe             | ✗ No              |
| GPL-3.0      | ✓ Yes            | ✓ Yes                   | ⚠️ Maybe             | ✓ Yes                | ✗ No              |
| AGPL         | ✓ Yes            | ✓ Yes                   | ⚠️ Maybe             | ✓ Yes                | ✓ Yes             |
| LGPL         | ✓ Yes            | ✓ Yes                   | ✓ Yes                | ✓ Yes                | ⚠️ Maybe          |

*Note: Including permissive code in GPL means the result must be GPL

## Common Scenarios

### Scenario 1: Commercial/Proprietary Product

**Safe to use:**
- ✓ MIT, Apache-2.0, BSD, ISC
- ✓ LGPL (with dynamic linking)
- ✓ MPL, EPL (for specific files)

**Avoid:**
- ✗ GPL (any version)
- ✗ AGPL

**Action:**
Replace GPL dependencies with MIT/Apache alternatives

### Scenario 2: Open Source (MIT/Apache)

**Safe to use:**
- ✓ MIT, Apache-2.0, BSD, ISC
- ✓ LGPL, MPL, EPL
- ⚠️ GPL (if you want to relicense to GPL)

**Considerations:**
- Including GPL makes entire project GPL
- May limit adoption by commercial users

### Scenario 3: GPL-3.0 Project

**Safe to use:**
- ✓ MIT, Apache-2.0, BSD, ISC (becomes GPL in combination)
- ✓ LGPL-3.0, GPL-3.0
- ✓ Other GPL-3.0 compatible

**Avoid:**
- ✗ GPL-2.0 only (license conflict)
- ⚠️ AGPL (different network requirements)

### Scenario 4: SaaS Application

**Safe to use:**
- ✓ MIT, Apache-2.0, BSD, ISC
- ✓ LGPL, MPL (with conditions)

**Critical:**
- ✗ AGPL requires releasing server source code
- ✗ GPL may require release depending on interpretation

## Red Flags

🚩 **GPL in proprietary code**
- High risk, likely license violation
- Action: Remove or replace with permissive alternative

🚩 **AGPL in SaaS product**
- Requires releasing server code
- Action: Replace or prepare to open source

🚩 **UNLICENSED packages**
- No legal right to use
- Action: Contact author or find alternative

🚩 **Multiple GPL versions (2.0 and 3.0)**
- May be incompatible
- Action: Check "or later" clauses

🚩 **Custom licenses**
- Unknown restrictions
- Action: Legal review required

## Safe Combinations

### Web Application (Proprietary)
```
Your code: Proprietary
Frontend libs: MIT, Apache-2.0 (React, Vue, etc.)
Backend libs: MIT, Apache-2.0 (Express, etc.)
Databases: PostgreSQL (PostgreSQL License - permissive)
Result: ✓ Safe
```

### Open Source Library (MIT)
```
Your code: MIT
Dependencies: MIT, Apache-2.0, BSD
Result: ✓ Safe, stays MIT
```

### Open Source Application (GPL-3.0)
```
Your code: GPL-3.0
Dependencies: MIT, Apache-2.0, GPL-3.0, LGPL
Result: ✓ Safe, entire project is GPL-3.0
```

## License Mitigation Strategies

### If you find GPL in proprietary code:

1. **Replace the dependency**
   - Find MIT/Apache alternative
   - Write your own implementation
   - Use a paid proprietary alternative

2. **Isolate via services**
   - Run GPL code in separate service
   - Communicate via API/network
   - May avoid license infection (consult lawyer)

3. **Dual licensing**
   - Some GPL projects offer commercial licenses
   - Contact copyright holder

4. **Relicense your project**
   - If feasible, make your project GPL
   - Understand implications for users

### If you find AGPL in SaaS:

1. **Replace with permissive alternative**
2. **Open source your application**
3. **Purchase commercial license** (if available)
4. **Isolate in separate service** (legal gray area)

## Best Practices

1. **Audit regularly**: Check licenses before adding dependencies
2. **Use automation**: Tools like `license-checker`, `FOSSA`, `Black Duck`
3. **Document decisions**: Why certain licenses were approved
4. **Consult legal**: For commercial products, get legal review
5. **Prefer permissive**: MIT/Apache-2.0 for maximum compatibility
6. **Track transitive deps**: Hidden GPL in dependency tree is still GPL
7. **Version matters**: GPL-2.0 ≠ GPL-3.0
8. **Read licenses**: Don't assume based on name alone

## Resources

- [Choose a License](https://choosealicense.com/)
- [SPDX License List](https://spdx.org/licenses/)
- [tl;drLegal](https://www.tldrlegal.com/)
- [OSI Approved Licenses](https://opensource.org/licenses)

## Common License Alternatives

| GPL Package | MIT/Apache Alternative |
|-------------|------------------------|
| readline (GPL) | libedit (BSD) |
| MySQL (GPL) | PostgreSQL (PostgreSQL License) |
| Qt (GPL/Commercial) | GTK+ (LGPL), wxWidgets (wxWindows) |
| FFmpeg (GPL with some parts LGPL) | GStreamer (LGPL) |

---

**Disclaimer**: This is general guidance. For legal questions about licenses in your specific project, consult a lawyer specializing in software licensing.
