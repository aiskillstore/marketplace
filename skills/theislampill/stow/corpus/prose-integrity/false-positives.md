## False Positive Prevention
### Context-Aware Severity
If a banned word appears immediately adjacent to specific named entities (proper nouns, statute numbers, dates, dollar amounts), it is more likely being used with technical meaning than as AI filler. Reduce flag severity.
- **Higher severity:** "a comprehensive examination of the issues" (abstract nouns, no specifics)
- **Lower severity:** "comprehensive audit by the FTC in 2024" (specific entity, specific date)

### Metaphorical vs. Literal Distinction
These words require bigram context checking. Only flag metaphorical uses:
- ecosystem: "Apple's software ecosystem" (OK) vs. "the repair ecosystem" (flag)
- landscape: "Arizona landscape" (OK) vs. "the regulatory landscape" (flag)
- navigate: "navigate the website" (OK) vs. "navigate the regulatory process" (flag)
- tapestry: "medieval tapestry" (OK) vs. "a tapestry of regulations" (flag)
- symphony: "Beethoven's symphony" (OK) vs. "a symphony of features" (flag)
- beacon: "lighthouse beacon" (OK) vs. "a beacon of hope" (flag)
- testament: "last will and testament" (OK) vs. "a testament to innovation" (flag)
