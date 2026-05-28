# PROSPERO Registration Prompt Templates

Use these templates to generate the respective sections of the PROSPERO registration form.

## 1. Review Title and Basic Details

**Role**: You are a clinical medical scientist and meta-analysis expert assisting a user in registering a meta-analysis on the PROSPERO platform.

**Input**:
- Title: `<User Provided Title>`
- Protocol: `<User Provided Protocol (Optional)>`

**Instructions**:
1.  Extract PICO(s) from the title: Population, Intervention/Exposure, Comparison, Outcome.
2.  Based on the PICO and Title, answer the questions below.
3.  **Rules**:
    *   Replace content in `<>` with your analysis.
    *   Keep content in `{}` exactly as is.
    *   Output in English.

**Template**:

```text
**【PROSPERO registration】**

**【REVIEW TITLE AND BASIC DETAILS】：**

1.*Review title. (title)
<give the user's title of the review in English>

2.*Condition or domain being studied. (background)
<Disease name + Introduction + Current status + Existing interventions + Intervention studied in this paper and its advantages (significance). Limit to 200 words.>
Example: "Major depressive disorder is one of the most common..."

3.*Review objectives. (purpose)
<Briefly describe the rationale for the review explaining why it is being done and what it might add to existing knowledge>

4.*Keywords. (keywords：at least 3，recommend 3~5）
<Please extract three to five keywords from the title>

5.*Country.
{Select the country in which the review is being carried out，}
```

## 2. Eligibility Criteria

**Role**: Same as above.

**Input**: Title and extracted PICO.

**Instructions**:
1.  Analyze PICO to fill in the criteria.
2.  Use future tense ("will be...").
3.  Output ONLY the Eligibility Criteria section.

**Template**:

```text
**【ELIGIBILITY CRITERIA】：**

1.*population.
<Specify the populations being studied. Format: Inclusion: ... Exclusion: ...>

2.*Intervention(s), exposure(s).
<Give full and clear descriptions or definitions of the interventions or the exposures to be reviewed.>

3.*Comparator(s)/control(s).
-{Does this review compare the intervention with another treatment or with a control?}
-{Add comparator PICO tags here}<Choose labels: Placebo, Usual Care, etc.>

4.*Study design
{Randomised studies}

5.*Context.
<Give summary details of the setting and other relevant characteristics.>
```

## 3. Timeline and Methods

**Role**: Same as above.

**Input**:
- Title
- Start Date: `<Calculated Start Date>`
- End Date: `<Calculated End Date>`

**Instructions**:
1.  Fill in the Timeline with the provided dates.
2.  Design a search strategy based on the PICO extracted from the title.

**Template**:

```text
**【SIMILAR REVIEWS】：**

*Check for similar records already in PROSPERO
-Check similar PROSPERO registrations?
{Show similar records}
-Similar registrations
Is this review similar to your review?
{This review is different to our review}

**【TIMELINE OF THE REVIEW】：**

*Review timeline
-Start date: <Start Date>
-End date: <End Date>
{The end date should be at least 28 days after the start date }

**【AVAILABILITY OF FULL PROTOCOL】：**

*Availability of full protocol
-Please select from the options below
{A full protocol has not been written...}
{Upload a full protocol to PROSPERO in PDF format(Recommended choices)}

**【SEARCHING AND SCREENING】：**

1.*Search for unpublished studies
{We will search for published studies and We will search for unpublished studies }

2.*Main bibliographic databases that will be searched
{Pubmed、Embase... (Please choose according to your personal situation)}

3.*Search language restrictions
{No search language restrictions}

4.*Search date restrictions
{There are no search date restrictions}

6.*Link to search strategy
-Search formula:
<Design a PubMed search strategy based on the PICO. Use OR for synonyms and AND for different concepts.>

7.*Selection process
{Studies screened independently by at least 2 people...}

**【DATA COLLECTION PROCESS】：**

1.*Data extraction
{Data will be extracted independently by at least two people...}

2.*Study risk of bias or quality assessment
<Recommend a tool based on the title, e.g., ROB-2>

3.*Reporting bias assessment
{Yes - risk of bias due to missing results will be assessed}

4.*Certainty assessment
{Yes - certainty of findings will be assessed}
```
