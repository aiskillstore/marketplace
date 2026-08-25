# LH/T&M Data Source Operations and Mapping Reference

Use this reference for SOC selection, BLS wage retrieval, CALC+ positioning, and GSA Per Diem. Keep operation names stable and let the host supply any runtime namespace.

## Contents

1. Constants and runtime checks
2. SOC mapping
3. BLS OEWS operations
4. CALC+ operations
5. GSA Per Diem operations
6. Raw-data recording

## 1. Constants and runtime checks

| Item | Current baseline | Required handling |
|---|---:|---|
| Standard work year | 2,080 hours | Convert annual wage to hourly direct labor |
| Default productive hours | 1,880 hours | Editable workbook assumption; derive shift-coverage FTE from this value |
| BLS wage cap | $239,200 annual or $115 hourly | Reconfirm each release and treat capped values as lower bounds |
| BLS vintage | May 2025 | Call `detect_latest_year` before every estimate |
| First and last day M&IE | 75% | Use the MCP's discounted result once |
| City Pair fare | YCA when available | Use only when origin and destination are known |

Treat published constants as baselines. Runtime data controls the estimate.

### Request pacing

Serialize credentialed federal API calls and leave at least three seconds between them, including capability checks. Do not parallelize keyed BLS or Per Diem calls. Honor any longer server-provided retry interval. If a service reports a rate limit, stop and report it instead of issuing rapid retries. Unkeyed services must still follow their advertised limits and must not be queried in uncontrolled loops.

## 2. SOC mapping

Classify the requirement domain before mapping job titles.

### IT and software

| Common title | SOC | BLS title |
|---|---|---|
| IT Program Manager | 11-3021 | Computer and Information Systems Managers |
| Management Analyst | 13-1111 | Management Analysts |
| Project Manager | 13-1082 | Project Management Specialists |
| Systems Engineer or Analyst, IT | 15-1211 | Computer Systems Analysts |
| Cybersecurity or InfoSec Analyst | 15-1212 | Information Security Analysts |
| Network Architect | 15-1241 | Computer Network Architects |
| Database Administrator | 15-1242 | Database Administrators |
| Systems Administrator | 15-1244 | Network and Computer Systems Administrators |
| Software Developer | 15-1252 | Software Developers |
| QA Tester | 15-1253 | Software QA Analysts and Testers |
| Help Desk or User Support | 15-1232 | Computer User Support Specialists |
| Data Scientist | 15-2051 | Data Scientists |

### Physical and non-IT engineering

Use these codes for physical systems, reactors, aerospace, infrastructure, chemical, mechanical, and hardware integration.

| Common title | SOC | BLS title |
|---|---|---|
| Aerospace Engineer | 17-2011 | Aerospace Engineers |
| Biomedical Engineer | 17-2031 | Bioengineers and Biomedical Engineers |
| Chemical Engineer | 17-2041 | Chemical Engineers |
| Civil Engineer | 17-2051 | Civil Engineers |
| Electrical Engineer | 17-2071 | Electrical Engineers |
| Electronics Engineer | 17-2072 | Electronics Engineers, Except Computer |
| Environmental Engineer | 17-2081 | Environmental Engineers |
| Industrial Engineer | 17-2112 | Industrial Engineers |
| Mechanical Engineer | 17-2141 | Mechanical Engineers |
| Nuclear Engineer | 17-2161 | Nuclear Engineers |
| Petroleum Engineer | 17-2171 | Petroleum Engineers |
| Systems Engineer, non-IT | 17-2199 | Engineers, All Other |

Use 17-2199 when an integration role spans engineering disciplines. Query a specific engineering SOC beside it when useful.

### Science, research, medical, and support

| Common title | SOC | BLS title |
|---|---|---|
| Physicist | 19-2012 | Physicists |
| Chemist | 19-2031 | Chemists |
| Medical Scientist | 19-1042 | Medical Scientists, Except Epidemiologists |
| Registered Nurse | 29-1141 | Registered Nurses |
| Physician Assistant | 29-1071 | Physician Assistants |
| Technical Writer | 27-3042 | Technical Writers |
| Contracting Specialist | 13-1020 | Buyers and Purchasing Agents |

### Program management context

Use the contract domain to map Program Manager:

- Operations or administration: 11-1021, General and Operations Managers
- Physical engineering or R&D: 11-9041, Architectural and Engineering Managers
- IT or software: 11-3021, Computer and Information Systems Managers

Document the choice. Do not default every technical Program Manager to 11-3021.

## 3. BLS OEWS operations

### Runtime vintage

Call `detect_latest_year` before wage retrieval. Record the returned year and use it in Raw Data, the Summary assumption block, and the aging calculation. If it differs from May 2025, use the runtime result.

### Wage retrieval

Call:

```text
get_wage_data(
  occ_code=<six-character SOC>,
  scope=<metro|state|national>,
  area_code=<five-digit MSA or two-digit state FIPS>,
  datatypes=["04", "11", "12", "13", "14", "15"]
)
```

The requested datatypes provide mean plus P10, P25, P50, P75, and P90. Valid operation datatypes include `01`, `03`, `04`, `08`, `11`, `12`, `13`, `14`, and `15`. Do not send `02` or `05`.

Use `list_common_metros` to resolve common MSAs and renumbering notes. If a metro is absent, resolve its current code from BLS before falling back.

Fallback ladder:

1. Metro
2. State, only after the metro series and current MSA code are checked
3. National

Record each fallback and its reason. Do not treat suppressed or unavailable metro data as evidence about market quality.

For a single-category sanity check, `igce_wage_benchmark` may return compact wage and burden information. Use `get_wage_data` for the full workbook so the percentile basis remains visible.

### Seniority convention

When BLS does not distinguish job levels:

- Junior or entry: P25
- Mid or journeyman: P50
- Senior: P50 to P75 based on scope
- Principal, director, or SME: P75 to P90

If no levels are supplied, price all members at P50 and disclose that convention. Do not invent a junior/mid/senior staffing mix.

### Capped and compressed distributions

If a selected percentile hits the BLS cap, treat it as a lower bound. If a selected value is within 10% of the current cap, note that the local market may exceed the reported value and flag the proximity for Contracting Officer review. If P75 is capped:

1. Use the uncapped mean as a senior anchor when appropriate.
2. Cross-reference a separate commercial source if available.
3. Consider national P75 divided by national P50, applied to local P50, and label it as a derivation.
4. Never present the cap as an exact point estimate.

If P75 equals P90 below the cap, disclose a flat upper tail. If P25 equals P10, do not use P25 for a junior anchor without review. A possible derived junior value is national P25 multiplied by local P50 divided by national P50. Label every derived value.

## 4. CALC+ operations

### Silent-wrong-answer signature

The CALC+ keyword route is:

```text
/v3/api/ceilingrates/?keyword=<term>
```

The parameter is `keyword=`. Never use `q=`. The wrong parameter can be accepted while returning the unfiltered corpus.

The labor-category discovery response path is:

```text
aggregations.labor_category.buckets[*].key
aggregations.labor_category.buckets[*].doc_count
```

Record enough of the selected buckets and counts to reproduce the pool.

### Discovery-first flow

1. Call `suggest_contains(field="labor_category", term=<LCAT term>)`.
2. If the top exact buckets form an adequate pool, call `exact_search(field="labor_category", value=<bucket>)` for each selected bucket.
3. If buckets are fragmented, call `keyword_search(keyword=<term>)` and document that keyword matching can include other fields.
4. Use `igce_benchmark(labor_category=<title>, experience_min=<years>, education_level=<level>)` for compact percentile statistics.
5. Do not send `page_size=0`. Use at least 1 when an operation requires the parameter.

Expected benchmark fields include count, minimum, maximum, mean, standard deviation, P10, P25, P50, P75, and P90. Use the returned canonical fields instead of probing large raw payloads.

### Tier matching and dual pools

Match the actual level. For a mid-level developer, prefer `Software Developer II` over an all-level Software Developer pool.

For senior categories, present both:

- Title-match pool, discovered through `suggest_contains` and `exact_search`
- Experience-match pool, returned by `igce_benchmark` with an appropriate minimum experience filter

Report both sample sizes and medians. Do not merge them without disclosure.

Useful fragmented-title alternatives:

- SOC Analyst or Cyber Analyst: Information Security Analyst I, II, and III
- Software Engineer: Software Developer I, II, and III
- Data Engineer with a thin pool: Data Scientist with experience filter, clearly labeled as a proxy

### Workflow B shortcut

Call:

```text
price_reasonableness_check(
  labor_category=<title>,
  proposed_rate=<rate>,
  education_level=<level if known>,
  experience_min=<years if known>
)
```

Use the returned count, bounds, z-score, and percentile only as positioning data. Label a pool under about 25 records as directional.

### LH/T&M positioning bands

- Within 15% of P50: expected comparison range
- Between 15% and 30% from P50: show the full burden, seniority, geography, and pool-composition arithmetic
- More than 30% from P50: show alternate SOC or title pools and direct the result to Contracting Officer review
- Below P25: report the position and ask the Contracting Officer to review the input, level, or pool alignment

LH/T&M burdened hourly labor rates are directly comparable to CALC+ ceiling labor rates, but CALC+ pools can still mix education, experience, geography, and labor-category definitions. Do not translate a band into a fair-and-reasonable conclusion.

Do not translate a band into a fair-and-reasonable conclusion.

## 5. GSA Per Diem operations

### Travel estimate

For one or more nights, call:

```text
estimate_travel_cost(
  city=<civilian locality>,
  state=<state>,
  num_nights=<integer>,
  travel_month=<optional month>,
  fiscal_year=<optional FY>
)
```

Expected fields include nightly lodging, lodging total, daily M&IE, first/last-day M&IE, M&IE total, grand total, and travel days.

Calculate annual travel as:

```text
grand total per trip * trips per year * travelers
```

Use the operation's first/last-day amount once. `get_mie_breakdown` already returns a 75% value. Do not multiply it by 0.75 again.

`estimate_travel_cost` requires at least one night. For a 0-night day trip, do not pass zero to that operation. Call `lookup_city_perdiem` for the locality and fiscal year, use `mie_first_last_day` once, and set lodging to zero. Record one travel day in the workbook.

### Installation to locality crosswalk

GSA uses civilian localities. Translate installations before lookup.

| Installation or site | GSA locality |
|---|---|
| Fort Meade, MD | Annapolis or Anne Arundel County, MD |
| Fort Belvoir, VA | Fairfax or Alexandria, VA |
| Pentagon, VA | Arlington, VA or DC rate |
| Joint Base Andrews, MD | District of Columbia |
| NSA Bethesda or Walter Reed, MD | District of Columbia composite locality |
| Fort Liberty, NC | Fayetteville, NC |
| Peterson SFB, Schriever SFB, or Fort Carson, CO | Colorado Springs, CO |
| Wright-Patterson AFB, OH | Dayton, OH |
| Eglin AFB, FL | Fort Walton Beach, FL |
| JB San Antonio, Randolph, or Lackland, TX | San Antonio, TX |
| Hanscom AFB, MA | Bedford or Boston, MA |
| Redstone Arsenal, AL | Huntsville, AL |
| Offutt AFB, NE | Omaha or Bellevue, NE |
| Cape Canaveral or Patrick SFB, FL | Cocoa Beach or Cape Canaveral, FL |
| Joint Base Lewis-McChord, WA | Tacoma or Pierce County, WA |
| Oak Ridge National Laboratory or Y-12, TN | Knoxville, TN |
| Los Alamos National Laboratory, NM | Santa Fe or Los Alamos County, NM |
| Hanford or PNNL, WA | Richland, WA |
| Sandia National Laboratories, NM | Albuquerque, NM |
| Lawrence Livermore National Laboratory, CA | Livermore or Oakland, CA |
| Idaho National Laboratory, ID | Idaho Falls, ID |
| White Sands Missile Range, NM | Las Cruces, NM |
| NAWS China Lake, CA | Ridgecrest or Kern County, CA |
| Edwards AFB, CA | Lancaster or Palmdale, CA |
| Dugway Proving Ground, UT | Salt Lake City metro standard rate |
| Nellis AFB or Creech AFB, NV | Las Vegas, NV |
| Point Mugu or NBVC, CA | Oxnard or Ventura County, CA |

For another site, call `lookup_city_perdiem` with the nearest civilian locality and verify the returned county.

### Fiscal-year fallback

If the requested fiscal year returns an empty rate list or an error containing `No rates found for FY`, retry the prior fiscal year. Record the requested and fallback years in Methodology. If contract start is within six months of a new fiscal year, query the new year when published or disclose that the current-year baseline must be refreshed.

### Travel interpretation

"Quarterly travel between sites" means four total trips split across destinations unless the user says each way or per destination. Ask when the interpretation materially changes cost.

If origin and destination are in the same metro or within ordinary local-travel distance, flag that lodging per diem may not apply. Use mileage or another user-supplied local-travel basis instead.

## 6. Raw-data recording

Record compact, reproducible inputs and outputs on the Raw Data sheet:

- BLS operation, SOC, scope, area code, datatypes, returned vintage, and selected percentiles
- CALC+ operation, exact buckets or keyword, count, percentiles, and contamination caveat if applicable
- Per Diem locality, state, fiscal year, month, nights, returned lodging, and returned M&IE
- Every fallback, proxy, or derived value

Do not paste full JSON payloads. Record the parameters and summary fields needed to reproduce each call.
