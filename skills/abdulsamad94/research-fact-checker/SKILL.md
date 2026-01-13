---
name: research-fact-checker
description: Assists authors in researching topics, verifying facts, and ensuring accuracy in their writing. Particularly useful for historical fiction, non-fiction, science fiction, and any genre requiring real-world accuracy. Use when the user needs help with research or fact-checking.
---

# Research and Fact-Checking Tool

## Purpose

This skill helps authors conduct research, verify factual accuracy, and maintain credibility in their writing. It provides structured research approaches, fact-checking methodologies, and helps authors integrate research seamlessly into their narrative without info-dumping.

## When to Use

- User is writing historical fiction and needs period-accurate details
- User is writing non-fiction and needs to verify claims
- User is writing science fiction/fantasy and wants scientifically plausible elements
- User needs to research a specific topic for their book
- User wants to fact-check existing content
- User needs help citing sources properly
- User is concerned about cultural accuracy and sensitivity

## Instructions

### Step 1: Identify Research Needs

Ask the user:

- **Topic/Subject**: What needs to be researched or fact-checked?
- **Genre/Context**: How will this information be used in the book?
- **Depth Required**: Surface-level accuracy or deep expertise?
- **Time Period**: For historical content, what era?
- **Geographic Location**: Where is this set/relevant?
- **Specific Questions**: What exactly do they need to know?

### Step 2: Develop Research Strategy

Based on the topic, create a structured research plan:

#### A. Historical Research

- Primary sources (period documents, letters, newspapers)
- Secondary sources (historical analysis, academic papers)
- Expert memoirs and firsthand accounts
- Period-specific databases and archives
- Museum collections and exhibits

#### B. Scientific/Technical Research

- Peer-reviewed journals and publications
- Expert interviews or consultations
- Scientific databases (PubMed, arXiv, etc.)
- Technical manuals and specifications
- University course materials

#### C. Cultural Research

- Cultural consultants and sensitivity readers
- First-person narratives from that culture
- Academic anthropological/sociological studies
- Contemporary media from that culture
- Community forums and discussions

#### D. Professional/Career Research

- Professional associations and their resources
- Industry publications and trade journals
- Interviews with professionals in the field
- Job descriptions and required qualifications
- Day-in-the-life accounts

### Step 3: Provide Research Framework

For each research topic, create:

```markdown
# Research Brief: [Topic]

## Research Question

[Specific question to answer]

## Background Context

[Why this research is needed for the story]

## Key Areas to Investigate

1. [Area 1]
2. [Area 2]
3. [Area 3]

## Suggested Sources

### Primary Sources

- [Source 1] - [Why it's valuable]
- [Source 2] - [Why it's valuable]

### Secondary Sources

- [Source 1] - [Why it's valuable]
- [Source 2] - [Why it's valuable]

### Expert Consultation

- [Type of expert needed]
- [Where to find them: professional orgs, university departments, etc.]

## Research Notes Template

**Fact**: [Verified information]
**Source**: [Where it came from]
**Reliability**: High / Medium / Low
**Relevance**: How it applies to your story
**Story Integration**: How to use it without info-dumping

## Red Flags to Watch For

- [Potential inaccuracy or myth about this topic]
- [Common misconceptions]
- [Dated information that may no longer be accurate]

## Cross-Reference Checklist

- [ ] Verified with at least 2 independent sources
- [ ] Checked publication date for currency
- [ ] Evaluated author credentials and bias
- [ ] Confirmed applicability to time period/context
```

### Step 4: Fact-Checking Existing Content

When the user needs to verify already-written content:

1. **Extract Claims**: Identify all factual statements
2. **Categorize**: Sort by type (historical, scientific, cultural, etc.)
3. **Verify Each**: Check against reliable sources
4. **Flag Issues**: Mark inaccuracies, anachronisms, impossibilities
5. **Suggest Corrections**: Provide accurate alternatives

Present as:

```markdown
# Fact-Check Report: [Chapter/Section]

## Claims Analyzed: [Number]

## Accurate: [X] ✓

## Inaccurate: [Y] ✗

## Unverifiable: [Z] ?

---

## Inaccurate Claims (Priority Fixes)

### Claim #1

**Text**: "[Quote from manuscript]"
**Location**: Chapter [X], paragraph [Y]
**Issue**: [What's wrong]
**Correct Information**: [Accurate version]
**Source**: [Where the correct info comes from]
**Suggested Revision**: "[Proposed text]"

---

## Anachronisms Detected

### Anachronism #1

**Text**: "[Quote]"
**Problem**: [Item/phrase/concept didn't exist in this time period]
**Appeared**: [When it actually became available/common]
**Period-Appropriate Alternative**: [What they would have used instead]

---

## Unverifiable Claims

### Claim #1

**Text**: "[Quote]"
**Issue**: Cannot find reliable source confirming this
**Recommendation**:

- Option 1: Find credible source
- Option 2: Frame as character belief, not fact
- Option 3: Revise or remove

---

## Accuracy Strengths

[What the author got right—positive reinforcement]

- ✓ Period-accurate clothing descriptions (Ch. 2)
- ✓ Correct use of historical events as backdrop (Ch. 5)
```

### Step 5: Integrate Research into Narrative

Help authors use research without info-dumping:

**Poor Integration** (Info-Dump):

> "The M1 Garand rifle, officially designated as United States Rifle, Caliber .30, M1, is a .30-06 Springfield semi-automatic rifle that was the standard U.S. service rifle during World War II and the Korean War. It was designed by Canadian-American John Garand in 1928 and officially adopted in 1936."

**Good Integration** (Woven In):

> "Miller checked his M1 Garand, the rifle's solid weight familiar in his hands after two years of carrying it across Europe. The distinctive 'ping' as it ejected the empty clip had saved his life more than once—enemy soldiers had learned to wait for that sound before attacking."

**Techniques for Integration**:

1. **Character Knowledge**: Filter facts through what the character would know
2. **Sensory Details**: Use research to add authentic textures, smells, sounds
3. **Dialogue**: Let characters naturally discuss relevant details
4. **Contrast**: Show differences between character expectations and reality
5. **Conflict**: Use factual constraints to create problems characters must solve

### Step 6: Create Research Bibliography

Maintain organized source tracking:

```markdown
# Research Bibliography: [Book Title]

## [Topic Category 1]

### [Subtopic]

1. **Source Title**: [Full citation]
   - **Author**: [Name]
   - **Type**: Book / Article / Interview / Website
   - **Publication**: [Date]
   - **Key Information Used**: [Brief summary]
   - **Reliability**: High / Medium / Low
   - **Story Chapters**: Used in Ch. [X, Y, Z]

---

## Experts Consulted

### [Expert Name]

- **Credentials**: [Title, affiliation]
- **Consultation Date**: [Date]
- **Topic**: [What you discussed]
- **Key Insights**: [Summary]
- **Follow-Up Needed**: Yes/No

---

## To Research Further

- [ ] [Topic 1] - Needed for Chapter [X]
- [ ] [Topic 2] - Verify before final draft
```

## Examples

### Example 1: Historical Fiction Research

**User**: "I'm writing a novel set in 1920s Paris. My protagonist is an American woman studying art. What do I need to research?"

**Output**:

```markdown
# Research Brief: 1920s Paris - American Female Art Student

## Research Question

What was daily life like for American women studying art in Paris during the 1920s, and what historical details would make this setting authentic?

## Background Context

Your protagonist will interact with the art world, navigate daily life as a foreigner, and experience the cultural atmosphere of the era. Readers of historical fiction expect period-accurate details that bring the setting to life.

## Key Areas to Investigate

### 1. Art Education in 1920s Paris

- Which art schools accepted women? (Académie Julian, Académie de la Grande Chaumière)
- Tuition costs and living expenses
- Teaching methods and curriculum
- Famous instructors of the period
- Gender discrimination challenges women faced

### 2. Daily Life Logistics

- Housing options for foreign students (pensions, apartments)
- Cost of living (bread, milk, rent in 1920s francs)
- Transportation (Metro lines available, taxi costs, bicycle culture)
- Communication (letters home, telegraph costs, trans-Atlantic mail time)
- Banking and money exchange for Americans

### 3. Social/Cultural Context

- Expatriate communities (Gertrude Stein's salon, Shakespeare and Company bookshop)
- Women's fashion of the era (silhouettes, undergarments, day vs evening wear)
- Prohibition's effect on Americans abroad
- Jazz age nightlife (specific venues like Le Boeuf sur le Toit)
- Attitudes toward independent women

### 4. Historical Events & Atmosphere

- Post-WWI sentiment and visible war impact
- Exchange rates (dollar very strong against franc in mid-1920s)
- Political climate in France
- Famous artists present in Paris then (Picasso, Hemingway, Josephine Baker)

## Suggested Sources

### Primary Sources

- **"The Autobiography of Alice B. Toklas" by Gertrude Stein** - First-hand account of 1920s Paris art scene
- **"Paris Was Yesterday: 1925-1939" by Janet Flanner** - Contemporary journalism
- **Letters and diaries from actual American art students** - Check museum archives (Smithsonian, Yale)
- **Period photographs** - Bibliothèque Nationale de France online collection
- **1920s Paris newspapers** - Gallica digital library

### Secondary Sources

- **"Sylvia Beach and the Lost Generation" by Noel Riley Fitch** - Excellent on expatriate community
- **"Americans in Paris: Life and Death Under Nazi Occupation" (early chapters)** - Context of American community
- **"Women Together/Women Apart: Portraits of Lesbian Paris"** - LGBTQ+ context of the era
- **University theses on women art students** - JSTOR, Google Scholar

### Expert Consultation

- **Art historians** specializing in 1920s Paris modernism - Contact through university art history departments
- **Fashion historians** - Museums with 1920s collections (Metropolitan Museum, V&A)
- **French cultural historians** - Alliance Française, university French departments

## Research Notes Template

**Fact**: The Académie Julian accepted women students and was one of the few that allowed women to study from nude models.

**Source**: "The Students of Paris" by Robert Jensen, Oxford University Press, 2014

**Reliability**: High - Academic press, art history professor, well-cited

**Relevance**: Explains why your protagonist would choose this school specifically

**Story Integration**:
Poor: "The Académie Julian was one of the few schools that let women study nudes."
Better: "Sarah chose the Académie Julian precisely because she could study from live models here—something the conservative academies back home would never have allowed a woman to do. The scandal of it thrilled her."

## Red Flags to Watch For

- **Myth**: All 1920s women had short "flapper" hair
  - **Reality**: Bobbed hair was fashionable but not universal; older women and conservatives kept long hair
- **Myth**: Everyone hung out with famous artists
  - **Reality**: Most students wouldn't have had access to Picasso's circle; stratification existed
- **Anachronism Watch**:
  - Eiffel Tower wasn't lit up at night yet (lighting installed 1985)
  - No ballpoint pens (invented 1938)
  - "Métro" not "Subway"
  - Francs, not Euros

## Cross-Reference Checklist

- [ ] Verified fashion details with period photographs AND written sources
- [ ] Checked that specific venues/businesses mentioned actually existed in 1925 (not 1935)
- [ ] Confirmed art movements mentioned were active then (Surrealism just starting, not established)
- [ ] Verified slang and idioms were in use during this specific period
- [ ] Double-checked exchange rates and economic details with multiple sources

---

## Quick Reference: Period-Accurate Details

### Money

- In 1925, $1 USD = approximately 20 francs (rate fluctuated)
- Monthly pension room: 200-400 francs
- Café coffee: 1-2 francs
- Metro ticket: 0.50 francs
- Art supplies: (research specific costs)

### Transportation

- Metro lines: 1-10 operational by 1920s
- Walking was most common
- Taxis: expensive luxury
- Bicycles: common for students

### Food Culture

- Breakfast: café au lait and croissant at corner café
- Lunch: longest meal, 12-2pm
- Dinner: typically late, 8-9pm
- Student cafeterias: cheap fixed-price meals

### Communication

- Letters took 7-10 days to reach America
- Telegrams expensive but fast
- Telephone rare in homes
- Writing letters home weekly was expected

---

## Story Integration Examples

**Info-Dump (Bad)**:

> "In the 1920s, American women studying art in Paris faced many challenges. They lived in pensions, which were boarding houses, and had to deal with exchange rates. The Académie Julian was one of the few schools that accepted women."

**Integrated (Good)**:

> "Sarah counted out Friday's francs for Madame Beaumont—400 for the month's room, leaving her with barely enough for canvas and paint, even with the dollar's generous exchange rate. 'Worth it,' she reminded herself, thinking of the Académie Julian's studio where she'd spent all morning sketching from a nude model, something no school in Boston would have allowed her to even witness, let alone practice."

(Shows: housing cost, exchange rates, school choice, and social mores—all naturally woven in)
```

### Example 2: Science Fiction Fact-Check

**User**: "I'm writing a sci-fi novel about a colony on Mars. Can you fact-check this paragraph?"

**User's Text**:

> "The colonists breathed normally in the Martian atmosphere thanks to the terraforming efforts. Outside, the temperature was a comfortable 70°F. Emma walked outside without a spacesuit, feeling the gentle Martian breeze. In the distance, she could see Earth in the night sky, as large as the Moon appears from Earth."

**Output**:

```markdown
# Fact-Check Report: Mars Colony Scene

## Claims Analyzed: 4

## Accurate: 0 ✓

## Inaccurate: 4 ✗

---

## Inaccurate Claims (All Critical)

### Claim #1: Breathable Martian Atmosphere After Terraforming

**Text**: "The colonists breathed normally in the Martian atmosphere thanks to the terraforming efforts."

**Issue**: Terraforming Mars to create a breathable atmosphere would require:

- Massive amounts of greenhouse gases to warm planet
- Centuries to millennia of time
- Technology that doesn't currently exist
- Magnetic field generation to prevent atmospheric loss

**Current Scientific Consensus**:

- Mars has only 1% of Earth's atmospheric pressure
- 95% CO2 composition (unbreathable)
- Terraforming possible in theory but would take 500-100,000 years depending on method
- Not feasible with current or near-future technology

**Suggested Revision Options**:

Option 1 (Pressurized Domes):

> "The colonists breathed normally inside the pressurized biodome. Outside the transparent alloy, the thin Martian atmosphere—barely 1% of Earth's pressure—remained as inhospitable as ever."

Option 2 (Far Future Setting):

> "After eight centuries of terraforming, the atmospheric pressure had finally risen enough for humans to breathe unassisted—one of humanity's greatest achievements. The air was still thin, like standing at 15,000 feet on Earth, and oxygen masks were recommended for exertion, but it beat the alternative."

Option 3 (Bioengineered Humans):

> "The third-generation colonists, their lungs bioengineered for efficiency, could extract oxygen from Mars's still-thin atmosphere. It felt like breathing at high altitude, but it beat wearing a suit."

---

### Claim #2: 70°F Temperature

**Text**: "Outside, the temperature was a comfortable 70°F."

**Issue**: Mars is cold.

- Average surface temperature: -80°F (-60°C)
- Warmest equatorial summer afternoon: might reach 70°F
- Same spot at night: -100°F
- Extreme temperature swings due to thin atmosphere

**Correct Information**:
If you want 70°F, it needs to be:

- Midday
- Summer
- Equatorial region
- Character acknowledges this is unusually warm
- And mention that it'll plunge after sunset

**Suggested Revision**:

> "Outside, the afternoon temperature had climbed to an almost-comfortable 65°F—about as warm as Mars ever got, even here at the equator in midsummer. Emma would need to be back inside within two hours, before the temperature plunged below freezing with the setting sun."

---

### Claim #3: Walking Without Spacesuit

**Text**: "Emma walked outside without a spacesuit, feeling the gentle Martian breeze."

**Issue**: Multiple problems even in terraformed scenario:

- Atmospheric pressure (addressed above)
- UV radiation (Mars has no ozone layer, no magnetic field)
- Toxic perchlorates in Martian dust
- Low pressure would cause water in body to vaporize

**Current Reality**:
Without a pressure suit on Mars, a human would:

- Lose consciousness in 15 seconds (hypoxia)
- Blood would not boil (common myth) but:
- Water in mouth/eyes would vaporize
- Skin would swell but not pop
- Death in 1-2 minutes

**Suggested Revision**:

> "Emma cycled through the airlock and stepped onto the Martian surface, her suit's environmental system humming. Even after two years, she still felt a thrill feeling the crunch of rust-red regolith under her boots."

---

### Claim #4: Earth Appearing As Large As Moon

**Text**: "In the distance, she could see Earth in the night sky, as large as the Moon appears from Earth."

**Issue**: Apparent size depends on distance.

- Mars to Earth distance: 34-250 million miles (varies with orbits)
- Earth to Moon distance: 239,000 miles
- Earth's diameter: 7,926 miles
- Moon's diameter: 2,159 miles

**Math**:
From Mars, Earth would appear:

- At closest approach: slightly larger than Venus appears from Earth
- Maximum apparent diameter: about 45 arcseconds
- Moon from Earth: 31 arcminutes (1860 arcseconds)
- Earth from Mars = about 40x smaller than Moon from Earth

**Visualization**: From Mars, Earth is a bright "star," not a disk visible to naked eye.

**Suggested Revision**:

> "In the night sky, she spotted Earth easily—the brightest blue-white 'star' visible, nothing like the pale disk of the Moon she'd grown up with, but unmistakably home. Next to it, barely visible, hung a tinier point of light: Luna, humanity's first stepping stone."

---

## Overall Assessment

**Accuracy Level**: 0/10 - All major details are scientifically inaccurate

**Reader Impact**:

- Hard sci-fi readers will immediately notice these errors and lose trust
- Soft sci-fi readers might not care, but you should still decide consciously
- Consider: Is this hard sci-fi (science is accurate) or space fantasy (science is flavor)?

**Recommendation**:
Decide your book's relationship to scientific accuracy:

1. **Hard Sci-Fi** (Prioritize accuracy): Revise all four issues
2. **Soft Sci-Fi** (Plausible-sounding): Fix pressure/temperature, handwave terraforming
3. **Science Fantasy** (Rule of cool): Acknowledge it's not realistic, lean into adventure

Whatever you choose, be consistent throughout the book.

---

## Quick Mars Facts Reference

**Atmosphere**:

- 1% Earth pressure
- 95% CO2, 3% nitrogen, 2% argon
- No oxygen

**Temperature**:

- Average: -80°F
- Range: -190°F to +70°F
- Massive day/night swings

**Gravity**:

- 38% of Earth
- 100lb person weighs 38lb

**Day Length**:

- 24 hours, 37 minutes (sol)

**Year Length**:

- 687 Earth days

**Distance from Earth**:

- Closest: 34 million miles
- Farthest: 250 million miles

**Radiation**:

- No magnetic field
- No ozone layer
- Surface radiation 100x Earth
- Unsurvivable for unshielded humans

**Dust**:

- Contains toxic perchlorates
- Fine and electrostatically charged
- Global dust storms possible
```

## Tips for Authors

### Research Best Practices

- Start research early, not during first draft
- Take detailed notes with sources
- Bookmark and save web sources (they disappear)
- Interview real experts when possible
- Visit locations if feasible
- Read both contemporary and modern sources

### Avoiding Info-Dumps

- Trust readers to infer from context
- Reveal details through character action, not narrative aside
- Use the "iceberg principle"—show 10%, know 90%
- If it doesn't affect the plot or character, cut it
- Spread details throughout, not all at once

### When to Break the Rules

- For pacing (condensing timeline)
- For clarity (simplifying complexity)
- For character (intentional ignorance/mistakes)
- Document your conscious choices

## Validation Checklist

Before finalizing research/fact-checking:

- [ ] All sources are cited with publication dates
- [ ] Checked multiple independent sources for important facts
- [ ] Evaluated source reliability and potential bias
- [ ] Verified time-period accuracy (no anachronisms)
- [ ] Confirmed cultural details with sensitivity readers/consultants when appropriate
- [ ] Integrated research naturally into narrative
- [ ] Maintained bibliography for future reference
- [ ] Determined acceptable level of accuracy for genre
